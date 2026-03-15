import unreal


BUILDING_NAME = "SecondaryHall"
GAMEPLAY_SCALE = 3.0
LEVEL_COUNT = 3

BASE_WIDTH = 1100.0 * GAMEPLAY_SCALE
BASE_DEPTH = 1000.0 * GAMEPLAY_SCALE
PLINTH_HEIGHT = 120.0 * GAMEPLAY_SCALE
LEVEL_HEIGHT = 360.0 * GAMEPLAY_SCALE
ROOF_THICKNESS = 65.0 * GAMEPLAY_SCALE
ROOF_OVERHANG = 130.0 * GAMEPLAY_SCALE
LEVEL_SHRINK = 0.84

TURRET_WIDTH = 180.0 * GAMEPLAY_SCALE
TURRET_HEIGHT = 260.0 * GAMEPLAY_SCALE
SPIRE_HEIGHT = 180.0 * GAMEPLAY_SCALE

STAIR_WIDTH = 420.0 * GAMEPLAY_SCALE
STAIR_DEPTH = 280.0 * GAMEPLAY_SCALE
STAIR_HEIGHT = 105.0 * GAMEPLAY_SCALE
STAIR_STEPS = 5

FOLDER = "Generated/{0}".format(BUILDING_NAME)
CUBE_PATH = "/Engine/BasicShapes/Cube.Cube"
SCALE_REF_PATH = "/Game/S2/Core_Env/Prototype/S_Placeholder_Char.S_Placeholder_Char"


editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
unreal_editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
cube_mesh = unreal.EditorAssetLibrary.load_asset(CUBE_PATH)
scale_ref_mesh = unreal.EditorAssetLibrary.load_asset(SCALE_REF_PATH)
actor_grouping_utils_class = getattr(unreal, "ActorGroupingUtils", None)
generated_actors = []


def vec(x, y, z):
    return unreal.Vector(float(x), float(y), float(z))


def add(a, b):
    return vec(a.x + b.x, a.y + b.y, a.z + b.z)


def mul(v, s):
    return vec(v.x * s, v.y * s, v.z * s)


def set_folder(actor):
    try:
        actor.set_folder_path(FOLDER)
    except Exception:
        pass


def register_actor(actor):
    if actor:
        generated_actors.append(actor)
    return actor


def destroy_previous():
    for actor in editor_actor_subsystem.get_all_level_actors():
        try:
            if actor.get_actor_label().startswith(BUILDING_NAME):
                editor_actor_subsystem.destroy_actor(actor)
        except Exception:
            pass


def spawn_box(label, center, size_cm):
    actor = editor_actor_subsystem.spawn_actor_from_class(unreal.StaticMeshActor, center, unreal.Rotator(0.0, 0.0, 0.0))
    actor.set_actor_label(label)
    set_folder(actor)
    smc = actor.get_editor_property("static_mesh_component")
    smc.set_static_mesh(cube_mesh)
    actor.set_actor_scale3d(vec(size_cm.x / 100.0, size_cm.y / 100.0, size_cm.z / 100.0))
    return register_actor(actor)


def spawn_scale_ref(location):
    if not scale_ref_mesh:
        return
    actor = editor_actor_subsystem.spawn_actor_from_class(unreal.StaticMeshActor, location, unreal.Rotator(0.0, 0.0, 0.0))
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


def spawn_stairs(origin, front_y):
    run = STAIR_DEPTH / STAIR_STEPS
    rise = STAIR_HEIGHT / STAIR_STEPS
    for index in range(STAIR_STEPS):
        depth = STAIR_DEPTH - (index * run)
        center = vec(origin.x, front_y - (depth * 0.5), origin.z + (index * rise * 0.5))
        spawn_box("{0}_Stair_{1}".format(BUILDING_NAME, index + 1), center, vec(STAIR_WIDTH, depth, rise))


def build_secondary_hall(origin):
    generated_actors[:] = []
    destroy_previous()

    current_width = BASE_WIDTH
    current_depth = BASE_DEPTH
    z_cursor = origin.z

    spawn_box("{0}_Plinth".format(BUILDING_NAME), add(origin, vec(0.0, 0.0, PLINTH_HEIGHT * 0.5)), vec(BASE_WIDTH * 1.08, BASE_DEPTH * 1.08, PLINTH_HEIGHT))
    z_cursor += PLINTH_HEIGHT

    for level in range(LEVEL_COUNT):
        floor_z = z_cursor + (ROOF_THICKNESS * 0.5)
        wall_z = z_cursor + ROOF_THICKNESS + (LEVEL_HEIGHT * 0.5)
        roof_z = z_cursor + ROOF_THICKNESS + LEVEL_HEIGHT + (ROOF_THICKNESS * 0.5)

        spawn_box("{0}_L{1}_Floor".format(BUILDING_NAME, level + 1), add(origin, vec(0.0, 0.0, floor_z)), vec(current_width, current_depth, ROOF_THICKNESS))
        spawn_box("{0}_L{1}_Core".format(BUILDING_NAME, level + 1), add(origin, vec(0.0, 0.0, wall_z)), vec(current_width * 0.72, current_depth * 0.72, LEVEL_HEIGHT))
        spawn_box("{0}_L{1}_RoofLower".format(BUILDING_NAME, level + 1), add(origin, vec(0.0, 0.0, roof_z)), vec(current_width + (ROOF_OVERHANG * 2.0), current_depth + (ROOF_OVERHANG * 2.0), ROOF_THICKNESS))
        spawn_box("{0}_L{1}_RoofUpper".format(BUILDING_NAME, level + 1), add(origin, vec(0.0, 0.0, roof_z + (ROOF_THICKNESS * 0.65))), vec((current_width + (ROOF_OVERHANG * 2.0)) * 0.78, (current_depth + (ROOF_OVERHANG * 2.0)) * 0.78, ROOF_THICKNESS * 0.7))

        turret_offset = (current_width * 0.34)
        turret_z = z_cursor + ROOF_THICKNESS + (TURRET_HEIGHT * 0.5)
        for side, x_pos in (("L", -turret_offset), ("R", turret_offset)):
            spawn_box("{0}_L{1}_Turret_{2}".format(BUILDING_NAME, level + 1, side), add(origin, vec(x_pos, 0.0, turret_z)), vec(TURRET_WIDTH, TURRET_WIDTH, TURRET_HEIGHT))

        z_cursor = roof_z + (ROOF_THICKNESS * 1.4)
        current_width *= LEVEL_SHRINK
        current_depth *= LEVEL_SHRINK

    spawn_box("{0}_Spire".format(BUILDING_NAME), add(origin, vec(0.0, 0.0, z_cursor + (SPIRE_HEIGHT * 0.5))), vec(TURRET_WIDTH * 0.7, TURRET_WIDTH * 0.7, SPIRE_HEIGHT))
    spawn_stairs(origin, origin.y - (BASE_DEPTH * 0.55))
    spawn_scale_ref(add(origin, vec(BASE_WIDTH * 0.72, 0.0, 0.0)))
    finalize_generated_building()


camera_info = unreal_editor_subsystem.get_level_viewport_camera_info() if unreal_editor_subsystem else None
if camera_info:
    camera_location, camera_rotation = camera_info
    forward = unreal.MathLibrary.get_forward_vector(camera_rotation)
    spawn_origin = add(camera_location, mul(forward, 2600.0))
else:
    unreal.log_warning("{0}: viewport camera unavailable, spawning at world origin".format(BUILDING_NAME))
    spawn_origin = vec(0.0, 0.0, 0.0)

build_secondary_hall(spawn_origin)

print("{0} generated at {1}".format(BUILDING_NAME, spawn_origin))
