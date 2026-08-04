from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import tempfile
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from h3_prompt import chapter_mode, compile_chapter_prompt, lint_config, normalize_runtime


SAVE_NODE = "92"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_config(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    required = ("series", "runtime", "models", "style_lock", "chapters")
    missing = [key for key in required if key not in data]
    if missing:
        raise RuntimeError(f"Missing config keys: {', '.join(missing)}")
    numbers = [int(item["number"]) for item in data["chapters"]]
    if numbers != sorted(numbers) or len(numbers) != len(set(numbers)):
        raise RuntimeError("Chapter numbers must be unique and ascending")
    data["runtime"] = normalize_runtime(data["runtime"])
    for index, item in enumerate(data["chapters"]):
        mode = chapter_mode(item)
        if index == 0 and mode in {"i2va", "fl2va"} and not data.get("initial_frame"):
            raise RuntimeError(f"First chapter in {mode.upper()} mode requires initial_frame")
        if index > 0 and mode in {"t2va", "l2va"}:
            raise RuntimeError(f"{mode.upper()} is supported only for the first standalone/prequel chapter")
    prompt_errors, prompt_warnings = lint_config(data)
    if prompt_errors:
        raise RuntimeError("Prompt validation failed: " + "; ".join(prompt_errors))
    data["_prompt_warnings"] = prompt_warnings
    data["_config_path"] = str(path.resolve())
    return data


def paths(cfg: dict) -> dict[str, Path]:
    root = Path(cfg["runtime"]["comfy_root"]).resolve()
    output = root / "output" / cfg["series"]["output_subdir"]
    return {
        "root": root,
        "input": root / "input",
        "output": output,
        "manifest": output / cfg["series"].get("manifest", "series-manifest.json"),
        "review": output / "review",
        "posters": output / "review" / "posters",
        "rejects": output / "rejects",
    }


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value or "chapter"


def chapter(cfg: dict, number: int) -> dict:
    for item in cfg["chapters"]:
        if int(item["number"]) == number:
            return item
    raise RuntimeError(f"Chapter {number} is not present in the config")


def load_manifest(cfg: dict) -> dict:
    location = paths(cfg)["manifest"]
    if location.exists():
        data = json.loads(location.read_text(encoding="utf-8-sig"))
        if data.get("series_slug") != cfg["series"]["slug"]:
            raise RuntimeError("Manifest belongs to a different series slug")
        return data
    return {
        "schema_version": 1,
        "series": cfg["series"]["title"],
        "series_slug": cfg["series"]["slug"],
        "config": cfg["_config_path"],
        "continuity": "Accepted chapter N final frame is the exact input to chapter N+1.",
        "chapters": [],
    }


def save_manifest(cfg: dict, manifest: dict) -> None:
    location = paths(cfg)["manifest"]
    location.parent.mkdir(parents=True, exist_ok=True)
    manifest["updated_at"] = now()
    location.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def manifest_item(manifest: dict, number: int, create: bool = False) -> dict | None:
    for item in manifest["chapters"]:
        if int(item["number"]) == number:
            return item
    if not create:
        return None
    item = {"number": number, "state": "unrendered", "attempts": []}
    manifest["chapters"].append(item)
    manifest["chapters"].sort(key=lambda value: int(value["number"]))
    return item


def request_json(cfg: dict, route: str, payload: dict | None = None, timeout: int = 30) -> dict:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        cfg["runtime"].get("comfy_url", "http://127.0.0.1:8188") + route,
        data=body,
        headers={"Content-Type": "application/json"} if body else {},
        method="POST" if body else "GET",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def input_image_name(cfg: dict, number: int) -> str | None:
    p = paths(cfg)
    numbers = [int(item["number"]) for item in cfg["chapters"]]
    if number == numbers[0]:
        if chapter_mode(chapter(cfg, number)) in {"t2va", "l2va"}:
            return None
        image = Path(cfg["initial_frame"])
        image = image.resolve() if image.is_absolute() else (p["input"] / image).resolve()
    else:
        image = p["input"] / f"{cfg['series']['slug']}-chapter-{number:03d}-start.png"
    try:
        relative = image.resolve().relative_to(p["input"].resolve())
    except ValueError as exc:
        raise RuntimeError(f"Input image must be inside {p['input']}: {image}") from exc
    if not image.exists():
        raise FileNotFoundError(image)
    return relative.as_posix()


def optional_input_image_name(cfg: dict, value: str | None) -> str | None:
    if not value:
        return None
    root = paths(cfg)["input"].resolve()
    image = Path(value)
    image = image.resolve() if image.is_absolute() else (root / image).resolve()
    try:
        relative = image.relative_to(root)
    except ValueError as exc:
        raise RuntimeError(f"Optional frame must be inside {root}: {image}") from exc
    if not image.exists():
        raise FileNotFoundError(image)
    return relative.as_posix()


def output_prefix(cfg: dict, item: dict) -> str:
    subdir = Path(cfg["series"]["output_subdir"]).as_posix().strip("/")
    return f"{subdir}/{int(item['number']):03d}-{slugify(item['title'])}"


def build_prompt(cfg: dict, item: dict) -> str:
    return compile_chapter_prompt(cfg, item)


def graph(
    cfg: dict,
    item: dict,
    image_name: str | None,
    last_image_name: str | None = None,
) -> dict:
    rt, models = cfg["runtime"], cfg["models"]
    result = {
        "6": {"class_type": "UNETLoader", "inputs": {"unet_name": models["unet"], "weight_dtype": "default"}},
        "13": {"class_type": "CLIPLoader", "inputs": {"clip_name": models["text_encoder"], "type": "minimax", "device": "default"}},
        "11": {"class_type": "VAELoader", "inputs": {"vae_name": models["video_vae"]}},
        "24": {"class_type": "VAELoader", "inputs": {"vae_name": models["audio_vae"]}},
        "104": {"class_type": "MiniMaxH3ImageToVideo", "inputs": {
            "clip": ["13", 0], "vae": ["11", 0],
            "prompt": build_prompt(cfg, item), "width": int(rt["width"]),
            "height": int(rt["height"]), "length": int(rt["length"]),
        }},
        "15": {"class_type": "RandomNoise", "inputs": {"noise_seed": int(item["seed"])}},
        "16": {"class_type": "BasicGuider", "inputs": {"model": ["6", 0], "conditioning": ["104", 0]}},
        "17": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}},
        "9": {"class_type": "BasicScheduler", "inputs": {"model": ["6", 0], "scheduler": "simple", "steps": int(rt["steps"]), "denoise": 1.0}},
        "14": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["15", 0], "guider": ["16", 0], "sampler": ["17", 0], "sigmas": ["9", 0], "latent_image": ["104", 1]}},
        "10": {"class_type": "VAEDecode", "inputs": {"samples": ["14", 0], "vae": ["11", 0]}},
        "23": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["14", 0], "vae": ["24", 0]}},
        "91": {"class_type": "CreateVideo", "inputs": {"images": ["10", 0], "audio": ["23", 0], "fps": float(rt["fps"]), "bit_depth": 8}},
        SAVE_NODE: {"class_type": "SaveVideo", "inputs": {"video": ["91", 0], "filename_prefix": output_prefix(cfg, item), "format": "auto", "codec": "auto"}},
    }
    if image_name:
        result["1"] = {"class_type": "LoadImage", "inputs": {"image": image_name}}
        result["104"]["inputs"]["first_frame"] = ["1", 0]
    if last_image_name:
        result["2"] = {"class_type": "LoadImage", "inputs": {"image": last_image_name}}
        result["104"]["inputs"]["last_frame"] = ["2", 0]
    return result


def probe(video: Path) -> dict:
    return json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
        "-of", "json", str(video),
    ], text=True))


def media_summary(video: Path) -> dict:
    info = probe(video)
    result = {
        "duration": float(info["format"]["duration"]),
        "size": int(info["format"]["size"]),
        "streams": info.get("streams", []),
    }
    return result


def decoded_frame_count(video: Path) -> int:
    data = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
        "-show_entries", "stream=nb_read_frames", "-of", "json", str(video),
    ], text=True))
    value = data.get("streams", [{}])[0].get("nb_read_frames")
    if value in (None, "N/A") or int(value) < 1:
        raise RuntimeError(f"Could not determine decoded frame count: {video}")
    return int(value)


def extract_indexed_frame(video: Path, frame_index: int, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.unlink(missing_ok=True)
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video),
        "-vf", f"select=eq(n\\,{frame_index})", "-fps_mode", "passthrough", str(destination),
    ], check=True)
    if not destination.exists():
        raise RuntimeError(f"Could not extract frame {frame_index} from {video}")


def extract_poster(video: Path, destination: Path) -> None:
    duration = float(probe(video)["format"]["duration"])
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{duration * 0.5:.4f}",
        "-i", str(video), "-frames:v", "1", "-q:v", "3", str(destination),
    ], check=True)


def make_review_sheet(video: Path, destination: Path, samples: int = 6) -> None:
    duration = float(probe(video)["format"]["duration"])
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="minimax-review-") as temp_name:
        temp = Path(temp_name)
        for index in range(samples):
            at = duration * (index / max(samples - 1, 1))
            if index == samples - 1:
                at = max(0.0, duration - 0.05)
            subprocess.run([
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{at:.4f}",
                "-i", str(video), "-frames:v", "1", "-vf", "scale=320:-2", "-q:v", "3",
                str(temp / f"{index:03d}.jpg"),
            ], check=True)
        cols = 3
        rows = math.ceil(samples / cols)
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-framerate", "1",
            "-i", str(temp / "%03d.jpg"), "-vf", f"tile={cols}x{rows}:padding=4:margin=4",
            "-frames:v", "1", str(destination),
        ], check=True)


def active_attempt(entry: dict) -> dict:
    if not entry.get("attempts"):
        raise RuntimeError(f"Chapter {entry['number']} has no rendered attempts")
    return entry["attempts"][-1]


def cmd_preflight(cfg: dict, _args: argparse.Namespace) -> None:
    failures, notes = [], []
    for tool in ("ffmpeg", "ffprobe"):
        location = shutil.which(tool)
        (notes if location else failures).append(f"{tool}: {location or 'missing'}")
    p = paths(cfg)
    if not p["root"].exists():
        failures.append(f"ComfyUI root missing: {p['root']}")
    model_paths = {
        "unet": p["root"] / "models" / "diffusion_models" / cfg["models"]["unet"],
        "text_encoder": p["root"] / "models" / "text_encoders" / cfg["models"]["text_encoder"],
        "video_vae": p["root"] / "models" / "vae" / cfg["models"]["video_vae"],
        "audio_vae": p["root"] / "models" / "vae" / cfg["models"]["audio_vae"],
    }
    for name, location in model_paths.items():
        (notes if location.exists() else failures).append(f"{name}: {location} ({'ok' if location.exists() else 'missing'})")
    try:
        stats = request_json(cfg, "/system_stats")
        notes.append(f"ComfyUI API: ok; devices={len(stats.get('devices', []))}")
        objects = request_json(cfg, "/object_info", timeout=60)
        first = cfg["chapters"][0]
        first_name = input_image_name(cfg, int(first["number"]))
        last_name = optional_input_image_name(cfg, first.get("last_frame"))
        preflight_graph = graph(cfg, first, first_name, last_name)
        required_nodes = {node["class_type"] for node in preflight_graph.values()}
        missing_nodes = sorted(required_nodes - set(objects))
        if missing_nodes:
            failures.append("Missing ComfyUI node classes: " + ", ".join(missing_nodes))
    except Exception as exc:
        failures.append(f"ComfyUI API unavailable: {exc}")
    try:
        first_name = input_image_name(cfg, int(cfg["chapters"][0]["number"]))
        notes.append(f"initial frame: {'not used by mode' if first_name is None else 'ok'}")
        for item in cfg["chapters"]:
            if item.get("last_frame"):
                optional_input_image_name(cfg, item["last_frame"])
                notes.append(f"chapter {int(item['number'])} last frame: ok")
    except Exception as exc:
        failures.append(str(exc))
    notes.extend(f"prompt warning: {warning}" for warning in cfg.get("_prompt_warnings", []))
    print("\n".join(notes + failures))
    if failures:
        raise SystemExit(1)


def cmd_render(cfg: dict, args: argparse.Namespace) -> None:
    item = chapter(cfg, args.chapter)
    manifest = load_manifest(cfg)
    entry = manifest_item(manifest, args.chapter, create=True)
    assert entry is not None
    if entry["state"] in {"pending_review", "accepted"}:
        raise RuntimeError(f"Chapter {args.chapter} is {entry['state']}; accept/reject it before another render")
    numbers = [int(value["number"]) for value in cfg["chapters"]]
    index = numbers.index(args.chapter)
    if index > 0:
        previous = manifest_item(manifest, numbers[index - 1])
        if not previous or previous.get("state") != "accepted":
            raise RuntimeError(f"Chapter {numbers[index - 1]} must be accepted first")
    image_name = input_image_name(cfg, args.chapter)
    last_image_name = optional_input_image_name(cfg, item.get("last_frame"))
    queued_input_hash = sha256(paths(cfg)["input"] / image_name) if image_name else None
    queued_last_hash = sha256(paths(cfg)["input"] / last_image_name) if last_image_name else None
    started = time.time()
    response = request_json(cfg, "/prompt", {
        "prompt": graph(cfg, item, image_name, last_image_name),
        "client_id": f"{cfg['series']['slug']}-{args.chapter:03d}-{int(started)}",
    })
    if response.get("node_errors"):
        raise RuntimeError(json.dumps(response["node_errors"], indent=2))
    prompt_id = response["prompt_id"]
    print(f"QUEUED chapter={args.chapter} prompt_id={prompt_id}", flush=True)
    while True:
        history = request_json(cfg, f"/history/{prompt_id}")
        record = history.get(prompt_id)
        if record:
            status = record.get("status", {})
            if status.get("completed") and status.get("status_str") == "success":
                saved = record["outputs"][SAVE_NODE]["images"][0]
                video = paths(cfg)["root"] / "output" / saved["subfolder"] / saved["filename"]
                break
            if status.get("status_str") == "error":
                raise RuntimeError(f"ComfyUI render failed: {status}")
        print(f"PROGRESS chapter={args.chapter} elapsed={int(time.time() - started)}s", flush=True)
        time.sleep(int(cfg["runtime"].get("poll_seconds", 15)))
    summary = media_summary(video)
    attempt_number = len(entry["attempts"]) + 1
    sheet = paths(cfg)["review"] / f"chapter-{args.chapter:03d}-attempt-{attempt_number:02d}-review.jpg"
    make_review_sheet(video, sheet)
    attempt = {
        "attempt": attempt_number,
        "state": "pending_review",
        "created_at": now(),
        "path": str(video.resolve()),
        "filename": video.name,
        "seed": int(item["seed"]),
        "prompt": build_prompt(cfg, item),
        "mode": chapter_mode(item),
        "input_image": image_name,
        "input_sha256": queued_input_hash,
        "last_frame": last_image_name,
        "last_frame_sha256": queued_last_hash,
        "runtime": {
            "width": int(cfg["runtime"]["width"]), "height": int(cfg["runtime"]["height"]),
            "length": int(cfg["runtime"]["length"]), "fps": int(cfg["runtime"]["fps"]),
            "duration_seconds": float(cfg["runtime"]["duration_seconds"]),
        },
        "prompt_id": prompt_id,
        "render_seconds": round(time.time() - started, 2),
        "media": summary,
        "review_sheet": str(sheet.resolve()),
    }
    entry.update({
        "title": item["title"], "movement": item.get("movement", "Sequence"),
        "state": "pending_review", "active_attempt": attempt["attempt"],
    })
    entry["attempts"].append(attempt)
    save_manifest(cfg, manifest)
    print(f"PENDING_REVIEW chapter={args.chapter} video={video} sheet={sheet}")


def cmd_accept(cfg: dict, args: argparse.Namespace) -> None:
    manifest = load_manifest(cfg)
    entry = manifest_item(manifest, args.chapter)
    if not entry or entry.get("state") != "pending_review":
        raise RuntimeError(f"Chapter {args.chapter} is not pending review")
    attempt = active_attempt(entry)
    video = Path(attempt["path"])
    if not video.exists():
        raise FileNotFoundError(video)
    numbers = [int(value["number"]) for value in cfg["chapters"]]
    index = numbers.index(args.chapter)
    continuation = None
    if index < len(numbers) - 1:
        next_number = numbers[index + 1]
        continuation = paths(cfg)["input"] / f"{cfg['series']['slug']}-chapter-{next_number:03d}-start.png"
        extract_indexed_frame(video, int(cfg["runtime"]["length"]) - 1, continuation)
    poster = paths(cfg)["posters"] / f"chapter-{args.chapter:03d}-poster.jpg"
    extract_poster(video, poster)
    video_hash = sha256(video)
    current_input_hash = None
    if attempt.get("input_image"):
        input_path = paths(cfg)["input"] / attempt["input_image"]
        current_input_hash = sha256(input_path)
        if current_input_hash != attempt.get("input_sha256"):
            raise RuntimeError("Chapter input image changed after the render was queued")
    if attempt.get("last_frame"):
        last_path = paths(cfg)["input"] / attempt["last_frame"]
        if sha256(last_path) != attempt.get("last_frame_sha256"):
            raise RuntimeError("Chapter last-frame image changed after the render was queued")
    attempt.update({
        "state": "accepted", "reviewed_at": now(), "review_notes": args.notes or "accepted",
        "video_sha256": video_hash,
    })
    entry.update({
        "state": "accepted", "accepted_path": str(video.resolve()),
        "poster": str(poster.resolve()), "review_notes": args.notes or "accepted",
        "accepted_video_sha256": video_hash, "input_sha256": current_input_hash,
    })
    if continuation:
        entry["continuation_frame"] = str(continuation.resolve())
        entry["continuation_sha256"] = sha256(continuation)
    save_manifest(cfg, manifest)
    print(f"ACCEPTED chapter={args.chapter} continuation={continuation or 'final chapter'}")


def cmd_reject(cfg: dict, args: argparse.Namespace) -> None:
    manifest = load_manifest(cfg)
    entry = manifest_item(manifest, args.chapter)
    if not entry or entry.get("state") != "pending_review":
        raise RuntimeError(f"Chapter {args.chapter} is not pending review")
    attempt = active_attempt(entry)
    source = Path(attempt["path"])
    reject_dir = paths(cfg)["rejects"]
    reject_dir.mkdir(parents=True, exist_ok=True)
    reason = slugify(args.reason)[:60]
    destination = reject_dir / f"{source.stem}_REJECT-{reason}{source.suffix}"
    if destination.exists():
        destination = reject_dir / f"{source.stem}_REJECT-{reason}-{int(time.time())}{source.suffix}"
    if source.exists():
        shutil.move(str(source), str(destination))
    attempt.update({"state": "rejected", "rejected_at": now(), "reason": args.reason, "path": str(destination.resolve())})
    entry.update({"state": "rejected", "rejection_reason": args.reason})
    save_manifest(cfg, manifest)
    print(f"REJECTED chapter={args.chapter} preserved={destination}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def cmd_verify(cfg: dict, _args: argparse.Namespace) -> None:
    manifest = load_manifest(cfg)
    p, rt = paths(cfg), cfg["runtime"]
    errors, warnings, checked, chains = [], [], 0, 0
    accepted = {int(item["number"]): item for item in manifest["chapters"] if item.get("state") == "accepted"}
    expected_duration = int(rt["length"]) / float(rt["fps"])
    numbers = [int(item["number"]) for item in cfg["chapters"]]
    upstream = manifest.get("upstream")
    if upstream:
        source = Path(upstream["source_video"])
        initial = Path(upstream["initial_frame"])
        if not source.exists() or not initial.exists():
            errors.append("upstream boundary source or initial frame is missing")
        else:
            if sha256(source) != upstream.get("source_video_sha256"):
                errors.append("upstream source video SHA-256 changed")
            with tempfile.TemporaryDirectory(prefix="minimax-upstream-") as temp_name:
                fresh = Path(temp_name) / "upstream-final.png"
                extract_indexed_frame(source, int(upstream["frame_index"]), fresh)
                if sha256(fresh) != sha256(initial) or sha256(initial) != upstream.get("frame_sha256"):
                    errors.append(f"chain {upstream.get('source_chapter')}->{numbers[0]}: upstream SHA-256 mismatch")
                else:
                    chains += 1
    for number in numbers:
        entry = accepted.get(number)
        if not entry:
            warnings.append(f"chapter {number}: not accepted")
            continue
        checked += 1
        video = Path(entry["accepted_path"])
        if not video.exists():
            errors.append(f"chapter {number}: missing {video}")
            continue
        if entry.get("accepted_video_sha256") and sha256(video) != entry["accepted_video_sha256"]:
            errors.append(f"chapter {number}: accepted video SHA-256 changed")
        attempt = active_attempt(entry)
        if attempt.get("input_image"):
            input_file = p["input"] / attempt["input_image"]
            if not input_file.exists() or sha256(input_file) != entry.get("input_sha256"):
                errors.append(f"chapter {number}: accepted input image SHA-256 changed")
        if attempt.get("last_frame"):
            last_file = p["input"] / attempt["last_frame"]
            if not last_file.exists() or sha256(last_file) != attempt.get("last_frame_sha256"):
                errors.append(f"chapter {number}: accepted last-frame image SHA-256 changed")
        info = probe(video)
        duration = float(info["format"]["duration"])
        if abs(duration - expected_duration) > 0.35:
            errors.append(f"chapter {number}: duration {duration:.3f}s, expected about {expected_duration:.3f}s")
        streams = info.get("streams", [])
        v = next((s for s in streams if s.get("codec_type") == "video"), None)
        a = next((s for s in streams if s.get("codec_type") == "audio"), None)
        if not v or v.get("codec_name") != "h264" or int(v.get("width", 0)) != int(rt["width"]) or int(v.get("height", 0)) != int(rt["height"]):
            errors.append(f"chapter {number}: unexpected video stream {v}")
        if not a or a.get("codec_name") != "aac" or int(a.get("channels", 0)) != 2:
            errors.append(f"chapter {number}: unexpected audio stream {a}")
        idx = numbers.index(number)
        if idx < len(numbers) - 1 and numbers[idx + 1] in accepted:
            expected = p["input"] / f"{cfg['series']['slug']}-chapter-{numbers[idx + 1]:03d}-start.png"
            if not expected.exists():
                errors.append(f"chain {number}->{numbers[idx + 1]}: stored input missing")
            else:
                if entry.get("continuation_sha256") and sha256(expected) != entry["continuation_sha256"]:
                    errors.append(f"chain {number}->{numbers[idx + 1]}: stored continuation SHA-256 changed")
                with tempfile.TemporaryDirectory(prefix="minimax-chain-") as temp_name:
                    fresh = Path(temp_name) / "final.png"
                    extract_indexed_frame(video, int(rt["length"]) - 1, fresh)
                    if sha256(fresh) != sha256(expected):
                        errors.append(f"chain {number}->{numbers[idx + 1]}: SHA-256 mismatch")
                    else:
                        chains += 1
    result = {"accepted_checked": checked, "exact_frame_chains": chains, "errors": errors, "warnings": warnings}
    print(json.dumps(result, indent=2))
    if errors:
        raise SystemExit(1)


def accepted_range(cfg: dict, first: int | None, last: int | None) -> list[tuple[int, Path]]:
    manifest = load_manifest(cfg)
    result = []
    for entry in sorted(manifest["chapters"], key=lambda value: int(value["number"])):
        number = int(entry["number"])
        if entry.get("state") != "accepted" or (first is not None and number < first) or (last is not None and number > last):
            continue
        result.append((number, Path(entry["accepted_path"])))
    if not result:
        raise RuntimeError("No accepted chapters in the requested range")
    return result


def concat_escape(path: Path) -> str:
    return path.resolve().as_posix().replace("'", "'\\''")


def cmd_concat(cfg: dict, args: argparse.Namespace) -> None:
    videos = accepted_range(cfg, args.first, args.last)
    requested = [int(item["number"]) for item in cfg["chapters"] if (args.first is None or int(item["number"]) >= args.first) and (args.last is None or int(item["number"]) <= args.last)]
    if [number for number, _ in videos] != requested:
        raise RuntimeError("Every configured chapter in the range must be accepted before concat")
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    list_file = output.with_suffix(".concat.txt")
    list_file.write_text("".join(f"file '{concat_escape(video)}'\n" for _, video in videos), encoding="utf-8")
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
        "-i", str(list_file), "-c", "copy", "-movflags", "+faststart", str(output),
    ], check=True)
    print(json.dumps({"output": str(output), **media_summary(output)}, indent=2))


def cmd_contact_sheet(cfg: dict, args: argparse.Namespace) -> None:
    videos = accepted_range(cfg, args.first, args.last)
    output = Path(args.output).resolve() if args.output else paths(cfg)["review"] / f"chapters-{videos[0][0]:03d}-{videos[-1][0]:03d}-contact-sheet.jpg"
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="minimax-contact-") as temp_name:
        temp = Path(temp_name)
        for index, (_number, video) in enumerate(videos):
            duration = float(probe(video)["format"]["duration"])
            subprocess.run([
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{duration * 0.5:.4f}",
                "-i", str(video), "-frames:v", "1", "-vf", "scale=240:-2", "-q:v", "3",
                str(temp / f"{index:04d}.jpg"),
            ], check=True)
        cols = min(6, max(1, math.ceil(math.sqrt(len(videos)))))
        rows = math.ceil(len(videos) / cols)
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-framerate", "1", "-i", str(temp / "%04d.jpg"),
            "-vf", f"tile={cols}x{rows}:padding=4:margin=4", "-frames:v", "1", str(output),
        ], check=True)
    print(output)


def cmd_web_encode(_cfg: dict, args: argparse.Namespace) -> None:
    source, output = Path(args.input).resolve(), Path(args.output).resolve()
    duration = float(probe(source)["format"]["duration"])
    audio_bps = 64_000
    video_bps = int((int(args.max_bytes) * 8 * 0.965 / duration) - audio_bps)
    if video_bps < 120_000:
        raise RuntimeError(f"Target is only {video_bps} video bits/s; use a playlist or larger host limit")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="minimax-pass-") as temp_name:
        passlog = str(Path(temp_name) / "ffmpeg2pass")
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source), "-an",
            "-c:v", "libx264", "-b:v", str(video_bps), "-pass", "1", "-passlogfile", passlog, "-f", "null", "NUL",
        ], check=True)
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
            "-c:v", "libx264", "-b:v", str(video_bps), "-pass", "2", "-passlogfile", passlog,
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", str(audio_bps), "-movflags", "+faststart", str(output),
        ], check=True)
    size = output.stat().st_size
    print(json.dumps({"output": str(output), "size": size, "max_bytes": int(args.max_bytes)}, indent=2))
    if size > int(args.max_bytes):
        raise SystemExit(1)


def copy_if_changed(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and source.stat().st_size == destination.stat().st_size and sha256(source) == sha256(destination):
        return
    shutil.copy2(source, destination)


def seed_existing_catalog(site: Path, destination: Path) -> dict[int, dict]:
    existing: dict[int, dict] = {}
    catalog_path = destination / "archive-catalog.json"
    if catalog_path.exists():
        raw = json.loads(catalog_path.read_text(encoding="utf-8-sig"))
        for item in raw.get("chapters", []):
            try:
                existing[int(item["number"])] = item
            except (KeyError, ValueError, TypeError):
                continue
        return existing
    page = site / "app" / "page.tsx"
    page_text = page.read_text(encoding="utf-8-sig") if page.exists() else ""
    tuple_pattern = re.compile(
        r'\[\s*"(?P<number>\d+)"\s*,\s*"(?P<title>[^"]+)"\s*,\s*"(?P<video>[^"]+\.mp4)"\s*,\s*"(?P<note>[^"]*)"\s*\]'
    )
    recovered = {int(match.group("number")): match.groupdict() for match in tuple_pattern.finditer(page_text)}
    for video in sorted(destination.glob("*.mp4")):
        match = re.match(r"(?P<number>\d+)-(?P<slug>.+?)(?:_\d+_)?\.mp4$", video.name, re.IGNORECASE)
        if not match:
            continue
        number = int(match.group("number"))
        found = recovered.get(number, {})
        title = found.get("title") or match.group("slug").replace("-", " ").title()
        existing[number] = {
            "number": f"{number:02d}", "title": title, "movement": "Legacy archive",
            "video": video.name, "poster": f"chapter-{number:02d}-poster.jpg",
            "duration": media_summary(video)["duration"], "note": found.get("note", ""),
            "catalog_source": "recovered" if found else "media-scan",
        }
    return existing


def cmd_bootstrap(cfg: dict, args: argparse.Namespace) -> None:
    manifest = load_manifest(cfg)
    if manifest.get("chapters"):
        raise RuntimeError("Bootstrap must run before any chapter is rendered")
    if manifest.get("upstream") and not args.replace:
        raise RuntimeError("Manifest already has upstream provenance; inspect it or pass --replace")
    source = Path(args.source_video).resolve()
    if not source.exists():
        raise FileNotFoundError(source)
    first_chapter = int(cfg["chapters"][0]["number"])
    if int(args.source_chapter) != first_chapter - 1 and not args.allow_nonadjacent:
        raise RuntimeError(f"Source chapter must be {first_chapter - 1}; pass --allow-nonadjacent only if intentional")
    p = paths(cfg)
    target_value = Path(cfg["initial_frame"])
    target = target_value.resolve() if target_value.is_absolute() else (p["input"] / target_value).resolve()
    try:
        target.relative_to(p["input"].resolve())
    except ValueError as exc:
        raise RuntimeError(f"initial_frame must be inside {p['input']}") from exc
    frame_count = decoded_frame_count(source)
    frame_index = frame_count - 1
    with tempfile.TemporaryDirectory(prefix="minimax-bootstrap-") as temp_name:
        extracted = Path(temp_name) / "final.png"
        extract_indexed_frame(source, frame_index, extracted)
        if target.exists() and sha256(target) != sha256(extracted) and not args.replace:
            raise RuntimeError(f"initial_frame already exists with different content: {target}; inspect it or pass --replace")
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or sha256(target) != sha256(extracted):
            shutil.copy2(extracted, target)
    manifest["upstream"] = {
        "source_chapter": int(args.source_chapter), "source_video": str(source),
        "source_video_sha256": sha256(source), "source_frame_count": frame_count, "frame_index": frame_index,
        "initial_frame": str(target), "frame_sha256": sha256(target), "created_at": now(),
    }
    save_manifest(cfg, manifest)
    print(json.dumps(manifest["upstream"], indent=2))


def cmd_stage_site(cfg: dict, _args: argparse.Namespace) -> None:
    archive = cfg.get("archive")
    if not archive:
        raise RuntimeError("Config has no archive object")
    site = Path(archive["site_root"]).resolve()
    if not (site / ".openai" / "hosting.json").exists():
        raise RuntimeError(f"Not a configured Sites project: {site}")
    destination = site / archive.get("public_series_subdir", "public/series")
    maximum = int(archive.get("max_file_bytes", 25_000_000))
    manifest = load_manifest(cfg)
    catalog_by_number = seed_existing_catalog(site, destination)
    configured = {int(item["number"]): item for item in cfg["chapters"]}
    for entry in sorted(manifest["chapters"], key=lambda value: int(value["number"])):
        if entry.get("state") != "accepted":
            continue
        number = int(entry["number"])
        video, poster = Path(entry["accepted_path"]), Path(entry["poster"])
        if video.stat().st_size > maximum:
            raise RuntimeError(f"Chapter {number} exceeds site file limit: {video.stat().st_size} > {maximum}")
        copy_if_changed(video, destination / video.name)
        site_poster = destination / f"chapter-{number:02d}-poster.jpg"
        copy_if_changed(poster, site_poster)
        spec = configured[number]
        catalog_by_number[number] = {
            "number": f"{number:02d}", "title": spec["title"], "movement": spec.get("movement", "Sequence"),
            "video": video.name, "poster": site_poster.name, "duration": media_summary(video)["duration"],
            "prompt": spec.get("prompt") or json.dumps(spec.get("shots", []), ensure_ascii=False),
            "transition": spec.get("transition", ""),
        }
    catalog = [catalog_by_number[number] for number in sorted(catalog_by_number)]
    catalog_path = destination / "archive-catalog.json"
    catalog_path.write_text(json.dumps({"series": cfg["series"]["title"], "chapters": catalog}, indent=2), encoding="utf-8")
    print(json.dumps({"site": str(site), "catalog": str(catalog_path), "staged_chapters": len(catalog)}, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Supervised MiniMax H3 chaptered video pipeline")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("preflight", "verify", "stage-site"):
        p = sub.add_parser(name)
        p.add_argument("--config", type=Path, required=True)
    p = sub.add_parser("render")
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--chapter", type=int, required=True)
    p = sub.add_parser("bootstrap")
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--source-video", required=True)
    p.add_argument("--source-chapter", type=int, required=True)
    p.add_argument("--replace", action="store_true")
    p.add_argument("--allow-nonadjacent", action="store_true")
    p = sub.add_parser("accept")
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--chapter", type=int, required=True)
    p.add_argument("--notes", default="")
    p = sub.add_parser("reject")
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--chapter", type=int, required=True)
    p.add_argument("--reason", required=True)
    for name in ("concat", "contact-sheet"):
        p = sub.add_parser(name)
        p.add_argument("--config", type=Path, required=True)
        p.add_argument("--from", dest="first", type=int)
        p.add_argument("--to", dest="last", type=int)
        if name == "concat":
            p.add_argument("--output", required=True)
        else:
            p.add_argument("--output")
    p = sub.add_parser("web-encode")
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--max-bytes", type=int, default=24_500_000)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    cfg = load_config(args.config)
    commands = {
        "preflight": cmd_preflight,
        "bootstrap": cmd_bootstrap,
        "render": cmd_render,
        "accept": cmd_accept,
        "reject": cmd_reject,
        "verify": cmd_verify,
        "concat": cmd_concat,
        "contact-sheet": cmd_contact_sheet,
        "web-encode": cmd_web_encode,
        "stage-site": cmd_stage_site,
    }
    commands[args.command](cfg, args)


if __name__ == "__main__":
    main()
