---
name: game-level-building-python
description: Use when a user wants reusable Unreal Python building generators, concept-art or floor-plan extraction, or a growing library of configurable level-design scripts.
---

# Unreal Python Building Generator

## Objective

Turn a text brief, drawing, concept art sheet, or floor plan into a reusable Unreal Editor Python generator that produces gameplay-first blockouts and can grow into a larger script library over time.

When spatial ambiguity is high, use an ASCII previsualization step before writing the Unreal Python generator so facade, plan, and component axes are explicit.

## Best For

- concept-art-driven blockouts
- floor-plan-to-blockout conversion
- fast UE editor building generators without C++ or PCG
- reusable generator families with presets and variations
- compound, district, or landmark libraries built from one shared pattern

Typical triggers:
- "make a Python generator for this building"
- "turn this concept art into a reusable Unreal script"
- "derive a blockout generator from this floor plan"
- "make three variations from this drawing"
- "grow this into a library of pagoda / gate / hall scripts"
- "save the script so I can rerun it in Unreal"

## Success Criteria

A good result from this skill should include all of the following:

- a saved `.py` script, preferably under this skill's `scripts/generated/` folder
- a one-line launcher with the exact saved path
- a clear customization surface at the top of the script
- idempotent rerun behavior that replaces prior actors with the same prefix when practical
- foldered output under `Generated/<BuildingName>`
- best-effort grouping, or a clear fallback when grouping is unavailable
- a short verification checklist describing what should appear in the Outliner and viewport
- at least one next-step path: variant preset, script family, or compound expansion

## Intake

Before writing code, identify:

- source type: text brief, concept art, floor plan, hybrid reference, or existing bundled script
- target outcome: one-off blockout, reusable generator, preset family, or recursive library growth
- gameplay intent: traversal landmark, combat arena shell, gate choke, courtyard hub, shrine approach, or set dressing shell
- expected customization: size only, silhouette variants, footprint variants, style presets, batch output, or asset-swap hooks

## Routing

Use the smallest workflow that fits the request.

| Input / Goal | Open Next |
|---|---|
| Verbal brief or quick design direction | `workflows/build-from-text-brief.md` |
| Paintover, drawing, or concept art sheet | `workflows/build-from-concept-art.md` |
| Floor plan, layout sketch, or architectural reference | `workflows/build-from-floor-plan.md` |
| User wants a whole compound, precinct, or garden court layout | `workflows/build-compound-layout.md` |
| Existing bundled script needs extension | `workflows/adapt-bundled-generator.md` |
| User wants a reusable family of scripts and presets | `workflows/grow-generator-library.md` |
| Need a quick starter scaffold | `references/script-template.md` and `scripts/templates/modular_building_generator_template.py` |

## Default Delivery Pattern

Prefer a saved `.py` file plus a one-line launcher over a large console paste.

Default save location:
- `E:\S2_\.codex\skills\engineer\graphic-engineer\game-level-building-python\scripts\generated\<building_slug>_generator.py`

Launcher pattern:

```python
exec(open(r"E:\S2_\.codex\skills\engineer\graphic-engineer\game-level-building-python\scripts\generated\<building_slug>_generator.py", encoding="utf-8").read(), globals())
```

In practice, large console pastes are brittle. Prefer saved scripts for repeatability, diffability, and reuse.

## Required Reading

Read only what the request needs:

- `references/design-principles.md`
- `references/unreal-python-compatibility.md`
- `references/detail-modes.md`
- `references/source-analysis.md`
- `references/floor-plan-reading.md`
- `references/era-archetypes.md`
- `references/regional-packs.md`
- `references/variation-axes.md`
- `references/script-library.md`
- `references/script-template.md`
- `references/project-art-asset-scan-overview.md` when the user wants project-aware palette swaps or real asset reuse
- `references/project-art-assets/index.md` for the progressive-disclosure Markdown tree built from the scan
- `references/project-art-asset-analysis.md` for curated family and starter palette guidance
- `references/project-art-asset-naming-convention-proposal.md` when the team wants cleaner future asset naming for scans and AI reuse
- `references/project-art-asset-inventory.md` when exact candidate asset paths are needed by role
- `references/ascii-previs.md`

## Core Rules

- Start from gameplay-first silhouette and circulation, not art fidelity.
- When doorway, gate, or facade placement is ambiguous, draft a quick ASCII plan and front elevation before writing 3D generation code.
- Prefer one configurable generator with presets over many near-duplicate scripts.
- Expose meaningful knobs: footprint, floor count, roof family, stair profile, symmetry, courtyard, wing count, mesh palette, and output naming.
- When the user wants a richer look, expose `DETAIL_MODE` with progressive `blockout`, `low`, `medium`, and `high` passes rather than baking ornament into the base massing.
- Separate engine-guaranteed assets from project-optional assets.
- Treat bundled scripts as reference starting points; use subsystem-based camera access for new work.
- When the user provides unusual references, decompose them into modules instead of forcing a single archetype.
- When the user asks for templates, packs, or starting points, offer the relevant currently available packs from `references/regional-packs.md` before choosing one.

## Bundled Assets

The current packaged examples are indexed in `references/script-library.md`.

Use them as:
- ready-to-run first-pass generators
- adaptation bases for nearby archetypes
- pattern references for naming, cleanup, grouping, and blockout massing

Use `scripts/templates/modular_building_generator_template.py` when you need a fresh configurable generator rather than another one-off file.

For compound-scale work, start with one of the dedicated layout templates in `scripts/templates/`.

For project-aware asset reuse, refresh the inventory with:

- `python "E:\S2_\.codex\skills\engineer\graphic-engineer\game-level-building-python\scripts\build_project_art_asset_inventory.py"`

## Available Packs

When the user asks what templates or packs exist, summarize the currently available sets from `references/regional-packs.md` first, then recommend the closest one based on the request.

## Related Skills

Route onward when useful:

- `architectural-review`: critique floor plans or drawings before extracting modules
- `game-level-building-python`: stay here for generator authoring and variation building
- `open-editor`: launch Unreal before validating scripts
- `read-uasset` or `read-uasset-deep`: inspect existing asset naming and dependencies when replacing placeholders
- `plugin-documenter`: explain the resulting tool or generator for non-programmers

## Output Contract

Every response produced with this skill should include:

- extracted design summary
- ASCII plan/elevation scaffold when the spatial layout was ambiguous or newly invented
- relevant currently available packs or templates, when the user asked for options
- chosen archetype or module stack
- exposed parameters and presets
- chosen detail mode when the user asked for visual richness
- exact saved file path
- exact launcher line
- verification checklist
- recommended next variants or library additions
