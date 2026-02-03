#!/usr/bin/env python3
"""
Weekly synthesis process for the three-layer memory system.
Optional automation — manual synthesis is the default.
"""

import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple


def get_home_dir() -> Path:
    """Get the user's home directory."""
    return Path.home()


def find_all_entities() -> List[Tuple[str, str, Path]]:
    """Find all entities in the knowledge graph."""
    home = get_home_dir()
    entities = []
    
    entities_dir = home / "life" / "entities"
    if not entities_dir.exists():
        return entities
    
    for file_path in entities_dir.iterdir():
        if not file_path.is_file() or not file_path.suffix == ".md":
            continue
        
        # Parse filename: name.type.md
        parts = file_path.stem.split(".")
        if len(parts) < 2:
            continue
        
        entity_type = parts[-1]
        entity_name = ".".join(parts[:-1])
        entities.append((entity_type, entity_name, file_path))
    
    return entities


def load_entity_content(file_path: Path) -> Tuple[Dict, str]:
    """Load entity file and parse frontmatter and body."""
    content = file_path.read_text()
    frontmatter = {}
    body = content
    
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            import yaml
            try:
                frontmatter = yaml.safe_load(parts[1]) or {}
                body = parts[2]
            except Exception:
                pass
    
    return frontmatter, body


def extract_facts(body: str) -> Tuple[List[str], List[str]]:
    """Extract current and historical facts from entity body."""
    current_facts = []
    historical_facts = []
    
    lines = body.split("\n")
    in_facts_section = False
    
    for line in lines:
        # Track if we're in a Key Facts section
        if line.strip().startswith("## Key Facts"):
            in_facts_section = True
            continue
        elif line.strip().startswith("## ") and in_facts_section:
            in_facts_section = False
        
        # Extract facts
        if line.strip().startswith("- [current]"):
            fact_text = line.strip()[len("- [current] "):].strip()
            current_facts.append(fact_text)
        elif line.strip().startswith("- [was]"):
            fact_text = line.strip()[len("- [was] "):].strip()
            historical_facts.append(fact_text)
    
    return current_facts, historical_facts


def rewrite_summary(file_path: Path, entity_name: str, entity_type: str, 
                    current_facts: List[str], dry_run: bool = False) -> bool:
    """Rewrite the summary section of an entity file."""
    content = file_path.read_text()
    frontmatter, body = load_entity_content(file_path)
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Generate new summary
    display_name = entity_name.replace("-", " ").title()
    
    new_summary = f"# {display_name}\n\n"
    
    # Add one-line description from first current fact
    if current_facts:
        first_fact = current_facts[0].split(" — ")[0]  # Remove date
        new_summary += f"> {first_fact}\n\n"
    
    # Build new body while preserving Key Facts section
    lines = body.split("\n")
    new_lines = []
    i = 0
    
    # Skip old summary (everything before ## Key Facts or ## Context)
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("## Key Facts") or line.strip().startswith("## Context"):
            break
        i += 1
    
    # Add the rest of the file (Key Facts and Context sections)
    while i < len(lines):
        new_lines.append(lines[i])
        i += 1
    
    body = "\n".join(new_lines)
    
    # Reconstruct file
    if frontmatter:
        import yaml
        fm_text = yaml.dump(frontmatter, default_flow_style=False).strip()
        new_content = f"---\n{fm_text}\n---\n{new_summary}{body}"
    else:
        new_content = new_summary + body
    
    if dry_run:
        print(f"\n{'='*50}")
        print(f"Would update: {file_path.name}")
        print(f"Current facts: {len(current_facts)}")
        print(f"\nNew summary preview:")
        print(new_summary)
        return True
    
    file_path.write_text(new_content)
    print(f"✓ Updated summary: {file_path.name}")
    
    return True


def run_synthesis(dry_run: bool = False, force: bool = False):
    """Run synthesis for all entities."""
    entities = find_all_entities()
    
    if not entities:
        print("No entities found in knowledge graph.")
        return
    
    print(f"Found {len(entities)} entities")
    print()
    
    updated_count = 0
    
    for entity_type, entity_name, file_path in entities:
        # Skip example entity unless forced
        if entity_name == "example-person" and not force:
            continue
        
        frontmatter, body = load_entity_content(file_path)
        current_facts, historical_facts = extract_facts(body)
        
        if not current_facts:
            continue
        
        if rewrite_summary(file_path, entity_name, entity_type, current_facts, dry_run):
            updated_count += 1
    
    print()
    print(f"Synthesis complete: {updated_count} entities updated")
    
    if dry_run:
        print("\nThis was a dry run. No files were modified.")
        print("Run without --dry-run to apply changes.")


def main():
    parser = argparse.ArgumentParser(description="Weekly synthesis for the memory system")
    parser.add_argument("--dry-run", "-d", action="store_true", 
                        help="Show what would be changed without making changes")
    parser.add_argument("--force", "-f", action="store_true", 
                        help="Include example entities")
    
    args = parser.parse_args()
    
    print("Three-Layer Memory System — Weekly Synthesis (Optional)")
    print("=" * 50)
    print()
    print("Note: Manual synthesis is the default.")
    print("When reading an entity file, if the summary feels stale:")
    print("  1. Read the current facts")
    print("  2. Rewrite the summary section")
    print("  3. Mark superseded facts with [was]")
    print()
    
    run_synthesis(dry_run=args.dry_run, force=args.force)


if __name__ == "__main__":
    main()
