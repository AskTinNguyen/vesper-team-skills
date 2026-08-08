#!/usr/bin/env python3
"""Validate canonical semantic indexes against normalized chapter JSON."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FILES = {"arcs": "arcs.json", "entities": "entities.json",
         "events": "events.json", "intents": "intents.json"}


class Validator:
    def __init__(self, total):
        self.total, self.errors, self.warnings = total, [], []

    def error(self, path, message): self.errors.append(f"{path}: {message}")
    def chapter(self, value, path):
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= self.total:
            self.error(path, f"must be an integer in 1..{self.total}")
            return None
        return value
    def text(self, item, key, path):
        value = item.get(key)
        if not isinstance(value, str) or not value.strip(): self.error(f"{path}.{key}", "must be non-empty text")
    def refs(self, values, allowed, path):
        if not isinstance(values, list): self.error(path, "must be an array"); return
        if len(values) != len(set(x for x in values if isinstance(x, str))): self.error(path, "duplicate reference")
        for i, value in enumerate(values):
            if value not in allowed: self.error(f"{path}[{i}]", f"unknown reference {value!r}")


def load_document(directory, kind, errors):
    path = directory / FILES[kind]
    try: doc = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc: errors.append(f"{path.name}: {exc}"); return []
    if not isinstance(doc, dict) or doc.get("schema_version") != 1:
        errors.append(f"{path.name}: schema_version must be 1"); return []
    records = doc.get(kind)
    if not isinstance(records, list): errors.append(f"{path.name}.{kind}: must be an array"); return []
    return records


def validate(index_dir: Path, library: Path) -> dict:
    chapter_paths = sorted((library / "chapters").glob("*.json"))
    orders = []
    for path in chapter_paths:
        try: orders.append(json.loads(path.read_text(encoding="utf-8"))["order"])
        except Exception: pass
    preliminary = []
    if orders != list(range(1, len(orders) + 1)): preliminary.append("library chapters are not continuous 1..N")
    v = Validator(len(orders))
    v.errors.extend(preliminary)
    documents = {kind: load_document(index_dir, kind, v.errors) for kind in FILES}
    ids = {}
    for kind, records in documents.items():
        seen = set()
        for i, item in enumerate(records):
            path = f"{kind}[{i}]"
            if not isinstance(item, dict): v.error(path, "must be an object"); continue
            ident = item.get("id")
            if not isinstance(ident, str) or not ID_RE.fullmatch(ident): v.error(f"{path}.id", "invalid ASCII slug")
            elif ident in seen: v.error(f"{path}.id", "duplicate id")
            else: seen.add(ident)
        ids[kind] = seen

    covered = []
    for i, arc in enumerate(documents["arcs"]):
        if not isinstance(arc, dict): continue
        path = f"arcs[{i}]"; v.text(arc, "title", path); v.text(arc, "summary", path)
        start = v.chapter(arc.get("start_chapter"), f"{path}.start_chapter")
        end = v.chapter(arc.get("end_chapter"), f"{path}.end_chapter")
        if start and end:
            if start > end: v.error(path, "start exceeds end")
            else: covered.extend(range(start, end + 1))
        for field in ("themes", "search_terms"):
            if not isinstance(arc.get(field), list) or not arc[field]: v.error(f"{path}.{field}", "must be a non-empty array")
        for field in ("characters", "locations", "factions"): v.refs(arc.get(field), ids["entities"], f"{path}.{field}")
        keys = arc.get("key_chapters")
        if not isinstance(keys, list) or not keys: v.error(f"{path}.key_chapters", "must be a non-empty array"); continue
        for j, key in enumerate(keys):
            kp = f"{path}.key_chapters[{j}]"
            if not isinstance(key, dict): v.error(kp, "must be an object"); continue
            chapter = v.chapter(key.get("chapter"), f"{kp}.chapter")
            v.text(key, "label", kp); v.text(key, "reason", kp)
            if chapter and start and end and not start <= chapter <= end: v.error(f"{kp}.chapter", "outside arc")
    if covered != list(range(1, v.total + 1)): v.error("arcs", "must cover 1..N exactly once in order")

    for i, entity in enumerate(documents["entities"]):
        if not isinstance(entity, dict): continue
        path = f"entities[{i}]"
        for key in ("name", "summary", "type"): v.text(entity, key, path)
        if entity.get("type") not in {"character", "location", "faction", "concept"}: v.error(f"{path}.type", "invalid type")
        v.chapter(entity.get("first_chapter"), f"{path}.first_chapter")
        v.refs(entity.get("arc_ids"), ids["arcs"], f"{path}.arc_ids")
        v.refs(entity.get("related_entities"), ids["entities"], f"{path}.related_entities")
        ranges = entity.get("important_ranges")
        if not isinstance(ranges, list) or not ranges: v.error(f"{path}.important_ranges", "must be non-empty"); continue
        for j, item in enumerate(ranges):
            rp = f"{path}.important_ranges[{j}]"
            if not isinstance(item, dict): v.error(rp, "must be an object"); continue
            start = v.chapter(item.get("start"), f"{rp}.start"); end = v.chapter(item.get("end"), f"{rp}.end")
            v.text(item, "label", rp)
            if start and end and start > end: v.error(rp, "start exceeds end")

    for i, event in enumerate(documents["events"]):
        if not isinstance(event, dict): continue
        path = f"events[{i}]"; v.text(event, "title", path); v.text(event, "summary", path)
        start = v.chapter(event.get("start_chapter"), f"{path}.start_chapter")
        end = v.chapter(event.get("end_chapter"), f"{path}.end_chapter")
        peak = v.chapter(event.get("peak_chapter"), f"{path}.peak_chapter")
        if start and end and peak and not start <= peak <= end: v.error(f"{path}.peak_chapter", "outside event")
        v.refs(event.get("arc_ids"), ids["arcs"], f"{path}.arc_ids")
        v.refs(event.get("participants"), ids["entities"], f"{path}.participants")
        v.refs(event.get("locations"), ids["entities"], f"{path}.locations")

    for i, intent in enumerate(documents["intents"]):
        if not isinstance(intent, dict): continue
        path = f"intents[{i}]"
        for key in ("title", "description", "category"): v.text(intent, key, path)
        terms = intent.get("search_terms")
        if not isinstance(terms, list) or not terms: v.error(f"{path}.search_terms", "must be non-empty")
        destinations = intent.get("destinations")
        if not isinstance(destinations, list) or not 1 <= len(destinations) <= 6:
            v.error(f"{path}.destinations", "must contain 1..6 items"); continue
        priorities = []
        for j, dest in enumerate(destinations):
            dp = f"{path}.destinations[{j}]"
            if not isinstance(dest, dict): v.error(dp, "must be an object"); continue
            start = v.chapter(dest.get("chapter"), f"{dp}.chapter")
            end = dest.get("end_chapter", start)
            end = v.chapter(end, f"{dp}.end_chapter")
            if start and end and start > end: v.error(dp, "start exceeds end")
            v.text(dest, "label", dp); v.text(dest, "reason", dp)
            priority = dest.get("priority")
            if isinstance(priority, bool) or not isinstance(priority, int) or priority < 1: v.error(f"{dp}.priority", "must be positive integer")
            else: priorities.append(priority)
            if dest.get("arc_id") not in ids["arcs"]: v.error(f"{dp}.arc_id", "unknown arc")
        if len(priorities) != len(set(priorities)): v.error(f"{path}.destinations", "duplicate priority")

    return {"valid": not v.errors, "chapter_count": v.total,
            "counts": {kind: len(records) for kind, records in documents.items()},
            "errors": v.errors, "warnings": v.warnings}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("index", type=Path); parser.add_argument("library", type=Path); parser.add_argument("--report", type=Path)
    args = parser.parse_args(); result = validate(args.index, args.library)
    output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.report: args.report.parent.mkdir(parents=True, exist_ok=True); args.report.write_text(output, encoding="utf-8")
    sys.stdout.write(output); return 0 if result["valid"] else 1


if __name__ == "__main__": raise SystemExit(main())
