import unreal


BUILDING_NAME = "GuestHall"
GAMEPLAY_SCALE = 3.0

PLINTH_WIDTH = 1700.0 * GAMEPLAY_SCALE
PLINTH_DEPTH = 1050.0 * GAMEPLAY_SCALE
PLINTH_HEIGHT = 110.0 * GAMEPLAY_SCALE
MAIN_HEIGHT = 520.0 * GAMEPLAY_SCALE
WING_WIDTH = 420.0 * GAMEPLAY_SCALE
WING_DEPTH = 780.0 * GAMEPLAY_SCALE
WING_HEIGHT = 340.0 * GAMEPLAY_SCALE
VERANDA_DEPTH = 180.0 * GAMEPLAY_SCALE
COLUMN_SIZE = 42.0 * GAMEPLAY_SCALE

ROOF_THICKNESS = 70.0 * GAMEPLAY_SCALE
ROOF_OVERHANG = 150.0 * GAMEPLAY_SCALE
STAIR_WIDTH = 560.0 * GAMEPLAY_SCALE
STAIR_DEPTH = 280.0 * GAMEPLAY_SCALE
STAIR_HEIGHT = 110.0 * GAMEPLAY_SCALE
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


def spawn_columns(origin, base_z):
    x_positions = (-PLINTH_WIDTH * 0.28, -PLINTH_WIDTH * 0.09, PLINTH_WIDTH * 0.09, PLINTH_WIDTH * 0.28)
    front_y = -(PLINTH_DEPTH * 0.34)
    for index, x_pos in enumerate(x_positions):
        spawn_box(
            "{0}_Column_{1}".format(BUILDING_NAME, index + 1),
            add(origin, vec(x_pos, front_y, base_z + (MAIN_HEIGHT * 0.5))),
            vec(COLUMN_SIZE, COLUMN_SIZE, MAIN_HEIGHT),
        )


def build_guest_hall(origin):
    generated_actors[:] = []
    destroy_previous()

    spawn_box("{0}_Plinth".format(BUILDING_NAME), add(origin, vec(0.0, 0.0, PLINTH_HEIGHT * 0.5)), vec(PLINTH_WIDTH, PLINTH_DEPTH, PLINTH_HEIGHT))

    veranda_y = -(PLINTH_DEPTH * 0.36)
    spawn_box(
        "{0}_Veranda".format(BUILDING_NAME),
        add(origin, vec(0.0, veranda_y, PLINTH_HEIGHT + (ROOF_THICKNESS * 0.5))),
        vec(PLINTH_WIDTH * 0.88, VERANDA_DEPTH, ROOF_THICKNESS),
    )

    spawn_box(
        "{0}_MainCore".format(BUILDING_NAME),
        add(origin, vec(0.0, 60.0 * GAMEPLAY_SCALE, PLINTH_HEIGHT + (MAIN_HEIGHT * 0.5))),
        vec(PLINTH_WIDTH * 0.62, PLINTH_DEPTH * 0.58, MAIN_HEIGHT),
    )

    wing_offset = (PLINTH_WIDTH * 0.5) - (WING_WIDTH * 0.5) - (90.0 * GAMEPLAY_SCALE)
    for side, x_pos in (("L", -wing_offset), ("R", wing_offset)):
        spawn_box(
            "{0}_Wing_{1}".format(BUILDING_NAME, side),
            add(origin, vec(x_pos, 20.0 * GAMEPLAY_SCALE, PLINTH_HEIGHT + (WING_HEIGHT * 0.5))),
            vec(WING_WIDTH, WING_DEPTH, WING_HEIGHT),
        )

    main_roof_width = (PLINTH_WIDTH * 0.62) + (ROOF_OVERHANG * 2.0)
    main_roof_depth = (PLINTH_DEPTH * 0.58) + (ROOF_OVERHANG * 2.0)
    roof_z = PLINTH_HEIGHT + MAIN_HEIGHT + (ROOF_THICKNESS * 0.5)
    spawn_box("{0}_RoofLower".format(BUILDING_NAME), add(origin, vec(0.0, 60.0 * GAMEPLAY_SCALE, roof_z)), vec(main_roof_width, main_roof_depth, ROOF_THICKNESS))
    spawn_box("{0}_RoofUpper".format(BUILDING_NAME), add(origin, vec(0.0, 60.0 * GAMEPLAY_SCALE, roof_z + (ROOF_THICKNESS * 0.7))), vec(main_roof_width * 0.78, main_roof_depth * 0.76, ROOF_THICKNESS * 0.8))

    wing_roof_width = WING_WIDTH + (ROOF_OVERHANG * 1.5)
    wing_roof_depth = WING_DEPTH + (ROOF_OVERHANG * 1.5)
    wing_roof_z = PLINTH_HEIGHT + WING_HEIGHT + (ROOF_THICKNESS * 0.5)
    for side, x_pos in (("L", -wing_offset), ("R", wing_offset)):
        spawn_box("{0}_WingRoof_{1}".format(BUILDING_NAME, side), add(origin, vec(x_pos, 20.0 * GAMEPLAY_SCALE, wing_roof_z)), vec(wing_roof_width, wing_roof_depth, ROOF_THICKNESS))

    spawn_columns(origin, PLINTH_HEIGHT)
    spawn_stairs(origin, origin.y - (PLINTH_DEPTH * 0.56))
    spawn_scale_ref(add(origin, vec(PLINTH_WIDTH * 0.78, 0.0, 0.0)))
    finalize_generated_building()


camera_info = unreal_editor_subsystem.get_level_viewport_camera_info() if unreal_editor_subsystem else None
if camera_info:
    camera_location, camera_rotation = camera_info
    forward = unreal.MathLibrary.get_forward_vector(camera_rotation)
    spawn_origin = add(camera_location, mul(forward, 2600.0))
else:
    unreal.log_warning("{0}: viewport camera unavailable, spawning at world origin".format(BUILDING_NAME))
    spawn_origin = vec(0.0, 0.0, 0.0)

build_guest_hall(spawn_origin)

print("{0} generated at {1}".format(BUILDING_NAME, spawn_origin))
