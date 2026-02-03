#!/usr/bin/env python3
"""
Extract durable facts from conversations.
Can run automatically via heartbeat or manually on specific files.
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional


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


def find_existing_entities() -> Dict[str, List[str]]:
    """Find all existing entities in the knowledge graph."""
    home = get_home_dir()
    entities = {"people": [], "companies": [], "projects": []}
    
    base_path = home / "life" / "areas"
    for entity_type in entities.keys():
        type_path = base_path / entity_type
        if type_path.exists():
            entities[entity_type] = [
                d.name for d in type_path.iterdir() if d.is_dir()
            ]
    
    return entities


def generate_fact_id(entity_name: str, existing_facts: List[Dict]) -> str:
    """Generate a unique fact ID."""
    prefix = entity_name.lower().replace(" ", "-")[:20]
    existing_nums = []
    
    for fact in existing_facts:
        fact_id = fact.get("id", "")
        if fact_id.startswith(prefix):
            try:
                num = int(fact_id.split("-")[-1])
                existing_nums.append(num)
            except ValueError:
                pass
    
    next_num = max(existing_nums, default=0) + 1
    return f"{prefix}-{next_num:03d}"


def load_entity_facts(entity_type: str, entity_name: str) -> Dict[str, Any]:
    """Load facts for an entity."""
    home = get_home_dir()
    items_path = home / "life" / "areas" / entity_type / entity_name / "items.json"
    
    if items_path.exists():
        return json.loads(items_path.read_text())
    
    return {
        "entity": entity_name,
        "type": entity_type,
        "created": datetime.now().strftime("%Y-%m-%d"),
        "facts": []
    }


def save_entity_facts(entity_type: str, entity_name: str, data: Dict[str, Any]):
    """Save facts for an entity."""
    home = get_home_dir()
    entity_dir = home / "life" / "areas" / entity_type / entity_name
    entity_dir.mkdir(parents=True, exist_ok=True)
    
    items_path = entity_dir / "items.json"
    items_path.write_text(json.dumps(data, indent=2))


def create_entity(entity_type: str, entity_name: str) -> Path:
    """Create a new entity folder structure."""
    home = get_home_dir()
    entity_dir = home / "life" / "areas" / entity_type / entity_name
    entity_dir.mkdir(parents=True, exist_ok=True)
    
    # Create items.json
    items = {
        "entity": entity_name,
        "type": entity_type,
        "created": datetime.now().strftime("%Y-%m-%d"),
        "facts": []
    }
    
    items_path = entity_dir / "items.json"
    items_path.write_text(json.dumps(items, indent=2))
    
    # Create initial summary.md
    summary = f"""# {entity_name.replace("-", " ").title()}

## Current Context
<!-- Living summary - rewritten weekly -->
- 

## Relationship Timeline
<!-- Key dates and changes -->
- Created: {datetime.now().strftime("%Y-%m-%d")}
"""
    
    summary_path = entity_dir / "summary.md"
    summary_path.write_text(summary)
    
    return entity_dir


def extract_facts_manual(conversation_text: str, entities: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    """
    Manual fact extraction - in practice, this would use a sub-agent.
    Returns list of extracted facts with entity mapping.
    """
    # This is a placeholder - actual implementation would use a cheap LLM
    # to parse conversation and extract structured facts
    print("Note: This script is designed to spawn a sub-agent for fact extraction.")
    print("For automated extraction, configure via heartbeat (see SKILL.md).")
    print()
    print("Found entities in knowledge graph:")
    for entity_type, names in entities.items():
        if names:
            print(f"  {entity_type}: {', '.join(names)}")
    
    return []


def add_fact(entity_type: str, entity_name: str, fact_text: str, category: str = "status") -> bool:
    """Add a fact to an entity."""
    # Ensure entity exists
    home = get_home_dir()
    entity_dir = home / "life" / "areas" / entity_type / entity_name
    
    if not entity_dir.exists():
        print(f"Creating new entity: {entity_type}/{entity_name}")
        create_entity(entity_type, entity_name)
    
    # Load existing facts
    data = load_entity_facts(entity_type, entity_name)
    
    # Generate fact ID
    fact_id = generate_fact_id(entity_name, data["facts"])
    
    # Create fact
    fact = {
        "id": fact_id,
        "fact": fact_text,
        "category": category,
        "timestamp": datetime.now().strftime("%Y-%m-%d"),
        "source": "manual",
        "status": "active"
    }
    
    data["facts"].append(fact)
    save_entity_facts(entity_type, entity_name, data)
    
    print(f"✓ Added fact to {entity_type}/{entity_name}: {fact_id}")
    print(f"  {fact_text}")
    
    return True


def supersede_fact(entity_type: str, entity_name: str, old_fact_id: str, new_fact_text: str, category: str = "status"):
    """Mark an old fact as superseded and add a new one."""
    data = load_entity_facts(entity_type, entity_name)
    
    # Find and mark old fact
    old_fact = None
    for fact in data["facts"]:
        if fact["id"] == old_fact_id:
            old_fact = fact
            break
    
    if not old_fact:
        print(f"⚠ Fact not found: {old_fact_id}")
        return False
    
    # Generate new fact ID
    new_fact_id = generate_fact_id(entity_name, data["facts"])
    
    # Mark old fact as superseded
    old_fact["status"] = "superseded"
    old_fact["supersededBy"] = new_fact_id
    old_fact["supersededDate"] = datetime.now().strftime("%Y-%m-%d")
    
    # Add new fact
    new_fact = {
        "id": new_fact_id,
        "fact": new_fact_text,
        "category": category,
        "timestamp": datetime.now().strftime("%Y-%m-%d"),
        "source": "manual",
        "status": "active"
    }
    
    data["facts"].append(new_fact)
    save_entity_facts(entity_type, entity_name, data)
    
    print(f"✓ Superseded {old_fact_id} with {new_fact_id}")
    print(f"  Old: {old_fact['fact']}")
    print(f"  New: {new_fact_text}")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Extract and manage facts for the memory system")
    parser.add_argument("--file", "-f", help="Conversation file to extract facts from")
    parser.add_argument("--since", "-s", help="Extract facts since timestamp (ISO format)")
    parser.add_argument("--add", "-a", action="store_true", help="Add a fact manually")
    parser.add_argument("--entity-type", "-t", choices=["people", "companies", "projects"], help="Entity type")
    parser.add_argument("--entity-name", "-n", help="Entity name/slug")
    parser.add_argument("--fact", help="Fact text to add")
    parser.add_argument("--category", "-c", default="status", choices=["relationship", "milestone", "status", "preference"], help="Fact category")
    parser.add_argument("--supersede", help="ID of fact to supersede")
    
    args = parser.parse_args()
    
    # Load system state
    config = load_system_config()
    entities = find_existing_entities()
    
    if args.add:
        # Manual fact addition
        if not args.entity_type or not args.entity_name or not args.fact:
            print("Error: --add requires --entity-type, --entity-name, and --fact")
            return
        
        if args.supersede:
            supersede_fact(args.entity_type, args.entity_name, args.supersede, args.fact, args.category)
        else:
            add_fact(args.entity_type, args.entity_name, args.fact, args.category)
    
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
        print("Note: Automated extraction requires heartbeat integration")
    
    else:
        # List entities and recent activity
        print("Three-Layer Memory System — Fact Extraction")
        print("=" * 50)
        print()
        print("Usage:")
        print("  extract_facts.py --add -t people -n maria --fact 'Business partner'")
        print("  extract_facts.py --add -t people -n sarah --fact 'No longer works together' --supersede sarah-001")
        print()
        print("Existing entities:")
        for entity_type, names in entities.items():
            if names:
                print(f"\n  {entity_type}:")
                for name in names:
                    fact_count = len(load_entity_facts(entity_type, name)["facts"])
                    print(f"    - {name} ({fact_count} facts)")
        
        if config.get("lastExtractedTimestamp"):
            print(f"\nLast extraction: {config['lastExtractedTimestamp']}")


if __name__ == "__main__":
    main()
