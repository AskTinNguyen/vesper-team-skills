import unreal


BUILDING_NAME = "Warehouse"
GAMEPLAY_SCALE = 3.0

PLINTH_WIDTH = 1450.0 * GAMEPLAY_SCALE
PLINTH_DEPTH = 950.0 * GAMEPLAY_SCALE
PLINTH_HEIGHT = 95.0 * GAMEPLAY_SCALE
BODY_HEIGHT = 360.0 * GAMEPLAY_SCALE
ROOF_THICKNESS = 70.0 * GAMEPLAY_SCALE
ROOF_HEIGHT = 180.0 * GAMEPLAY_SCALE
ROOF_OVERHANG = 110.0 * GAMEPLAY_SCALE
BUTTRESS_WIDTH = 90.0 * GAMEPLAY_SCALE
BUTTRESS_DEPTH = 120.0 * GAMEPLAY_SCALE
BUTTRESS_HEIGHT = 260.0 * GAMEPLAY_SCALE

DOOR_WIDTH = 260.0 * GAMEPLAY_SCALE
DOOR_DEPTH = 70.0 * GAMEPLAY_SCALE
DOOR_HEIGHT = 250.0 * GAMEPLAY_SCALE

STAIR_WIDTH = 340.0 * GAMEPLAY_SCALE
STAIR_DEPTH = 220.0 * GAMEPLAY_SCALE
STAIR_HEIGHT = 90.0 * GAMEPLAY_SCALE
STAIR_STEPS = 4

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


def build_warehouse(origin):
    generated_actors[:] = []
    destroy_previous()

    spawn_box("{0}_Plinth".format(BUILDING_NAME), add(origin, vec(0.0, 0.0, PLINTH_HEIGHT * 0.5)), vec(PLINTH_WIDTH, PLINTH_DEPTH, PLINTH_HEIGHT))
    spawn_box("{0}_Body".format(BUILDING_NAME), add(origin, vec(0.0, 0.0, PLINTH_HEIGHT + (BODY_HEIGHT * 0.5))), vec(PLINTH_WIDTH * 0.84, PLINTH_DEPTH * 0.72, BODY_HEIGHT))

    buttress_x = (PLINTH_WIDTH * 0.5) - (BUTTRESS_WIDTH * 0.5) - (80.0 * GAMEPLAY_SCALE)
    buttress_y = (PLINTH_DEPTH * 0.5) - (BUTTRESS_DEPTH * 0.5) - (80.0 * GAMEPLAY_SCALE)
    points = [(-buttress_x, -buttress_y), (-buttress_x, buttress_y), (buttress_x, -buttress_y), (buttress_x, buttress_y)]
    for index, point in enumerate(points):
        spawn_box(
            "{0}_Buttress_{1}".format(BUILDING_NAME, index + 1),
            add(origin, vec(point[0], point[1], PLINTH_HEIGHT + (BUTTRESS_HEIGHT * 0.5))),
            vec(BUTTRESS_WIDTH, BUTTRESS_DEPTH, BUTTRESS_HEIGHT),
        )

    roof_width = (PLINTH_WIDTH * 0.84) + (ROOF_OVERHANG * 2.0)
    roof_depth = (PLINTH_DEPTH * 0.72) + (ROOF_OVERHANG * 2.0)
    roof_z = PLINTH_HEIGHT + BODY_HEIGHT + (ROOF_THICKNESS * 0.5)
    spawn_box("{0}_RoofBase".format(BUILDING_NAME), add(origin, vec(0.0, 0.0, roof_z)), vec(roof_width, roof_depth, ROOF_THICKNESS))
    spawn_box("{0}_RoofPeak".format(BUILDING_NAME), add(origin, vec(0.0, 0.0, roof_z + (ROOF_HEIGHT * 0.5))), vec(roof_width * 0.52, roof_depth * 0.68, ROOF_HEIGHT))

    front_y = -(PLINTH_DEPTH * 0.36)
    spawn_box("{0}_DoorFrame".format(BUILDING_NAME), add(origin, vec(0.0, front_y, PLINTH_HEIGHT + (DOOR_HEIGHT * 0.5))), vec(DOOR_WIDTH, DOOR_DEPTH, DOOR_HEIGHT))

    side_annex_width = 240.0 * GAMEPLAY_SCALE
    side_annex_depth = 340.0 * GAMEPLAY_SCALE
    side_annex_height = 180.0 * GAMEPLAY_SCALE
    side_offset_x = (PLINTH_WIDTH * 0.5) + (side_annex_width * 0.5) - (50.0 * GAMEPLAY_SCALE)
    for side, x_pos in (("L", -side_offset_x), ("R", side_offset_x)):
        spawn_box(
            "{0}_Annex_{1}".format(BUILDING_NAME, side),
            add(origin, vec(x_pos, 0.0, PLINTH_HEIGHT + (side_annex_height * 0.5))),
            vec(side_annex_width, side_annex_depth, side_annex_height),
        )

    spawn_stairs(origin, origin.y - (PLINTH_DEPTH * 0.56))
    spawn_scale_ref(add(origin, vec(PLINTH_WIDTH * 0.75, 0.0, 0.0)))
    finalize_generated_building()


camera_info = unreal_editor_subsystem.get_level_viewport_camera_info() if unreal_editor_subsystem else None
if camera_info:
    camera_location, camera_rotation = camera_info
    forward = unreal.MathLibrary.get_forward_vector(camera_rotation)
    spawn_origin = add(camera_location, mul(forward, 2600.0))
else:
    unreal.log_warning("{0}: viewport camera unavailable, spawning at world origin".format(BUILDING_NAME))
    spawn_origin = vec(0.0, 0.0, 0.0)

build_warehouse(spawn_origin)

print("{0} generated at {1}".format(BUILDING_NAME, spawn_origin))
