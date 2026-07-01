import unreal


COMPOUND_NAME = "FortifiedPrecinct"
PRESET_NAME = "frontier_garrison"
DETAIL_MODE = "blockout"
GAMEPLAY_SCALE = 3.0

PRESETS = {
    "frontier_garrison": {
        "precinct_width": 5000.0,
        "precinct_depth": 4600.0,
        "wall_height": 240.0,
        "tower_height": 720.0,
        "gate_width": 1300.0,
        "yard_width": 2200.0,
        "yard_depth": 1600.0,
        "service_width": 1100.0,
        "service_depth": 900.0,
        "service_height": 320.0,
    },
    "granary_fort": {
        "precinct_width": 5600.0,
        "precinct_depth": 5200.0,
        "wall_height": 260.0,
        "tower_height": 780.0,
        "gate_width": 1500.0,
        "yard_width": 2500.0,
        "yard_depth": 1700.0,
        "service_width": 1200.0,
        "service_depth": 980.0,
        "service_height": 360.0,
    },
}

DETAIL_PROFILES = {
    "blockout": {"add_parapets": False, "add_gate_frame": False, "add_yard_barricades": False, "add_tower_caps": False, "add_supply_racks": False, "add_barbican": False, "add_catwalks": False, "add_command_platform": False},
    "low": {"add_parapets": True, "add_gate_frame": True, "add_yard_barricades": False, "add_tower_caps": False, "add_supply_racks": False, "add_barbican": False, "add_catwalks": False, "add_command_platform": False},
    "medium": {"add_parapets": True, "add_gate_frame": True, "add_yard_barricades": True, "add_tower_caps": True, "add_supply_racks": True, "add_barbican": False, "add_catwalks": False, "add_command_platform": False},
    "high": {"add_parapets": True, "add_gate_frame": True, "add_yard_barricades": True, "add_tower_caps": True, "add_supply_racks": True, "add_barbican": True, "add_catwalks": True, "add_command_platform": True},
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


def spawn_wall_segments(origin, width, depth, wall_height, gate_width, detail_profile):
    thickness = 90.0 * GAMEPLAY_SCALE
    half_w = width * 0.5
    half_d = depth * 0.5
    side_segment_width = (width - gate_width) * 0.5
    pieces = (
        ("NorthWall", vec(0.0, half_d, wall_height * 0.5), vec(width, thickness, wall_height)),
        ("WestWall", vec(-half_w, 0.0, wall_height * 0.5), vec(thickness, depth, wall_height)),
        ("EastWall", vec(half_w, 0.0, wall_height * 0.5), vec(thickness, depth, wall_height)),
        ("SouthWall_L", vec(-(gate_width + side_segment_width) * 0.5, -half_d, wall_height * 0.5), vec(side_segment_width, thickness, wall_height)),
        ("SouthWall_R", vec((gate_width + side_segment_width) * 0.5, -half_d, wall_height * 0.5), vec(side_segment_width, thickness, wall_height)),
    )
    for suffix, offset, size in pieces:
        spawn_box("{0}_{1}".format(COMPOUND_NAME, suffix), add(origin, offset), size)
        if detail_profile["add_parapets"]:
            spawn_box("{0}_{1}_Parapet".format(COMPOUND_NAME, suffix), add(origin, vec(offset.x, offset.y, wall_height + (30.0 * GAMEPLAY_SCALE))), vec(size.x * 0.96, size.y * 0.96, 40.0 * GAMEPLAY_SCALE))


def spawn_towers(origin, width, depth, tower_height, detail_profile):
    tower_size = vec(280.0 * GAMEPLAY_SCALE, 280.0 * GAMEPLAY_SCALE, tower_height)
    offset_x = (width * 0.5) - tower_size.x * 0.6
    offset_y = (depth * 0.5) - tower_size.y * 0.6
    for index, (x_pos, y_pos) in enumerate(((-offset_x, -offset_y), (-offset_x, offset_y), (offset_x, -offset_y), (offset_x, offset_y))):
        label = "{0}_Tower_{1}".format(COMPOUND_NAME, index + 1)
        spawn_box(label, add(origin, vec(x_pos, y_pos, tower_size.z * 0.5)), tower_size)
        if detail_profile["add_tower_caps"]:
            spawn_box(label + "_Cap", add(origin, vec(x_pos, y_pos, tower_height + (36.0 * GAMEPLAY_SCALE))), vec(tower_size.x * 1.08, tower_size.y * 1.08, 48.0 * GAMEPLAY_SCALE))


def spawn_gatehouse(origin, gate_width, detail_profile):
    spawn_box("{0}_Gatehouse".format(COMPOUND_NAME), add(origin, vec(0.0, 0.0, 280.0 * GAMEPLAY_SCALE)), vec(gate_width, 700.0 * GAMEPLAY_SCALE, 560.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_GateRoof".format(COMPOUND_NAME), add(origin, vec(0.0, 0.0, 620.0 * GAMEPLAY_SCALE)), vec(gate_width * 1.08, 860.0 * GAMEPLAY_SCALE, 90.0 * GAMEPLAY_SCALE))
    if detail_profile["add_gate_frame"]:
        spawn_box("{0}_GateBeam".format(COMPOUND_NAME), add(origin, vec(0.0, -(360.0 * GAMEPLAY_SCALE), 520.0 * GAMEPLAY_SCALE)), vec(gate_width * 0.72, 90.0 * GAMEPLAY_SCALE, 70.0 * GAMEPLAY_SCALE))
        for suffix, direction in (("L", -1.0), ("R", 1.0)):
            spawn_box("{0}_GatePier_{1}".format(COMPOUND_NAME, suffix), add(origin, vec((gate_width * 0.36) * direction, -(360.0 * GAMEPLAY_SCALE), 280.0 * GAMEPLAY_SCALE)), vec(90.0 * GAMEPLAY_SCALE, 90.0 * GAMEPLAY_SCALE, 560.0 * GAMEPLAY_SCALE))


def spawn_service_blocks(origin, config, detail_profile):
    left_x = -(config["precinct_width"] * 0.5) + (config["service_width"] * 0.9)
    right_x = -left_x
    rear_y = (config["precinct_depth"] * 0.5) - (config["service_depth"] * 1.0)
    front_y = -(config["precinct_depth"] * 0.5) + config["service_depth"] * 1.2
    for index, (x_pos, y_pos) in enumerate(((left_x, rear_y), (right_x, rear_y), (left_x, front_y), (right_x, front_y))):
        label = "{0}_Service_{1}".format(COMPOUND_NAME, index + 1)
        spawn_box(label, add(origin, vec(x_pos, y_pos, config["service_height"] * 0.5)), vec(config["service_width"], config["service_depth"], config["service_height"]))
        if detail_profile["add_supply_racks"]:
            spawn_box(label + "_Rack", add(origin, vec(x_pos, y_pos - (config["service_depth"] * 0.44), config["service_height"] + (22.0 * GAMEPLAY_SCALE))), vec(config["service_width"] * 0.82, 80.0 * GAMEPLAY_SCALE, 44.0 * GAMEPLAY_SCALE))


def build_fortified_precinct(origin):
    config = get_config()
    detail_profile = get_detail_profile()
    generated_actors[:] = []
    destroy_previous(COMPOUND_NAME)

    gate_origin = add(origin, vec(0.0, -(config["precinct_depth"] * 0.5) + (380.0 * GAMEPLAY_SCALE), 0.0))
    spawn_wall_segments(origin, config["precinct_width"], config["precinct_depth"], config["wall_height"], config["gate_width"], detail_profile)
    spawn_towers(origin, config["precinct_width"], config["precinct_depth"], config["tower_height"], detail_profile)
    spawn_gatehouse(gate_origin, config["gate_width"], detail_profile)
    spawn_box("{0}_DrillYard".format(COMPOUND_NAME), add(origin, vec(0.0, 0.0, 15.0 * GAMEPLAY_SCALE)), vec(config["yard_width"], config["yard_depth"], 30.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_RearKeep".format(COMPOUND_NAME), add(origin, vec(0.0, (config["precinct_depth"] * 0.5) - (900.0 * GAMEPLAY_SCALE), 340.0 * GAMEPLAY_SCALE)), vec(config["service_width"] * 1.6, config["service_depth"] * 1.3, 680.0 * GAMEPLAY_SCALE))
    spawn_service_blocks(origin, config, detail_profile)

    if detail_profile["add_yard_barricades"]:
        barricade_size = vec(config["yard_width"] * 0.24, 90.0 * GAMEPLAY_SCALE, 80.0 * GAMEPLAY_SCALE)
        spawn_box("{0}_Barricade_North".format(COMPOUND_NAME), add(origin, vec(0.0, config["yard_depth"] * 0.22, barricade_size.z * 0.5)), barricade_size)
        spawn_box("{0}_Barricade_South".format(COMPOUND_NAME), add(origin, vec(0.0, -(config["yard_depth"] * 0.22), barricade_size.z * 0.5)), barricade_size)

    if detail_profile["add_barbican"]:
        spawn_box("{0}_Barbican".format(COMPOUND_NAME), add(gate_origin, vec(0.0, -(config["gate_width"] * 0.42), 180.0 * GAMEPLAY_SCALE)), vec(config["gate_width"] * 1.16, 320.0 * GAMEPLAY_SCALE, 360.0 * GAMEPLAY_SCALE))

    if detail_profile["add_catwalks"]:
        spawn_box("{0}_WestCatwalk".format(COMPOUND_NAME), add(origin, vec(-(config["precinct_width"] * 0.34), 0.0, config["wall_height"] + (18.0 * GAMEPLAY_SCALE))), vec(120.0 * GAMEPLAY_SCALE, config["precinct_depth"] * 0.72, 36.0 * GAMEPLAY_SCALE))
        spawn_box("{0}_EastCatwalk".format(COMPOUND_NAME), add(origin, vec(config["precinct_width"] * 0.34, 0.0, config["wall_height"] + (18.0 * GAMEPLAY_SCALE))), vec(120.0 * GAMEPLAY_SCALE, config["precinct_depth"] * 0.72, 36.0 * GAMEPLAY_SCALE))

    if detail_profile["add_command_platform"]:
        spawn_box("{0}_CommandPlatform".format(COMPOUND_NAME), add(origin, vec(0.0, config["yard_depth"] * 0.34, 70.0 * GAMEPLAY_SCALE)), vec(config["yard_width"] * 0.36, config["yard_depth"] * 0.14, 140.0 * GAMEPLAY_SCALE))

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


spawn_origin = get_spawn_origin(3400.0)
build_fortified_precinct(spawn_origin)

print("{0} ({1}, {2}) generated at {3}".format(COMPOUND_NAME, PRESET_NAME, resolve_detail_mode(), spawn_origin))
