# Project Art Asset Scan Overview

Use this file as the entry point for project-aware asset reuse.

## What This Scan Gives Us

- a current inventory generated from `E:/S2_/Content`
- a role-based manifest for court-and-garden generation
- a recommended palette payload that generators can consume automatically
- a handoff layer for later progressive-disclosure Markdown docs

## Current Baseline

| Metric | Value |
|---|---|
| Generated at | 2026-03-15 13:43 UTC |
| Repo root | `E:\S2_` |
| Content root | `E:\S2_\Content` |
| Total `.uasset` files scanned | 445000 |
| Roles with candidates | 11 |
| Recommended palette roles | 8 |

## Read Order

1. Start here for scan status and routing.
2. Read `project-art-asset-analysis.md` for curated pack and role guidance.
3. Read `project-art-asset-naming-convention-proposal.md` when planning naming cleanup or scan-quality improvements.
4. Read `project-art-asset-inventory.md` when you need exact candidate paths by role.
5. Read `project-art-asset-inventory.json` when a script or generator needs machine-readable palette data.

## Generator Hook

The current court-and-garden generator can consume the inventory-backed palette directly:

- set `PALETTE_NAME = "repo_scan_recommended"`
- use `PALETTE_APPLICATION_MODE = "replace"` or `"overlay"`

This keeps the layout logic stable while swapping blockout placeholders for project-aware assets.

## Scan Method

- scans `.uasset` files under `Content/`
- classifies by path and asset name heuristics
- prefers blueprint and static mesh candidates
- excludes obvious non-environment paths like animation, VFX, textures, and maps

## Trust Model

- treat the curated analysis as the best first recommendation layer
- treat the raw inventory as a searchable candidate pool, not perfect truth
- expect some false positives because this is not deep binary `.uasset` introspection
- rescan when major environment packs land or when the manifest feels stale
- use cached outputs by default instead of rescanning on every generator request

## Refresh Command

```powershell
python ".codex/skills/engineer/graphic-engineer/game-level-building-python/scripts/build_project_art_asset_inventory.py"
```

## Current Recommended Families

- `s2_core_env_prototype`
- `s2_core_env_mesh`
- `asian_modular_temple`
- `uscans_wind_temple`
- `bamboo_forest`
- `deep_in_the_forest`

## Curated Starter Palettes

- `project_native_court_garden`: Safest first pass for project-native court and garden generation.
- `prototype_plus_modular_temple`: Keep project-native pavilions and ponds while using cleaner modular walls and hall language.
- `garden_overgrowth_support`: Layer foliage-heavy dressing and older naturalized edges onto a project-native core.

## Next Step Toward Progressive Disclosure

Use this overview as the root node, then branch later into:

- pack documents
- role documents
- palette documents
- exact asset-path leaf documents

Until that deeper tree exists, this file is the canonical scan handoff document.
