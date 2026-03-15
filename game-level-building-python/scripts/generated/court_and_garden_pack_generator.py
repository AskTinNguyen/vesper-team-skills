import json
import os
import random
import unreal


BUILDING_NAME = "CourtAndGardenPack"
PRESET_NAME = "formal_pond_court"
GAMEPLAY_SCALE = 3.0
RANDOM_SEED = 19
OUTPUT_PREFIX = BUILDING_NAME
OUTPUT_FOLDER = "Generated/{0}".format(BUILDING_NAME)
AUTO_RUN = globals().get("AUTO_RUN", True)
PALETTE_NAME = "blockout"
PALETTE_APPLICATION_MODE = "replace"
GENERATE_SHOWCASE_LAYOUT = False
SHOWCASE_PRESETS = [
    "formal_pond_court",
    "scholar_villa_retreat",
    "moon_gate_respite",
    "tea_ceremony_court",
]

PRESETS = {
    "formal_pond_court": {
        "layout_type": "formal_pond_court",
        "compound_width": 4200.0,
        "compound_depth": 3400.0,
        "wall_height": 160.0,
        "court_path_width": 320.0,
        "cross_path_width": 260.0,
        "main_hall_width": 1100.0,
        "main_hall_depth": 820.0,
        "main_hall_height": 420.0,
        "side_pavilion_width": 760.0,
        "side_pavilion_depth": 760.0,
        "side_pavilion_height": 300.0,
        "pond_width": 1480.0,
        "pond_depth": 960.0,
        "tree_count": 8,
        "tree_ring_ratio": 0.72,
        "bridge_enabled": True,
        "moon_gate_enabled": False,
        "screen_wall_enabled": True,
        "rockery_enabled": True,
    },
    "scholar_villa_retreat": {
        "layout_type": "scholar_villa_retreat",
        "compound_width": 5200.0,
        "compound_depth": 4600.0,
        "wall_height": 165.0,
        "court_path_width": 300.0,
        "cross_path_width": 220.0,
        "main_hall_width": 1850.0,
        "main_hall_depth": 1280.0,
        "main_hall_height": 520.0,
        "side_pavilion_width": 860.0,
        "side_pavilion_depth": 820.0,
        "side_pavilion_height": 320.0,
        "pond_width": 1540.0,
        "pond_depth": 980.0,
        "tree_count": 10,
        "tree_ring_ratio": 0.8,
        "bridge_enabled": True,
        "moon_gate_enabled": True,
        "screen_wall_enabled": True,
        "rockery_enabled": True,
    },
    "moon_gate_respite": {
        "layout_type": "moon_gate_respite",
        "compound_width": 3600.0,
        "compound_depth": 3200.0,
        "wall_height": 150.0,
        "court_path_width": 260.0,
        "cross_path_width": 220.0,
        "main_hall_width": 920.0,
        "main_hall_depth": 760.0,
        "main_hall_height": 340.0,
        "side_pavilion_width": 660.0,
        "side_pavilion_depth": 620.0,
        "side_pavilion_height": 240.0,
        "pond_width": 860.0,
        "pond_depth": 640.0,
        "tree_count": 6,
        "tree_ring_ratio": 0.66,
        "bridge_enabled": False,
        "moon_gate_enabled": True,
        "screen_wall_enabled": False,
        "rockery_enabled": True,
    },
    "tea_ceremony_court": {
        "layout_type": "tea_ceremony_court",
        "compound_width": 3400.0,
        "compound_depth": 3000.0,
        "wall_height": 145.0,
        "court_path_width": 220.0,
        "cross_path_width": 180.0,
        "main_hall_width": 840.0,
        "main_hall_depth": 620.0,
        "main_hall_height": 280.0,
        "side_pavilion_width": 520.0,
        "side_pavilion_depth": 520.0,
        "side_pavilion_height": 210.0,
        "pond_width": 720.0,
        "pond_depth": 520.0,
        "tree_count": 6,
        "tree_ring_ratio": 0.62,
        "bridge_enabled": False,
        "moon_gate_enabled": True,
        "screen_wall_enabled": True,
        "rockery_enabled": True,
    },
}

CUBE_PATH = "/Engine/BasicShapes/Cube.Cube"
SCALE_REF_PATH = "/Game/S2/Core_Env/Prototype/S_Placeholder_Char.S_Placeholder_Char"
SCRIPT_DIR = os.path.dirname(__file__) if "__file__" in globals() else r"E:\S2_\.codex\skills\engineer\graphic-engineer\game-level-building-python\scripts\generated"
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
REPO_SCAN_MANIFEST_PATH = os.path.join(SKILL_DIR, "references", "project-art-asset-inventory.json")
ASSET_PALETTES = {
    "blockout": {},
    "prototype_garden": {
        "wall": [
            {"path": "/Game/S2/Core_Env/Prototype/BP_proto_env_L_Wall_01.BP_proto_env_L_Wall_01", "fit_to_bounds": True},
        ],
        "screen_wall": [
            {"path": "/Game/S2/Core_Env/Prototype/BP_proto_env_L_Decor-Wall_01_ScreenPanel.BP_proto_env_L_Decor-Wall_01_ScreenPanel", "fit_to_bounds": True},
        ],
        "pond": [
            {"path": "/Game/S2/Core_Env/Prototype/BP_proto_env_L_Pond_01_Actor.BP_proto_env_L_Pond_01_Actor", "fit_to_bounds": True},
        ],
        "main_hall": [
            {"path": "/Game/S2/Core_Env/Prototype/BP_proto_env_L_Pavilion_15_Actor.BP_proto_env_L_Pavilion_15_Actor", "fit_to_bounds": True},
            {"path": "/Game/S2/Core_Env/Prototype/BP_proto_env_L_Pavilion_14_Actor.BP_proto_env_L_Pavilion_14_Actor", "fit_to_bounds": True},
        ],
        "villa": [
            {"path": "/Game/S2/Core_Env/Prototype/BP_proto_env_L_Pavilion_16_Hill_Actor.BP_proto_env_L_Pavilion_16_Hill_Actor", "fit_to_bounds": True},
            {"path": "/Game/S2/Core_Env/Prototype/BP_proto_env_L_Pavilion_17_Island_Actor.BP_proto_env_L_Pavilion_17_Island_Actor", "fit_to_bounds": True},
        ],
        "pavilion": [
            {"path": "/Game/S2/Core_Env/Prototype/BP_proto_env_L_Pavilion_03_Garden_Actor.BP_proto_env_L_Pavilion_03_Garden_Actor", "fit_to_bounds": True},
            {"path": "/Game/S2/Core_Env/Prototype/BP_proto_env_L_Pavilion_02_Tea_Actor.BP_proto_env_L_Pavilion_02_Tea_Actor", "fit_to_bounds": True},
            {"path": "/Game/S2/Core_Env/Prototype/BP_proto_env_L_Pavilion_07_Actor.BP_proto_env_L_Pavilion_07_Actor", "fit_to_bounds": True},
        ],
        "moon_gate": [
            {"path": "/Game/S2/Core_Env/Prototype/BP_proto_env_L_Gate_03_Actor.BP_proto_env_L_Gate_03_Actor", "fit_to_bounds": True},
            {"path": "/Game/S2/Core_Env/Prototype/BP_proto_env_L_Gate_04_Actor.BP_proto_env_L_Gate_04_Actor", "fit_to_bounds": True},
        ],
        "rockery": [
            {"path": "/Game/S2/Core_Env/Prototype/BP_proto_env_M_Rock_01.BP_proto_env_M_Rock_01", "fit_to_bounds": True},
            {"path": "/Game/S2/Core_Env/Prototype/BP_proto_env_M_Rock_02.BP_proto_env_M_Rock_02", "fit_to_bounds": True},
            {"path": "/Game/S2/Core_Env/Prototype/BP_proto_env_M_Rock_03.BP_proto_env_M_Rock_03", "fit_to_bounds": True},
        ],
        "tree": [
            {"path": "/Game/S2/Core_Env/Prototype/BP_proto_env_L_Tree_01.BP_proto_env_L_Tree_01", "fit_to_bounds": True},
            {"path": "/Game/S2/Core_Env/Prototype/BP_proto_env_L_Tree_02.BP_proto_env_L_Tree_02", "fit_to_bounds": True},
            {"path": "/Game/S2/Core_Env/Prototype/BP_proto_env_L_Tree_03.BP_proto_env_L_Tree_03", "fit_to_bounds": True},
            {"path": "/Game/S2/Core_Env/Prototype/BP_proto_env_L_Tree_04.BP_proto_env_L_Tree_04", "fit_to_bounds": True},
        ],
    },
}


def vec(x, y, z):
    return unreal.Vector(float(x), float(y), float(z))


def add(a, b):
    return vec(a.x + b.x, a.y + b.y, a.z + b.z)


def mul(v, s):
    return vec(v.x * s, v.y * s, v.z * s)


def stable_index(text, count):
    value = 0
    for char in text:
        value = ((value * 33) + ord(char)) & 0xFFFFFFFF
    return value % max(count, 1)


def load_repo_scan_palette():
    if not os.path.exists(REPO_SCAN_MANIFEST_PATH):
        return {}

    try:
        with open(REPO_SCAN_MANIFEST_PATH, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception as exc:
        unreal.log_warning("{0}: failed to read asset inventory manifest ({1})".format(BUILDING_NAME, exc))
        return {}

    recommended_palette = payload.get("recommended_palette", {})
    if not isinstance(recommended_palette, dict):
        return {}
    return recommended_palette


editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
unreal_editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
cube_mesh = unreal.EditorAssetLibrary.load_asset(CUBE_PATH)
scale_ref_mesh = unreal.EditorAssetLibrary.load_asset(SCALE_REF_PATH)
actor_grouping_utils_class = getattr(unreal, "ActorGroupingUtils", None)
generated_actors = []
asset_cache = {}

if not cube_mesh:
    raise RuntimeError("Could not load cube mesh: {0}".format(CUBE_PATH))

repo_scan_palette = load_repo_scan_palette()
if repo_scan_palette:
    ASSET_PALETTES["repo_scan_recommended"] = repo_scan_palette


def get_active_config(preset_name):
    base_config = dict(PRESETS[preset_name])
    for key in list(base_config.keys()):
        value = base_config[key]
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)) and (
            key.endswith("width")
            or key.endswith("depth")
            or key.endswith("height")
        ):
            base_config[key] = value * GAMEPLAY_SCALE
    return base_config


def set_folder(actor):
    try:
        actor.set_folder_path(OUTPUT_FOLDER)
    except Exception:
        pass


def register_actor(actor):
    if actor:
        generated_actors.append(actor)
    return actor


def load_asset_cached(asset_path):
    if asset_path not in asset_cache:
        asset_cache[asset_path] = unreal.EditorAssetLibrary.load_asset(asset_path)
    return asset_cache[asset_path]


def get_palette_entry(module_key, label):
    palette = ASSET_PALETTES.get(PALETTE_NAME, {})
    entries = palette.get(module_key, [])
    if not entries:
        return None
    return entries[stable_index(label, len(entries))]


def get_actor_bounds_size(actor):
    bounds_origin, bounds_extent = actor.get_actor_bounds(False)
    return bounds_origin, vec(bounds_extent.x * 2.0, bounds_extent.y * 2.0, bounds_extent.z * 2.0)


def scale_actor_to_target_size(actor, target_size_cm):
    if not actor:
        return

    _, bounds_size = get_actor_bounds_size(actor)
    current_scale = actor.get_actor_scale3d()
    desired_scale = vec(current_scale.x, current_scale.y, current_scale.z)

    if bounds_size.x > 1.0:
        desired_scale.x *= target_size_cm.x / bounds_size.x
    if bounds_size.y > 1.0:
        desired_scale.y *= target_size_cm.y / bounds_size.y
    if bounds_size.z > 1.0:
        desired_scale.z *= target_size_cm.z / bounds_size.z

    actor.set_actor_scale3d(desired_scale)


def spawn_static_mesh_asset(label, static_mesh, center, target_size_cm, yaw=0.0):
    actor = editor_actor_subsystem.spawn_actor_from_class(
        unreal.StaticMeshActor,
        center,
        unreal.Rotator(0.0, yaw, 0.0),
    )
    actor.set_actor_label(label)
    set_folder(actor)
    smc = actor.get_editor_property("static_mesh_component")
    smc.set_static_mesh(static_mesh)
    smc.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
    register_actor(actor)
    scale_actor_to_target_size(actor, target_size_cm)
    return actor


def spawn_palette_asset(label, module_key, center, target_size_cm, yaw=0.0):
    entry = get_palette_entry(module_key, label)
    if not entry:
        return None

    asset = load_asset_cached(entry["path"])
    if not asset:
        unreal.log_warning("{0}: missing palette asset '{1}' for module '{2}'".format(BUILDING_NAME, entry["path"], module_key))
        return None

    if isinstance(asset, unreal.StaticMesh):
        return spawn_static_mesh_asset(label, asset, center, target_size_cm, yaw)

    spawn_from_object = getattr(editor_actor_subsystem, "spawn_actor_from_object", None)
    if not callable(spawn_from_object):
        unreal.log_warning("{0}: spawn_actor_from_object unavailable, using blockout fallback for '{1}'".format(BUILDING_NAME, module_key))
        return None

    try:
        actor = spawn_from_object(asset, center, unreal.Rotator(0.0, yaw, 0.0))
    except Exception as exc:
        unreal.log_warning("{0}: failed to spawn palette asset '{1}' ({2})".format(BUILDING_NAME, entry["path"], exc))
        return None

    actor.set_actor_label(label)
    set_folder(actor)
    register_actor(actor)
    if entry.get("fit_to_bounds", True):
        scale_actor_to_target_size(actor, target_size_cm)
    return actor


def should_spawn_overlay_blockout():
    return PALETTE_NAME != "blockout" and PALETTE_APPLICATION_MODE == "overlay"


def try_spawn_palette_module(label, module_key, center, target_size_cm, yaw=0.0):
    if PALETTE_NAME == "blockout":
        return None
    return spawn_palette_asset(label, module_key, center, target_size_cm, yaw)


def destroy_previous(prefix):
    for actor in editor_actor_subsystem.get_all_level_actors():
        try:
            if actor.get_actor_label().startswith(prefix):
                editor_actor_subsystem.destroy_actor(actor)
        except Exception:
            pass


def spawn_box(label, center, size_cm, yaw=0.0):
    actor = editor_actor_subsystem.spawn_actor_from_class(
        unreal.StaticMeshActor,
        center,
        unreal.Rotator(0.0, yaw, 0.0),
    )
    actor.set_actor_label(label)
    set_folder(actor)
    smc = actor.get_editor_property("static_mesh_component")
    smc.set_static_mesh(cube_mesh)
    smc.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
    actor.set_actor_scale3d(vec(size_cm.x / 100.0, size_cm.y / 100.0, size_cm.z / 100.0))
    return register_actor(actor)


def spawn_scale_ref(label, location):
    if not scale_ref_mesh:
        unreal.log_warning("{0}: scale reference mesh missing, continuing without it".format(BUILDING_NAME))
        return None

    actor = editor_actor_subsystem.spawn_actor_from_class(
        unreal.StaticMeshActor,
        location,
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    actor.set_actor_label(label)
    set_folder(actor)
    smc = actor.get_editor_property("static_mesh_component")
    smc.set_static_mesh(scale_ref_mesh)
    smc.set_hidden_in_game(True)
    smc.set_cast_shadow(False)
    smc.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    return register_actor(actor)


def finalize_generated_layout(group_label):
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
            group_actor.set_actor_label(group_label)
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


def spawn_wall_ring(label_prefix, origin, width, depth, wall_height, gate_side):
    wall_thickness = 60.0 * GAMEPLAY_SCALE
    gate_span = 520.0 * GAMEPLAY_SCALE
    half_width = width * 0.5
    half_depth = depth * 0.5

    def spawn_wall_segment(label, center, size_cm, yaw=0.0):
        if should_spawn_overlay_blockout():
            spawn_box(label + "_Blockout", center, size_cm, yaw)
        if not try_spawn_palette_module(label, "wall", center, size_cm, yaw):
            spawn_box(label, center, size_cm, yaw)

    if gate_side in ("south", "north"):
        gate_y = -half_depth if gate_side == "south" else half_depth
        left_width = (width - gate_span) * 0.5
        spawn_wall_segment(
            "{0}_Wall_{1}_Left".format(label_prefix, gate_side.title()),
            add(origin, vec(-(gate_span + left_width) * 0.5, gate_y, wall_height * 0.5)),
            vec(left_width, wall_thickness, wall_height),
        )
        spawn_wall_segment(
            "{0}_Wall_{1}_Right".format(label_prefix, gate_side.title()),
            add(origin, vec((gate_span + left_width) * 0.5, gate_y, wall_height * 0.5)),
            vec(left_width, wall_thickness, wall_height),
        )
    else:
        spawn_wall_segment("{0}_Wall_South".format(label_prefix), add(origin, vec(0.0, -half_depth, wall_height * 0.5)), vec(width, wall_thickness, wall_height))

    if gate_side != "north":
        spawn_wall_segment("{0}_Wall_North".format(label_prefix), add(origin, vec(0.0, half_depth, wall_height * 0.5)), vec(width, wall_thickness, wall_height))
    if gate_side != "west":
        spawn_wall_segment("{0}_Wall_West".format(label_prefix), add(origin, vec(-half_width, 0.0, wall_height * 0.5)), vec(wall_thickness, depth, wall_height), yaw=90.0)
    if gate_side != "east":
        spawn_wall_segment("{0}_Wall_East".format(label_prefix), add(origin, vec(half_width, 0.0, wall_height * 0.5)), vec(wall_thickness, depth, wall_height), yaw=90.0)


def spawn_hall(label_prefix, origin, width, depth, height, roof_scale, palette_key=None):
    plinth_height = 90.0 * GAMEPLAY_SCALE
    roof_height = 80.0 * GAMEPLAY_SCALE
    target_size = vec(width * roof_scale, depth * roof_scale, plinth_height + height + (roof_height * 1.5))
    if palette_key:
        if should_spawn_overlay_blockout():
            spawn_box(label_prefix + "_ArtBlockout", add(origin, vec(0.0, 0.0, target_size.z * 0.5)), target_size)
        if try_spawn_palette_module(label_prefix, palette_key, origin, target_size):
            return
    spawn_box(label_prefix + "_Plinth", add(origin, vec(0.0, 0.0, plinth_height * 0.5)), vec(width, depth, plinth_height))
    spawn_box(label_prefix + "_Core", add(origin, vec(0.0, 0.0, plinth_height + (height * 0.5))), vec(width * 0.66, depth * 0.7, height))
    spawn_box(label_prefix + "_RoofLower", add(origin, vec(0.0, 0.0, plinth_height + height + (roof_height * 0.5))), vec(width * roof_scale, depth * roof_scale, roof_height))
    spawn_box(label_prefix + "_RoofUpper", add(origin, vec(0.0, 0.0, plinth_height + height + (roof_height * 1.15))), vec(width * roof_scale * 0.72, depth * roof_scale * 0.72, roof_height * 0.68))


def spawn_path(label_prefix, origin, size_cm):
    spawn_box(label_prefix, add(origin, vec(0.0, 0.0, size_cm.z * 0.5)), size_cm)


def spawn_pond(label_prefix, origin, width, depth, bridge_enabled):
    water_height = 45.0 * GAMEPLAY_SCALE
    target_size = vec(width, depth, 160.0 * GAMEPLAY_SCALE)
    if should_spawn_overlay_blockout():
        spawn_box(label_prefix + "_ArtBlockout", add(origin, vec(0.0, 0.0, target_size.z * 0.5)), target_size)
    if try_spawn_palette_module(label_prefix, "pond", origin, target_size):
        return
    spawn_box(label_prefix + "_Water", add(origin, vec(0.0, 0.0, water_height * 0.5)), vec(width, depth, water_height))
    if bridge_enabled:
        spawn_box(label_prefix + "_Bridge", add(origin, vec(0.0, 0.0, water_height + (24.0 * GAMEPLAY_SCALE))), vec(260.0 * GAMEPLAY_SCALE, depth * 0.88, 22.0 * GAMEPLAY_SCALE))


def spawn_tree_marker(label_prefix, origin, crown_scale):
    trunk_size = vec(40.0 * GAMEPLAY_SCALE, 40.0 * GAMEPLAY_SCALE, 190.0 * GAMEPLAY_SCALE)
    crown_size = vec(150.0 * crown_scale, 150.0 * crown_scale, 170.0 * crown_scale)
    target_size = vec(crown_size.x * 1.2, crown_size.y * 1.2, trunk_size.z + crown_size.z)
    tree_center = add(origin, vec(0.0, 0.0, target_size.z * 0.5))
    if should_spawn_overlay_blockout():
        spawn_box(label_prefix + "_ArtBlockout", tree_center, target_size)
    if try_spawn_palette_module(label_prefix, "tree", tree_center, target_size):
        return
    spawn_box(label_prefix + "_Trunk", add(origin, vec(0.0, 0.0, trunk_size.z * 0.5)), trunk_size)
    spawn_box(label_prefix + "_Crown", add(origin, vec(0.0, 0.0, trunk_size.z + (crown_size.z * 0.5))), crown_size)


def spawn_tree_rows(label_prefix, origin, width, depth, tree_count, ring_ratio):
    trees_per_side = max(2, int((tree_count + 1) / 2))
    x_offset = (width * 0.5) * min(ring_ratio, 0.9)
    y_start = -(depth * 0.32)
    y_step = (depth * 0.64) / max(trees_per_side - 1, 1)
    for index in range(trees_per_side):
        y_pos = y_start + (index * y_step)
        spawn_tree_marker("{0}_Tree_L_{1}".format(label_prefix, index + 1), add(origin, vec(-x_offset, y_pos, 0.0)), GAMEPLAY_SCALE)
        spawn_tree_marker("{0}_Tree_R_{1}".format(label_prefix, index + 1), add(origin, vec(x_offset, y_pos, 0.0)), GAMEPLAY_SCALE)


def spawn_screen_wall(label_prefix, origin, width):
    wall_size = vec(width, 70.0 * GAMEPLAY_SCALE, 180.0 * GAMEPLAY_SCALE)
    wall_center = add(origin, vec(0.0, 0.0, wall_size.z * 0.5))
    if should_spawn_overlay_blockout():
        spawn_box(label_prefix + "_ScreenWall_Blockout", wall_center, wall_size)
    if not try_spawn_palette_module(label_prefix + "_ScreenWall", "screen_wall", wall_center, wall_size):
        spawn_box(label_prefix + "_ScreenWall", wall_center, wall_size)


def spawn_moon_gate(label_prefix, origin):
    pillar_size = vec(60.0 * GAMEPLAY_SCALE, 50.0 * GAMEPLAY_SCALE, 210.0 * GAMEPLAY_SCALE)
    ring_size = vec(220.0 * GAMEPLAY_SCALE, 40.0 * GAMEPLAY_SCALE, 220.0 * GAMEPLAY_SCALE)
    target_size = vec(260.0 * GAMEPLAY_SCALE, 90.0 * GAMEPLAY_SCALE, 240.0 * GAMEPLAY_SCALE)
    gate_center = add(origin, vec(0.0, 0.0, target_size.z * 0.5))
    if should_spawn_overlay_blockout():
        spawn_box(label_prefix + "_Blockout", gate_center, target_size)
    if try_spawn_palette_module(label_prefix, "moon_gate", gate_center, target_size):
        return
    spawn_box(label_prefix + "_FrameLeft", add(origin, vec(-95.0 * GAMEPLAY_SCALE, 0.0, pillar_size.z * 0.5)), pillar_size)
    spawn_box(label_prefix + "_FrameRight", add(origin, vec(95.0 * GAMEPLAY_SCALE, 0.0, pillar_size.z * 0.5)), pillar_size)
    spawn_box(label_prefix + "_RingTop", add(origin, vec(0.0, 0.0, 210.0 * GAMEPLAY_SCALE)), ring_size)


def spawn_rockery(label_prefix, origin):
    base_size = vec(220.0 * GAMEPLAY_SCALE, 160.0 * GAMEPLAY_SCALE, 120.0 * GAMEPLAY_SCALE)
    top_size = vec(140.0 * GAMEPLAY_SCALE, 120.0 * GAMEPLAY_SCALE, 170.0 * GAMEPLAY_SCALE)
    target_size = vec(260.0 * GAMEPLAY_SCALE, 220.0 * GAMEPLAY_SCALE, 260.0 * GAMEPLAY_SCALE)
    rockery_center = add(origin, vec(0.0, 0.0, target_size.z * 0.5))
    if should_spawn_overlay_blockout():
        spawn_box(label_prefix + "_Blockout", rockery_center, target_size)
    if try_spawn_palette_module(label_prefix, "rockery", rockery_center, target_size):
        return
    spawn_box(label_prefix + "_Base", add(origin, vec(0.0, 0.0, base_size.z * 0.5)), base_size, yaw=15.0)
    spawn_box(label_prefix + "_Top", add(origin, vec(40.0 * GAMEPLAY_SCALE, 0.0, base_size.z + (top_size.z * 0.5))), top_size, yaw=-18.0)


def build_formal_pond_court(label_prefix, origin, config):
    spawn_wall_ring(label_prefix, origin, config["compound_width"], config["compound_depth"], config["wall_height"], "south")
    spawn_path(label_prefix + "_MainPath", add(origin, vec(0.0, 120.0 * GAMEPLAY_SCALE, 0.0)), vec(config["court_path_width"], config["compound_depth"] * 0.86, 18.0 * GAMEPLAY_SCALE))
    spawn_path(label_prefix + "_CrossPath", add(origin, vec(0.0, 260.0 * GAMEPLAY_SCALE, 0.0)), vec(config["compound_width"] * 0.72, config["cross_path_width"], 18.0 * GAMEPLAY_SCALE))
    spawn_pond(label_prefix + "_Pond", add(origin, vec(0.0, 80.0 * GAMEPLAY_SCALE, 0.0)), config["pond_width"], config["pond_depth"], config["bridge_enabled"])
    spawn_hall(label_prefix + "_MainHall", add(origin, vec(0.0, (config["compound_depth"] * 0.5) - (760.0 * GAMEPLAY_SCALE), 0.0)), config["main_hall_width"], config["main_hall_depth"], config["main_hall_height"], 1.12, palette_key="main_hall")
    side_offset_x = (config["compound_width"] * 0.5) - (760.0 * GAMEPLAY_SCALE)
    for suffix, direction in (("EastPavilion", 1.0), ("WestPavilion", -1.0)):
        spawn_hall(
            "{0}_{1}".format(label_prefix, suffix),
            add(origin, vec(side_offset_x * direction, 120.0 * GAMEPLAY_SCALE, 0.0)),
            config["side_pavilion_width"],
            config["side_pavilion_depth"],
            config["side_pavilion_height"],
            1.08,
            palette_key="pavilion",
        )
    if config["screen_wall_enabled"]:
        spawn_screen_wall(label_prefix, add(origin, vec(0.0, -(config["compound_depth"] * 0.5) + (360.0 * GAMEPLAY_SCALE), 0.0)), 640.0 * GAMEPLAY_SCALE)
    if config["rockery_enabled"]:
        spawn_rockery(label_prefix + "_Rockery_L", add(origin, vec(-(config["compound_width"] * 0.24), -(config["compound_depth"] * 0.16), 0.0)))
        spawn_rockery(label_prefix + "_Rockery_R", add(origin, vec(config["compound_width"] * 0.24, -(config["compound_depth"] * 0.16), 0.0)))
    spawn_tree_rows(label_prefix, add(origin, vec(0.0, 220.0 * GAMEPLAY_SCALE, 0.0)), config["compound_width"], config["compound_depth"], config["tree_count"], config["tree_ring_ratio"])


def build_scholar_villa_retreat(label_prefix, origin, config):
    spawn_wall_ring(label_prefix, origin, config["compound_width"], config["compound_depth"], config["wall_height"], "south")
    spawn_hall(label_prefix + "_MainVilla", add(origin, vec(0.0, (config["compound_depth"] * 0.5) - (1020.0 * GAMEPLAY_SCALE), 0.0)), config["main_hall_width"], config["main_hall_depth"], config["main_hall_height"], 1.14, palette_key="villa")
    spawn_hall(label_prefix + "_SouthStudy", add(origin, vec(0.0, -(config["compound_depth"] * 0.5) + (820.0 * GAMEPLAY_SCALE), 0.0)), config["side_pavilion_width"] * 1.1, config["side_pavilion_depth"] * 0.92, config["side_pavilion_height"], 1.06, palette_key="pavilion")
    spawn_hall(label_prefix + "_EastPavilion", add(origin, vec((config["compound_width"] * 0.5) - (920.0 * GAMEPLAY_SCALE), -180.0 * GAMEPLAY_SCALE, 0.0)), config["side_pavilion_width"], config["side_pavilion_depth"], config["side_pavilion_height"], 1.08, palette_key="pavilion")
    spawn_hall(label_prefix + "_WestPavilion", add(origin, vec(-(config["compound_width"] * 0.5) + (920.0 * GAMEPLAY_SCALE), -180.0 * GAMEPLAY_SCALE, 0.0)), config["side_pavilion_width"], config["side_pavilion_depth"], config["side_pavilion_height"], 1.08, palette_key="pavilion")
    spawn_path(label_prefix + "_NorthAxisPath", add(origin, vec(0.0, 220.0 * GAMEPLAY_SCALE, 0.0)), vec(config["court_path_width"], config["compound_depth"] * 0.9, 18.0 * GAMEPLAY_SCALE))
    spawn_path(label_prefix + "_GardenWalk", add(origin, vec(0.0, -(config["compound_depth"] * 0.18), 0.0)), vec(config["compound_width"] * 0.7, config["cross_path_width"], 18.0 * GAMEPLAY_SCALE))
    spawn_pond(label_prefix + "_LotusPond", add(origin, vec(0.0, -(config["compound_depth"] * 0.12), 0.0)), config["pond_width"], config["pond_depth"], config["bridge_enabled"])
    if config["screen_wall_enabled"]:
        spawn_screen_wall(label_prefix, add(origin, vec(0.0, -(config["compound_depth"] * 0.5) + (420.0 * GAMEPLAY_SCALE), 0.0)), 720.0 * GAMEPLAY_SCALE)
    if config["moon_gate_enabled"]:
        spawn_moon_gate(label_prefix + "_MoonGate_E", add(origin, vec((config["compound_width"] * 0.5) - (300.0 * GAMEPLAY_SCALE), 520.0 * GAMEPLAY_SCALE, 0.0)))
        spawn_moon_gate(label_prefix + "_MoonGate_W", add(origin, vec(-(config["compound_width"] * 0.5) + (300.0 * GAMEPLAY_SCALE), 520.0 * GAMEPLAY_SCALE, 0.0)))
    if config["rockery_enabled"]:
        spawn_rockery(label_prefix + "_Rockery_E", add(origin, vec((config["compound_width"] * 0.24), 460.0 * GAMEPLAY_SCALE, 0.0)))
        spawn_rockery(label_prefix + "_Rockery_W", add(origin, vec(-(config["compound_width"] * 0.24), 460.0 * GAMEPLAY_SCALE, 0.0)))
    spawn_tree_rows(label_prefix, add(origin, vec(0.0, 260.0 * GAMEPLAY_SCALE, 0.0)), config["compound_width"], config["compound_depth"], config["tree_count"], config["tree_ring_ratio"])


def build_moon_gate_respite(label_prefix, origin, config):
    spawn_wall_ring(label_prefix, origin, config["compound_width"], config["compound_depth"], config["wall_height"], "south")
    spawn_hall(label_prefix + "_NorthPavilion", add(origin, vec(0.0, (config["compound_depth"] * 0.5) - (700.0 * GAMEPLAY_SCALE), 0.0)), config["main_hall_width"], config["main_hall_depth"], config["main_hall_height"], 1.08, palette_key="pavilion")
    spawn_hall(label_prefix + "_TeaPavilion_L", add(origin, vec(-(config["compound_width"] * 0.23), -120.0 * GAMEPLAY_SCALE, 0.0)), config["side_pavilion_width"], config["side_pavilion_depth"], config["side_pavilion_height"], 1.04, palette_key="pavilion")
    spawn_hall(label_prefix + "_TeaPavilion_R", add(origin, vec(config["compound_width"] * 0.23, -120.0 * GAMEPLAY_SCALE, 0.0)), config["side_pavilion_width"], config["side_pavilion_depth"], config["side_pavilion_height"], 1.04, palette_key="pavilion")
    spawn_path(label_prefix + "_NorthPath", add(origin, vec(0.0, 240.0 * GAMEPLAY_SCALE, 0.0)), vec(config["court_path_width"], config["compound_depth"] * 0.84, 18.0 * GAMEPLAY_SCALE))
    spawn_path(label_prefix + "_SouthGardenWalk", add(origin, vec(0.0, -200.0 * GAMEPLAY_SCALE, 0.0)), vec(config["compound_width"] * 0.56, config["cross_path_width"], 18.0 * GAMEPLAY_SCALE))
    spawn_pond(label_prefix + "_CenterPool", add(origin, vec(0.0, -160.0 * GAMEPLAY_SCALE, 0.0)), config["pond_width"], config["pond_depth"], config["bridge_enabled"])
    if config["moon_gate_enabled"]:
        spawn_moon_gate(label_prefix + "_MoonGate", add(origin, vec(0.0, -(config["compound_depth"] * 0.5) + (340.0 * GAMEPLAY_SCALE), 0.0)))
    if config["rockery_enabled"]:
        spawn_rockery(label_prefix + "_Rockery_L", add(origin, vec(-(config["compound_width"] * 0.3), 520.0 * GAMEPLAY_SCALE, 0.0)))
        spawn_rockery(label_prefix + "_Rockery_R", add(origin, vec(config["compound_width"] * 0.3, 520.0 * GAMEPLAY_SCALE, 0.0)))
    spawn_tree_rows(label_prefix, add(origin, vec(0.0, 120.0 * GAMEPLAY_SCALE, 0.0)), config["compound_width"], config["compound_depth"], config["tree_count"], config["tree_ring_ratio"])


def build_tea_ceremony_court(label_prefix, origin, config):
    spawn_wall_ring(label_prefix, origin, config["compound_width"], config["compound_depth"], config["wall_height"], "south")
    spawn_hall(label_prefix + "_TeaHall", add(origin, vec(0.0, (config["compound_depth"] * 0.5) - (660.0 * GAMEPLAY_SCALE), 0.0)), config["main_hall_width"], config["main_hall_depth"], config["main_hall_height"], 1.05, palette_key="pavilion")
    spawn_hall(label_prefix + "_TeaPrepWest", add(origin, vec(-(config["compound_width"] * 0.22), 60.0 * GAMEPLAY_SCALE, 0.0)), config["side_pavilion_width"], config["side_pavilion_depth"], config["side_pavilion_height"], 1.02, palette_key="pavilion")
    spawn_hall(label_prefix + "_TeaPrepEast", add(origin, vec(config["compound_width"] * 0.22, 60.0 * GAMEPLAY_SCALE, 0.0)), config["side_pavilion_width"], config["side_pavilion_depth"], config["side_pavilion_height"], 1.02, palette_key="pavilion")
    spawn_path(label_prefix + "_EntryWalk", add(origin, vec(0.0, -(config["compound_depth"] * 0.08), 0.0)), vec(config["court_path_width"], config["compound_depth"] * 0.82, 18.0 * GAMEPLAY_SCALE))
    spawn_path(label_prefix + "_TeaCourtWalk", add(origin, vec(0.0, 60.0 * GAMEPLAY_SCALE, 0.0)), vec(config["compound_width"] * 0.44, config["cross_path_width"], 18.0 * GAMEPLAY_SCALE))
    spawn_pond(label_prefix + "_ReflectingPool", add(origin, vec(0.0, -(config["compound_depth"] * 0.16), 0.0)), config["pond_width"], config["pond_depth"], config["bridge_enabled"])
    if config["screen_wall_enabled"]:
        spawn_screen_wall(label_prefix, add(origin, vec(0.0, -(config["compound_depth"] * 0.5) + (340.0 * GAMEPLAY_SCALE), 0.0)), 560.0 * GAMEPLAY_SCALE)
    if config["moon_gate_enabled"]:
        spawn_moon_gate(label_prefix + "_MoonGate_West", add(origin, vec(-(config["compound_width"] * 0.5) + (280.0 * GAMEPLAY_SCALE), 340.0 * GAMEPLAY_SCALE, 0.0)))
        spawn_moon_gate(label_prefix + "_MoonGate_East", add(origin, vec((config["compound_width"] * 0.5) - (280.0 * GAMEPLAY_SCALE), 340.0 * GAMEPLAY_SCALE, 0.0)))
    if config["rockery_enabled"]:
        spawn_rockery(label_prefix + "_Rockery_NW", add(origin, vec(-(config["compound_width"] * 0.28), 420.0 * GAMEPLAY_SCALE, 0.0)))
        spawn_rockery(label_prefix + "_Rockery_SE", add(origin, vec(config["compound_width"] * 0.2, -(config["compound_depth"] * 0.18), 0.0)))
    spawn_tree_rows(label_prefix, add(origin, vec(0.0, 80.0 * GAMEPLAY_SCALE, 0.0)), config["compound_width"], config["compound_depth"], config["tree_count"], config["tree_ring_ratio"])


def build_layout(label_prefix, origin, preset_name):
    config = get_active_config(preset_name)
    layout_type = config["layout_type"]
    if layout_type == "formal_pond_court":
        build_formal_pond_court(label_prefix, origin, config)
    elif layout_type == "scholar_villa_retreat":
        build_scholar_villa_retreat(label_prefix, origin, config)
    elif layout_type == "moon_gate_respite":
        build_moon_gate_respite(label_prefix, origin, config)
    elif layout_type == "tea_ceremony_court":
        build_tea_ceremony_court(label_prefix, origin, config)
    else:
        raise RuntimeError("Unsupported layout type: {0}".format(layout_type))

    compound_width = config["compound_width"]
    spawn_scale_ref(label_prefix + "_ScaleRef", add(origin, vec((compound_width * 0.5) + (240.0 * GAMEPLAY_SCALE), 0.0, 0.0)))


def build_selected_layout(origin):
    random.seed(RANDOM_SEED)
    generated_actors[:] = []
    destroy_previous(OUTPUT_PREFIX)

    if GENERATE_SHOWCASE_LAYOUT:
        spacing = 6200.0 * GAMEPLAY_SCALE
        for index, preset_name in enumerate(SHOWCASE_PRESETS):
            offset = vec(float(index) * spacing, 0.0, 0.0)
            build_layout("{0}_{1}".format(OUTPUT_PREFIX, preset_name), add(origin, offset), preset_name)
        group_label = "{0}_Showcase_Group".format(BUILDING_NAME)
    else:
        build_layout("{0}_{1}".format(OUTPUT_PREFIX, PRESET_NAME), origin, PRESET_NAME)
        group_label = "{0}_Group".format(BUILDING_NAME)

    finalize_generated_layout(group_label)


def get_spawn_origin(distance):
    if unreal_editor_subsystem:
        camera_info = unreal_editor_subsystem.get_level_viewport_camera_info()
        if camera_info:
            camera_location, camera_rotation = camera_info
            forward = unreal.MathLibrary.get_forward_vector(camera_rotation)
            return add(camera_location, mul(forward, distance))

    unreal.log_warning("{0}: viewport camera unavailable, spawning at world origin".format(BUILDING_NAME))
    return vec(0.0, 0.0, 0.0)


if AUTO_RUN:
    spawn_origin = get_spawn_origin(3400.0)
    build_selected_layout(spawn_origin)
    print("{0} generated preset '{1}' at {2}".format(BUILDING_NAME, PRESET_NAME, spawn_origin))
