import unreal


COMPOUND_NAME = "RitualBurialPrecinct"
PRESET_NAME = "noble_tomb_precinct"
DETAIL_MODE = "blockout"
GAMEPLAY_SCALE = 3.0

PRESETS = {
    "noble_tomb_precinct": {
        "precinct_width": 4800.0,
        "precinct_depth": 7600.0,
        "wall_height": 180.0,
        "spirit_path_width": 620.0,
        "marker_width": 260.0,
        "marker_depth": 260.0,
        "marker_height": 420.0,
        "offering_hall_width": 1600.0,
        "offering_hall_depth": 1100.0,
        "offering_hall_height": 420.0,
        "tomb_mound_width": 2200.0,
        "tomb_mound_depth": 1800.0,
        "tomb_mound_height": 900.0,
    },
    "mausoleum_axis": {
        "precinct_width": 5600.0,
        "precinct_depth": 8800.0,
        "wall_height": 220.0,
        "spirit_path_width": 720.0,
        "marker_width": 300.0,
        "marker_depth": 300.0,
        "marker_height": 500.0,
        "offering_hall_width": 1850.0,
        "offering_hall_depth": 1200.0,
        "offering_hall_height": 480.0,
        "tomb_mound_width": 2600.0,
        "tomb_mound_depth": 2100.0,
        "tomb_mound_height": 1100.0,
    },
}

DETAIL_PROFILES = {
    "blockout": {
        "add_hall_eaves": False,
        "add_spirit_path_edges": False,
        "add_marker_caps": False,
        "add_tree_pairs": False,
        "add_offering_tables": False,
        "add_gate_screen": False,
        "add_processional_platform": False,
        "add_memorial_arch": False,
        "add_outer_stelae": False,
        "add_mound_forecourt": False,
    },
    "low": {
        "add_hall_eaves": True,
        "add_spirit_path_edges": True,
        "add_marker_caps": True,
        "add_tree_pairs": False,
        "add_offering_tables": False,
        "add_gate_screen": False,
        "add_processional_platform": False,
        "add_memorial_arch": False,
        "add_outer_stelae": False,
        "add_mound_forecourt": False,
    },
    "medium": {
        "add_hall_eaves": True,
        "add_spirit_path_edges": True,
        "add_marker_caps": True,
        "add_tree_pairs": True,
        "add_offering_tables": True,
        "add_gate_screen": True,
        "add_processional_platform": False,
        "add_memorial_arch": False,
        "add_outer_stelae": False,
        "add_mound_forecourt": False,
    },
    "high": {
        "add_hall_eaves": True,
        "add_spirit_path_edges": True,
        "add_marker_caps": True,
        "add_tree_pairs": True,
        "add_offering_tables": True,
        "add_gate_screen": True,
        "add_processional_platform": True,
        "add_memorial_arch": True,
        "add_outer_stelae": True,
        "add_mound_forecourt": True,
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


def spawn_roof_eaves(label, origin, width, depth, roof_z):
    band_height = 22.0 * GAMEPLAY_SCALE
    overhang = 84.0 * GAMEPLAY_SCALE
    thickness = 42.0 * GAMEPLAY_SCALE
    span_x = width + (overhang * 2.0)
    span_y = depth + (overhang * 2.0)
    for suffix, offset, size in (
        ("North", vec(0.0, (span_y - thickness) * 0.5, roof_z), vec(span_x, thickness, band_height)),
        ("South", vec(0.0, -(span_y - thickness) * 0.5, roof_z), vec(span_x, thickness, band_height)),
        ("West", vec(-(span_x - thickness) * 0.5, 0.0, roof_z), vec(thickness, span_y, band_height)),
        ("East", vec((span_x - thickness) * 0.5, 0.0, roof_z), vec(thickness, span_y, band_height)),
    ):
        spawn_box("{0}_{1}".format(label, suffix), add(origin, offset), size)


def spawn_wall_ring(origin, width, depth, wall_height):
    thickness = 70.0 * GAMEPLAY_SCALE
    half_w = width * 0.5
    half_d = depth * 0.5
    for suffix, offset, size in (
        ("North", vec(0.0, half_d, wall_height * 0.5), vec(width, thickness, wall_height)),
        ("South", vec(0.0, -half_d, wall_height * 0.5), vec(width, thickness, wall_height)),
        ("West", vec(-half_w, 0.0, wall_height * 0.5), vec(thickness, depth, wall_height)),
        ("East", vec(half_w, 0.0, wall_height * 0.5), vec(thickness, depth, wall_height)),
    ):
        spawn_box("{0}_Wall_{1}".format(COMPOUND_NAME, suffix), add(origin, offset), size)


def spawn_offering_hall(label, origin, width, depth, height, detail_profile):
    roof_height = 70.0 * GAMEPLAY_SCALE
    roof_z = 160.0 * GAMEPLAY_SCALE + height + (roof_height * 0.5)
    spawn_box(label + "_Plinth", add(origin, vec(0.0, 0.0, 80.0 * GAMEPLAY_SCALE)), vec(width, depth, 160.0 * GAMEPLAY_SCALE))
    spawn_box(label + "_Core", add(origin, vec(0.0, 0.0, 160.0 * GAMEPLAY_SCALE + (height * 0.5))), vec(width * 0.68, depth * 0.72, height))
    spawn_box(label + "_Roof", add(origin, vec(0.0, 0.0, roof_z)), vec(width * 1.08, depth * 1.08, roof_height))
    if detail_profile["add_hall_eaves"]:
        spawn_roof_eaves(label + "_Eaves", origin, width * 1.08, depth * 1.08, roof_z)


def build_burial_precinct(origin):
    config = get_config()
    detail_profile = get_detail_profile()
    generated_actors[:] = []
    destroy_previous(COMPOUND_NAME)

    spawn_wall_ring(origin, config["precinct_width"], config["precinct_depth"], config["wall_height"])
    spirit_path_center = add(origin, vec(0.0, -(config["precinct_depth"] * 0.08), 15.0 * GAMEPLAY_SCALE))
    spirit_path_size = vec(config["spirit_path_width"], config["precinct_depth"] * 0.72, 30.0 * GAMEPLAY_SCALE)
    spawn_box("{0}_SpiritPath".format(COMPOUND_NAME), spirit_path_center, spirit_path_size)

    if detail_profile["add_spirit_path_edges"]:
        edge_size = vec(40.0 * GAMEPLAY_SCALE, spirit_path_size.y, config["wall_height"] * 0.52)
        for suffix, direction in (("L", -1.0), ("R", 1.0)):
            spawn_box("{0}_SpiritEdge_{1}".format(COMPOUND_NAME, suffix), add(spirit_path_center, vec((config["spirit_path_width"] * 0.52) * direction, 0.0, edge_size.z * 0.5)), edge_size)

    marker_offset_x = config["spirit_path_width"] * 0.95
    marker_positions = (
        -(config["precinct_depth"] * 0.18),
        config["precinct_depth"] * 0.02,
        config["precinct_depth"] * 0.22,
    )
    for index, y_pos in enumerate(marker_positions):
        for suffix, direction in (("L", -1.0), ("R", 1.0)):
            marker_label = "{0}_Marker_{1}_{2}".format(COMPOUND_NAME, suffix, index + 1)
            marker_origin = add(origin, vec(marker_offset_x * direction, y_pos, 0.0))
            spawn_box(marker_label, add(marker_origin, vec(0.0, 0.0, config["marker_height"] * 0.5)), vec(config["marker_width"], config["marker_depth"], config["marker_height"]))
            if detail_profile["add_marker_caps"]:
                spawn_box(marker_label + "_Cap", add(marker_origin, vec(0.0, 0.0, config["marker_height"] + (28.0 * GAMEPLAY_SCALE))), vec(config["marker_width"] * 1.08, config["marker_depth"] * 1.08, 40.0 * GAMEPLAY_SCALE))

    hall_y = config["precinct_depth"] * 0.12
    spawn_offering_hall("{0}_OfferingHall".format(COMPOUND_NAME), add(origin, vec(0.0, hall_y, 0.0)), config["offering_hall_width"], config["offering_hall_depth"], config["offering_hall_height"], detail_profile)

    if detail_profile["add_offering_tables"]:
        table_size = vec(config["offering_hall_width"] * 0.24, config["offering_hall_depth"] * 0.12, 70.0 * GAMEPLAY_SCALE)
        spawn_box("{0}_OfferingTable".format(COMPOUND_NAME), add(origin, vec(0.0, hall_y - (config["offering_hall_depth"] * 0.54), table_size.z * 0.5)), table_size)

    mound_y = (config["precinct_depth"] * 0.5) - (config["tomb_mound_depth"] * 0.75)
    spawn_box("{0}_TombMound_Base".format(COMPOUND_NAME), add(origin, vec(0.0, mound_y, config["tomb_mound_height"] * 0.3)), vec(config["tomb_mound_width"], config["tomb_mound_depth"], config["tomb_mound_height"] * 0.6))
    spawn_box("{0}_TombMound_Upper".format(COMPOUND_NAME), add(origin, vec(0.0, mound_y, config["tomb_mound_height"] * 0.72)), vec(config["tomb_mound_width"] * 0.72, config["tomb_mound_depth"] * 0.72, config["tomb_mound_height"] * 0.44))

    pylon_offset_x = config["tomb_mound_width"] * 0.34
    for suffix, direction in (("L", -1.0), ("R", 1.0)):
        spawn_box("{0}_MoundPylon_{1}".format(COMPOUND_NAME, suffix), add(origin, vec(pylon_offset_x * direction, mound_y - (config["tomb_mound_depth"] * 0.28), config["marker_height"] * 0.72)), vec(config["marker_width"] * 1.1, config["marker_depth"] * 1.1, config["marker_height"] * 1.44))

    if detail_profile["add_gate_screen"]:
        spawn_box("{0}_GateScreen".format(COMPOUND_NAME), add(origin, vec(0.0, -(config["precinct_depth"] * 0.28), config["wall_height"] * 0.42)), vec(config["precinct_width"] * 0.18, 90.0 * GAMEPLAY_SCALE, config["wall_height"] * 0.84))

    if detail_profile["add_tree_pairs"]:
        tree_size = vec(160.0 * GAMEPLAY_SCALE, 160.0 * GAMEPLAY_SCALE, 300.0 * GAMEPLAY_SCALE)
        for row_name, y_pos in (("Fore", -(config["precinct_depth"] * 0.14)), ("Rear", hall_y + (config["offering_hall_depth"] * 0.6))):
            for suffix, direction in (("L", -1.0), ("R", 1.0)):
                spawn_box("{0}_Tree_{1}_{2}".format(COMPOUND_NAME, row_name, suffix), add(origin, vec((config["precinct_width"] * 0.22) * direction, y_pos, tree_size.z * 0.5)), tree_size)

    if detail_profile["add_processional_platform"]:
        spawn_box("{0}_ProcessionalPlatform".format(COMPOUND_NAME), add(origin, vec(0.0, hall_y - (config["offering_hall_depth"] * 0.9), 45.0 * GAMEPLAY_SCALE)), vec(config["offering_hall_width"] * 0.52, config["offering_hall_depth"] * 0.18, 90.0 * GAMEPLAY_SCALE))

    if detail_profile["add_memorial_arch"]:
        arch_y = -(config["precinct_depth"] * 0.5) + (220.0 * GAMEPLAY_SCALE)
        spawn_box("{0}_MemorialArchBeam".format(COMPOUND_NAME), add(origin, vec(0.0, arch_y, config["wall_height"] + (110.0 * GAMEPLAY_SCALE))), vec(config["precinct_width"] * 0.24, 100.0 * GAMEPLAY_SCALE, 90.0 * GAMEPLAY_SCALE))
        for suffix, direction in (("L", -1.0), ("R", 1.0)):
            spawn_box("{0}_MemorialArchPier_{1}".format(COMPOUND_NAME, suffix), add(origin, vec((config["precinct_width"] * 0.12) * direction, arch_y, config["wall_height"] * 0.62)), vec(120.0 * GAMEPLAY_SCALE, 100.0 * GAMEPLAY_SCALE, config["wall_height"] * 1.24))

    if detail_profile["add_outer_stelae"]:
        stele_size = vec(130.0 * GAMEPLAY_SCALE, 120.0 * GAMEPLAY_SCALE, 320.0 * GAMEPLAY_SCALE)
        for suffix, direction in (("L", -1.0), ("R", 1.0)):
            spawn_box("{0}_OuterStele_{1}".format(COMPOUND_NAME, suffix), add(origin, vec((config["precinct_width"] * 0.24) * direction, -(config["precinct_depth"] * 0.22), stele_size.z * 0.5)), stele_size)

    if detail_profile["add_mound_forecourt"]:
        spawn_box("{0}_MoundForecourt".format(COMPOUND_NAME), add(origin, vec(0.0, mound_y - (config["tomb_mound_depth"] * 0.62), 18.0 * GAMEPLAY_SCALE)), vec(config["tomb_mound_width"] * 0.58, config["tomb_mound_depth"] * 0.22, 36.0 * GAMEPLAY_SCALE))

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


spawn_origin = get_spawn_origin(3600.0)
build_burial_precinct(spawn_origin)

print("{0} ({1}, {2}) generated at {3}".format(COMPOUND_NAME, PRESET_NAME, resolve_detail_mode(), spawn_origin))
