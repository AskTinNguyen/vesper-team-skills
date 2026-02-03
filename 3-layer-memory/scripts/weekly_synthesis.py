#!/usr/bin/env python3
"""
Weekly synthesis process for the three-layer memory system.
Rewrites entity summaries from active facts and prunes stale context.
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple


def get_home_dir() -> Path:
    """Get the user's home directory."""
    return Path.home()


def load_system_config() -> Dict[str, Any]:
    """Load system configuration."""
    config_path = get_home_dir() / ".memory_system"
    if config_path.exists():
        return json.loads(config_path.read_text())
    return {}


def save_system_config(config: Dict[str, Any]):
    """Save system configuration."""
    config_path = get_home_dir() / ".memory_system"
    config_path.write_text(json.dumps(config, indent=2))


def find_all_entities() -> List[Tuple[str, str, Path]]:
    """Find all entities in the knowledge graph."""
    home = get_home_dir()
    entities = []
    
    base_path = home / "life" / "areas"
    for entity_type in ["people", "companies", "projects"]:
        type_path = base_path / entity_type
        if type_path.exists():
            for entity_dir in type_path.iterdir():
                if entity_dir.is_dir() and not entity_dir.name.startswith("."):
                    entities.append((entity_type, entity_dir.name, entity_dir))
    
    return entities


def load_entity_data(entity_type: str, entity_name: str) -> Tuple[Dict, str]:
    """Load both items.json and summary.md for an entity."""
    home = get_home_dir()
    entity_dir = home / "life" / "areas" / entity_type / entity_name
    
    items_path = entity_dir / "items.json"
    summary_path = entity_dir / "summary.md"
    
    items_data = json.loads(items_path.read_text()) if items_path.exists() else {"facts": []}
    summary_text = summary_path.read_text() if summary_path.exists() else ""
    
    return items_data, summary_text


def save_summary(entity_type: str, entity_name: str, summary_text: str):
    """Save updated summary for an entity."""
    home = get_home_dir()
    summary_path = home / "life" / "areas" / entity_type / entity_name / "summary.md"
    summary_path.write_text(summary_text)


def get_active_facts(facts: List[Dict]) -> List[Dict]:
    """Filter to only active (non-superseded) facts."""
    return [f for f in facts if f.get("status") == "active"]


def get_recent_facts(facts: List[Dict], days: int = 7) -> List[Dict]:
    """Get facts created or modified in the last N days."""
    cutoff = datetime.now() - timedelta(days=days)
    recent = []
    
    for fact in facts:
        try:
            fact_date = datetime.strptime(fact.get("timestamp", "2000-01-01"), "%Y-%m-%d")
            if fact_date >= cutoff:
                recent.append(fact)
        except ValueError:
            pass
    
    return recent


def identify_contradictions(facts: List[Dict]) -> List[Tuple[Dict, Dict]]:
    """
    Identify facts that likely contradict each other.
    Returns list of (old_fact, new_fact) pairs.
    In practice, this would use an LLM to detect contradictions.
    """
    # Placeholder - actual implementation would analyze fact text
    # For now, we'll rely on manual superseding
    return []


def generate_summary(entity_name: str, entity_type: str, facts: List[Dict]) -> str:
    """
    Generate a living summary from active facts.
    In practice, this would use an LLM to synthesize the summary.
    """
    display_name = entity_name.replace("-", " ").title()
    
    lines = [
        f"# {display_name}",
        "",
        "## Current Context",
        ""
    ]
    
    # Group facts by category
    by_category = {}
    for fact in facts:
        cat = fact.get("category", "status")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(fact)
    
    # Add facts by category
    category_order = ["relationship", "status", "milestone", "preference"]
    category_labels = {
        "relationship": "Relationship",
        "status": "Current Status",
        "milestone": "Recent Milestones",
        "preference": "Preferences"
    }
    
    for cat in category_order:
        if cat in by_category:
            lines.append(f"### {category_labels.get(cat, cat)}")
            lines.append("")
            for fact in by_category[cat]:
                lines.append(f"- {fact['fact']}")
            lines.append("")
    
    # Add timeline section
    lines.append("## Timeline")
    lines.append("")
    
    sorted_facts = sorted(facts, key=lambda f: f.get("timestamp", "2000-01-01"))
    for fact in sorted_facts:
        date = fact.get("timestamp", "unknown")
        lines.append(f"- {date}: {fact['fact']}")
    
    lines.append("")
    lines.append("---")
    lines.append(f"*Last synthesized: {datetime.now().strftime("%Y-%m-%d")}*")
    lines.append(f"*Active facts: {len(facts)}*")
    
    return "\n".join(lines)


def synthesize_entity(entity_type: str, entity_name: str, dry_run: bool = False) -> bool:
    """Run synthesis for a single entity."""
    items_data, old_summary = load_entity_data(entity_type, entity_name)
    facts = items_data.get("facts", [])
    
    if not facts:
        return False
    
    active_facts = get_active_facts(facts)
    
    if not active_facts:
        return False
    
    # Generate new summary
    new_summary = generate_summary(entity_name, entity_type, active_facts)
    
    if dry_run:
        print(f"\n{'='*50}")
        print(f"Would update: {entity_type}/{entity_name}")
        print(f"Active facts: {len(active_facts)}")
        print(f"Superseded facts: {len(facts) - len(active_facts)}")
        print("\nNew summary preview:")
        print(new_summary[:500] + "..." if len(new_summary) > 500 else new_summary)
        return True
    
    # Save new summary
    save_summary(entity_type, entity_name, new_summary)
    print(f"✓ Updated summary: {entity_type}/{entity_name}")
    
    return True


def run_full_synthesis(dry_run: bool = False, force: bool = False):
    """Run synthesis for all entities."""
    config = load_system_config()
    entities = find_all_entities()
    
    if not entities:
        print("No entities found in knowledge graph.")
        return
    
    print(f"Found {len(entities)} entities")
    print()
    
    updated_count = 0
    
    for entity_type, entity_name, entity_dir in entities:
        # Skip example entity unless forced
        if entity_name == "example-person" and not force:
            continue
        
        if synthesize_entity(entity_type, entity_name, dry_run):
            updated_count += 1
    
    print()
    print(f"Synthesis complete: {updated_count} entities updated")
    
    if not dry_run:
        config["lastSynthesisTimestamp"] = datetime.now().isoformat()
        save_system_config(config)
        print(f"Last synthesis time updated")


def main():
    parser = argparse.ArgumentParser(description="Weekly synthesis for the memory system")
    parser.add_argument("--dry-run", "-d", action="store_true", help="Show what would be changed without making changes")
    parser.add_argument("--force", "-f", action="store_true", help="Include example entities")
    parser.add_argument("--entity-type", "-t", choices=["people", "companies", "projects"], help="Synthesize only this entity type")
    parser.add_argument("--entity-name", "-n", help="Synthesize only this entity")
    
    args = parser.parse_args()
    
    print("Three-Layer Memory System — Weekly Synthesis")
    print("=" * 50)
    print()
    
    if args.entity_type and args.entity_name:
        # Single entity synthesis
        synthesize_entity(args.entity_type, args.entity_name, args.dry_run)
    else:
        # Full synthesis
        run_full_synthesis(dry_run=args.dry_run, force=args.force)


if __name__ == "__main__":
    main()
