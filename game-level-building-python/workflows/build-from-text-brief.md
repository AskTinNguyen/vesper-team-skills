<required_reading>
Read `references/design-principles.md`, `references/script-template.md`, `references/ascii-previs.md`, and `references/unreal-python-compatibility.md`.
</required_reading>

# Build From Text Brief

## Goal

Turn a verbal request into a reusable Unreal Python generator, not just a one-off script.

## Process

1. Extract archetype, gameplay role, and the top three silhouette cues.
2. If the layout is still fuzzy, draft a quick ASCII top plan and front elevation before any 3D scripting.
3. Choose whether this should be:
   - a fresh generator from the template
   - an adaptation of a bundled script
   - or a preset added to an existing family
4. Define the minimum customization surface the user is likely to need.
5. Save the script under `scripts/generated/` when creating a new file.
6. Provide the exact launcher line.
7. Provide a short verification checklist.

## Required Output

- extracted design summary
- ASCII plan/elevation when the layout was newly invented or axis-sensitive
- chosen archetype
- exposed config keys
- exact path
- exact launcher
- verification checklist
- next suggested presets or family expansions
