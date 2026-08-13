#!/usr/bin/env python3
"""Initialize, validate, and summarize a monkey-test fleet run ledger."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ISSUE_STATES = {
    "identified",
    "normalized",
    "assigned",
    "implementing",
    "review_spec",
    "review_engineering",
    "rework",
    "integration_ready",
    "integrated",
    "final_review",
    "cleared",
    "partial",
    "blocked",
    "roadmap",
    "unmeasured",
    "wont_fix",
}
TERMINAL_STATES = {
    "cleared",
    "partial",
    "blocked",
    "roadmap",
    "unmeasured",
    "wont_fix",
}
LANE_STATES = {
    "planned",
    "running",
    "committed",
    "reviewing",
    "rework",
    "cleared",
    "integrating",
    "integrated",
    "final_review",
    "complete",
    "errored",
    "blocked",
}
ACCEPTANCE_STATES = {"pending", "pass", "fail", "unmeasured", "not_applicable"}
REVIEW_VERDICTS = {"clear", "partial", "fail", "unmeasured"}
GATE_RESULTS = {"pass", "fail", "unmeasured", "not_applicable"}


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"ledger does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"invalid JSON at {path}:{exc.lineno}:{exc.colno}: {exc.msg}"
        ) from exc
    if not isinstance(value, dict):
        raise TypeError("ledger root must be a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )


def init_ledger(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir).expanduser().resolve()
    run_dir.mkdir(parents=True, exist_ok=False)
    ledger_path = run_dir / "ledger.json"
    run_id = args.run_id or run_dir.name
    ledger: dict[str, Any] = {
        "schema_version": 1,
        "run": {
            "id": run_id,
            "repo_root": str(Path(args.repo_root).expanduser().resolve()),
            "dossier": args.dossier,
            "base_revision": args.base_revision,
            "integration_revision": None,
            "deployment_revision": None,
            "status": "intake",
            "created_at": utc_now(),
            "authority": [],
            "protected_paths": [],
            "live_process_notes": [],
        },
        "issues": [],
        "lanes": [],
        "gates": [],
        "discoveries": [],
        "residuals": [],
        "events": [
            {
                "timestamp": utc_now(),
                "kind": "run_initialized",
                "summary": "Fleet ledger initialized",
            }
        ],
    }
    write_json(ledger_path, ledger)
    print(ledger_path)
    return 0


def require_list(value: Any, name: str, errors: list[str]) -> list[Any]:
    if not isinstance(value, list):
        errors.append(f"{name} must be a list")
        return []
    return value


def clear_review(reviews: Any, axis: str) -> bool:
    if not isinstance(reviews, dict):
        return False
    records = reviews.get(axis)
    if not isinstance(records, list):
        return False
    return any(
        isinstance(record, dict) and record.get("verdict") == "clear"
        for record in records
    )


def validate_ledger(data: dict[str, Any], strict: bool) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")

    run = data.get("run")
    if not isinstance(run, dict):
        errors.append("run must be an object")
        run = {}
    for field in (
        "id",
        "repo_root",
        "dossier",
        "base_revision",
        "status",
        "created_at",
    ):
        if not run.get(field):
            errors.append(f"run.{field} is required")

    issues = require_list(data.get("issues"), "issues", errors)
    lanes = require_list(data.get("lanes"), "lanes", errors)
    gates = require_list(data.get("gates"), "gates", errors)
    require_list(data.get("discoveries"), "discoveries", errors)
    require_list(data.get("residuals"), "residuals", errors)
    require_list(data.get("events"), "events", errors)

    issue_ids: set[str] = set()
    for index, issue in enumerate(issues):
        prefix = f"issues[{index}]"
        if not isinstance(issue, dict):
            errors.append(f"{prefix} must be an object")
            continue
        issue_id = issue.get("id")
        if not isinstance(issue_id, str) or not issue_id:
            errors.append(f"{prefix}.id is required")
        elif issue_id in issue_ids:
            errors.append(f"duplicate issue id: {issue_id}")
        else:
            issue_ids.add(issue_id)
        if not issue.get("title"):
            errors.append(f"{prefix}.title is required")
        state = issue.get("state")
        if state not in ISSUE_STATES:
            errors.append(f"{prefix}.state has invalid value: {state!r}")
        acceptance = require_list(
            issue.get("acceptance"), f"{prefix}.acceptance", errors
        )
        acceptance_ids: set[str] = set()
        for criterion_index, criterion in enumerate(acceptance):
            criterion_prefix = f"{prefix}.acceptance[{criterion_index}]"
            if not isinstance(criterion, dict):
                errors.append(f"{criterion_prefix} must be an object")
                continue
            criterion_id = criterion.get("id")
            if not criterion_id:
                errors.append(f"{criterion_prefix}.id is required")
            elif criterion_id in acceptance_ids:
                errors.append(f"duplicate acceptance id in {issue_id}: {criterion_id}")
            else:
                acceptance_ids.add(str(criterion_id))
            if not criterion.get("criterion"):
                errors.append(f"{criterion_prefix}.criterion is required")
            if criterion.get("status") not in ACCEPTANCE_STATES:
                errors.append(f"{criterion_prefix}.status is invalid")
            evidence = criterion.get("evidence")
            if not isinstance(evidence, list):
                errors.append(f"{criterion_prefix}.evidence must be a list")
            if strict and criterion.get("status") == "pass" and not evidence:
                errors.append(f"{criterion_prefix} passes without evidence")

        reviews = issue.get("reviews")
        if not isinstance(reviews, dict):
            errors.append(f"{prefix}.reviews must be an object")
            reviews = {}
        for axis in ("spec", "engineering"):
            records = reviews.get(axis)
            if not isinstance(records, list):
                errors.append(f"{prefix}.reviews.{axis} must be a list")
                continue
            for review_index, review in enumerate(records):
                if not isinstance(review, dict):
                    errors.append(
                        f"{prefix}.reviews.{axis}[{review_index}] must be an object"
                    )
                elif review.get("verdict") not in REVIEW_VERDICTS:
                    errors.append(
                        f"{prefix}.reviews.{axis}[{review_index}].verdict is invalid"
                    )

        if state == "cleared":
            nonpassing = [
                criterion.get("id")
                for criterion in acceptance
                if isinstance(criterion, dict)
                and criterion.get("status") not in {"pass", "not_applicable"}
            ]
            if nonpassing:
                errors.append(
                    f"{issue_id} is cleared with non-passing acceptance: {nonpassing}"
                )
            commits = issue.get("implementation_commits")
            if not isinstance(commits, list) or not commits:
                errors.append(f"{issue_id} is cleared without implementation_commits")
            if not clear_review(reviews, "spec"):
                errors.append(f"{issue_id} is cleared without a clear spec review")
            if not clear_review(reviews, "engineering"):
                errors.append(
                    f"{issue_id} is cleared without a clear engineering review"
                )
            if not issue.get("integration_commit"):
                errors.append(f"{issue_id} is cleared without integration_commit")
        if strict and state in TERMINAL_STATES - {"cleared"}:
            residuals = issue.get("residuals")
            notes = issue.get("notes")
            if not residuals and not notes:
                errors.append(
                    f"{issue_id} is {state} without a recorded rationale or residual"
                )
        if strict and state not in TERMINAL_STATES:
            errors.append(f"{issue_id} is non-terminal in strict mode: {state}")

    lane_ids: set[str] = set()
    for index, lane in enumerate(lanes):
        prefix = f"lanes[{index}]"
        if not isinstance(lane, dict):
            errors.append(f"{prefix} must be an object")
            continue
        lane_id = lane.get("id")
        if not isinstance(lane_id, str) or not lane_id:
            errors.append(f"{prefix}.id is required")
        elif lane_id in lane_ids:
            errors.append(f"duplicate lane id: {lane_id}")
        else:
            lane_ids.add(lane_id)
        if lane.get("state") not in LANE_STATES:
            errors.append(f"{prefix}.state is invalid")
        lane_issue_ids = require_list(
            lane.get("issue_ids"), f"{prefix}.issue_ids", errors
        )
        for issue_id in lane_issue_ids:
            if issue_id not in issue_ids:
                errors.append(f"{prefix} references unknown issue: {issue_id}")

    for index, issue in enumerate(issues):
        if not isinstance(issue, dict):
            continue
        lane_id = issue.get("lane")
        if lane_id and lane_id not in lane_ids:
            errors.append(f"issues[{index}] references unknown lane: {lane_id}")
        if strict and not lane_id:
            errors.append(f"issues[{index}] has no ownership lane in strict mode")

    for index, gate in enumerate(gates):
        prefix = f"gates[{index}]"
        if not isinstance(gate, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in ("id", "kind", "result"):
            if not gate.get(field):
                errors.append(f"{prefix}.{field} is required")
        if gate.get("result") not in GATE_RESULTS:
            errors.append(f"{prefix}.result is invalid")
        if strict and gate.get("result") == "pass" and not gate.get("revision"):
            errors.append(f"{prefix} passes without an exact revision")

    if strict:
        if not issues:
            errors.append("strict mode requires at least one normalized issue")
        if not lanes:
            errors.append("strict mode requires at least one ownership lane")
        for index, lane in enumerate(lanes):
            if isinstance(lane, dict) and lane.get("state") not in {
                "complete",
                "blocked",
            }:
                errors.append(
                    f"lanes[{index}] is non-terminal in strict mode: {lane.get('state')}"
                )
        if not run.get("integration_revision"):
            errors.append("strict mode requires run.integration_revision")
        if run.get("status") not in {
            "certified",
            "deployed",
            "complete_with_residuals",
        }:
            errors.append("strict mode requires a terminal truthful run.status")
        final_pass = any(
            isinstance(gate, dict)
            and gate.get("kind") == "final"
            and gate.get("result") == "pass"
            and gate.get("revision") == run.get("integration_revision")
            for gate in gates
        )
        if not final_pass:
            errors.append(
                "strict mode requires a passing final gate at integration_revision"
            )
        for review_kind in ("final_spec_review", "final_engineering_review"):
            review_pass = any(
                isinstance(gate, dict)
                and gate.get("kind") == review_kind
                and gate.get("result") == "pass"
                and gate.get("revision") == run.get("integration_revision")
                for gate in gates
            )
            if not review_pass:
                errors.append(
                    f"strict mode requires a passing {review_kind} gate at integration_revision"
                )
        if run.get("status") == "deployed" and run.get(
            "deployment_revision"
        ) != run.get("integration_revision"):
            errors.append(
                "a deployed run must deploy the exact certified integration_revision"
            )

    return errors


def validate_command(args: argparse.Namespace) -> int:
    ledger_path = Path(args.ledger).expanduser().resolve()
    try:
        data = load_json(ledger_path)
        errors = validate_ledger(data, args.strict)
    except (TypeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print(f"Valid ledger: {ledger_path}")
    return 0


def status_command(args: argparse.Namespace) -> int:
    ledger_path = Path(args.ledger).expanduser().resolve()
    try:
        data = load_json(ledger_path)
    except (TypeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    issues = data.get("issues") if isinstance(data.get("issues"), list) else []
    counts: dict[str, int] = {}
    for issue in issues:
        state = issue.get("state", "invalid") if isinstance(issue, dict) else "invalid"
        counts[state] = counts.get(state, 0) + 1
    run = data.get("run") if isinstance(data.get("run"), dict) else {}
    print(f"Run: {run.get('id', '<unknown>')}")
    print(f"Status: {run.get('status', '<unknown>')}")
    print(f"Base: {run.get('base_revision', '<unknown>')}")
    print(f"Integration: {run.get('integration_revision') or '<none>'}")
    print(f"Deployment: {run.get('deployment_revision') or '<none>'}")
    print(f"Issues: {len(issues)}")
    for state in sorted(counts):
        print(f"  {state}: {counts[state]}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="create a new fleet run ledger")
    init_parser.add_argument("--run-dir", required=True)
    init_parser.add_argument("--repo-root", required=True)
    init_parser.add_argument("--dossier", required=True)
    init_parser.add_argument("--base-revision", required=True)
    init_parser.add_argument("--run-id")
    init_parser.set_defaults(func=init_ledger)

    validate_parser = subparsers.add_parser(
        "validate", help="validate a fleet run ledger"
    )
    validate_parser.add_argument("--ledger", required=True)
    validate_parser.add_argument("--strict", action="store_true")
    validate_parser.set_defaults(func=validate_command)

    status_parser = subparsers.add_parser("status", help="print issue-state counts")
    status_parser.add_argument("--ledger", required=True)
    status_parser.set_defaults(func=status_command)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
