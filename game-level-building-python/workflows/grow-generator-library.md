<required_reading>
Read `references/script-library.md`, `references/variation-axes.md`, `references/script-template.md`, and `references/unreal-python-compatibility.md`.
</required_reading>

# Grow Generator Library

## Goal

Turn one request into a reusable family of scripts, presets, and composition helpers.

## Process

1. Start from one base generator.
2. Add three meaningful presets before creating a second standalone script.
3. Add shared helpers in `scripts/lib/` only when at least two generators need the same logic.
4. Place new user-facing generators in `scripts/generated/`.
5. Record the new script or preset in `references/script-library.md` when the package meaningfully expands.
6. Suggest the next layer:
   - preset family
   - compound helper
   - district composition
   - project mesh palette swap

## Recursive Pattern

Use this loop:

1. Extract base archetype
2. Build configurable generator
3. Add presets
4. Compose multiple instances
5. Save the composition as a new helper

Avoid producing isolated one-off files when a preset or composition layer would serve better.
