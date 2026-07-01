import json
import os
from collections import defaultdict


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
REFERENCES_DIR = os.path.join(SKILL_DIR, "references")
INVENTORY_JSON_PATH = os.path.join(REFERENCES_DIR, "project-art-asset-inventory.json")
ANALYSIS_JSON_PATH = os.path.join(REFERENCES_DIR, "project-art-pack-analysis.json")
OUTPUT_ROOT = os.path.join(REFERENCES_DIR, "project-art-assets")

PACKS_DIR = os.path.join(OUTPUT_ROOT, "packs")
ROLES_DIR = os.path.join(OUTPUT_ROOT, "roles")
PALETTES_DIR = os.path.join(OUTPUT_ROOT, "palettes")
LEAVES_DIR = os.path.join(OUTPUT_ROOT, "leaves", "packs")

SOURCE_LABEL_TO_FAMILY_ID = {
    "s2_prototype": "s2_core_env_prototype",
    "s2_env_mesh": "s2_core_env_mesh",
    "asian_modular_temple": "asian_modular_temple",
    "uscans_wind_temple": "uscans_wind_temple",
    "bamboo_forest": "bamboo_forest",
    "deep_in_the_forest": "deep_in_the_forest",
}

FALLBACK_FAMILY_METADATA = {
    "dreamscape_tower": {
        "display_name": "Dreamscape Tower",
        "tier": 4,
        "strengths": ["stylized support"],
        "best_for": ["non-primary support references"],
        "path_prefixes": ["/Game/DreamscapeSeries/DreamscapeTower"],
    },
    "asian_forest_town_artref": {
        "display_name": "Asian Forest Town ArtRef",
        "tier": 4,
        "strengths": ["reference meshes", "look-dev support"],
        "best_for": ["reference only"],
        "path_prefixes": ["/Game/ArtRef/ASIAN_ForestTown_YOS3D"],
    },
    "massive_village": {
        "display_name": "Massive Village",
        "tier": 4,
        "strengths": ["village props", "bench support"],
        "best_for": ["non-primary support references"],
        "path_prefixes": ["/Game/Massive/MassiveVillage"],
    },
    "other": {
        "display_name": "Other",
        "tier": 5,
        "strengths": ["uncategorized"],
        "best_for": ["manual review"],
        "path_prefixes": [],
    },
}


def slugify(value):
    return value.replace("_", "-").replace(" ", "-").lower()


def titleize_label(value):
    return value.replace("_", " ").title()


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def write_text(path, lines):
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")


def rel_link(from_path, to_path):
    return os.path.relpath(to_path, os.path.dirname(from_path)).replace("\\", "/")


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def build_family_catalog(analysis, inventory):
    families = {}
    for family_id, data in analysis.get("families", {}).items():
        families[family_id] = {
            "family_id": family_id,
            "source_labels": set(),
            "display_name": data.get("display_name", titleize_label(family_id)),
            "tier": data.get("tier", 5),
            "strengths": data.get("strengths", []),
            "best_for": data.get("best_for", []),
            "path_prefixes": data.get("path_prefixes", []),
        }

    roles = inventory.get("roles", {})
    for role, assets in roles.items():
        for asset in assets:
            source_label = asset.get("source_label", "other")
            family_id = SOURCE_LABEL_TO_FAMILY_ID.get(source_label, source_label)
            if family_id not in families:
                fallback = FALLBACK_FAMILY_METADATA.get(
                    family_id,
                    {
                        "display_name": titleize_label(family_id),
                        "tier": 5,
                        "strengths": ["uncurated support"],
                        "best_for": ["manual review"],
                        "path_prefixes": [],
                    },
                )
                families[family_id] = {
                    "family_id": family_id,
                    "source_labels": set(),
                    "display_name": fallback["display_name"],
                    "tier": fallback["tier"],
                    "strengths": fallback["strengths"],
                    "best_for": fallback["best_for"],
                    "path_prefixes": fallback["path_prefixes"],
                }
            families[family_id]["source_labels"].add(source_label)

    for family in families.values():
        family["source_labels"] = sorted(family["source_labels"])

    return families


def build_role_family_index(inventory):
    role_family_assets = defaultdict(lambda: defaultdict(list))
    for role, assets in inventory.get("roles", {}).items():
        for asset in assets:
            source_label = asset.get("source_label", "other")
            family_id = SOURCE_LABEL_TO_FAMILY_ID.get(source_label, source_label)
            role_family_assets[role][family_id].append(asset)
    return role_family_assets


def write_root_index(inventory, analysis, families, role_family_assets):
    path = os.path.join(OUTPUT_ROOT, "index.md")
    lines = [
        "# Project Art Assets",
        "",
        "This is the progressive-disclosure root for project-aware asset reuse.",
        "",
        "## Read Order",
        "",
        "1. Read `../project-art-asset-scan-overview.md` for scan status and refresh rules.",
        "2. Read `../project-art-asset-analysis.md` for curated recommendations.",
        "3. Read `../project-art-asset-naming-convention-proposal.md` when planning naming cleanup or future scan hardening.",
        "4. Use the sections below to drill into packs, roles, and starter palettes.",
        "5. Use the leaf docs when you need exact asset paths grouped by pack and role.",
        "",
        "## Current Scan Snapshot",
        "",
        "| Metric | Value |",
        "|---|---|",
        "| Generated at UTC | {0} |".format(inventory.get("generated_at_utc", "unknown")),
        "| Total `.uasset` files scanned | {0} |".format(inventory.get("total_assets_scanned", 0)),
        "| Packs in tree | {0} |".format(len(families)),
        "| Roles in tree | {0} |".format(len(inventory.get("roles", {}))),
        "| Starter palettes | {0} |".format(len(analysis.get("starter_palettes", {}))),
        "",
        "## Sections",
        "",
        "- [Packs](packs/index.md)",
        "- [Roles](roles/index.md)",
        "- [Palettes](palettes/index.md)",
        "",
        "## Recommended Starting Families",
        "",
    ]

    for family_id in analysis.get("recommended_starting_families", []):
        family = families.get(family_id)
        if not family:
            continue
        lines.append("- [{0}](packs/{1}.md)".format(family["display_name"], slugify(family_id)))

    lines.extend(
        [
            "",
            "## Roles With Exact Leaf Docs",
            "",
        ]
    )
    for role in sorted(role_family_assets.keys()):
        lines.append("- [{0}](roles/{1}.md)".format(role, slugify(role)))

    write_text(path, lines)


def write_packs_index(families, role_family_assets):
    path = os.path.join(PACKS_DIR, "index.md")
    family_role_counts = defaultdict(int)
    for role, families_for_role in role_family_assets.items():
        for family_id in families_for_role.keys():
            family_role_counts[family_id] += 1

    lines = [
        "# Packs",
        "",
        "Browse asset families first when you want a coherent visual language.",
        "",
        "| Pack | Tier | Supported Roles |",
        "|---|---|---|",
    ]

    for family_id, family in sorted(families.items(), key=lambda item: (item[1]["tier"], item[1]["display_name"])):
        lines.append(
            "| [{0}]({1}.md) | {2} | {3} |".format(
                family["display_name"],
                slugify(family_id),
                family["tier"],
                family_role_counts.get(family_id, 0),
            )
        )

    write_text(path, lines)


def write_pack_docs(families, role_family_assets):
    for family_id, family in families.items():
        path = os.path.join(PACKS_DIR, "{0}.md".format(slugify(family_id)))
        role_rows = []
        for role, families_for_role in sorted(role_family_assets.items()):
            assets = families_for_role.get(family_id, [])
            if not assets:
                continue
            leaf_path = os.path.join(LEAVES_DIR, slugify(family_id), "{0}.md".format(slugify(role)))
            role_rows.append((role, len(assets), leaf_path))

        lines = [
            "# {0}".format(family["display_name"]),
            "",
            "[Back to packs](index.md)",
            "",
            "## Summary",
            "",
            "| Field | Value |",
            "|---|---|",
            "| Family ID | `{0}` |".format(family_id),
            "| Tier | {0} |".format(family["tier"]),
            "| Source Labels | {0} |".format(", ".join("`{0}`".format(item) for item in family["source_labels"]) or "n/a"),
            "",
            "## Strengths",
            "",
        ]

        for item in family["strengths"]:
            lines.append("- {0}".format(item))

        lines.extend(
            [
                "",
                "## Best For",
                "",
            ]
        )
        for item in family["best_for"]:
            lines.append("- {0}".format(item))

        lines.extend(
            [
                "",
                "## Supported Roles",
                "",
                "| Role | Candidate Count | Exact Asset Leaf |",
                "|---|---|---|",
            ]
        )
        for role, count, leaf_path in role_rows:
            lines.append(
                "| [{0}]({1}) | {2} | [Leaf]({3}) |".format(
                    role,
                    rel_link(path, os.path.join(ROLES_DIR, "{0}.md".format(slugify(role)))),
                    count,
                    rel_link(path, leaf_path),
                )
            )

        write_text(path, lines)


def write_roles_index(inventory):
    path = os.path.join(ROLES_DIR, "index.md")
    lines = [
        "# Roles",
        "",
        "Browse by gameplay or layout role when you know what the generator needs to place.",
        "",
        "| Role | Candidate Count |",
        "|---|---|",
    ]

    for role, assets in sorted(inventory.get("roles", {}).items()):
        lines.append("| [{0}]({1}.md) | {2} |".format(role, slugify(role), len(assets)))

    write_text(path, lines)


def write_role_docs(families, role_family_assets):
    for role, families_for_role in sorted(role_family_assets.items()):
        path = os.path.join(ROLES_DIR, "{0}.md".format(slugify(role)))
        total_assets = sum(len(items) for items in families_for_role.values())
        lines = [
            "# {0}".format(role),
            "",
            "[Back to roles](index.md)",
            "",
            "## Summary",
            "",
            "| Field | Value |",
            "|---|---|",
            "| Role | `{0}` |".format(role),
            "| Total Candidates | {0} |".format(total_assets),
            "| Families With Candidates | {0} |".format(len(families_for_role)),
            "",
            "## Families",
            "",
            "| Family | Count | Exact Asset Leaf |",
            "|---|---|---|",
        ]

        for family_id, assets in sorted(
            families_for_role.items(),
            key=lambda item: (families[item[0]]["tier"], -len(item[1]), families[item[0]]["display_name"]),
        ):
            leaf_path = os.path.join(LEAVES_DIR, slugify(family_id), "{0}.md".format(slugify(role)))
            lines.append(
                "| [{0}]({1}) | {2} | [Leaf]({3}) |".format(
                    families[family_id]["display_name"],
                    rel_link(path, os.path.join(PACKS_DIR, "{0}.md".format(slugify(family_id)))),
                    len(assets),
                    rel_link(path, leaf_path),
                )
            )

        lines.extend(
            [
                "",
                "## Top Candidates",
                "",
                "| Asset Name | Family | Type | Path |",
                "|---|---|---|---|",
            ]
        )

        top_assets = []
        for assets in families_for_role.values():
            top_assets.extend(assets[:2])
        top_assets.sort(key=lambda item: (-item.get("score", 0), item["asset_path"]))

        for asset in top_assets[:8]:
            family_id = SOURCE_LABEL_TO_FAMILY_ID.get(asset.get("source_label", "other"), asset.get("source_label", "other"))
            lines.append(
                "| `{0}` | [{1}]({2}) | {3} | `{4}` |".format(
                    asset["asset_name"],
                    families[family_id]["display_name"],
                    rel_link(path, os.path.join(PACKS_DIR, "{0}.md".format(slugify(family_id)))),
                    asset["asset_type"],
                    asset["asset_path"],
                )
            )

        write_text(path, lines)


def write_palettes_index(analysis):
    path = os.path.join(PALETTES_DIR, "index.md")
    lines = [
        "# Palettes",
        "",
        "Starter palettes combine packs into a recommended first-pass generation strategy.",
        "",
        "| Palette | Families |",
        "|---|---|",
    ]
    for palette_name, palette_data in sorted(analysis.get("starter_palettes", {}).items()):
        lines.append(
            "| [{0}]({1}.md) | {2} |".format(
                palette_name,
                slugify(palette_name),
                len(palette_data.get("families", [])),
            )
        )

    write_text(path, lines)


def write_palette_docs(analysis, families):
    for palette_name, palette_data in sorted(analysis.get("starter_palettes", {}).items()):
        path = os.path.join(PALETTES_DIR, "{0}.md".format(slugify(palette_name)))
        lines = [
            "# {0}".format(palette_name),
            "",
            "[Back to palettes](index.md)",
            "",
            "## Intent",
            "",
            palette_data.get("intent", "No intent recorded."),
            "",
            "## Families",
            "",
        ]

        for family_id in palette_data.get("families", []):
            family = families.get(family_id)
            if not family:
                continue
            lines.append(
                "- [{0}]({1})".format(
                    family["display_name"],
                    rel_link(path, os.path.join(PACKS_DIR, "{0}.md".format(slugify(family_id)))),
                )
            )

        lines.extend(
            [
                "",
                "## Suggested Role Drilldown",
                "",
                "- [Walls]({0})".format(rel_link(path, os.path.join(ROLES_DIR, "wall.md"))),
                "- [Pavilions]({0})".format(rel_link(path, os.path.join(ROLES_DIR, "pavilion.md"))),
                "- [Ponds]({0})".format(rel_link(path, os.path.join(ROLES_DIR, "pond.md"))),
                "- [Trees]({0})".format(rel_link(path, os.path.join(ROLES_DIR, "tree.md"))),
                "- [Rockery]({0})".format(rel_link(path, os.path.join(ROLES_DIR, "rockery.md"))),
            ]
        )

        write_text(path, lines)


def write_leaf_docs(families, role_family_assets):
    leaves_index_path = os.path.join(OUTPUT_ROOT, "leaves", "index.md")
    leaves_index_lines = [
        "# Leaves",
        "",
        "Leaf docs contain exact asset paths grouped by pack and role.",
        "",
    ]

    for family_id, family in sorted(families.items(), key=lambda item: (item[1]["tier"], item[1]["display_name"])):
        family_leaf_dir = os.path.join(LEAVES_DIR, slugify(family_id))
        ensure_dir(family_leaf_dir)
        family_links = []
        for role, families_for_role in sorted(role_family_assets.items()):
            assets = families_for_role.get(family_id, [])
            if not assets:
                continue

            path = os.path.join(family_leaf_dir, "{0}.md".format(slugify(role)))
            lines = [
                "# {0} / {1}".format(family["display_name"], role),
                "",
                "[Back to pack]({0})".format(
                    rel_link(path, os.path.join(PACKS_DIR, "{0}.md".format(slugify(family_id))))
                ),
                "",
                "[Back to role]({0})".format(
                    rel_link(path, os.path.join(ROLES_DIR, "{0}.md".format(slugify(role))))
                ),
                "",
                "## Exact Asset Candidates",
                "",
                "| Score | Asset Name | Type | Path | Notes |",
                "|---|---|---|---|---|",
            ]

            for asset in assets:
                lines.append(
                    "| {0} | `{1}` | {2} | `{3}` | {4} |".format(
                        asset.get("score", 0),
                        asset["asset_name"],
                        asset["asset_type"],
                        asset["asset_path"],
                        asset.get("note", ""),
                    )
                )

            write_text(path, lines)
            family_links.append("- [{0}]({1}/{2}.md)".format(role, slugify(family_id), slugify(role)))

        if family_links:
            leaves_index_lines.extend(
                [
                    "## {0}".format(family["display_name"]),
                    "",
                ]
            )
            leaves_index_lines.extend(family_links)
            leaves_index_lines.append("")

    write_text(leaves_index_path, leaves_index_lines)


def main():
    inventory = load_json(INVENTORY_JSON_PATH)
    analysis = load_json(ANALYSIS_JSON_PATH)
    families = build_family_catalog(analysis, inventory)
    role_family_assets = build_role_family_index(inventory)

    ensure_dir(OUTPUT_ROOT)
    ensure_dir(PACKS_DIR)
    ensure_dir(ROLES_DIR)
    ensure_dir(PALETTES_DIR)
    ensure_dir(LEAVES_DIR)

    write_root_index(inventory, analysis, families, role_family_assets)
    write_packs_index(families, role_family_assets)
    write_pack_docs(families, role_family_assets)
    write_roles_index(inventory)
    write_role_docs(families, role_family_assets)
    write_palettes_index(analysis)
    write_palette_docs(analysis, families)
    write_leaf_docs(families, role_family_assets)

    print("Wrote progressive-disclosure tree:")
    print(OUTPUT_ROOT)


if __name__ == "__main__":
    main()
