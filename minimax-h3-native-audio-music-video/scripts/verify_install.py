from __future__ import annotations

import argparse
import json
import subprocess
import urllib.request
from pathlib import Path


PRIMARY_NODES = {
    "MiniMaxH3ReferenceToVideo",
    "MiniMaxH3NativeAudioLock",
    "LoadAudio",
    "TrimAudioDuration",
    "SamplerCustomAdvanced",
    "CreateVideo",
    "SaveVideo",
}
RIFE_NODES = {"LoadVideo", "GetVideoComponents", "RIFE VFI", "CreateVideo", "SaveVideo"}


def request_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify the MiniMax H3 native-audio music-video installation")
    parser.add_argument("--comfy-root", type=Path, default=Path(r"C:\Users\Admin\ComfyUI"))
    parser.add_argument("--comfy-url", default="http://127.0.0.1:8188")
    args = parser.parse_args()
    root = args.comfy_root.resolve()
    skill_root = Path(__file__).resolve().parents[1]
    required = {
        "prompt_compiler": skill_root / "scripts" / "native_audio_prompt.py",
        "prompt_example": skill_root / "assets" / "music-video.example.json",
        "audio_lock": root / "custom_nodes" / "ComfyUI-H3-NativeAudioLock" / "__init__.py",
        "music_workflow": root / "user" / "default" / "workflows" / "MiniMaxH3_NativeAudio_MusicVideo_TEMPLATE.json",
        "rife_workflow": root / "user" / "default" / "workflows" / "RIFE_WAN_Method_Interpolation_TEMPLATE.json",
        "rife_extension": root / "custom_nodes" / "ComfyUI-Frame-Interpolation" / "__init__.py",
        "rife47": root / "custom_nodes" / "ComfyUI-Frame-Interpolation" / "ckpts" / "rife" / "rife47.pth",
        "ref2va": root / "models" / "diffusion_models" / "minimax_h3_ref2va_pruned_int8_convrot.safetensors",
        "video_vae": root / "models" / "vae" / "minimax_h3_video_vae_fp16.safetensors",
        "audio_vae": root / "models" / "vae" / "minimax_h3_audio_vae_fp32.safetensors",
        "heretic_encoder": root / "models" / "text_encoders" / "MiniMax-H3" / "qwen3vl_32b_minimax_h3_ultra_uncensored_heretic_int8_convrot.safetensors",
    }
    failures = []
    for name, path in required.items():
        if path.exists() and path.stat().st_size > 0:
            print(f"OK file {name}: {path} ({path.stat().st_size} bytes)")
        else:
            failures.append(f"missing {name}: {path}")

    for workflow_name, required_nodes in (("music_workflow", PRIMARY_NODES), ("rife_workflow", RIFE_NODES)):
        path = required[workflow_name]
        if not path.exists():
            continue
        workflow = json.loads(path.read_text(encoding="utf-8-sig"))
        types = {node.get("type") for node in workflow.get("nodes", [])}
        missing = required_nodes - types
        if missing:
            failures.append(f"{workflow_name} omits nodes: {sorted(missing)}")
        else:
            print(f"OK workflow {workflow_name}: {len(workflow.get('nodes', []))} nodes")
        if workflow_name == "music_workflow":
            unet = next((node for node in workflow.get("nodes", []) if node.get("type") == "UNETLoader"), {})
            clip = next((node for node in workflow.get("nodes", []) if node.get("type") == "CLIPLoader"), {})
            if not unet.get("widgets_values") or unet["widgets_values"][0] != "minimax_h3_ref2va_pruned_int8_convrot.safetensors":
                failures.append("music workflow is not configured for the Ref2VA INT8 model")
            if not clip.get("widgets_values") or "heretic_int8_convrot" not in clip["widgets_values"][0]:
                failures.append("music workflow is not configured for the installed Heretic MiniMax encoder")
            prompt = next((node for node in workflow.get("nodes", []) if node.get("type") == "PrimitiveStringMultiline"), {})
            prompt_text = str((prompt.get("widgets_values") or [""])[0])
            for field in (
                "integrated_multimodal_description:",
                "overall_soundscape:",
                "non_diegetic_music:",
            ):
                if field not in prompt_text:
                    failures.append(f"music workflow prompt template omits {field}")
        if workflow_name == "rife_workflow":
            rife = next((node for node in workflow.get("nodes", []) if node.get("type") == "RIFE VFI"), {})
            if not rife.get("widgets_values") or rife["widgets_values"][0] != "rife47.pth":
                failures.append("RIFE workflow is not configured for rife47.pth")

    python = root / ".venv" / "Scripts" / "python.exe"
    if python.exists():
        check = subprocess.run(
            [str(python), "-c", "import torch, torchaudio, cv2; print(torch.__version__, torchaudio.__version__, cv2.__version__)"],
            capture_output=True,
            text=True,
        )
        if check.returncode:
            failures.append("ComfyUI venv dependency import failed: " + check.stderr.strip())
        else:
            print("OK venv dependencies:", check.stdout.strip())
    else:
        failures.append(f"missing ComfyUI Python: {python}")

    try:
        object_info = request_json(args.comfy_url.rstrip("/") + "/object_info")
        missing_runtime = (PRIMARY_NODES | RIFE_NODES) - set(object_info)
        if missing_runtime:
            failures.append("running ComfyUI is missing nodes (restart may be required): " + ", ".join(sorted(missing_runtime)))
        else:
            print("OK ComfyUI runtime nodes")
    except Exception as exc:
        failures.append(f"ComfyUI API unavailable: {exc}")

    if failures:
        print("\nFAIL")
        for failure in failures:
            print("-", failure)
        raise SystemExit(1)
    print("\nPASS: MiniMax H3 native-audio music-video suite is ready")


if __name__ == "__main__":
    main()
