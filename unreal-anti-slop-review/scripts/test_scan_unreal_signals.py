#!/usr/bin/env python3
"""Deterministic fixtures for scan_unreal_signals.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


SCANNER = Path(__file__).with_name("scan_unreal_signals.py")


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCANNER), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def write_manifest(root: Path, files: list[dict[str, object]]) -> Path:
    path = root / "surface.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "unreal-review-surface/v2",
                "root": str(root),
                "review_mode": "named",
                "files": files,
                "exclusions": [{"path": "Excluded", "reason": "Outside the named surface."}],
                "engine_provenance": {},
            }
        ),
        encoding="utf-8",
    )
    return path


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        positive = root / "Positive.cpp"
        positive.write_text(
            """
void UThing::Tick(float DeltaSeconds) {}
auto* Owner = CastChecked<APawn>(GetOwner());
Handle = Source->AddRaw(
    this,
    &FThing::OnChanged);
auto* Defaults = GetMutableDefault<UThingSettings>();
AsyncTask(
    ENamedThreads::GameThread,
    []() {});
Asset.LoadSynchronous();
Path.TryLoad();
""".strip(),
            encoding="utf-8",
        )
        safe = root / "SafeNearMiss.cpp"
        safe.write_text(
            """
// CastChecked<APawn>(GetOwner());
const TCHAR* Text = TEXT("LoadSynchronous AddRaw GetMutableDefault<UThing>");
const auto Token = 'LoadSynchronous';
Source->AddUObject(this, &UThing::OnChanged);
TWeakObjectPtr<UObject> Weak;
""".strip(),
            encoding="utf-8",
        )
        build = root / "Module.Build.cs"
        build.write_text("public class Module : ModuleRules {}", encoding="utf-8")
        producer_test = root / "ProducerTests.cpp"
        producer_test.write_text("OnChanged.Broadcast();\n", encoding="utf-8")

        manifest = write_manifest(
            root,
            [
                {"path": positive.name, "attribution": "introduced", "scan": True},
                {"path": safe.name, "attribution": "context", "scan": True},
                {"path": producer_test.name, "attribution": "context", "scan": True},
                {"path": build.name, "attribution": "context", "scan": False},
            ],
        )
        result = run("--manifest", str(manifest))
        require(result.returncode == 0, result.stderr)
        receipt = json.loads(result.stdout)
        emitted = {(item["path"], item["signal"]) for item in receipt["signals"]}
        expected = {
            (positive.name, "tick-definition"),
            (positive.name, "hard-cast-invariant"),
            (positive.name, "raw-callback-registration"),
            (positive.name, "mutable-default-access"),
            (positive.name, "deferred-work"),
            (positive.name, "synchronous-load"),
            (producer_test.name, "test-direct-broadcast"),
        }
        require(emitted == expected, f"unexpected signals: {sorted(emitted)}")
        require(receipt["unscanned_files"][0]["path"] == build.name, "unscanned file was not receipted")
        require(all(item["path"] != safe.name for item in receipt["signals"]), "safe near-miss emitted a signal")
        require([item["signal_id"] for item in receipt["signals"]] == [f"SIG-{i:04d}" for i in range(1, 9)], "IDs are unstable")

        empty = write_manifest(root, [])
        require(run("--manifest", str(empty)).returncode == 2, "empty surface did not fail closed")

        missing = write_manifest(root, [{"path": "Missing.cpp", "attribution": "unknown", "scan": True}])
        require(run("--manifest", str(missing)).returncode == 2, "missing file did not fail closed")

        duplicate = write_manifest(
            root,
            [
                {"path": positive.name, "attribution": "unknown", "scan": True},
                {"path": positive.name, "attribution": "unknown", "scan": True},
            ],
        )
        require(run("--manifest", str(duplicate)).returncode == 2, "duplicate file did not fail closed")

        unsupported = write_manifest(root, [{"path": build.name, "attribution": "unknown", "scan": True}])
        require(run("--manifest", str(unsupported)).returncode == 2, "unsupported scan type did not fail closed")

        outside = write_manifest(root, [{"path": "../Outside.cpp", "attribution": "unknown", "scan": True}])
        require(run("--manifest", str(outside)).returncode == 2, "outside-root path did not fail closed")

    print("scanner fixtures OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
