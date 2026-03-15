import unreal


COMPOUND_NAME = "FormalGardenCourt"
PRESET_NAME = "ritual_pond_court"
DETAIL_MODE = "blockout"
GAMEPLAY_SCALE = 3.0

PRESETS = {
    "ritual_pond_court": {
        "court_width": 3600.0,
        "court_depth": 3000.0,
        "wall_height": 140.0,
        "pond_width": 1200.0,
        "pond_depth": 820.0,
        "pavilion_width": 760.0,
        "pavilion_depth": 760.0,
        "pavilion_height": 340.0,
        "tree_count": 6,
    },
    "noble_respite_court": {
        "court_width": 4200.0,
        "court_depth": 3400.0,
        "wall_height": 160.0,
        "pond_width": 1500.0,
        "pond_depth": 920.0,
        "pavilion_width": 820.0,
        "pavilion_depth": 820.0,
        "pavilion_height": 380.0,
        "tree_count": 8,
    },
}

DETAIL_PROFILES = {
    "blockout": {
        "add_pavilion_eaves": False,
        "add_lanterns": False,
        "add_bridge_rails": False,
        "add_pond_edge": False,
        "add_path_posts": False,
        "add_garden_border": False,
    },
    "low": {
        "add_pavilion_eaves": True,
        "add_lanterns": False,
        "add_bridge_rails": False,
        "add_pond_edge": True,
        "add_path_posts": False,
        "add_garden_border": False,
    },
    "medium": {
        "add_pavilion_eaves": True,
        "add_lanterns": True,
        "add_bridge_rails": True,
        "add_pond_edge": True,
        "add_path_posts": False,
        "add_garden_border": False,
    },
    "high": {
        "add_pavilion_eaves": True,
        "add_lanterns": True,
        "add_bridge_rails": True,
        "add_pond_edge": True,
        "add_path_posts": True,
        "add_garden_border": True,
    },
}

DETAIL_ALIASES = {
    "ornamented": "medium",
}

CUBE_PATH = "/Engine/BasicShapes/Cube.Cube"
CYLINDER_PATH = "/Engine/BasicShapes/Cylinder.Cylinder"
SPHERE_PATH = "/Engine/BasicShapes/Sphere.Sphere"
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
cylinder_mesh = unreal.EditorAssetLibrary.load_asset(CYLINDER_PATH)
sphere_mesh = unreal.EditorAssetLibrary.load_asset(SPHERE_PATH)
actor_grouping_utils_class = getattr(unreal, "ActorGroupingUtils", None)
generated_actors = []

if not cube_mesh:
    raise RuntimeError("Could not load cube mesh: {0}".format(CUBE_PATH))


def get_config():
    config = dict(PRESETS[PRESET_NAME])
    for key in list(config.keys()):
        if key == "tree_count":
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


def spawn_mesh_actor(label, center, size_cm, mesh):
    if not mesh:
        return None
    actor = editor_actor_subsystem.spawn_actor_from_class(unreal.StaticMeshActor, center, unreal.Rotator(0.0, 0.0, 0.0))
    actor.set_actor_label(label)
    set_folder(actor)
    smc = actor.get_editor_property("static_mesh_component")
    smc.set_static_mesh(mesh)
    smc.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
    actor.set_actor_scale3d(vec(size_cm.x / 100.0, size_cm.y / 100.0, size_cm.z / 100.0))
    return register_actor(actor)


def spawn_box(label, center, size_cm):
    return spawn_mesh_actor(label, center, size_cm, cube_mesh)


def spawn_cylinder(label, center, size_cm):
    return spawn_mesh_actor(label, center, size_cm, cylinder_mesh or cube_mesh)


def spawn_sphere(label, center, size_cm):
    return spawn_mesh_actor(label, center, size_cm, sphere_mesh or cube_mesh)


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


def spawn_pavilion(label, origin, width, depth, height):
    plinth_height = 80.0 * GAMEPLAY_SCALE
    roof_height = 70.0 * GAMEPLAY_SCALE
    spawn_box(label + "_Plinth", add(origin, vec(0.0, 0.0, plinth_height * 0.5)), vec(width, depth, plinth_height))
    spawn_box(label + "_Core", add(origin, vec(0.0, 0.0, plinth_height + (height * 0.5))), vec(width * 0.62, depth * 0.62, height))
    spawn_box(label + "_Roof", add(origin, vec(0.0, 0.0, plinth_height + height + (roof_height * 0.5))), vec(width * 1.12, depth * 1.12, roof_height))

    if get_detail_profile()["add_pavilion_eaves"]:
        eave_z = plinth_height + height + (roof_height * 0.1)
        spawn_box(label + "_Eave_North", add(origin, vec(0.0, depth * 0.48, eave_z)), vec(width * 0.92, 18.0 * GAMEPLAY_SCALE, 24.0 * GAMEPLAY_SCALE))
        spawn_box(label + "_Eave_South", add(origin, vec(0.0, -depth * 0.48, eave_z)), vec(width * 0.92, 18.0 * GAMEPLAY_SCALE, 24.0 * GAMEPLAY_SCALE))
        spawn_box(label + "_Eave_West", add(origin, vec(-width * 0.48, 0.0, eave_z)), vec(18.0 * GAMEPLAY_SCALE, depth * 0.92, 24.0 * GAMEPLAY_SCALE))
        spawn_box(label + "_Eave_East", add(origin, vec(width * 0.48, 0.0, eave_z)), vec(18.0 * GAMEPLAY_SCALE, depth * 0.92, 24.0 * GAMEPLAY_SCALE))


def spawn_tree_marker(label, origin):
    trunk = vec(45.0 * GAMEPLAY_SCALE, 45.0 * GAMEPLAY_SCALE, 180.0 * GAMEPLAY_SCALE)
    crown = vec(160.0 * GAMEPLAY_SCALE, 160.0 * GAMEPLAY_SCALE, 160.0 * GAMEPLAY_SCALE)
    spawn_cylinder(label + "_Trunk", add(origin, vec(0.0, 0.0, trunk.z * 0.5)), trunk)
    spawn_sphere(label + "_Crown", add(origin, vec(0.0, 0.0, trunk.z + (crown.z * 0.5))), crown)


def spawn_lantern(label, origin):
    spawn_cylinder(label + "_Post", add(origin, vec(0.0, 0.0, 110.0 * GAMEPLAY_SCALE)), vec(16.0 * GAMEPLAY_SCALE, 16.0 * GAMEPLAY_SCALE, 220.0 * GAMEPLAY_SCALE))
    spawn_box(label + "_Frame", add(origin, vec(0.0, 0.0, 225.0 * GAMEPLAY_SCALE)), vec(42.0 * GAMEPLAY_SCALE, 42.0 * GAMEPLAY_SCALE, 64.0 * GAMEPLAY_SCALE))


def spawn_pond_edge(origin, pond_width, pond_depth):
    edge_thickness = 28.0 * GAMEPLAY_SCALE
    edge_height = 14.0 * GAMEPLAY_SCALE
    half_w = pond_width * 0.5
    half_d = pond_depth * 0.5
    for suffix, offset, size in (
        ("North", vec(0.0, half_d, edge_height * 0.5), vec(pond_width, edge_thickness, edge_height)),
        ("South", vec(0.0, -half_d, edge_height * 0.5), vec(pond_width, edge_thickness, edge_height)),
        ("West", vec(-half_w, 0.0, edge_height * 0.5), vec(edge_thickness, pond_depth, edge_height)),
        ("East", vec(half_w, 0.0, edge_height * 0.5), vec(edge_thickness, pond_depth, edge_height)),
    ):
        spawn_box("{0}_PondEdge_{1}".format(COMPOUND_NAME, suffix), add(origin, offset), size)


def spawn_bridge_rails(origin, bridge_depth):
    rail_height = 34.0 * GAMEPLAY_SCALE
    rail_offset_x = 120.0 * GAMEPLAY_SCALE
    for suffix, direction in (("L", -1.0), ("R", 1.0)):
        spawn_box(
            "{0}_BridgeRail_{1}".format(COMPOUND_NAME, suffix),
            add(origin, vec(rail_offset_x * direction, 0.0, 76.0 * GAMEPLAY_SCALE)),
            vec(18.0 * GAMEPLAY_SCALE, bridge_depth * 0.9, rail_height),
        )


def spawn_path_posts(origin, court_depth):
    post_height = 80.0 * GAMEPLAY_SCALE
    post_offset_x = 260.0 * GAMEPLAY_SCALE
    start_y = -(court_depth * 0.34)
    for index in range(4):
        y_pos = start_y + (index * 240.0 * GAMEPLAY_SCALE)
        for suffix, direction in (("L", -1.0), ("R", 1.0)):
            spawn_cylinder(
                "{0}_PathPost_{1}_{2}".format(COMPOUND_NAME, suffix, index + 1),
                add(origin, vec(post_offset_x * direction, y_pos, post_height * 0.5)),
                vec(14.0 * GAMEPLAY_SCALE, 14.0 * GAMEPLAY_SCALE, post_height),
            )


def spawn_garden_border(origin, court_width, court_depth):
    border_height = 26.0 * GAMEPLAY_SCALE
    border_thickness = 16.0 * GAMEPLAY_SCALE
    half_w = court_width * 0.36
    half_d = court_depth * 0.36
    for suffix, offset, size in (
        ("North", vec(0.0, half_d, border_height * 0.5), vec(court_width * 0.72, border_thickness, border_height)),
        ("South", vec(0.0, -half_d, border_height * 0.5), vec(court_width * 0.72, border_thickness, border_height)),
        ("West", vec(-half_w, 0.0, border_height * 0.5), vec(border_thickness, court_depth * 0.72, border_height)),
        ("East", vec(half_w, 0.0, border_height * 0.5), vec(border_thickness, court_depth * 0.72, border_height)),
    ):
        spawn_box("{0}_GardenBorder_{1}".format(COMPOUND_NAME, suffix), add(origin, offset), size)


def add_detail_pass(origin, config):
    detail_profile = get_detail_profile()
    if detail_profile["add_pond_edge"]:
        spawn_pond_edge(add(origin, vec(0.0, 120.0 * GAMEPLAY_SCALE, 44.0 * GAMEPLAY_SCALE)), config["pond_width"], config["pond_depth"])
    if detail_profile["add_bridge_rails"]:
        spawn_bridge_rails(add(origin, vec(0.0, 120.0 * GAMEPLAY_SCALE, 0.0)), config["pond_depth"])
    if detail_profile["add_lanterns"]:
        lantern_y = -(config["court_depth"] * 0.24)
        lantern_x = 220.0 * GAMEPLAY_SCALE
        spawn_lantern("{0}_Lantern_L".format(COMPOUND_NAME), add(origin, vec(-lantern_x, lantern_y, 0.0)))
        spawn_lantern("{0}_Lantern_R".format(COMPOUND_NAME), add(origin, vec(lantern_x, lantern_y, 0.0)))
    if detail_profile["add_path_posts"]:
        spawn_path_posts(origin, config["court_depth"])
    if detail_profile["add_garden_border"]:
        spawn_garden_border(add(origin, vec(0.0, 160.0 * GAMEPLAY_SCALE, 0.0)), config["court_width"], config["court_depth"])


def build_formal_garden(origin):
    config = get_config()
    generated_actors[:] = []
    destroy_previous(COMPOUND_NAME)

    spawn_wall_ring(origin, config["court_width"], config["court_depth"], config["wall_height"])
    spawn_box("{0}_MainPath".format(COMPOUND_NAME), add(origin, vec(0.0, 0.0, 10.0 * GAMEPLAY_SCALE)), vec(300.0 * GAMEPLAY_SCALE, config["court_depth"] * 0.88, 20.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_CrossPath".format(COMPOUND_NAME), add(origin, vec(0.0, 180.0 * GAMEPLAY_SCALE, 10.0 * GAMEPLAY_SCALE)), vec(config["court_width"] * 0.68, 260.0 * GAMEPLAY_SCALE, 20.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_Pond".format(COMPOUND_NAME), add(origin, vec(0.0, 120.0 * GAMEPLAY_SCALE, 25.0 * GAMEPLAY_SCALE)), vec(config["pond_width"], config["pond_depth"], 50.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_Bridge".format(COMPOUND_NAME), add(origin, vec(0.0, 120.0 * GAMEPLAY_SCALE, 55.0 * GAMEPLAY_SCALE)), vec(280.0 * GAMEPLAY_SCALE, config["pond_depth"] * 0.9, 30.0 * GAMEPLAY_SCALE))

    spawn_pavilion("{0}_NorthPavilion".format(COMPOUND_NAME), add(origin, vec(0.0, (config["court_depth"] * 0.5) - (700.0 * GAMEPLAY_SCALE), 0.0)), config["pavilion_width"], config["pavilion_depth"], config["pavilion_height"])
    spawn_pavilion("{0}_EastPavilion".format(COMPOUND_NAME), add(origin, vec((config["court_width"] * 0.5) - (700.0 * GAMEPLAY_SCALE), 0.0, 0.0)), config["pavilion_width"] * 0.88, config["pavilion_depth"] * 0.88, config["pavilion_height"] * 0.82)
    spawn_pavilion("{0}_WestPavilion".format(COMPOUND_NAME), add(origin, vec(-(config["court_width"] * 0.5) + (700.0 * GAMEPLAY_SCALE), 0.0, 0.0)), config["pavilion_width"] * 0.88, config["pavilion_depth"] * 0.88, config["pavilion_height"] * 0.82)

    tree_rows = max(2, int(config["tree_count"] / 2))
    spacing_x = (config["court_width"] * 0.5) - (520.0 * GAMEPLAY_SCALE)
    spacing_y = 760.0 * GAMEPLAY_SCALE
    for index in range(tree_rows):
        y_pos = -(spacing_y * 0.5) + (index * spacing_y)
        spawn_tree_marker("{0}_Tree_L_{1}".format(COMPOUND_NAME, index + 1), add(origin, vec(-spacing_x, y_pos, 0.0)))
        spawn_tree_marker("{0}_Tree_R_{1}".format(COMPOUND_NAME, index + 1), add(origin, vec(spacing_x, y_pos, 0.0)))

    add_detail_pass(origin, config)
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


spawn_origin = get_spawn_origin(3000.0)
build_formal_garden(spawn_origin)

print("{0} ({1}, {2}) generated at {3}".format(COMPOUND_NAME, PRESET_NAME, resolve_detail_mode(), spawn_origin))
