# Design Principles

## Blockout Priorities

- Readability beats realism.
- Favor plinth, core mass, roof tiers, stairs, wings, towers, courtyards, and spires before ornament.
- Make traversal width, combat staging, and landmark silhouette legible from the first pass.
- Use oversized gameplay scale by default when no measured target is provided.

## First-Pass Scope

A first-pass generator should usually include:

- foundation or plinth
- dominant structural masses
- roof masses
- entry approach or stairs
- a scale reference if a safe mesh is available

It should not try to solve:

- final art polish
- final collision authoring
- dense set dressing
- material fidelity
- every decorative detail from the reference

## Customization Surface

Prefer scripts that expose explicit config keys near the top:

- `BUILDING_NAME`
- `GAMEPLAY_SCALE`
- `FOOTPRINT_WIDTH` / `FOOTPRINT_DEPTH`
- `FLOOR_COUNT` or `TIER_COUNT`
- `ROOF_STYLE`
- `SYMMETRY_MODE`
- `COURTYARD_ENABLED`
- `WING_COUNT`
- `STAIR_STYLE`
- `MESH_PALETTE`
- `DETAIL_MODE`
- `RANDOM_SEED`
- `OUTPUT_PREFIX`

Prefer presets plus toggles over duplicated scripts whenever the requested shapes share the same construction logic.

When using `DETAIL_MODE`, prefer:

- `blockout` for pure massing
- `low` for silhouette refinement
- `medium` for readable decorative support
- `high` for denser scene delicacy

## Verification Checklist

After running a generator, confirm:

- the Outliner contains `Generated/<BuildingName>`
- a `<BuildingName>_Group` is selected if grouping succeeded
- rerunning the script does not create duplicate actors with the same prefix
- the blockout spawns in front of the active viewport, or logs a clear fallback
- the silhouette contains the expected dominant masses from the brief
- traversal and stair scale read correctly next to the scale reference

## Second-Pass Extension

When evolving a blockout into a richer family, add:

- mesh palette dictionaries for project-specific swaps
- optional facade modules and ornament layers
- detail-mode toggles for eaves, lanterns, totems, tree markers, fence runs, and ridge caps
- courtyard walls, bridges, or gatehouse variants
- preset-driven roof and stair families
- compound composition helpers that place multiple generated structures together
