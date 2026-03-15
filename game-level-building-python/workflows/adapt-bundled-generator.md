<required_reading>
Read `references/script-library.md`, `references/design-principles.md`, and `references/unreal-python-compatibility.md`.
</required_reading>

# Adapt Bundled Generator

## Goal

Start from an existing packaged script when the requested building is near an existing archetype.

## Process

1. Pick the closest bundled generator from `references/script-library.md`.
2. Keep the existing cleanup, foldering, and grouping behavior unless it blocks the new design.
3. Move repeated differences into config or presets instead of cloning the whole file.
4. Update deprecated camera-access patterns when you touch the script.
5. Save the result as either:
   - a preset-ready adaptation
   - or a new generator when the structure is no longer meaningfully shared

## Good Reasons To Fork

- the footprint logic changes completely
- the module list changes substantially
- the original script would become harder to understand than a clean new template-based file
