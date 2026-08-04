# Configuration reference

## Contents

1. Config structure
2. Chapter design
3. Model and runtime defaults
4. Resume semantics

## Config structure

Start from `assets/series.example.json`. Paths may be absolute. `initial_frame` must resolve inside ComfyUI's `input` directory because `LoadImage` receives an input-relative filename.

Required top-level objects:

- `series`: title, slug, output subdirectory, manifest name.
- `runtime`: ComfyUI URL/root, width, height, length, fps, steps.
- `models`: ComfyUI-relative model names for UNet, text encoder, video VAE, and audio VAE.
- `style_lock`: global identity, visual language, framing, anatomy, and negative constraints.
- `initial_frame`: first image, relative to the ComfyUI input directory or absolute within it.
- `chapters`: ordered list of chapter objects.
- `archive`: current site source, public media subdirectory, public URL, and maximum file bytes.

Each chapter requires:

```json
{
  "number": 1,
  "title": "The Opening",
  "movement": "Act I",
  "prompt": "One principal visual action and an explicit end tableau.",
  "audio_prompt": "specific ambience, no dialogue",
  "transition": "foreground object wipe",
  "seed": 2026080401
}
```

Chapter numbers must be unique and ascending. Titles determine safe output slugs. Seeds must be integers and should remain stable across retries unless prompt-only corrections fail.

## Chapter design

The installed workflow produces 362 frames at 24 fps, approximately 15.083 seconds. Treat that as one cinematic sentence, not a complete scene. Put exposition in staging and image relationships rather than dialogue.

For exact continuation:

1. Preserve the input composition for roughly the first second.
2. Begin motion from an element already visible.
3. Perform one readable action.
4. Motivate the transition from the scene.
5. Land on a simple, stable last frame with an obvious next-shot affordance.

Useful end states include full-frame bark, darkness, flare, eye, reflection, portal, seed, leaf, doorway, held wide composition, or a centered object. Avoid ending on mid-morph anatomy, rapid camera motion, crowded faces, or an unresolved occlusion.

## Model and runtime defaults

Known working internal names:

- UNet: `minimax_h3_fl2va_pruned_int8_convrot.safetensors`
- Text encoder: `MiniMax-H3\\qwen3vl_32b_minimax_h3_ultra_uncensored_heretic_int8_convrot.safetensors`
- Video VAE: `minimax_h3_video_vae_fp16.safetensors`
- Audio VAE: `minimax_h3_audio_vae_fp32.safetensors`
- Sampler: `res_multistep`
- Scheduler: `simple`
- Output: native `CreateVideo` → `SaveVideo`

Do not rename or relocate models from the skill. Update config if the installation changes.

## Resume semantics

The output manifest is authoritative. A chapter state is one of:

- `pending_review`: rendered but not allowed to propagate;
- `accepted`: reviewed and eligible as the source for the next chapter;
- `rejected`: active take quarantined; chapter may be rendered again.

Every render appends an attempt. `accept` writes review notes and extracts the configured final frame into ComfyUI input for the next chapter. `reject` preserves the attempt under `rejects/` with a reason-bearing filename.

For a new config that begins after a legacy chapter, run `bootstrap`. It probes the source's actual decoded frame count, records an `upstream` object, and writes the exact source final frame to `initial_frame`. By default it requires `source_chapter == first_new_chapter - 1` and refuses an existing different target or upstream record. The verifier then audits the external legacy→new boundary as well as all internal accepted chains.

If config and manifest disagree, stop and reconcile explicitly. Do not silently renumber accepted chapters or substitute a different output file.
