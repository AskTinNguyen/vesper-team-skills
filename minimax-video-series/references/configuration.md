# Configuration reference

## Contents

1. Config structure
2. Prompt structure
3. Chapter design
4. Runtime defaults
5. Resume semantics

## Config structure

Start from `assets/series.example.json`. Required top-level objects are:

- `series`: title, slug, output subdirectory, and manifest name.
- `runtime`: ComfyUI URL/root, duration/aspect/quality or explicit dimensions/length, 24 fps, and steps.
- `models`: ComfyUI-relative UNet, text encoder, video VAE, and audio VAE names.
- `style_lock`: global identity, visual language, framing, anatomy, and targeted exclusions.
- `initial_frame`: first image for I2VA/FL2VA, inside ComfyUI `input`. T2VA/L2VA first chapters do not use it.
- `speakers`: optional stable `(S1)`, `(S2)`, ... identity and voice registry.
- `chapters`: ordered chapter objects.
- `archive`: optional site source, public media path, URL, and file limit.

Chapter numbers must be unique and ascending. Titles determine safe output slugs. Seeds must be integers and remain stable across prompt-only retries.

## Prompt structure

Legacy chapters may use one raw visible-action prompt:

```json
{
  "number": 1,
  "title": "The Opening",
  "movement": "Act I",
  "mode": "i2va",
  "prompt": "One principal visible action and an explicit end tableau.",
  "audio_prompt": "Specific ambience continues while no dialogue is audible.",
  "music_prompt": "N/A",
  "transition": "foreground object wipe",
  "seed": 2026080401
}
```

Prefer structured shots when timing, camera, speech, singing, voiceover, or visible text matters:

```json
{
  "number": 2,
  "title": "The Answer",
  "movement": "Act I",
  "mode": "fl2va",
  "last_frame": "desired-ending.png",
  "shots": [
    {
      "action": "The young woman raises the folded letter toward the window.",
      "camera": {
        "type": "Truck Right",
        "amplitude": "small",
        "speed": "slow",
        "target_phrase": "along the rain-covered glass"
      },
      "speech": [
        {
          "speaker_id": "S1",
          "kind": "dialogue",
          "language": "English",
          "text": "I get off at the next station."
        }
      ],
      "on_screen_text": ["营业中"]
    }
  ],
  "audio_prompt": "Train wheels produce a steady metallic rhythm while rain taps against the window.",
  "music_prompt": "Sparse piano notes at a slow tempo alternate with sustained low strings.",
  "seed": 2026080402
}
```

Define each vocalizing subject once:

```json
{
  "speakers": {
    "S1": {
      "description": "The young woman beside the train window",
      "voice": "a quiet, breathy voice with a measured speaking rate"
    }
  }
}
```

Mode defaults to FL2VA when `last_frame` exists and I2VA otherwise. Set it explicitly for clarity. T2VA and L2VA are limited to the first standalone/prequel chapter; L2VA requires `last_frame`. Every supplied frame is hashed when queued and checked again at acceptance.

Shot 1 must not contain `cut_at`. Every later shot requires a strictly increasing numeric `cut_at` below the effective snapped duration and an approved cut phrase. A cross-dissolve, fade, or wipe also requires `user_requested_transition: true`. Camera objects use a supported `type`, optional `small`/`large` amplitude, optional `slow`/`fast` speed, and optional natural-language `target_phrase`.

Speech `text` and `on_screen_text` are exact data. Never translate, normalize punctuation, or silently correct them. For speech crossing a cut, set `scene_transition` to `out` on the first fragment and `in` on the adjacent fragment for the same speaker. Set `cutoff: true` only when the video intentionally truncates an utterance.

Write `audio_prompt` as 1-4 complete sentences containing ambience, action sounds, and non-verbal human sounds. Write `music_prompt` as `N/A` or 1-3 complete sentences containing instrumentation, tempo, rhythm, and dynamics. See `minimax-h3-official-prompt-contract.md` for exact semantics.

## Chapter design

Treat each 5-15-second chapter as one cinematic sentence. For exact continuation:

1. Preserve the input composition for roughly the first second.
2. Begin motion from an element already visible.
3. Perform one readable action.
4. Motivate the transition from the scene.
5. Land on a simple stable frame with an obvious next-shot affordance.

Useful endpoints include full-frame bark, darkness, flare, eye, reflection, portal, seed, leaf, doorway, held wide, or a centered object. Avoid mid-morph anatomy, rapid camera motion, crowded faces, and unresolved occlusion.

## Runtime defaults

Prefer:

```json
{
  "duration_seconds": 15,
  "aspect_ratio": "4:5",
  "quality": "preview",
  "fps": 24,
  "steps": 20
}
```

The normalizer derives 640 x 800 and 362 frames. Legacy explicit dimensions remain valid when they are multiples of 32 and length follows `17k+5`.

Known local names:

- UNet: `minimax_h3_fl2va_pruned_int8_convrot.safetensors`
- Text encoder: `MiniMax-H3\qwen3vl_32b_minimax_h3_ultra_uncensored_heretic_int8_convrot.safetensors`
- Video VAE: `minimax_h3_video_vae_fp16.safetensors`
- Audio VAE: `minimax_h3_audio_vae_fp32.safetensors`
- Sampler: `res_multistep`
- Scheduler: `simple`

## Resume semantics

The manifest is authoritative. A chapter is `pending_review`, `accepted`, or `rejected`. Every render appends an attempt. Accept extracts the configured continuation frame; reject preserves the attempt under `rejects/`.

For a legacy boundary, run `bootstrap`. It records the source video, decoded frame index, initial image, and SHA-256 provenance. If config and manifest disagree, stop and reconcile explicitly; never renumber accepted history or substitute a different output silently.
