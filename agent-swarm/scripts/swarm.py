#!/usr/bin/env python3
"""Run a bounded set of local Codex or Claude worker packets.

The runner deliberately owns only packet validation, process launch, and result
capture. It does not implement a message bus, sandbox, Git workflow, or remote
service. A manifest is reviewed by the caller before execution; packets must
be explicitly approved unless ``--allow-unapproved`` is supplied.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Mapping, Sequence


class ManifestError(ValueError):
    """Raised when a manifest does not satisfy the runner contract."""


_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")
_PROVIDERS = {"codex", "claude"}


@dataclass(frozen=True)
class Packet:
    id: str
    owner: str
    prompt: str
    provider: str
    approved: bool = False
    cwd: Path | None = None
    timeout_seconds: float = 900.0
    args: tuple[str, ...] = ()
    result_file: str | None = None
    depends_on: tuple[str, ...] = ()


@dataclass(frozen=True)
class Manifest:
    packets: tuple[Packet, ...]
    max_workers: int = 1
    result_dir: Path | None = None
    source: Path | None = None
    executables: Mapping[str, str] = field(default_factory=dict)
    provider_args: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    capture_max_bytes: int | None = None


@dataclass
class PacketResult:
    id: str
    provider: str
    status: str
    command: list[str]
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""
    error: str | None = None
    started_at: str | None = None
    finished_at: str | None = None
    duration_seconds: float | None = None
    stdout_original_bytes: int = 0
    stdout_truncated: bool = False
    stdout_sha256: str = field(default_factory=lambda: hashlib.sha256(b"").hexdigest())
    stderr_original_bytes: int = 0
    stderr_truncated: bool = False
    stderr_sha256: str = field(default_factory=lambda: hashlib.sha256(b"").hexdigest())

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "provider": self.provider,
            "status": self.status,
            "command": self.command,
            "returncode": self.returncode,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "error": self.error,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_seconds": self.duration_seconds,
            "stdout_original_bytes": self.stdout_original_bytes,
            "stdout_truncated": self.stdout_truncated,
            "stdout_sha256": self.stdout_sha256,
            "stderr_original_bytes": self.stderr_original_bytes,
            "stderr_truncated": self.stderr_truncated,
            "stderr_sha256": self.stderr_sha256,
        }


def _as_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ManifestError(f"{name} must be an object")
    return value


def _string(obj: Mapping[str, Any], key: str, *, required: bool = True) -> str | None:
    value = obj.get(key)
    if value is None and not required:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"{key} must be a non-empty string")
    if "\0" in value:
        raise ManifestError(f"{key} must not contain NUL characters")
    return value.strip()


def _relative_result(path: str, packet_id: str) -> str:
    candidate = Path(path)
    if candidate.is_absolute() or ".." in candidate.parts or candidate.name != path:
        raise ManifestError(f"packet {packet_id}: result_file must be a simple file name")
    if candidate.suffix.lower() != ".json":
        raise ManifestError(f"packet {packet_id}: result_file must end in .json")
    if "\0" in path or any(char in path for char in '<>:"/\\|?*') or path.rstrip(" .") != path:
        raise ManifestError(f"packet {packet_id}: result_file contains Windows-unsafe characters")
    stem = candidate.stem.split(".", 1)[0].upper()
    if stem in {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}:
        raise ManifestError(f"packet {packet_id}: result_file uses a reserved Windows device name")
    return path


def _provider_arguments(value: Any) -> dict[str, tuple[str, ...]]:
    if not isinstance(value, Mapping):
        raise ManifestError("provider_args must be an object")
    normalized: dict[str, tuple[str, ...]] = {}
    for provider, args in value.items():
        if provider not in _PROVIDERS:
            raise ManifestError(f"provider_args has unsupported provider: {provider}")
        if not isinstance(args, list) or any(not isinstance(arg, str) or "\0" in arg for arg in args):
            raise ManifestError(f"provider_args.{provider} must be an array of strings")
        normalized[provider] = tuple(args)
    return normalized


def _validate_dependency_graph(packets: Sequence[Packet]) -> tuple[Packet, ...]:
    canonical_ids = {packet.id.casefold(): packet.id for packet in packets}
    normalized: list[Packet] = []
    for packet in packets:
        dependencies: list[str] = []
        seen: set[str] = set()
        for dependency in packet.depends_on:
            dependency_key = dependency.casefold()
            if dependency_key == packet.id.casefold():
                raise ManifestError(f"packet {packet.id}: depends_on cannot contain itself")
            if dependency_key in seen:
                raise ManifestError(f"packet {packet.id}: duplicate dependency: {dependency}")
            if dependency_key not in canonical_ids:
                raise ManifestError(f"packet {packet.id}: missing dependency: {dependency}")
            seen.add(dependency_key)
            dependencies.append(canonical_ids[dependency_key])
        normalized.append(replace(packet, depends_on=tuple(dependencies)))

    by_id = {packet.id: packet for packet in normalized}
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(packet_id: str) -> None:
        packet_state = state.get(packet_id, 0)
        if packet_state == 2:
            return
        if packet_state == 1:
            cycle_start = stack.index(packet_id)
            cycle = stack[cycle_start:] + [packet_id]
            raise ManifestError("dependency cycle: " + " -> ".join(cycle))
        state[packet_id] = 1
        stack.append(packet_id)
        for dependency in by_id[packet_id].depends_on:
            visit(dependency)
        stack.pop()
        state[packet_id] = 2

    for packet in normalized:
        visit(packet.id)
    return tuple(normalized)


def validate_manifest(data: Mapping[str, Any], *, base_dir: Path | None = None) -> Manifest:
    """Validate and normalize a decoded JSON manifest."""
    root = _as_mapping(data, "manifest")
    version = root.get("version", 1)
    if version != 1:
        raise ManifestError("version must be 1")
    raw_packets = root.get("packets")
    if not isinstance(raw_packets, list) or not raw_packets:
        raise ManifestError("packets must be a non-empty array")
    provider_default = root.get("provider", "codex")
    if not isinstance(provider_default, str) or provider_default not in _PROVIDERS:
        raise ManifestError("provider must be codex or claude")
    provider_args = _provider_arguments(root.get("provider_args", {}))

    capture_max_bytes = root.get("capture_max_bytes")
    if capture_max_bytes is not None and (
        isinstance(capture_max_bytes, bool)
        or not isinstance(capture_max_bytes, int)
        or not 0 <= capture_max_bytes <= 1073741824
    ):
        raise ManifestError("capture_max_bytes must be an integer from 0 to 1073741824")

    workers = root.get("max_workers", root.get("concurrency", 1))
    if isinstance(workers, bool) or not isinstance(workers, int) or not 1 <= workers <= 64:
        raise ManifestError("max_workers must be an integer from 1 to 64")
    require_approval = root.get("require_approval", True)
    if not isinstance(require_approval, bool):
        raise ManifestError("require_approval must be boolean")
    if not require_approval:
        raise ManifestError("require_approval cannot be disabled; use the explicit runtime override")

    raw_executables = root.get("executables", {})
    if not isinstance(raw_executables, Mapping):
        raise ManifestError("executables must be an object")
    executables: dict[str, str] = {}
    for provider, executable in raw_executables.items():
        if provider not in _PROVIDERS:
            raise ManifestError(f"executables has unsupported provider: {provider}")
        if not isinstance(executable, str) or not executable.strip() or "\0" in executable:
            raise ManifestError(f"executables.{provider} must be a non-empty string")
        executables[provider] = executable.strip()

    root_dir = base_dir or Path.cwd()
    raw_result_dir = root.get("result_dir")
    result_dir: Path | None = None
    if raw_result_dir is not None:
        if not isinstance(raw_result_dir, str) or not raw_result_dir.strip():
            raise ManifestError("result_dir must be a non-empty path")
        result_dir = Path(raw_result_dir)
        if not result_dir.is_absolute():
            result_dir = (root_dir / result_dir).resolve()

    packets: list[Packet] = []
    seen: set[str] = set()
    result_names: set[str] = set()
    for index, raw in enumerate(raw_packets):
        item = _as_mapping(raw, f"packets[{index}]")
        packet_id = _string(item, "id")
        assert packet_id is not None
        if not _ID_RE.fullmatch(packet_id):
            raise ManifestError(f"packet {packet_id}: id must match {_ID_RE.pattern}")
        packet_key = packet_id.casefold()
        if packet_key in seen:
            raise ManifestError(f"duplicate packet id: {packet_id}")
        seen.add(packet_key)
        owner = _string(item, "owner")
        prompt = _string(item, "prompt")
        assert owner is not None and prompt is not None
        provider = item.get("provider", provider_default)
        if not isinstance(provider, str) or provider not in _PROVIDERS:
            raise ManifestError(f"packet {packet_id}: provider must be codex or claude")
        approved = item.get("approved", False)
        if not isinstance(approved, bool):
            raise ManifestError(f"packet {packet_id}: approved must be boolean")
        timeout = item.get("timeout_seconds", 900.0)
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 0 < timeout <= 86400:
            raise ManifestError(f"packet {packet_id}: timeout_seconds must be in (0, 86400]")
        args = item.get("args", [])
        if not isinstance(args, list) or any(not isinstance(arg, str) or "\0" in arg for arg in args):
            raise ManifestError(f"packet {packet_id}: args must be an array of strings")
        depends_on = item.get("depends_on", [])
        if not isinstance(depends_on, list) or any(
            not isinstance(dependency, str) or not dependency.strip() or "\0" in dependency
            for dependency in depends_on
        ):
            raise ManifestError(f"packet {packet_id}: depends_on must be an array of non-empty packet IDs")
        cwd = item.get("cwd")
        cwd_path: Path | None = None
        if cwd is not None:
            if not isinstance(cwd, str) or not cwd.strip():
                raise ManifestError(f"packet {packet_id}: cwd must be a path")
            cwd_path = Path(cwd)
            if not cwd_path.is_absolute():
                cwd_path = (root_dir / cwd_path).resolve()
            if not cwd_path.is_dir():
                raise ManifestError(f"packet {packet_id}: cwd does not exist: {cwd_path}")
        result_file = item.get("result_file")
        if result_file is not None:
            if not isinstance(result_file, str):
                raise ManifestError(f"packet {packet_id}: result_file must be a string")
            result_file = _relative_result(result_file, packet_id)
            if result_file == "summary.json":
                raise ManifestError(f"packet {packet_id}: result_file is reserved")
            result_key = result_file.casefold()
        else:
            result_file_default = _relative_result(f"{packet_id}.json", packet_id)
            result_key = result_file_default.casefold()
        if result_key == "summary.json" or result_key in result_names:
            raise ManifestError(f"packet {packet_id}: result file collides with another result or summary.json")
        result_names.add(result_key)
        packets.append(
            Packet(
                packet_id,
                owner,
                prompt,
                provider,
                approved,
                cwd_path,
                float(timeout),
                tuple(args),
                result_file,
                tuple(dependency.strip() for dependency in depends_on),
            )
        )
    return Manifest(
        _validate_dependency_graph(packets),
        workers,
        result_dir,
        executables=executables,
        provider_args=provider_args,
        capture_max_bytes=capture_max_bytes,
    )


def load_manifest(path: str | Path) -> Manifest:
    path = Path(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"cannot read manifest {path}: {exc}") from exc
    return validate_manifest(data, base_dir=path.parent.resolve())


def build_command(
    packet: Packet,
    executables: Mapping[str, str] | None = None,
    provider_args: Mapping[str, Sequence[str]] | None = None,
) -> list[str]:
    """Build an argv list; no shell interpolation is performed."""
    names = {"codex": "codex", "claude": "claude"}
    if executables:
        names.update(executables)
    executable = shutil.which(names[packet.provider]) or names[packet.provider]
    root_args = tuple(provider_args.get(packet.provider, ())) if provider_args else ()
    if packet.provider == "codex":
        return [executable, "exec", *root_args, *packet.args, packet.prompt]
    return [executable, *root_args, *packet.args, "-p", packet.prompt]


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds")


def _file_evidence(stream: Any, capture_max_bytes: int | None) -> tuple[str, int, bool, str]:
    stream.seek(0)
    digest = hashlib.sha256()
    retained = bytearray()
    original_bytes = 0
    while True:
        chunk = stream.read(65536)
        if not chunk:
            break
        original_bytes += len(chunk)
        digest.update(chunk)
        if capture_max_bytes is None:
            retained.extend(chunk)
        elif len(retained) < capture_max_bytes:
            retained.extend(chunk[: capture_max_bytes - len(retained)])
    return (
        retained.decode("utf-8", errors="replace"),
        original_bytes,
        len(retained) < original_bytes,
        digest.hexdigest(),
    )


def _apply_file_evidence(
    result: PacketResult,
    stdout_stream: Any,
    stderr_stream: Any,
    capture_max_bytes: int | None,
) -> None:
    (
        result.stdout,
        result.stdout_original_bytes,
        result.stdout_truncated,
        result.stdout_sha256,
    ) = _file_evidence(stdout_stream, capture_max_bytes)
    (
        result.stderr,
        result.stderr_original_bytes,
        result.stderr_truncated,
        result.stderr_sha256,
    ) = _file_evidence(stderr_stream, capture_max_bytes)


def _execute(
    packet: Packet,
    *,
    executables: Mapping[str, str] | None = None,
    provider_args: Mapping[str, Sequence[str]] | None = None,
    capture_max_bytes: int | None = None,
) -> PacketResult:
    command = build_command(packet, executables, provider_args)
    started = time.monotonic()
    started_at = _now()
    process = None
    cleanup_confirmed = False
    try:
        process_group: dict[str, Any] = {}
        if os.name == "nt":
            process_group["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            process_group["start_new_session"] = True
        with tempfile.TemporaryFile() as stdout_stream, tempfile.TemporaryFile() as stderr_stream:
            try:
                process = subprocess.Popen(
                    command,
                    cwd=packet.cwd,
                    stdout=stdout_stream,
                    stderr=stderr_stream,
                    **process_group,
                )
                process.wait(timeout=packet.timeout_seconds)
                status = "succeeded" if process.returncode == 0 else "failed"
                result = PacketResult(packet.id, packet.provider, status, command, process.returncode)
            except subprocess.TimeoutExpired:
                if process is not None:
                    cleanup_confirmed = _terminate_process_tree(process)
                    try:
                        process.wait(timeout=5)
                    except (OSError, subprocess.TimeoutExpired):
                        pass
                timeout_status = "timed_out" if cleanup_confirmed else "cleanup_unconfirmed"
                result = PacketResult(
                    packet.id,
                    packet.provider,
                    timeout_status,
                    command,
                    None,
                    error="process timed out; descendant cleanup confirmed" if cleanup_confirmed else "process timed out; unsafe state, descendants may still be running",
                )
            _apply_file_evidence(result, stdout_stream, stderr_stream, capture_max_bytes)
    except (OSError, ValueError) as exc:
        result = PacketResult(packet.id, packet.provider, "failed", command, None, error=str(exc))
    result.started_at = started_at
    result.finished_at = _now()
    result.duration_seconds = round(time.monotonic() - started, 6)
    return result


def _terminate_process_tree(process: subprocess.Popen[Any]) -> bool:
    """Terminate a timed-out worker and its descendants without a shell."""
    if os.name == "nt":
        try:
            completed = subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            if completed.returncode == 0:
                return True
        except OSError:
            pass
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
            return True
        except OSError:
            pass
    try:
        process.kill()
    except OSError:
        pass
    return False


def _preflight_executables(manifest: Manifest, executables: Mapping[str, str]) -> dict[str, str]:
    resolved = dict(executables)
    for provider in sorted({packet.provider for packet in manifest.packets}):
        candidate = resolved.get(provider, provider)
        executable = shutil.which(candidate)
        if executable is None:
            raise ManifestError(f"provider executable is unavailable: {provider} ({candidate})")
        resolved[provider] = executable
    return resolved


def _run_dependency_graph(
    manifest: Manifest,
    command_executables: Mapping[str, str],
) -> list[PacketResult]:
    packet_order = {packet.id: index for index, packet in enumerate(manifest.packets)}
    pending = {packet.id: packet for packet in manifest.packets}
    completed: dict[str, PacketResult] = {}
    running: dict[concurrent.futures.Future[PacketResult], Packet] = {}
    results: list[PacketResult] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=min(manifest.max_workers, len(manifest.packets))) as pool:
        while pending or running:
            for packet in tuple(pending.values()):
                if not all(dependency in completed for dependency in packet.depends_on):
                    continue
                failed_dependencies = [
                    dependency
                    for dependency in packet.depends_on
                    if completed[dependency].status != "succeeded"
                ]
                if failed_dependencies:
                    details = ", ".join(
                        f"{dependency}={completed[dependency].status}"
                        for dependency in failed_dependencies
                    )
                    result = PacketResult(
                        packet.id,
                        packet.provider,
                        "blocked",
                        build_command(packet, command_executables, manifest.provider_args),
                        error=f"blocked by unsuccessful dependencies: {details}",
                    )
                    completed[packet.id] = result
                    results.append(result)
                    del pending[packet.id]

            available_slots = manifest.max_workers - len(running)
            if available_slots > 0:
                ready = [
                    packet
                    for packet in pending.values()
                    if all(
                        dependency in completed and completed[dependency].status == "succeeded"
                        for dependency in packet.depends_on
                    )
                ]
                for packet in ready[:available_slots]:
                    future = pool.submit(
                        _execute,
                        packet,
                        executables=command_executables,
                        provider_args=manifest.provider_args,
                        capture_max_bytes=manifest.capture_max_bytes,
                    )
                    running[future] = packet
                    del pending[packet.id]

            if running:
                done, _ = concurrent.futures.wait(
                    running,
                    return_when=concurrent.futures.FIRST_COMPLETED,
                )
                for future in sorted(done, key=lambda item: packet_order[running[item].id]):
                    packet = running.pop(future)
                    result = future.result()
                    completed[packet.id] = result
                    results.append(result)
            elif pending:
                raise RuntimeError("validated dependency graph made no scheduling progress")
    return results


def run_manifest(manifest: Manifest, *, dry_run: bool = False, allow_unapproved: bool = False, output_dir: str | Path | None = None, executables: Mapping[str, str] | None = None) -> dict[str, Any]:
    """Execute packets and persist deterministic JSON results when requested."""
    if not allow_unapproved and not dry_run:
        blocked = [packet.id for packet in manifest.packets if not packet.approved]
        if blocked:
            raise ManifestError("unapproved packets: " + ", ".join(blocked))
    command_executables = dict(manifest.executables)
    if executables:
        command_executables.update(executables)
    results: list[PacketResult] = []
    if dry_run:
        results = [
            PacketResult(
                p.id,
                p.provider,
                "dry-run",
                build_command(p, command_executables, manifest.provider_args),
            )
            for p in manifest.packets
        ]
    else:
        command_executables = _preflight_executables(manifest, command_executables)
        results = _run_dependency_graph(manifest, command_executables)
    results.sort(key=lambda item: item.id)
    summary = {
        "version": 1,
        "dry_run": dry_run,
        "max_workers": manifest.max_workers,
        "results": [result.as_dict() for result in results],
        "succeeded": sum(result.status == "succeeded" for result in results),
        "failed": sum(result.status in {"failed", "timed_out", "cleanup_unconfirmed", "blocked"} for result in results),
    }
    destination = Path(output_dir) if output_dir is not None else manifest.result_dir
    if destination is not None:
        destination = destination.resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise ManifestError("output already exists; choose a new output directory")
        staging = Path(tempfile.mkdtemp(prefix=f".{destination.name}.", dir=destination.parent))
        output_paths = []
        for result in results:
            packet = next(p for p in manifest.packets if p.id == result.id)
            name = packet.result_file or f"{packet.id}.json"
            output_paths.append(staging / name)
        output_paths.append(staging / "summary.json")
        payloads = [json.dumps(result.as_dict(), indent=2, sort_keys=True) + "\n" for result in results]
        payloads.append(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        try:
            for path, payload in zip(output_paths, payloads):
                with path.open("w", encoding="utf-8", newline="\n") as handle:
                    handle.write(payload)
                    handle.flush()
                    os.fsync(handle.fileno())
            os.replace(staging, destination)
        finally:
            if staging.exists():
                shutil.rmtree(staging)
    return summary


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("validate", "run"):
        command = sub.add_parser(action)
        command.add_argument("--manifest", required=True, type=Path)
        command.add_argument("--output-dir", type=Path)
        command.add_argument("--dry-run", action="store_true")
        command.add_argument("--allow-unapproved", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        manifest = load_manifest(args.manifest)
        if args.action == "validate":
            print(json.dumps({"valid": True, "packets": len(manifest.packets), "max_workers": manifest.max_workers}, sort_keys=True))
            return 0
        summary = run_manifest(manifest, dry_run=args.dry_run, allow_unapproved=args.allow_unapproved, output_dir=args.output_dir)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0 if summary["failed"] == 0 else 1
    except ManifestError as exc:
        print(f"manifest error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
