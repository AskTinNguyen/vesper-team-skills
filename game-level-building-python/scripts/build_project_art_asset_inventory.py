import json
import os
from collections import defaultdict
from datetime import datetime, timezone


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
REFERENCES_DIR = os.path.join(SKILL_DIR, "references")
REPO_ROOT = os.path.abspath(os.path.join(SKILL_DIR, "..", "..", "..", "..", ".."))
CONTENT_DIR = os.path.join(REPO_ROOT, "Content")
OUTPUT_OVERVIEW_PATH = os.path.join(REFERENCES_DIR, "project-art-asset-scan-overview.md")
OUTPUT_MARKDOWN_PATH = os.path.join(REFERENCES_DIR, "project-art-asset-inventory.md")
OUTPUT_JSON_PATH = os.path.join(REFERENCES_DIR, "project-art-asset-inventory.json")
ANALYSIS_MARKDOWN_PATH = os.path.join(REFERENCES_DIR, "project-art-asset-analysis.md")
ANALYSIS_JSON_PATH = os.path.join(REFERENCES_DIR, "project-art-pack-analysis.json")

ROLE_ORDER = [
    "wall",
    "screen_wall",
    "gate",
    "moon_gate",
    "main_hall",
    "villa",
    "pavilion",
    "pond",
    "tree",
    "rockery",
    "bench",
    "decor",
]

ROLE_KEYWORDS = {
    "wall": ["wall", "panel"],
    "screen_wall": ["screenpanel", "screen"],
    "gate": ["gate", "archway"],
    "moon_gate": ["moon", "circle", "circular", "archway"],
    "main_hall": ["hall", "temple"],
    "villa": ["villa", "island", "hill"],
    "pavilion": ["pavilion", "tea", "hall"],
    "pond": ["pond", "basin", "water"],
    "tree": ["tree", "bonsai", "grove"],
    "rockery": ["rock", "stone", "roots"],
    "bench": ["bench", "chair"],
    "decor": ["decor", "altar", "statue", "monument", "vase", "burner", "plaque", "tablet"],
}

SOURCE_RULES = [
    {"label": "s2_prototype", "path_tokens": ["S2", "Core_Env", "Prototype"], "score": 120, "style": "prototype"},
    {"label": "s2_env_mesh", "path_tokens": ["S2", "Core_Env", "Mesh"], "score": 95, "style": "project"},
    {"label": "asian_modular_temple", "path_tokens": ["Asian_Modular_Temple"], "score": 90, "style": "marketplace"},
    {"label": "bamboo_forest", "path_tokens": ["Bamboo_Forest"], "score": 75, "style": "marketplace"},
    {"label": "deep_in_the_forest", "path_tokens": ["DeepInTheForest"], "score": 78, "style": "marketplace"},
    {"label": "dreamscape_tower", "path_tokens": ["DreamscapeSeries", "DreamscapeTower"], "score": 72, "style": "stylized"},
    {"label": "asian_forest_town_artref", "path_tokens": ["ArtRef", "ASIAN_ForestTown_YOS3D"], "score": 68, "style": "artref"},
    {"label": "zhangjiajie_artref", "path_tokens": ["ArtRef", "8KZhangjiajieLandscapePack"], "score": 66, "style": "artref"},
    {"label": "massive_village", "path_tokens": ["Massive", "MassiveVillage"], "score": 65, "style": "marketplace"},
]

EXCLUDED_PATH_TOKENS = {
    "__ExternalObjects__",
    "Audio",
    "Anims",
    "Animation",
    "BehaviorTrees",
    "Materials",
    "Textures",
    "Niagara",
    "VFX",
    "Maps",
    "Map",
    "DemoRoom",
    "Effects",
}

EXCLUDED_NAME_TOKENS = {
    "placeholder",
    "projectile",
    "weapon",
    "voodoo",
    "teleport",
    "bloodtree",
}

ROLE_EXCLUDED_SUBSTRINGS = {
    "bench": {"throne", "torture", "toture", "sedanchair"},
    "main_hall": {"base", "fence", "stair", "stairs", "floor", "roof", "bell", "tower", "decor", "statue", "pillar"},
    "pond": {"bucket", "waterfall"},
    "tree": {"pavilion", "grove", "roots", "root", "tabletop", "module"},
    "villa": {"village"},
    "wall": {"decor-wall", "plaque", "tablet", "painting", "medallion", "portrait", "celendar", "calendar"},
    "moon_gate": {"spring", "summer", "autumn", "winter", "ground", "roots", "foliage", "bamboo", "vfx"},
}


def normalize_tokens(path_text):
    return [token for token in path_text.replace("\\", "/").split("/") if token]


def to_game_path(content_relative_path):
    asset_path = content_relative_path.replace("\\", "/")
    asset_without_ext = asset_path[:-7]
    asset_name = os.path.basename(asset_without_ext)
    return "/Game/{0}.{1}".format(asset_without_ext, asset_name)


def infer_asset_type(filename):
    if filename.startswith("BP_") or "_Actor" in filename:
        return "blueprint"
    if filename.startswith("SM_"):
        return "static_mesh"
    return "unknown"


def infer_source(asset_tokens):
    best = {"label": "other", "score": 0, "style": "unknown"}
    for rule in SOURCE_RULES:
        if all(token in asset_tokens for token in rule["path_tokens"]):
            if rule["score"] > best["score"]:
                best = rule
    return best["label"], best["style"], best["score"]


def has_gate_keyword(lower_name):
    if lower_name.startswith("gate") or lower_name.endswith("gate"):
        return True
    return any(marker in lower_name for marker in ("_gate", "gate_", "-gate", "gate-"))


def role_matches(role, lower_name, asset_type):
    if any(token in lower_name for token in ROLE_EXCLUDED_SUBSTRINGS.get(role, ())):
        return False
    if role == "moon_gate":
        if any(keyword in lower_name for keyword in ROLE_KEYWORDS[role]):
            return True
        return "round" in lower_name and has_gate_keyword(lower_name)
    if role == "gate":
        return has_gate_keyword(lower_name)
    keyword_hits = [keyword for keyword in ROLE_KEYWORDS[role] if keyword in lower_name]
    if keyword_hits:
        if role == "main_hall" and asset_type == "static_mesh" and "hall" not in lower_name:
            return False
        return True
    if role == "villa" and ("island" in lower_name or "hill" in lower_name):
        return True
    return False


def role_score(role, lower_name, asset_tokens, asset_type, source_boost):
    score = source_boost
    for keyword in ROLE_KEYWORDS[role]:
        keyword_hit = keyword in lower_name
        if role == "gate":
            keyword_hit = has_gate_keyword(lower_name)
        if keyword_hit:
            score += 45
    if asset_type == "blueprint":
        score += 18
    elif asset_type == "static_mesh":
        score += 10
    if "_actor" in lower_name:
        score += 10
    if role == "moon_gate" and (
        any(token in lower_name for token in ("moon", "circle", "circular", "archway"))
        or ("round" in lower_name and has_gate_keyword(lower_name))
    ):
        score += 20
    if role == "screen_wall" and ("screenpanel" in lower_name or "decor-wall" in lower_name):
        score += 24
    if role == "main_hall" and "hall" in lower_name:
        score += 20
    if role == "villa" and ("hill" in lower_name or "island" in lower_name):
        score += 16
    if any(token in lower_name for token in EXCLUDED_NAME_TOKENS):
        score -= 80
    if any(token in asset_tokens for token in EXCLUDED_PATH_TOKENS):
        score -= 100
    return score


def asset_note(role, lower_name, source_label):
    note_bits = [source_label]
    if "tea" in lower_name:
        note_bits.append("tea")
    if "garden" in lower_name:
        note_bits.append("garden")
    if "_actor" in lower_name:
        note_bits.append("assembled")
    return ", ".join(note_bits)


def scan_assets():
    candidates_by_role = defaultdict(list)
    total_assets_scanned = 0

    for root, _, files in os.walk(CONTENT_DIR):
        for filename in files:
            if not filename.endswith(".uasset"):
                continue

            total_assets_scanned += 1
            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, CONTENT_DIR)
            asset_tokens = normalize_tokens(rel_path)

            if any(token in EXCLUDED_PATH_TOKENS for token in asset_tokens):
                continue

            lower_name = filename[:-7].lower()
            asset_type = infer_asset_type(filename)
            if asset_type == "unknown":
                continue

            source_label, style_hint, source_boost = infer_source(asset_tokens)

            for role in ROLE_ORDER:
                if not role_matches(role, lower_name, asset_type):
                    continue
                score = role_score(role, lower_name, asset_tokens, asset_type, source_boost)
                if score < 95:
                    continue

                candidates_by_role[role].append(
                    {
                        "asset_name": filename[:-7],
                        "asset_path": to_game_path(rel_path),
                        "asset_type": asset_type,
                        "source_label": source_label,
                        "style_hint": style_hint,
                        "score": score,
                        "note": asset_note(role, lower_name, source_label),
                    }
                )

    for role in list(candidates_by_role.keys()):
        candidates_by_role[role].sort(key=lambda item: (-item["score"], item["asset_path"]))
        deduped = []
        seen_paths = set()
        for item in candidates_by_role[role]:
            if item["asset_path"] in seen_paths:
                continue
            deduped.append(item)
            seen_paths.add(item["asset_path"])
        candidates_by_role[role] = deduped[:18]

    return total_assets_scanned, candidates_by_role


def make_recommended_palette(candidates_by_role):
    palette_roles = ["wall", "screen_wall", "pond", "main_hall", "villa", "pavilion", "moon_gate", "rockery", "tree"]
    palette = {}
    for role in palette_roles:
        entries = []
        for item in candidates_by_role.get(role, [])[:4]:
            entries.append(
                {
                    "path": item["asset_path"],
                    "asset_type": item["asset_type"],
                    "source_label": item["source_label"],
                    "style_hint": item["style_hint"],
                    "fit_to_bounds": True,
                }
            )
        if entries:
            palette[role] = entries
    return palette


def write_markdown(total_assets_scanned, candidates_by_role, recommended_palette):
    lines = [
        "# Project Art Asset Inventory",
        "",
        "Generated automatically from the current repo `Content/` tree.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---|",
        "| Total `.uasset` files scanned | {0} |".format(total_assets_scanned),
        "| Roles with candidates | {0} |".format(sum(1 for role in ROLE_ORDER if candidates_by_role.get(role))),
        "| Recommended palette roles | {0} |".format(len(recommended_palette)),
        "",
        "## Recommended Palette Roles",
        "",
        "| Role | Top Sources | Candidate Count |",
        "|---|---|---|",
    ]

    for role in ROLE_ORDER:
        items = candidates_by_role.get(role, [])
        if not items:
            continue
        top_sources = ", ".join(sorted({item["source_label"] for item in items[:4]}))
        lines.append("| `{0}` | {1} | {2} |".format(role, top_sources, len(items)))

    for role in ROLE_ORDER:
        items = candidates_by_role.get(role, [])
        if not items:
            continue
        lines.extend(
            [
                "",
                "## `{0}`".format(role),
                "",
                "| Score | Asset Type | Source | Asset Path | Notes |",
                "|---|---|---|---|---|",
            ]
        )
        for item in items:
            lines.append(
                "| {score} | {asset_type} | {source_label} | `{asset_path}` | {note} |".format(**item)
            )

    with open(OUTPUT_MARKDOWN_PATH, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")


def write_json(total_assets_scanned, candidates_by_role, recommended_palette):
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": REPO_ROOT,
        "content_dir": CONTENT_DIR,
        "total_assets_scanned": total_assets_scanned,
        "roles": candidates_by_role,
        "recommended_palette": recommended_palette,
    }
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def load_curated_analysis():
    if not os.path.exists(ANALYSIS_JSON_PATH):
        return {}
    with open(ANALYSIS_JSON_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def write_overview(total_assets_scanned, candidates_by_role, recommended_palette):
    curated_analysis = load_curated_analysis()
    starter_palettes = curated_analysis.get("starter_palettes", {})
    recommended_families = curated_analysis.get("recommended_starting_families", [])
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Project Art Asset Scan Overview",
        "",
        "Use this file as the entry point for project-aware asset reuse.",
        "",
        "## What This Scan Gives Us",
        "",
        "- a current inventory generated from `E:/S2_/Content`",
        "- a role-based manifest for court-and-garden generation",
        "- a recommended palette payload that generators can consume automatically",
        "- a handoff layer for later progressive-disclosure Markdown docs",
        "",
        "## Current Baseline",
        "",
        "| Metric | Value |",
        "|---|---|",
        "| Generated at | {0} |".format(generated_at),
        "| Repo root | `{0}` |".format(REPO_ROOT),
        "| Content root | `{0}` |".format(CONTENT_DIR),
        "| Total `.uasset` files scanned | {0} |".format(total_assets_scanned),
        "| Roles with candidates | {0} |".format(sum(1 for role in ROLE_ORDER if candidates_by_role.get(role))),
        "| Recommended palette roles | {0} |".format(len(recommended_palette)),
        "",
        "## Read Order",
        "",
        "1. Start here for scan status and routing.",
        "2. Read `project-art-asset-analysis.md` for curated pack and role guidance.",
        "3. Read `project-art-asset-naming-convention-proposal.md` when planning naming cleanup or scan-quality improvements.",
        "4. Read `project-art-asset-inventory.md` when you need exact candidate paths by role.",
        "5. Read `project-art-asset-inventory.json` when a script or generator needs machine-readable palette data.",
        "",
        "## Generator Hook",
        "",
        "The current court-and-garden generator can consume the inventory-backed palette directly:",
        "",
        "- set `PALETTE_NAME = \"repo_scan_recommended\"`",
        "- use `PALETTE_APPLICATION_MODE = \"replace\"` or `\"overlay\"`",
        "",
        "This keeps the layout logic stable while swapping blockout placeholders for project-aware assets.",
        "",
        "## Scan Method",
        "",
        "- scans `.uasset` files under `Content/`",
        "- classifies by path and asset name heuristics",
        "- prefers blueprint and static mesh candidates",
        "- excludes obvious non-environment paths like animation, VFX, textures, and maps",
        "",
        "## Trust Model",
        "",
        "- treat the curated analysis as the best first recommendation layer",
        "- treat the raw inventory as a searchable candidate pool, not perfect truth",
        "- expect some false positives because this is not deep binary `.uasset` introspection",
        "- rescan when major environment packs land or when the manifest feels stale",
        "- use cached outputs by default instead of rescanning on every generator request",
        "",
        "## Refresh Command",
        "",
        "```powershell",
        "python \".codex/skills/engineer/graphic-engineer/game-level-building-python/scripts/build_project_art_asset_inventory.py\"",
        "```",
    ]

    if recommended_families:
        lines.extend(
            [
            "",
            "## Current Recommended Families",
            "",
        ]
        )
        for family_name in recommended_families:
            lines.append("- `{0}`".format(family_name))

    if starter_palettes:
        lines.extend(
            [
                "",
                "## Curated Starter Palettes",
                "",
            ]
        )
        for palette_name, palette_data in starter_palettes.items():
            lines.append("- `{0}`: {1}".format(palette_name, palette_data.get("intent", "")))

    lines.extend(
        [
            "",
            "## Next Step Toward Progressive Disclosure",
            "",
            "Use this overview as the root node, then branch later into:",
            "",
            "- pack documents",
            "- role documents",
            "- palette documents",
            "- exact asset-path leaf documents",
            "",
            "Until that deeper tree exists, this file is the canonical scan handoff document.",
        ]
    )

    with open(OUTPUT_OVERVIEW_PATH, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")


def main():
    total_assets_scanned, candidates_by_role = scan_assets()
    recommended_palette = make_recommended_palette(candidates_by_role)
    write_overview(total_assets_scanned, candidates_by_role, recommended_palette)
    write_markdown(total_assets_scanned, candidates_by_role, recommended_palette)
    write_json(total_assets_scanned, candidates_by_role, recommended_palette)
    print(OUTPUT_OVERVIEW_PATH)
    print("Wrote inventory:")
    print(OUTPUT_MARKDOWN_PATH)
    print(OUTPUT_JSON_PATH)


if __name__ == "__main__":
    main()
