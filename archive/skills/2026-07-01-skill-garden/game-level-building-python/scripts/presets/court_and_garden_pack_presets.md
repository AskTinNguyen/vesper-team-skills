# Court And Garden Pack Presets

Palette hooks:

- `PALETTE_NAME = "blockout"` keeps pure cube blockout mode
- `PALETTE_NAME = "prototype_garden"` swaps eligible modules to project art assets under `/Game/S2/Core_Env/Prototype`
- `PALETTE_NAME = "repo_scan_recommended"` loads the latest recommended palette from `references/project-art-asset-inventory.json`
- `PALETTE_APPLICATION_MODE = "replace"` swaps cubes out when art is available
- `PALETTE_APPLICATION_MODE = "overlay"` keeps blockout cubes and adds art on top for comparison
- Refresh the repo-scan palette by running `python ".codex/skills/engineer/graphic-engineer/game-level-building-python/scripts/build_project_art_asset_inventory.py"`

## `formal_pond_court`

- intended silhouette: axial pond court with a dominant north hall and balanced side pavilions
- key config overrides: medium footprint, bridge-enabled pond, entry screen wall, twin rockeries, 8-tree garden ring
- expected gameplay role: readable hub court, dueling arena shell, or noble audience garden

## `scholar_villa_retreat`

- intended silhouette: deeper walled estate with a main villa, south study, side pavilions, and paired moon gates
- key config overrides: largest footprint, broader villa mass, double moon-gate escape routes, lotus pond crosswalk
- expected gameplay role: traversal villa, stealth garden approach, or elite residential retreat

## `moon_gate_respite`

- intended silhouette: compact leisure court centered on a moon gate and tea pavilions
- key config overrides: smallest footprint, lower hall mass, no pond bridge, compact pool, relaxed garden walk
- expected gameplay role: side courtyard landmark, quiet rest stop, or encounter transition pocket

## `tea_ceremony_court`

- intended silhouette: intimate tea court with a small north tea hall, prep pavilions, twin moon gates, and a reflecting pool
- key config overrides: compact footprint, tighter paths, no bridge, paired tea prep wings, entry screen wall, offset rockeries
- expected gameplay role: social staging pocket, focused duel court, or quiet ceremonial encounter space
