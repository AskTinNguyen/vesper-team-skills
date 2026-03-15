# Script Template Guidance

Use `scripts/templates/modular_building_generator_template.py` as the default starting point for new reusable generators.

For compound-scale work, start from one of these:

- `scripts/templates/axial_compound_layout_template.py`
- `scripts/templates/palace_forecourt_administrative_template.py`
- `scripts/templates/fortified_precinct_template.py`
- `scripts/templates/city_wall_gate_district_template.py`
- `scripts/templates/riverside_warehouse_dock_template.py`
- `scripts/templates/inner_city_ward_block_template.py`
- `scripts/templates/formal_garden_court_template.py`
- `scripts/templates/garden_villa_retreat_template.py`
- `scripts/templates/terraced_shrine_sequence_template.py`
- `scripts/templates/ritual_burial_precinct_template.py`

## Required Structure

1. Config and preset section at the top
2. Optional ASCII scaffold comment block when the design is being invented from text
3. Small vector and spawning helpers
4. Cleanup and grouping helpers
5. Module builders such as plinth, core, wings, towers, courtyard walls, and stairs
6. One orchestration function that composes modules from config
7. Viewport-aware placement with a fallback origin
8. Final verification-friendly print statement

## Minimum Config Surface

At minimum, expose:

- building name
- preset name
- gameplay scale
- footprint dimensions
- roof style
- symmetry mode
- detail mode with `blockout`, `low`, `medium`, or `high`
- optional modules
- output folder
- random seed

## Output Contract

A good generated script should make it obvious:

- what to tweak first
- what the intended plan/front layout is when an ASCII scaffold is present
- how to add a new preset
- how to switch between blockout and ornamented passes
- how to disable optional modules
- where prior actors are cleaned up
- how to rerun safely
