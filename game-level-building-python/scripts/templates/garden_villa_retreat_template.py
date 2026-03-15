import unreal


COMPOUND_NAME = "GardenVillaRetreat"
PRESET_NAME = "noble_retreat"
DETAIL_MODE = "blockout"
GAMEPLAY_SCALE = 3.0

PRESETS = {
    "noble_retreat": {
        "compound_width": 4200.0,
        "compound_depth": 4200.0,
        "villa_width": 1800.0,
        "villa_depth": 1200.0,
        "villa_height": 480.0,
        "pond_width": 1200.0,
        "pond_depth": 860.0,
        "garden_wall_height": 140.0,
        "side_pavilion_width": 760.0,
        "side_pavilion_depth": 760.0,
        "side_pavilion_height": 300.0,
    },
    "scholar_estate": {
        "compound_width": 4800.0,
        "compound_depth": 4600.0,
        "villa_width": 2100.0,
        "villa_depth": 1300.0,
        "villa_height": 540.0,
        "pond_width": 1450.0,
        "pond_depth": 980.0,
        "garden_wall_height": 160.0,
        "side_pavilion_width": 840.0,
        "side_pavilion_depth": 840.0,
        "side_pavilion_height": 340.0,
    },
}

DETAIL_PROFILES = {
    "blockout": {"add_eaves": False, "add_bridge_rails": False, "add_lanterns": False, "add_tree_clusters": False, "add_screen_wall": False, "add_moon_gate": False, "add_pond_edge": False, "add_forecourt": False},
    "low": {"add_eaves": True, "add_bridge_rails": True, "add_lanterns": False, "add_tree_clusters": False, "add_screen_wall": False, "add_moon_gate": False, "add_pond_edge": False, "add_forecourt": False},
    "medium": {"add_eaves": True, "add_bridge_rails": True, "add_lanterns": True, "add_tree_clusters": True, "add_screen_wall": True, "add_moon_gate": False, "add_pond_edge": False, "add_forecourt": False},
    "high": {"add_eaves": True, "add_bridge_rails": True, "add_lanterns": True, "add_tree_clusters": True, "add_screen_wall": True, "add_moon_gate": True, "add_pond_edge": True, "add_forecourt": True},
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
    plinth_height = 100.0 * GAMEPLAY_SCALE
    roof_height = 80.0 * GAMEPLAY_SCALE
    roof_z = plinth_height + height + (roof_height * 0.5)
    spawn_box(label + "_Plinth", add(origin, vec(0.0, 0.0, plinth_height * 0.5)), vec(width, depth, plinth_height))
    spawn_box(label + "_Core", add(origin, vec(0.0, 0.0, plinth_height + (height * 0.5))), vec(width * 0.68, depth * 0.72, height))
    spawn_box(label + "_Roof", add(origin, vec(0.0, 0.0, roof_z)), vec(width * 1.12, depth * 1.08, roof_height))
    if detail_profile["add_eaves"]:
        spawn_box(label + "_EaveBand", add(origin, vec(0.0, 0.0, roof_z)), vec(width * 1.18, depth * 1.14, 20.0 * GAMEPLAY_SCALE))


def build_villa_retreat(origin):
    config = get_config()
    detail_profile = get_detail_profile()
    generated_actors[:] = []
    destroy_previous(COMPOUND_NAME)

    wall_thickness = 60.0 * GAMEPLAY_SCALE
    half_w = config["compound_width"] * 0.5
    half_d = config["compound_depth"] * 0.5
    for suffix, offset, size in (
        ("North", vec(0.0, half_d, config["garden_wall_height"] * 0.5), vec(config["compound_width"], wall_thickness, config["garden_wall_height"])),
        ("South", vec(0.0, -half_d, config["garden_wall_height"] * 0.5), vec(config["compound_width"], wall_thickness, config["garden_wall_height"])),
        ("West", vec(-half_w, 0.0, config["garden_wall_height"] * 0.5), vec(wall_thickness, config["compound_depth"], config["garden_wall_height"])),
        ("East", vec(half_w, 0.0, config["garden_wall_height"] * 0.5), vec(wall_thickness, config["compound_depth"], config["garden_wall_height"])),
    ):
        spawn_box("{0}_Wall_{1}".format(COMPOUND_NAME, suffix), add(origin, offset), size)

    villa_origin = add(origin, vec(0.0, (config["compound_depth"] * 0.5) - (980.0 * GAMEPLAY_SCALE), 0.0))
    spawn_hall("{0}_MainVilla".format(COMPOUND_NAME), villa_origin, config["villa_width"], config["villa_depth"], config["villa_height"], detail_profile)
    spawn_box("{0}_MainPath".format(COMPOUND_NAME), add(origin, vec(0.0, 120.0 * GAMEPLAY_SCALE, 12.0 * GAMEPLAY_SCALE)), vec(320.0 * GAMEPLAY_SCALE, config["compound_depth"] * 0.82, 24.0 * GAMEPLAY_SCALE))
    pond_center = add(origin, vec(0.0, -420.0 * GAMEPLAY_SCALE, 22.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_Pond".format(COMPOUND_NAME), pond_center, vec(config["pond_width"], config["pond_depth"], 44.0 * GAMEPLAY_SCALE))
    bridge_center = add(origin, vec(0.0, -420.0 * GAMEPLAY_SCALE, 52.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_Bridge".format(COMPOUND_NAME), bridge_center, vec(260.0 * GAMEPLAY_SCALE, config["pond_depth"] * 0.92, 24.0 * GAMEPLAY_SCALE))

    if detail_profile["add_bridge_rails"]:
        rail_size = vec(24.0 * GAMEPLAY_SCALE, config["pond_depth"] * 0.92, 90.0 * GAMEPLAY_SCALE)
        spawn_box("{0}_BridgeRail_L".format(COMPOUND_NAME), add(bridge_center, vec(-120.0 * GAMEPLAY_SCALE, 0.0, 45.0 * GAMEPLAY_SCALE)), rail_size)
        spawn_box("{0}_BridgeRail_R".format(COMPOUND_NAME), add(bridge_center, vec(120.0 * GAMEPLAY_SCALE, 0.0, 45.0 * GAMEPLAY_SCALE)), rail_size)

    side_offset_x = (config["compound_width"] * 0.5) - (config["side_pavilion_width"] * 0.92)
    for suffix, direction in (("L", -1.0), ("R", 1.0)):
        spawn_hall("{0}_SidePavilion_{1}".format(COMPOUND_NAME, suffix), add(origin, vec(side_offset_x * direction, -80.0 * GAMEPLAY_SCALE, 0.0)), config["side_pavilion_width"], config["side_pavilion_depth"], config["side_pavilion_height"], detail_profile)

    if detail_profile["add_lanterns"]:
        lantern_size = vec(70.0 * GAMEPLAY_SCALE, 70.0 * GAMEPLAY_SCALE, 210.0 * GAMEPLAY_SCALE)
        for suffix, direction in (("L", -1.0), ("R", 1.0)):
            spawn_box("{0}_Lantern_{1}".format(COMPOUND_NAME, suffix), add(origin, vec((config["villa_width"] * 0.26) * direction, (config["compound_depth"] * 0.5) - (config["villa_depth"] * 1.28), lantern_size.z * 0.5)), lantern_size)

    if detail_profile["add_tree_clusters"]:
        tree_size = vec(160.0 * GAMEPLAY_SCALE, 160.0 * GAMEPLAY_SCALE, 220.0 * GAMEPLAY_SCALE)
        for index, (x_pos, y_pos) in enumerate(((-side_offset_x * 0.75, 820.0 * GAMEPLAY_SCALE), (side_offset_x * 0.75, 820.0 * GAMEPLAY_SCALE), (-side_offset_x * 0.7, -980.0 * GAMEPLAY_SCALE), (side_offset_x * 0.7, -980.0 * GAMEPLAY_SCALE))):
            spawn_box("{0}_Tree_{1}".format(COMPOUND_NAME, index + 1), add(origin, vec(x_pos, y_pos, tree_size.z * 0.5)), tree_size)

    if detail_profile["add_screen_wall"]:
        spawn_box("{0}_ScreenWall".format(COMPOUND_NAME), add(origin, vec(0.0, config["compound_depth"] * 0.16, config["garden_wall_height"] * 0.42)), vec(config["compound_width"] * 0.18, 80.0 * GAMEPLAY_SCALE, config["garden_wall_height"] * 0.84))

    if detail_profile["add_moon_gate"]:
        spawn_box("{0}_MoonGateLintel".format(COMPOUND_NAME), add(origin, vec(0.0, -(config["compound_depth"] * 0.42), config["garden_wall_height"] + (70.0 * GAMEPLAY_SCALE))), vec(config["compound_width"] * 0.18, 80.0 * GAMEPLAY_SCALE, 70.0 * GAMEPLAY_SCALE))
        spawn_box("{0}_MoonGatePier_L".format(COMPOUND_NAME), add(origin, vec(-(config["compound_width"] * 0.09), -(config["compound_depth"] * 0.42), config["garden_wall_height"] * 0.5)), vec(90.0 * GAMEPLAY_SCALE, 80.0 * GAMEPLAY_SCALE, config["garden_wall_height"]))
        spawn_box("{0}_MoonGatePier_R".format(COMPOUND_NAME), add(origin, vec(config["compound_width"] * 0.09, -(config["compound_depth"] * 0.42), config["garden_wall_height"] * 0.5)), vec(90.0 * GAMEPLAY_SCALE, 80.0 * GAMEPLAY_SCALE, config["garden_wall_height"]))

    if detail_profile["add_pond_edge"]:
        spawn_box("{0}_PondEdge".format(COMPOUND_NAME), add(pond_center, vec(0.0, 0.0, 28.0 * GAMEPLAY_SCALE)), vec(config["pond_width"] * 1.08, config["pond_depth"] * 1.08, 16.0 * GAMEPLAY_SCALE))

    if detail_profile["add_forecourt"]:
        spawn_box("{0}_Forecourt".format(COMPOUND_NAME), add(origin, vec(0.0, config["compound_depth"] * 0.28, 16.0 * GAMEPLAY_SCALE)), vec(config["villa_width"] * 0.52, config["villa_depth"] * 0.22, 32.0 * GAMEPLAY_SCALE))

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
build_villa_retreat(spawn_origin)

print("{0} ({1}, {2}) generated at {3}".format(COMPOUND_NAME, PRESET_NAME, resolve_detail_mode(), spawn_origin))
