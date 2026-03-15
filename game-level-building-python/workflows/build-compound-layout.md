<required_reading>
Read `references/design-principles.md`, `references/floor-plan-reading.md`, `references/era-archetypes.md`, `references/variation-axes.md`, and `references/unreal-python-compatibility.md`.
</required_reading>

# Build Compound Layout

## Goal

Generate a reusable layout script for a full compound, precinct, or formal garden court instead of a single building.

## Process

1. Decide the layout family:
   - axial ceremonial compound
   - fortified precinct
   - shrine terrace sequence
   - formal garden court
   - inner-city ward block or alley compound
   - tomb or ritual burial precinct
   - service yard or depot cluster
2. Extract the main circulation line, major courts, side wings, and landmark masses.
3. Encode the layout as repeated modules and toggles rather than fixed coordinates wherever practical.
4. Prefer one compound script with presets over separate one-off building files.
5. Save the layout generator under `scripts/generated/`.
6. Suggest at least one follow-on preset for a larger or denser version of the same compound.

## Required Output

- layout family
- module list
- key dimensions and spacing rules
- exact saved path
- exact launcher
- verification checklist for circulation, courts, and skyline
