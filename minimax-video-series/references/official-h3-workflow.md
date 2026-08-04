# Official MiniMax H3 workflow notes

Use this reference when choosing the generation mode, compiling prompts, or changing duration and resolution.

## Local modes

- **I2V / I2VA**: one first frame drives a video with native stereo audio. This is the default for continuation chapters.
- **FL2V / FL2VA**: a first and last frame constrain both endpoints. Add `last_frame` to a chapter only when the terminal composition is already known.
- **T2V**: supported by the model, but this skill's supervised continuity pipeline is image-led.
- **R2V / R2VA**: reference-driven generation uses a different `ref2va` diffusion model. The official workflow supports up to 9 images, 3 videos with soundtracks, and 3 audio inputs. Do not point the installed FL2VA model at an R2V graph.

## Duration and frame grid

MiniMax H3 runs at 24 fps and uses a temporal grid of `17k + 5` frames. The documented trained range is 124 through 362 frames, approximately 5.17 through 15.08 seconds. Longer output is experimental and can increase memory use, drift, and failure risk.

Use `duration_seconds` in new configs. The helper rounds upward to the next valid temporal-grid length. It rejects out-of-range lengths unless `allow_untrained_length` is explicitly enabled for an experiment.

## Resolution presets

All dimensions are multiples of 32. `preview` preserves the proven 640 x 800 vertical baseline and is the default for iteration. `production` moves closer to the model's native 1344 x 768 landscape canvas and costs substantially more VRAM and render time.

| Aspect | Preview | Production |
|---|---:|---:|
| 16:9 | 960 x 544 | 1344 x 768 |
| 9:16 | 544 x 960 | 768 x 1344 |
| 1:1 | 736 x 736 | 1024 x 1024 |
| 4:5 | 640 x 800 | 768 x 960 |
| 5:4 | 800 x 640 | 960 x 768 |

Treat production resolutions as candidates to benchmark on this machine, not an automatic quality guarantee.

## Prompt contract

The compiler emits the official multimodal sections in this order:

1. time-aligned Picture reference instruction;
2. `integrated_multimodal_description`;
3. `overall_soundscape`;
4. `non_diegetic_music`.

The chapter's `prompt` should describe visible, chronological action. State camera motion as type plus optional amplitude and speed. Keep stable speaker IDs such as `(S1)` across shots, and wrap exact dialogue in the official `<d>[English] ...</d>` form when dialogue is genuinely required. Use strictly increasing timestamps if a chapter contains multiple timed shots.

For FL2VA, Picture 1 is aligned at 0.00 seconds and Picture 2 at the normalized clip duration. The terminal frame should still be visually compatible with the opening frame; endpoint conditioning cannot make an implausible transformation stable.

## Optional acceleration

Sage Attention can improve speed on a compatible build, but the wheel must match the installed PyTorch and CUDA versions. Benchmark it against the same seed, prompt, and dimensions before adopting it. Do not alter the known-working environment merely because the option exists.

Sources: the official ComfyUI MiniMax H3 tutorial and the MiniMax H3 base/reference prompt-writing guides.
