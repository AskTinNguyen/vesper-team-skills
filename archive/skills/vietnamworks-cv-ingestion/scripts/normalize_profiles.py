#!/usr/bin/env python3
"""
Normalize and filter candidate profile data for lawful internal HR usage.

Supported input:
- JSON array (.json)
- NDJSON (.ndjson)

This script intentionally excludes direct web scraping behavior.
Only process data from authorized sources.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ALLOWED_SOURCES_DEFAULT = {"user_export", "ats_export", "official_api"}
CONSENT_GRANTED = {"granted", "yes", "true", "1", "consented"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize and filter candidate profiles")
    parser.add_argument("--input", required=True, help="Absolute path to input JSON/NDJSON")
    parser.add_argument("--output", required=True, help="Absolute path to output JSON")
    parser.add_argument("--position", default=None, help="Filter by position/title substring")
    parser.add_argument("--skills", default="", help="Comma-separated required skills")
    parser.add_argument("--min-years", type=float, default=0, help="Minimum years of experience")
    parser.add_argument(
        "--allowed-sources",
        default=",".join(sorted(ALLOWED_SOURCES_DEFAULT)),
        help="Comma-separated allowed sources (default: user_export,ats_export,official_api)",
    )
    parser.add_argument(
        "--require-consent",
        action="store_true",
        help="Only keep profiles with granted consent",
    )
    return parser.parse_args()


def read_input(path: Path) -> list[dict[str, Any]]:
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return []

    if path.suffix.lower() == ".ndjson":
        rows: list[dict[str, Any]] = []
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            if isinstance(item, dict):
                rows.append(item)
        return rows

    loaded = json.loads(raw)
    if isinstance(loaded, list):
        return [x for x in loaded if isinstance(x, dict)]
    if isinstance(loaded, dict):
        return [loaded]
    return []


def first_value(record: dict[str, Any], keys: list[str], default: Any = None) -> Any:
    for key in keys:
        if key in record and record[key] not in (None, ""):
            return record[key]
    return default


def parse_years(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().lower()
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if not match:
        return 0.0
    return float(match.group(1))


def parse_skills(value: Any) -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        skills = [str(x).strip().lower() for x in value if str(x).strip()]
        return sorted(set(skills))

    text = str(value)
    parts = re.split(r"[,;/|]", text)
    skills = [p.strip().lower() for p in parts if p.strip()]
    return sorted(set(skills))


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    source = str(first_value(record, ["source", "source_type"], "unknown")).strip().lower()
    consent_raw = str(first_value(record, ["consent_status", "consent", "privacy_consent"], "unknown")).strip().lower()

    normalized = {
        "candidate_id": str(first_value(record, ["candidate_id", "id", "profile_id"], "")).strip() or None,
        "full_name": str(first_value(record, ["full_name", "name", "candidate_name"], "")).strip(),
        "current_title": str(first_value(record, ["current_title", "title", "position", "desired_position"], "")).strip(),
        "total_years_experience": parse_years(first_value(record, ["total_years_experience", "experience_years", "years_experience"], 0)),
        "skills": parse_skills(first_value(record, ["skills", "skill_tags", "primary_skills"], [])),
        "source": source,
        "consent_status": "granted" if consent_raw in CONSENT_GRANTED else ("denied" if consent_raw in {"denied", "no", "false", "0"} else "unknown"),
        "profile_url": str(first_value(record, ["profile_url", "url"], "")).strip() or None,
        "last_updated": first_value(record, ["last_updated", "updated_at"], None),
    }

    return normalized


def match_filters(
    normalized: dict[str, Any],
    position: str | None,
    required_skills: set[str],
    min_years: float,
    allowed_sources: set[str],
    require_consent: bool,
) -> tuple[bool, str | None]:
    if normalized["source"] not in allowed_sources:
        return False, f"source_not_allowed:{normalized['source']}"

    if require_consent and normalized["consent_status"] != "granted":
        return False, "missing_or_invalid_consent"

    if position:
        title = (normalized.get("current_title") or "").lower()
        if position.lower() not in title:
            return False, "position_mismatch"

    if normalized.get("total_years_experience", 0) < min_years:
        return False, "insufficient_experience"

    profile_skills = set(normalized.get("skills", []))
    if required_skills and not required_skills.issubset(profile_skills):
        return False, "missing_required_skills"

    if not normalized.get("full_name"):
        return False, "missing_full_name"

    return True, None


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    allowed_sources = {x.strip().lower() for x in args.allowed_sources.split(",") if x.strip()}
    required_skills = {x.strip().lower() for x in args.skills.split(",") if x.strip()}

    rows = read_input(input_path)

    accepted: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []

    for row in rows:
        normalized = normalize_record(row)
        ok, reason = match_filters(
            normalized=normalized,
            position=args.position,
            required_skills=required_skills,
            min_years=args.min_years,
            allowed_sources=allowed_sources,
            require_consent=args.require_consent,
        )
        if ok:
            accepted.append(normalized)
        else:
            excluded.append(
                {
                    "candidate_id": normalized.get("candidate_id"),
                    "reason": reason,
                }
            )

    payload = {
        "meta": {
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "input_count": len(rows),
            "accepted_count": len(accepted),
            "excluded_count": len(excluded),
            "filters": {
                "position": args.position,
                "skills": sorted(required_skills),
                "min_years": args.min_years,
                "require_consent": bool(args.require_consent),
            },
        },
        "records": accepted,
        "excluded": excluded,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote normalized output to: {output_path}")


if __name__ == "__main__":
    main()
