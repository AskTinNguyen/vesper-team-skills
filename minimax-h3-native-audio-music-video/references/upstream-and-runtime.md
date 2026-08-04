# Upstream and runtime reference

## Native-audio workflow

- Repository: `https://github.com/Shrek3OnVH5/MiniMax-H3-NativeAudio-MusicVideo-Workflow`
- Audited commit: `84895cfaaef39abb42fb844b02cb42f868c7bebf`
- Local source clone: `C:\Users\Admin\source\repos\MiniMax-H3-NativeAudio-MusicVideo-Workflow`
- The repository contains a ComfyUI node and two workflow templates, not an original Codex `SKILL.md`.
- The repository does not publish a license file. Keep its code/templates local unless redistribution rights are clarified.

The native-audio node imports Torch, TorchAudio, and ComfyUI internals. It does not execute subprocesses, read credentials, scan user files, or make network calls. It encodes the supplied waveform with the H3 audio VAE, pads/trims the audio latent to the target shape, applies a zero audio noise mask, and returns the supplied audio to the video mux.

## Frame interpolation

- Repository: `https://github.com/Fannovel16/ComfyUI-Frame-Interpolation`
- Installed commit: `26545cc2dd95bc3d27f056016300673bdeee78f5`
- Local clone: `C:\Users\Admin\ComfyUI\custom_nodes\ComfyUI-Frame-Interpolation`
- License: MIT in the upstream repository.
- Installed without CuPy. RIFE runs through Torch and does not require the optional CuPy operators.
- `opencv-contrib-python` is installed in `C:\Users\Admin\ComfyUI\.venv`.
- RIFE 4.7 downloads to `custom_nodes\ComfyUI-Frame-Interpolation\ckpts\rife\rife47.pth`.

## Model selection

The music workflow is Ref2VA, not FL2VA. Require:

- `minimax_h3_ref2va_pruned_int8_convrot.safetensors`
- `minimax_h3_video_vae_fp16.safetensors`
- `minimax_h3_audio_vae_fp32.safetensors`
- a compatible MiniMax Qwen3-VL encoder.

The upstream template named `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`. This installation deliberately reuses the existing Heretic INT8 MiniMax encoder to avoid a redundant 15.7 GB download. Do not replace the Ref2VA diffusion model with the existing FL2VA model.

## Timing and exact-audio invariants

- H3 accepts `17k+5` video-frame lengths. Render the next valid length, but accept only the exact musical-window frame count at 24 fps.
- The continuation reference is the final accepted frame, not the final padded render frame.
- Assemble silent accepted chapters first and mux the untouched full source song once. Per-chapter audio is conditioning and review material, not the final master soundtrack.
- Installed RIFE produces `(N-1)*m+1` frames. Pad `m-1` copies of the endpoint before temporal decimation so the interpolated master has exactly `N*m` frames.
- Define audio equality with a direct stream copy when the container supports it and a fixed-format decoded-PCM SHA-256 comparison. Never stretch the song to repair video timing.

## Update discipline

Before updating either upstream repository:

1. Record the current Git commit.
2. Preserve accepted video masters and workflow JSON.
3. Pull changes without rewriting local workflow copies.
4. Reinstall only newly required Python packages into the ComfyUI venv.
5. Restart ComfyUI and run `verify_install.py`.
6. Test one short disposable clip and one RIFE pair before production.
