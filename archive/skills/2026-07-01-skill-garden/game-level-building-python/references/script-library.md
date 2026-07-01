# Script Library

## Current Bundled Generators

| Script | Current Use | Strongest Pattern | Good Next Adaptations |
|---|---|---|---|
| `scripts/main_keep_pagoda_generator.py` | central landmark pagoda | stacked roof tiers and vertical silhouette | shrine towers, watchtowers, tiered keeps |
| `scripts/main_gate_generator.py` | gate complex | twin-tower gate massing | wall gates, bridge gates, checkpoint entries |
| `scripts/guest_hall_generator.py` | guest-facing hall | core plus mirrored wings | audience halls, inns, barracks halls |
| `scripts/secondary_hall_generator.py` | secondary hall | hall variant proportions | side halls, temple annexes, service halls |
| `scripts/warehouse_generator.py` | utilitarian building | simple hall massing | workshops, market sheds, storehouses |
| `scripts/boss_shrine_generator.py` | shrine approach | ceremonial massing | sanctums, altar halls, summit landmarks |
| `scripts/generated/court_and_garden_pack_generator.py` | court and garden family | preset-driven courtyard layouts plus showcase composition | tea courts, noble estates, expanded leisure compounds |
| `scripts/generated/garden_district_showcase_layout_generator.py` | composed garden district | district-scale layout built from the pack generator | full leisure precincts, noble quarters, linked retreat chains |

## Library Growth Layout

Use this folder layout as the package grows:

- `scripts/generated/`: newly produced user-facing generators
- `scripts/templates/`: starter generator scaffolds
- `scripts/presets/`: preset notes, config sets, or serialized parameter packs
- `scripts/lib/`: shared helper modules when multiple generators need the same logic

## Template Pack

Use these templates when the request is broader than a single building:

| Template | Best For |
|---|---|
| `scripts/templates/modular_building_generator_template.py` | configurable single-building families |
| `scripts/templates/axial_compound_layout_template.py` | manor, palace, or prefectural axial compounds |
| `scripts/templates/palace_forecourt_administrative_template.py` | audience forecourts, official compounds, and palace-adjacent administration |
| `scripts/templates/fortified_precinct_template.py` | garrisons, depots, granary forts, and gate precincts |
| `scripts/templates/city_wall_gate_district_template.py` | wall-gate districts, market gates, and defended entry streets |
| `scripts/templates/riverside_warehouse_dock_template.py` | river ports, supply quays, and dockside warehouse compounds |
| `scripts/templates/inner_city_ward_block_template.py` | ward blocks, alley compounds, and dense market-residential fabric |
| `scripts/templates/formal_garden_court_template.py` | restrained formal courts with ponds, pavilions, and trees |
| `scripts/templates/garden_villa_retreat_template.py` | noble retreats, villa courts, and walled leisure compounds |
| `scripts/templates/terraced_shrine_sequence_template.py` | hill shrines, altar climbs, and summit ceremonial layouts |
| `scripts/templates/ritual_burial_precinct_template.py` | tomb mounds, mausoleum axes, spirit paths, and burial courts |

All templates under `scripts/templates/` now expose the same fidelity contract:

- `DETAIL_MODE = "blockout"`, `"low"`, `"medium"`, or `"high"`
- `ornamented` is treated as `medium`
- `blockout` keeps the original gameplay-first massing
- `low` sharpens silhouette and architectural readability
- `medium` adds readable scene dressing and decorative support
- `high` adds a larger composition pass specific to the template archetype

## Naming Convention

Prefer:

- `<archetype>_generator.py` for reusable bases
- `<archetype>_<preset>_generator.py` for stable preset exports
- `<compound_name>_layout_generator.py` for composition helpers

## Manifest Expectations

When growing the library, maintain an index with:

- script name
- archetype
- main presets
- expected input style
- best extension path
