#!/usr/bin/env python3
"""
Extract durable facts from conversations.
Optional automation — manual fact extraction is the default.
"""

import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional


def get_home_dir() -> Path:
    """Get the user's home directory."""
    return Path.home()


def find_existing_entities() -> Dict[str, List[str]]:
    """Find all existing entities in the knowledge graph."""
    home = get_home_dir()
    entities = {}
    
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
        
        if entity_type not in entities:
            entities[entity_type] = []
        entities[entity_type].append(entity_name)
    
    return entities


def load_entity_file(filename: str) -> str:
    """Load an entity file."""
    home = get_home_dir()
    entity_path = home / "life" / "entities" / filename
    
    if entity_path.exists():
        return entity_path.read_text()
    return ""


def save_entity_file(filename: str, content: str):
    """Save an entity file."""
    home = get_home_dir()
    entity_path = home / "life" / "entities" / filename
    entity_path.write_text(content)


def parse_entity_content(content: str) -> tuple:
    """Parse entity file into frontmatter and body."""
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


def add_fact_to_entity(filename: str, fact_text: str) -> bool:
    """Add a fact to an entity file."""
    content = load_entity_file(filename)
    today = datetime.now().strftime("%Y-%m-%d")
    
    if not content:
        # Create new entity file
        parts = filename.rsplit(".", 2)
        if len(parts) >= 2:
            entity_type = parts[-2]
            entity_name = parts[0].replace("-", " ").title()
        else:
            entity_type = "unknown"
            entity_name = filename
        
        content = f"""---
type: {entity_type}
created_at: {today}
---

# {entity_name}

## Key Facts

- [current] {fact_text} — {today}

## Context

"""
    else:
        # Add fact to existing file
        frontmatter, body = parse_entity_content(content)
        
        # Find the Key Facts section
        lines = body.split("\n")
        new_lines = []
        facts_added = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # Add fact after ## Key Facts heading
            if line.strip() == "## Key Facts" and not facts_added:
                new_lines.append(f"")
                new_lines.append(f"- [current] {fact_text} — {today}")
                facts_added = True
            # Or after any existing fact line
            elif line.strip().startswith("- [current]") and not facts_added:
                new_lines.append(f"- [current] {fact_text} — {today}")
                facts_added = True
        
        if not facts_added:
            # No Key Facts section found, add one
            new_lines.append(f"")
            new_lines.append(f"## Key Facts")
            new_lines.append(f"")
            new_lines.append(f"- [current] {fact_text} — {today}")
        
        body = "\n".join(new_lines)
        
        # Reconstruct file
        if frontmatter:
            import yaml
            fm_text = yaml.dump(frontmatter, default_flow_style=False).strip()
            content = f"---\n{fm_text}\n---\n{body}"
        else:
            content = body
    
    save_entity_file(filename, content)
    return True


def supersede_fact_in_entity(filename: str, old_fact_pattern: str, new_fact_text: str) -> bool:
    """Mark a fact as superseded and add a new one."""
    content = load_entity_file(filename)
    today = datetime.now().strftime("%Y-%m-%d")
    
    if not content:
        print(f"Entity not found: {filename}")
        return False
    
    # Find and replace the old fact
    lines = content.split("\n")
    new_lines = []
    superseded = False
    
    for line in lines:
        if old_fact_pattern.lower() in line.lower() and "[current]" in line:
            # Mark old fact as superseded
            new_lines.append(line.replace("[current]", "[was]"))
            superseded = True
        else:
            new_lines.append(line)
    
    if not superseded:
        print(f"⚠ Could not find matching current fact: {old_fact_pattern}")
        return False
    
    # Add new fact after the superseded one
    for i, line in enumerate(new_lines):
        if "[was]" in line and old_fact_pattern.lower() in line.lower():
            new_lines.insert(i + 1, f"- [current] {new_fact_text} — {today}")
            break
    
    content = "\n".join(new_lines)
    save_entity_file(filename, content)
    
    print(f"✓ Superseded fact and added new one in {filename}")
    return True


def extract_facts_manual(conversation_text: str, entities: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    """
    Manual fact extraction guidance.
    In practice, this would use a sub-agent for automated extraction.
    """
    print("Note: Manual fact extraction is the default.")
    print("For automated extraction, this script can spawn a sub-agent.")
    print()
    print("Found entities in knowledge graph:")
    for entity_type, names in entities.items():
        if names:
            print(f"  {entity_type}: {', '.join(names)}")
    
    return []


def main():
    parser = argparse.ArgumentParser(description="Extract and manage facts for the memory system")
    parser.add_argument("--file", "-f", help="Conversation file to extract facts from")
    parser.add_argument("--since", "-s", help="Extract facts since timestamp (ISO format)")
    parser.add_argument("--add", "-a", action="store_true", help="Add a fact manually")
    parser.add_argument("--entity", "-e", help="Entity filename (e.g., maria.person.md)")
    parser.add_argument("--fact", help="Fact text to add")
    parser.add_argument("--supersede", help="Pattern of fact to supersede")
    
    args = parser.parse_args()
    
    entities = find_existing_entities()
    
    if args.add:
        # Manual fact addition
        if not args.entity or not args.fact:
            print("Error: --add requires --entity and --fact")
            print("  Example: extract_facts.py --add -e maria.person.md --fact 'Business partner'")
            return
        
        if args.supersede:
            supersede_fact_in_entity(args.entity, args.supersede, args.fact)
        else:
            add_fact_to_entity(args.entity, args.fact)
            print(f"✓ Added fact to {args.entity}")
    
    elif args.file:
        # Extract from file
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File not found: {args.file}")
            return
        
        conversation = file_path.read_text()
        extract_facts_manual(conversation, entities)
    
    elif args.since:
        # Extract since timestamp (would integrate with conversation history)
        print(f"Would extract facts since: {args.since}")
        print("Note: Automated extraction requires additional configuration")
    
    else:
        # List entities and show usage
        print("Three-Layer Memory System — Fact Extraction (Optional)")
        print("=" * 50)
        print()
        print("Usage:")
        print("  Manual (recommended):")
        print("    Edit entity files directly during conversations")
        print()
        print("  Using this script:")
        print("    extract_facts.py --add -e maria.person.md --fact 'Business partner'")
        print("    extract_facts.py --add -e maria.person.md --fact 'New status' --supersede 'Old status'")
        print()
        
        if entities:
            print("Existing entities:")
            for entity_type, names in entities.items():
                if names:
                    print(f"\n  {entity_type}:")
                    for name in names:
                        print(f"    - {name}.{entity_type}.md")


if __name__ == "__main__":
    main()
