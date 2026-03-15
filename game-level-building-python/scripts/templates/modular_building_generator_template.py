import math
import random
import unreal


BUILDING_NAME = "ModularBuilding"
PRESET_NAME = "courtyard_hall"
DETAIL_MODE = "blockout"
GAMEPLAY_SCALE = 3.0
RANDOM_SEED = 7

PRESETS = {
    "courtyard_hall": {
        "footprint_width": 1600.0,
        "footprint_depth": 1100.0,
        "plinth_height": 120.0,
        "core_height": 460.0,
        "roof_height": 80.0,
        "roof_style": "layered",
        "symmetry_mode": "strict",
        "front_stairs": True,
        "side_wings": True,
        "courtyard_wall": True,
        "corner_towers": False,
    },
    "gatehouse": {
        "footprint_width": 1800.0,
        "footprint_depth": 900.0,
        "plinth_height": 110.0,
        "core_height": 520.0,
        "roof_height": 70.0,
        "roof_style": "gate",
        "symmetry_mode": "strict",
        "front_stairs": True,
        "side_wings": False,
        "courtyard_wall": False,
        "corner_towers": True,
    },
    "shrine_tower": {
        "footprint_width": 1200.0,
        "footprint_depth": 1200.0,
        "plinth_height": 150.0,
        "core_height": 720.0,
        "roof_height": 85.0,
        "roof_style": "pagoda",
        "symmetry_mode": "mostly_axial",
        "front_stairs": True,
        "side_wings": False,
        "courtyard_wall": False,
        "corner_towers": False,
    },
}

DETAIL_PROFILES = {
    "blockout": {
        "add_eaves": False,
        "add_ridge_caps": False,
        "add_lanterns": False,
        "add_totems": False,
        "add_tree_markers": False,
        "add_corner_finials": False,
        "add_fence_segments": False,
        "add_path_posts": False,
        "add_bracket_rhythm": False,
        "add_lantern_row": False,
        "add_screen_walls": False,
        "add_tree_grove": False,
        "add_deep_roof_tier": False,
        "add_front_colonnade": False,
        "add_gate_composition": False,
        "add_processional_forecourt": False,
        "add_axial_frontispiece": False,
        "add_ceremonial_stair": False,
    },
    "low": {
        "add_eaves": True,
        "add_ridge_caps": True,
        "add_lanterns": False,
        "add_totems": False,
        "add_tree_markers": False,
        "add_corner_finials": False,
        "add_fence_segments": False,
        "add_path_posts": False,
        "add_bracket_rhythm": False,
        "add_lantern_row": False,
        "add_screen_walls": False,
        "add_tree_grove": False,
        "add_deep_roof_tier": False,
        "add_front_colonnade": False,
        "add_gate_composition": False,
        "add_processional_forecourt": False,
        "add_axial_frontispiece": False,
        "add_ceremonial_stair": False,
    },
    "medium": {
        "add_eaves": True,
        "add_ridge_caps": True,
        "add_lanterns": True,
        "add_totems": True,
        "add_tree_markers": True,
        "add_corner_finials": False,
        "add_fence_segments": False,
        "add_path_posts": False,
        "add_bracket_rhythm": False,
        "add_lantern_row": False,
        "add_screen_walls": False,
        "add_tree_grove": False,
        "add_deep_roof_tier": False,
        "add_front_colonnade": False,
        "add_gate_composition": False,
        "add_processional_forecourt": False,
        "add_axial_frontispiece": False,
        "add_ceremonial_stair": False,
    },
    "high": {
        "add_eaves": True,
        "add_ridge_caps": True,
        "add_lanterns": True,
        "add_totems": True,
        "add_tree_markers": True,
        "add_corner_finials": True,
        "add_fence_segments": True,
        "add_path_posts": True,
        "add_bracket_rhythm": True,
        "add_lantern_row": True,
        "add_screen_walls": True,
        "add_tree_grove": True,
        "add_deep_roof_tier": True,
        "add_front_colonnade": True,
        "add_gate_composition": True,
        "add_processional_forecourt": True,
        "add_axial_frontispiece": True,
        "add_ceremonial_stair": True,
    },
}

DETAIL_ALIASES = {
    "ornamented": "medium",
}

OUTPUT_FOLDER = "Generated/{0}".format(BUILDING_NAME)
CUBE_PATH = "/Engine/BasicShapes/Cube.Cube"
CYLINDER_PATH = "/Engine/BasicShapes/Cylinder.Cylinder"
SPHERE_PATH = "/Engine/BasicShapes/Sphere.Sphere"
CONE_PATH = "/Engine/BasicShapes/Cone.Cone"
BASIC_SHAPE_MATERIAL_PATH = "/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"
SCALE_REF_PATH = "/Game/S2/Core_Env/Prototype/S_Placeholder_Char.S_Placeholder_Char"
ENABLE_COLOR_ACCENTS = True
COLOR_PALETTE = {
    "default": unreal.LinearColor(0.58, 0.58, 0.56, 1.0),
    "roof": unreal.LinearColor(0.12, 0.13, 0.15, 1.0),
    "structure": unreal.LinearColor(0.26, 0.27, 0.29, 1.0),
    "stone": unreal.LinearColor(0.60, 0.58, 0.53, 1.0),
    "accent": unreal.LinearColor(0.44, 0.16, 0.10, 1.0),
    "foliage": unreal.LinearColor(0.22, 0.30, 0.20, 1.0),
}


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
cone_mesh = unreal.EditorAssetLibrary.load_asset(CONE_PATH)
basic_shape_material = unreal.EditorAssetLibrary.load_asset(BASIC_SHAPE_MATERIAL_PATH)
scale_ref_mesh = unreal.EditorAssetLibrary.load_asset(SCALE_REF_PATH)
actor_grouping_utils_class = getattr(unreal, "ActorGroupingUtils", None)
generated_actors = []
material_cache = {}

if not cube_mesh:
    raise RuntimeError("Could not load cube mesh: {0}".format(CUBE_PATH))


def get_active_config():
    base_config = dict(PRESETS[PRESET_NAME])
    for key in list(base_config.keys()):
        if key.endswith("width") or key.endswith("depth") or key.endswith("height"):
            base_config[key] *= GAMEPLAY_SCALE
    return base_config


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


def resolve_material_role(label):
    lower_label = label.lower()
    if "roof" in lower_label or "eave" in lower_label or "crest" in lower_label or "finial" in lower_label:
        return "roof"
    if "tree" in lower_label or "grove" in lower_label:
        return "foliage"
    if "plinth" in lower_label or "stair" in lower_label or "path" in lower_label or "terrace" in lower_label:
        return "stone"
    if "gate" in lower_label or "lantern" in lower_label or "frontispiece" in lower_label or "burner" in lower_label or "totem" in lower_label:
        return "accent"
    if "wall" in lower_label or "core" in lower_label or "wing" in lower_label or "colonnade" in lower_label or "screen" in lower_label or "pier" in lower_label:
        return "structure"
    return "default"


def get_tinted_material(role):
    if not ENABLE_COLOR_ACCENTS or not basic_shape_material:
        return None

    cached_material = material_cache.get(role)
    if cached_material:
        return cached_material

    try:
        material = unreal.MaterialInstanceDynamic.create(basic_shape_material, basic_shape_material)
        tint = COLOR_PALETTE.get(role, COLOR_PALETTE["default"])
        for parameter_name in ("Color", "BaseColor", "Tint", "Base Color"):
            try:
                material.set_vector_parameter_value(parameter_name, tint)
            except Exception:
                pass
        material_cache[role] = material
        return material
    except Exception:
        return None


def apply_material_style(smc, label):
    material = get_tinted_material(resolve_material_role(label))
    if not material:
        return
    try:
        smc.set_material(0, material)
    except Exception:
        pass


def spawn_mesh_actor(label, center, size_cm, mesh, yaw=0.0, pitch=0.0, roll=0.0):
    if not mesh:
        return None

    actor = editor_actor_subsystem.spawn_actor_from_class(
        unreal.StaticMeshActor,
        center,
        unreal.Rotator(pitch, yaw, roll),
    )
    actor.set_actor_label(label)
    set_folder(actor)

    smc = actor.get_editor_property("static_mesh_component")
    smc.set_static_mesh(mesh)
    smc.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
    apply_material_style(smc, label)
    actor.set_actor_scale3d(vec(size_cm.x / 100.0, size_cm.y / 100.0, size_cm.z / 100.0))
    return register_actor(actor)


def spawn_box(label, center, size_cm, yaw=0.0):
    return spawn_mesh_actor(label, center, size_cm, cube_mesh, yaw)


def spawn_cylinder(label, center, size_cm, yaw=0.0):
    return spawn_mesh_actor(label, center, size_cm, cylinder_mesh or cube_mesh, yaw)


def spawn_sphere(label, center, size_cm, yaw=0.0):
    return spawn_mesh_actor(label, center, size_cm, sphere_mesh or cube_mesh, yaw)


def spawn_cone(label, center, size_cm, yaw=0.0, pitch=0.0, roll=0.0):
    return spawn_mesh_actor(label, center, size_cm, cone_mesh or cylinder_mesh or cube_mesh, yaw, pitch, roll)


def spawn_sphere_arc_x(label_prefix, origin, span_width, y_pos, z_pos, arc_height, segment_count, sphere_size):
    for index in range(segment_count):
        alpha = float(index) / float(max(segment_count - 1, 1))
        x_pos = (-0.5 + alpha) * span_width
        arc_z = z_pos + (math.sin(alpha * math.pi) * arc_height)
        spawn_sphere("{0}_{1}".format(label_prefix, index + 1), add(origin, vec(x_pos, y_pos, arc_z)), sphere_size)


def spawn_scale_ref(location):
    if not scale_ref_mesh:
        unreal.log_warning("{0}: scale reference mesh missing, continuing without it".format(BUILDING_NAME))
        return None

    actor = editor_actor_subsystem.spawn_actor_from_class(
        unreal.StaticMeshActor,
        location,
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    actor.set_actor_label("{0}_ScaleRef".format(BUILDING_NAME))
    set_folder(actor)

    smc = actor.get_editor_property("static_mesh_component")
    smc.set_static_mesh(scale_ref_mesh)
    smc.set_hidden_in_game(True)
    smc.set_cast_shadow(False)
    smc.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    return register_actor(actor)


def finalize_generated_building():
    if not generated_actors:
        return None

    group_actor = None
    if actor_grouping_utils_class:
        try:
            if not actor_grouping_utils_class.is_grouping_active():
                actor_grouping_utils_class.set_grouping_active(True)
            grouping_utils = actor_grouping_utils_class.get()
            if grouping_utils and grouping_utils.can_group_actors(generated_actors):
                group_actor = grouping_utils.group_actors(generated_actors)
        except Exception as exc:
            unreal.log_warning("{0}: failed to group generated actors ({1})".format(BUILDING_NAME, exc))

    try:
        editor_actor_subsystem.clear_actor_selection_set()
    except Exception:
        pass

    if group_actor:
        try:
            group_actor.set_actor_label("{0}_Group".format(BUILDING_NAME))
        except Exception:
            pass
        set_folder(group_actor)
        try:
            editor_actor_subsystem.set_actor_selection_state(group_actor, True)
        except Exception:
            pass
        return group_actor

    for actor in generated_actors:
        try:
            editor_actor_subsystem.set_actor_selection_state(actor, True)
        except Exception:
            pass
    return None


def spawn_stairs(origin, width, depth, height, steps):
    run = depth / max(steps, 1)
    rise = height / max(steps, 1)
    front_y = origin.y - (depth * 0.6)
    for index in range(steps):
        step_depth = depth - (index * run)
        center = vec(origin.x, front_y - (step_depth * 0.5), origin.z + (index * rise * 0.5))
        spawn_box(
            "{0}_Stair_{1}".format(BUILDING_NAME, index + 1),
            center,
            vec(width, step_depth, rise),
        )


def spawn_corner_towers(origin, width, depth, height):
    offset_x = (width * 0.5) - (180.0 * GAMEPLAY_SCALE)
    offset_y = (depth * 0.5) - (180.0 * GAMEPLAY_SCALE)
    tower_size = vec(240.0 * GAMEPLAY_SCALE, 240.0 * GAMEPLAY_SCALE, height * 0.8)
    for index, (x_pos, y_pos) in enumerate((
        (-offset_x, -offset_y),
        (-offset_x, offset_y),
        (offset_x, -offset_y),
        (offset_x, offset_y),
    )):
        spawn_box(
            "{0}_Tower_{1}".format(BUILDING_NAME, index + 1),
            add(origin, vec(x_pos, y_pos, tower_size.z * 0.5)),
            tower_size,
        )


def spawn_courtyard_walls(origin, width, depth, wall_height):
    wall_thickness = 70.0 * GAMEPLAY_SCALE
    half_width = width * 0.6
    half_depth = depth * 0.6
    wall_specs = (
        ("North", vec(0.0, half_depth, wall_height * 0.5), vec(half_width * 2.0, wall_thickness, wall_height)),
        ("South", vec(0.0, -half_depth, wall_height * 0.5), vec(half_width * 2.0, wall_thickness, wall_height)),
        ("West", vec(-half_width, 0.0, wall_height * 0.5), vec(wall_thickness, half_depth * 2.0, wall_height)),
        ("East", vec(half_width, 0.0, wall_height * 0.5), vec(wall_thickness, half_depth * 2.0, wall_height)),
    )
    for suffix, offset, size in wall_specs:
        spawn_box("{0}_Courtyard_{1}".format(BUILDING_NAME, suffix), add(origin, offset), size)


def spawn_eave_bands(origin, footprint_width, footprint_depth, plinth_height, core_height, roof_height):
    eave_height = max(roof_height * 0.22, 18.0 * GAMEPLAY_SCALE)
    eave_drop = max(roof_height * 0.34, 26.0 * GAMEPLAY_SCALE)
    eave_width = footprint_width * 0.78
    eave_depth = footprint_depth * 0.74
    eave_y = eave_depth * 0.5
    eave_x = eave_width * 0.5
    z_pos = plinth_height + core_height + (roof_height * 0.18) - eave_drop

    spawn_box("{0}_Eave_North".format(BUILDING_NAME), add(origin, vec(0.0, eave_y, z_pos)), vec(eave_width, 28.0 * GAMEPLAY_SCALE, eave_height))
    spawn_box("{0}_Eave_South".format(BUILDING_NAME), add(origin, vec(0.0, -eave_y, z_pos)), vec(eave_width, 28.0 * GAMEPLAY_SCALE, eave_height))
    spawn_box("{0}_Eave_West".format(BUILDING_NAME), add(origin, vec(-eave_x, 0.0, z_pos)), vec(28.0 * GAMEPLAY_SCALE, eave_depth, eave_height))
    spawn_box("{0}_Eave_East".format(BUILDING_NAME), add(origin, vec(eave_x, 0.0, z_pos)), vec(28.0 * GAMEPLAY_SCALE, eave_depth, eave_height))


def spawn_ridge_caps(origin, footprint_width, footprint_depth, plinth_height, core_height, roof_height):
    ridge_z = plinth_height + core_height + roof_height + (roof_height * 0.32)
    spawn_box("{0}_Ridge_Main".format(BUILDING_NAME), add(origin, vec(0.0, 0.0, ridge_z)), vec(footprint_width * 0.42, 18.0 * GAMEPLAY_SCALE, roof_height * 0.24))
    spawn_box("{0}_Ridge_Cross".format(BUILDING_NAME), add(origin, vec(0.0, 0.0, ridge_z)), vec(18.0 * GAMEPLAY_SCALE, footprint_depth * 0.38, roof_height * 0.2))


def spawn_lantern_pair(origin, footprint_width, footprint_depth):
    lantern_offset_x = min(footprint_width * 0.22, 240.0 * GAMEPLAY_SCALE)
    lantern_y = -(footprint_depth * 0.62)
    for suffix, direction in (("L", -1.0), ("R", 1.0)):
        post_origin = add(origin, vec(lantern_offset_x * direction, lantern_y, 0.0))
        spawn_cylinder("{0}_LanternPost_{1}".format(BUILDING_NAME, suffix), add(post_origin, vec(0.0, 0.0, 120.0 * GAMEPLAY_SCALE)), vec(18.0 * GAMEPLAY_SCALE, 18.0 * GAMEPLAY_SCALE, 240.0 * GAMEPLAY_SCALE))
        spawn_sphere("{0}_LanternGlobe_{1}".format(BUILDING_NAME, suffix), add(post_origin, vec(0.0, 0.0, 230.0 * GAMEPLAY_SCALE)), vec(52.0 * GAMEPLAY_SCALE, 52.0 * GAMEPLAY_SCALE, 52.0 * GAMEPLAY_SCALE))
        spawn_box("{0}_LanternFrame_{1}".format(BUILDING_NAME, suffix), add(post_origin, vec(0.0, 0.0, 240.0 * GAMEPLAY_SCALE)), vec(34.0 * GAMEPLAY_SCALE, 34.0 * GAMEPLAY_SCALE, 70.0 * GAMEPLAY_SCALE))
        spawn_box("{0}_LanternCap_{1}".format(BUILDING_NAME, suffix), add(post_origin, vec(0.0, 0.0, 290.0 * GAMEPLAY_SCALE)), vec(22.0 * GAMEPLAY_SCALE, 22.0 * GAMEPLAY_SCALE, 18.0 * GAMEPLAY_SCALE))
        spawn_box("{0}_LanternFoot_{1}".format(BUILDING_NAME, suffix), add(post_origin, vec(0.0, 0.0, 188.0 * GAMEPLAY_SCALE)), vec(26.0 * GAMEPLAY_SCALE, 26.0 * GAMEPLAY_SCALE, 14.0 * GAMEPLAY_SCALE))


def spawn_entry_totems(origin, footprint_width, footprint_depth):
    totem_offset_x = min(footprint_width * 0.3, 320.0 * GAMEPLAY_SCALE)
    totem_y = -(footprint_depth * 0.54)
    for suffix, direction in (("L", -1.0), ("R", 1.0)):
        spawn_box(
            "{0}_Totem_{1}".format(BUILDING_NAME, suffix),
            add(origin, vec(totem_offset_x * direction, totem_y, 150.0 * GAMEPLAY_SCALE)),
            vec(80.0 * GAMEPLAY_SCALE, 80.0 * GAMEPLAY_SCALE, 300.0 * GAMEPLAY_SCALE),
        )


def spawn_cypress_tree(label_prefix, base_origin, trunk_height, foliage_height, foliage_width):
    spawn_sphere("{0}_Root".format(label_prefix), add(base_origin, vec(0.0, 0.0, 18.0 * GAMEPLAY_SCALE)), vec(52.0 * GAMEPLAY_SCALE, 52.0 * GAMEPLAY_SCALE, 36.0 * GAMEPLAY_SCALE))
    trunk_z = trunk_height * 0.5
    spawn_cylinder("{0}_Trunk".format(label_prefix), add(base_origin, vec(0.0, 0.0, trunk_z)), vec(28.0 * GAMEPLAY_SCALE, 28.0 * GAMEPLAY_SCALE, trunk_height))

    lower_height = foliage_height * 0.42
    mid_height = foliage_height * 0.32
    upper_height = foliage_height * 0.24
    lower_z = trunk_height + (lower_height * 0.5)
    mid_z = trunk_height + lower_height + (mid_height * 0.42)
    upper_z = trunk_height + lower_height + mid_height + (upper_height * 0.35)

    spawn_cylinder("{0}_FoliageLower".format(label_prefix), add(base_origin, vec(0.0, 0.0, lower_z)), vec(foliage_width, foliage_width, lower_height))
    spawn_cylinder("{0}_FoliageMid".format(label_prefix), add(base_origin, vec(0.0, 0.0, mid_z)), vec(foliage_width * 0.8, foliage_width * 0.8, mid_height))
    spawn_cylinder("{0}_FoliageUpper".format(label_prefix), add(base_origin, vec(0.0, 0.0, upper_z)), vec(foliage_width * 0.56, foliage_width * 0.56, upper_height))
    spawn_cylinder("{0}_FoliageTip".format(label_prefix), add(base_origin, vec(0.0, 0.0, trunk_height + foliage_height + (46.0 * GAMEPLAY_SCALE))), vec(foliage_width * 0.22, foliage_width * 0.22, 92.0 * GAMEPLAY_SCALE))


def spawn_tree_markers(origin, footprint_width, footprint_depth):
    tree_offset_x = (footprint_width * 0.5) + (260.0 * GAMEPLAY_SCALE)
    tree_offset_y = (footprint_depth * 0.5) + (220.0 * GAMEPLAY_SCALE)
    tree_points = (
        (-tree_offset_x, -tree_offset_y),
        (tree_offset_x, -tree_offset_y),
        (-tree_offset_x, tree_offset_y),
        (tree_offset_x, tree_offset_y),
    )
    for index, (x_pos, y_pos) in enumerate(tree_points):
        base_origin = add(origin, vec(x_pos, y_pos, 0.0))
        spawn_cypress_tree("{0}_Tree_{1}".format(BUILDING_NAME, index + 1), base_origin, 180.0 * GAMEPLAY_SCALE, 340.0 * GAMEPLAY_SCALE, 110.0 * GAMEPLAY_SCALE)


def spawn_corner_finials(origin, footprint_width, footprint_depth, plinth_height, core_height, roof_height):
    finial_size = vec(28.0 * GAMEPLAY_SCALE, 28.0 * GAMEPLAY_SCALE, 70.0 * GAMEPLAY_SCALE)
    offset_x = footprint_width * 0.46
    offset_y = footprint_depth * 0.42
    z_pos = plinth_height + core_height + roof_height + (finial_size.z * 0.5)
    for index, (x_pos, y_pos) in enumerate((
        (-offset_x, -offset_y),
        (-offset_x, offset_y),
        (offset_x, -offset_y),
        (offset_x, offset_y),
    )):
        spawn_cylinder("{0}_Finial_{1}".format(BUILDING_NAME, index + 1), add(origin, vec(x_pos, y_pos, z_pos)), finial_size)
        spawn_sphere("{0}_FinialOrb_{1}".format(BUILDING_NAME, index + 1), add(origin, vec(x_pos, y_pos, z_pos + (70.0 * GAMEPLAY_SCALE))), vec(34.0 * GAMEPLAY_SCALE, 34.0 * GAMEPLAY_SCALE, 34.0 * GAMEPLAY_SCALE))
        spawn_box("{0}_FinialTip_{1}".format(BUILDING_NAME, index + 1), add(origin, vec(x_pos, y_pos, z_pos + (100.0 * GAMEPLAY_SCALE))), vec(16.0 * GAMEPLAY_SCALE, 16.0 * GAMEPLAY_SCALE, 30.0 * GAMEPLAY_SCALE))


def spawn_fence_segments(origin, footprint_width, footprint_depth):
    fence_height = 52.0 * GAMEPLAY_SCALE
    fence_thickness = 16.0 * GAMEPLAY_SCALE
    fence_width = footprint_width * 0.72
    fence_depth = footprint_depth * 0.72
    y_pos = -(footprint_depth * 0.82)
    spawn_box("{0}_Fence_Front".format(BUILDING_NAME), add(origin, vec(0.0, y_pos, fence_height * 0.5)), vec(fence_width, fence_thickness, fence_height))
    spawn_box("{0}_Fence_Left".format(BUILDING_NAME), add(origin, vec(-(fence_width * 0.5), y_pos + (fence_depth * 0.26), fence_height * 0.5)), vec(fence_thickness, fence_depth * 0.52, fence_height))
    spawn_box("{0}_Fence_Right".format(BUILDING_NAME), add(origin, vec(fence_width * 0.5, y_pos + (fence_depth * 0.26), fence_height * 0.5)), vec(fence_thickness, fence_depth * 0.52, fence_height))


def spawn_path_posts(origin, footprint_width, footprint_depth):
    post_height = 90.0 * GAMEPLAY_SCALE
    post_spacing = 260.0 * GAMEPLAY_SCALE
    post_x = min(footprint_width * 0.24, 260.0 * GAMEPLAY_SCALE)
    start_y = -(footprint_depth * 1.02)
    for index in range(4):
        y_pos = start_y + (index * post_spacing)
        for suffix, direction in (("L", -1.0), ("R", 1.0)):
            spawn_cylinder(
                "{0}_PathPost_{1}_{2}".format(BUILDING_NAME, suffix, index + 1),
                add(origin, vec(post_x * direction, y_pos, post_height * 0.5)),
                vec(18.0 * GAMEPLAY_SCALE, 18.0 * GAMEPLAY_SCALE, post_height),
            )


def spawn_bracket_rhythm(origin, footprint_width, footprint_depth, plinth_height, core_height, roof_height):
    bracket_size = vec(32.0 * GAMEPLAY_SCALE, 26.0 * GAMEPLAY_SCALE, 38.0 * GAMEPLAY_SCALE)
    front_y = footprint_depth * 0.34
    side_x = footprint_width * 0.34
    z_pos = plinth_height + core_height + (roof_height * 0.02)
    for index in range(5):
        x_pos = (-0.28 + (index * 0.14)) * footprint_width
        spawn_box("{0}_Bracket_North_{1}".format(BUILDING_NAME, index + 1), add(origin, vec(x_pos, front_y, z_pos)), bracket_size)
        spawn_box("{0}_Bracket_South_{1}".format(BUILDING_NAME, index + 1), add(origin, vec(x_pos, -front_y, z_pos)), bracket_size)
        spawn_box("{0}_BeamTail_North_{1}".format(BUILDING_NAME, index + 1), add(origin, vec(x_pos, front_y + (42.0 * GAMEPLAY_SCALE), z_pos + (26.0 * GAMEPLAY_SCALE))), vec(24.0 * GAMEPLAY_SCALE, 84.0 * GAMEPLAY_SCALE, 24.0 * GAMEPLAY_SCALE))
        spawn_box("{0}_BeamTail_South_{1}".format(BUILDING_NAME, index + 1), add(origin, vec(x_pos, -front_y - (42.0 * GAMEPLAY_SCALE), z_pos + (26.0 * GAMEPLAY_SCALE))), vec(24.0 * GAMEPLAY_SCALE, 84.0 * GAMEPLAY_SCALE, 24.0 * GAMEPLAY_SCALE))
        spawn_box("{0}_BracketDrop_North_{1}".format(BUILDING_NAME, index + 1), add(origin, vec(x_pos, front_y - (24.0 * GAMEPLAY_SCALE), z_pos - (34.0 * GAMEPLAY_SCALE))), vec(18.0 * GAMEPLAY_SCALE, 18.0 * GAMEPLAY_SCALE, 68.0 * GAMEPLAY_SCALE))
        spawn_box("{0}_BracketDrop_South_{1}".format(BUILDING_NAME, index + 1), add(origin, vec(x_pos, -front_y + (24.0 * GAMEPLAY_SCALE), z_pos - (34.0 * GAMEPLAY_SCALE))), vec(18.0 * GAMEPLAY_SCALE, 18.0 * GAMEPLAY_SCALE, 68.0 * GAMEPLAY_SCALE))
    for index in range(3):
        y_pos = (-0.18 + (index * 0.18)) * footprint_depth
        spawn_box("{0}_Bracket_West_{1}".format(BUILDING_NAME, index + 1), add(origin, vec(-side_x, y_pos, z_pos)), vec(26.0 * GAMEPLAY_SCALE, 32.0 * GAMEPLAY_SCALE, 38.0 * GAMEPLAY_SCALE))
        spawn_box("{0}_Bracket_East_{1}".format(BUILDING_NAME, index + 1), add(origin, vec(side_x, y_pos, z_pos)), vec(26.0 * GAMEPLAY_SCALE, 32.0 * GAMEPLAY_SCALE, 38.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_UnderEaveBeam_Front".format(BUILDING_NAME), add(origin, vec(0.0, front_y + (34.0 * GAMEPLAY_SCALE), z_pos + (30.0 * GAMEPLAY_SCALE))), vec(footprint_width * 0.74, 28.0 * GAMEPLAY_SCALE, 28.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_UnderEaveBeam_Back".format(BUILDING_NAME), add(origin, vec(0.0, -front_y - (34.0 * GAMEPLAY_SCALE), z_pos + (30.0 * GAMEPLAY_SCALE))), vec(footprint_width * 0.74, 28.0 * GAMEPLAY_SCALE, 28.0 * GAMEPLAY_SCALE))


def spawn_lantern_row(origin, footprint_width, footprint_depth):
    lantern_y = -(footprint_depth * 0.82)
    for index in range(4):
        x_pos = (-0.24 + (index * 0.16)) * footprint_width
        base_origin = add(origin, vec(x_pos, lantern_y, 0.0))
        spawn_cylinder("{0}_LanternRowPost_{1}".format(BUILDING_NAME, index + 1), add(base_origin, vec(0.0, 0.0, 132.0 * GAMEPLAY_SCALE)), vec(18.0 * GAMEPLAY_SCALE, 18.0 * GAMEPLAY_SCALE, 264.0 * GAMEPLAY_SCALE))
        spawn_sphere("{0}_LanternRowGlobe_{1}".format(BUILDING_NAME, index + 1), add(base_origin, vec(0.0, 0.0, 246.0 * GAMEPLAY_SCALE)), vec(58.0 * GAMEPLAY_SCALE, 58.0 * GAMEPLAY_SCALE, 58.0 * GAMEPLAY_SCALE))
        spawn_box("{0}_LanternRowFrame_{1}".format(BUILDING_NAME, index + 1), add(base_origin, vec(0.0, 0.0, 252.0 * GAMEPLAY_SCALE)), vec(36.0 * GAMEPLAY_SCALE, 36.0 * GAMEPLAY_SCALE, 82.0 * GAMEPLAY_SCALE))
        spawn_box("{0}_LanternRowCap_{1}".format(BUILDING_NAME, index + 1), add(base_origin, vec(0.0, 0.0, 306.0 * GAMEPLAY_SCALE)), vec(24.0 * GAMEPLAY_SCALE, 24.0 * GAMEPLAY_SCALE, 18.0 * GAMEPLAY_SCALE))


def spawn_screen_walls(origin, footprint_width, footprint_depth):
    screen_y = -(footprint_depth * 1.02)
    spawn_box("{0}_Screen_Center".format(BUILDING_NAME), add(origin, vec(0.0, screen_y, 90.0 * GAMEPLAY_SCALE)), vec(footprint_width * 0.34, 22.0 * GAMEPLAY_SCALE, 180.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_Screen_Left".format(BUILDING_NAME), add(origin, vec(-(footprint_width * 0.32), screen_y + (140.0 * GAMEPLAY_SCALE), 70.0 * GAMEPLAY_SCALE)), vec(22.0 * GAMEPLAY_SCALE, 280.0 * GAMEPLAY_SCALE, 140.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_Screen_Right".format(BUILDING_NAME), add(origin, vec(footprint_width * 0.32, screen_y + (140.0 * GAMEPLAY_SCALE), 70.0 * GAMEPLAY_SCALE)), vec(22.0 * GAMEPLAY_SCALE, 280.0 * GAMEPLAY_SCALE, 140.0 * GAMEPLAY_SCALE))


def spawn_tree_grove(origin, footprint_width, footprint_depth):
    grove_points = (
        (-0.78 * footprint_width, -0.88 * footprint_depth),
        (-0.62 * footprint_width, -0.64 * footprint_depth),
        (0.78 * footprint_width, -0.88 * footprint_depth),
        (0.62 * footprint_width, -0.64 * footprint_depth),
        (-0.76 * footprint_width, 0.82 * footprint_depth),
        (0.76 * footprint_width, 0.82 * footprint_depth),
    )
    for index, (x_pos, y_pos) in enumerate(grove_points):
        base_origin = add(origin, vec(x_pos, y_pos, 0.0))
        spawn_cypress_tree("{0}_Grove_{1}".format(BUILDING_NAME, index + 1), base_origin, 210.0 * GAMEPLAY_SCALE, 420.0 * GAMEPLAY_SCALE, 126.0 * GAMEPLAY_SCALE)


def spawn_deep_roof_tier(origin, footprint_width, footprint_depth, plinth_height, core_height, roof_height):
    skirt_z = plinth_height + core_height + (roof_height * 0.05)
    lower_height = roof_height * 0.42
    mid_height = roof_height * 0.22
    upper_height = roof_height * 0.16
    spawn_box("{0}_RoofSkirt_Lower".format(BUILDING_NAME), add(origin, vec(0.0, 0.0, skirt_z)), vec(footprint_width * 1.28, footprint_depth * 1.22, lower_height))
    spawn_box("{0}_RoofSkirt_Mid".format(BUILDING_NAME), add(origin, vec(0.0, 0.0, skirt_z + (lower_height * 0.72))), vec(footprint_width * 1.1, footprint_depth * 1.04, mid_height))
    spawn_box("{0}_RoofSkirt_Upper".format(BUILDING_NAME), add(origin, vec(0.0, 0.0, skirt_z + lower_height + (mid_height * 0.4))), vec(footprint_width * 0.92, footprint_depth * 0.86, upper_height))

    edge_height = roof_height * 0.12
    edge_z = skirt_z + (lower_height * 0.3)
    spawn_box("{0}_RoofEdge_North".format(BUILDING_NAME), add(origin, vec(0.0, footprint_depth * 0.58, edge_z)), vec(footprint_width * 1.08, 34.0 * GAMEPLAY_SCALE, edge_height))
    spawn_box("{0}_RoofEdge_South".format(BUILDING_NAME), add(origin, vec(0.0, -(footprint_depth * 0.58), edge_z)), vec(footprint_width * 1.08, 34.0 * GAMEPLAY_SCALE, edge_height))
    spawn_box("{0}_RoofEdge_West".format(BUILDING_NAME), add(origin, vec(-(footprint_width * 0.6), 0.0, edge_z)), vec(34.0 * GAMEPLAY_SCALE, footprint_depth * 1.02, edge_height))
    spawn_box("{0}_RoofEdge_East".format(BUILDING_NAME), add(origin, vec(footprint_width * 0.6, 0.0, edge_z)), vec(34.0 * GAMEPLAY_SCALE, footprint_depth * 1.02, edge_height))

    lift_height = roof_height * 0.16
    lift_z = edge_z + (edge_height * 0.35)
    spawn_box("{0}_RoofLift_North".format(BUILDING_NAME), add(origin, vec(0.0, footprint_depth * 0.66, lift_z)), vec(footprint_width * 0.8, 26.0 * GAMEPLAY_SCALE, lift_height))
    spawn_box("{0}_RoofLift_South".format(BUILDING_NAME), add(origin, vec(0.0, -(footprint_depth * 0.66), lift_z)), vec(footprint_width * 0.8, 26.0 * GAMEPLAY_SCALE, lift_height))

    monitor_z = plinth_height + core_height + roof_height + (roof_height * 0.52)
    spawn_box("{0}_RoofMonitor_Base".format(BUILDING_NAME), add(origin, vec(0.0, 0.0, monitor_z)), vec(footprint_width * 0.46, footprint_depth * 0.32, roof_height * 0.24))
    spawn_box("{0}_RoofMonitor_Upper".format(BUILDING_NAME), add(origin, vec(0.0, 0.0, monitor_z + (roof_height * 0.18))), vec(footprint_width * 0.3, footprint_depth * 0.22, roof_height * 0.18))
    spawn_box("{0}_RoofCrest_Long".format(BUILDING_NAME), add(origin, vec(0.0, 0.0, monitor_z + (roof_height * 0.3))), vec(footprint_width * 0.58, 20.0 * GAMEPLAY_SCALE, roof_height * 0.12))
    spawn_box("{0}_RoofCrest_Cross".format(BUILDING_NAME), add(origin, vec(0.0, 0.0, monitor_z + (roof_height * 0.26))), vec(24.0 * GAMEPLAY_SCALE, footprint_depth * 0.38, roof_height * 0.1))

    corner_size = vec(220.0 * GAMEPLAY_SCALE, 90.0 * GAMEPLAY_SCALE, roof_height * 0.26)
    corner_x = footprint_width * 0.58
    corner_y = footprint_depth * 0.54
    corner_z = plinth_height + core_height + roof_height + (corner_size.z * 0.4)
    for index, (x_pos, y_pos) in enumerate((
        (-corner_x, -corner_y),
        (-corner_x, corner_y),
        (corner_x, -corner_y),
        (corner_x, corner_y),
    )):
        spawn_box("{0}_RoofWing_{1}".format(BUILDING_NAME, index + 1), add(origin, vec(x_pos, y_pos, corner_z)), corner_size)


def spawn_front_colonnade(origin, footprint_width, footprint_depth, plinth_height, core_height):
    column_height = core_height * 0.82
    column_z = plinth_height + (column_height * 0.5)
    front_y = -(footprint_depth * 0.38)
    for index in range(7):
        x_pos = (-0.3 + (index * 0.1)) * footprint_width
        spawn_cylinder("{0}_Colonnade_{1}".format(BUILDING_NAME, index + 1), add(origin, vec(x_pos, front_y, column_z)), vec(34.0 * GAMEPLAY_SCALE, 34.0 * GAMEPLAY_SCALE, column_height))

    for suffix, x_direction in (("West", -1.0), ("East", 1.0)):
        return_x = (footprint_width * 0.34) * x_direction
        for index in range(2):
            return_y = front_y + ((index + 1) * 150.0 * GAMEPLAY_SCALE)
            spawn_cylinder("{0}_ColonnadeReturn_{1}_{2}".format(BUILDING_NAME, suffix, index + 1), add(origin, vec(return_x, return_y, column_z)), vec(30.0 * GAMEPLAY_SCALE, 30.0 * GAMEPLAY_SCALE, column_height * 0.92))

    lintel_z = plinth_height + column_height + (36.0 * GAMEPLAY_SCALE)
    spawn_box("{0}_ColonnadeLintel".format(BUILDING_NAME), add(origin, vec(0.0, front_y, lintel_z)), vec(footprint_width * 0.58, 28.0 * GAMEPLAY_SCALE, 72.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_ColonnadeFrieze".format(BUILDING_NAME), add(origin, vec(0.0, front_y - (24.0 * GAMEPLAY_SCALE), lintel_z + (42.0 * GAMEPLAY_SCALE))), vec(footprint_width * 0.66, 22.0 * GAMEPLAY_SCALE, 48.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_ColonnadeCanopy_Lower".format(BUILDING_NAME), add(origin, vec(0.0, front_y - (64.0 * GAMEPLAY_SCALE), lintel_z + (88.0 * GAMEPLAY_SCALE))), vec(footprint_width * 0.5, 200.0 * GAMEPLAY_SCALE, 54.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_ColonnadeCanopy_Upper".format(BUILDING_NAME), add(origin, vec(0.0, front_y - (64.0 * GAMEPLAY_SCALE), lintel_z + (130.0 * GAMEPLAY_SCALE))), vec(footprint_width * 0.34, 150.0 * GAMEPLAY_SCALE, 38.0 * GAMEPLAY_SCALE))


def spawn_timber_portal(label_prefix, origin, center_y, sill_z, opening_width, opening_height, frame_depth, stile_width):
    back_panel_height = opening_height + (160.0 * GAMEPLAY_SCALE)
    back_panel_z = sill_z + (back_panel_height * 0.5) + (10.0 * GAMEPLAY_SCALE)
    spawn_box("{0}_BackPanel".format(label_prefix), add(origin, vec(0.0, center_y - (frame_depth * 0.35), back_panel_z)), vec(opening_width + (stile_width * 3.0), frame_depth * 0.4, back_panel_height))

    stile_height = opening_height + (140.0 * GAMEPLAY_SCALE)
    stile_z = sill_z + (stile_height * 0.5)
    stile_offset_x = (opening_width * 0.5) + (stile_width * 0.5)
    header_height = 84.0 * GAMEPLAY_SCALE
    header_z = sill_z + opening_height + (header_height * 0.5) + (42.0 * GAMEPLAY_SCALE)
    lintel_width = opening_width + (stile_width * 2.0)

    spawn_box("{0}_PortalStile_Left".format(label_prefix), add(origin, vec(-stile_offset_x, center_y, stile_z)), vec(stile_width, frame_depth, stile_height))
    spawn_box("{0}_PortalStile_Right".format(label_prefix), add(origin, vec(stile_offset_x, center_y, stile_z)), vec(stile_width, frame_depth, stile_height))
    spawn_box("{0}_PortalHeader".format(label_prefix), add(origin, vec(0.0, center_y, header_z)), vec(lintel_width, frame_depth, header_height))
    spawn_box("{0}_PortalThreshold".format(label_prefix), add(origin, vec(0.0, center_y + (frame_depth * 0.15), sill_z + (24.0 * GAMEPLAY_SCALE))), vec(lintel_width, frame_depth * 1.2, 48.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_PortalLintelFace".format(label_prefix), add(origin, vec(0.0, center_y + (frame_depth * 0.22), header_z)), vec(lintel_width * 0.94, frame_depth * 0.3, header_height * 0.7))

    leaf_width = (opening_width * 0.5) - (10.0 * GAMEPLAY_SCALE)
    leaf_height = opening_height * 0.92
    leaf_z = sill_z + (leaf_height * 0.5) + (34.0 * GAMEPLAY_SCALE)
    leaf_offset_x = (leaf_width * 0.5) + (8.0 * GAMEPLAY_SCALE)
    for suffix, direction in (("Left", -1.0), ("Right", 1.0)):
        leaf_center = add(origin, vec(leaf_offset_x * direction, center_y + (frame_depth * 0.08), leaf_z))
        spawn_box("{0}_DoorLeaf_{1}".format(label_prefix, suffix), leaf_center, vec(leaf_width, frame_depth * 0.6, leaf_height))
        spawn_box("{0}_DoorRailTop_{1}".format(label_prefix, suffix), add(leaf_center, vec(0.0, 2.0 * GAMEPLAY_SCALE, leaf_height * 0.22)), vec(leaf_width * 0.84, frame_depth * 0.3, 18.0 * GAMEPLAY_SCALE))
        spawn_box("{0}_DoorRailMid_{1}".format(label_prefix, suffix), add(leaf_center, vec(0.0, 2.0 * GAMEPLAY_SCALE, 0.0)), vec(leaf_width * 0.84, frame_depth * 0.3, 16.0 * GAMEPLAY_SCALE))
        spawn_box("{0}_DoorRailLow_{1}".format(label_prefix, suffix), add(leaf_center, vec(0.0, 2.0 * GAMEPLAY_SCALE, -(leaf_height * 0.22))), vec(leaf_width * 0.84, frame_depth * 0.3, 18.0 * GAMEPLAY_SCALE))
        for index in range(4):
            stud_z = leaf_z - (leaf_height * 0.24) + (index * leaf_height * 0.16)
            spawn_box("{0}_Stud_{1}_{2}".format(label_prefix, suffix, index + 1), add(origin, vec(leaf_offset_x * direction, center_y + (frame_depth * 0.24), stud_z)), vec(10.0 * GAMEPLAY_SCALE, 10.0 * GAMEPLAY_SCALE, 10.0 * GAMEPLAY_SCALE))

    side_screen_width = stile_width * 0.9
    side_screen_height = opening_height * 0.62
    side_screen_z = sill_z + (side_screen_height * 0.5) + (80.0 * GAMEPLAY_SCALE)
    side_screen_offset_x = stile_offset_x + (stile_width * 0.9)
    spawn_box("{0}_SideScreen_Left".format(label_prefix), add(origin, vec(-side_screen_offset_x, center_y - (frame_depth * 0.14), side_screen_z)), vec(side_screen_width, frame_depth * 0.45, side_screen_height))
    spawn_box("{0}_SideScreen_Right".format(label_prefix), add(origin, vec(side_screen_offset_x, center_y - (frame_depth * 0.14), side_screen_z)), vec(side_screen_width, frame_depth * 0.45, side_screen_height))


def spawn_axial_frontispiece(origin, footprint_width, footprint_depth, plinth_height, core_height):
    porch_y = -(footprint_depth * 0.46)
    frame_height = core_height * 0.74
    frame_z = plinth_height + (frame_height * 0.5)
    spawn_box("{0}_Frontispiece_Platform".format(BUILDING_NAME), add(origin, vec(0.0, porch_y - (90.0 * GAMEPLAY_SCALE), plinth_height + (44.0 * GAMEPLAY_SCALE))), vec(footprint_width * 0.4, 260.0 * GAMEPLAY_SCALE, 88.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_Frontispiece_LeftPier".format(BUILDING_NAME), add(origin, vec(-(footprint_width * 0.12), porch_y, frame_z)), vec(76.0 * GAMEPLAY_SCALE, 92.0 * GAMEPLAY_SCALE, frame_height))
    spawn_box("{0}_Frontispiece_RightPier".format(BUILDING_NAME), add(origin, vec(footprint_width * 0.12, porch_y, frame_z)), vec(76.0 * GAMEPLAY_SCALE, 92.0 * GAMEPLAY_SCALE, frame_height))
    spawn_box("{0}_Frontispiece_CenterFrame".format(BUILDING_NAME), add(origin, vec(0.0, porch_y + (28.0 * GAMEPLAY_SCALE), plinth_height + (frame_height * 0.52))), vec(footprint_width * 0.18, 80.0 * GAMEPLAY_SCALE, frame_height * 0.88))
    lintel_z = plinth_height + frame_height + (54.0 * GAMEPLAY_SCALE)
    spawn_box("{0}_Frontispiece_Lintel".format(BUILDING_NAME), add(origin, vec(0.0, porch_y, lintel_z)), vec(footprint_width * 0.34, 104.0 * GAMEPLAY_SCALE, 108.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_Frontispiece_CanopyLower".format(BUILDING_NAME), add(origin, vec(0.0, porch_y - (42.0 * GAMEPLAY_SCALE), lintel_z + (74.0 * GAMEPLAY_SCALE))), vec(footprint_width * 0.42, 180.0 * GAMEPLAY_SCALE, 54.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_Frontispiece_CanopyUpper".format(BUILDING_NAME), add(origin, vec(0.0, porch_y - (42.0 * GAMEPLAY_SCALE), lintel_z + (118.0 * GAMEPLAY_SCALE))), vec(footprint_width * 0.26, 130.0 * GAMEPLAY_SCALE, 36.0 * GAMEPLAY_SCALE))
    spawn_timber_portal("{0}_Frontispiece".format(BUILDING_NAME), origin, -(footprint_depth * 0.22), plinth_height + (8.0 * GAMEPLAY_SCALE), footprint_width * 0.24, frame_height * 0.68, 42.0 * GAMEPLAY_SCALE, 36.0 * GAMEPLAY_SCALE)
    spawn_box("{0}_Frontispiece_StepBlock".format(BUILDING_NAME), add(origin, vec(0.0, porch_y - (170.0 * GAMEPLAY_SCALE), plinth_height * 0.5)), vec(footprint_width * 0.22, 180.0 * GAMEPLAY_SCALE, plinth_height))


def spawn_gate_composition(origin, footprint_width, footprint_depth, approach_offset_x):
    gate_y = -(footprint_depth * 1.42)
    gate_center = add(origin, vec(approach_offset_x, 0.0, 0.0))
    screen_height = 180.0 * GAMEPLAY_SCALE
    screen_depth = 26.0 * GAMEPLAY_SCALE
    spawn_box("{0}_GateScreen_Main".format(BUILDING_NAME), add(gate_center, vec(0.0, gate_y, screen_height * 0.5)), vec(footprint_width * 0.46, screen_depth, screen_height))
    spawn_box("{0}_GateScreen_Left".format(BUILDING_NAME), add(gate_center, vec(-(footprint_width * 0.42), gate_y + (180.0 * GAMEPLAY_SCALE), 140.0 * GAMEPLAY_SCALE)), vec(48.0 * GAMEPLAY_SCALE, 420.0 * GAMEPLAY_SCALE, 280.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_GateScreen_Right".format(BUILDING_NAME), add(gate_center, vec(footprint_width * 0.42, gate_y + (180.0 * GAMEPLAY_SCALE), 140.0 * GAMEPLAY_SCALE)), vec(48.0 * GAMEPLAY_SCALE, 420.0 * GAMEPLAY_SCALE, 280.0 * GAMEPLAY_SCALE))
    pillar_height = 420.0 * GAMEPLAY_SCALE
    for suffix, direction in (("L", -1.0), ("R", 1.0)):
        spawn_cylinder(
            "{0}_GatePillar_{1}".format(BUILDING_NAME, suffix),
            add(gate_center, vec((footprint_width * 0.32) * direction, gate_y - (60.0 * GAMEPLAY_SCALE), pillar_height * 0.5)),
            vec(54.0 * GAMEPLAY_SCALE, 54.0 * GAMEPLAY_SCALE, pillar_height),
        )
        spawn_box("{0}_GatePier_{1}".format(BUILDING_NAME, suffix), add(gate_center, vec((footprint_width * 0.44) * direction, gate_y + (10.0 * GAMEPLAY_SCALE), 180.0 * GAMEPLAY_SCALE)), vec(136.0 * GAMEPLAY_SCALE, 150.0 * GAMEPLAY_SCALE, 360.0 * GAMEPLAY_SCALE))
        spawn_box("{0}_GateBracketBlock_{1}".format(BUILDING_NAME, suffix), add(gate_center, vec((footprint_width * 0.33) * direction, gate_y - (4.0 * GAMEPLAY_SCALE), pillar_height - (24.0 * GAMEPLAY_SCALE))), vec(64.0 * GAMEPLAY_SCALE, 64.0 * GAMEPLAY_SCALE, 48.0 * GAMEPLAY_SCALE))
    lintel_z = pillar_height + (44.0 * GAMEPLAY_SCALE)
    spawn_box("{0}_GateLintel".format(BUILDING_NAME), add(gate_center, vec(0.0, gate_y - (60.0 * GAMEPLAY_SCALE), lintel_z)), vec(footprint_width * 0.88, 48.0 * GAMEPLAY_SCALE, 104.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_GateCrossBeam".format(BUILDING_NAME), add(gate_center, vec(0.0, gate_y + (16.0 * GAMEPLAY_SCALE), pillar_height - (46.0 * GAMEPLAY_SCALE))), vec(footprint_width * 0.72, 56.0 * GAMEPLAY_SCALE, 42.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_GateRoofLower".format(BUILDING_NAME), add(gate_center, vec(0.0, gate_y - (60.0 * GAMEPLAY_SCALE), lintel_z + (84.0 * GAMEPLAY_SCALE))), vec(footprint_width * 1.08, 380.0 * GAMEPLAY_SCALE, 82.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_GateRoofUpper".format(BUILDING_NAME), add(gate_center, vec(0.0, gate_y - (60.0 * GAMEPLAY_SCALE), lintel_z + (146.0 * GAMEPLAY_SCALE))), vec(footprint_width * 0.72, 240.0 * GAMEPLAY_SCALE, 56.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_GateRoofWing_Left".format(BUILDING_NAME), add(gate_center, vec(-(footprint_width * 0.48), gate_y - (56.0 * GAMEPLAY_SCALE), lintel_z + (94.0 * GAMEPLAY_SCALE))), vec(footprint_width * 0.24, 220.0 * GAMEPLAY_SCALE, 60.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_GateRoofWing_Right".format(BUILDING_NAME), add(gate_center, vec(footprint_width * 0.48, gate_y - (56.0 * GAMEPLAY_SCALE), lintel_z + (94.0 * GAMEPLAY_SCALE))), vec(footprint_width * 0.24, 220.0 * GAMEPLAY_SCALE, 60.0 * GAMEPLAY_SCALE))
    spawn_timber_portal("{0}_Gate".format(BUILDING_NAME), gate_center, gate_y + (34.0 * GAMEPLAY_SCALE), 0.0, footprint_width * 0.34, 290.0 * GAMEPLAY_SCALE, 34.0 * GAMEPLAY_SCALE, 42.0 * GAMEPLAY_SCALE)
    spawn_box("{0}_GateThreshold".format(BUILDING_NAME), add(gate_center, vec(0.0, gate_y + (110.0 * GAMEPLAY_SCALE), 40.0 * GAMEPLAY_SCALE)), vec(footprint_width * 0.56, 260.0 * GAMEPLAY_SCALE, 80.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_GateWingWall_Left".format(BUILDING_NAME), add(gate_center, vec(-(footprint_width * 0.66), gate_y + (220.0 * GAMEPLAY_SCALE), 120.0 * GAMEPLAY_SCALE)), vec(footprint_width * 0.24, 140.0 * GAMEPLAY_SCALE, 240.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_GateWingWall_Right".format(BUILDING_NAME), add(gate_center, vec(footprint_width * 0.66, gate_y + (220.0 * GAMEPLAY_SCALE), 120.0 * GAMEPLAY_SCALE)), vec(footprint_width * 0.24, 140.0 * GAMEPLAY_SCALE, 240.0 * GAMEPLAY_SCALE))
    for index in range(4):
        panel_y = gate_y + (120.0 * GAMEPLAY_SCALE) + (index * 70.0 * GAMEPLAY_SCALE)
        spawn_box("{0}_GateScreenRailLeft_{1}".format(BUILDING_NAME, index + 1), add(gate_center, vec(-(footprint_width * 0.42), panel_y, 160.0 * GAMEPLAY_SCALE)), vec(26.0 * GAMEPLAY_SCALE, 18.0 * GAMEPLAY_SCALE, 240.0 * GAMEPLAY_SCALE))
        spawn_box("{0}_GateScreenRailRight_{1}".format(BUILDING_NAME, index + 1), add(gate_center, vec(footprint_width * 0.42, panel_y, 160.0 * GAMEPLAY_SCALE)), vec(26.0 * GAMEPLAY_SCALE, 18.0 * GAMEPLAY_SCALE, 240.0 * GAMEPLAY_SCALE))


def spawn_processional_forecourt(origin, footprint_width, footprint_depth, plinth_height, approach_offset_x):
    terrace_height = max(plinth_height * 0.26, 42.0 * GAMEPLAY_SCALE)
    terrace_depth = footprint_depth * 0.6
    terrace_y = -(footprint_depth * 1.02)
    forecourt_center = add(origin, vec(approach_offset_x * 0.58, 0.0, 0.0))
    spawn_box("{0}_ForecourtTerrace".format(BUILDING_NAME), add(forecourt_center, vec(0.0, terrace_y, terrace_height * 0.5)), vec(footprint_width * 0.78, terrace_depth, terrace_height))
    spawn_box("{0}_ForecourtPath".format(BUILDING_NAME), add(forecourt_center, vec(0.0, terrace_y - (terrace_depth * 1.05), 18.0 * GAMEPLAY_SCALE)), vec(footprint_width * 0.22, terrace_depth * 2.1, 36.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_ForecourtPath_Left".format(BUILDING_NAME), add(forecourt_center, vec(-(footprint_width * 0.18), terrace_y - (terrace_depth * 0.12), 14.0 * GAMEPLAY_SCALE)), vec(footprint_width * 0.12, terrace_depth * 0.76, 28.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_ForecourtPath_Right".format(BUILDING_NAME), add(forecourt_center, vec(footprint_width * 0.18, terrace_y - (terrace_depth * 0.34), 14.0 * GAMEPLAY_SCALE)), vec(footprint_width * 0.12, terrace_depth * 0.92, 28.0 * GAMEPLAY_SCALE))

    stele_z = terrace_height + (110.0 * GAMEPLAY_SCALE)
    stele_y = terrace_y + (terrace_depth * 0.22)
    for suffix, direction in (("L", -1.0), ("R", 1.0)):
        stele_x = (footprint_width * 0.23) * direction
        spawn_box("{0}_ForecourtSteleBase_{1}".format(BUILDING_NAME, suffix), add(forecourt_center, vec(stele_x, stele_y, terrace_height + (24.0 * GAMEPLAY_SCALE))), vec(92.0 * GAMEPLAY_SCALE, 92.0 * GAMEPLAY_SCALE, 48.0 * GAMEPLAY_SCALE))
        spawn_box("{0}_ForecourtStele_{1}".format(BUILDING_NAME, suffix), add(forecourt_center, vec(stele_x, stele_y, stele_z)), vec(74.0 * GAMEPLAY_SCALE, 28.0 * GAMEPLAY_SCALE, 220.0 * GAMEPLAY_SCALE))

    burner_y = terrace_y - (terrace_depth * 0.18)
    spawn_box("{0}_ForecourtBurnerBase".format(BUILDING_NAME), add(forecourt_center, vec(0.0, burner_y, terrace_height + (22.0 * GAMEPLAY_SCALE))), vec(88.0 * GAMEPLAY_SCALE, 88.0 * GAMEPLAY_SCALE, 44.0 * GAMEPLAY_SCALE))
    spawn_cylinder("{0}_ForecourtBurner".format(BUILDING_NAME), add(forecourt_center, vec(0.0, burner_y, terrace_height + (88.0 * GAMEPLAY_SCALE))), vec(66.0 * GAMEPLAY_SCALE, 66.0 * GAMEPLAY_SCALE, 92.0 * GAMEPLAY_SCALE))
    spawn_sphere("{0}_ForecourtBurnerOrb".format(BUILDING_NAME), add(forecourt_center, vec(0.0, burner_y, terrace_height + (146.0 * GAMEPLAY_SCALE))), vec(54.0 * GAMEPLAY_SCALE, 54.0 * GAMEPLAY_SCALE, 54.0 * GAMEPLAY_SCALE))
    spawn_box("{0}_ForecourtBurnerCap".format(BUILDING_NAME), add(forecourt_center, vec(0.0, burner_y, terrace_height + (188.0 * GAMEPLAY_SCALE))), vec(28.0 * GAMEPLAY_SCALE, 28.0 * GAMEPLAY_SCALE, 18.0 * GAMEPLAY_SCALE))
    for suffix, direction in (("L", -1.0), ("R", 1.0)):
        marker_x = (footprint_width * 0.3) * direction
        marker_y = terrace_y - (terrace_depth * 0.46)
        spawn_box("{0}_ForecourtMarker_{1}".format(BUILDING_NAME, suffix), add(forecourt_center, vec(marker_x, marker_y, terrace_height + (60.0 * GAMEPLAY_SCALE))), vec(72.0 * GAMEPLAY_SCALE, 72.0 * GAMEPLAY_SCALE, 120.0 * GAMEPLAY_SCALE))


def spawn_ceremonial_stair(origin, footprint_width, footprint_depth, plinth_height, approach_offset_x):
    lower_depth = 420.0 * GAMEPLAY_SCALE
    upper_depth = 260.0 * GAMEPLAY_SCALE
    stair_y = -(footprint_depth * 0.86)
    stair_center = add(origin, vec(approach_offset_x, 0.0, 0.0))
    spawn_box("{0}_CeremonialStair_Lower".format(BUILDING_NAME), add(stair_center, vec(0.0, stair_y, plinth_height * 0.24)), vec(footprint_width * 0.36, lower_depth, plinth_height * 0.48))
    spawn_box("{0}_CeremonialStair_Upper".format(BUILDING_NAME), add(stair_center, vec(0.0, stair_y + (lower_depth * 0.34), plinth_height * 0.44)), vec(footprint_width * 0.22, upper_depth, plinth_height * 0.38))
    cheek_height = plinth_height * 0.9
    for suffix, direction in (("L", -1.0), ("R", 1.0)):
        spawn_box("{0}_CeremonialStairCheek_{1}".format(BUILDING_NAME, suffix), add(stair_center, vec((footprint_width * 0.16) * direction, stair_y + (lower_depth * 0.1), cheek_height * 0.5)), vec(72.0 * GAMEPLAY_SCALE, lower_depth * 0.82, cheek_height))


def add_detail_pass(origin, config, footprint_width, footprint_depth, plinth_height, core_height, roof_height):
    detail_profile = get_detail_profile()
    approach_offset_x = footprint_width * 0.28
    if detail_profile["add_eaves"]:
        spawn_eave_bands(origin, footprint_width, footprint_depth, plinth_height, core_height, roof_height)
    if detail_profile["add_ridge_caps"]:
        spawn_ridge_caps(origin, footprint_width, footprint_depth, plinth_height, core_height, roof_height)
    if detail_profile["add_lanterns"]:
        spawn_lantern_pair(origin, footprint_width, footprint_depth)
    if detail_profile["add_totems"] and config["front_stairs"]:
        spawn_entry_totems(origin, footprint_width, footprint_depth)
    if detail_profile["add_tree_markers"]:
        spawn_tree_markers(origin, footprint_width, footprint_depth)
    if detail_profile["add_corner_finials"]:
        spawn_corner_finials(origin, footprint_width, footprint_depth, plinth_height, core_height, roof_height)
    if detail_profile["add_fence_segments"]:
        spawn_fence_segments(origin, footprint_width, footprint_depth)
    if detail_profile["add_path_posts"] and config["front_stairs"]:
        spawn_path_posts(origin, footprint_width, footprint_depth)
    if detail_profile["add_bracket_rhythm"]:
        spawn_bracket_rhythm(origin, footprint_width, footprint_depth, plinth_height, core_height, roof_height)
    if detail_profile["add_lantern_row"]:
        spawn_lantern_row(origin, footprint_width, footprint_depth)
    if detail_profile["add_screen_walls"]:
        spawn_screen_walls(origin, footprint_width, footprint_depth)
    if detail_profile["add_tree_grove"]:
        spawn_tree_grove(origin, footprint_width, footprint_depth)
    if detail_profile["add_deep_roof_tier"]:
        spawn_deep_roof_tier(origin, footprint_width, footprint_depth, plinth_height, core_height, roof_height)
    if detail_profile["add_front_colonnade"]:
        spawn_front_colonnade(origin, footprint_width, footprint_depth, plinth_height, core_height)
    if detail_profile["add_axial_frontispiece"]:
        spawn_axial_frontispiece(origin, footprint_width, footprint_depth, plinth_height, core_height)
    if detail_profile["add_gate_composition"]:
        spawn_gate_composition(origin, footprint_width, footprint_depth, approach_offset_x)
    if detail_profile["add_processional_forecourt"]:
        spawn_processional_forecourt(origin, footprint_width, footprint_depth, plinth_height, approach_offset_x)
    if detail_profile["add_ceremonial_stair"] and config["front_stairs"]:
        spawn_ceremonial_stair(origin, footprint_width, footprint_depth, plinth_height, approach_offset_x)


def build_modular_building(origin):
    random.seed(RANDOM_SEED)
    config = get_active_config()
    detail_profile = get_detail_profile()
    generated_actors[:] = []
    destroy_previous(BUILDING_NAME)

    footprint_width = config["footprint_width"]
    footprint_depth = config["footprint_depth"]
    plinth_height = config["plinth_height"]
    core_height = config["core_height"]
    roof_height = config["roof_height"]

    spawn_box(
        "{0}_Plinth".format(BUILDING_NAME),
        add(origin, vec(0.0, 0.0, plinth_height * 0.5)),
        vec(footprint_width, footprint_depth, plinth_height),
    )

    spawn_box(
        "{0}_Core".format(BUILDING_NAME),
        add(origin, vec(0.0, 0.0, plinth_height + (core_height * 0.5))),
        vec(footprint_width * 0.62, footprint_depth * 0.58, core_height),
    )

    roof_scale = 1.22 if config["roof_style"] in ("layered", "pagoda") else 1.12
    spawn_box(
        "{0}_RoofLower".format(BUILDING_NAME),
        add(origin, vec(0.0, 0.0, plinth_height + core_height + (roof_height * 0.5))),
        vec(footprint_width * roof_scale, footprint_depth * roof_scale, roof_height),
    )

    if config["roof_style"] in ("layered", "pagoda", "gate"):
        spawn_box(
            "{0}_RoofUpper".format(BUILDING_NAME),
            add(origin, vec(0.0, 0.0, plinth_height + core_height + (roof_height * 1.15))),
            vec(footprint_width * roof_scale * 0.75, footprint_depth * roof_scale * 0.75, roof_height * 0.7),
        )

    if config["side_wings"]:
        wing_width = footprint_width * 0.22
        wing_depth = footprint_depth * 0.72
        wing_height = core_height * 0.7
        wing_offset = (footprint_width * 0.5) - (wing_width * 0.5) - (60.0 * GAMEPLAY_SCALE)
        for suffix, direction in (("L", -1.0), ("R", 1.0)):
            spawn_box(
                "{0}_Wing_{1}".format(BUILDING_NAME, suffix),
                add(origin, vec(wing_offset * direction, 0.0, plinth_height + (wing_height * 0.5))),
                vec(wing_width, wing_depth, wing_height),
            )

    if config["front_stairs"] and not detail_profile["add_ceremonial_stair"]:
        spawn_stairs(origin, footprint_width * 0.32, 320.0 * GAMEPLAY_SCALE, 120.0 * GAMEPLAY_SCALE, 5)

    if config["corner_towers"]:
        spawn_corner_towers(origin, footprint_width, footprint_depth, core_height)

    if config["courtyard_wall"]:
        spawn_courtyard_walls(origin, footprint_width * 1.35, footprint_depth * 1.35, core_height * 0.4)

    add_detail_pass(origin, config, footprint_width, footprint_depth, plinth_height, core_height, roof_height)
    spawn_scale_ref(add(origin, vec(footprint_width * 0.75, 0.0, 0.0)))
    finalize_generated_building()


def get_spawn_origin(distance):
    if unreal_editor_subsystem:
        camera_info = unreal_editor_subsystem.get_level_viewport_camera_info()
        if camera_info:
            camera_location, camera_rotation = camera_info
            forward = unreal.MathLibrary.get_forward_vector(camera_rotation)
            return add(camera_location, mul(forward, distance))

    unreal.log_warning("{0}: viewport camera unavailable, spawning at world origin".format(BUILDING_NAME))
    return vec(0.0, 0.0, 0.0)


spawn_origin = get_spawn_origin(2600.0)
build_modular_building(spawn_origin)

print("{0} ({1}, {2}) generated at {3}".format(BUILDING_NAME, PRESET_NAME, resolve_detail_mode(), spawn_origin))
