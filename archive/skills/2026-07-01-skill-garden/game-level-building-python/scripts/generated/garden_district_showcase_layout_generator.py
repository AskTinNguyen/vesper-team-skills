import os
import random
import unreal


BUILDING_NAME = "GardenDistrictShowcase"
GAMEPLAY_SCALE = 3.0
RANDOM_SEED = 41
OUTPUT_PREFIX = BUILDING_NAME
OUTPUT_FOLDER = "Generated/{0}".format(BUILDING_NAME)
PALETTE_NAME = "blockout"
PALETTE_APPLICATION_MODE = "replace"
DISTRICT_SPACING_X = 5600.0
DISTRICT_SPACING_Y = 4600.0

SCRIPT_DIR = os.path.dirname(__file__) if "__file__" in globals() else r"E:\S2_\.codex\skills\engineer\graphic-engineer\game-level-building-python\scripts\generated"
COURT_AND_GARDEN_SCRIPT = os.path.join(
    SCRIPT_DIR,
    "court_and_garden_pack_generator.py",
)

DISTRICT_LAYOUT = [
    {
        "preset_name": "formal_pond_court",
        "slot_x": 0,
        "slot_y": 1,
    },
    {
        "preset_name": "tea_ceremony_court",
        "slot_x": -1,
        "slot_y": 0,
    },
    {
        "preset_name": "moon_gate_respite",
        "slot_x": 1,
        "slot_y": 0,
    },
    {
        "preset_name": "scholar_villa_retreat",
        "slot_x": 0,
        "slot_y": -1,
    },
]


def vec(x, y, z):
    return unreal.Vector(float(x), float(y), float(z))


def add(a, b):
    return vec(a.x + b.x, a.y + b.y, a.z + b.z)


def mul(v, s):
    return vec(v.x * s, v.y * s, v.z * s)


if not os.path.exists(COURT_AND_GARDEN_SCRIPT):
    raise RuntimeError("Missing dependency script: {0}".format(COURT_AND_GARDEN_SCRIPT))

shared = {
    "__file__": COURT_AND_GARDEN_SCRIPT,
    "AUTO_RUN": False,
}
exec(open(COURT_AND_GARDEN_SCRIPT, encoding="utf-8").read(), shared)

shared["BUILDING_NAME"] = BUILDING_NAME
shared["OUTPUT_PREFIX"] = OUTPUT_PREFIX
shared["OUTPUT_FOLDER"] = OUTPUT_FOLDER
shared["PALETTE_NAME"] = PALETTE_NAME
shared["PALETTE_APPLICATION_MODE"] = PALETTE_APPLICATION_MODE

editor_actor_subsystem = shared["editor_actor_subsystem"]


def build_garden_district(origin):
    random.seed(RANDOM_SEED)
    shared["generated_actors"][:] = []
    shared["destroy_previous"](OUTPUT_PREFIX)

    spacing_x = DISTRICT_SPACING_X * GAMEPLAY_SCALE
    spacing_y = DISTRICT_SPACING_Y * GAMEPLAY_SCALE

    for item in DISTRICT_LAYOUT:
        offset = vec(item["slot_x"] * spacing_x, item["slot_y"] * spacing_y, 0.0)
        label_prefix = "{0}_{1}".format(OUTPUT_PREFIX, item["preset_name"])
        shared["build_layout"](label_prefix, add(origin, offset), item["preset_name"])

    shared["spawn_path"](
        "{0}_NorthSouthSpine".format(OUTPUT_PREFIX),
        add(origin, vec(0.0, 0.0, 0.0)),
        vec(320.0 * GAMEPLAY_SCALE, (spacing_y * 2.15), 20.0 * GAMEPLAY_SCALE),
    )
    shared["spawn_path"](
        "{0}_EastWestSpine".format(OUTPUT_PREFIX),
        add(origin, vec(0.0, -(spacing_y * 0.12), 0.0)),
        vec(spacing_x * 2.2, 280.0 * GAMEPLAY_SCALE, 20.0 * GAMEPLAY_SCALE),
    )
    shared["spawn_screen_wall"](
        "{0}_EntryMarker".format(OUTPUT_PREFIX),
        add(origin, vec(0.0, -(spacing_y * 1.45), 0.0)),
        700.0 * GAMEPLAY_SCALE,
    )

    for suffix, direction in (("West", -1.0), ("East", 1.0)):
        shared["spawn_moon_gate"](
            "{0}_{1}Connector".format(OUTPUT_PREFIX, suffix),
            add(origin, vec(direction * (spacing_x * 0.5), -(spacing_y * 0.08), 0.0)),
        )

    for index, x_pos in enumerate((-spacing_x * 0.72, 0.0, spacing_x * 0.72)):
        shared["spawn_rockery"](
            "{0}_PromenadeRockery_{1}".format(OUTPUT_PREFIX, index + 1),
            add(origin, vec(x_pos, spacing_y * 0.42, 0.0)),
        )

    shared["spawn_scale_ref"](
        "{0}_ScaleRef".format(OUTPUT_PREFIX),
        add(origin, vec(spacing_x * 1.35, 0.0, 0.0)),
    )
    shared["finalize_generated_layout"]("{0}_Group".format(BUILDING_NAME))


spawn_origin = shared["get_spawn_origin"](5200.0)
build_garden_district(spawn_origin)

print("{0} generated at {1}".format(BUILDING_NAME, spawn_origin))
