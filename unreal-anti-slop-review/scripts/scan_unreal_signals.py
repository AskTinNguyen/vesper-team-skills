#!/usr/bin/env python3
"""Collect deterministic lexical signals from a frozen Unreal review surface."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


SURFACE_SCHEMA = "unreal-review-surface/v2"
RECEIPT_SCHEMA = "unreal-signal-receipt/v2"
SOURCE_SUFFIXES = {".h", ".hpp", ".cpp", ".cc", ".cxx", ".inl"}
ATTRIBUTIONS = {
    "introduced",
    "modified",
    "pre-existing",
    "context",
    "untracked",
    "generated",
    "unknown",
}
REVIEW_MODES = {"named", "worktree", "branch", "pr", "engine-install", "engine-fork"}


@dataclass(frozen=True)
class SurfaceFile:
    path: str
    attribution: str
    scan: bool
    absolute_path: Path


@dataclass(frozen=True)
class Signal:
    signal_id: str
    path: str
    line: int
    signal: str
    attribution: str
    question: str
    excerpt: str


class SurfaceError(RuntimeError):
    pass


SIGNALS = (
    (
        "synchronous-load",
        re.compile(r"\b(?:LoadSynchronous|StaticLoadObject|TryLoad|LoadObject\s*<)", re.MULTILINE),
        "Is blocking load safe at this lifecycle phase, thread, frequency, and scale?",
    ),
    (
        "runtime-object-discovery",
        re.compile(r"\b(?:GetComponentByClass|FindObject|FindObjectChecked|FindFProperty)\b", re.MULTILINE),
        "Is this a dynamic boundary, or is a typed canonical owner being rediscovered?",
    ),
    (
        "reflection-dispatch",
        re.compile(r"\b(?:ProcessEvent|FindFunction|CallFunctionByNameWithArguments)\b", re.MULTILINE),
        "Is reflection required by a dynamic contract with recoverable failure handling?",
    ),
    (
        "hard-cast-invariant",
        re.compile(r"\bCastChecked\s*<", re.MULTILINE),
        "Which construction, load, authored-data, networking, and teardown paths enforce this type invariant?",
    ),
    (
        "tick-definition",
        re.compile(r"\bvoid\s+[A-Za-z_][A-Za-z0-9_:<>]*::(?:Tick|TickComponent|NativeTick)\s*\(", re.MULTILINE),
        "What are activation, frequency, scale, stop condition, and bounded cost?",
    ),
    (
        "raw-callback-registration",
        re.compile(r"\b(?:AddRaw|BindRaw|CreateRaw)\s*\(\s*this\b", re.MULTILINE),
        "Where are the bound source, exact inverse, replacement path, and logical terminal?",
    ),
    (
        "global-registration",
        re.compile(
            r"\b(?:RegisterNomadTabSpawner|RegisterStartupCallback|RegisterCustomClassLayout|"
            r"AddDynamicSection|AddMenuExtension|UDebugDrawService\s*::\s*Register)\b",
            re.MULTILINE,
        ),
        "Which owner or handle removes this registration at reload, deactivation, teardown, or shutdown?",
    ),
    (
        "direct-package-save",
        re.compile(r"\b(?:UPackage\s*::\s*Save|SavePackage)\s*\(", re.MULTILINE),
        "Is saving an explicit user action after successful transaction, mutation, and failure checks?",
    ),
    (
        "config-write",
        re.compile(r"\bGConfig\s*->\s*(?:Set|SetArray|RemoveKey|EmptySection)\b", re.MULTILINE),
        "What owns validation, rollback, persistence, and the configuration round trip?",
    ),
    (
        "deferred-work",
        re.compile(r"\b(?:RequestAsyncLoad|AsyncTask|SetTimer)\s*\(", re.MULTILINE),
        "Where are operation identity, cancellation, stale-result rejection, world/thread revalidation, and terminal state?",
    ),
    (
        "mutable-default-access",
        re.compile(r"\bGetMutableDefault\s*<", re.MULTILINE),
        "Can shared default state be observed concurrently, and are all fields and derived side effects restored?",
    ),
)


def normalized_key(path: str) -> str:
    return path.replace("\\", "/").casefold()


def relative_path(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def resolve_inside(root: Path, value: str, *, require_file: bool) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        raise SurfaceError(f"manifest paths must be relative to root: {value}")
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise SurfaceError(f"path escapes root: {value}") from error
    if require_file and not resolved.is_file():
        raise SurfaceError(f"surface file does not exist: {value}")
    return resolved


def validate_surface(data: dict[str, Any], manifest_path: Path | None = None) -> tuple[Path, list[SurfaceFile], list[dict[str, str]]]:
    if data.get("schema_version") != SURFACE_SCHEMA:
        raise SurfaceError(f"unsupported surface schema: {data.get('schema_version')!r}")
    if data.get("review_mode") not in REVIEW_MODES:
        raise SurfaceError(f"invalid review_mode: {data.get('review_mode')!r}")
    if not isinstance(data.get("engine_provenance", {}), dict):
        raise SurfaceError("engine_provenance must be an object")

    root_value = data.get("root")
    if not isinstance(root_value, str) or not root_value.strip():
        raise SurfaceError("surface root must be a non-empty string")
    root_path = Path(root_value)
    if not root_path.is_absolute() and manifest_path is not None:
        root_path = manifest_path.parent / root_path
    root = root_path.resolve()
    if not root.is_dir():
        raise SurfaceError(f"surface root is not a directory: {root}")

    entries = data.get("files")
    if not isinstance(entries, list) or not entries:
        raise SurfaceError("surface files must be a non-empty list")

    files: list[SurfaceFile] = []
    seen: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise SurfaceError(f"files[{index}] must be an object")
        path_value = entry.get("path")
        attribution = entry.get("attribution")
        scan = entry.get("scan")
        if not isinstance(path_value, str) or not path_value.strip():
            raise SurfaceError(f"files[{index}].path must be a non-empty string")
        if attribution not in ATTRIBUTIONS:
            raise SurfaceError(f"files[{index}].attribution is invalid: {attribution!r}")
        if not isinstance(scan, bool):
            raise SurfaceError(f"files[{index}].scan must be boolean")
        absolute = resolve_inside(root, path_value, require_file=True)
        canonical = relative_path(root, absolute)
        key = normalized_key(canonical)
        if key in seen:
            raise SurfaceError(f"duplicate surface file: {canonical}")
        seen.add(key)
        if scan and absolute.suffix.lower() not in SOURCE_SUFFIXES:
            raise SurfaceError(f"scanner-eligible file has unsupported source type: {canonical}")
        files.append(SurfaceFile(canonical, attribution, scan, absolute))

    exclusions_data = data.get("exclusions", [])
    if not isinstance(exclusions_data, list):
        raise SurfaceError("surface exclusions must be a list")
    exclusions: list[dict[str, str]] = []
    exclusion_seen: set[str] = set()
    for index, entry in enumerate(exclusions_data):
        if not isinstance(entry, dict):
            raise SurfaceError(f"exclusions[{index}] must be an object")
        path_value = entry.get("path")
        reason = entry.get("reason")
        if not isinstance(path_value, str) or not path_value.strip():
            raise SurfaceError(f"exclusions[{index}].path must be a non-empty string")
        if not isinstance(reason, str) or not reason.strip():
            raise SurfaceError(f"exclusions[{index}].reason must be a non-empty string")
        absolute = resolve_inside(root, path_value, require_file=False)
        canonical = relative_path(root, absolute)
        key = normalized_key(canonical)
        if key in exclusion_seen:
            raise SurfaceError(f"duplicate exclusion: {canonical}")
        if key in seen:
            raise SurfaceError(f"path cannot be both selected and excluded: {canonical}")
        exclusion_seen.add(key)
        exclusions.append({"path": canonical, "reason": reason.strip()})

    return root, files, exclusions


def load_manifest(path: Path) -> tuple[dict[str, Any], Path, list[SurfaceFile], list[dict[str, str]]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SurfaceError(f"cannot read manifest {path}: {error}") from error
    if not isinstance(data, dict):
        raise SurfaceError("surface manifest root must be an object")
    root, files, exclusions = validate_surface(data, path.resolve())
    return data, root, files, exclusions


def direct_surface(root_value: str, paths: list[str]) -> tuple[dict[str, Any], Path, list[SurfaceFile], list[dict[str, str]]]:
    root = Path(root_value).resolve()
    data = {
        "schema_version": SURFACE_SCHEMA,
        "root": str(root),
        "review_mode": "named",
        "files": [{"path": value, "attribution": "unknown", "scan": True} for value in paths],
        "exclusions": [],
        "engine_provenance": {},
    }
    validated_root, files, exclusions = validate_surface(data)
    data["files"] = [{"path": item.path, "attribution": item.attribution, "scan": item.scan} for item in files]
    return data, validated_root, files, exclusions


def mask_non_code(text: str) -> str:
    chars = list(text)
    index = 0
    state = "code"
    quote = ""
    while index < len(chars):
        current = chars[index]
        following = chars[index + 1] if index + 1 < len(chars) else ""
        if state == "line-comment":
            if current == "\n":
                state = "code"
            else:
                chars[index] = " "
            index += 1
            continue
        if state == "block-comment":
            if current == "*" and following == "/":
                chars[index] = chars[index + 1] = " "
                index += 2
                state = "code"
            else:
                if current != "\n":
                    chars[index] = " "
                index += 1
            continue
        if state == "string":
            if current == "\\" and index + 1 < len(chars):
                if current != "\n":
                    chars[index] = " "
                if chars[index + 1] != "\n":
                    chars[index + 1] = " "
                index += 2
                continue
            if current == quote:
                chars[index] = " "
                state = "code"
            elif current != "\n":
                chars[index] = " "
            index += 1
            continue
        if current == "/" and following == "/":
            chars[index] = chars[index + 1] = " "
            index += 2
            state = "line-comment"
            continue
        if current == "/" and following == "*":
            chars[index] = chars[index + 1] = " "
            index += 2
            state = "block-comment"
            continue
        if current in {'"', "'"}:
            quote = current
            chars[index] = " "
            index += 1
            state = "string"
            continue
        index += 1
    return "".join(chars)


def source_excerpt(lines: list[str], line: int) -> str:
    if line < 1 or line > len(lines):
        return ""
    return lines[line - 1].strip()[:240]


def scan_file(surface_file: SurfaceFile, start_index: int) -> list[Signal]:
    try:
        text = surface_file.absolute_path.read_text(encoding="utf-8", errors="replace")
    except OSError as error:
        raise SurfaceError(f"cannot read {surface_file.path}: {error}") from error
    masked = mask_non_code(text)
    lines = text.splitlines()
    matches: list[tuple[int, str, str]] = []
    for signal_name, pattern, question in SIGNALS:
        for match in pattern.finditer(masked):
            line = masked.count("\n", 0, match.start()) + 1
            matches.append((line, signal_name, question))
    if "test" in surface_file.path.casefold():
        broadcast = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\s*(?:\.|->)\s*Broadcast\s*\(", re.MULTILINE)
        for match in broadcast.finditer(masked):
            line = masked.count("\n", 0, match.start()) + 1
            matches.append(
                (
                    line,
                    "test-direct-broadcast",
                    "Does this test reach the production producer, or only exercise consumer/event shape?",
                )
            )
    matches.sort(key=lambda item: (item[0], item[1]))
    return [
        Signal(
            signal_id=f"SIG-{start_index + offset:04d}",
            path=surface_file.path,
            line=line,
            signal=signal_name,
            attribution=surface_file.attribution,
            question=question,
            excerpt=source_excerpt(lines, line),
        )
        for offset, (line, signal_name, question) in enumerate(matches)
    ]


def build_receipt(surface: dict[str, Any], root: Path, files: list[SurfaceFile], exclusions: list[dict[str, str]]) -> dict[str, Any]:
    scanned = [item for item in files if item.scan]
    unscanned = [item for item in files if not item.scan]
    signals: list[Signal] = []
    next_index = 1
    for item in scanned:
        file_signals = scan_file(item, next_index)
        signals.extend(file_signals)
        next_index += len(file_signals)
    return {
        "schema_version": RECEIPT_SCHEMA,
        "surface_schema_version": surface["schema_version"],
        "root": str(root),
        "status": "OK" if scanned else "NOT_APPLICABLE",
        "scanned_files": [{"path": item.path, "attribution": item.attribution} for item in scanned],
        "unscanned_files": [
            {"path": item.path, "attribution": item.attribution, "reason": "manifest scan=false"}
            for item in unscanned
        ],
        "exclusions": exclusions,
        "signals": [asdict(item) for item in signals],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--manifest", help="Frozen surface manifest JSON")
    source.add_argument("--paths", nargs="+", help="Exact source files relative to --root")
    parser.add_argument("--root", default=".", help="Root for direct --paths mode")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.manifest:
            surface, root, files, exclusions = load_manifest(Path(args.manifest).resolve())
        else:
            surface, root, files, exclusions = direct_surface(args.root, args.paths)
        receipt = build_receipt(surface, root, files, exclusions)
    except SurfaceError as error:
        print(f"NO_SURFACE: {error}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps(receipt, indent=2))
    else:
        print(
            f"status={receipt['status']} scanned={len(receipt['scanned_files'])} "
            f"unscanned={len(receipt['unscanned_files'])} signals={len(receipt['signals'])}"
        )
        for item in receipt["signals"]:
            print(f"{item['path']}:{item['line']}: [{item['signal']}/{item['attribution']}] {item['question']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
