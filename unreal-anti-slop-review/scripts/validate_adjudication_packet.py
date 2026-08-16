#!/usr/bin/env python3
"""Validate structural closure of an Unreal adjudication V2 packet."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any


PACKET_SCHEMA = "unreal-adjudication/v2"
SURFACE_SCHEMA = "unreal-review-surface/v2"
ATTRIBUTIONS = {
    "introduced",
    "modified",
    "pre-existing",
    "context",
    "untracked",
    "generated",
    "unknown",
}
BRANCH_FIELDS = {
    "uobject": {
        "input",
        "runtime_type",
        "canonical_owner",
        "retention_gc",
        "cdo_archetype_phase",
        "reflected_persistence_path",
        "consumer",
        "destruction",
    },
    "registration": {
        "logical_owner",
        "current_source",
        "bound_source",
        "handles",
        "bind_point",
        "use",
        "exact_inverse",
        "replacement_path",
        "logical_terminal",
    },
    "async": {
        "request_owner",
        "captured_state",
        "destination_thread",
        "operation_identity",
        "cancellation",
        "stale_result_rejection",
        "reentrant_check",
        "world_teardown_guard",
        "terminal_state",
    },
    "shared-state": {
        "shared_object",
        "mutated_state",
        "saved_prior_state",
        "derived_side_effects",
        "restoration_paths",
        "concurrent_observers",
        "isolation",
        "terminal_state",
    },
    "editor-mutation": {
        "preflight",
        "transaction_owner",
        "modify_point",
        "first_persistent_write",
        "mutation_sequence",
        "notification",
        "dirtying",
        "save_policy",
        "failure_rollback",
        "success_terminal",
    },
    "loading-performance": {
        "activation",
        "phase_thread",
        "frequency",
        "scale",
        "operation_type",
        "retention_backpressure",
        "stop_condition",
        "cost_evidence",
    },
    "gameplay-networking": {
        "input_producer",
        "canonical_state_owner",
        "authority",
        "net_owner_connection",
        "prediction",
        "replication_relevancy",
        "consumer",
        "removal_rollback",
        "teardown",
    },
    "test-proof": {
        "failure_mode",
        "production_executor",
        "injected_dependency_seam",
        "trigger",
        "observable",
        "cleanup",
        "claimed_boundary",
        "false_substitute_excluded",
    },
    "engine-ownership": {
        "supplied_provenance",
        "exact_delta_claim",
        "extension_alternative",
        "product_neutral_owner",
        "irreversible_mutation",
        "callback_result",
        "rollback",
        "module_load_boundary",
        "merge_surface",
        "focused_regression",
    },
}
PROOF_BOUNDARIES = {
    "surface",
    "source-static",
    "compile-uht",
    "pure-automation",
    "engine-integration",
    "serialization-migration",
    "editor-authoring",
    "evaluated-asset",
    "pie-runtime",
    "networking",
    "cook-server-commandlet",
    "platform",
    "engine-fork",
}
PROOF_STATES = {"PROVED", "NOT_APPLICABLE", "GAP"}
DISPOSITIONS = {"FINDING", "GAP", "DISMISSED"}
REVIEW_MODES = {"named", "worktree", "branch", "pr", "engine-install", "engine-fork"}


def non_empty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def normalized(path: str) -> str:
    return path.replace("\\", "/").casefold()


def duplicate_values(values: list[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def validate_packet(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if packet.get("schema_version") != PACKET_SCHEMA:
        errors.append(f"unsupported packet schema: {packet.get('schema_version')!r}")

    surface = packet.get("surface")
    surface_paths: dict[str, dict[str, Any]] = {}
    if not isinstance(surface, dict):
        errors.append("surface must be an object")
        surface = {}
    if surface.get("schema_version") != SURFACE_SCHEMA:
        errors.append(f"unsupported surface schema: {surface.get('schema_version')!r}")
    if surface.get("review_mode") not in REVIEW_MODES:
        errors.append(f"surface.review_mode is invalid: {surface.get('review_mode')!r}")
    if not isinstance(surface.get("engine_provenance", {}), dict):
        errors.append("surface.engine_provenance must be an object")
    root_value = surface.get("root")
    root: Path | None = None
    if not non_empty(root_value):
        errors.append("surface.root must be a non-empty string")
    else:
        root = Path(root_value).resolve()
        if not root.is_dir():
            errors.append(f"surface.root is not a directory: {root}")
    files = surface.get("files")
    if not isinstance(files, list) or not files:
        errors.append("surface.files must be a non-empty list")
        files = []
    for index, entry in enumerate(files):
        if not isinstance(entry, dict):
            errors.append(f"surface.files[{index}] must be an object")
            continue
        path = entry.get("path")
        attribution = entry.get("attribution")
        scan = entry.get("scan")
        if not non_empty(path):
            errors.append(f"surface.files[{index}].path must be non-empty")
            continue
        key = normalized(path)
        if key in surface_paths:
            errors.append(f"duplicate surface file: {path}")
        surface_paths[key] = entry
        candidate = Path(path)
        if candidate.is_absolute():
            errors.append(f"surface file path must be relative: {path}")
        elif root is not None and root.is_dir():
            resolved = (root / candidate).resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                errors.append(f"surface file escapes root: {path}")
            else:
                if not resolved.is_file():
                    errors.append(f"surface file does not exist: {path}")
        if attribution not in ATTRIBUTIONS:
            errors.append(f"surface file has invalid attribution: {path}: {attribution!r}")
        if not isinstance(scan, bool):
            errors.append(f"surface file scan flag must be boolean: {path}")
    exclusions = surface.get("exclusions", [])
    if not isinstance(exclusions, list):
        errors.append("surface.exclusions must be a list")
    else:
        exclusion_keys: set[str] = set()
        for index, entry in enumerate(exclusions):
            if not isinstance(entry, dict) or not non_empty(entry.get("path")) or not non_empty(entry.get("reason")):
                errors.append(f"surface.exclusions[{index}] requires non-empty path and reason")
                continue
            candidate = Path(entry["path"])
            exclusion_key = normalized(entry["path"])
            if exclusion_key in exclusion_keys:
                errors.append(f"duplicate surface exclusion: {entry['path']}")
            exclusion_keys.add(exclusion_key)
            if exclusion_key in surface_paths:
                errors.append(f"path cannot be both selected and excluded: {entry['path']}")
            if candidate.is_absolute():
                errors.append(f"surface exclusion path must be relative: {entry['path']}")
            elif root is not None and root.is_dir():
                resolved = (root / candidate).resolve()
                try:
                    resolved.relative_to(root)
                except ValueError:
                    errors.append(f"surface exclusion escapes root: {entry['path']}")

    scanner = packet.get("scanner")
    if not isinstance(scanner, dict):
        errors.append("scanner must be an object")
        scanner = {}
    scanner_status = scanner.get("status")
    if scanner_status not in {"OK", "NOT_APPLICABLE"}:
        errors.append(f"scanner.status is invalid: {scanner_status!r}")
    scanned_files = scanner.get("scanned_files")
    unscanned_files = scanner.get("unscanned_files")
    signals = scanner.get("signals")
    if not isinstance(scanned_files, list):
        errors.append("scanner.scanned_files must be a list")
        scanned_files = []
    if not isinstance(unscanned_files, list):
        errors.append("scanner.unscanned_files must be a list")
        unscanned_files = []
    if not isinstance(signals, list):
        errors.append("scanner.signals must be a list")
        signals = []

    scanned_keys: set[str] = set()
    unscanned_keys: set[str] = set()
    for label, entries, target in (
        ("scanned", scanned_files, scanned_keys),
        ("unscanned", unscanned_files, unscanned_keys),
    ):
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict) or not non_empty(entry.get("path")):
                errors.append(f"scanner.{label}_files[{index}] requires a path")
                continue
            key = normalized(entry["path"])
            if key in target:
                errors.append(f"duplicate scanner {label} file: {entry['path']}")
            target.add(key)
    if scanned_keys & unscanned_keys:
        errors.append("a file appears in both scanner scanned and unscanned receipts")
    if scanned_keys | unscanned_keys != set(surface_paths):
        errors.append("scanner receipt does not account for every surface file exactly once")
    for key, entry in surface_paths.items():
        if entry.get("scan") is True and key not in scanned_keys:
            errors.append(f"scanner-eligible surface file was not scanned: {entry.get('path')}")
        if entry.get("scan") is False and key not in unscanned_keys:
            errors.append(f"scanner-ineligible surface file was not receipted as unscanned: {entry.get('path')}")
    if scanner_status == "NOT_APPLICABLE" and (scanned_keys or signals):
        errors.append("scanner NOT_APPLICABLE cannot contain scanned files or signals")
    if scanner_status == "OK" and not scanned_keys:
        errors.append("scanner OK requires at least one scanned file")

    signal_by_id: dict[str, dict[str, Any]] = {}
    for index, signal in enumerate(signals):
        if not isinstance(signal, dict):
            errors.append(f"scanner.signals[{index}] must be an object")
            continue
        signal_id = signal.get("signal_id")
        if not non_empty(signal_id):
            errors.append(f"scanner.signals[{index}].signal_id must be non-empty")
            continue
        if signal_id in signal_by_id:
            errors.append(f"duplicate signal ID: {signal_id}")
        signal_by_id[signal_id] = signal
        if normalized(str(signal.get("path", ""))) not in scanned_keys:
            errors.append(f"signal {signal_id} references an unscanned file")
        surface_entry = surface_paths.get(normalized(str(signal.get("path", ""))))
        if surface_entry is not None and signal.get("attribution") != surface_entry.get("attribution"):
            errors.append(f"signal {signal_id} attribution does not match the surface")
        if not isinstance(signal.get("line"), int) or signal.get("line", 0) < 1:
            errors.append(f"signal {signal_id} requires a positive line number")
        if not non_empty(signal.get("signal")):
            errors.append(f"signal {signal_id} requires a signal name")
        if not non_empty(signal.get("review_item_id")):
            errors.append(f"signal {signal_id} must map to review_item_id")

    applicability = packet.get("applicability")
    if not isinstance(applicability, list):
        errors.append("applicability must be a list")
        applicability = []
    app_by_branch: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(applicability):
        if not isinstance(entry, dict):
            errors.append(f"applicability[{index}] must be an object")
            continue
        branch = entry.get("branch")
        if branch not in BRANCH_FIELDS:
            errors.append(f"applicability[{index}] has invalid branch: {branch!r}")
            continue
        if branch in app_by_branch:
            errors.append(f"duplicate applicability branch: {branch}")
        app_by_branch[branch] = entry
        status = entry.get("status")
        if status not in {"APPLICABLE", "NOT_APPLICABLE"}:
            errors.append(f"applicability {branch} has invalid status: {status!r}")
        if not non_empty(entry.get("reason")):
            errors.append(f"applicability {branch} requires a reason")
        ledger_ids = entry.get("ledger_ids")
        if not isinstance(ledger_ids, list) or any(not non_empty(item) for item in ledger_ids):
            errors.append(f"applicability {branch}.ledger_ids must be a list of IDs")
            ledger_ids = []
        zero_owner_reason = entry.get("zero_owner_reason")
        if status == "APPLICABLE" and not ledger_ids and not non_empty(zero_owner_reason):
            errors.append(f"applicable branch {branch} needs ledger IDs or zero_owner_reason")
        if status == "NOT_APPLICABLE" and ledger_ids:
            errors.append(f"not-applicable branch {branch} cannot reference ledgers")
    missing_branches = set(BRANCH_FIELDS) - set(app_by_branch)
    extra_branches = set(app_by_branch) - set(BRANCH_FIELDS)
    if missing_branches:
        errors.append(f"missing applicability branches: {sorted(missing_branches)}")
    if extra_branches:
        errors.append(f"unknown applicability branches: {sorted(extra_branches)}")

    ledgers = packet.get("ledgers")
    if not isinstance(ledgers, list):
        errors.append("ledgers must be a list")
        ledgers = []
    ledger_by_id: dict[str, dict[str, Any]] = {}
    for index, ledger in enumerate(ledgers):
        if not isinstance(ledger, dict):
            errors.append(f"ledgers[{index}] must be an object")
            continue
        ledger_id = ledger.get("ledger_id")
        branch = ledger.get("branch")
        if not non_empty(ledger_id):
            errors.append(f"ledgers[{index}].ledger_id must be non-empty")
            continue
        if ledger_id in ledger_by_id:
            errors.append(f"duplicate ledger ID: {ledger_id}")
        ledger_by_id[ledger_id] = ledger
        if branch not in BRANCH_FIELDS:
            errors.append(f"ledger {ledger_id} has invalid branch: {branch!r}")
            continue
        if not non_empty(ledger.get("owner")):
            errors.append(f"ledger {ledger_id} requires an owner")
        fields = ledger.get("fields")
        if not isinstance(fields, dict):
            errors.append(f"ledger {ledger_id}.fields must be an object")
            fields = {}
        missing_fields = BRANCH_FIELDS[branch] - set(fields)
        if missing_fields:
            errors.append(f"ledger {ledger_id} missing typed fields: {sorted(missing_fields)}")
        for field in BRANCH_FIELDS[branch]:
            if field in fields and fields[field] in (None, "", [], {}):
                errors.append(f"ledger {ledger_id}.{field} must be explicit; use a reasoned NOT_APPLICABLE value")
        review_item_ids = ledger.get("review_item_ids")
        if not isinstance(review_item_ids, list) or any(not non_empty(item) for item in review_item_ids):
            errors.append(f"ledger {ledger_id}.review_item_ids must be a list of IDs")

    for branch, entry in app_by_branch.items():
        for ledger_id in entry.get("ledger_ids", []) if isinstance(entry.get("ledger_ids"), list) else []:
            ledger = ledger_by_id.get(ledger_id)
            if ledger is None:
                errors.append(f"applicability {branch} references missing ledger {ledger_id}")
            elif ledger.get("branch") != branch:
                errors.append(f"applicability {branch} references ledger {ledger_id} from branch {ledger.get('branch')}")
    for ledger_id, ledger in ledger_by_id.items():
        branch = ledger.get("branch")
        app = app_by_branch.get(branch)
        if app is None or ledger_id not in app.get("ledger_ids", []):
            errors.append(f"ledger {ledger_id} is not referenced by its applicability branch")

    items = packet.get("items")
    if not isinstance(items, list):
        errors.append("items must be a list")
        items = []
    item_by_id: dict[str, dict[str, Any]] = {}
    signal_to_items: dict[str, list[str]] = {signal_id: [] for signal_id in signal_by_id}
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"items[{index}] must be an object")
            continue
        item_id = item.get("item_id")
        if not non_empty(item_id):
            errors.append(f"items[{index}].item_id must be non-empty")
            continue
        if item_id in item_by_id:
            errors.append(f"duplicate item ID: {item_id}")
        item_by_id[item_id] = item
        if item.get("attribution") not in ATTRIBUTIONS:
            errors.append(f"item {item_id} has invalid attribution: {item.get('attribution')!r}")
        disposition = item.get("disposition")
        if disposition not in DISPOSITIONS:
            errors.append(f"item {item_id} has invalid disposition: {disposition!r}")
        for field in ("invariant", "mechanism", "owner"):
            if not non_empty(item.get(field)):
                errors.append(f"item {item_id}.{field} must be non-empty")
        evidence = item.get("evidence")
        if not isinstance(evidence, list) or not evidence or any(not non_empty(value) for value in evidence):
            errors.append(f"item {item_id}.evidence must be a non-empty list")
        if disposition == "FINDING":
            if not non_empty(item.get("consequence")) or not non_empty(item.get("remedy")):
                errors.append(f"finding {item_id} requires consequence and remedy")
            if item.get("item_gap") is not None:
                errors.append(f"finding {item_id} cannot have item_gap")
        elif disposition == "GAP":
            if not non_empty(item.get("item_gap")):
                errors.append(f"gap item {item_id} requires item_gap")
        elif disposition == "DISMISSED" and item.get("item_gap") is not None:
            errors.append(f"dismissed item {item_id} cannot have item_gap")

        origin = item.get("origin")
        if not isinstance(origin, dict) or origin.get("kind") not in {"SIGNAL", "MANUAL"}:
            errors.append(f"item {item_id}.origin must have kind SIGNAL or MANUAL")
            origin = {}
        signal_ids = origin.get("signal_ids", [])
        if not isinstance(signal_ids, list) or any(not non_empty(value) for value in signal_ids):
            errors.append(f"item {item_id}.origin.signal_ids must be a list")
            signal_ids = []
        if origin.get("kind") == "SIGNAL" and not signal_ids:
            errors.append(f"signal-origin item {item_id} requires signal IDs")
        if origin.get("kind") == "MANUAL" and signal_ids:
            errors.append(f"manual item {item_id} cannot reference signal IDs")
        for signal_id in signal_ids:
            if signal_id not in signal_by_id:
                errors.append(f"item {item_id} references missing signal {signal_id}")
            else:
                signal_to_items[signal_id].append(item_id)

        proof = item.get("proof")
        if not isinstance(proof, dict):
            errors.append(f"item {item_id}.proof must be an object")
            proof = {}
        for required in ("surface", "source-static"):
            if required not in proof:
                errors.append(f"item {item_id}.proof missing {required}")
        for boundary, state in proof.items():
            if boundary not in PROOF_BOUNDARIES:
                errors.append(f"item {item_id} has unknown proof boundary: {boundary}")
            if state not in PROOF_STATES:
                errors.append(f"item {item_id} proof {boundary} has invalid state: {state!r}")

    for signal_id, signal in signal_by_id.items():
        mapped = signal_to_items.get(signal_id, [])
        expected_item = signal.get("review_item_id")
        if mapped != [expected_item]:
            errors.append(f"signal {signal_id} must map to exactly its declared item {expected_item}; got {mapped}")
    for ledger_id, ledger in ledger_by_id.items():
        for item_id in ledger.get("review_item_ids", []) if isinstance(ledger.get("review_item_ids"), list) else []:
            if item_id not in item_by_id:
                errors.append(f"ledger {ledger_id} references missing item {item_id}")
    item_to_ledgers: dict[str, list[str]] = {item_id: [] for item_id in item_by_id}
    for ledger_id, ledger in ledger_by_id.items():
        for item_id in ledger.get("review_item_ids", []) if isinstance(ledger.get("review_item_ids"), list) else []:
            if item_id in item_to_ledgers:
                item_to_ledgers[item_id].append(ledger_id)
    for item_id, ledger_ids in item_to_ledgers.items():
        if not ledger_ids:
            errors.append(f"review item {item_id} is not owned by any typed ledger")

    residual = packet.get("residual_gaps")
    if not isinstance(residual, list):
        errors.append("residual_gaps must be a list")
        residual = []
    actual_gap_keys: list[tuple[str, str, str | None]] = []
    for index, gap in enumerate(residual):
        if not isinstance(gap, dict):
            errors.append(f"residual_gaps[{index}] must be an object")
            continue
        scope = gap.get("scope")
        item_id = gap.get("item_id")
        boundary = gap.get("boundary")
        if scope not in {"ITEM", "PROOF"}:
            errors.append(f"residual gap has invalid scope: {scope!r}")
            continue
        if item_id not in item_by_id:
            errors.append(f"residual gap references missing item: {item_id!r}")
        if scope == "ITEM" and boundary is not None:
            errors.append(f"ITEM residual gap for {item_id} cannot have a boundary")
        if scope == "PROOF" and boundary not in PROOF_BOUNDARIES:
            errors.append(f"PROOF residual gap for {item_id} has invalid boundary: {boundary!r}")
        if not non_empty(gap.get("missing_artifact")) or not non_empty(gap.get("closest_evidence")):
            errors.append(f"residual gap for {item_id} requires missing_artifact and closest_evidence")
        actual_gap_keys.append((scope, item_id, boundary))
    if duplicate_values([repr(value) for value in actual_gap_keys]):
        errors.append("duplicate residual gap entries")

    expected_gap_keys: set[tuple[str, str, str | None]] = set()
    for item_id, item in item_by_id.items():
        if item.get("disposition") == "GAP":
            expected_gap_keys.add(("ITEM", item_id, None))
        proof = item.get("proof", {})
        if isinstance(proof, dict):
            for boundary, state in proof.items():
                if state == "GAP":
                    expected_gap_keys.add(("PROOF", item_id, boundary))
    if set(actual_gap_keys) != expected_gap_keys:
        errors.append(
            f"residual gaps do not exactly match item/proof gaps; expected {sorted(expected_gap_keys)}, got {sorted(set(actual_gap_keys))}"
        )

    if packet.get("process_status") != "ADJUDICATION COMPLETE":
        errors.append("final validated packet must report ADJUDICATION COMPLETE")
    finding_count = sum(item.get("disposition") == "FINDING" for item in item_by_id.values())
    if finding_count:
        expected_outcome = "FINDINGS PRESENT"
    elif expected_gap_keys:
        expected_outcome = "GAPS ONLY"
    else:
        expected_outcome = "NO FINDINGS OR GAPS"
    if packet.get("outcome") != expected_outcome:
        errors.append(f"outcome must be {expected_outcome!r}, got {packet.get('outcome')!r}")

    return errors


def valid_self_test_packet(root: Path) -> dict[str, Any]:
    source = root / "Example.cpp"
    source.write_text("auto* Owner = CastChecked<APawn>(GetOwner());\n", encoding="utf-8")
    fields = {field: "NOT_APPLICABLE: fixture field" for field in BRANCH_FIELDS["uobject"]}
    fields.update(
        {
            "input": "GetOwner() at lifecycle use",
            "runtime_type": "AActor supplied by authored attachment",
            "canonical_owner": "UExampleComponent",
        }
    )
    applicability = []
    for branch in BRANCH_FIELDS:
        if branch == "uobject":
            applicability.append(
                {
                    "branch": branch,
                    "status": "APPLICABLE",
                    "reason": "Lifecycle owner cast exists.",
                    "ledger_ids": ["LED-0001"],
                    "zero_owner_reason": None,
                }
            )
        else:
            applicability.append(
                {
                    "branch": branch,
                    "status": "NOT_APPLICABLE",
                    "reason": "The fixture does not cross this contract.",
                    "ledger_ids": [],
                    "zero_owner_reason": None,
                }
            )
    return {
        "schema_version": PACKET_SCHEMA,
        "surface": {
            "schema_version": SURFACE_SCHEMA,
            "root": str(root),
            "review_mode": "named",
            "files": [{"path": source.name, "attribution": "unknown", "scan": True}],
            "exclusions": [],
            "engine_provenance": {},
        },
        "scanner": {
            "status": "OK",
            "scanned_files": [{"path": source.name, "attribution": "unknown"}],
            "unscanned_files": [],
            "signals": [
                {
                    "signal_id": "SIG-0001",
                    "path": source.name,
                    "line": 1,
                    "signal": "hard-cast-invariant",
                    "attribution": "unknown",
                    "review_item_id": "ITEM-0001",
                }
            ],
        },
        "applicability": applicability,
        "ledgers": [
            {
                "ledger_id": "LED-0001",
                "branch": "uobject",
                "owner": "UExampleComponent",
                "fields": fields,
                "review_item_ids": ["ITEM-0001"],
            }
        ],
        "items": [
            {
                "item_id": "ITEM-0001",
                "origin": {"kind": "SIGNAL", "signal_ids": ["SIG-0001"]},
                "attribution": "unknown",
                "disposition": "FINDING",
                "invariant": "Lifecycle owner type must be validated or enforced.",
                "evidence": [f"{source.name}:1"],
                "mechanism": "Authored attachment can supply a non-pawn owner.",
                "consequence": "The lifecycle callback can assert or crash.",
                "owner": "UExampleComponent",
                "remedy": "Validate recoverably or enforce every creation path.",
                "item_gap": None,
                "proof": {"surface": "PROVED", "source-static": "PROVED", "pie-runtime": "GAP"},
            }
        ],
        "residual_gaps": [
            {
                "scope": "PROOF",
                "item_id": "ITEM-0001",
                "boundary": "pie-runtime",
                "missing_artifact": "PIE reproduction with a non-pawn owner.",
                "closest_evidence": "Lifecycle source and Blueprint-spawnable construction path.",
            }
        ],
        "process_status": "ADJUDICATION COMPLETE",
        "outcome": "FINDINGS PRESENT",
    }


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as directory:
        packet = valid_self_test_packet(Path(directory))
        errors = validate_packet(packet)
        if errors:
            for error in errors:
                print(f"SELF_TEST_ERROR: {error}", file=sys.stderr)
            return 1
        packet["scanner"]["signals"][0]["review_item_id"] = "ITEM-MISSING"
        if not validate_packet(packet):
            print("SELF_TEST_ERROR: broken cross-reference was accepted", file=sys.stderr)
            return 1
    print("packet validator self-test OK")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", nargs="?", help="Adjudication packet JSON")
    parser.add_argument("--self-test", action="store_true", help="Run built-in valid and invalid fixtures")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if not args.packet:
        print("packet path is required unless --self-test is used", file=sys.stderr)
        return 2
    path = Path(args.packet)
    try:
        packet = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"PACKET_INVALID: cannot read {path}: {error}", file=sys.stderr)
        return 2
    if not isinstance(packet, dict):
        print("PACKET_INVALID: packet root must be an object", file=sys.stderr)
        return 2
    errors = validate_packet(packet)
    if errors:
        for error in errors:
            print(f"PACKET_INVALID: {error}", file=sys.stderr)
        return 2
    print("adjudication packet valid: ADJUDICATION COMPLETE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
