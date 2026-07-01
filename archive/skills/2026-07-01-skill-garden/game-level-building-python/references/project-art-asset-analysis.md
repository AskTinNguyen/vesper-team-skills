# Project Art Asset Analysis

This document is a curated analysis layer on top of the raw inventory outputs:

- `project-art-asset-inventory.md`
- `project-art-asset-inventory.json`

Use this file first when deciding which asset families a generator should target. Use the raw inventory when you need exact asset paths by role.

## Analysis Summary

The repo already has enough environment content to support dynamic palette swapping without asking the user to hand-pick assets first.

The strongest court-and-garden asset families are:

1. `S2/Core_Env/Prototype`
2. `S2/Core_Env/Mesh`
3. `Asian_Modular_Temple`
4. `USCANS_WindTemple`
5. `Bamboo_Forest`
6. `DeepInTheForest`

The best immediate strategy is:

- use `S2/Core_Env/Prototype` for project-native garden prototypes and assembled blueprints
- use `Asian_Modular_Temple` for cleaner modular temple walls and hall language
- use `S2/Core_Env/Mesh` for project-native gates, rockery, and larger environment support
- use `Bamboo_Forest` or `DeepInTheForest` for foliage-heavy dressing passes

## Asset Family Tiers

### Tier 1: Project-Native Court And Garden Assets

#### `S2/Core_Env/Prototype`

Best for:

- pavilion families
- pond and basin features
- walls and screen walls
- gate variants
- trees, bonsai, benches, and small decor
- assembled blueprint-first swaps that match existing prototype language

Strong signals:

- many `BP_proto_env_L_Pavilion_*`
- `BP_proto_env_L_Pond_01`
- `BP_proto_env_L_Wall_01`
- `BP_proto_env_L_Gate_*`
- `BP_proto_env_L_Tree_*`
- `BP_proto_env_M_Rock_*`
- `BP_proto_env_M_Chair_*Bench*`

Primary recommendation:

- default first-choice palette source for court-and-garden generators

#### `S2/Core_Env/Mesh`

Best for:

- project-native gates and wall kits
- larger rockery and environment support
- foliage blueprints
- temple-adjacent structural pieces

Strong signals:

- `BP_Env_cm_Gate_01_Kit_*`
- `BP_Env_cm_Wall_01_Kit_*`
- `BP_Foliage_SM_DragonTree_04`
- `SM_RockMountain_A1`

Primary recommendation:

- second-choice source when the prototype set lacks the scale or finish level needed

### Tier 2: Modular Non-Project Kits

#### `Asian_Modular_Temple`

Best for:

- clean modular temple walls
- halls and gates
- roof language
- altar and prop dressing

Why it matters:

- strongest clean modular East Asian architectural kit in the repo
- good for swapping from prototype assembled blueprints to more regularized modular pieces

Primary recommendation:

- best marketplace source for walls and main hall style

#### `USCANS_WindTemple`

Best for:

- large compound walls
- fence lines and pillars
- floor and roof assemblies
- bigger precinct shells

Why it matters:

- largest temple/compound-style modular set identified by the scan agents

Primary recommendation:

- use for future compound-scale layouts more than small court layouts

### Tier 3: Foliage And Nature Support

#### `Bamboo_Forest`

Best for:

- bamboo groves
- path-edge rocks
- fern and ground dressing
- atmospheric garden perimeter treatment

Primary recommendation:

- strongest foliage add-on for Asian court-and-garden scenes

#### `DeepInTheForest`

Best for:

- mossy walls
- roots
- shrubs and wild ground coverage
- overgrown ruin variations

Primary recommendation:

- best support pack when the garden should feel older, wetter, or more overgrown

## Role Recommendations

### Walls

Best immediate candidates:

- `BP_proto_env_L_Wall_01`
- `BP_proto_env_L_Decor-Wall_01_ScreenPanel`
- `SM_Wall_Panel`, `SM_Wall_Panel_2`, `SM_Wall_Panel_3` from `Asian_Modular_Temple`

Recommendation:

- use `S2/Core_Env/Prototype` for readable project-native blockout
- use `Asian_Modular_Temple` for cleaner modular wall palettes

### Gates And Moon Gates

Best immediate candidates:

- `BP_proto_env_L_Gate_02_Actor`
- `BP_proto_env_L_Gate_03_Actor`
- `BP_proto_env_L_Gate_04_Actor`
- `BP_Env_cm_Gate_01_Kit_*`

Recommendation:

- treat the prototype gate family as the default moon-gate / court entry source
- use `S2/Core_Env/Mesh` gate kits for more modular perimeter work

### Main Hall / Villa / Pavilion

Best immediate candidates:

- `BP_proto_env_L_Pavilion_02_Tea_Actor`
- `BP_proto_env_L_Pavilion_03_Garden_Actor`
- `BP_proto_env_L_Pavilion_15_Actor`
- `BP_proto_env_L_Pavilion_16_Hill_Actor`
- `BP_proto_env_L_Pavilion_17_Island_Actor`
- `Asian_Modular_Temple/BP_Hall`
- `Asian_Modular_Temple/BP_Hall_2`

Recommendation:

- use prototype pavilions for court-centered and tea-court generation
- use `Asian_Modular_Temple` halls for more regularized formal architecture

### Ponds

Best immediate candidates:

- `BP_proto_env_L_Pond_01_Actor`
- `BP_proto_env_L_Pond_01`
- `BP_proto_env_M_Decor-Floor_02_WaterBasin`
- `BP_proto_env_L_Decor-Floor_16_PondDecors`

Recommendation:

- keep pond sourcing project-native for now

### Trees

Best immediate candidates:

- `BP_proto_env_L_Tree_01` through `BP_proto_env_L_Tree_04`
- `BP_proto_env_L_Decor-Floor_18_PottedTree`
- `BP_Foliage_SM_DragonTree_04`

Recommendation:

- default to prototype trees for curated gardens
- reserve broader foliage packs for later dressing layers

### Rockery

Best immediate candidates:

- `BP_proto_env_M_Rock_01`
- `BP_proto_env_M_Rock_02`
- `BP_proto_env_M_Rock_03`
- `SM_RockMountain_A1`

Recommendation:

- use project-native rockery first
- mix in `Bamboo_Forest` or `DeepInTheForest` rock sets for more natural borders later

## Best Starter Palettes

### `project_native_court_garden`

Use when:

- the goal is immediate compatibility with the existing project look

Composition:

- mostly `S2/Core_Env/Prototype`
- selected `S2/Core_Env/Mesh` support assets

### `prototype_plus_modular_temple`

Use when:

- the generator should keep project-native pavilions and ponds, but use cleaner modular walls and halls

Composition:

- pavilions, ponds, trees, rockery from `S2/Core_Env/Prototype`
- walls and main halls from `Asian_Modular_Temple`

### `garden_overgrowth_support`

Use when:

- the court should feel older, greener, and more naturalized

Composition:

- base structure from `S2/Core_Env/Prototype`
- foliage and rock support from `Bamboo_Forest` and `DeepInTheForest`

## Caveats

- This analysis is still name- and path-driven, not full binary `.uasset` introspection.
- Some high-ranked assets are assembled blueprints, which may scale differently than simple static meshes.
- Some packs are art reference or marketplace demo content and should be treated as candidates, not automatic defaults.
- `S2/Core_Env/Prototype` currently remains the safest first-choice family for court-and-garden generation.

## Next Use

When building progressive-disclosure docs later, branch outward from this file into:

- pack docs
- role docs
- style docs
- recommended palette docs
