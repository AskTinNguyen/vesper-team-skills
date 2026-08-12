#!/usr/bin/env python3
"""Control and inspect the verified local MiniMax H3 ComfyUI installation."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import Request, urlopen


ROOT = Path(r"C:\ComfyUI-H3")
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
URL = "http://127.0.0.1:8188"
LOG = ROOT / "user" / "skill-server.log"
WORKFLOWS = ROOT / "user" / "default" / "workflows"
OUTPUT = ROOT / "output"

REQUIRED = (
    ROOT / "models" / "diffusion_models" / "minimax_h3_fl2va_pruned_int8_convrot.safetensors",
    ROOT / "models" / "diffusion_models" / "minimax_h3_ref2va_pruned_int8_convrot.safetensors",
    ROOT / "models" / "text_encoders" / "MiniMax-H3" / "qwen3vl_32b_minimax_h3_ultra_uncensored_heretic_int8_convrot.safetensors",
    ROOT / "models" / "text_encoders" / "MiniMax-H3" / "qwen3vl_32b_minimax_h3_generation_tail_50_63_int8_convrot.safetensors",
    ROOT / "models" / "vae" / "minimax_h3_video_vae_fp16.safetensors",
    ROOT / "models" / "vae" / "minimax_h3_audio_vae_fp32.safetensors",
)


def api(path: str, timeout: float = 5.0):
    request = Request(URL + path, headers={"Accept": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)


def healthy() -> bool:
    try:
        api("/system_stats")
        return True
    except (OSError, URLError, ValueError):
        return False


def doctor(_args) -> int:
    missing = []
    for path in (ROOT, PYTHON, *REQUIRED):
        if not path.exists() or (path.is_file() and path.stat().st_size == 0):
            missing.append(str(path))
    workflows = list(WORKFLOWS.glob("video_minimax_h3_*.json")) if WORKFLOWS.exists() else []
    if len(workflows) < 3:
        missing.append(f"three prepared workflows under {WORKFLOWS}")
    if missing:
        print("DOCTOR_FAIL")
        for item in missing:
            print(f"missing: {item}")
        return 1
    total_gib = sum(path.stat().st_size for path in REQUIRED) / 1024**3
    print(f"DOCTOR_OK root={ROOT} model_gib={total_gib:.2f} workflows={len(workflows)} server={'ready' if healthy() else 'stopped'}")
    return 0


def start(args) -> int:
    if healthy():
        print(f"SERVER_READY {URL}")
        return 0
    LOG.parent.mkdir(parents=True, exist_ok=True)
    flags = 0
    if os.name == "nt":
        flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
    with LOG.open("ab", buffering=0) as log:
        process = subprocess.Popen(
            [str(PYTHON), "main.py", "--disable-auto-launch", "--listen", "127.0.0.1", "--port", "8188"],
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            creationflags=flags,
        )
    deadline = time.time() + args.timeout
    while time.time() < deadline:
        if healthy():
            print(f"SERVER_READY {URL} pid={process.pid} log={LOG}")
            return 0
        if process.poll() is not None:
            print(f"SERVER_FAILED exit={process.returncode} log={LOG}")
            return 1
        time.sleep(2)
    print(f"SERVER_STARTING pid={process.pid} log={LOG}")
    return 2


def status(_args) -> int:
    try:
        stats = api("/system_stats")
    except (OSError, URLError, ValueError) as exc:
        print(f"SERVER_STOPPED {exc}")
        return 1
    devices = stats.get("devices", [])
    device = devices[0] if devices else {}
    print(
        "SERVER_READY "
        f"url={URL} device={device.get('name', 'unknown')} "
        f"vram_free_gib={device.get('vram_free', 0) / 1024**3:.2f}"
    )
    return 0


def queue(_args) -> int:
    try:
        data = api("/queue")
    except (OSError, URLError, ValueError) as exc:
        print(f"QUEUE_UNAVAILABLE {exc}")
        return 1
    running = len(data.get("queue_running", []))
    pending = len(data.get("queue_pending", []))
    print(f"QUEUE running={running} pending={pending}")
    return 2 if running or pending else 0


def workflows(_args) -> int:
    files = sorted(WORKFLOWS.glob("video_minimax_h3_*.json"))
    for path in files:
        print(path)
    return 0 if files else 1


def video_outputs(limit: int):
    extensions = {".mp4", ".webm", ".mov", ".mkv"}
    if not OUTPUT.exists():
        return []
    files = (p for p in OUTPUT.rglob("*") if p.is_file() and p.suffix.lower() in extensions)
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[:limit]


def outputs(args) -> int:
    files = video_outputs(args.limit)
    for path in files:
        stat = path.stat()
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))}\t{stat.st_size}\t{path}")
    return 0 if files else 1


def logs(args) -> int:
    if not LOG.exists():
        print(f"No log at {LOG}")
        return 1
    lines = LOG.read_text(encoding="utf-8", errors="replace").splitlines()
    print("\n".join(lines[-args.tail :]))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, function in (("doctor", doctor), ("status", status), ("queue", queue), ("workflows", workflows)):
        command = sub.add_parser(name)
        command.set_defaults(function=function)
    command = sub.add_parser("start")
    command.add_argument("--timeout", type=int, default=180)
    command.set_defaults(function=start)
    command = sub.add_parser("outputs")
    command.add_argument("--limit", type=int, default=5)
    command.set_defaults(function=outputs)
    command = sub.add_parser("logs")
    command.add_argument("--tail", type=int, default=120)
    command.set_defaults(function=logs)
    args = parser.parse_args()
    return args.function(args)


if __name__ == "__main__":
    raise SystemExit(main())
