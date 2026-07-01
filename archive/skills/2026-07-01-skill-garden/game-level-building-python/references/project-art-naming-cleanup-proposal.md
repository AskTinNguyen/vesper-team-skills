# Project Art Naming Cleanup Proposal

This document is intended for the art lead and environment owners who want future asset scans, generator prompts, and AI-assisted layout building to work more reliably.

It is based on the current court-and-garden scan baseline:

- `445000` `.uasset` files scanned
- strongest target families are `S2/Core_Env/Prototype`, `S2/Core_Env/Mesh`, `Asian_Modular_Temple`, `USCANS_WindTemple`, `Bamboo_Forest`, and `DeepInTheForest`
- current scan quality is good enough to drive reuse, but naming is still doing too much guesswork

## Why This Matters

The current asset-reuse workflow is starting to work because the scanner can infer roles such as:

- `wall`
- `screen_wall`
- `gate`
- `main_hall`
- `villa`
- `pavilion`
- `pond`
- `tree`
- `rockery`
- `bench`
- `decor`

The more explicit those roles become in asset names, the less the generator has to rely on path heuristics, marketplace folder names, or lucky substring matches.

For AI-assisted generation, good names should answer these questions directly:

1. What kind of asset is this?
2. What gameplay or layout role does it serve?
3. Is it a single mesh piece, a kit piece, or a full assembled blueprint?
4. What style or source family does it belong to?
5. What variation, size, or state is this?

## What The Scan Is Still Struggling With

These are the recurring naming problems that forced scanner heuristics to stay defensive:

- mixed semantics in one token:
  `Decor-Wall` may actually mean `ScreenWall`, plaque, painting, or wall dressing rather than a structural wall
- scene nouns mixed with role nouns:
  `Pavilion_09_Grove` reads like a tree candidate because of `grove`, but it is really a pavilion scene assembly
- building pieces named as buildings:
  `TempleStair`, `TempleFence`, `TempleRoof` can be mistaken for `main_hall` candidates if the role token is too broad
- implicit assembly state:
  `_Actor` often means assembled blueprint, but the semantic difference is buried late in the name
- environment role hidden behind production shorthand:
  tokens like `proto`, `cm`, `Loc03`, or internal set IDs are meaningful to teams but weak for automated role detection
- seasonal or variant suffixes without stable ordering:
  `_Spring` or `_Var2` can appear before or after the part that actually matters
- overuse of generic words:
  `decor`, `module`, `part`, `object`, `prop`, and `asset` are not enough to drive layout generation unless a real role token is also present

## Recommendation

Adopt one controlled naming grammar for generator-relevant environment assets and preserve it across:

- blueprints
- static meshes
- foliage actors
- kit pieces
- hero assemblies

The scanner can still support legacy names, but newly named assets should be easy to classify by reading the name left-to-right.

## Proposed Naming Grammar

Recommended format:

`<ClassPrefix>_<Domain>_<Role>_<Subtype>_<StyleOrFamily>_<Scale>_<Variant>[_<State>][_Asm|_Kit|_Part]`

Examples:

- `BP_Env_Wall_Panel_Temple_M_01`
- `BP_Env_ScreenWall_Prototype_L_01`
- `BP_Env_Gate_Moon_Prototype_L_02_Asm`
- `BP_Env_MainHall_Temple_L_01`
- `BP_Env_Pavilion_Tea_Prototype_L_02_Asm`
- `BP_Env_Villa_Island_Prototype_L_17`
- `BP_Env_Pond_Basin_Prototype_M_02`
- `BP_Foliage_Tree_Dragon_L_04`
- `SM_Env_Rockery_Cliff_M_03`
- `BP_Env_Bench_Garden_Prototype_M_11`
- `BP_Env_Decor_Altar_Prototype_L_04`

## Token Meanings

### 1. Class Prefix

Use standard Unreal-style prefixes first:

- `BP` for blueprint actor or assembled asset
- `SM` for static mesh
- `SK` for skeletal mesh
- `T` for texture
- `M` or `MI` for material and material instance

This part should stay conventional so artists and technical users both recognize it instantly.

### 2. Domain

Use a small controlled vocabulary:

- `Env` for environment architecture and structural dressing
- `Foliage` for trees, bamboo, shrubs, and foliage wrappers
- `Prop` for loose objects that are not layout-defining
- `FX` for VFX-owned environment support when needed

For the current generator workflow, `Env` and `Foliage` are the most important.

### 3. Role

This is the most important AI-readable token and should be mandatory for generator-relevant assets.

Recommended controlled role list:

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

If an asset is expected to participate in layout generation, one of these should appear explicitly in the name.

### 4. Subtype

Use this to describe the functional or visual subtype, not the production origin.

Good examples:

- `Panel`
- `Tea`
- `Garden`
- `Island`
- `Hill`
- `Basin`
- `Arch`
- `Courtyard`
- `Hero`
- `Shrine`
- `Cliff`

Avoid using this slot for vague words like `Decor`, `Object`, or `Set`.

### 5. Style Or Family

This should identify the family or look:

- `Prototype`
- `Temple`
- `Bamboo`
- `Forest`
- `Overgrown`
- `Ruin`
- `Formal`

This token helps the generator keep a stable layout role while changing the art language.

### 6. Scale

Use a small controlled scale set:

- `XS`
- `S`
- `M`
- `L`
- `XL`

If the team prefers footprint-driven sizing, use a stable module size token instead, but keep it controlled.

### 7. Variant

Use zero-padded numbers:

- `01`
- `02`
- `03`

Do not put semantic meaning into the variant number alone.

### 8. Optional State

Only append state when it matters:

- `Clean`
- `Broken`
- `Overgrown`
- `Spring`
- `Summer`
- `Autumn`
- `Winter`

Keep state near the end so scanners can ignore it without losing the role.

### 9. Optional Assembly Marker

Use one clear marker for how the asset should behave in generation:

- `_Asm` for full assembled blueprint
- `_Kit` for reusable blueprint kit
- `_Part` for single modular piece

This is much more useful than relying on `_Actor` or hidden production habits.

## AI-Readable Rules

These rules matter more than style preferences if the goal is automated reuse.

- Put the role token before the family token.
- Use singular nouns for roles.
- Use full words instead of internal abbreviations when possible.
- Use underscores only.
- Avoid hyphenated semantic mixes such as `Decor-Wall` when a real role exists.
- Keep the same token order across blueprints and meshes.
- Make assemblies explicit with `_Asm`.
- Make kits explicit with `_Kit`.
- Do not rely on numbers to imply role, scale, or subtype.
- Put state or seasonal variants at the end.
- Keep location, sprint, or team-private codes out of the core role portion of the name.

## Practical Rename Examples

These are not mandatory exact names, but they show the direction.

| Current Name | Better AI-Readable Direction |
|---|---|
| `BP_proto_env_L_Decor-Wall_01_ScreenPanel` | `BP_Env_ScreenWall_Prototype_L_01` |
| `BP_proto_env_L_Pavilion_03_Garden_Actor` | `BP_Env_Pavilion_Garden_Prototype_L_03_Asm` |
| `BP_proto_env_L_Pavilion_17_Island` | `BP_Env_Villa_Island_Prototype_L_17` |
| `BP_proto_env_M_Decor-Floor_02_WaterBasin` | `BP_Env_Pond_Basin_Prototype_M_02` |
| `SM_Env_cm_Wall_01_Part_03` | `SM_Env_Wall_Panel_Prototype_M_03_Part` |
| `BP_Env_cm_Gate_01_Kit_03_Spring` | `BP_Env_Gate_Formal_Prototype_M_03_Spring_Kit` |
| `BP_Foliage_SM_DragonTree_04` | `BP_Foliage_Tree_Dragon_L_04` |

## Recommended Cleanup Priority

### Priority 1

Rename generator-driving assets first:

- walls
- gates
- main halls
- pavilions
- villas
- ponds
- trees
- rockery

These roles directly affect automated layout quality.

### Priority 2

Make assembly state explicit:

- rename scene-level blueprints with `_Asm`
- rename kits with `_Kit`
- rename modular pieces with `_Part`

This makes spawning behavior safer for tools.

### Priority 3

Normalize family/style tokens:

- `Prototype`
- `Temple`
- `Bamboo`
- `Forest`
- `Overgrown`

This is what makes palette switching dependable.

### Priority 4

Clean up long-tail decor and secondary props after the main layout roles are stable.

## Low-Risk Adoption Plan

1. Start with newly created assets only.
2. Apply the role token dictionary to the court-and-garden families first.
3. Add redirectors or migration support for renamed assets.
4. After the first cleanup pass, update the scanner to prefer explicit role tokens over heuristics.
5. Expand the same grammar to other environment themes once the workflow proves useful.

## What Success Looks Like

If the naming cleanup works, future scans should be able to answer questions like:

- "Find me all project-native `ScreenWall` assets."
- "Swap only `Pavilion` assemblies from `Prototype` to `Temple`."
- "Populate a courtyard with `Tree`, `Rockery`, and `Bench` assets from the `Overgrown` family."
- "Use `MoonGate` assets only when that role appears explicitly."

That is the point of this cleanup: less guesswork, better generator control, and much stronger AI-assisted asset reuse.
