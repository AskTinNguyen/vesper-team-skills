import unreal


# =========================
# CONFIG
# =========================
PAGODA_NAME = "MainKeepPagoda"
GAMEPLAY_SCALE = 3.0
LEVEL_COUNT = 5

BASE_WIDTH = 1800.0 * GAMEPLAY_SCALE
BASE_DEPTH = 1800.0 * GAMEPLAY_SCALE
LEVEL_HEIGHT = 420.0 * GAMEPLAY_SCALE
ROOF_THICKNESS = 70.0 * GAMEPLAY_SCALE
ROOF_OVERHANG = 140.0 * GAMEPLAY_SCALE
PLINTH_HEIGHT = 120.0 * GAMEPLAY_SCALE
COLUMN_SIZE = 45.0 * GAMEPLAY_SCALE
SPIRE_HEIGHT = 220.0 * GAMEPLAY_SCALE

LEVEL_SHRINK = 0.78
CORE_RATIO = 0.68
COLUMN_INSET = 110.0 * GAMEPLAY_SCALE
STAIR_WIDTH = 280.0 * GAMEPLAY_SCALE
STAIR_DEPTH = 420.0 * GAMEPLAY_SCALE
STAIR_HEIGHT = 140.0 * GAMEPLAY_SCALE
STAIR_STEPS = 6

FOLDER = "Generated/{0}".format(PAGODA_NAME)

CUBE_PATH = "/Engine/BasicShapes/Cube.Cube"
SCALE_REF_PATH = "/Game/S2/Core_Env/Prototype/S_Placeholder_Char.S_Placeholder_Char"


editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
unreal_editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
cube_mesh = unreal.EditorAssetLibrary.load_asset(CUBE_PATH)
scale_ref_mesh = unreal.EditorAssetLibrary.load_asset(SCALE_REF_PATH)
actor_grouping_utils_class = getattr(unreal, "ActorGroupingUtils", None)
generated_actors = []

if not cube_mesh:
    raise RuntimeError("Could not load cube mesh: {0}".format(CUBE_PATH))


def vec(x, y, z):
    return unreal.Vector(float(x), float(y), float(z))


def add(a, b):
    return vec(a.x + b.x, a.y + b.y, a.z + b.z)


def mul(v, s):
    return vec(v.x * s, v.y * s, v.z * s)


def set_folder(actor, folder_name):
    try:
        actor.set_folder_path(folder_name)
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


def spawn_box(label, center, size_cm, yaw=0.0):
    actor = editor_actor_subsystem.spawn_actor_from_class(
        unreal.StaticMeshActor,
        center,
        unreal.Rotator(0.0, yaw, 0.0),
    )
    actor.set_actor_label(label)
    set_folder(actor, FOLDER)

    smc = actor.get_editor_property("static_mesh_component")
    smc.set_static_mesh(cube_mesh)
    smc.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
    actor.set_actor_scale3d(vec(size_cm.x / 100.0, size_cm.y / 100.0, size_cm.z / 100.0))
    return register_actor(actor)


def spawn_scale_ref(label, location):
    if not scale_ref_mesh:
        return None

    actor = editor_actor_subsystem.spawn_actor_from_class(
        unreal.StaticMeshActor,
        location,
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    actor.set_actor_label(label)
    set_folder(actor, FOLDER)

    smc = actor.get_editor_property("static_mesh_component")
    smc.set_static_mesh(scale_ref_mesh)
    smc.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
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
            unreal.log_warning("{0}: failed to group generated actors ({1})".format(PAGODA_NAME, exc))

    try:
        editor_actor_subsystem.clear_actor_selection_set()
    except Exception:
        pass

    if group_actor:
        try:
            group_actor.set_actor_label("{0}_Group".format(PAGODA_NAME))
        except Exception:
            pass
        set_folder(group_actor, FOLDER)
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


def spawn_columns(level_index, center, width, depth, base_z, column_height):
    x_pos = (width * 0.5) - COLUMN_INSET
    y_pos = (depth * 0.5) - COLUMN_INSET

    points = [
        vec(-x_pos, -y_pos, 0.0),
        vec(-x_pos, y_pos, 0.0),
        vec(x_pos, -y_pos, 0.0),
        vec(x_pos, y_pos, 0.0),
        vec(0.0, -y_pos, 0.0),
        vec(0.0, y_pos, 0.0),
        vec(-x_pos, 0.0, 0.0),
        vec(x_pos, 0.0, 0.0),
    ]

    for i, point in enumerate(points):
        spawn_box(
            "{0}_L{1}_Column_{2}".format(PAGODA_NAME, level_index + 1, i + 1),
            add(center, vec(point.x, point.y, base_z + column_height * 0.5)),
            vec(COLUMN_SIZE, COLUMN_SIZE, column_height),
        )


def spawn_stairs(center, front_y, ground_z):
    step_run = STAIR_DEPTH / STAIR_STEPS
    step_rise = STAIR_HEIGHT / STAIR_STEPS

    for i in range(STAIR_STEPS):
        step_depth = STAIR_DEPTH - (i * step_run)
        step_center = vec(
            center.x,
            front_y - (step_depth * 0.5),
            ground_z + (i * step_rise * 0.5),
        )
        spawn_box(
            "{0}_Stair_{1}".format(PAGODA_NAME, i + 1),
            step_center,
            vec(STAIR_WIDTH, step_depth, step_rise),
        )


def build_pagoda(origin):
    generated_actors[:] = []
    destroy_previous(PAGODA_NAME)

    current_width = BASE_WIDTH
    current_depth = BASE_DEPTH
    z_cursor = origin.z

    spawn_box(
        "{0}_Plinth".format(PAGODA_NAME),
        vec(origin.x, origin.y, z_cursor + PLINTH_HEIGHT * 0.5),
        vec(BASE_WIDTH * 1.12, BASE_DEPTH * 1.12, PLINTH_HEIGHT),
    )
    z_cursor += PLINTH_HEIGHT

    front_y = origin.y - (BASE_DEPTH * 0.56)
    spawn_stairs(origin, front_y, origin.z)

    for level in range(LEVEL_COUNT):
        floor_center_z = z_cursor + ROOF_THICKNESS * 0.5
        spawn_box(
            "{0}_L{1}_Floor".format(PAGODA_NAME, level + 1),
            vec(origin.x, origin.y, floor_center_z),
            vec(current_width, current_depth, ROOF_THICKNESS),
        )

        core_width = current_width * CORE_RATIO
        core_depth = current_depth * CORE_RATIO
        wall_height = LEVEL_HEIGHT

        core_center_z = z_cursor + ROOF_THICKNESS + wall_height * 0.5
        spawn_box(
            "{0}_L{1}_Core".format(PAGODA_NAME, level + 1),
            vec(origin.x, origin.y, core_center_z),
            vec(core_width, core_depth, wall_height),
        )

        spawn_columns(level, origin, current_width, current_depth, z_cursor + ROOF_THICKNESS, wall_height)

        roof_base_z = z_cursor + ROOF_THICKNESS + wall_height + (ROOF_THICKNESS * 0.5)
        roof_width = current_width + (ROOF_OVERHANG * 2.0)
        roof_depth = current_depth + (ROOF_OVERHANG * 2.0)

        spawn_box(
            "{0}_L{1}_RoofLower".format(PAGODA_NAME, level + 1),
            vec(origin.x, origin.y, roof_base_z),
            vec(roof_width, roof_depth, ROOF_THICKNESS),
        )

        spawn_box(
            "{0}_L{1}_RoofUpper".format(PAGODA_NAME, level + 1),
            vec(origin.x, origin.y, roof_base_z + ROOF_THICKNESS * 0.65),
            vec(roof_width * 0.78, roof_depth * 0.78, ROOF_THICKNESS * 0.7),
        )

        spawn_box(
            "{0}_L{1}_RidgeX".format(PAGODA_NAME, level + 1),
            vec(origin.x, origin.y, roof_base_z + ROOF_THICKNESS * 1.2),
            vec(roof_width * 0.55, ROOF_THICKNESS * 0.35, ROOF_THICKNESS * 0.5),
        )

        spawn_box(
            "{0}_L{1}_RidgeY".format(PAGODA_NAME, level + 1),
            vec(origin.x, origin.y, roof_base_z + ROOF_THICKNESS * 1.2),
            vec(ROOF_THICKNESS * 0.35, roof_depth * 0.55, ROOF_THICKNESS * 0.5),
        )

        z_cursor = roof_base_z + ROOF_THICKNESS * 1.55
        current_width *= LEVEL_SHRINK
        current_depth *= LEVEL_SHRINK

    spawn_box(
        "{0}_SpireBase".format(PAGODA_NAME),
        vec(origin.x, origin.y, z_cursor + SPIRE_HEIGHT * 0.35),
        vec(COLUMN_SIZE * 1.2, COLUMN_SIZE * 1.2, SPIRE_HEIGHT * 0.7),
    )
    spawn_box(
        "{0}_SpireTop".format(PAGODA_NAME),
        vec(origin.x, origin.y, z_cursor + SPIRE_HEIGHT * 0.85),
        vec(COLUMN_SIZE * 0.6, COLUMN_SIZE * 0.6, SPIRE_HEIGHT * 0.3),
    )

    spawn_scale_ref(
        "{0}_ScaleRef".format(PAGODA_NAME),
        vec(origin.x + BASE_WIDTH * 0.75, origin.y, origin.z),
    )
    finalize_generated_building()


camera_info = unreal_editor_subsystem.get_level_viewport_camera_info() if unreal_editor_subsystem else None
if camera_info:
    camera_location, camera_rotation = camera_info
    forward = unreal.MathLibrary.get_forward_vector(camera_rotation)
    spawn_origin = add(camera_location, mul(forward, 3000.0))
else:
    unreal.log_warning("{0}: viewport camera unavailable, spawning at world origin".format(PAGODA_NAME))
    spawn_origin = vec(0.0, 0.0, 0.0)

build_pagoda(spawn_origin)

print("{0} generated at {1}".format(PAGODA_NAME, spawn_origin))
