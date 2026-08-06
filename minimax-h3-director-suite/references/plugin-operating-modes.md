# Local plugin operating modes

## Installed targets

| Component | Local directory | Required API node IDs | Role |
| --- | --- | --- | --- |
| MiniMax H3 Director | `C:\Users\Admin\ComfyUI\custom_nodes\ComfyUI-MiniMaxH3-Director` | `MiniMaxH3DirectorCS`, `MiniMaxH3PreviewOverrideCS`, `MiniMaxH3RetakeStitchCS`, `MiniMaxH3EnhancePromptCS` | H3 timeline, preview, retake, prompt helper |
| Spectrum MiniMax H3 | `C:\Users\Admin\ComfyUI\custom_nodes\ComfyUI-Spectrum-MiniMax-H3` | `SpectrumApplyMiniMaxH3` | Optional H3 feature forecasting |
| ComfyUI-nunchaku | `C:\Users\Admin\ComfyUI\custom_nodes\ComfyUI-nunchaku` | `NunchakuWheelInstaller` | Separate low-bit image-model runtime; not H3 |

## Director graph wiring

The Director outputs a patched H3 `model`, compiled `positive` conditioning, joint AV `latent`, `combined_audio`, `fps`, `width`, `height`, `length`, a compiled `prompt`, and `retake_info`.

Use this order for an experimental Spectrum workflow:

```text
H3 model loader -> MiniMax H3 Director -> Spectrum Apply MiniMax H3 -> Preview Override -> guider/sampler
```

Wire Director `positive` and `latent` to the corresponding H3 guider/sampler inputs. Use its output dimensions, frame length, and fps for decode/video creation. Preview Override attaches a non-destructive sample wrapper to the model; use `latent2rgb (fast)` routinely and VAE decoding only for a detail check.

Director snaps output length to H3's `17k+5` frame grid and warns past its approximately 4–15 second trained window. Split longer stories into series chapters. The withdrawn Director Chain node is deliberately not registered; do not plan around it.

Director timeline audio is a mixdown/reference feature, not an exact-audio preservation mechanism. Exact song workflows remain on the `MiniMaxH3NativeAudioLock` graph.

## Spectrum decision table

| Situation | Action |
| --- | --- |
| First production take, terminal continuation frame, or delicate face/hand action | Use native sampling. |
| Need a faster candidate and can afford a native control | A/B Spectrum with its conservative preset. |
| Euler, RES multistep, or RES multistep CFG++ | Eligible for forecasting after all guardrails pass. |
| Ancestral, unsupported, multi-GPU, or topology-changing setup | Expect native fallback; do not use as an acceleration result. |
| RAM constrained | Lower the rendering load or use native; keep `max_history >= degree + 1`. |
| Plenty of measured generation-peak VRAM | Test `vram` history separately; compare wall time and peak VRAM, not a theoretical reduction. |

The conservative 20-step configuration schedules some actual H3 evaluations and some forecasted solver steps. Its output is not guaranteed to be identical to native sampling. Compare decoded motion, details, sound, duration, and the continuation frame—not only completion time.

## Nunchaku boundary

Nunchaku currently targets low-bit FLUX, Qwen Image, and Z-Image workflows. It has no MiniMax H3 model wrapper. The local H3 runtime uses Python 3.13, CUDA 13.0, and Torch 2.13; the published Nunchaku wheels do not match Torch 2.13. Installing a different binary wheel or dependency stack in this environment can compromise the working H3 deployment.

Leave Nunchaku's backend uninstalled here. Consider it only in a user-approved isolated environment for a supported non-H3 workflow.
