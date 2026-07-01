import unreal


COMPOUND_NAME = "CityWallGateDistrict"
PRESET_NAME = "market_gate"
DETAIL_MODE = "blockout"
GAMEPLAY_SCALE = 3.0

PRESETS = {
    "market_gate": {
        "wall_span": 5200.0,
        "wall_height": 260.0,
        "gate_width": 1300.0,
        "gate_depth": 900.0,
        "gate_height": 620.0,
        "tower_height": 820.0,
        "street_width": 1100.0,
        "shop_width": 820.0,
        "shop_depth": 760.0,
        "shop_height": 300.0,
    },
    "military_gate": {
        "wall_span": 5600.0,
        "wall_height": 300.0,
        "gate_width": 1500.0,
        "gate_depth": 980.0,
        "gate_height": 720.0,
        "tower_height": 960.0,
        "street_width": 1200.0,
        "shop_width": 860.0,
        "shop_depth": 820.0,
        "shop_height": 340.0,
    },
}

DETAIL_PROFILES = {
    "blockout": {"add_parapets": False, "add_awning_rows": False, "add_lantern_rows": False, "add_guard_platforms": False, "add_market_stalls": False, "add_gate_frame": False, "add_barbican": False, "add_screen_nodes": False},
    "low": {"add_parapets": True, "add_awning_rows": True, "add_lantern_rows": False, "add_guard_platforms": False, "add_market_stalls": False, "add_gate_frame": True, "add_barbican": False, "add_screen_nodes": False},
    "medium": {"add_parapets": True, "add_awning_rows": True, "add_lantern_rows": True, "add_guard_platforms": True, "add_market_stalls": True, "add_gate_frame": True, "add_barbican": False, "add_screen_nodes": False},
    "high": {"add_parapets": True, "add_awning_rows": True, "add_lantern_rows": True, "add_guard_platforms": True, "add_market_stalls": True, "add_gate_frame": True, "add_barbican": True, "add_screen_nodes": True},
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


def build_city_gate_district(origin):
    config = get_config()
    detail_profile = get_detail_profile()
    generated_actors[:] = []
    destroy_previous(COMPOUND_NAME)

    wall_thickness = 110.0 * GAMEPLAY_SCALE
    south_y = -(config["gate_depth"] * 0.5)
    side_span = (config["wall_span"] - config["gate_width"]) * 0.5

    left_wall_center = add(origin, vec(-(config["gate_width"] + side_span) * 0.5, south_y, config["wall_height"] * 0.5))
    right_wall_center = add(origin, vec((config["gate_width"] + side_span) * 0.5, south_y, config["wall_height"] * 0.5))
    left_wall_size = vec(side_span, wall_thickness, config["wall_height"])
    right_wall_size = vec(side_span, wall_thickness, config["wall_height"])
    spawn_box("{0}_Wall_L".format(COMPOUND_NAME), left_wall_center, left_wall_size)
    spawn_box("{0}_Wall_R".format(COMPOUND_NAME), right_wall_center, right_wall_size)
    if detail_profile["add_parapets"]:
        spawn_box("{0}_Wall_L_Parapet".format(COMPOUND_NAME), add(left_wall_center, vec(0.0, 0.0, config["wall_height"] + (28.0 * GAMEPLAY_SCALE))), vec(left_wall_size.x * 0.94, left_wall_size.y * 0.96, 36.0 * GAMEPLAY_SCALE))
        spawn_box("{0}_Wall_R_Parapet".format(COMPOUND_NAME), add(right_wall_center, vec(0.0, 0.0, config["wall_height"] + (28.0 * GAMEPLAY_SCALE))), vec(right_wall_size.x * 0.94, right_wall_size.y * 0.96, 36.0 * GAMEPLAY_SCALE))

    gate_origin = origin
    spawn_box("{0}_Gatehouse".format(COMPOUND_NAME), add(gate_origin, vec(0.0, 0.0, config["gate_height"] * 0.5)), vec(config["gate_width"], config["gate_depth"], config["gate_height"]))
    spawn_box("{0}_GateRoof".format(COMPOUND_NAME), add(gate_origin, vec(0.0, 0.0, config["gate_height"] + (90.0 * GAMEPLAY_SCALE))), vec(config["gate_width"] * 1.08, config["gate_depth"] * 1.1, 80.0 * GAMEPLAY_SCALE))
    if detail_profile["add_gate_frame"]:
        spawn_box("{0}_GateBeam".format(COMPOUND_NAME), add(gate_origin, vec(0.0, -(config["gate_depth"] * 0.45), config["gate_height"] * 0.82)), vec(config["gate_width"] * 0.72, 90.0 * GAMEPLAY_SCALE, 70.0 * GAMEPLAY_SCALE))
        for suffix, direction in (("L", -1.0), ("R", 1.0)):
            spawn_box("{0}_GatePier_{1}".format(COMPOUND_NAME, suffix), add(gate_origin, vec((config["gate_width"] * 0.34) * direction, -(config["gate_depth"] * 0.45), config["gate_height"] * 0.41)), vec(90.0 * GAMEPLAY_SCALE, 90.0 * GAMEPLAY_SCALE, config["gate_height"] * 0.82))

    tower_size = vec(260.0 * GAMEPLAY_SCALE, 260.0 * GAMEPLAY_SCALE, config["tower_height"])
    tower_offset_x = (config["gate_width"] * 0.5) + (tower_size.x * 0.7)
    for suffix, direction in (("L", -1.0), ("R", 1.0)):
        tower_center = add(origin, vec(tower_offset_x * direction, 0.0, tower_size.z * 0.5))
        spawn_box("{0}_Tower_{1}".format(COMPOUND_NAME, suffix), tower_center, tower_size)
        if detail_profile["add_guard_platforms"]:
            spawn_box("{0}_Tower_{1}_Cap".format(COMPOUND_NAME, suffix), add(tower_center, vec(0.0, 0.0, tower_size.z * 0.5 + (30.0 * GAMEPLAY_SCALE))), vec(tower_size.x * 1.08, tower_size.y * 1.08, 40.0 * GAMEPLAY_SCALE))

    street_y = config["gate_depth"] * 1.2
    spawn_box("{0}_MainStreet".format(COMPOUND_NAME), add(origin, vec(0.0, street_y, 20.0 * GAMEPLAY_SCALE)), vec(config["street_width"], 3200.0 * GAMEPLAY_SCALE, 40.0 * GAMEPLAY_SCALE))

    row_offset_x = (config["street_width"] * 0.5) + (config["shop_width"] * 0.65)
    for row in range(4):
        y_pos = street_y + (row * (config["shop_depth"] + (220.0 * GAMEPLAY_SCALE)))
        for suffix, direction in (("L", -1.0), ("R", 1.0)):
            label = "{0}_Shop_{1}_{2}".format(COMPOUND_NAME, suffix, row + 1)
            shop_center = add(origin, vec(row_offset_x * direction, y_pos, config["shop_height"] * 0.5))
            shop_size = vec(config["shop_width"], config["shop_depth"], config["shop_height"])
            spawn_box(label, shop_center, shop_size)
            if detail_profile["add_awning_rows"]:
                spawn_box(label + "_Awning", add(shop_center, vec(0.0, -(config["shop_depth"] * 0.38), config["shop_height"] * 0.6)), vec(config["shop_width"] * 1.04, config["shop_depth"] * 0.24, 28.0 * GAMEPLAY_SCALE))

    if detail_profile["add_lantern_rows"]:
        lantern_size = vec(60.0 * GAMEPLAY_SCALE, 60.0 * GAMEPLAY_SCALE, 220.0 * GAMEPLAY_SCALE)
        for row in range(5):
            y_pos = street_y + (row * (540.0 * GAMEPLAY_SCALE))
            for suffix, direction in (("L", -1.0), ("R", 1.0)):
                spawn_box("{0}_Lantern_{1}_{2}".format(COMPOUND_NAME, suffix, row + 1), add(origin, vec((config["street_width"] * 0.7) * direction, y_pos, lantern_size.z * 0.5)), lantern_size)

    if detail_profile["add_market_stalls"]:
        stall_size = vec(config["shop_width"] * 0.72, config["shop_depth"] * 0.28, config["shop_height"] * 0.44)
        for row in range(3):
            y_pos = street_y + (row * (760.0 * GAMEPLAY_SCALE)) + (180.0 * GAMEPLAY_SCALE)
            spawn_box("{0}_StreetStall_L_{1}".format(COMPOUND_NAME, row + 1), add(origin, vec(-(config["street_width"] * 0.9), y_pos, stall_size.z * 0.5)), stall_size)
            spawn_box("{0}_StreetStall_R_{1}".format(COMPOUND_NAME, row + 1), add(origin, vec(config["street_width"] * 0.9, y_pos, stall_size.z * 0.5)), stall_size)

    if detail_profile["add_barbican"]:
        spawn_box("{0}_Barbican".format(COMPOUND_NAME), add(origin, vec(0.0, -(config["gate_depth"] * 0.86), config["gate_height"] * 0.32)), vec(config["gate_width"] * 1.2, 360.0 * GAMEPLAY_SCALE, config["gate_height"] * 0.64))

    if detail_profile["add_screen_nodes"]:
        screen_size = vec(config["street_width"] * 0.58, 80.0 * GAMEPLAY_SCALE, config["wall_height"] * 0.72)
        spawn_box("{0}_ScreenNorth".format(COMPOUND_NAME), add(origin, vec(0.0, street_y + (2800.0 * GAMEPLAY_SCALE), screen_size.z * 0.5)), screen_size)
        spawn_box("{0}_ScreenSouth".format(COMPOUND_NAME), add(origin, vec(0.0, street_y - (240.0 * GAMEPLAY_SCALE), screen_size.z * 0.5)), screen_size)

    spawn_box("{0}_RearTower".format(COMPOUND_NAME), add(origin, vec(0.0, street_y + (3000.0 * GAMEPLAY_SCALE), (config["tower_height"] * 0.8) * 0.5)), vec(360.0 * GAMEPLAY_SCALE, 360.0 * GAMEPLAY_SCALE, config["tower_height"] * 0.8))
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
build_city_gate_district(spawn_origin)

print("{0} ({1}, {2}) generated at {3}".format(COMPOUND_NAME, PRESET_NAME, resolve_detail_mode(), spawn_origin))
