from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import threading
import time
from pathlib import Path
from unittest import TestCase, mock


MODULE_PATH = Path(__file__).with_name("swarm.py")
SPEC = importlib.util.spec_from_file_location("agent_swarm_swarm", MODULE_PATH)
assert SPEC and SPEC.loader
swarm = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = swarm
SPEC.loader.exec_module(swarm)


class ManifestTests(TestCase):
    def test_valid_manifest_normalizes_paths_and_defaults(self):
        manifest = swarm.validate_manifest(
            {
                "packets": [{"id": "one", "owner": "alice", "prompt": "hello"}],
                "result_dir": "out",
            },
            base_dir=Path("C:/workspace"),
        )
        self.assertEqual(manifest.max_workers, 1)
        self.assertEqual(manifest.packets[0].provider, "codex")
        self.assertEqual(manifest.packets[0].depends_on, ())
        self.assertEqual(manifest.provider_args, {})
        self.assertIsNone(manifest.capture_max_bytes)
        self.assertEqual(manifest.result_dir, (Path("C:/workspace") / "out").resolve())

    def test_rejects_duplicate_ids_and_unsafe_result_file(self):
        base = {"packets": [{"id": "one", "owner": "a", "prompt": "x"}]}
        with self.assertRaises(swarm.ManifestError):
            swarm.validate_manifest({**base, "packets": base["packets"] * 2})
        with self.assertRaises(swarm.ManifestError):
            swarm.validate_manifest({"packets": [{"id": "one", "owner": "a", "prompt": "x", "result_file": "../x.json"}]})
        with self.assertRaises(swarm.ManifestError):
            swarm.validate_manifest({"packets": [
                {"id": "one", "owner": "a", "prompt": "x", "result_file": "same.json"},
                {"id": "two", "owner": "b", "prompt": "y", "result_file": "same.json"},
            ]})
        with self.assertRaises(swarm.ManifestError):
            swarm.validate_manifest({"packets": [{"id": "one", "owner": "a", "prompt": "x", "result_file": "summary.json"}]})
        with self.assertRaises(swarm.ManifestError):
            swarm.validate_manifest({"packets": [
                {"id": "one", "owner": "a", "prompt": "x", "result_file": "A.json"},
                {"id": "two", "owner": "b", "prompt": "y", "result_file": "a.JSON"},
            ]})
        with self.assertRaises(swarm.ManifestError):
            swarm.validate_manifest({"packets": [{"id": "one", "owner": "a", "prompt": "x", "result_file": "CON.json"}]})
        with self.assertRaises(swarm.ManifestError):
            swarm.validate_manifest({"packets": [{"id": "CON", "owner": "a", "prompt": "x"}]})
        with self.assertRaises(swarm.ManifestError):
            swarm.validate_manifest({"packets": [
                {"id": "A", "owner": "a", "prompt": "x"},
                {"id": "a", "owner": "b", "prompt": "y"},
            ]})

    def test_approval_gate_is_explicit(self):
        manifest = swarm.validate_manifest({"packets": [{"id": "one", "owner": "a", "prompt": "x"}]})
        result = swarm.run_manifest(manifest, dry_run=True)
        self.assertEqual(result["results"][0]["status"], "dry-run")
        with self.assertRaisesRegex(swarm.ManifestError, "unapproved"):
            swarm.run_manifest(manifest)
        with self.assertRaisesRegex(swarm.ManifestError, "cannot be disabled"):
            swarm.validate_manifest({"require_approval": False, "packets": [{"id": "one", "owner": "a", "prompt": "x"}]})

    def test_rejects_malformed_provider_and_nul_arguments(self):
        with self.assertRaises(swarm.ManifestError):
            swarm.validate_manifest({"provider": [], "packets": [{"id": "one", "owner": "a", "prompt": "x"}]})
        with self.assertRaises(swarm.ManifestError):
            swarm.validate_manifest({"packets": [{"id": "one", "owner": "a", "prompt": "x", "provider": {}}]})
        with self.assertRaises(swarm.ManifestError):
            swarm.validate_manifest({"packets": [{"id": "one", "owner": "a", "prompt": "x", "args": ["bad\0arg"]}]})
        with self.assertRaises(swarm.ManifestError):
            swarm.validate_manifest({"executables": {"codex": "bad\0path"}, "packets": [{"id": "one", "owner": "a", "prompt": "x"}]})
        with self.assertRaises(swarm.ManifestError):
            swarm.validate_manifest({"provider_args": {"codex": ["bad\0arg"]}, "packets": [{"id": "one", "owner": "a", "prompt": "x"}]})
        with self.assertRaises(swarm.ManifestError):
            swarm.validate_manifest({"capture_max_bytes": -1, "packets": [{"id": "one", "owner": "a", "prompt": "x"}]})

    def test_validates_and_normalizes_dependency_dag(self):
        manifest = swarm.validate_manifest({"packets": [
            {"id": "Research", "owner": "a", "prompt": "x"},
            {"id": "review", "owner": "b", "prompt": "y", "depends_on": ["research"]},
        ]})
        self.assertEqual(manifest.packets[1].depends_on, ("Research",))

        invalid_dependencies = (
            [{"id": "one", "owner": "a", "prompt": "x", "depends_on": ["missing"]}],
            [{"id": "one", "owner": "a", "prompt": "x", "depends_on": ["one"]}],
            [
                {"id": "one", "owner": "a", "prompt": "x"},
                {"id": "two", "owner": "b", "prompt": "y", "depends_on": ["one", "ONE"]},
            ],
            [
                {"id": "one", "owner": "a", "prompt": "x", "depends_on": ["two"]},
                {"id": "two", "owner": "b", "prompt": "y", "depends_on": ["one"]},
            ],
        )
        for packets in invalid_dependencies:
            with self.subTest(packets=packets), self.assertRaises(swarm.ManifestError):
                swarm.validate_manifest({"packets": packets})


class AdapterTests(TestCase):
    def test_builds_provider_commands_without_shell(self):
        codex = swarm.Packet("a", "o", "say 'hi'", "codex", args=("--json",))
        claude = swarm.Packet("b", "o", "say hi", "claude", args=("--model", "test"))
        self.assertEqual(swarm.build_command(codex, {"codex": "codex-test"}), ["codex-test", "exec", "--json", "say 'hi'"])
        self.assertEqual(swarm.build_command(claude, {"claude": "claude-test"}), ["claude-test", "--model", "test", "-p", "say hi"])

    def test_root_provider_args_precede_packet_args(self):
        manifest = swarm.validate_manifest({
            "provider_args": {
                "codex": ["--model", "root-model"],
                "claude": ["--verbose"],
            },
            "packets": [
                {"id": "a", "owner": "o", "prompt": "codex prompt", "args": ["--json"]},
                {"id": "b", "owner": "o", "prompt": "claude prompt", "provider": "claude", "args": ["--model", "packet-model"]},
            ],
        })
        self.assertEqual(
            swarm.build_command(manifest.packets[0], {"codex": "codex-test"}, manifest.provider_args),
            ["codex-test", "exec", "--model", "root-model", "--json", "codex prompt"],
        )
        self.assertEqual(
            swarm.build_command(manifest.packets[1], {"claude": "claude-test"}, manifest.provider_args),
            ["claude-test", "--verbose", "--model", "packet-model", "-p", "claude prompt"],
        )

    def test_manifest_accepts_explicit_executable_map(self):
        manifest = swarm.validate_manifest({
            "executables": {"codex": r"C:\\Tools\\codex.cmd"},
            "packets": [{"id": "one", "owner": "a", "prompt": "x"}],
        })
        self.assertEqual(manifest.executables["codex"].lower().endswith("codex.cmd"), True)

    def test_resolves_default_provider_from_path(self):
        packet = swarm.Packet("a", "o", "prompt", "codex")
        with mock.patch.object(swarm.shutil, "which", return_value=r"C:\\Tools\\codex.cmd"):
            self.assertEqual(swarm.build_command(packet)[0], r"C:\\Tools\\codex.cmd")


class ExecutionTests(TestCase):
    def test_real_subprocess_capture_uses_bounded_result_evidence(self):
        script = "import sys; sys.stdout.buffer.write(b'abcdef'); sys.stderr.buffer.write(b'uvwxyz')"
        packet = swarm.Packet(
            "local",
            "owner",
            "ignored prompt",
            "claude",
            approved=True,
            args=("-c", script),
        )
        manifest = swarm.Manifest((packet,), capture_max_bytes=4)
        result = swarm.run_manifest(manifest, executables={"claude": sys.executable})["results"][0]
        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(result["stdout"], "abcd")
        self.assertEqual(result["stdout_original_bytes"], 6)
        self.assertTrue(result["stdout_truncated"])
        self.assertEqual(result["stderr"], "uvwx")
        self.assertEqual(result["stderr_original_bytes"], 6)
        self.assertTrue(result["stderr_truncated"])

    def test_bounded_parallel_execution_and_capture(self):
        packets = tuple(swarm.Packet(str(i), "owner", str(i), "codex", approved=True) for i in range(4))
        manifest = swarm.Manifest(packets, max_workers=2)
        active = 0
        peak = 0
        lock = threading.Lock()

        class FakeProcess:
            def __init__(self, command, **kwargs):
                self.command = command
                self.returncode = 0
                self.stdout = kwargs["stdout"]

            def wait(self, timeout=None):
                nonlocal active, peak
                with lock:
                    active += 1
                    peak = max(peak, active)
                time.sleep(0.02)
                with lock:
                    active -= 1
                self.stdout.write(("out:" + self.command[-1]).encode())
                return self.returncode

            def kill(self):
                self.returncode = -9

        with mock.patch.object(swarm, "_preflight_executables", return_value={"codex": "codex-test"}), mock.patch.object(swarm.subprocess, "Popen", side_effect=FakeProcess):
            summary = swarm.run_manifest(manifest)
        self.assertEqual(summary["succeeded"], 4)
        self.assertEqual(summary["failed"], 0)
        self.assertLessEqual(peak, 2)
        self.assertEqual([item["id"] for item in summary["results"]], ["0", "1", "2", "3"])

    def test_result_files_and_timeout_are_captured(self):
        packet = swarm.Packet("slow", "owner", "wait", "codex", approved=True, result_file="custom.json")
        manifest = swarm.Manifest((packet,), max_workers=1, result_dir=Path("."))
        with tempfile.TemporaryDirectory() as temp_root:
            output = Path(temp_root) / "results"

            class SlowProcess:
                pid = 123
                returncode = None

                def __init__(self, **kwargs):
                    self.stdout = kwargs["stdout"]
                    self.first_wait = True

                def wait(self, timeout=None):
                    if self.first_wait:
                        self.first_wait = False
                        self.stdout.write(b"partial")
                        raise swarm.subprocess.TimeoutExpired(["codex"], 1)
                    return self.returncode

                def kill(self):
                    self.returncode = -9

            with mock.patch.object(swarm, "_preflight_executables", return_value={"codex": "codex-test"}), mock.patch.object(swarm.subprocess, "Popen", side_effect=lambda command, **kwargs: SlowProcess(**kwargs)), mock.patch.object(swarm, "_terminate_process_tree", return_value=False):
                summary = swarm.run_manifest(manifest, output_dir=output)
            self.assertEqual(summary["results"][0]["status"], "cleanup_unconfirmed")
            self.assertIn("unsafe state", summary["results"][0]["error"])
            self.assertEqual(summary["results"][0]["stdout_original_bytes"], len(b"partial"))
            self.assertTrue((output / "custom.json").exists())
            self.assertEqual(json.loads((output / "summary.json").read_text())["failed"], 1)

    def test_execution_decodes_utf8_capture_and_records_bounded_provenance(self):
        packet = swarm.Packet("utf8", "owner", "say", "codex", approved=True)
        manifest = swarm.Manifest((packet,), capture_max_bytes=4)
        seen = {}
        stdout = b"abcdef"
        stderr = "\u2713".encode("utf-8")

        def fake_popen(command, **kwargs):
            seen.update(kwargs)
            process = mock.Mock(returncode=0)

            def wait(timeout=None):
                kwargs["stdout"].write(stdout)
                kwargs["stderr"].write(stderr)
                return 0

            process.wait = wait
            return process

        with mock.patch.object(swarm, "_preflight_executables", return_value={"codex": "codex-test"}), mock.patch.object(swarm.subprocess, "Popen", side_effect=fake_popen):
            packet_result = swarm.run_manifest(manifest)["results"][0]
        self.assertEqual(packet_result["stdout"], "abcd")
        self.assertEqual(packet_result["stdout_original_bytes"], len(stdout))
        self.assertTrue(packet_result["stdout_truncated"])
        self.assertEqual(packet_result["stdout_sha256"], hashlib.sha256(stdout).hexdigest())
        self.assertEqual(packet_result["stderr"], "\u2713")
        self.assertEqual(packet_result["stderr_original_bytes"], len(stderr))
        self.assertFalse(packet_result["stderr_truncated"])
        self.assertEqual(packet_result["stderr_sha256"], hashlib.sha256(stderr).hexdigest())
        self.assertNotIn("text", seen)

    def test_dependency_scheduler_blocks_without_launching_dependents(self):
        manifest = swarm.validate_manifest({"max_workers": 2, "packets": [
            {"id": "root", "owner": "a", "prompt": "x", "approved": True},
            {"id": "child", "owner": "b", "prompt": "y", "approved": True, "depends_on": ["root"]},
            {"id": "leaf", "owner": "c", "prompt": "z", "approved": True, "depends_on": ["child"]},
        ]})
        launched = []

        def fake_execute(packet, **kwargs):
            launched.append(packet.id)
            return swarm.PacketResult(packet.id, packet.provider, "failed", ["fake"])

        with tempfile.TemporaryDirectory() as temp_root, mock.patch.object(swarm, "_preflight_executables", return_value={"codex": "codex-test"}), mock.patch.object(swarm, "_execute", side_effect=fake_execute):
            output = Path(temp_root) / "results"
            summary = swarm.run_manifest(manifest, output_dir=output)
            persisted_child = json.loads((output / "child.json").read_text(encoding="utf-8"))
        self.assertEqual(launched, ["root"])
        self.assertEqual(
            {item["id"]: item["status"] for item in summary["results"]},
            {"child": "blocked", "leaf": "blocked", "root": "failed"},
        )
        self.assertEqual(summary["failed"], 3)
        self.assertEqual(persisted_child["status"], "blocked")
        self.assertIn("root=failed", persisted_child["error"])

    def test_dependency_scheduler_launches_ready_packets_in_manifest_order(self):
        manifest = swarm.validate_manifest({"max_workers": 1, "packets": [
            {"id": "root", "owner": "a", "prompt": "x", "approved": True},
            {"id": "child", "owner": "b", "prompt": "y", "approved": True, "depends_on": ["root"]},
            {"id": "independent", "owner": "c", "prompt": "z", "approved": True},
        ]})
        launched = []

        def fake_execute(packet, **kwargs):
            launched.append(packet.id)
            return swarm.PacketResult(packet.id, packet.provider, "succeeded", ["fake"])

        with mock.patch.object(swarm, "_preflight_executables", return_value={"codex": "codex-test"}), mock.patch.object(swarm, "_execute", side_effect=fake_execute):
            summary = swarm.run_manifest(manifest)
        self.assertEqual(launched, ["root", "child", "independent"])
        self.assertEqual(summary["succeeded"], 3)

    def test_real_run_preflights_all_providers_before_launch(self):
        manifest = swarm.validate_manifest({"packets": [
            {"id": "a", "owner": "o", "prompt": "x", "approved": True},
            {"id": "b", "owner": "o", "prompt": "y", "provider": "claude", "approved": True},
        ]})
        with mock.patch.object(swarm.shutil, "which", side_effect=lambda candidate: None if candidate == "claude" else "resolved-codex"), mock.patch.object(swarm.subprocess, "Popen") as popen:
            with self.assertRaisesRegex(swarm.ManifestError, "claude"):
                swarm.run_manifest(manifest)
        popen.assert_not_called()

        candidates = []

        def resolve(candidate):
            candidates.append(candidate)
            return f"resolved-{candidate}"

        with mock.patch.object(swarm.shutil, "which", side_effect=resolve):
            resolved = swarm._preflight_executables(manifest, {})
        self.assertEqual(candidates, ["claude", "codex"])
        self.assertEqual(resolved, {"claude": "resolved-claude", "codex": "resolved-codex"})

    def test_omitted_capture_limit_preserves_complete_stream(self):
        packet = swarm.Packet("full", "owner", "say", "codex", approved=True)
        manifest = swarm.Manifest((packet,))
        output = b"complete output"

        def fake_popen(command, **kwargs):
            process = mock.Mock(returncode=0)

            def wait(timeout=None):
                kwargs["stdout"].write(output)
                return 0

            process.wait = wait
            return process

        with mock.patch.object(swarm, "_preflight_executables", return_value={"codex": "codex-test"}), mock.patch.object(swarm.subprocess, "Popen", side_effect=fake_popen):
            result = swarm.run_manifest(manifest)["results"][0]
        self.assertEqual(result["stdout"], output.decode())
        self.assertFalse(result["stdout_truncated"])


if __name__ == "__main__":
    import unittest

    unittest.main()
