import unreal


COMPOUND_NAME = "TerracedShrineSequence"
PRESET_NAME = "hill_shrine"
DETAIL_MODE = "blockout"
GAMEPLAY_SCALE = 3.0

PRESETS = {
    "hill_shrine": {
        "terrace_width": 2800.0,
        "terrace_depth": 1500.0,
        "terrace_height": 180.0,
        "terrace_count": 3,
        "stair_width": 520.0,
        "stair_depth": 420.0,
        "stair_height": 180.0,
        "mid_pavilion_width": 1000.0,
        "mid_pavilion_depth": 900.0,
        "mid_pavilion_height": 360.0,
        "summit_shrine_width": 1500.0,
        "summit_shrine_depth": 1100.0,
        "summit_shrine_height": 520.0,
    },
    "imperial_altar_approach": {
        "terrace_width": 3400.0,
        "terrace_depth": 1700.0,
        "terrace_height": 200.0,
        "terrace_count": 4,
        "stair_width": 620.0,
        "stair_depth": 460.0,
        "stair_height": 200.0,
        "mid_pavilion_width": 1200.0,
        "mid_pavilion_depth": 980.0,
        "mid_pavilion_height": 400.0,
        "summit_shrine_width": 1800.0,
        "summit_shrine_depth": 1200.0,
        "summit_shrine_height": 620.0,
    },
}

DETAIL_PROFILES = {
    "blockout": {"add_shrine_eaves": False, "add_terrace_edges": False, "add_lanterns": False, "add_guardians": False, "add_altar_markers": False, "add_summit_forecourt": False, "add_entry_arch": False, "add_processional_posts": False},
    "low": {"add_shrine_eaves": True, "add_terrace_edges": True, "add_lanterns": False, "add_guardians": False, "add_altar_markers": False, "add_summit_forecourt": False, "add_entry_arch": False, "add_processional_posts": False},
    "medium": {"add_shrine_eaves": True, "add_terrace_edges": True, "add_lanterns": True, "add_guardians": True, "add_altar_markers": True, "add_summit_forecourt": False, "add_entry_arch": False, "add_processional_posts": False},
    "high": {"add_shrine_eaves": True, "add_terrace_edges": True, "add_lanterns": True, "add_guardians": True, "add_altar_markers": True, "add_summit_forecourt": True, "add_entry_arch": True, "add_processional_posts": True},
}

DETAIL_ALIASES = {"ornamented": "medium"}

CUBE_PATH = "/Engine/BasicShapes/Cube.Cube"
OUTPUT_FOLDER = "Generated/{0}".format(COMPOUND_NAME)


def vec(x, y, z):
    return unreal.Vector(float(x), float(y), float(z))


def add(a, b):
    return vec(a.x + b.x, a.y + b.y, a.z + b.z)


def mul(v, s):
    return vec(v.x * s, v.y * s, v.z * s)


editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
unreal_editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
cube_mesh = unreal.EditorAssetLibrary.load_asset(CUBE_PATH)
actor_grouping_utils_class = getattr(unreal, "ActorGroupingUtils", None)
generated_actors = []

if not cube_mesh:
    raise RuntimeError("Could not load cube mesh: {0}".format(CUBE_PATH))


def get_config():
    config = dict(PRESETS[PRESET_NAME])
    for key in list(config.keys()):
        if key == "terrace_count":
            continue
        config[key] *= GAMEPLAY_SCALE
    return config


def resolve_detail_mode():
    normalized_mode = DETAIL_MODE.strip().lower()
    normalized_mode = DETAIL_ALIASES.get(normalized_mode, normalized_mode)
    if normalized_mode not in DETAIL_PROFILES:
        return "blockout"
    return normalized_mode


def get_detail_profile():
    return dict(DETAIL_PROFILES[resolve_detail_mode()])


def set_folder(actor):
    try:
        actor.set_folder_path(OUTPUT_FOLDER)
    except Exception:
        pass


def register_actor(actor):
    if actor:
        generated_actors.append(actor)
    return actor


def destroy_previous(prefix):
    for actor in editor_actor_subsystem.get_all_level_actors():
        try:
            if actor.get_actor_label().startswith(prefix):
                editor_actor_subsystem.destroy_actor(actor)
        except Exception:
            pass


def spawn_box(label, center, size_cm):
    actor = editor_actor_subsystem.spawn_actor_from_class(unreal.StaticMeshActor, center, unreal.Rotator(0.0, 0.0, 0.0))
    actor.set_actor_label(label)
    set_folder(actor)
    smc = actor.get_editor_property("static_mesh_component")
    smc.set_static_mesh(cube_mesh)
    smc.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
    actor.set_actor_scale3d(vec(size_cm.x / 100.0, size_cm.y / 100.0, size_cm.z / 100.0))
    return register_actor(actor)


def finalize_generated_layout():
    if actor_grouping_utils_class:
        try:
            if not actor_grouping_utils_class.is_grouping_active():
                actor_grouping_utils_class.set_grouping_active(True)
            grouping_utils = actor_grouping_utils_class.get()
            if grouping_utils and grouping_utils.can_group_actors(generated_actors):
                group_actor = grouping_utils.group_actors(generated_actors)
                group_actor.set_actor_label("{0}_Group".format(COMPOUND_NAME))
                set_folder(group_actor)
        except Exception as exc:
            unreal.log_warning("{0}: failed to group generated actors ({1})".format(COMPOUND_NAME, exc))


def spawn_hall(label, origin, width, depth, height, detail_profile):
    roof_height = 80.0 * GAMEPLAY_SCALE
    roof_z = height + (roof_height * 0.5)
    spawn_box(label + "_Core", add(origin, vec(0.0, 0.0, height * 0.5)), vec(width * 0.72, depth * 0.78, height))
    spawn_box(label + "_Roof", add(origin, vec(0.0, 0.0, roof_z)), vec(width, depth, roof_height))
    if detail_profile["add_shrine_eaves"]:
        spawn_box(label + "_EaveBand", add(origin, vec(0.0, 0.0, roof_z)), vec(width * 1.08, depth * 1.06, 20.0 * GAMEPLAY_SCALE))


def spawn_stair_run(origin, width, depth, total_height, steps):
    run = depth / max(steps, 1)
    rise = total_height / max(steps, 1)
    for index in range(steps):
        step_depth = depth - (index * run)
        center = add(origin, vec(0.0, -(step_depth * 0.5), index * rise + (rise * 0.5)))
        spawn_box("{0}_Stair_{1}".format(COMPOUND_NAME, index + 1), center, vec(width, step_depth, rise))


def build_terraced_sequence(origin):
    config = get_config()
    detail_profile = get_detail_profile()
    generated_actors[:] = []
    destroy_previous(COMPOUND_NAME)

    current_origin = origin
    for terrace_index in range(int(PRESETS[PRESET_NAME]["terrace_count"])):
        width_scale = 1.0 - (terrace_index * 0.1)
        terrace_size = vec(config["terrace_width"] * width_scale, config["terrace_depth"], config["terrace_height"])
        terrace_center = add(current_origin, vec(0.0, terrace_size.y * 0.5, terrace_size.z * 0.5))
        spawn_box("{0}_Terrace_{1}".format(COMPOUND_NAME, terrace_index + 1), terrace_center, terrace_size)
        if detail_profile["add_terrace_edges"]:
            spawn_box("{0}_Terrace_{1}_Edge".format(COMPOUND_NAME, terrace_index + 1), add(terrace_center, vec(0.0, 0.0, terrace_size.z * 0.5 + (12.0 * GAMEPLAY_SCALE))), vec(terrace_size.x * 1.02, terrace_size.y * 1.02, 16.0 * GAMEPLAY_SCALE))
        spawn_stair_run(current_origin, config["stair_width"], config["stair_depth"], config["stair_height"], 5)
        if detail_profile["add_processional_posts"]:
            post_size = vec(50.0 * GAMEPLAY_SCALE, 50.0 * GAMEPLAY_SCALE, 170.0 * GAMEPLAY_SCALE)
            for suffix, direction in (("L", -1.0), ("R", 1.0)):
                spawn_box("{0}_Post_{1}_{2}".format(COMPOUND_NAME, terrace_index + 1, suffix), add(current_origin, vec((config["stair_width"] * 0.6) * direction, -(config["stair_depth"] * 0.26), post_size.z * 0.5)), post_size)
        current_origin = add(current_origin, vec(0.0, config["terrace_depth"] * 0.82, config["terrace_height"]))

        if terrace_index == 1:
            spawn_hall("{0}_MidPavilion".format(COMPOUND_NAME), add(current_origin, vec(0.0, 180.0 * GAMEPLAY_SCALE, 0.0)), config["mid_pavilion_width"], config["mid_pavilion_depth"], config["mid_pavilion_height"], detail_profile)

    summit_origin = add(current_origin, vec(0.0, 220.0 * GAMEPLAY_SCALE, 0.0))
    spawn_hall("{0}_SummitShrine".format(COMPOUND_NAME), summit_origin, config["summit_shrine_width"], config["summit_shrine_depth"], config["summit_shrine_height"], detail_profile)
    tower_offset_x = config["summit_shrine_width"] * 0.48
    tower_size = vec(220.0 * GAMEPLAY_SCALE, 220.0 * GAMEPLAY_SCALE, 580.0 * GAMEPLAY_SCALE)
    for suffix, direction in (("L", -1.0), ("R", 1.0)):
        spawn_box("{0}_SummitTower_{1}".format(COMPOUND_NAME, suffix), add(summit_origin, vec(tower_offset_x * direction, 60.0 * GAMEPLAY_SCALE, tower_size.z * 0.5)), tower_size)

    if detail_profile["add_lanterns"]:
        lantern_size = vec(70.0 * GAMEPLAY_SCALE, 70.0 * GAMEPLAY_SCALE, 210.0 * GAMEPLAY_SCALE)
        for suffix, direction in (("L", -1.0), ("R", 1.0)):
            spawn_box("{0}_Lantern_{1}".format(COMPOUND_NAME, suffix), add(summit_origin, vec((config["summit_shrine_width"] * 0.3) * direction, -(config["summit_shrine_depth"] * 0.64), lantern_size.z * 0.5)), lantern_size)

    if detail_profile["add_guardians"]:
        guardian_size = vec(130.0 * GAMEPLAY_SCALE, 130.0 * GAMEPLAY_SCALE, 240.0 * GAMEPLAY_SCALE)
        for suffix, direction in (("L", -1.0), ("R", 1.0)):
            spawn_box("{0}_Guardian_{1}".format(COMPOUND_NAME, suffix), add(summit_origin, vec((config["summit_shrine_width"] * 0.26) * direction, -(config["summit_shrine_depth"] * 0.52), guardian_size.z * 0.5)), guardian_size)

    if detail_profile["add_altar_markers"]:
        spawn_box("{0}_AltarMarker".format(COMPOUND_NAME), add(summit_origin, vec(0.0, config["summit_shrine_depth"] * 0.56, 40.0 * GAMEPLAY_SCALE)), vec(config["summit_shrine_width"] * 0.26, config["summit_shrine_depth"] * 0.16, 80.0 * GAMEPLAY_SCALE))

    if detail_profile["add_summit_forecourt"]:
        spawn_box("{0}_SummitForecourt".format(COMPOUND_NAME), add(summit_origin, vec(0.0, -(config["summit_shrine_depth"] * 0.74), 16.0 * GAMEPLAY_SCALE)), vec(config["summit_shrine_width"] * 0.52, config["summit_shrine_depth"] * 0.26, 32.0 * GAMEPLAY_SCALE))

    if detail_profile["add_entry_arch"]:
        spawn_box("{0}_EntryArchBeam".format(COMPOUND_NAME), add(origin, vec(0.0, -(config["stair_depth"] * 0.9), config["terrace_height"] + (80.0 * GAMEPLAY_SCALE))), vec(config["stair_width"] * 1.28, 90.0 * GAMEPLAY_SCALE, 70.0 * GAMEPLAY_SCALE))
        spawn_box("{0}_EntryArchPier_L".format(COMPOUND_NAME), add(origin, vec(-(config["stair_width"] * 0.62), -(config["stair_depth"] * 0.9), config["terrace_height"] * 0.5)), vec(90.0 * GAMEPLAY_SCALE, 90.0 * GAMEPLAY_SCALE, config["terrace_height"]))
        spawn_box("{0}_EntryArchPier_R".format(COMPOUND_NAME), add(origin, vec(config["stair_width"] * 0.62, -(config["stair_depth"] * 0.9), config["terrace_height"] * 0.5)), vec(90.0 * GAMEPLAY_SCALE, 90.0 * GAMEPLAY_SCALE, config["terrace_height"]))

    finalize_generated_layout()


def get_spawn_origin(distance):
    if unreal_editor_subsystem:
        camera_info = unreal_editor_subsystem.get_level_viewport_camera_info()
        if camera_info:
            camera_location, camera_rotation = camera_info
            forward = unreal.MathLibrary.get_forward_vector(camera_rotation)
            return add(camera_location, mul(forward, distance))
    unreal.log_warning("{0}: viewport camera unavailable, spawning at world origin".format(COMPOUND_NAME))
    return vec(0.0, 0.0, 0.0)


spawn_origin = get_spawn_origin(3200.0)
build_terraced_sequence(spawn_origin)

print("{0} ({1}, {2}) generated at {3}".format(COMPOUND_NAME, PRESET_NAME, resolve_detail_mode(), spawn_origin))
