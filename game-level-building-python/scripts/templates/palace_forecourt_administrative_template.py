import unreal


COMPOUND_NAME = "PalaceForecourtAdministrative"
PRESET_NAME = "royal_audience_axis"
DETAIL_MODE = "blockout"
GAMEPLAY_SCALE = 3.0

PRESETS = {
    "royal_audience_axis": {
        "forecourt_width": 5200.0,
        "forecourt_depth": 7600.0,
        "court_depth": 1700.0,
        "hall_width": 2400.0,
        "hall_depth": 1300.0,
        "hall_height": 700.0,
        "admin_width": 1000.0,
        "admin_depth": 920.0,
        "admin_height": 360.0,
        "wall_height": 220.0,
    },
    "governor_yamen": {
        "forecourt_width": 4600.0,
        "forecourt_depth": 6800.0,
        "court_depth": 1500.0,
        "hall_width": 2100.0,
        "hall_depth": 1180.0,
        "hall_height": 620.0,
        "admin_width": 920.0,
        "admin_depth": 840.0,
        "admin_height": 320.0,
        "wall_height": 180.0,
    },
}

DETAIL_PROFILES = {
    "blockout": {
        "add_roof_eaves": False,
        "add_gate_frame": False,
        "add_side_screens": False,
        "add_lantern_pairs": False,
        "add_tree_rows": False,
        "add_court_steles": False,
        "add_forecourt_path": False,
        "add_ceremonial_platform": False,
        "add_entry_arch": False,
        "add_outer_markers": False,
    },
    "low": {
        "add_roof_eaves": True,
        "add_gate_frame": True,
        "add_side_screens": True,
        "add_lantern_pairs": False,
        "add_tree_rows": False,
        "add_court_steles": False,
        "add_forecourt_path": False,
        "add_ceremonial_platform": False,
        "add_entry_arch": False,
        "add_outer_markers": False,
    },
    "medium": {
        "add_roof_eaves": True,
        "add_gate_frame": True,
        "add_side_screens": True,
        "add_lantern_pairs": True,
        "add_tree_rows": True,
        "add_court_steles": True,
        "add_forecourt_path": False,
        "add_ceremonial_platform": False,
        "add_entry_arch": False,
        "add_outer_markers": False,
    },
    "high": {
        "add_roof_eaves": True,
        "add_gate_frame": True,
        "add_side_screens": True,
        "add_lantern_pairs": True,
        "add_tree_rows": True,
        "add_court_steles": True,
        "add_forecourt_path": True,
        "add_ceremonial_platform": True,
        "add_entry_arch": True,
        "add_outer_markers": True,
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
    band_height = 24.0 * GAMEPLAY_SCALE
    overhang = 90.0 * GAMEPLAY_SCALE
    thickness = 44.0 * GAMEPLAY_SCALE
    span_x = width + (overhang * 2.0)
    span_y = depth + (overhang * 2.0)
    for suffix, offset, size in (
        ("North", vec(0.0, (span_y - thickness) * 0.5, roof_z), vec(span_x, thickness, band_height)),
        ("South", vec(0.0, -(span_y - thickness) * 0.5, roof_z), vec(span_x, thickness, band_height)),
        ("West", vec(-(span_x - thickness) * 0.5, 0.0, roof_z), vec(thickness, span_y, band_height)),
        ("East", vec((span_x - thickness) * 0.5, 0.0, roof_z), vec(thickness, span_y, band_height)),
    ):
        spawn_box("{0}_{1}".format(label, suffix), add(origin, offset), size)


def spawn_pair(prefix, origin, y_pos, x_offset, size_cm, z_offset):
    for suffix, direction in (("L", -1.0), ("R", 1.0)):
        spawn_box("{0}_{1}".format(prefix, suffix), add(origin, vec(x_offset * direction, y_pos, z_offset)), size_cm)


def spawn_wall_ring(origin, width, depth, wall_height):
    thickness = 80.0 * GAMEPLAY_SCALE
    half_w = width * 0.5
    half_d = depth * 0.5
    for suffix, offset, size in (
        ("North", vec(0.0, half_d, wall_height * 0.5), vec(width, thickness, wall_height)),
        ("South", vec(0.0, -half_d, wall_height * 0.5), vec(width, thickness, wall_height)),
        ("West", vec(-half_w, 0.0, wall_height * 0.5), vec(thickness, depth, wall_height)),
        ("East", vec(half_w, 0.0, wall_height * 0.5), vec(thickness, depth, wall_height)),
    ):
        spawn_box("{0}_Wall_{1}".format(COMPOUND_NAME, suffix), add(origin, offset), size)


def spawn_hall(label, origin, width, depth, height, detail_profile):
    plinth_height = 120.0 * GAMEPLAY_SCALE
    roof_height = 90.0 * GAMEPLAY_SCALE
    lower_roof_z = plinth_height + height + (roof_height * 0.5)
    spawn_box(label + "_Plinth", add(origin, vec(0.0, 0.0, plinth_height * 0.5)), vec(width, depth, plinth_height))
    spawn_box(label + "_Core", add(origin, vec(0.0, 0.0, plinth_height + (height * 0.5))), vec(width * 0.68, depth * 0.72, height))
    spawn_box(label + "_RoofLower", add(origin, vec(0.0, 0.0, lower_roof_z)), vec(width * 1.08, depth * 1.08, roof_height))
    spawn_box(label + "_RoofUpper", add(origin, vec(0.0, 0.0, plinth_height + height + (roof_height * 1.15))), vec(width * 0.8, depth * 0.8, roof_height * 0.72))
    if detail_profile["add_roof_eaves"]:
        spawn_roof_eaves(label + "_Eaves", origin, width * 1.08, depth * 1.08, lower_roof_z)


def build_palace_forecourt(origin):
    config = get_config()
    detail_profile = get_detail_profile()
    generated_actors[:] = []
    destroy_previous(COMPOUND_NAME)

    spawn_wall_ring(origin, config["forecourt_width"], config["forecourt_depth"], config["wall_height"])

    south_y = -(config["forecourt_depth"] * 0.5) + (config["court_depth"] * 0.6)
    center_y = 0.0
    north_y = (config["forecourt_depth"] * 0.5) - (config["court_depth"] * 0.72)
    gate_y = south_y - (config["court_depth"] * 0.7)

    spawn_hall("{0}_GateHall".format(COMPOUND_NAME), add(origin, vec(0.0, gate_y, 0.0)), config["hall_width"] * 0.7, config["hall_depth"] * 0.78, config["hall_height"] * 0.72, detail_profile)
    spawn_hall("{0}_AudienceHall".format(COMPOUND_NAME), add(origin, vec(0.0, center_y, 0.0)), config["hall_width"], config["hall_depth"], config["hall_height"], detail_profile)
    spawn_hall("{0}_RearCouncilHall".format(COMPOUND_NAME), add(origin, vec(0.0, north_y, 0.0)), config["hall_width"] * 0.82, config["hall_depth"] * 0.82, config["hall_height"] * 0.84, detail_profile)

    admin_offset_x = (config["forecourt_width"] * 0.5) - (config["admin_width"] * 0.95)
    for row_name, row_y in (("Fore", south_y), ("Main", center_y), ("Rear", north_y)):
        for suffix, direction in (("L", -1.0), ("R", 1.0)):
            spawn_hall(
                "{0}_{1}Admin_{2}".format(COMPOUND_NAME, row_name, suffix),
                add(origin, vec(admin_offset_x * direction, row_y, 0.0)),
                config["admin_width"],
                config["admin_depth"],
                config["admin_height"],
                detail_profile,
            )

    for suffix, row_y in (("Forecourt", south_y), ("MainCourt", center_y), ("RearCourt", north_y)):
        spawn_box(
            "{0}_{1}".format(COMPOUND_NAME, suffix),
            add(origin, vec(0.0, row_y, 18.0 * GAMEPLAY_SCALE)),
            vec(config["forecourt_width"] * 0.48, config["court_depth"] * 0.86, 36.0 * GAMEPLAY_SCALE),
        )

    if detail_profile["add_gate_frame"]:
        spawn_box("{0}_GateBeam".format(COMPOUND_NAME), add(origin, vec(0.0, gate_y - (config["hall_depth"] * 0.42), config["hall_height"] * 0.88)), vec(config["hall_width"] * 0.54, 90.0 * GAMEPLAY_SCALE, 80.0 * GAMEPLAY_SCALE))
        spawn_pair("{0}_GatePier".format(COMPOUND_NAME), origin, gate_y - (config["hall_depth"] * 0.42), config["hall_width"] * 0.26, vec(120.0 * GAMEPLAY_SCALE, 90.0 * GAMEPLAY_SCALE, config["hall_height"] * 1.02), config["hall_height"] * 0.51)

    if detail_profile["add_side_screens"]:
        screen_size = vec(config["forecourt_width"] * 0.14, 90.0 * GAMEPLAY_SCALE, config["wall_height"] * 0.8)
        spawn_pair("{0}_SideScreen_Fore".format(COMPOUND_NAME), origin, south_y + (config["court_depth"] * 0.2), config["forecourt_width"] * 0.18, screen_size, screen_size.z * 0.5)
        spawn_pair("{0}_SideScreen_Main".format(COMPOUND_NAME), origin, center_y + (config["court_depth"] * 0.2), config["forecourt_width"] * 0.18, screen_size, screen_size.z * 0.5)

    if detail_profile["add_lantern_pairs"]:
        lantern_size = vec(80.0 * GAMEPLAY_SCALE, 80.0 * GAMEPLAY_SCALE, 240.0 * GAMEPLAY_SCALE)
        spawn_pair("{0}_GateLantern".format(COMPOUND_NAME), origin, south_y - (config["court_depth"] * 0.12), config["hall_width"] * 0.32, lantern_size, lantern_size.z * 0.5)
        spawn_pair("{0}_AudienceLantern".format(COMPOUND_NAME), origin, center_y - (config["hall_depth"] * 0.72), config["hall_width"] * 0.38, lantern_size, lantern_size.z * 0.5)

    if detail_profile["add_tree_rows"]:
        tree_size = vec(170.0 * GAMEPLAY_SCALE, 170.0 * GAMEPLAY_SCALE, 300.0 * GAMEPLAY_SCALE)
        spawn_pair("{0}_ForeTree".format(COMPOUND_NAME), origin, south_y + (config["court_depth"] * 0.12), config["forecourt_width"] * 0.23, tree_size, tree_size.z * 0.5)
        spawn_pair("{0}_RearTree".format(COMPOUND_NAME), origin, north_y - (config["court_depth"] * 0.08), config["forecourt_width"] * 0.23, tree_size, tree_size.z * 0.5)

    if detail_profile["add_court_steles"]:
        stele_size = vec(120.0 * GAMEPLAY_SCALE, 100.0 * GAMEPLAY_SCALE, 260.0 * GAMEPLAY_SCALE)
        spawn_pair("{0}_MainStele".format(COMPOUND_NAME), origin, center_y + (config["court_depth"] * 0.2), config["hall_width"] * 0.26, stele_size, stele_size.z * 0.5)

    if detail_profile["add_forecourt_path"]:
        spawn_box("{0}_ForecourtPath".format(COMPOUND_NAME), add(origin, vec(0.0, (gate_y + center_y) * 0.5, 14.0 * GAMEPLAY_SCALE)), vec(config["hall_width"] * 0.36, (center_y - gate_y) + (config["hall_depth"] * 0.22), 28.0 * GAMEPLAY_SCALE))

    if detail_profile["add_ceremonial_platform"]:
        spawn_box("{0}_AudiencePlatform".format(COMPOUND_NAME), add(origin, vec(0.0, center_y - (config["hall_depth"] * 0.7), 65.0 * GAMEPLAY_SCALE)), vec(config["hall_width"] * 0.56, config["hall_depth"] * 0.24, 130.0 * GAMEPLAY_SCALE))

    if detail_profile["add_entry_arch"]:
        arch_y = -(config["forecourt_depth"] * 0.5) + (200.0 * GAMEPLAY_SCALE)
        spawn_box("{0}_EntryArchBeam".format(COMPOUND_NAME), add(origin, vec(0.0, arch_y, config["wall_height"] + (120.0 * GAMEPLAY_SCALE))), vec(config["forecourt_width"] * 0.28, 100.0 * GAMEPLAY_SCALE, 90.0 * GAMEPLAY_SCALE))
        spawn_pair("{0}_EntryArchPier".format(COMPOUND_NAME), origin, arch_y, config["forecourt_width"] * 0.14, vec(120.0 * GAMEPLAY_SCALE, 100.0 * GAMEPLAY_SCALE, config["wall_height"] * 1.25), config["wall_height"] * 0.62)

    if detail_profile["add_outer_markers"]:
        marker_size = vec(130.0 * GAMEPLAY_SCALE, 130.0 * GAMEPLAY_SCALE, 320.0 * GAMEPLAY_SCALE)
        spawn_pair("{0}_OuterMarker".format(COMPOUND_NAME), origin, -(config["forecourt_depth"] * 0.5) + (460.0 * GAMEPLAY_SCALE), config["forecourt_width"] * 0.24, marker_size, marker_size.z * 0.5)

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
build_palace_forecourt(spawn_origin)

print("{0} ({1}, {2}) generated at {3}".format(COMPOUND_NAME, PRESET_NAME, resolve_detail_mode(), spawn_origin))
