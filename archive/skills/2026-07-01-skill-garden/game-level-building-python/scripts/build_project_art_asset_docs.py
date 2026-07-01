import json
import os
from collections import Counter


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
REFERENCES_DIR = os.path.join(SKILL_DIR, "references")
INVENTORY_JSON_PATH = os.path.join(REFERENCES_DIR, "project-art-asset-inventory.json")
PACK_ANALYSIS_JSON_PATH = os.path.join(REFERENCES_DIR, "project-art-pack-analysis.json")
OUTPUT_ROOT = os.path.join(REFERENCES_DIR, "project-art-assets")
PACKS_DIR = os.path.join(OUTPUT_ROOT, "packs")
ROLES_DIR = os.path.join(OUTPUT_ROOT, "roles")
PALETTES_DIR = os.path.join(OUTPUT_ROOT, "palettes")

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

ROLE_LABELS = {
    "wall": "Wall",
    "screen_wall": "Screen Wall",
    "gate": "Gate",
    "moon_gate": "Moon Gate",
    "main_hall": "Main Hall",
    "villa": "Villa",
    "pavilion": "Pavilion",
    "pond": "Pond",
    "tree": "Tree",
    "rockery": "Rockery",
    "bench": "Bench",
    "decor": "Decor",
}

ROLE_GUIDANCE = {
    "wall": "Use for perimeter edges, compartment dividers, and formal court boundaries.",
    "screen_wall": "Use for view blockers, court layering, and ornamental separators rather than hard perimeter walls.",
    "gate": "Use for primary entrances, threshold framing, and perimeter openings.",
    "moon_gate": "Use only when a role is explicitly a moon or circular gate. The current scan does not find explicit candidates yet.",
    "main_hall": "Use for formal anchor buildings and compound focal architecture.",
    "villa": "Use for retreat structures, island pavilions, and hill villas that read as destination buildings.",
    "pavilion": "Use for tea houses, garden pavilions, and small architectural anchors inside a court.",
    "pond": "Use for water features, basins, and pond-centered layout moments.",
    "tree": "Use for curated canopy placement, potted tree accents, and major vertical nature forms.",
    "rockery": "Use for edge shaping, islands, natural borders, and terrain-like composition support.",
    "bench": "Use for seating, small rest points, and soft gathering beats.",
    "decor": "Use for altar, statue, vase, burner, and non-structural scene accents.",
}

SOURCE_TO_FAMILY = {
    "s2_prototype": "s2_core_env_prototype",
    "s2_env_mesh": "s2_core_env_mesh",
    "asian_modular_temple": "asian_modular_temple",
    "uscans_wind_temple": "uscans_wind_temple",
    "bamboo_forest": "bamboo_forest",
    "deep_in_the_forest": "deep_in_the_forest",
}


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def rel_link(from_path, to_path):
    return os.path.relpath(to_path, os.path.dirname(from_path)).replace("\\", "/")


def write_markdown(path, lines):
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")


def role_doc_path(role):
    return os.path.join(ROLES_DIR, "{0}.md".format(role))


def family_doc_path(family_id):
    return os.path.join(PACKS_DIR, "{0}.md".format(family_id))


def palette_doc_path(palette_name):
    return os.path.join(PALETTES_DIR, "{0}.md".format(palette_name))


def infer_family_id(asset_item, families):
    source_label = asset_item.get("source_label")
    mapped = SOURCE_TO_FAMILY.get(source_label)
    if mapped:
        return mapped
    asset_path = asset_item.get("asset_path", "")
    for family_id, family_data in families.items():
        for prefix in family_data.get("path_prefixes", []):
            if asset_path.startswith(prefix):
                return family_id
    return None


def top_family_ids_for_role(role, role_items, families):
    counts = Counter()
    for item in role_items.get(role, []):
        family_id = infer_family_id(item, families)
        if family_id:
            counts[family_id] += 1
    return [family_id for family_id, _ in counts.most_common(3)]


def build_role_docs(inventory, analysis):
    families = analysis["families"]
    role_items = inventory["roles"]

    for role in ROLE_ORDER:
        output_path = role_doc_path(role)
        items = role_items.get(role, [])
        top_families = top_family_ids_for_role(role, role_items, families)
        lines = [
            "# {0}".format(ROLE_LABELS[role]),
            "",
            ROLE_GUIDANCE[role],
            "",
            "## Snapshot",
            "",
            "| Metric | Value |",
            "|---|---|",
            "| Candidate count | {0} |".format(len(items)),
            "| Top family candidates | {0} |".format(", ".join(top_families) if top_families else "Needs curation"),
            "",
            "## Recommended Families",
            "",
        ]

        if top_families:
            for family_id in top_families:
                lines.append("- [{0}]({1})".format(
                    analysis["families"][family_id]["display_name"],
                    rel_link(output_path, family_doc_path(family_id)),
                ))
        else:
            lines.append("- No explicit candidates found in the current scan.")
            if role == "moon_gate":
                lines.append("- Use the [Gate]({0}) doc as a fallback until explicit `MoonGate` assets exist.".format(
                    rel_link(output_path, role_doc_path("gate"))
                ))

        lines.extend(
            [
                "",
                "## Candidate Assets",
                "",
            ]
        )

        if items:
            lines.extend(
                [
                    "| Score | Asset Type | Source | Asset Path | Notes |",
                    "|---|---|---|---|---|",
                ]
            )
            for item in items[:12]:
                lines.append(
                    "| {0} | {1} | {2} | `{3}` | {4} |".format(
                        item["score"],
                        item["asset_type"],
                        item["source_label"],
                        item["asset_path"],
                        item["note"],
                    )
                )
        else:
            lines.append("No explicit candidates were found for this role in the current scan.")

        lines.extend(
            [
                "",
                "## Related Palettes",
                "",
            ]
        )

        related_palette_lines = []
        for palette_name, palette_data in analysis["starter_palettes"].items():
            if any(family_id in palette_data["families"] for family_id in top_families):
                related_palette_lines.append(
                    "- [{0}]({1})".format(
                        palette_name,
                        rel_link(output_path, palette_doc_path(palette_name)),
                    )
                )
        if role == "moon_gate" and not related_palette_lines:
            related_palette_lines.append("- No curated palette maps this role yet.")

        lines.extend(related_palette_lines or ["- No palette emphasis for this role yet."])
        write_markdown(output_path, lines)


def build_family_docs(inventory, analysis):
    families = analysis["families"]
    role_items = inventory["roles"]

    for family_id in analysis["recommended_starting_families"]:
        family = families[family_id]
        output_path = family_doc_path(family_id)
        role_matches = []
        sample_assets = []
        seen_paths = set()

        for role in ROLE_ORDER:
            matches = []
            for item in role_items.get(role, []):
                inferred_family_id = infer_family_id(item, families)
                if inferred_family_id == family_id:
                    matches.append(item)
            if matches:
                role_matches.append((role, len(matches)))
                for item in matches[:2]:
                    if item["asset_path"] in seen_paths:
                        continue
                    sample_assets.append(item)
                    seen_paths.add(item["asset_path"])

        lines = [
            "# {0}".format(family["display_name"]),
            "",
            "## Snapshot",
            "",
            "| Metric | Value |",
            "|---|---|",
            "| Tier | {0} |".format(family["tier"]),
            "| Path Prefixes | {0} |".format(", ".join("`{0}`".format(prefix) for prefix in family["path_prefixes"])),
            "| Roles covered by current scan | {0} |".format(len(role_matches)),
            "",
            "## Strengths",
            "",
        ]

        for value in family["strengths"]:
            lines.append("- {0}".format(value))

        lines.extend(
            [
                "",
                "## Best For",
                "",
            ]
        )
        for value in family["best_for"]:
            lines.append("- {0}".format(value))

        lines.extend(
            [
                "",
                "## Role Coverage",
                "",
            ]
        )
        for role, count in role_matches:
            lines.append(
                "- [{0}]({1}): {2} candidate(s) in the current scan".format(
                    ROLE_LABELS[role],
                    rel_link(output_path, role_doc_path(role)),
                    count,
                )
            )

        lines.extend(
            [
                "",
                "## Sample Assets",
                "",
            ]
        )
        if sample_assets:
            lines.extend(
                [
                    "| Role | Asset Name | Asset Path |",
                    "|---|---|---|",
                ]
            )
            for item in sample_assets[:10]:
                matched_role = next((role for role in ROLE_ORDER if item in role_items.get(role, [])), "unknown")
                lines.append(
                    "| {0} | {1} | `{2}` |".format(
                        ROLE_LABELS.get(matched_role, matched_role),
                        item["asset_name"],
                        item["asset_path"],
                    )
                )
        else:
            lines.append("No sample assets were resolved for this family from the current role inventory.")

        lines.extend(
            [
                "",
                "## Related Palettes",
                "",
            ]
        )
        related_palettes = []
        for palette_name, palette_data in analysis["starter_palettes"].items():
            if family_id in palette_data["families"]:
                related_palettes.append(
                    "- [{0}]({1})".format(
                        palette_name,
                        rel_link(output_path, palette_doc_path(palette_name)),
                    )
                )
        lines.extend(related_palettes or ["- No starter palette references this family yet."])
        write_markdown(output_path, lines)


def pick_palette_assets(inventory, analysis, palette_name, allowed_family_ids):
    families = analysis["families"]
    selected = []
    for role in ROLE_ORDER:
        for item in inventory["roles"].get(role, []):
            family_id = infer_family_id(item, families)
            if family_id in allowed_family_ids:
                selected.append((role, item))
                break
    return selected


def build_palette_docs(inventory, analysis):
    for palette_name, palette_data in analysis["starter_palettes"].items():
        output_path = palette_doc_path(palette_name)
        selected_assets = pick_palette_assets(inventory, analysis, palette_name, set(palette_data["families"]))
        lines = [
            "# {0}".format(palette_name),
            "",
            palette_data["intent"],
            "",
            "## Family Mix",
            "",
        ]

        for family_id in palette_data["families"]:
            lines.append(
                "- [{0}]({1})".format(
                    analysis["families"][family_id]["display_name"],
                    rel_link(output_path, family_doc_path(family_id)),
                )
            )

        lines.extend(
            [
                "",
                "## Suggested Role Coverage",
                "",
            ]
        )

        if selected_assets:
            lines.extend(
                [
                    "| Role | Source | Asset Name | Asset Path |",
                    "|---|---|---|---|",
                ]
            )
            for role, item in selected_assets:
                lines.append(
                    "| [{0}]({1}) | {2} | {3} | `{4}` |".format(
                        ROLE_LABELS[role],
                        rel_link(output_path, role_doc_path(role)),
                        item["source_label"],
                        item["asset_name"],
                        item["asset_path"],
                    )
                )
        else:
            lines.append("No palette-specific role assets were resolved from the current inventory.")

        write_markdown(output_path, lines)


def build_indexes(inventory, analysis):
    root_index = os.path.join(OUTPUT_ROOT, "index.md")
    pack_index = os.path.join(PACKS_DIR, "index.md")
    role_index = os.path.join(ROLES_DIR, "index.md")
    palette_index = os.path.join(PALETTES_DIR, "index.md")
    naming_doc = os.path.join(REFERENCES_DIR, "project-art-naming-cleanup-proposal.md")
    overview_doc = os.path.join(REFERENCES_DIR, "project-art-asset-scan-overview.md")
    analysis_doc = os.path.join(REFERENCES_DIR, "project-art-asset-analysis.md")
    inventory_doc = os.path.join(REFERENCES_DIR, "project-art-asset-inventory.md")

    write_markdown(
        root_index,
        [
            "# Project Art Assets",
            "",
            "This is the progressive-disclosure entry point for project-aware asset reuse.",
            "",
            "## Start Here",
            "",
            "1. Read the [scan overview]({0}).".format(rel_link(root_index, overview_doc)),
            "2. Read the [curated analysis]({0}).".format(rel_link(root_index, analysis_doc)),
            "3. Use [palettes]({0}) when you want a recommended mix.".format(rel_link(root_index, palette_index)),
            "4. Use [packs]({0}) when you want to browse by family.".format(rel_link(root_index, pack_index)),
            "5. Use [roles]({0}) when you want exact candidate paths by semantic role.".format(rel_link(root_index, role_index)),
            "6. Use the [naming cleanup proposal]({0}) when planning asset renames for stronger future scans.".format(rel_link(root_index, naming_doc)),
            "",
            "## Baseline",
            "",
            "| Metric | Value |",
            "|---|---|",
            "| Total `.uasset` files scanned | {0} |".format(inventory["total_assets_scanned"]),
            "| Roles with candidates | {0} |".format(len(inventory["roles"])),
            "| Curated starter palettes | {0} |".format(len(analysis["starter_palettes"])),
            "| Recommended families | {0} |".format(len(analysis["recommended_starting_families"])),
            "",
            "## Fast Paths",
            "",
            "- Use [project_native_court_garden]({0}) for safest project-native swaps.".format(
                rel_link(root_index, palette_doc_path("project_native_court_garden"))
            ),
            "- Use [prototype_plus_modular_temple]({0}) for cleaner walls and halls.".format(
                rel_link(root_index, palette_doc_path("prototype_plus_modular_temple"))
            ),
            "- Use [garden_overgrowth_support]({0}) for greener, older courts.".format(
                rel_link(root_index, palette_doc_path("garden_overgrowth_support"))
            ),
        ],
    )

    pack_lines = [
        "# Packs",
        "",
        "Browse environment families by pack or source set.",
        "",
        "| Family | Tier | Best For |",
        "|---|---|---|",
    ]
    for family_id in analysis["recommended_starting_families"]:
        family = analysis["families"][family_id]
        pack_lines.append(
            "| [{0}]({1}) | {2} | {3} |".format(
                family["display_name"],
                rel_link(pack_index, family_doc_path(family_id)),
                family["tier"],
                ", ".join(family["best_for"][:2]),
            )
        )
    write_markdown(pack_index, pack_lines)

    role_lines = [
        "# Roles",
        "",
        "Browse exact candidates by semantic layout role.",
        "",
        "| Role | Candidate Count | Top Sources |",
        "|---|---|---|",
    ]
    for role in ROLE_ORDER:
        items = inventory["roles"].get(role, [])
        top_sources = ", ".join(sorted({item["source_label"] for item in items[:4]})) if items else "Needs curation"
        role_lines.append(
            "| [{0}]({1}) | {2} | {3} |".format(
                ROLE_LABELS[role],
                rel_link(role_index, role_doc_path(role)),
                len(items),
                top_sources,
            )
        )
    write_markdown(role_index, role_lines)

    palette_lines = [
        "# Palettes",
        "",
        "Browse recommended family mixes for generator-driven asset swaps.",
        "",
        "| Palette | Families | Intent |",
        "|---|---|---|",
    ]
    for palette_name, palette_data in analysis["starter_palettes"].items():
        family_names = [analysis["families"][family_id]["display_name"] for family_id in palette_data["families"]]
        palette_lines.append(
            "| [{0}]({1}) | {2} | {3} |".format(
                palette_name,
                rel_link(palette_index, palette_doc_path(palette_name)),
                ", ".join(family_names),
                palette_data["intent"],
            )
        )
    write_markdown(palette_index, palette_lines)


def main():
    with open(INVENTORY_JSON_PATH, "r", encoding="utf-8") as handle:
        inventory = json.load(handle)
    with open(PACK_ANALYSIS_JSON_PATH, "r", encoding="utf-8") as handle:
        analysis = json.load(handle)

    ensure_dir(OUTPUT_ROOT)
    ensure_dir(PACKS_DIR)
    ensure_dir(ROLES_DIR)
    ensure_dir(PALETTES_DIR)

    build_role_docs(inventory, analysis)
    build_family_docs(inventory, analysis)
    build_palette_docs(inventory, analysis)
    build_indexes(inventory, analysis)

    print("Wrote project art asset docs:")
    print(OUTPUT_ROOT)


if __name__ == "__main__":
    main()
