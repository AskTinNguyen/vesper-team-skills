# MiniMax H3 official prompt contract

Use this concise contract when compiling or reviewing prompts. It paraphrases the [official English base guide](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md), reviewed at repository revision `b8b09e34f8d2b9d1b7a51982ccb26ae2b8b9ef08` on 2026-08-04.

## Prompt order

Put the mode-specific image-alignment instruction first, then one blank line. T2VA has no alignment instruction. Follow with exactly:

1. `integrated_multimodal_description`
2. `overall_soundscape`
3. `non_diegetic_music`

Use the effective generated duration, formatted to two decimals, for final-frame alignment. FL2VA identifies the actual final shot containing Picture 2; L2VA identifies the final shot containing its sole ending picture.

## Keyframe paths

- **I2VA**: establish the style, identity, composition, objects, and spatial relationships from Picture 1; then develop continuously forward.
- **FL2VA**: describe observable intermediate pose, object, composition, camera, and lighting changes that connect Picture 1 to Picture 2. Prefer one continuous shot.
- **L2VA**: infer a plausible earlier state and progressively converge on the supplied final image.
- Do not expect endpoint conditioning to stabilize an implausible transformation.

## Shots and camera

Do not timestamp Shot 1. Start every later shot with a strictly increasing cut time inside the effective duration. Use ordinary cut language unless the user explicitly requests a dissolve, fade, or wipe. Every cut must reveal new subject, space, state, viewpoint, or time; use camera motion for a small framing change.

Express camera direction as motion type plus optional amplitude and speed inside a natural sentence. Supported types include zoom, push/pull, pan, truck, tilt, pedestal, arc, tracking, static, shake, POV, and roll. Use only small/large amplitude and slow/fast speed when those qualifiers matter.

## Speakers, exact words, and text

Register vocalizing subjects as stable `(S1)`, `(S2)`, ... identities across shots and chapters. Put identity, vocal character, action, and delivery outside `<d>`; put only `[Language]` and exact user-provided words inside. Never translate, rewrite, or repair supplied dialogue or lyrics.

Use the exact phrase `says in an off-screen voiceover` for voiceover and immediately state that the corresponding on-screen character's lips remain completely closed. Use paired `<scenetrans>` markers when one utterance crosses a cut and `<cutoff>` when the video truncates it.

Write deliberate visible text verbatim inside English double quotation marks. Do not generate labels, subtitles, signs, or logos that the user did not request.

## Audio fields

`overall_soundscape` contains 1-4 complete English sentences about ambience, physical action sounds, and non-verbal human sounds. Do not repeat dialogue, singing, or diegetic music. Use `N/A` only for explicitly complete silence.

`non_diegetic_music` contains 1-3 complete English sentences about audience-only music. Describe instrumentation, tempo, rhythm, and dynamic changes rather than mood or narrative purpose. Put music audible to characters, including visible performance, radio, television, or phone playback, in the multimodal description. Use `N/A` when there is no audience-only score.

## Local enforcement

Run `h3_prompt.py lint` before preflight. Treat errors as render blockers. The compiler removes chapter titles and movement metadata from model prompts, validates cut times and structured cameras, preserves exact speech and visible text, and emits official mode headers. Keep raw prose `prompt` support only for backward compatibility; prefer structured `shots` for new work.
