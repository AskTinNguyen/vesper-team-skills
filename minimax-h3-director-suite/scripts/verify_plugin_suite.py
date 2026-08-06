#!/usr/bin/env python3
"""Probe the local ComfyUI API for the MiniMax H3 Director plugin suite."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


DIRECTOR_NODES = (
    "MiniMaxH3DirectorCS",
    "MiniMaxH3PreviewOverrideCS",
    "MiniMaxH3RetakeStitchCS",
    "MiniMaxH3EnhancePromptCS",
)
SPECTRUM_NODE = "SpectrumApplyMiniMaxH3"
NUNCHAKU_NODE = "NunchakuWheelInstaller"
PLUGIN_DIRS = {
    "director": "ComfyUI-MiniMaxH3-Director",
    "spectrum": "ComfyUI-Spectrum-MiniMax-H3",
    "nunchaku": "ComfyUI-nunchaku",
}


def get_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=8) as response:
        return json.load(response)


def package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api", default="http://127.0.0.1:8188", help="ComfyUI API base URL")
    parser.add_argument("--comfy-root", default=r"C:\Users\Admin\ComfyUI", help="ComfyUI installation root")
    parser.add_argument("--strict", action="store_true", help="Fail unless Director and Spectrum nodes are live")
    parser.add_argument("--json", action="store_true", help="Print structured JSON")
    args = parser.parse_args()

    custom_nodes = Path(args.comfy_root) / "custom_nodes"
    report: dict[str, object] = {
        "api": args.api.rstrip("/"),
        "directories": {key: (custom_nodes / name).is_dir() for key, name in PLUGIN_DIRS.items()},
        "api_reachable": False,
        "director_nodes": {},
        "spectrum_node": False,
        "nunchaku_installer_node": False,
        "nunchaku_backend_version": package_version("nunchaku"),
        "nunchaku_h3_compatible": False,
    }
    try:
        object_info = get_json(f"{report['api']}/object_info")
        report["api_reachable"] = True
        report["director_nodes"] = {name: name in object_info for name in DIRECTOR_NODES}
        report["spectrum_node"] = SPECTRUM_NODE in object_info
        report["nunchaku_installer_node"] = NUNCHAKU_NODE in object_info
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        report["api_error"] = str(exc)

    director_live = report["api_reachable"] and all(report["director_nodes"].values())
    spectrum_live = bool(report["api_reachable"] and report["spectrum_node"])
    report["director_live"] = director_live
    report["spectrum_live"] = spectrum_live

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"ComfyUI API: {'reachable' if report['api_reachable'] else 'unreachable'} ({report['api']})")
        print(f"Director: {'ready' if director_live else 'restart or inspect required'}")
        print(f"Spectrum: {'ready' if spectrum_live else 'restart or inspect required'}")
        nunchaku = report["nunchaku_backend_version"] or "not installed (expected for H3)"
        print(f"Nunchaku backend: {nunchaku}; not applicable to MiniMax H3")

    if args.strict and not (director_live and spectrum_live):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
