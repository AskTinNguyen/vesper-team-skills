import unreal


COMPOUND_NAME = "InnerCityWardBlock"
PRESET_NAME = "market_residential_ward"
DETAIL_MODE = "blockout"
GAMEPLAY_SCALE = 3.0

PRESETS = {
    "market_residential_ward": {
        "block_width": 5200.0,
        "block_depth": 4200.0,
        "main_street_width": 920.0,
        "alley_width": 420.0,
        "wall_height": 150.0,
        "shop_width": 820.0,
        "shop_depth": 720.0,
        "shop_height": 300.0,
        "courtyard_width": 980.0,
        "courtyard_depth": 920.0,
        "courtyard_height": 260.0,
    },
    "artisan_lane_block": {
        "block_width": 5600.0,
        "block_depth": 4600.0,
        "main_street_width": 1000.0,
        "alley_width": 480.0,
        "wall_height": 170.0,
        "shop_width": 900.0,
        "shop_depth": 760.0,
        "shop_height": 320.0,
        "courtyard_width": 1080.0,
        "courtyard_depth": 980.0,
        "courtyard_height": 280.0,
    },
}

DETAIL_PROFILES = {
    "blockout": {
        "add_shop_awning": False,
        "add_lane_walls": False,
        "add_gate_frames": False,
        "add_lantern_rows": False,
        "add_market_stalls": False,
        "add_tree_markers": False,
        "add_screen_walls": False,
        "add_entry_nodes": False,
        "add_secondary_crossings": False,
        "add_court_layers": False,
    },
    "low": {
        "add_shop_awning": True,
        "add_lane_walls": True,
        "add_gate_frames": True,
        "add_lantern_rows": False,
        "add_market_stalls": False,
        "add_tree_markers": False,
        "add_screen_walls": False,
        "add_entry_nodes": False,
        "add_secondary_crossings": False,
        "add_court_layers": False,
    },
    "medium": {
        "add_shop_awning": True,
        "add_lane_walls": True,
        "add_gate_frames": True,
        "add_lantern_rows": True,
        "add_market_stalls": True,
        "add_tree_markers": True,
        "add_screen_walls": False,
        "add_entry_nodes": False,
        "add_secondary_crossings": False,
        "add_court_layers": False,
    },
    "high": {
        "add_shop_awning": True,
        "add_lane_walls": True,
        "add_gate_frames": True,
        "add_lantern_rows": True,
        "add_market_stalls": True,
        "add_tree_markers": True,
        "add_screen_walls": True,
        "add_entry_nodes": True,
        "add_secondary_crossings": True,
        "add_court_layers": True,
    },
}

DETAIL_ALIASES = {
    "ornamented": "medium",
}

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


def spawn_wall_ring(origin, width, depth, wall_height):
    thickness = 60.0 * GAMEPLAY_SCALE
    half_w = width * 0.5
    half_d = depth * 0.5
    for suffix, offset, size in (
        ("North", vec(0.0, half_d, wall_height * 0.5), vec(width, thickness, wall_height)),
        ("South", vec(0.0, -half_d, wall_height * 0.5), vec(width, thickness, wall_height)),
        ("West", vec(-half_w, 0.0, wall_height * 0.5), vec(thickness, depth, wall_height)),
        ("East", vec(half_w, 0.0, wall_height * 0.5), vec(thickness, depth, wall_height)),
    ):
        spawn_box("{0}_Wall_{1}".format(COMPOUND_NAME, suffix), add(origin, offset), size)


def build_ward_block(origin):
    config = get_config()
    detail_profile = get_detail_profile()
    generated_actors[:] = []
    destroy_previous(COMPOUND_NAME)

    spawn_wall_ring(origin, config["block_width"], config["block_depth"], config["wall_height"])
    spawn_box("{0}_MainStreet".format(COMPOUND_NAME), add(origin, vec(0.0, 0.0, 15.0 * GAMEPLAY_SCALE)), vec(config["main_street_width"], config["block_depth"] * 0.92, 30.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_CrossLane".format(COMPOUND_NAME), add(origin, vec(0.0, 0.0, 15.0 * GAMEPLAY_SCALE)), vec(config["block_width"] * 0.92, config["alley_width"], 30.0 * GAMEPLAY_SCALE))

    row_offset_x = (config["main_street_width"] * 0.5) + (config["shop_width"] * 0.7)
    row_offset_y = config["block_depth"] * 0.24
    for row_index, y_pos in enumerate((-row_offset_y, row_offset_y)):
        for column_index in range(3):
            x_base = row_offset_x + (column_index * (config["courtyard_width"] + (220.0 * GAMEPLAY_SCALE)))
            for suffix, direction in (("L", -1.0), ("R", 1.0)):
                court_label = "{0}_Court_{1}_{2}".format(COMPOUND_NAME, suffix, (row_index * 3) + column_index + 1)
                shop_label = "{0}_Shop_{1}_{2}".format(COMPOUND_NAME, suffix, (row_index * 3) + column_index + 1)
                courtyard_origin = add(origin, vec(x_base * direction, y_pos, 0.0))
                shop_origin = add(courtyard_origin, vec(0.0, -(config["courtyard_depth"] * 0.85), 0.0))
                spawn_box(court_label, add(courtyard_origin, vec(0.0, 0.0, config["courtyard_height"] * 0.5)), vec(config["courtyard_width"], config["courtyard_depth"], config["courtyard_height"]))
                spawn_box(shop_label, add(shop_origin, vec(0.0, 0.0, config["shop_height"] * 0.5)), vec(config["shop_width"], config["shop_depth"], config["shop_height"]))

                if detail_profile["add_shop_awning"]:
                    spawn_box(shop_label + "_Awning", add(shop_origin, vec(0.0, -(config["shop_depth"] * 0.4), config["shop_height"] + (24.0 * GAMEPLAY_SCALE))), vec(config["shop_width"] * 1.04, config["shop_depth"] * 0.26, 28.0 * GAMEPLAY_SCALE))

                if detail_profile["add_gate_frames"]:
                    spawn_box(court_label + "_GateBeam", add(courtyard_origin, vec(0.0, -(config["courtyard_depth"] * 0.46), config["courtyard_height"] + (28.0 * GAMEPLAY_SCALE))), vec(config["courtyard_width"] * 0.42, 60.0 * GAMEPLAY_SCALE, 56.0 * GAMEPLAY_SCALE))

                if detail_profile["add_court_layers"]:
                    spawn_box(court_label + "_RearCourt", add(courtyard_origin, vec(0.0, config["courtyard_depth"] * 0.22, config["courtyard_height"] * 0.22)), vec(config["courtyard_width"] * 0.76, config["courtyard_depth"] * 0.42, config["courtyard_height"] * 0.44))

    alley_offset_x = config["block_width"] * 0.22
    for suffix, direction in (("L", -1.0), ("R", 1.0)):
        north_center = add(origin, vec(alley_offset_x * direction, config["block_depth"] * 0.27, 15.0 * GAMEPLAY_SCALE))
        south_center = add(origin, vec(alley_offset_x * direction, -(config["block_depth"] * 0.27), 15.0 * GAMEPLAY_SCALE))
        alley_size = vec(config["alley_width"], config["block_depth"] * 0.38, 30.0 * GAMEPLAY_SCALE)
        spawn_box("{0}_NorthAlley_{1}".format(COMPOUND_NAME, suffix), north_center, alley_size)
        spawn_box("{0}_SouthAlley_{1}".format(COMPOUND_NAME, suffix), south_center, alley_size)
        if detail_profile["add_lane_walls"]:
            wall_size = vec(40.0 * GAMEPLAY_SCALE, config["block_depth"] * 0.36, config["wall_height"] * 0.72)
            spawn_box("{0}_NorthLaneWall_{1}".format(COMPOUND_NAME, suffix), add(north_center, vec((config["alley_width"] * 0.44) * direction, 0.0, wall_size.z * 0.5)), wall_size)
            spawn_box("{0}_SouthLaneWall_{1}".format(COMPOUND_NAME, suffix), add(south_center, vec((config["alley_width"] * 0.44) * direction, 0.0, wall_size.z * 0.5)), wall_size)

    if detail_profile["add_lantern_rows"]:
        lantern_size = vec(60.0 * GAMEPLAY_SCALE, 60.0 * GAMEPLAY_SCALE, 200.0 * GAMEPLAY_SCALE)
        for index in range(5):
            y_pos = -(config["block_depth"] * 0.32) + (index * (config["block_depth"] * 0.16))
            for suffix, direction in (("L", -1.0), ("R", 1.0)):
                spawn_box("{0}_Lantern_{1}_{2}".format(COMPOUND_NAME, suffix, index + 1), add(origin, vec((config["main_street_width"] * 0.62) * direction, y_pos, lantern_size.z * 0.5)), lantern_size)

    if detail_profile["add_market_stalls"]:
        stall_size = vec(config["main_street_width"] * 0.24, config["shop_depth"] * 0.34, config["shop_height"] * 0.46)
        for index in range(4):
            y_pos = -(config["block_depth"] * 0.22) + (index * (config["shop_depth"] * 0.7))
            for suffix, direction in (("L", -1.0), ("R", 1.0)):
                spawn_box("{0}_Stall_{1}_{2}".format(COMPOUND_NAME, suffix, index + 1), add(origin, vec((config["main_street_width"] * 0.8) * direction, y_pos, stall_size.z * 0.5)), stall_size)

    if detail_profile["add_tree_markers"]:
        tree_size = vec(150.0 * GAMEPLAY_SCALE, 150.0 * GAMEPLAY_SCALE, 250.0 * GAMEPLAY_SCALE)
        for index, (x_pos, y_pos) in enumerate((
            (-config["block_width"] * 0.18, config["block_depth"] * 0.34),
            (config["block_width"] * 0.18, config["block_depth"] * 0.34),
            (-config["block_width"] * 0.18, -config["block_depth"] * 0.34),
            (config["block_width"] * 0.18, -config["block_depth"] * 0.34),
        )):
            spawn_box("{0}_Tree_{1}".format(COMPOUND_NAME, index + 1), add(origin, vec(x_pos, y_pos, tree_size.z * 0.5)), tree_size)

    if detail_profile["add_screen_walls"]:
        screen_size = vec(config["block_width"] * 0.12, 70.0 * GAMEPLAY_SCALE, config["wall_height"] * 0.82)
        spawn_box("{0}_NorthScreen".format(COMPOUND_NAME), add(origin, vec(0.0, config["block_depth"] * 0.14, screen_size.z * 0.5)), screen_size)
        spawn_box("{0}_SouthScreen".format(COMPOUND_NAME), add(origin, vec(0.0, -(config["block_depth"] * 0.14), screen_size.z * 0.5)), screen_size)

    if detail_profile["add_entry_nodes"]:
        node_size = vec(config["main_street_width"] * 0.62, config["shop_depth"] * 0.42, config["wall_height"] * 0.74)
        spawn_box("{0}_NorthEntryNode".format(COMPOUND_NAME), add(origin, vec(0.0, config["block_depth"] * 0.45, node_size.z * 0.5)), node_size)
        spawn_box("{0}_SouthEntryNode".format(COMPOUND_NAME), add(origin, vec(0.0, -(config["block_depth"] * 0.45), node_size.z * 0.5)), node_size)

    if detail_profile["add_secondary_crossings"]:
        crossing_size = vec(config["block_width"] * 0.8, config["alley_width"] * 0.42, 24.0 * GAMEPLAY_SCALE)
        spawn_box("{0}_NorthCrossing".format(COMPOUND_NAME), add(origin, vec(0.0, config["block_depth"] * 0.2, 12.0 * GAMEPLAY_SCALE)), crossing_size)
        spawn_box("{0}_SouthCrossing".format(COMPOUND_NAME), add(origin, vec(0.0, -(config["block_depth"] * 0.2), 12.0 * GAMEPLAY_SCALE)), crossing_size)

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
build_ward_block(spawn_origin)

print("{0} ({1}, {2}) generated at {3}".format(COMPOUND_NAME, PRESET_NAME, resolve_detail_mode(), spawn_origin))
