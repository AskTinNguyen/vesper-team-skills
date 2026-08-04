from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path


def load_h3_prompt():
    candidates = [
        Path(__file__).resolve().parents[2] / "minimax-video-series" / "scripts",
        Path.home() / ".codex" / "skills" / "minimax-video-series" / "scripts",
    ]
    for candidate in candidates:
        if (candidate / "h3_prompt.py").exists():
            sys.path.insert(0, str(candidate))
            return importlib.import_module("h3_prompt")
    raise RuntimeError("Install $minimax-video-series with scripts/h3_prompt.py first")


H3 = load_h3_prompt()


def segment(config: dict, number: int) -> dict:
    for item in config["segments"]:
        if int(item["number"]) == number:
            return item
    raise ValueError(f"Segment {number} is not present")


def lint_segment(config: dict, item: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    performance = str(item.get("performance", "")).lower()
    if performance not in {"vocal", "instrumental"}:
        errors.append("performance must be vocal or instrumental")
    if performance == "vocal" and item.get("lyrics"):
        lyrics = item["lyrics"]
        if not isinstance(lyrics, dict) or not isinstance(lyrics.get("text"), str) or not lyrics.get("text"):
            errors.append("lyrics.text must contain exact verified lyrics")
        if str(item.get("speaker_id", "S1")) not in config.get("speakers", {}):
            errors.append("vocal speaker_id must exist in the stable speakers registry")
    role = str(item.get("music_role", "soundtrack")).lower()
    music = str(item.get("non_diegetic_music", item.get("music_prompt", "N/A"))).strip()
    if role not in {"soundtrack", "diegetic-performance"}:
        errors.append("music_role must be soundtrack or diegetic-performance")
    if role == "diegetic-performance" and music != "N/A":
        errors.append("diegetic-performance music belongs in the multimodal description; set non_diegetic_music to N/A")
    if role == "soundtrack" and music == "N/A":
        warnings.append("A supplied audience-only soundtrack should be described factually in non_diegetic_music")
    try:
        H3.compile_native_audio_prompt(config, item)
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(str(exc))
    return errors, warnings


def lint_config(config: dict, number: int | None = None) -> tuple[list[str], list[str]]:
    H3.normalize_runtime(config["runtime"])
    items = config["segments"]
    if number is not None:
        try:
            items = [segment(config, number)]
        except ValueError as exc:
            return [str(exc)], []
    errors: list[str] = []
    warnings: list[str] = []
    for item in items:
        item_errors, item_warnings = lint_segment(config, item)
        prefix = f"segment {int(item['number'])}: "
        errors.extend(prefix + value for value in item_errors)
        warnings.extend(prefix + value for value in item_warnings)
    return errors, warnings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compile official-grammar prompts for locked-audio MiniMax H3 videos")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("compile", "lint"):
        command = sub.add_parser(name)
        command.add_argument("--config", type=Path, required=True)
        command.add_argument("--segment", type=int, required=name == "compile")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8-sig"))
    if args.command == "lint":
        errors, warnings = lint_config(config, args.segment)
        for warning in warnings:
            print("WARNING:", warning)
        for error in errors:
            print("ERROR:", error)
        if errors:
            raise SystemExit(1)
        count = 1 if args.segment is not None else len(config["segments"])
        print(f"PASS: {count} NativeAudio segment prompt(s) valid")
        return
    item = segment(config, args.segment)
    errors, warnings = lint_segment(config, item)
    for warning in warnings:
        print("WARNING:", warning, file=sys.stderr)
    if errors:
        raise SystemExit("; ".join(errors))
    print(H3.compile_native_audio_prompt(config, item))


if __name__ == "__main__":
    main()
