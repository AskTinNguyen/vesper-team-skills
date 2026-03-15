import unreal


BUILDING_NAME = "MainGate"
GAMEPLAY_SCALE = 3.0

PLINTH_WIDTH = 1800.0 * GAMEPLAY_SCALE
PLINTH_DEPTH = 900.0 * GAMEPLAY_SCALE
PLINTH_HEIGHT = 110.0 * GAMEPLAY_SCALE

TOWER_WIDTH = 420.0 * GAMEPLAY_SCALE
TOWER_DEPTH = 420.0 * GAMEPLAY_SCALE
TOWER_HEIGHT = 700.0 * GAMEPLAY_SCALE
GATE_OPENING_WIDTH = 520.0 * GAMEPLAY_SCALE
GATE_OPENING_HEIGHT = 430.0 * GAMEPLAY_SCALE

ROOF_THICKNESS = 65.0 * GAMEPLAY_SCALE
ROOF_OVERHANG = 110.0 * GAMEPLAY_SCALE
BRIDGE_DEPTH = 260.0 * GAMEPLAY_SCALE

STAIR_WIDTH = 520.0 * GAMEPLAY_SCALE
STAIR_DEPTH = 300.0 * GAMEPLAY_SCALE
STAIR_HEIGHT = 120.0 * GAMEPLAY_SCALE
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
    actor = editor_actor_subsystem.spawn_actor_from_class(
        unreal.StaticMeshActor,
        center,
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    actor.set_actor_label(label)
    set_folder(actor)

    smc = actor.get_editor_property("static_mesh_component")
    smc.set_static_mesh(cube_mesh)
    actor.set_actor_scale3d(vec(size_cm.x / 100.0, size_cm.y / 100.0, size_cm.z / 100.0))
    return register_actor(actor)


def spawn_scale_ref(location):
    if not scale_ref_mesh:
        return

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


def spawn_stairs(origin, front_y):
    run = STAIR_DEPTH / STAIR_STEPS
    rise = STAIR_HEIGHT / STAIR_STEPS
    for index in range(STAIR_STEPS):
        depth = STAIR_DEPTH - (index * run)
        center = vec(origin.x, front_y - (depth * 0.5), origin.z + (index * rise * 0.5))
        spawn_box(
            "{0}_Stair_{1}".format(BUILDING_NAME, index + 1),
            center,
            vec(STAIR_WIDTH, depth, rise),
        )


def spawn_tower(origin, x_offset, name_suffix):
    base_center = add(origin, vec(x_offset, 0.0, PLINTH_HEIGHT + (TOWER_HEIGHT * 0.5)))
    spawn_box(
        "{0}_{1}_Base".format(BUILDING_NAME, name_suffix),
        base_center,
        vec(TOWER_WIDTH, TOWER_DEPTH, TOWER_HEIGHT),
    )

    roof_width = TOWER_WIDTH + (ROOF_OVERHANG * 2.0)
    roof_depth = TOWER_DEPTH + (ROOF_OVERHANG * 2.0)
    roof_z = PLINTH_HEIGHT + TOWER_HEIGHT + (ROOF_THICKNESS * 0.5)

    spawn_box(
        "{0}_{1}_RoofLower".format(BUILDING_NAME, name_suffix),
        add(origin, vec(x_offset, 0.0, roof_z)),
        vec(roof_width, roof_depth, ROOF_THICKNESS),
    )
    spawn_box(
        "{0}_{1}_RoofUpper".format(BUILDING_NAME, name_suffix),
        add(origin, vec(x_offset, 0.0, roof_z + (ROOF_THICKNESS * 0.65))),
        vec(roof_width * 0.72, roof_depth * 0.72, ROOF_THICKNESS * 0.7),
    )


def build_gate(origin):
    generated_actors[:] = []
    destroy_previous()

    spawn_box(
        "{0}_Plinth".format(BUILDING_NAME),
        add(origin, vec(0.0, 0.0, PLINTH_HEIGHT * 0.5)),
        vec(PLINTH_WIDTH, PLINTH_DEPTH, PLINTH_HEIGHT),
    )

    tower_offset_x = (GATE_OPENING_WIDTH * 0.5) + (TOWER_WIDTH * 0.5) + (120.0 * GAMEPLAY_SCALE)
    spawn_tower(origin, -tower_offset_x, "TowerL")
    spawn_tower(origin, tower_offset_x, "TowerR")

    bridge_width = (tower_offset_x * 2.0) + TOWER_WIDTH
    bridge_center = add(origin, vec(0.0, 0.0, PLINTH_HEIGHT + GATE_OPENING_HEIGHT + (BRIDGE_DEPTH * 0.2)))
    spawn_box(
        "{0}_Bridge".format(BUILDING_NAME),
        bridge_center,
        vec(bridge_width, TOWER_DEPTH * 0.82, BRIDGE_DEPTH),
    )

    center_roof_width = bridge_width + (ROOF_OVERHANG * 1.4)
    center_roof_depth = TOWER_DEPTH + (ROOF_OVERHANG * 2.0)
    center_roof_z = PLINTH_HEIGHT + GATE_OPENING_HEIGHT + BRIDGE_DEPTH + (ROOF_THICKNESS * 0.5)

    spawn_box(
        "{0}_CenterRoofLower".format(BUILDING_NAME),
        add(origin, vec(0.0, 0.0, center_roof_z)),
        vec(center_roof_width, center_roof_depth, ROOF_THICKNESS),
    )
    spawn_box(
        "{0}_CenterRoofUpper".format(BUILDING_NAME),
        add(origin, vec(0.0, 0.0, center_roof_z + (ROOF_THICKNESS * 0.65))),
        vec(center_roof_width * 0.78, center_roof_depth * 0.74, ROOF_THICKNESS * 0.7),
    )

    wall_segment_width = 260.0 * GAMEPLAY_SCALE
    wall_height = 280.0 * GAMEPLAY_SCALE
    wall_offset_x = tower_offset_x + (TOWER_WIDTH * 0.5) + (wall_segment_width * 0.5)
    for side, offset in (("L", -wall_offset_x), ("R", wall_offset_x)):
        spawn_box(
            "{0}_Wall_{1}".format(BUILDING_NAME, side),
            add(origin, vec(offset, 0.0, PLINTH_HEIGHT + (wall_height * 0.5))),
            vec(wall_segment_width, TOWER_DEPTH * 0.65, wall_height),
        )

    front_y = origin.y - (PLINTH_DEPTH * 0.56)
    spawn_stairs(origin, front_y)
    spawn_scale_ref(add(origin, vec(PLINTH_WIDTH * 0.72, 0.0, 0.0)))
    finalize_generated_building()


camera_info = unreal_editor_subsystem.get_level_viewport_camera_info() if unreal_editor_subsystem else None
if camera_info:
    camera_location, camera_rotation = camera_info
    forward = unreal.MathLibrary.get_forward_vector(camera_rotation)
    spawn_origin = add(camera_location, mul(forward, 2600.0))
else:
    unreal.log_warning("{0}: viewport camera unavailable, spawning at world origin".format(BUILDING_NAME))
    spawn_origin = vec(0.0, 0.0, 0.0)

build_gate(spawn_origin)

print("{0} generated at {1}".format(BUILDING_NAME, spawn_origin))
