#!/usr/bin/env python3
"""Install, validate, start, and inspect the pinned MiniMax H3 context loop."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import Request, urlopen


ROOT = Path(r"C:\ComfyUI-H3")
SKILL = Path(__file__).resolve().parents[1]
NODE_DIR = ROOT / "custom_nodes" / "ComfyUI-MiniMaxH3-Contex-Loop"
NODE_REPO = "https://github.com/ethanfel/ComfyUI-MiniMaxH3-Contex-Loop.git"
NODE_COMMIT = "92f923feef7472be1ef78232c6eff156d5b993bc"
WORKFLOW = ROOT / "user" / "default" / "workflows" / "h3_context_loop_reddit_recipe.json"
WORKFLOW_ASSET = SKILL / "assets" / WORKFLOW.name
SOURCE_DIR = ROOT / "user" / "default" / "workflows" / "h3-context-loop-source"
SOURCE_WORKFLOWS = {
    "t1-original.json": "https://huggingface.co/comfyuiman/various/resolve/main/t1-original.json",
    "tnew.json": "https://huggingface.co/comfyuiman/various/resolve/main/tnew.json",
}
LORA = ROOT / "models" / "loras" / "minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors"
LORA_URL = "https://huggingface.co/Kijai/MiniMax-H3_comfy/resolve/main/loras/minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors"
LORA_SIZE = 1_956_171_984
LORA_SHA256 = "fc9b6500f0331fe925b004738baaa31bd34104741c8bf9334816f9ac3005c8c1"
H3_CONTROL = Path(r"C:\Users\Admin\.codex\skills\generate-local-video\scripts\h3_control.py")
URL = "http://127.0.0.1:8188"
RUNS = ROOT / "output" / "h3_chains"
REQUIRED_NODES = {
    "MiniMaxH3ChainPlan",
    "MiniMaxH3ChainLoopStart",
    "MiniMaxH3ChainCurrent",
    "MiniMaxH3ChainContext",
    "MiniMaxH3ChainSegmentSave",
    "MiniMaxH3ChainReview",
    "MiniMaxH3ChainLoopEnd",
    "MiniMaxH3ChainAssemble",
    "MiniMaxH3LoopTrim",
}
FORBIDDEN_WORKFLOW_NODES = {
    "PathchSageAttentionKJ",
    "MiniMaxH3MemoryEfficientSageAttentionPatch",
    "SolAttnPatch",
}


def api(path: str, timeout: float = 10.0):
    request = Request(URL + path, headers={"Accept": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], check=check, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )


def node_commit() -> str | None:
    if not (NODE_DIR / ".git").exists():
        return None
    result = git("-C", str(NODE_DIR), "rev-parse", "HEAD", check=False)
    return result.stdout.strip() if result.returncode == 0 else None


def validate_workflow() -> list[str]:
    errors: list[str] = []
    if not WORKFLOW.exists():
        return [f"missing workflow: {WORKFLOW}"]
    try:
        data = json.loads(WORKFLOW.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"invalid workflow JSON: {exc}"]
    node_list = data.get("nodes", [])
    nodes = {node.get("type"): node for node in node_list}
    missing = REQUIRED_NODES - set(nodes)
    forbidden = FORBIDDEN_WORKFLOW_NODES & set(nodes)
    if missing:
        errors.append("workflow missing nodes: " + ", ".join(sorted(missing)))
    if forbidden:
        errors.append("workflow contains disabled compatibility nodes: " + ", ".join(sorted(forbidden)))
    plan = nodes.get("MiniMaxH3ChainPlan", {}).get("widgets_values", [])
    expected = {5: 22, 6: "video", 7: "head", 8: "disabled", 9: "generated_audio", 10: 22, 12: 6}
    for index, value in expected.items():
        if len(plan) <= index or plan[index] != value:
            errors.append(f"Plan widget {index} expected {value!r}")
    lora = nodes.get("LoraLoaderModelOnly", {}).get("widgets_values", [])
    if len(lora) < 2 or lora[0] != LORA.name or float(lora[1]) != 0.8:
        errors.append("workflow LightX selection/strength does not match the recipe")
    expected_models = {
        "UNETLoader": "minimax_h3_fl2va_pruned_int8_convrot.safetensors",
        "CLIPLoader": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
        "KSamplerSelect": "euler",
    }
    for node_type, expected_name in expected_models.items():
        values = nodes.get(node_type, {}).get("widgets_values", [])
        if not isinstance(values, list) or not values or values[0] != expected_name:
            errors.append(f"{node_type} expected {expected_name}")
    vaes = {
        values[0]
        for node in node_list
        if node.get("type") == "VAELoader"
        and isinstance((values := node.get("widgets_values", [])), list)
        and values
    }
    expected_vaes = {
        "minimax_h3_video_vae_fp16.safetensors",
        "minimax_h3_audio_vae_fp32.safetensors",
    }
    if vaes != expected_vaes:
        errors.append("workflow VAE selections do not match the verified local models")
    return errors


def doctor(_args) -> int:
    errors: list[str] = []
    if node_commit() != NODE_COMMIT:
        errors.append(f"context-loop commit is {node_commit() or 'missing'}, expected {NODE_COMMIT}")
    if not LORA.exists():
        errors.append(f"missing LightX LoRA: {LORA}")
    else:
        if LORA.stat().st_size != LORA_SIZE:
            errors.append(f"LightX size is {LORA.stat().st_size}, expected {LORA_SIZE}")
        elif sha256_file(LORA) != LORA_SHA256:
            errors.append("LightX SHA-256 mismatch")
    errors.extend(validate_workflow())
    for name in SOURCE_WORKFLOWS:
        if not (SOURCE_DIR / name).exists():
            errors.append(f"missing archived source workflow: {name}")
    try:
        object_info = api("/object_info")
    except (OSError, URLError, ValueError):
        server = "stopped"
    else:
        server = "ready"
        missing_nodes = REQUIRED_NODES - set(object_info)
        if missing_nodes:
            errors.append("running server has not loaded: " + ", ".join(sorted(missing_nodes)))
    sage = "available" if importlib.util.find_spec("sageattention") else "native-attention"
    if errors:
        print("DOCTOR_FAIL")
        for error in errors:
            print(f"error: {error}")
        print(f"server={server} attention={sage}")
        return 1
    print(f"DOCTOR_OK commit={NODE_COMMIT[:12]} lora_sha256={LORA_SHA256[:12]} server={server} attention={sage}")
    print(f"workflow={WORKFLOW}")
    return 0


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".download")
    request = Request(url, headers={"User-Agent": "Codex H3 Context Loop"})
    with urlopen(request, timeout=60) as response, temporary.open("wb") as output:
        total = int(response.headers.get("Content-Length", "0"))
        copied = 0
        last_report = 0
        while True:
            chunk = response.read(8 * 1024 * 1024)
            if not chunk:
                break
            output.write(chunk)
            copied += len(chunk)
            if total and copied - last_report >= 256 * 1024 * 1024:
                print(f"download {destination.name}: {copied * 100 // total}%")
                last_report = copied
    os.replace(temporary, destination)


def repair(_args) -> int:
    if not NODE_DIR.exists():
        git("clone", NODE_REPO, str(NODE_DIR))
    if node_commit() != NODE_COMMIT:
        dirty = git("-C", str(NODE_DIR), "status", "--porcelain").stdout.strip()
        if dirty:
            print(f"REPAIR_FAIL custom node has local changes: {NODE_DIR}")
            return 1
        git("-C", str(NODE_DIR), "fetch", "origin", NODE_COMMIT)
        git("-C", str(NODE_DIR), "checkout", "--detach", NODE_COMMIT)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in SOURCE_WORKFLOWS.items():
        path = SOURCE_DIR / name
        if not path.exists() or path.stat().st_size == 0:
            download(url, path)
    if not LORA.exists() or LORA.stat().st_size != LORA_SIZE or sha256_file(LORA) != LORA_SHA256:
        download(LORA_URL, LORA)
        if LORA.stat().st_size != LORA_SIZE or sha256_file(LORA) != LORA_SHA256:
            print("REPAIR_FAIL downloaded LightX file failed integrity validation")
            return 1
    if not WORKFLOW_ASSET.exists():
        print(f"REPAIR_FAIL missing bundled workflow: {WORKFLOW_ASSET}")
        return 1
    if not WORKFLOW.exists() or validate_workflow():
        WORKFLOW.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(WORKFLOW_ASSET, WORKFLOW)
    print("REPAIR_OK restart ComfyUI if the custom node was installed or changed")
    return doctor(_args)


def start(args) -> int:
    command = [sys.executable, str(H3_CONTROL), "start", "--timeout", str(args.timeout)]
    result = subprocess.run(command)
    if result.returncode not in (0, 2):
        return result.returncode
    try:
        object_info = api("/object_info", timeout=30)
    except (OSError, URLError, ValueError) as exc:
        print(f"NODE_CHECK_FAIL {exc}")
        return 1
    missing = REQUIRED_NODES - set(object_info)
    if missing:
        print("NODE_CHECK_FAIL restart ComfyUI to load: " + ", ".join(sorted(missing)))
        return 1
    print(f"CONTEXT_LOOP_READY workflow={WORKFLOW}")
    return 0


def status(_args) -> int:
    try:
        queue = api("/queue")
    except (OSError, URLError, ValueError) as exc:
        print(f"SERVER_STOPPED {exc}")
        return 1
    print(f"QUEUE running={len(queue.get('queue_running', []))} pending={len(queue.get('queue_pending', []))}")
    if RUNS.exists():
        runs = sorted((p for p in RUNS.iterdir() if p.is_dir()), key=lambda p: p.stat().st_mtime, reverse=True)
        for run in runs[:5]:
            checkpoints = len(list((run / "checkpoints").glob("*"))) if (run / "checkpoints").exists() else 0
            finals = len(list((run / "final").glob("*.mp4"))) if (run / "final").exists() else 0
            print(f"RUN {run.name} checkpoints={checkpoints} finals={finals}")
    return 0


def outputs(args) -> int:
    if not RUNS.exists():
        return 1
    files = sorted(RUNS.rglob("*.mp4"), key=lambda path: path.stat().st_mtime, reverse=True)[: args.limit]
    for path in files:
        stat = path.stat()
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))}\t{stat.st_size}\t{path}")
    return 0 if files else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, function in (("doctor", doctor), ("repair", repair), ("status", status)):
        command = sub.add_parser(name)
        command.set_defaults(function=function)
    command = sub.add_parser("start")
    command.add_argument("--timeout", type=int, default=180)
    command.set_defaults(function=start)
    command = sub.add_parser("outputs")
    command.add_argument("--limit", type=int, default=10)
    command.set_defaults(function=outputs)
    args = parser.parse_args()
    return args.function(args)


if __name__ == "__main__":
    raise SystemExit(main())
