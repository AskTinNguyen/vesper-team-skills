# Official MiniMax H3 workflow notes

Use this reference when choosing generation mode, duration, or resolution. Read [minimax-h3-official-prompt-contract.md](minimax-h3-official-prompt-contract.md) separately for prompt grammar.

## Local modes

- **T2VA**: text-only generation. Use only for a first standalone chapter with no keyframe.
- **I2VA**: one first frame drives a video with native stereo audio. Use this for ordinary continuation chapters.
- **FL2VA**: first and last frames constrain both endpoints. Supply `last_frame` only when the terminal composition is known and plausibly reachable.
- **L2VA**: one last frame anchors the ending. Use only for a first standalone/prequel chapter that must converge on a known image.
- **R2VA**: references use a different Ref2VA model and graph. Use `$minimax-h3-native-audio-music-video` for locked-source music videos.

The local `MiniMaxH3ImageToVideo` node accepts optional first and last frames, so all four base modes are available. The supervised series pipeline restricts T2VA and L2VA to the first chapter because later chapters normally inherit an accepted continuation frame.

## Duration and frame grid

MiniMax H3 runs at 24 fps and uses `17k+5` frames. The documented trained range is 124 through 362 frames, approximately 5.17 through 15.08 seconds. Longer output is experimental and can increase memory use, drift, and failure risk.

Use `duration_seconds` in new configs. The helper rounds upward to the next valid temporal-grid length and uses the effective generated duration in keyframe-alignment instructions. It rejects untrained lengths unless `allow_untrained_length` is explicitly enabled.

## Resolution presets

All dimensions are multiples of 32. `preview` preserves the proven local baseline; `production` costs substantially more VRAM and render time.

| Aspect | Preview | Production |
|-|-:|-:|
| 16:9 | 960 x 544 | 1344 x 768 |
| 9:16 | 544 x 960 | 768 x 1344 |
| 1:1 | 736 x 736 | 1024 x 1024 |
| 4:5 | 640 x 800 | 768 x 960 |
| 5:4 | 800 x 640 | 960 x 768 |

Benchmark production resolutions with the same seed, prompt, length, sampler, and steps. Do not assume a larger canvas automatically improves composition or identity.

## Optional acceleration

Sage Attention can improve speed on a compatible build, but its wheel must match the installed PyTorch and CUDA versions. Benchmark it against the same deterministic case before adopting it. Do not alter the known-working environment merely because the option exists.
