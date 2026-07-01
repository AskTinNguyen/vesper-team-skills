import unreal


COMPOUND_NAME = "AxialCompound"
PRESET_NAME = "prefecture_compound"
DETAIL_MODE = "blockout"
GAMEPLAY_SCALE = 3.0

PRESETS = {
    "prefecture_compound": {
        "compound_width": 4200.0,
        "compound_depth": 6200.0,
        "wall_height": 180.0,
        "court_depth": 1400.0,
        "hall_width": 1800.0,
        "hall_depth": 1100.0,
        "hall_height": 520.0,
        "side_hall_width": 720.0,
        "side_hall_depth": 880.0,
        "side_hall_height": 320.0,
        "watchtowers": False,
    },
    "warlord_manor": {
        "compound_width": 4800.0,
        "compound_depth": 7000.0,
        "wall_height": 220.0,
        "court_depth": 1600.0,
        "hall_width": 2200.0,
        "hall_depth": 1200.0,
        "hall_height": 620.0,
        "side_hall_width": 900.0,
        "side_hall_depth": 980.0,
        "side_hall_height": 380.0,
        "watchtowers": True,
    },
}

DETAIL_PROFILES = {
    "blockout": {
        "add_hall_eaves": False,
        "add_gate_frame": False,
        "add_screen_wall": False,
        "add_lantern_pairs": False,
        "add_tree_pairs": False,
        "add_link_walls": False,
        "add_frontispiece": False,
        "add_processional_path": False,
        "add_ceremonial_platform": False,
        "add_outer_markers": False,
    },
    "low": {
        "add_hall_eaves": True,
        "add_gate_frame": True,
        "add_screen_wall": True,
        "add_lantern_pairs": False,
        "add_tree_pairs": False,
        "add_link_walls": False,
        "add_frontispiece": False,
        "add_processional_path": False,
        "add_ceremonial_platform": False,
        "add_outer_markers": False,
    },
    "medium": {
        "add_hall_eaves": True,
        "add_gate_frame": True,
        "add_screen_wall": True,
        "add_lantern_pairs": True,
        "add_tree_pairs": True,
        "add_link_walls": True,
        "add_frontispiece": False,
        "add_processional_path": False,
        "add_ceremonial_platform": False,
        "add_outer_markers": False,
    },
    "high": {
        "add_hall_eaves": True,
        "add_gate_frame": True,
        "add_screen_wall": True,
        "add_lantern_pairs": True,
        "add_tree_pairs": True,
        "add_link_walls": True,
        "add_frontispiece": True,
        "add_processional_path": True,
        "add_ceremonial_platform": True,
        "add_outer_markers": True,
    },
}

DETAIL_ALIASES = {
    "ornamented": "medium",
}

OUTPUT_FOLDER = "Generated/{0}".format(COMPOUND_NAME)
CUBE_PATH = "/Engine/BasicShapes/Cube.Cube"


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
        if isinstance(config[key], bool):
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
    actor = editor_actor_subsystem.spawn_actor_from_class(
        unreal.StaticMeshActor,
        center,
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    actor.set_actor_label(label)
    set_folder(actor)
    smc = actor.get_editor_property("static_mesh_component")
    smc.set_static_mesh(cube_mesh)
    smc.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
    actor.set_actor_scale3d(vec(size_cm.x / 100.0, size_cm.y / 100.0, size_cm.z / 100.0))
    return register_actor(actor)


def finalize_generated_layout():
    if not generated_actors:
        return None

    if actor_grouping_utils_class:
        try:
            if not actor_grouping_utils_class.is_grouping_active():
                actor_grouping_utils_class.set_grouping_active(True)
            grouping_utils = actor_grouping_utils_class.get()
            if grouping_utils and grouping_utils.can_group_actors(generated_actors):
                group_actor = grouping_utils.group_actors(generated_actors)
                group_actor.set_actor_label("{0}_Group".format(COMPOUND_NAME))
                set_folder(group_actor)
                return group_actor
        except Exception as exc:
            unreal.log_warning("{0}: failed to group generated actors ({1})".format(COMPOUND_NAME, exc))

    return None


def spawn_roof_eaves(label, origin, width, depth, roof_z):
    band_height = 22.0 * GAMEPLAY_SCALE
    overhang = 80.0 * GAMEPLAY_SCALE
    thickness = 40.0 * GAMEPLAY_SCALE
    span_x = width + (overhang * 2.0)
    span_y = depth + (overhang * 2.0)
    pieces = (
        ("North", vec(0.0, (span_y - thickness) * 0.5, roof_z), vec(span_x, thickness, band_height)),
        ("South", vec(0.0, -(span_y - thickness) * 0.5, roof_z), vec(span_x, thickness, band_height)),
        ("West", vec(-(span_x - thickness) * 0.5, 0.0, roof_z), vec(thickness, span_y, band_height)),
        ("East", vec((span_x - thickness) * 0.5, 0.0, roof_z), vec(thickness, span_y, band_height)),
    )
    for suffix, offset, size in pieces:
        spawn_box("{0}_{1}".format(label, suffix), add(origin, offset), size)


def spawn_pair(prefix, origin, y_pos, x_offset, size_cm, z_offset):
    for suffix, direction in (("L", -1.0), ("R", 1.0)):
        spawn_box(
            "{0}_{1}".format(prefix, suffix),
            add(origin, vec(x_offset * direction, y_pos, z_offset)),
            size_cm,
        )


def spawn_wall_ring(origin, width, depth, wall_height):
    thickness = 80.0 * GAMEPLAY_SCALE
    half_w = width * 0.5
    half_d = depth * 0.5
    walls = (
        ("North", vec(0.0, half_d, wall_height * 0.5), vec(width, thickness, wall_height)),
        ("South", vec(0.0, -half_d, wall_height * 0.5), vec(width, thickness, wall_height)),
        ("West", vec(-half_w, 0.0, wall_height * 0.5), vec(thickness, depth, wall_height)),
        ("East", vec(half_w, 0.0, wall_height * 0.5), vec(thickness, depth, wall_height)),
    )
    for suffix, offset, size in walls:
        spawn_box("{0}_Wall_{1}".format(COMPOUND_NAME, suffix), add(origin, offset), size)


def spawn_hall(label, origin, width, depth, height, detail_profile):
    plinth_height = 120.0 * GAMEPLAY_SCALE
    roof_height = 80.0 * GAMEPLAY_SCALE
    roof_lower_z = plinth_height + height + (roof_height * 0.5)
    spawn_box(label + "_Plinth", add(origin, vec(0.0, 0.0, plinth_height * 0.5)), vec(width, depth, plinth_height))
    spawn_box(label + "_Core", add(origin, vec(0.0, 0.0, plinth_height + (height * 0.5))), vec(width * 0.7, depth * 0.72, height))
    spawn_box(label + "_Roof", add(origin, vec(0.0, 0.0, roof_lower_z)), vec(width * 1.12, depth * 1.1, roof_height))
    if detail_profile["add_hall_eaves"]:
        spawn_roof_eaves(label + "_EaveBand", origin, width * 1.12, depth * 1.1, roof_lower_z)


def spawn_gatehouse(origin, width, detail_profile):
    gate_width = width * 0.38
    gate_depth = 720.0 * GAMEPLAY_SCALE
    gate_height = 560.0 * GAMEPLAY_SCALE
    gate_label = "{0}_Gatehouse".format(COMPOUND_NAME)
    spawn_hall(gate_label, origin, gate_width, gate_depth, gate_height, detail_profile)
    if detail_profile["add_gate_frame"]:
        frame_size = vec(gate_width * 1.1, 70.0 * GAMEPLAY_SCALE, gate_height * 0.72)
        spawn_box(gate_label + "_FrameTop", add(origin, vec(0.0, -(gate_depth * 0.52), frame_size.z + (60.0 * GAMEPLAY_SCALE))), frame_size)
        spawn_pair(gate_label + "_FramePier", origin, -(gate_depth * 0.52), gate_width * 0.42, vec(90.0 * GAMEPLAY_SCALE, 80.0 * GAMEPLAY_SCALE, gate_height * 1.05), gate_height * 0.52)


def spawn_side_halls(origin, court_center_y, config, detail_profile):
    side_offset_x = (config["compound_width"] * 0.5) - (config["side_hall_width"] * 0.8)
    halls = []
    for suffix, direction in (("L", -1.0), ("R", 1.0)):
        hall_origin = add(origin, vec(side_offset_x * direction, court_center_y, 0.0))
        halls.append(hall_origin)
        spawn_hall(
            "{0}_SideHall_{1}".format(COMPOUND_NAME, suffix),
            hall_origin,
            config["side_hall_width"],
            config["side_hall_depth"],
            config["side_hall_height"],
            detail_profile,
        )
    if detail_profile["add_link_walls"]:
        link_size = vec(config["compound_width"] * 0.18, 80.0 * GAMEPLAY_SCALE, config["wall_height"] * 0.72)
        spawn_box("{0}_LinkWall_{1}".format(COMPOUND_NAME, int(court_center_y)), add(origin, vec(0.0, court_center_y + (config["side_hall_depth"] * 0.56), link_size.z * 0.5)), link_size)


def spawn_watchtowers(origin, width, depth, wall_height):
    tower_size = vec(220.0 * GAMEPLAY_SCALE, 220.0 * GAMEPLAY_SCALE, wall_height * 2.2)
    offset_x = (width * 0.5) - tower_size.x * 0.7
    offset_y = (depth * 0.5) - tower_size.y * 0.7
    for index, (x_pos, y_pos) in enumerate((
        (-offset_x, -offset_y),
        (-offset_x, offset_y),
        (offset_x, -offset_y),
        (offset_x, offset_y),
    )):
        spawn_box("{0}_Tower_{1}".format(COMPOUND_NAME, index + 1), add(origin, vec(x_pos, y_pos, tower_size.z * 0.5)), tower_size)


def build_axial_compound(origin):
    config = get_config()
    detail_profile = get_detail_profile()
    generated_actors[:] = []
    destroy_previous(COMPOUND_NAME)

    spawn_wall_ring(origin, config["compound_width"], config["compound_depth"], config["wall_height"])
    if config["watchtowers"]:
        spawn_watchtowers(origin, config["compound_width"], config["compound_depth"], config["wall_height"])

    south_court_y = -(config["compound_depth"] * 0.5) + config["court_depth"] * 0.55
    center_court_y = 0.0
    rear_court_y = (config["compound_depth"] * 0.5) - config["court_depth"] * 0.75
    gate_y = south_court_y - (config["court_depth"] * 0.55)

    spawn_gatehouse(add(origin, vec(0.0, gate_y, 0.0)), config["compound_width"], detail_profile)
    spawn_hall("{0}_MainHall".format(COMPOUND_NAME), add(origin, vec(0.0, center_court_y, 0.0)), config["hall_width"], config["hall_depth"], config["hall_height"], detail_profile)
    spawn_hall("{0}_RearHall".format(COMPOUND_NAME), add(origin, vec(0.0, rear_court_y, 0.0)), config["hall_width"] * 0.88, config["hall_depth"] * 0.86, config["hall_height"] * 0.82, detail_profile)

    spawn_side_halls(origin, south_court_y, config, detail_profile)
    spawn_side_halls(origin, center_court_y, config, detail_profile)

    court_marker_height = 20.0 * GAMEPLAY_SCALE
    for suffix, court_y in (("Forecourt", south_court_y), ("MainCourt", center_court_y), ("RearCourt", rear_court_y)):
        spawn_box(
            "{0}_{1}".format(COMPOUND_NAME, suffix),
            add(origin, vec(0.0, court_y, court_marker_height * 0.5)),
            vec(config["compound_width"] * 0.42, config["court_depth"] * 0.85, court_marker_height),
        )

    if detail_profile["add_screen_wall"]:
        spawn_box(
            "{0}_ScreenWall".format(COMPOUND_NAME),
            add(origin, vec(0.0, gate_y + (config["court_depth"] * 0.34), config["wall_height"] * 0.42)),
            vec(config["compound_width"] * 0.18, 90.0 * GAMEPLAY_SCALE, config["wall_height"] * 0.84),
        )

    if detail_profile["add_lantern_pairs"]:
        lantern_size = vec(80.0 * GAMEPLAY_SCALE, 80.0 * GAMEPLAY_SCALE, 220.0 * GAMEPLAY_SCALE)
        spawn_pair("{0}_GateLantern".format(COMPOUND_NAME), origin, south_court_y - (config["court_depth"] * 0.18), config["compound_width"] * 0.16, lantern_size, lantern_size.z * 0.5)
        spawn_pair("{0}_MainLantern".format(COMPOUND_NAME), origin, center_court_y - (config["hall_depth"] * 0.7), config["hall_width"] * 0.36, lantern_size, lantern_size.z * 0.5)

    if detail_profile["add_tree_pairs"]:
        tree_size = vec(160.0 * GAMEPLAY_SCALE, 160.0 * GAMEPLAY_SCALE, 280.0 * GAMEPLAY_SCALE)
        spawn_pair("{0}_CourtTree_Fore".format(COMPOUND_NAME), origin, south_court_y + (config["court_depth"] * 0.14), config["compound_width"] * 0.24, tree_size, tree_size.z * 0.5)
        spawn_pair("{0}_CourtTree_Main".format(COMPOUND_NAME), origin, center_court_y + (config["court_depth"] * 0.18), config["compound_width"] * 0.24, tree_size, tree_size.z * 0.5)

    if detail_profile["add_processional_path"]:
        spawn_box(
            "{0}_ProcessionalPath".format(COMPOUND_NAME),
            add(origin, vec(0.0, (gate_y + center_court_y) * 0.5, 15.0 * GAMEPLAY_SCALE)),
            vec(config["hall_width"] * 0.38, (center_court_y - gate_y) + (config["hall_depth"] * 0.32), 30.0 * GAMEPLAY_SCALE),
        )

    if detail_profile["add_ceremonial_platform"]:
        spawn_box(
            "{0}_MainHallPlatform".format(COMPOUND_NAME),
            add(origin, vec(0.0, center_court_y - (config["hall_depth"] * 0.66), 55.0 * GAMEPLAY_SCALE)),
            vec(config["hall_width"] * 0.54, config["hall_depth"] * 0.22, 110.0 * GAMEPLAY_SCALE),
        )

    if detail_profile["add_frontispiece"]:
        frontispiece_y = -(config["compound_depth"] * 0.5) + (170.0 * GAMEPLAY_SCALE)
        spawn_box(
            "{0}_FrontispieceBeam".format(COMPOUND_NAME),
            add(origin, vec(0.0, frontispiece_y, config["wall_height"] + (100.0 * GAMEPLAY_SCALE))),
            vec(config["compound_width"] * 0.26, 90.0 * GAMEPLAY_SCALE, 80.0 * GAMEPLAY_SCALE),
        )
        spawn_pair("{0}_FrontispiecePier".format(COMPOUND_NAME), origin, frontispiece_y, config["compound_width"] * 0.13, vec(100.0 * GAMEPLAY_SCALE, 90.0 * GAMEPLAY_SCALE, config["wall_height"] * 1.2), config["wall_height"] * 0.6)

    if detail_profile["add_outer_markers"]:
        marker_size = vec(120.0 * GAMEPLAY_SCALE, 120.0 * GAMEPLAY_SCALE, 300.0 * GAMEPLAY_SCALE)
        spawn_pair("{0}_EntryMarker".format(COMPOUND_NAME), origin, -(config["compound_depth"] * 0.5) + (420.0 * GAMEPLAY_SCALE), config["compound_width"] * 0.22, marker_size, marker_size.z * 0.5)

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
build_axial_compound(spawn_origin)

print("{0} ({1}, {2}) generated at {3}".format(COMPOUND_NAME, PRESET_NAME, resolve_detail_mode(), spawn_origin))
