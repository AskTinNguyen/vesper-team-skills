#!/usr/bin/env python3
"""Deep structural/link validation for an offline EPUB package."""

from __future__ import annotations

import argparse
import json
import posixpath
import sys
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET


def local_name(tag): return tag.rsplit("}", 1)[-1]


def validate(path: Path) -> dict:
    errors = []
    try:
        archive = zipfile.ZipFile(path)
    except Exception as exc:
        return {"valid": False, "errors": [f"cannot open ZIP: {exc}"]}
    with archive:
        infos, names = archive.infolist(), archive.namelist()
        if not infos or infos[0].filename != "mimetype": errors.append("mimetype must be first")
        elif infos[0].compress_type != zipfile.ZIP_STORED: errors.append("mimetype must be uncompressed")
        if len(names) != len(set(names)): errors.append("duplicate ZIP entry")
        if "mimetype" not in names or archive.read("mimetype") != b"application/epub+zip": errors.append("invalid mimetype")
        required = {"META-INF/container.xml"}
        for item in required - set(names): errors.append(f"missing {item}")
        roots = {}
        for name in names:
            if name.endswith((".xml", ".opf", ".ncx", ".xhtml")):
                try: roots[name] = ET.fromstring(archive.read(name))
                except Exception as exc: errors.append(f"invalid XML {name}: {exc}")
        opf_names = [name for name in roots if name.endswith(".opf")]
        if len(opf_names) != 1: errors.append(f"expected one OPF, found {len(opf_names)}")
        name_set = set(names)
        ids = {name: {node.attrib["id"] for node in root.iter() if "id" in node.attrib}
               for name, root in roots.items()}
        for name, root in roots.items():
            is_guide = "/guide/" in name
            if is_guide and any(local_name(node.tag).lower() == "script" for node in root.iter()): errors.append(f"script in guide {name}")
            for node in root.iter():
                if is_guide and any(key.lower().startswith("on") for key in node.attrib): errors.append(f"event handler in guide {name}")
                for attribute in ("href", "src"):
                    raw = node.attrib.get(attribute)
                    if not raw: continue
                    target = urlsplit(raw)
                    if target.scheme or target.netloc:
                        if is_guide: errors.append(f"network URL in guide {name}: {raw}")
                        continue
                    resource = unquote(target.path)
                    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), resource))
                    if resource and resolved not in name_set: errors.append(f"missing target in {name}: {raw}")
                    anchor_doc = resolved if resource else name
                    if target.fragment and target.fragment not in ids.get(anchor_doc, set()): errors.append(f"missing anchor in {name}: {raw}")
        if len(opf_names) == 1:
            opf = roots[opf_names[0]]
            manifest_nodes = [node for node in opf.iter() if local_name(node.tag) == "item"]
            manifest = {node.attrib.get("id"): node for node in manifest_nodes}
            if None in manifest or len(manifest) != len(manifest_nodes): errors.append("duplicate/empty manifest id")
            navs = [node for node in manifest_nodes if "nav" in node.attrib.get("properties", "").split()]
            if len(navs) != 1: errors.append("expected exactly one nav manifest item")
            opf_dir = posixpath.dirname(opf_names[0])
            for node in manifest_nodes:
                href = node.attrib.get("href")
                if not href or posixpath.normpath(posixpath.join(opf_dir, href)) not in name_set: errors.append(f"manifest target missing: {href}")
            spine_ids = [node.attrib.get("idref") for node in opf.iter() if local_name(node.tag) == "itemref"]
            for ident in spine_ids:
                if ident not in manifest: errors.append(f"unknown spine idref: {ident}")
        ncx = [root for name, root in roots.items() if name.endswith(".ncx")]
        if not ncx or not any(local_name(node.tag) == "navPoint" for root in ncx for node in root.iter()): errors.append("missing/non-functional NCX")
        return {"valid": not errors, "file": str(path.resolve()), "entries": len(names),
                "xml_documents": len(roots), "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("epub", type=Path); parser.add_argument("--report", type=Path)
    args = parser.parse_args(); result = validate(args.epub)
    output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.report: args.report.parent.mkdir(parents=True, exist_ok=True); args.report.write_text(output, encoding="utf-8")
    sys.stdout.write(output); return 0 if result["valid"] else 1


if __name__ == "__main__": raise SystemExit(main())
