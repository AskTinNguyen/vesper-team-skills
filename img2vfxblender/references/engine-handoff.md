# NineTails handoff boundary

When this skill is used inside S2/NineTails, read the host repository's VFX authoring skill, system map, Niagara parameter contract, and relevant local content instructions before doing engine work. Other engines need the equivalent owner and parameter documentation. This package deliberately keeps those host-specific documents out of the skill so the handoff remains portable. Study documentation is not permission to control an Editor, author tags or modify assets.

Provide a handoff table with feature ID, Blender target, exported artifact if any, proposed Niagara/material equivalent, actual integration owner, registered parameter candidate, binding proof, and remaining mismatch. Unknown bindings stay null. Preserve source IDs and prototype timings separately from authoritative gameplay timings.

Select an approved finished `NS_*` family before a value preset. A `USipherVFXPreset`/`VP_*` contains typed overrides, not emitters or a Blender graph. Exact registered `User.*` names/types, consumer wiring, default parity, clean compile and runtime override are required before a control is supported. `User.Size`, `User.Lifetime` and conditional `User.Duration` are multipliers; `Duration` is not the gameplay-state duration. Burst count uses `User.Spawn_Count`; looping density uses `User.SpawnRate_Multiplier`.

GameplayCue/notify owns approved spawning, placement and lifecycle. Arena walls use the arena owner; traversal owns portal availability; the death/material owner controls body removal; damage feedback owns confirmed victim hits. Cosmetic overrides cannot change collision, teleport distance, parry windows, armor, targetability or protected state. Read the MainChar visual contract before body overlays or transformation integration.

The preset-authoring proposal in the reference package is a draft, not proof a tool is shipped. Neutral Blender renders and VFX Gym previews do not establish gameplay readability under concurrency. Record actual engine compile/runtime/profile results separately; never convert Blender render seconds into a GPU budget claim.
