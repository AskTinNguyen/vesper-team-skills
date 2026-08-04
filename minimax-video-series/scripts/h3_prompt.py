from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


FPS = 24
MIN_TRAINED_FRAMES = 124
MAX_TRAINED_FRAMES = 362

RESOLUTION_PRESETS = {
    "preview": {
        "16:9": (960, 544), "9:16": (544, 960), "1:1": (736, 736),
        "4:5": (640, 800), "5:4": (800, 640),
    },
    "production": {
        "16:9": (1344, 768), "9:16": (768, 1344), "1:1": (1024, 1024),
        "4:5": (768, 960), "5:4": (960, 768),
    },
}


def snap_frames(duration_seconds: float, fps: int = FPS) -> int:
    """Round duration up to the MiniMax H3 temporal grid: 17k + 5 frames."""
    if duration_seconds <= 0:
        raise ValueError("duration_seconds must be positive")
    return 17 * max(0, math.ceil((duration_seconds * fps - 5) / 17)) + 5


def is_temporal_grid(length: int) -> bool:
    return length >= 5 and (length - 5) % 17 == 0


def normalize_runtime(runtime: dict) -> dict:
    result = dict(runtime)
    fps = int(result.get("fps", FPS))
    if fps != FPS:
        raise ValueError("MiniMax H3 local workflows are fixed at 24 fps")
    result["fps"] = FPS

    quality = str(result.get("quality", "preview")).lower()
    aspect = str(result.get("aspect_ratio", "4:5"))
    if "width" not in result or "height" not in result:
        if quality not in RESOLUTION_PRESETS:
            raise ValueError(f"Unknown quality preset: {quality}")
        if aspect not in RESOLUTION_PRESETS[quality]:
            raise ValueError(f"Unknown aspect ratio for {quality}: {aspect}")
        result["width"], result["height"] = RESOLUTION_PRESETS[quality][aspect]
    width, height = int(result["width"]), int(result["height"])
    if width <= 0 or height <= 0 or width % 32 or height % 32:
        raise ValueError("width and height must be positive multiples of 32")
    result.update({"width": width, "height": height, "quality": quality, "aspect_ratio": aspect})

    if "duration_seconds" in result:
        derived = snap_frames(float(result["duration_seconds"]), fps)
        if "length" in result and int(result["length"]) != derived:
            raise ValueError(
                f"length={result['length']} conflicts with duration_seconds; expected {derived} frames"
            )
        result["length"] = derived
    elif "length" not in result:
        result["length"] = MAX_TRAINED_FRAMES

    length = int(result["length"])
    if not is_temporal_grid(length):
        raise ValueError(f"length={length} is invalid; MiniMax H3 requires 17k+5 frames")
    if not result.get("allow_untrained_length") and not MIN_TRAINED_FRAMES <= length <= MAX_TRAINED_FRAMES:
        raise ValueError(
            f"length={length} is outside the documented trained range "
            f"{MIN_TRAINED_FRAMES}-{MAX_TRAINED_FRAMES}; set allow_untrained_length only for an experiment"
        )
    result["length"] = length
    result["duration_seconds"] = length / fps
    return result


def _shot_description(style_lock: str, item: dict, has_last_frame: bool) -> str:
    transition = item.get("transition", "clean held tableau")
    final_reference = (
        " Finish in the exact composition of <Picture 2>; use it as the terminal visual constraint."
        if has_last_frame else
        " Settle into the requested terminal tableau and hold nearly still for the final 12 to 15 frames."
    )
    return (
        f"[Shot 1] Chapter {int(item['number']):03d}, {item['title']}. {style_lock} "
        f"Movement: {item.get('movement', 'Sequence')}. {item['prompt']} "
        f"Transition language: {transition}; treat it as motivated in-shot direction, not an accidental hard cut."
        f"{final_reference}"
    )


def compile_i2va_prompt(style_lock: str, item: dict) -> str:
    return (
        "For the target video, at 0.00 seconds into the target video, "
        "<Picture 1> (from [Shot 1]) is fully referenced.\n\n"
        f"integrated_multimodal_description: {_shot_description(style_lock, item, False)}\n\n"
        f"overall_soundscape: {item.get('audio_prompt', 'restrained native stereo ambience, no intelligible dialogue')}\n\n"
        f"non_diegetic_music: {item.get('music_prompt', 'N/A')}"
    )


def compile_fl2va_prompt(style_lock: str, item: dict, duration_seconds: float) -> str:
    return (
        "For the target video, at 0.00 seconds into the target video, "
        "<Picture 1> (from [Shot 1]) is fully referenced. "
        f"At {duration_seconds:.2f} seconds into the target video, "
        "<Picture 2> (from [Shot 1]) is fully referenced.\n\n"
        f"integrated_multimodal_description: {_shot_description(style_lock, item, True)}\n\n"
        f"overall_soundscape: {item.get('audio_prompt', 'restrained native stereo ambience, no intelligible dialogue')}\n\n"
        f"non_diegetic_music: {item.get('music_prompt', 'N/A')}"
    )


def compile_chapter_prompt(config: dict, item: dict) -> str:
    runtime = normalize_runtime(config["runtime"])
    if item.get("last_frame"):
        return compile_fl2va_prompt(config["style_lock"], item, runtime["duration_seconds"])
    return compile_i2va_prompt(config["style_lock"], item)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MiniMax H3 runtime and official prompt helper")
    sub = parser.add_subparsers(dest="command", required=True)
    profile = sub.add_parser("profile", help="resolve duration and resolution settings")
    profile.add_argument("--duration", type=float, required=True)
    profile.add_argument("--aspect", choices=("16:9", "9:16", "1:1", "4:5", "5:4"), required=True)
    profile.add_argument("--quality", choices=tuple(RESOLUTION_PRESETS), default="preview")
    compile_parser = sub.add_parser("compile", help="show the exact prompt sent to ComfyUI")
    compile_parser.add_argument("--config", type=Path, required=True)
    compile_parser.add_argument("--chapter", type=int, required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "profile":
        result = normalize_runtime({
            "duration_seconds": args.duration, "aspect_ratio": args.aspect,
            "quality": args.quality, "fps": FPS,
        })
        print(json.dumps(result, indent=2))
        return
    config = json.loads(args.config.read_text(encoding="utf-8-sig"))
    try:
        item = next(value for value in config["chapters"] if int(value["number"]) == args.chapter)
    except StopIteration as exc:
        raise SystemExit(f"Chapter {args.chapter} is not present in {args.config}") from exc
    print(compile_chapter_prompt(config, item))


if __name__ == "__main__":
    main()
