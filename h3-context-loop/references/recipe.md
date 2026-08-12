# MiniMax H3 22-frame context-loop recipe

## Tested stack

- ComfyUI root: `C:\ComfyUI-H3`
- Context loop: `ethanfel/ComfyUI-MiniMaxH3-Contex-Loop` v0.3.11, pinned at
  `92f923feef7472be1ef78232c6eff156d5b993bc`
- LightX LoRA: `minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors`,
  strength `0.8`, Euler, simple scheduler, six steps
- Continuation: 22 video frames, 22 generated-audio frames, `video` encoding,
  `head` anchor, crop disabled, Loop Trim `match_tail=true`, Spectrum off
- Attention: verified native CUDA 13 ConvRot path. SageAttention is optional and
  may be enabled only when an official build exactly matches the runtime.

## Why the connection works

Each continuation regenerates roughly 0.92 seconds from the previous scene's
22-frame tail. The context node carries motion and audio into H3 conditioning;
the trim node removes the repeated leading overlap and frame-locks the decoded
audio. Each delivered scene is saved before review, so approval, retry, resume,
partial assembly, and final assembly operate on durable checkpoints.

## Scene boundary contract

Write shared visual style, stable subjects, speaker IDs, and character-sheet
roles once in `prompt_prefix`. In every later scene, describe the preceding
ending state again: pose, unfinished action, prop positions, camera direction,
environment, lighting, ambience, and music. Keep that state alive for about two
seconds, since an immediate cut can make H3 render the old and new states at the
same time.

End each scene on a still or low-motion transition beat such as a planted pose,
held close-up, door in motion, or camera glide that can be repeated naturally.
For a continuous take, leave the character and camera motion explicitly in
progress instead. Repeat distinguishing descriptions and negative clauses for
secondary characters when identity bleed is possible.

## Ref2VA prompt structure

Use native labels consistently:

- Define visible identity/style sources as `<Subject N>` and cite the relevant
  `<Picture N>` or `<Video N>`.
- Reserve `<Video N>` for whole-video continuation, editing, camera, or temporal
  relationships.
- Use `<Audio N>` for copied or referenced voice, music, rhythm, or sound.
- Keep global speaker IDs `(S1)`, `(S2)`, and so on stable across scenes. Put
  spoken words in `<d>[Language] ...</d>`.
- Structure detailed prompts with `subject_definitions`, `summary`,
  `retention_analysis`, `detailed_description`, `overall_soundscape`, and
  `non_diegetic_music` when full reference control is needed.

## Sources

- Reddit post supplied by the user:
  `https://www.reddit.com/r/StableDiffusion/comments/1vkfb49/longform_videos_1_min_long_are_very_possible_with/`
- Scene/prompt example: `https://pastebin.com/ig2G0KU9`
- Author workflows: `https://huggingface.co/comfyuiman/various/tree/main`
- Context-loop fork: `https://github.com/ethanfel/ComfyUI-MiniMaxH3-Contex-Loop`
- Original node: `https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context`
- LightX model: `https://huggingface.co/Kijai/MiniMax-H3_comfy`
- Native Ref2VA guide:
  `https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md`
