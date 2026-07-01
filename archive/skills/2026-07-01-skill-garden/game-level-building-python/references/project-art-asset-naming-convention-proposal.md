# Project Art Asset Naming Convention Proposal

This document is for the art lead, tech art, and tools owners.

Its purpose is to make future asset scans, AI-assisted generation, and palette building much more reliable without forcing artists to learn a complicated new workflow.

## Why This Matters

Our current project-aware scan touches roughly `445000` `.uasset` files and depends heavily on path and name heuristics.

That means naming quality directly affects:

- how well AI can infer pack, role, and form
- how safely generators can swap blockout assets for real assets
- how cleanly we can build manifests and progressive-disclosure docs
- how much manual cleanup is needed after every scan

The goal is not "perfect names."

The goal is names that are predictable enough that a human and an AI can both read the same asset and reach the same conclusion about:

- what it is
- what role it serves
- whether it is a module or an assembly
- which family it belongs to
- whether it is a variant, state, or seasonal version

## Current Naming Problems Seen In The Repo

### 1. Role ambiguity

Examples:

- `BP_proto_env_L_Decor-Wall_01_ScreenPanel`
- `BP_proto_env_M_Chair_02_StoneBench`
- `BP_Temple`

Problems:

- the same name can imply two or three roles
- `Decor`, `Wall`, `Chair`, `Bench`, and `Temple` are too broad on their own
- scanners have to guess whether something is a wall, prop, screen wall, bench, hall, or shrine

### 2. Assembly vs module ambiguity

Examples:

- `BP_proto_env_L_Gate_02_Actor`
- `BP_Env_cm_Gate_01_Kit_01`
- `SM_Env_cm_Gate_01_Part_01`

Problems:

- `Actor` tells us almost nothing about the asset's structural intent
- `Kit`, `Part`, and full assembled blueprints are mixed, but not in a fully consistent way
- AI cannot always tell whether the asset should replace one box, a modular strip, or a whole entrance

### 3. State or seasonal variants are mixed into core identity

Examples:

- `BP_Env_cm_Gate_01_Kit_01_Spring`
- `BP_Foliage_SM_DragonTree_04_NoNanite`
- `SM_env_GiantTree_High_dec1`

Problems:

- important state markers are there, but not normalized
- `Spring`, `NoNanite`, `High`, and `dec1` are all different kinds of suffixes
- scans can mistake a state variant for a unique design family

### 4. Generic buckets are overloaded

Examples:

- `Decor`
- `Prop`
- `Env`
- `Floor`
- `Temple`

Problems:

- these terms are useful as broad categories, but weak as final role labels
- if a name depends on generic tokens, role inference becomes fuzzy

### 5. Typo and abbreviation drift

Examples:

- `BP_proto_env_M_Chair_08_Toture`
- `BP_proto_env_S_Decor-Wall_03_Celendar`
- `cm`
- `proto`
- `env`

Problems:

- typo drift weakens searchability and automation
- personal or historical abbreviations are understandable to teams, but harder for new tools and new teammates

### 6. Similar nouns describe different physical scales

Examples:

- `BP_Temple`
- `BP_Hall`
- `BP_proto_env_L_Pavilion_02_Tea`
- `BP_proto_env_L_Pavilion_17_Island`

Problems:

- some names describe a small pavilion and some describe an entire hall or precinct
- role, subtype, and scale are not always clearly separated

## What A Good Name Should Let Us Infer

From the asset name alone, an AI or tool should be able to infer:

1. asset type: blueprint, static mesh, material instance, foliage wrapper, and so on
2. family or library: `S2Proto`, `S2Env`, `AsianTemple`, `BambooForest`
3. domain: architecture, nature, prop, fx
4. role: `Wall`, `ScreenWall`, `Gate`, `MoonGate`, `MainHall`, `Pavilion`, `Pond`, `Tree`, `Rockery`, `Bench`, `Decor`
5. form: `Assembly`, `Kit`, `Part`, `Module`, `Cluster`, `Single`
6. subtype: `Tea`, `Garden`, `Dragon`, `Stone`, `Island`, `Hill`
7. variant: `V01`, `V02`
8. optional state: `Spring`, `Ruin`, `Mossy`, `NoNanite`, `LOD0`

## Proposed Naming Grammar

Use this format for environment assets:

```text
<Prefix>_<Library>_<Domain>_<Role>_<Subtype>_<Form>_<Scale>_<Variant>[_<State>]
```

Not every token is required on every asset, but the order should stay stable.

## Controlled Vocabulary

### Prefix

- `BP`: Blueprint assembly or wrapper
- `SM`: Static mesh
- `SK`: Skeletal mesh
- `MI`: Material instance
- `MPC`: Material parameter collection

### Library

Use a stable project-approved family token.

Recommended examples:

- `S2Proto`
- `S2Env`
- `AsianTemple`
- `WindTemple`
- `BambooForest`
- `DeepForest`

### Domain

- `Arch`
- `Nature`
- `Prop`
- `FX`

### Role

Use one primary role token only.

Recommended role dictionary for this workflow:

- `Wall`
- `ScreenWall`
- `Gate`
- `MoonGate`
- `MainHall`
- `Villa`
- `Pavilion`
- `Pond`
- `Tree`
- `Rockery`
- `Bench`
- `Decor`

### Form

- `Assembly`
- `Kit`
- `Part`
- `Module`
- `Cluster`
- `Single`
- `Hero`

### Scale

Prefer explicit size words over single letters when possible:

- `Small`
- `Medium`
- `Large`
- `XL`
- `Hero`

### Variant

Always use zero-padded variants:

- `V01`
- `V02`
- `V03`

### State

Optional suffixes for non-identity states:

- `Spring`
- `Summer`
- `Autumn`
- `Winter`
- `Ruin`
- `Mossy`
- `NoNanite`
- `LOD0`

## Practical Rules

### Rule 1. Put the primary role early

Good:

- `SM_S2Env_Arch_Wall_Straight_Part_Large_V01`

Weak:

- `SM_env_dec_temple_wall_thing_01`

### Rule 2. Use one primary role per asset name

If an asset is really a bench, do not leave it named as a chair.

Good:

- `BP_S2Proto_Prop_Bench_Stone_Assembly_Medium_V02`

Weak:

- `BP_proto_env_M_Chair_02_StoneBench`

### Rule 3. Use `Assembly` instead of `Actor`

`Actor` is a technical Unreal concept, not a useful content role.

Good:

- `BP_S2Proto_Arch_Gate_Moon_Assembly_Large_V02`

Weak:

- `BP_proto_env_L_Gate_02_Actor`

### Rule 4. Keep seasonal or runtime state at the end

Good:

- `BP_S2Env_Arch_Gate_Kit_Medium_V01_Spring`
- `BP_S2Env_Nature_Tree_Dragon_Assembly_Large_V04_NoNanite`

### Rule 5. Avoid generic `Decor` when a more precise role exists

Use `ScreenWall`, `Bench`, `Pond`, `Rockery`, `Tree`, or `MainHall` if that is the actual functional role.

### Rule 6. Avoid undocumented abbreviations

If a code is necessary, it needs a shared dictionary.

Good:

- `S2Proto`
- `S2Env`

Weak:

- `cm`
- `env`
- `proto` when there are multiple prototype families

### Rule 7. Fix typos instead of normalizing around them

Examples that should be corrected:

- `Toture` -> `Torture`
- `Celendar` -> `Calendar`

## Suggested Folder Alignment

If feasible, the folder path should mirror the same logic:

```text
/Game/<Library>/<Domain>/<Role>/<AssetName>
```

Examples:

- `/Game/S2Proto/Arch/Gate/BP_S2Proto_Arch_Gate_Moon_Assembly_Large_V02`
- `/Game/S2Proto/Nature/Tree/BP_S2Proto_Nature_Tree_Potted_Assembly_Medium_V18`
- `/Game/AsianTemple/Arch/MainHall/BP_AsianTemple_Arch_MainHall_Assembly_Large_V01`

This makes scans more accurate even before opening the asset name itself.

## Example Renames

These are proposed directionally, not as a forced batch rename list.

| Current Name | Proposed Direction |
|---|---|
| `BP_proto_env_L_Gate_02_Actor` | `BP_S2Proto_Arch_Gate_Assembly_Large_V02` |
| `BP_proto_env_L_Decor-Wall_01_ScreenPanel` | `BP_S2Proto_Arch_ScreenWall_Assembly_Large_V01` |
| `BP_Env_cm_Gate_01_Kit_01_Spring` | `BP_S2Env_Arch_Gate_Kit_Medium_V01_Spring` |
| `SM_env_prop_TreeRoots_01_module_01` | `SM_S2Env_Nature_RootCluster_Module_Medium_V01` |
| `BP_proto_env_M_Chair_02_StoneBench` | `BP_S2Proto_Prop_Bench_Stone_Assembly_Medium_V02` |
| `BP_Temple` | `BP_AsianTemple_Arch_MainHall_Assembly_Large_V01` if that is the actual content role |
| `SM_env_GiantTree_High_dec1` | `SM_S2Env_Nature_Tree_Giant_Hero_V01` |

## Cleanup Priority

### P0. Apply to all new assets immediately

This gives us forward progress without blocking shipping work.

### P1. Rename the highest-value court-and-garden families first

Suggested first wave:

- `S2/Core_Env/Prototype`
- `S2/Core_Env/Mesh`
- `Asian_Modular_Temple`

### P2. Normalize role-heavy assets before generic props

Suggested priority order:

- walls
- screen walls
- gates
- pavilions
- main halls
- ponds
- trees
- rockery
- benches

### P3. Normalize state suffixes and typo fixes

Examples:

- `Spring`
- `NoNanite`
- `High`
- typo repairs

## Migration Strategy

1. Freeze the controlled vocabulary in this document.
2. Apply it to all new content first.
3. Rename only the highest-signal legacy families next.
4. Regenerate the scan after each rename wave.
5. Compare scan precision improvements role by role.

## Recommendation

The naming system does not need to become beautiful or academic.

It only needs to become consistent enough that:

- artists can browse it quickly
- tech art can validate it
- AI can infer role and family with high confidence
- future generators can safely place real assets instead of blockout placeholders

If we follow this proposal, scan quality should improve materially even before deeper asset metadata is added.
