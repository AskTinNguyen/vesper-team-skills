"""Evidence contracts for image-to-VFX studies; no Blender dependency."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys


class ContractError(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise ContractError(message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def resolve(base, name):
    return (Path(base).parent / name).resolve()


def relative(path, output):
    try:
        return Path(os.path.relpath(Path(path).resolve(), Path(output).resolve().parent)).as_posix()
    except ValueError:
        # Windows cannot express a relative path across drive letters.
        return Path(path).resolve().as_posix()


def reference(path, output, ref_id):
    path = Path(path).resolve()
    return {"id": ref_id, "path": relative(path, output), "sha256": digest(path), "kind": "original", "description": path.name}


def init_contract(name, paths, output):
    return {"schema_version": 1, "name": name, "effect_id": None, "mode": "study", "fidelity": "reference-study", "references": [reference(p, output, f"ref-{i:02}") for i, p in enumerate(paths, 1)], "source_notes": [], "source_region": None, "gameplay_intent": "", "camera_basis": "proposed-gameplay", "coverage_note": "", "coverage_confirmed": False, "features": [], "unknowns": [], "engine_handoff": {"status": "unverified", "asset_bindings": None}, "prototype": None}


def from_study(catalog_path, effect_id, output):
    catalog_path = Path(catalog_path).resolve()
    catalog = read(catalog_path)
    rows = [e for e in catalog["effects"] if e["id"] == effect_id]
    require(len(rows) == 1, f"Unknown or duplicate study ID: {effect_id}")
    e = rows[0]
    source = next(s for s in catalog["sources"] if s["id"] == e["source"]["board_id"])
    c = init_contract(e["name"], [catalog_path.parent / source["path"]], output)
    c.update(effect_id=effect_id, gameplay_intent=e["gameplay_intent_proposed"], source_region=e["source"], source_notes=e["author_notes_paraphrased"], unknowns=e["unresolved"], coverage_note="Initial proposed layer mapping from the study; refine source-specific feature coverage and explicit omissions before a prototype.")
    c["source_appearance"] = e["visible_read"]
    c["source_appearance_basis"] = "Catalog summary; recheck against original stills. Temporal claims are not directly observed motion."
    c["source_hypotheses"] = e["implementation_hypotheses"]
    c["proposed_sequence"] = e["timing"]["sequence"]
    c["lite_goal"] = e["lite_variant"]
    c["features"] = [{"id": f"{effect_id}-{l['layer']}", "layer": l["layer"], "priority": l["priority"], "description": l["description"], "evidence_class": "proposed", "reference_ids": ["ref-01"], "phase": "see proposed_sequence; refine per feature before authoring", "targets": [], "disposition": "implement", "reason": ""} for l in e["design_layers_proposed"] if l["layer"] != "L0"]
    return c


def unique(rows, label):
    require(isinstance(rows, list), f"{label} must be a list")
    ids = [r.get("id") for r in rows]
    require(all(isinstance(i, str) and i.strip() for i in ids), f"{label} IDs must be nonempty")
    require(len(ids) == len(set(ids)), f"Duplicate {label} IDs")
    return set(ids)


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def validate(c, path, stage="study", check_files=True):
    require(c.get("schema_version") == 1, "Unsupported schema_version")
    require(c.get("name") and c.get("gameplay_intent"), "Name and gameplay intent are required")
    require(c.get("camera_basis") in ("proposed-gameplay", "reference-match"), "Invalid camera basis")
    refs = c.get("references", [])
    ref_ids = unique(refs, "reference")
    require(ref_ids, "At least one source reference is required")
    ref_map = {r["id"]: r for r in refs}
    for r in refs:
        require(r.get("kind") in ("original", "derivative", "video-frame"), "Invalid reference kind")
        require(isinstance(r.get("sha256"), str) and len(r["sha256"]) == 64, "Invalid source hash")
        if check_files:
            target = resolve(path, r["path"])
            require(target.is_file(), f"Missing reference {r['id']}")
            require(digest(target) == r["sha256"], f"Stale reference hash: {r['id']}")
    features = c.get("features", [])
    feature_ids = unique(features, "feature")
    require(feature_ids, "At least one feature is required")
    require(any(f.get("layer") == "L1" and f.get("priority") == "essential" and f.get("disposition") == "implement" for f in features), "An implemented essential primary shape is required")
    for f in features:
        require(f.get("layer") in ("L1", "L2", "L3", "L4"), f"Invalid layer: {f['id']}")
        require(f.get("priority") in ("essential", "support", "optional"), f"Invalid priority: {f['id']}")
        require(f.get("evidence_class") in ("observed", "author-reported", "hypothesis", "proposed"), "Invalid evidence class")
        require(f.get("description") and f.get("phase"), f"Feature description/phase missing: {f['id']}")
        require(f.get("reference_ids") and set(f["reference_ids"]) <= ref_ids, f"Unadmitted source for {f['id']}")
        require(f.get("disposition") in ("implement", "omitted"), "Invalid feature disposition")
        if f["disposition"] == "omitted":
            require(f.get("reason") and f["priority"] != "essential", f"Essential or unexplained omission: {f['id']}")
        if f["priority"] == "essential" or f["evidence_class"] == "observed":
            require(any(ref_map[i]["kind"] != "derivative" for i in f["reference_ids"]), f"Derivative-only evidence: {f['id']}")
    require(c.get("coverage_note"), "Feature coverage note is required")
    if stage == "study":
        return c
    require(c.get("coverage_confirmed") is True, "Refine and confirm feature coverage before prototype capture")
    p = c.get("prototype")
    require(isinstance(p, dict), "Prototype settings are required")
    require(p.get("builder_id") and p.get("checkpoint"), "Builder and checkpoint are required")
    require(number(p.get("fps")) and p["fps"] > 0, "FPS must be positive")
    require(type(p.get("seed")) is int, "Integer seed required")
    require(type(p.get("frame_start")) is int and type(p.get("frame_end")) is int and p["frame_start"] < p["frame_end"], "Invalid frame interval")
    require(p.get("timing_basis") in ("proposed", "measured") and p.get("scale_basis"), "Timing and scale basis required")
    require(isinstance(p.get("events"), list) and p["events"], "Event anchors required")
    event_names = [e.get("name") for e in p["events"]]
    require(len(event_names) == len(set(event_names)), "Duplicate event names")
    for event in p["events"]:
        require(event.get("name") and type(event.get("frame")) is int and p["frame_start"] <= event["frame"] <= p["frame_end"], "Invalid event anchor")
        require(event.get("basis") in ("proposed", "measured"), "Event basis required")
        if p["timing_basis"] == "measured" or event["basis"] == "measured":
            require(event.get("basis") == "measured" and number(event.get("source_timestamp_seconds")) and event["source_timestamp_seconds"] >= 0, "Measured timing requires timestamp evidence")
            require(event.get("reference_id") in ref_ids and ref_map[event["reference_id"]]["kind"] == "video-frame", "Measured timing requires an admitted video frame")
    if check_files:
        checkpoint = resolve(path, p["checkpoint"])
        require(checkpoint.is_file() and checkpoint.suffix.lower() == ".blend", "Missing .blend checkpoint")
    samples = p.get("samples", [])
    sample_ids = unique(samples, "sample")
    roles = {s.get("role") for s in samples}
    implemented = [f for f in features if f["disposition"] == "implement"]
    mandatory = {"before", "event", "clear", "oblique", "lite", "no-accents"} | {"isolate-" + f["layer"].lower() for f in implemented}
    require(mandatory <= set(p.get("required_roles", [])) <= roles, "Missing required temporal/variant/layer roles")
    anchors = {e["name"]: e["frame"] for e in p["events"]}
    require({"before", "event", "clear"} <= set(anchors), "Named before/event/clear anchors are required")
    require(anchors["before"] < anchors["event"] < anchors["clear"], "Temporal anchors must order before < event < clear")
    for s in samples:
        require(s.get("scene") and s.get("camera") and s.get("variant") and s.get("scenario"), f"Incomplete sample {s['id']}")
        require(type(s.get("frame")) is int and p["frame_start"] <= s["frame"] <= p["frame_end"], f"Sample frame outside interval: {s['id']}")
        if s.get("anchor"):
            require(s["anchor"] in anchors and s["frame"] == anchors[s["anchor"]], "Sample does not match its event anchor")
        if s["role"] in ("before", "event", "clear"):
            require(s.get("anchor") == s["role"] and s["variant"] == "Standard" and s["scenario"] == "normal", "Temporal role must bind its Standard/normal anchor")
        if s["role"] in ("lite", "no-accents", "oblique") or s["role"].startswith("isolate-"):
            require(s["frame"] == anchors["event"] and s["scenario"] == "normal", "Comparison roles must use the normal event frame")
    require(set(p.get("expected_clear_samples", [])) <= sample_ids and p.get("expected_clear_samples"), "Clear sample IDs required")
    require(any(s["id"] in p["expected_clear_samples"] and s["role"] == "clear" for s in samples), "The clear role must have a clear assertion")
    mappings = p.get("required_feature_samples", {})
    for f in implemented:
        require(isinstance(f.get("targets"), list) and f["targets"] and all(isinstance(t, str) and t.strip() for t in f["targets"]), f"Exact Blender targets missing: {f['id']}")
        require(mappings.get(f["id"]) and set(mappings[f["id"]]) <= sample_ids, f"Feature evidence missing: {f['id']}")
    return c


def verify(c, path, m, manifest_path):
    validate(c, path, "prototype")
    p = c["prototype"]
    require(m.get("schema_version") == 1 and isinstance(m.get("blender_version"), str) and m["blender_version"], "Manifest schema and Blender version required")
    require(m.get("contract_sha256") == digest(path), "Manifest contract hash mismatch")
    require(m.get("checkpoint_sha256") == digest(resolve(path, p["checkpoint"])), "Manifest checkpoint hash mismatch")
    require(m.get("reference_hashes") == {r["id"]: r["sha256"] for r in c["references"]}, "Manifest source hashes mismatch")
    rows = m.get("samples", [])
    require(unique(rows, "manifest sample") == {s["id"] for s in p["samples"]}, "Incomplete manifest sample coverage")
    by_id = {r["id"]: r for r in rows}
    for s in p["samples"]:
        r = by_id[s["id"]]
        for field in ("visible_targets", "visible_layers"):
            require(isinstance(r.get(field), list) and all(isinstance(v, str) for v in r[field]), f"Missing/invalid audit list {field}: {s['id']}")
        matrix = r.get("camera_matrix")
        require(isinstance(matrix, list) and len(matrix) == 4 and all(isinstance(row, list) and len(row) == 4 and all(number(v) for v in row) for row in matrix), "Finite 4x4 camera matrix required")
        require(isinstance(r.get("engine"), str) and r["engine"] and r.get("camera_type") in ("PERSP", "ORTHO", "PANO"), "Renderer and camera type required")
        require(number(r.get("camera_lens")) and r["camera_lens"] > 0, "Camera lens required")
        require(isinstance(r.get("resolution"), list) and len(r["resolution"]) == 3 and all(type(v) is int and v > 0 for v in r["resolution"]), "Render resolution required")
        color = r.get("color_management")
        require(isinstance(color, dict) and all(isinstance(color.get(k), str) and color[k] for k in ("display", "view", "look")) and all(number(color.get(k)) for k in ("exposure", "gamma")), "Color management record required")
        require(type(r.get("compositor_enabled")) is bool, "Compositor state required")
        require(all(r.get(k) == s[k] for k in ("frame", "scene", "camera", "role", "variant", "scenario")), f"Sample metadata mismatch: {s['id']}")
        require(r.get("fps") == p["fps"] and r.get("seed") == p["seed"], "FPS/seed mismatch")
        require(r.get("scene_variant") == s["variant"] and r.get("scene_scenario") == s["scenario"], "Scene mislabeled as variant/scenario")
        image_path = resolve(manifest_path, r["path"])
        require(image_path.is_file() and digest(image_path) == r.get("sha256"), f"Missing or stale rendered image: {s['id']}")
        layers = set(r.get("visible_layers", []))
        if s["id"] in p["expected_clear_samples"]:
            require(not r.get("visible_targets"), f"VFX remains render-eligible at clear sample: {s['id']}")
        if s["role"] == "no-accents":
            require("L4" not in layers and not r.get("compositor_enabled"), "No-accents sample still contains accents/compositor")
        if s["role"].startswith("isolate-"):
            require(layers == {s["role"].removeprefix("isolate-").upper()}, "Layer isolation is mislabeled or empty")
    for f in c["features"]:
        if f["disposition"] != "implement":
            continue
        for sample_id in p["required_feature_samples"][f["id"]]:
            require(set(f["targets"]) <= set(by_id[sample_id].get("visible_targets", [])), f"Feature targets absent from evidence: {f['id']} in {sample_id}")
    event = next(r for r in rows if r["role"] == "event")
    oblique = next(r for r in rows if r["role"] == "oblique")
    require(event.get("camera_matrix") != oblique.get("camera_matrix"), "Oblique view duplicates event camera")
    lite = next(r for r in rows if r["role"] == "lite")
    for r in rows:
        require(r["resolution"] == event["resolution"] and r["engine"] == event["engine"] and r["color_management"] == event["color_management"], "Comparison render settings drift")
    require(lite["variant"].lower() == "lite", "Lite role has no Lite variant")
    require(lite.get("visible_targets") != event.get("visible_targets") or lite.get("variant_signature") != event.get("variant_signature"), "Lite has no recorded implementation difference")
    return m


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    initial = sub.add_parser("init")
    initial.add_argument("--name", required=True)
    initial.add_argument("--reference", action="append", required=True)
    initial.add_argument("--out", required=True)
    study = sub.add_parser("from-study")
    study.add_argument("--catalog", required=True)
    study.add_argument("--effect", required=True)
    study.add_argument("--out", required=True)
    val = sub.add_parser("validate")
    val.add_argument("contract")
    val.add_argument("--stage", choices=["study", "prototype"], default="study")
    ver = sub.add_parser("verify")
    ver.add_argument("contract")
    ver.add_argument("manifest")
    args = ap.parse_args()
    try:
        if args.command == "init":
            write_new(args.out, init_contract(args.name, args.reference, args.out))
            print("Created incomplete intake; fill purpose, features and coverage before validation.")
        elif args.command == "from-study":
            c = from_study(args.catalog, args.effect, args.out)
            validate(c, args.out)
            write_new(args.out, c)
            print("Created validated study contract; prototype fields remain intentionally incomplete.")
        elif args.command == "validate":
            validate(read(args.contract), args.contract, args.stage)
            print(f"PASS: {args.stage} contract; this does not establish visual quality")
        else:
            verify(read(args.contract), args.contract, read(args.manifest), args.manifest)
            print("PASS: evidence integrity; independent visual review still required")
    except (ContractError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
