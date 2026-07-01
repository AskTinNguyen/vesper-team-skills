<required_reading>
Read `references/design-principles.md`, `references/floor-plan-reading.md`, `references/script-template.md`, and `references/unreal-python-compatibility.md`.
</required_reading>

# Build From Floor Plan

## Goal

Convert a plan, layout sketch, or courtyard diagram into a generator that preserves layout logic, not just facade shape.

## Process

1. Extract the axis system and major solids and voids.
2. Translate repeated bays into reusable module dimensions.
3. Encode courtyards, side wings, gates, and shrine cores as toggles or sub-builders.
4. Prefer a compound-friendly generator if the plan already implies multiple structures.
5. Save the script under `scripts/generated/`.
6. Include a launcher and a note about which future presets would cover alternate plan layouts.

## Minimum Deliverable

- plan-derived spec summary
- module list
- config keys tied to plan features
- exact path and launcher
- verification checklist for footprint and circulation
