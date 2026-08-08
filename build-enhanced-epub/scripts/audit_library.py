#!/usr/bin/env python3
"""Audit a normalized enhanced-EPUB library without third-party dependencies."""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from collections import Counter
from pathlib import Path


def audit(library: Path) -> dict:
    chapter_dir = library / "chapters"
    paths = sorted(chapter_dir.glob("*.json"))
    errors, warnings, chapters, checksums = [], [], [], []
    for path in paths:
        try:
            item = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{path.name}: invalid JSON/UTF-8: {exc}")
            continue
        order = item.get("order")
        paragraphs = item.get("paragraphs")
        if isinstance(order, bool) or not isinstance(order, int):
            errors.append(f"{path.name}: order must be an integer")
            continue
        if not isinstance(paragraphs, list) or not all(isinstance(x, str) for x in paragraphs):
            errors.append(f"{path.name}: paragraphs must be an array of strings")
            continue
        text = "\n\n".join(x.strip() for x in paragraphs if x.strip())
        if not text:
            errors.append(f"{path.name}: empty chapter")
        checksum = hashlib.sha256(text.encode()).hexdigest()
        declared = item.get("checksum_sha256")
        if declared and declared != checksum:
            errors.append(f"{path.name}: checksum mismatch")
        if len(text) < 1000:
            warnings.append(f"{path.name}: unusually short ({len(text)} chars)")
        chapters.append((order, path.name, len(paragraphs), len(text)))
        checksums.append((checksum, order))

    orders = [x[0] for x in chapters]
    expected = list(range(1, len(chapters) + 1))
    if orders != expected:
        errors.append("chapter order is not exactly continuous 1..N in filename order")
    if len(orders) != len(set(orders)):
        errors.append("duplicate chapter order")
    duplicate_content = {key: values for key, values in _group(checksums).items() if len(values) > 1}
    if duplicate_content:
        errors.append(f"duplicate content checksums: {duplicate_content}")

    metadata = {}
    metadata_path = library / "metadata.json"
    if metadata_path.exists():
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"metadata.json: {exc}")
    else:
        errors.append("missing metadata.json")
    declared_count = metadata.get("expected_chapters")
    if declared_count is not None and declared_count != len(chapters):
        errors.append(f"expected_chapters={declared_count}, found={len(chapters)}")

    lengths = [x[3] for x in chapters]
    paragraph_counts = [x[2] for x in chapters]
    return {
        "valid": not errors,
        "library": str(library.resolve()),
        "chapter_count": len(chapters),
        "orders": {"first": min(orders) if orders else None, "last": max(orders) if orders else None},
        "characters": _summary(lengths),
        "paragraphs": {**_summary(paragraph_counts), "total": sum(paragraph_counts)},
        "errors": errors,
        "warnings": warnings,
    }


def _group(items):
    grouped = {}
    for key, value in items:
        grouped.setdefault(key, []).append(value)
    return grouped


def _summary(values):
    if not values:
        return {"min": None, "median": None, "max": None, "total": 0}
    return {"min": min(values), "median": statistics.median(values),
            "max": max(values), "total": sum(values)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("library", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = audit(args.library)
    output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output, encoding="utf-8")
    sys.stdout.write(output)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
