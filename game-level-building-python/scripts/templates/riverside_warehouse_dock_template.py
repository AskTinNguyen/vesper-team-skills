import unreal


COMPOUND_NAME = "RiversideWarehouseDock"
PRESET_NAME = "river_port"
DETAIL_MODE = "blockout"
GAMEPLAY_SCALE = 3.0

PRESETS = {
    "river_port": {
        "dock_width": 5200.0,
        "dock_depth": 1800.0,
        "water_strip_depth": 1200.0,
        "warehouse_width": 1200.0,
        "warehouse_depth": 900.0,
        "warehouse_height": 340.0,
        "shed_width": 820.0,
        "shed_depth": 720.0,
        "shed_height": 260.0,
        "tower_height": 640.0,
    },
    "supply_quay": {
        "dock_width": 6000.0,
        "dock_depth": 2000.0,
        "water_strip_depth": 1400.0,
        "warehouse_width": 1400.0,
        "warehouse_depth": 980.0,
        "warehouse_height": 380.0,
        "shed_width": 880.0,
        "shed_depth": 760.0,
        "shed_height": 280.0,
        "tower_height": 720.0,
    },
}

DETAIL_PROFILES = {
    "blockout": {"add_pier_posts": False, "add_roof_caps": False, "add_crates": False, "add_gantry_frames": False, "add_watch_caps": False, "add_loading_ramps": False, "add_quay_gate": False, "add_river_edge_markers": False},
    "low": {"add_pier_posts": True, "add_roof_caps": True, "add_crates": False, "add_gantry_frames": False, "add_watch_caps": False, "add_loading_ramps": False, "add_quay_gate": False, "add_river_edge_markers": False},
    "medium": {"add_pier_posts": True, "add_roof_caps": True, "add_crates": True, "add_gantry_frames": True, "add_watch_caps": True, "add_loading_ramps": False, "add_quay_gate": False, "add_river_edge_markers": False},
    "high": {"add_pier_posts": True, "add_roof_caps": True, "add_crates": True, "add_gantry_frames": True, "add_watch_caps": True, "add_loading_ramps": True, "add_quay_gate": True, "add_river_edge_markers": True},
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


def build_riverside_dock(origin):
    config = get_config()
    detail_profile = get_detail_profile()
    generated_actors[:] = []
    destroy_previous(COMPOUND_NAME)

    dock_center = add(origin, vec(0.0, 0.0, 40.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_DockPlatform".format(COMPOUND_NAME), dock_center, vec(config["dock_width"], config["dock_depth"], 80.0 * GAMEPLAY_SCALE))
    water_center = add(origin, vec(0.0, -(config["dock_depth"] * 0.5) - (config["water_strip_depth"] * 0.5), 10.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_WaterBand".format(COMPOUND_NAME), water_center, vec(config["dock_width"] * 1.15, config["water_strip_depth"], 20.0 * GAMEPLAY_SCALE))

    pier_width = 260.0 * GAMEPLAY_SCALE
    for index in range(3):
        x_pos = (index - 1) * (config["dock_width"] * 0.24)
        pier_center = add(origin, vec(x_pos, -(config["dock_depth"] * 0.5) - (config["water_strip_depth"] * 0.35), 30.0 * GAMEPLAY_SCALE))
        pier_size = vec(pier_width, config["water_strip_depth"] * 0.7, 60.0 * GAMEPLAY_SCALE)
        spawn_box("{0}_Pier_{1}".format(COMPOUND_NAME, index + 1), pier_center, pier_size)
        if detail_profile["add_pier_posts"]:
            post_size = vec(32.0 * GAMEPLAY_SCALE, 32.0 * GAMEPLAY_SCALE, 180.0 * GAMEPLAY_SCALE)
            for suffix, direction in (("L", -1.0), ("R", 1.0)):
                spawn_box("{0}_Pier_{1}_Post_{2}".format(COMPOUND_NAME, index + 1, suffix), add(pier_center, vec((pier_width * 0.34) * direction, pier_size.y * 0.34, post_size.z * 0.5)), post_size)

    rear_y = (config["dock_depth"] * 0.5) + (config["warehouse_depth"] * 0.7)
    for index in range(3):
        x_pos = (index - 1) * (config["warehouse_width"] + (220.0 * GAMEPLAY_SCALE))
        label = "{0}_Warehouse_{1}".format(COMPOUND_NAME, index + 1)
        center = add(origin, vec(x_pos, rear_y, config["warehouse_height"] * 0.5))
        size = vec(config["warehouse_width"], config["warehouse_depth"], config["warehouse_height"])
        spawn_box(label, center, size)
        if detail_profile["add_roof_caps"]:
            spawn_box(label + "_RoofCap", add(center, vec(0.0, 0.0, config["warehouse_height"] * 0.58)), vec(size.x * 1.06, size.y * 1.02, 40.0 * GAMEPLAY_SCALE))

    shed_row_y = 140.0 * GAMEPLAY_SCALE
    for index in range(4):
        x_pos = (index - 1.5) * (config["shed_width"] + (180.0 * GAMEPLAY_SCALE))
        label = "{0}_Shed_{1}".format(COMPOUND_NAME, index + 1)
        center = add(origin, vec(x_pos, shed_row_y, config["shed_height"] * 0.5))
        size = vec(config["shed_width"], config["shed_depth"], config["shed_height"])
        spawn_box(label, center, size)
        if detail_profile["add_gantry_frames"]:
            spawn_box(label + "_FrameBeam", add(center, vec(0.0, -(config["shed_depth"] * 0.44), config["shed_height"] + (24.0 * GAMEPLAY_SCALE))), vec(size.x * 0.78, 80.0 * GAMEPLAY_SCALE, 48.0 * GAMEPLAY_SCALE))

    if detail_profile["add_crates"]:
        crate_size = vec(180.0 * GAMEPLAY_SCALE, 180.0 * GAMEPLAY_SCALE, 120.0 * GAMEPLAY_SCALE)
        for index in range(5):
            spawn_box("{0}_Crate_{1}".format(COMPOUND_NAME, index + 1), add(origin, vec((index - 2) * (260.0 * GAMEPLAY_SCALE), config["dock_depth"] * 0.1, crate_size.z * 0.5)), crate_size)

    tower_offset_x = (config["dock_width"] * 0.5) - (260.0 * GAMEPLAY_SCALE)
    for suffix, direction in (("L", -1.0), ("R", 1.0)):
        label = "{0}_WatchTower_{1}".format(COMPOUND_NAME, suffix)
        center = add(origin, vec(tower_offset_x * direction, rear_y + (220.0 * GAMEPLAY_SCALE), config["tower_height"] * 0.5))
        size = vec(240.0 * GAMEPLAY_SCALE, 240.0 * GAMEPLAY_SCALE, config["tower_height"])
        spawn_box(label, center, size)
        if detail_profile["add_watch_caps"]:
            spawn_box(label + "_Cap", add(center, vec(0.0, 0.0, config["tower_height"] * 0.5 + (24.0 * GAMEPLAY_SCALE))), vec(size.x * 1.08, size.y * 1.08, 40.0 * GAMEPLAY_SCALE))

    if detail_profile["add_loading_ramps"]:
        spawn_box("{0}_LoadingRamp".format(COMPOUND_NAME), add(origin, vec(0.0, config["dock_depth"] * 0.42, 28.0 * GAMEPLAY_SCALE)), vec(config["dock_width"] * 0.42, 180.0 * GAMEPLAY_SCALE, 56.0 * GAMEPLAY_SCALE))

    if detail_profile["add_quay_gate"]:
        spawn_box("{0}_QuayGateBeam".format(COMPOUND_NAME), add(origin, vec(0.0, rear_y + (config["warehouse_depth"] * 0.62), config["warehouse_height"] + (140.0 * GAMEPLAY_SCALE))), vec(config["dock_width"] * 0.26, 100.0 * GAMEPLAY_SCALE, 90.0 * GAMEPLAY_SCALE))
        for suffix, direction in (("L", -1.0), ("R", 1.0)):
            spawn_box("{0}_QuayGatePier_{1}".format(COMPOUND_NAME, suffix), add(origin, vec((config["dock_width"] * 0.13) * direction, rear_y + (config["warehouse_depth"] * 0.62), config["warehouse_height"] * 0.72)), vec(100.0 * GAMEPLAY_SCALE, 100.0 * GAMEPLAY_SCALE, config["warehouse_height"] * 1.44))

    if detail_profile["add_river_edge_markers"]:
        marker_size = vec(80.0 * GAMEPLAY_SCALE, 80.0 * GAMEPLAY_SCALE, 200.0 * GAMEPLAY_SCALE)
        for index in range(4):
            x_pos = (index - 1.5) * (config["dock_width"] * 0.2)
            spawn_box("{0}_RiverMarker_{1}".format(COMPOUND_NAME, index + 1), add(origin, vec(x_pos, -(config["dock_depth"] * 0.5) - (config["water_strip_depth"] * 0.86), marker_size.z * 0.5)), marker_size)

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
build_riverside_dock(spawn_origin)

print("{0} ({1}, {2}) generated at {3}".format(COMPOUND_NAME, PRESET_NAME, resolve_detail_mode(), spawn_origin))
