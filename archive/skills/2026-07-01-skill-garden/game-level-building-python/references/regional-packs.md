# Regional Packs

Use this file when the user asks:

- what templates exist
- which pack to start from
- what kinds of ancient Chinese compounds are currently available
- for multiple options before generation

Always summarize the closest matching pack or packs before writing code when the user is browsing options.

All current templates in these packs support the shared `DETAIL_MODE` contract:

- `blockout`
- `low`
- `medium`
- `high`

When the user asks for a pack plus a fidelity level, offer the pack first, then state that the generated or adapted script can be produced at that requested detail level.

## Currently Available Packs

| Pack | Focus | Best For | Current Templates |
|---|---|---|---|
| Core Building Pack | single landmark and hall generators | pagodas, gates, halls, shrine buildings, warehouses | `main_keep_pagoda_generator.py`, `main_gate_generator.py`, `guest_hall_generator.py`, `secondary_hall_generator.py`, `warehouse_generator.py`, `boss_shrine_generator.py`, `modular_building_generator_template.py` |
| Axial Compound Pack | formal administrative and noble layouts | manor compounds, prefectural compounds, audience courts, palace-like progressions | `axial_compound_layout_template.py`, `palace_forecourt_administrative_template.py` |
| Fortified Frontier Pack | military and storage precincts | garrisons, depots, granary forts, wall gates, patrol compounds | `fortified_precinct_template.py`, `city_wall_gate_district_template.py`, `riverside_warehouse_dock_template.py` |
| Urban Ward Pack | dense civic and residential fabric | ward blocks, alley compounds, market-residential districts, artisan lanes | `inner_city_ward_block_template.py` |
| Sacred Terrace Pack | elevated ceremonial sequences | shrine climbs, summit sanctums, altar approaches | `terraced_shrine_sequence_template.py` |
| Court And Garden Pack | restrained formal leisure and courtyard spaces | pond courts, villa retreats, pavilion courts, noble respite compounds | `formal_garden_court_template.py`, `garden_villa_retreat_template.py`, `court_and_garden_pack_generator.py` |
| Funerary Precinct Pack | tomb and burial layouts | tomb mounds, mausoleum axes, spirit paths, offering courts, ritual burial compounds | `ritual_burial_precinct_template.py` |

## Quick Offer Menu

Use this as a short answer when the user asks what is available right now:

- `Core Building Pack`: pagodas, gates, halls, shrine buildings, warehouses
- `Axial Compound Pack`: manor compounds, administrative courts, audience forecourts
- `Fortified Frontier Pack`: defended gates, wall districts, depots, dockside warehouses
- `Urban Ward Pack`: ward blocks, alley compounds, dense inner-city residential and market fabric
- `Sacred Terrace Pack`: terraced shrine climbs and summit ceremonial layouts
- `Court And Garden Pack`: formal pond courts, villa retreats, pavilion-centered compounds
- `Funerary Precinct Pack`: tomb mounds, mausoleum approaches, spirit-path burial compounds

## Recommendation Rules

If the user asks for:

- a main seat, government hall, court, or noble residence: start with `Axial Compound Pack`
- walls, towers, barracks, depots, or district defense: start with `Fortified Frontier Pack`
- ward blocks, alleys, residential density, or market neighborhoods: start with `Urban Ward Pack`
- shrine climbs, ritual terraces, summit complexes: start with `Sacred Terrace Pack`
- villa compounds, pond courts, respite gardens, pavilion retreats: start with `Court And Garden Pack`
- tombs, mausoleums, spirit paths, burial courts, or ritual precincts: start with `Funerary Precinct Pack`
- a single hero building or a fast first-pass blockout: start with `Core Building Pack`

## Offer Format

When the user wants options, respond with:

1. the two closest packs
2. the specific templates inside each pack
3. one sentence on how each would fit the request

Then pick one only after giving the user that menu, unless the request clearly implies a single best fit.
