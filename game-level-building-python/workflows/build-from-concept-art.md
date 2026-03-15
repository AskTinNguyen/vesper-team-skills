<required_reading>
Read `references/design-principles.md`, `references/source-analysis.md`, `references/script-template.md`, and `references/unreal-python-compatibility.md`.
</required_reading>

# Build From Concept Art

## Goal

Extract structure from concept art, drawings, or screenshots, then encode the reusable parts into a generator.

## Process

1. Write a short extracted spec before writing code.
2. Identify:
   - dominant footprint
   - tier count
   - roof family
   - entry axis
   - symmetry mode
   - repeated motifs
3. Decide which details become geometry now and which become future mesh swaps.
4. Prefer one configurable base plus presets if the art suggests multiple nearby variants.
5. Save the generated script and include the launcher.
6. Suggest at least two follow-on variants based on unused motifs in the art.

## Verification

Confirm the generated blockout preserves:

- the main skyline silhouette
- the entry approach
- the dominant footprint
- the largest repeated massing rhythm
