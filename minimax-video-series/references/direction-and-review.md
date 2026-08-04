# Direction and review

## Contents

1. Story architecture
2. Prompt construction
3. Transition vocabulary
4. Per-take review rubric
5. Movement-level self-analysis
6. Rerender strategy
7. Fixed-seed prompt A/B

## Story architecture

Give the protagonist a visible goal, cost, and choice. For each movement, define:

- opening condition;
- dramatic question;
- discovery or reversal;
- irreversible decision;
- final image that launches the next movement.

Escalate one axis at a time: space, knowledge, cost, agency, or community. Do not confuse adding more objects with escalation.

## Prompt construction

Use this order:

1. Exact continuation clause.
2. Global identity and style lock.
3. Current movement/chapter label.
4. Principal action.
5. One secondary environmental reaction.
6. Camera behavior.
7. Explicit final-frame composition and hold.
8. Transition language.
9. Audio ambience.
10. Negative constraints targeted to known drift.

Compile this direction through the official mode header and three-field contract. Keep chapter numbers, titles, movement names, and review commentary in the manifest rather than the model prompt. Use structured shots for exact cut times, camera grammar, speech, lyrics, voiceover, or visible text; run prompt lint before rendering.

Describe what must remain stable positively, then exclude recurring failure modes. Spatial restrictions are stronger than vague quality words: “rear view only; camera passes completely beyond her” is more useful than “high quality anatomy.”

## Transition vocabulary

- Shape match: seed→eye, eye→portal, branch→lightning.
- Occlusion wipe: trunk, root, bough, cloth, wing, or silhouette fills every pixel.
- Reflection fill: lower camera until water or mirror becomes the entire frame.
- Aperture push: move through a hollow, flower, crack, mouth, or doorway.
- Light wash: flare or circular pulse fills frame, then resolves elsewhere.
- Darkness handoff: stable featureless black with one retained point or line.
- Motion handoff: leaf, moth, seed, ash, or light carries screen direction into the next shot.
- Camera reorientation: controlled roll or crane used at a genuine story reversal.
- Graphic overlap: two stable profiles or forms align without morphing.
- Held wide: use after escalation to let the audience understand a new world state.

Vary transition families. Repeated centered walking and push-ins flatten rhythm even when individual clips look good.

## Per-take review rubric

Inspect the six-frame sheet and the video. Score each item pass/fail:

- Continuity: first second inherits the exact input composition.
- Identity: face, hair, clothing/surface, age, silhouette, and defining colors stay fixed.
- Anatomy: hands, limbs, face count, and body topology remain plausible and stable.
- Action: the requested principal action is legible without explanation.
- Restraint: no unrelated character, object, transformation, or uncontrolled duplication appears.
- Style: rendering medium, palette, line language, and aspect ratio remain coherent.
- Camera: movement is intentional and does not fight the action.
- Prompt conformance: requested cut timing, camera motion, exact words, visible text, and audio roles match the compiled prompt.
- Transition: final state is simple enough to seed the next clip.
- Hold: last 12–15 frames are nearly still.
- Audio: ambience fits, stereo track exists, no unwanted intelligible speech or abrupt artifact.

For dialogue or singing, verify speaker identity, exact supplied words, language, delivery, and lip behavior across every cut. For voiceover, require closed on-screen lips. For visible text, compare the render against the exact requested string rather than accepting a near spelling.

Reject on identity/anatomy drift, an unusable final frame, missing main action, or a style rupture that changes the story world. Minor divergence may be accepted only when it improves the narrative and remains chainable; record that judgment in review notes.

## Movement-level self-analysis

Every five chapters, inspect a midpoint contact sheet and ask:

- Does each chapter visibly change the story state?
- Is the protagonist choosing, or merely witnessing?
- Are compositions varying between macro, profile, lateral, overhead, and wide views?
- Are transition families repeating?
- Is color evolution motivated?
- Are secondary faces/figures distinct people rather than passive ornament?
- Did any accepted divergence create a stronger obligation for later chapters?
- Does the movement end more decisively than it began?

Use these answers to redirect only future chapters unless continuity itself is broken.

## Rerender strategy

Change one variable per attempt:

1. Tighten frame and visibility restrictions.
2. Reduce the chapter to one action.
3. Make the final tableau explicit and require full-frame occlusion where applicable.
4. Add targeted negatives for observed drift.
5. Change the seed only after prompt corrections.

Never propagate a take merely because rendering was expensive.

## Fixed-seed prompt A/B

Before adopting a prompt-compiler or contract change in production, compare baseline and candidate with the same reference frames, source audio where applicable, seed, model, dimensions, length, sampler, scheduler, and steps. Change only the compiled prompt.

Use the shortest trained grid length that exercises the feature. Cover I2VA, FL2VA, NativeAudio vocal, and NativeAudio instrumental cases when the change touches shared grammar. Score both takes with the per-take rubric plus exact requested cut/camera/text/audio behavior. Preserve prompts, hashes, runtime settings, and review notes; do not call a compiler change better from one favorable seed.
