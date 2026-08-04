from __future__ import annotations

import argparse
import copy
import json
import math
import re
from pathlib import Path


FPS = 24
MIN_TRAINED_FRAMES = 124
MAX_TRAINED_FRAMES = 362
STANDARD_MODES = {"t2va", "i2va", "fl2va", "l2va"}
NATIVE_AUDIO_MODE = "r2va-native-audio"

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

CAMERA_MOTIONS = {
    "Zoom In": "zooms in",
    "Zoom Out": "zooms out",
    "Push In": "pushes in",
    "Pull Out": "pulls out",
    "Pan Left": "pans left",
    "Pan Right": "pans right",
    "Truck Left": "trucks left",
    "Truck Right": "trucks right",
    "Tilt Up": "tilts up",
    "Tilt Down": "tilts down",
    "Pedestal Up": "pedestals up",
    "Pedestal Down": "pedestals down",
    "Arc Shot": "moves in an arc around the subject",
    "Tracking Shot": "tracks the moving subject",
    "Static Shot": "holds a static shot",
    "Shake Slightly": "shakes slightly",
    "Shake Strongly": "shakes strongly",
    "POV": "holds the subject's point of view",
    "Roll Clockwise": "rolls clockwise",
    "Roll Counterclockwise": "rolls counterclockwise",
}

CUT_TRANSITIONS = {
    "the camera cuts to",
    "the shot cuts to",
    "the shot transitions to",
    "the shot changes to",
    "the shot switches to",
    "the shot cross-dissolves to",
    "the shot fades to",
    "the shot wipes to",
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


def chapter_mode(item: dict) -> str:
    mode = str(item.get("mode", "auto")).lower()
    if mode == "auto":
        return "fl2va" if item.get("last_frame") else "i2va"
    if mode not in STANDARD_MODES:
        raise ValueError(f"Unsupported MiniMax H3 mode: {mode}")
    return mode


def _sentences(text: str) -> int:
    return len(re.findall(r"[.!?](?:[\"']?\s|$)", text.strip()))


def _ensure_sentence(text: str) -> str:
    value = text.strip()
    if not value:
        return value
    return value if value[-1] in ".!?" else value + "."


def _lower_leading_article(text: str) -> str:
    for article in ("A ", "An ", "The "):
        if text.startswith(article):
            return article[0].lower() + text[1:]
    return text


def _timestamp(seconds: float) -> str:
    minutes = int(seconds // 60)
    remainder = seconds - minutes * 60
    return f"{minutes:02d}:{remainder:06.3f}"


def _speaker(speakers: dict, speaker_id: str) -> tuple[str, str]:
    value = speakers.get(speaker_id)
    if isinstance(value, str):
        return value.strip(), ""
    if isinstance(value, dict):
        return str(value.get("description", "")).strip(), str(value.get("voice", "")).strip()
    return "", ""


def _camera_clause(camera: dict | str | None) -> str:
    if not camera:
        return ""
    if isinstance(camera, str):
        return _ensure_sentence(camera)
    motion = str(camera["type"])
    clause = f"The camera {CAMERA_MOTIONS[motion]}"
    amplitude = camera.get("amplitude")
    speed = camera.get("speed")
    target_phrase = str(camera.get("target_phrase", "")).strip()
    if amplitude:
        clause += f" with {amplitude} amplitude"
    if speed:
        clause += f" at {speed} speed"
    if target_phrase:
        clause += " " + target_phrase.rstrip(".")
    return clause + "."


def _speech_clause(entry: dict, speakers: dict) -> str:
    speaker_id = str(entry["speaker_id"])
    description, voice = _speaker(speakers, speaker_id)
    identity = description
    if voice:
        identity += f" with {voice}"
    identity += f" ({speaker_id})"
    kind = str(entry.get("kind", "dialogue"))
    delivery = str(entry.get("delivery", "")).strip()
    language = str(entry.get("language", "English")).strip()
    text = str(entry["text"])
    bridge = entry.get("scene_transition")
    if bridge == "in":
        text = "<scenetrans>" + text
    elif bridge == "out":
        text = text + "<scenetrans>"
    if entry.get("cutoff"):
        text += "<cutoff>"
    delivery_phrase = f" {delivery}" if delivery else ""
    if kind == "singing":
        clause = f"{identity}{delivery_phrase} sings: <d>[{language}] {text}</d>"
    elif kind == "voiceover":
        clause = (
            f"{identity}{delivery_phrase} says in an off-screen voiceover: "
            f"<d>[{language}] {text}</d> while the corresponding on-screen character's lips remain completely closed."
        )
    else:
        clause = f"{identity}{delivery_phrase} says: <d>[{language}] {text}</d>"
    if bridge:
        clause += " The audio continues seamlessly across the cut."
    return clause


def _shot_list(item: dict) -> list[dict]:
    shots = item.get("shots")
    if shots:
        return copy.deepcopy(shots)
    return [{
        "action": item.get("prompt", ""),
        "camera": item.get("camera"),
        "speech": item.get("speech", []),
        "on_screen_text": item.get("on_screen_text", []),
    }]


def lint_prompt_item(
    item: dict,
    duration_seconds: float,
    speakers: dict | None = None,
    mode_override: str | None = None,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    speakers = speakers or {}
    try:
        mode = mode_override or chapter_mode(item)
    except ValueError as exc:
        return [str(exc)], warnings

    if mode == "fl2va" and not item.get("last_frame"):
        errors.append("FL2VA requires last_frame")
    if mode == "l2va" and not item.get("last_frame"):
        errors.append("L2VA requires last_frame")
    if mode == "i2va" and item.get("last_frame"):
        errors.append("I2VA cannot include last_frame; use FL2VA or remove it")
    if mode == "t2va" and item.get("last_frame"):
        errors.append("T2VA cannot include last_frame")

    shots = _shot_list(item)
    if not shots:
        errors.append("At least one shot is required")
    prior_time = 0.0
    bridge_out: dict[str, int] = {}
    for index, shot in enumerate(shots, 1):
        label = f"Shot {index}"
        if not isinstance(shot, dict):
            errors.append(f"{label} must be an object")
            continue
        if not str(shot.get("action", "")).strip():
            errors.append(f"{label} requires a visible or audible action")
        cut_at = shot.get("cut_at")
        if index == 1 and cut_at is not None:
            errors.append("Shot 1 must not have a timestamp")
        if index > 1:
            if cut_at is None:
                errors.append(f"{label} requires cut_at")
            else:
                try:
                    cut = float(cut_at)
                    if cut <= prior_time or cut >= duration_seconds:
                        errors.append(
                            f"{label} cut_at must be strictly increasing and below {duration_seconds:.2f} seconds"
                        )
                    prior_time = cut
                except (TypeError, ValueError):
                    errors.append(f"{label} cut_at must be numeric")
            transition = str(shot.get("transition", "the camera cuts to")).lower()
            if transition not in CUT_TRANSITIONS:
                errors.append(f"{label} has unsupported cut transition: {transition}")
            if transition in {
                "the shot cross-dissolves to", "the shot fades to", "the shot wipes to",
            } and not shot.get("user_requested_transition"):
                errors.append(
                    f"{label} stylized transition requires user_requested_transition=true"
                )

        camera = shot.get("camera")
        if camera and not isinstance(camera, (dict, str)):
            errors.append(f"{label} camera must be a string or object")
        if isinstance(camera, dict):
            motion = camera.get("type")
            if motion not in CAMERA_MOTIONS:
                errors.append(f"{label} camera type must be one of: {', '.join(CAMERA_MOTIONS)}")
            if camera.get("amplitude") not in (None, "small", "large"):
                errors.append(f"{label} camera amplitude must be small or large")
            if camera.get("speed") not in (None, "slow", "fast"):
                errors.append(f"{label} camera speed must be slow or fast")

        texts = shot.get("on_screen_text", [])
        if not isinstance(texts, list) or any(not isinstance(value, str) for value in texts):
            errors.append(f"{label} on_screen_text must be a list of exact strings")

        speech = shot.get("speech", [])
        if not isinstance(speech, list):
            errors.append(f"{label} speech must be a list")
            continue
        for entry in speech:
            if not isinstance(entry, dict):
                errors.append(f"{label} speech entries must be objects")
                continue
            speaker_id = str(entry.get("speaker_id", ""))
            if not re.fullmatch(r"S[1-9][0-9]*", speaker_id):
                errors.append(f"{label} speaker_id must use the S1, S2, ... form")
            description, _voice = _speaker(speakers, speaker_id)
            if not description:
                errors.append(f"{label} speaker {speaker_id or '<missing>'} is absent from the stable speakers registry")
            if entry.get("kind", "dialogue") not in {"dialogue", "singing", "voiceover"}:
                errors.append(f"{label} speech kind must be dialogue, singing, or voiceover")
            if not str(entry.get("language", "English")).strip():
                errors.append(f"{label} speech language is required")
            if not isinstance(entry.get("text"), str) or not entry.get("text"):
                errors.append(f"{label} speech text must be the exact non-empty user-provided text")
            bridge = entry.get("scene_transition")
            if bridge not in (None, "in", "out"):
                errors.append(f"{label} scene_transition must be in or out")
            if bridge == "out":
                bridge_out[speaker_id] = index
            if bridge == "in":
                if bridge_out.get(speaker_id) != index - 1:
                    errors.append(f"{label} speaker {speaker_id} has a transition-in without an adjacent transition-out")
                else:
                    bridge_out.pop(speaker_id, None)
    for speaker_id, shot_number in bridge_out.items():
        errors.append(f"Shot {shot_number} speaker {speaker_id} has a transition-out without an adjacent transition-in")

    soundscape = str(item.get("overall_soundscape", item.get("audio_prompt", ""))).strip()
    if not soundscape:
        errors.append("overall_soundscape/audio_prompt is required")
    elif soundscape == "N/A":
        if not item.get("complete_silence"):
            errors.append("overall_soundscape may be N/A only when complete_silence is true")
    elif not soundscape.endswith((".", "!", "?")) or not 1 <= _sentences(soundscape) <= 4:
        errors.append("overall_soundscape must contain 1-4 complete English sentences")

    music = str(item.get("non_diegetic_music", item.get("music_prompt", "N/A"))).strip()
    if not music:
        errors.append("non_diegetic_music/music_prompt is required")
    elif music != "N/A":
        if not music.endswith((".", "!", "?")) or not 1 <= _sentences(music) <= 3:
            errors.append("non_diegetic_music must contain 1-3 complete English sentences or N/A")
        if re.search(r"\b(mood|moody|emotion|emotional|evokes?|conveys?|feels?)\b", music, re.I):
            warnings.append("Describe non-diegetic music with instrumentation, tempo, rhythm, and dynamics instead of mood")
    return errors, warnings


def _build_shots(style_lock: str, item: dict, mode: str, speakers: dict) -> str:
    shots = _shot_list(item)
    rendered: list[str] = []
    for index, shot in enumerate(shots, 1):
        pieces: list[str] = []
        if index == 1:
            if style_lock.strip():
                pieces.append(_ensure_sentence(style_lock))
            if mode == "i2va":
                pieces.append(
                    "The composition, identity, clothing, colors, key objects, and spatial relationships "
                    "established by <Picture 1> remain the opening anchor."
                )
            elif mode == "fl2va":
                pieces.append("Begin in the exact state and composition established by <Picture 1>.")
            elif mode == "l2va":
                pieces.append("Begin from a plausible earlier state compatible with the supplied ending.")
            elif mode == NATIVE_AUDIO_MODE:
                pieces.append(
                    "Preserve the exact identity, wardrobe, style, and scene anchors from <Picture 1> while "
                    "following the performance timing in <Audio 1>."
                )
        pieces.append(_ensure_sentence(str(shot["action"])))
        camera = _camera_clause(shot.get("camera"))
        if camera:
            pieces.append(camera)
        for entry in shot.get("speech", []):
            pieces.append(_speech_clause(entry, speakers))
        for exact_text in shot.get("on_screen_text", []):
            pieces.append(f"Visible on-screen text reads {json.dumps(exact_text, ensure_ascii=False)}.")

        if index == 1:
            prefix = "[Shot 1] "
        else:
            transition = str(shot.get("transition", "the camera cuts to")).strip()
            pieces[0] = _lower_leading_article(pieces[0])
            prefix = f"[Shot {index}] At {_timestamp(float(shot['cut_at']))}, {transition} "
        rendered.append(prefix + " ".join(pieces))

    transition = str(item.get("transition", "")).strip()
    if transition:
        rendered[-1] += " " + _ensure_sentence(f"The action resolves through {transition}")
    if mode == "fl2va":
        rendered[-1] += (
            " Progressively narrow the visual differences and settle into the exact state, spacing, lighting, "
            "camera angle, and final composition established by <Picture 2>."
        )
    elif mode == "l2va":
        rendered[-1] += (
            " Gradually converge on the exact state, spacing, lighting, camera angle, and final composition "
            "established by <Picture 1>."
        )
    else:
        rendered[-1] += " Settle into the requested terminal tableau and hold nearly still for the final 12 to 15 frames."
    return " ".join(rendered)


def _core_fields(style_lock: str, item: dict, mode: str, speakers: dict) -> str:
    soundscape = item.get("overall_soundscape", item.get("audio_prompt"))
    music = item.get("non_diegetic_music", item.get("music_prompt", "N/A"))
    return (
        f"integrated_multimodal_description: {_build_shots(style_lock, item, mode, speakers)}\n\n"
        f"overall_soundscape: {soundscape}\n\n"
        f"non_diegetic_music: {music}"
    )


def compile_standard_prompt(config: dict, item: dict) -> str:
    runtime = normalize_runtime(config["runtime"])
    mode = chapter_mode(item)
    speakers = config.get("speakers", {})
    errors, _warnings = lint_prompt_item(item, runtime["duration_seconds"], speakers)
    if errors:
        raise ValueError("; ".join(errors))
    shot_number = len(_shot_list(item))
    core = _core_fields(config.get("style_lock", ""), item, mode, speakers)
    if mode == "t2va":
        return core
    if mode == "i2va":
        instruction = (
            "For the target video, at 0.00 seconds into the target video, "
            "<Picture 1> (from [Shot 1]) is fully referenced."
        )
    elif mode == "fl2va":
        instruction = (
            "How the reference pictures align with the target video — "
            "Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; "
            f"Picture 2 (from Shot {shot_number}) aligns with the {runtime['duration_seconds']:.2f}-second mark "
            "of the target video."
        )
    else:
        instruction = (
            "How the reference pictures align with the target video — "
            f"<Picture 1> (from [Shot {shot_number}]) aligns with the "
            f"{runtime['duration_seconds']:.2f}-second mark of the target video."
        )
    return instruction + "\n\n" + core


def compile_native_audio_prompt(config: dict, item: dict) -> str:
    runtime = normalize_runtime(config["runtime"])
    prepared = copy.deepcopy(item)
    speakers = config.get("speakers", {})
    performance = str(prepared.get("performance", "instrumental")).lower()
    shots = _shot_list(prepared)
    if str(prepared.get("music_role", "soundtrack")).lower() == "diegetic-performance":
        shots[0]["action"] = (
            _ensure_sentence(str(shots[0]["action"]))
            + " The on-screen performance and any visible instruments produce the supplied music from <Audio 1> within the scene."
        )
    if performance == "instrumental":
        shots[0]["action"] = (
            _ensure_sentence(str(shots[0]["action"])) + " The performer's lips remain fully closed for every frame; "
            "body, hands, gaze, and camera rhythm follow <Audio 1>."
        )
    elif performance == "vocal":
        lyrics = prepared.get("lyrics")
        if lyrics:
            speech = list(shots[0].get("speech", []))
            speech.append({
                "speaker_id": prepared.get("speaker_id", "S1"),
                "kind": "singing",
                "language": lyrics.get("language", "English"),
                "text": lyrics["text"],
                "delivery": lyrics.get("delivery", ""),
            })
            shots[0]["speech"] = speech
        else:
            speaker_id = str(prepared.get("speaker_id", "S1"))
            shots[0]["action"] = (
                _ensure_sentence(str(shots[0]["action"])) + f" The on-screen performer ({speaker_id}) sings the exact "
                "supplied vocal audio from <Audio 1> with precise natural lip synchronization."
            )
    else:
        raise ValueError("NativeAudio performance must be vocal or instrumental")
    prepared["shots"] = shots
    prepared.pop("prompt", None)
    errors, _warnings = lint_prompt_item(
        prepared, runtime["duration_seconds"], speakers, mode_override=NATIVE_AUDIO_MODE
    )
    if errors:
        raise ValueError("; ".join(errors))
    instruction = (
        "Use <Picture 1> as the exact identity, wardrobe, style, and scene reference. "
        "Use <Audio 1> as the exact performance timeline."
    )
    return instruction + "\n\n" + _core_fields(
        config.get("style_lock", ""), prepared, NATIVE_AUDIO_MODE, speakers
    )


def compile_chapter_prompt(config: dict, item: dict) -> str:
    return compile_standard_prompt(config, item)


def lint_config(config: dict, chapter: int | None = None) -> tuple[list[str], list[str]]:
    runtime = normalize_runtime(config["runtime"])
    errors: list[str] = []
    warnings: list[str] = []
    items = config["chapters"]
    if chapter is not None:
        items = [item for item in items if int(item["number"]) == chapter]
        if not items:
            return [f"Chapter {chapter} is not present"], warnings
    for item in items:
        item_errors, item_warnings = lint_prompt_item(
            item, runtime["duration_seconds"], config.get("speakers", {})
        )
        prefix = f"chapter {int(item['number'])}: "
        try:
            mode = chapter_mode(item)
        except ValueError:
            mode = "invalid"
        style_lock = str(config.get("style_lock", ""))
        if mode == "t2va" and "<Picture" in style_lock:
            item_warnings.append("T2VA style_lock refers to a picture that the mode does not receive")
        if mode == "l2va" and re.search(r"continue exactly from <Picture 1>|opening", style_lock, re.I):
            item_warnings.append("L2VA style_lock appears to treat its ending picture as an opening frame")
        if any(shot.get("on_screen_text") for shot in _shot_list(item)) and re.search(
            r"\bno\b[^.]{0,30}\btext\b", style_lock, re.I
        ):
            item_warnings.append("Requested on-screen text conflicts with the global style_lock")
        errors.extend(prefix + value for value in item_errors)
        warnings.extend(prefix + value for value in item_warnings)
    return errors, warnings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MiniMax H3 runtime and official prompt helper")
    sub = parser.add_subparsers(dest="command", required=True)
    profile = sub.add_parser("profile", help="resolve duration and resolution settings")
    profile.add_argument("--duration", type=float, required=True)
    profile.add_argument("--aspect", choices=("16:9", "9:16", "1:1", "4:5", "5:4"), required=True)
    profile.add_argument("--quality", choices=tuple(RESOLUTION_PRESETS), default="preview")
    for name, help_text in (("compile", "show the exact prompt sent to ComfyUI"), ("lint", "validate prompt structure")):
        command = sub.add_parser(name, help=help_text)
        command.add_argument("--config", type=Path, required=True)
        command.add_argument("--chapter", type=int)
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
    if args.command == "lint":
        errors, warnings = lint_config(config, args.chapter)
        for warning in warnings:
            print("WARNING:", warning)
        for error in errors:
            print("ERROR:", error)
        if errors:
            raise SystemExit(1)
        print(f"PASS: {len(config['chapters']) if args.chapter is None else 1} chapter prompt(s) valid")
        return
    if args.chapter is None:
        raise SystemExit("compile requires --chapter")
    try:
        item = next(value for value in config["chapters"] if int(value["number"]) == args.chapter)
    except StopIteration as exc:
        raise SystemExit(f"Chapter {args.chapter} is not present in {args.config}") from exc
    print(compile_chapter_prompt(config, item))


if __name__ == "__main__":
    main()
