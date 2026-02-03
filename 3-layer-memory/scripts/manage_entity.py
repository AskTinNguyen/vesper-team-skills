#!/usr/bin/env python3
"""
Manage entities in the knowledge graph.
Create, list, delete, and inspect entities.
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


def sanitize_name(name: str) -> str:
    """Convert a display name to a safe folder name."""
    # Lowercase, replace spaces with hyphens, remove special chars
    safe = name.lower().strip()
    safe = safe.replace(" ", "-")
    safe = "".join(c for c in safe if c.isalnum() or c == "-")
    safe = safe.strip("-")
    return safe


def create_entity(entity_type: str, entity_name: str, display_name: Optional[str] = None) -> Path:
    """Create a new entity with all necessary files."""
    home = get_home_dir()
    
    # Sanitize name for folder
    folder_name = sanitize_name(entity_name)
    if not folder_name:
        print("Error: Invalid entity name")
        return None
    
    entity_dir = home / "life" / "areas" / entity_type / folder_name
    
    if entity_dir.exists():
        print(f"Entity already exists: {entity_type}/{folder_name}")
        return entity_dir
    
    entity_dir.mkdir(parents=True, exist_ok=True)
    
    # Use provided display name or derive from folder name
    name = display_name or folder_name.replace("-", " ").title()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Create items.json
    items = {
        "entity": folder_name,
        "display_name": name,
        "type": entity_type,
        "created": today,
        "facts": []
    }
    
    items_path = entity_dir / "items.json"
    items_path.write_text(json.dumps(items, indent=2))
    
    # Create summary.md
    summary = f"""# {name}

## Current Context
- Entity created on {today}

## Notes
<!-- Add notes and context here -->

---
*Created: {today}*
*Type: {entity_type}*
"""
    
    summary_path = entity_dir / "summary.md"
    summary_path.write_text(summary)
    
    print(f"✓ Created entity: {entity_type}/{folder_name}")
    print(f"  Location: {entity_dir}")
    
    return entity_dir


def list_entities(entity_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all entities or entities of a specific type."""
    home = get_home_dir()
    base_path = home / "life" / "areas"
    
    types_to_list = [entity_type] if entity_type else ["people", "companies", "projects"]
    entities = []
    
    for etype in types_to_list:
        type_path = base_path / etype
        if not type_path.exists():
            continue
        
        for entity_dir in type_path.iterdir():
            if not entity_dir.is_dir() or entity_dir.name.startswith("."):
                continue
            
            items_path = entity_dir / "items.json"
            if items_path.exists():
                data = json.loads(items_path.read_text())
                fact_count = len(data.get("facts", []))
                display_name = data.get("display_name", entity_dir.name)
                created = data.get("created", "unknown")
                
                entities.append({
                    "type": etype,
                    "name": entity_dir.name,
                    "display_name": display_name,
                    "path": entity_dir,
                    "fact_count": fact_count,
                    "created": created
                })
    
    return entities


def delete_entity(entity_type: str, entity_name: str, force: bool = False) -> bool:
    """Delete an entity and all its data."""
    home = get_home_dir()
    entity_dir = home / "life" / "areas" / entity_type / entity_name
    
    if not entity_dir.exists():
        print(f"Entity not found: {entity_type}/{entity_name}")
        return False
    
    # Load fact count for confirmation
    items_path = entity_dir / "items.json"
    fact_count = 0
    if items_path.exists():
        data = json.loads(items_path.read_text())
        fact_count = len(data.get("facts", []))
    
    if not force:
        print(f"Warning: This will delete {entity_type}/{entity_name}")
        print(f"  Facts: {fact_count}")
        print(f"  Location: {entity_dir}")
        print()
        print("Use --force to confirm deletion")
        return False
    
    # Delete the directory
    import shutil
    shutil.rmtree(entity_dir)
    
    print(f"✓ Deleted entity: {entity_type}/{entity_name}")
    return True


def show_entity(entity_type: str, entity_name: str):
    """Display detailed information about an entity."""
    home = get_home_dir()
    entity_dir = home / "life" / "areas" / entity_type / entity_name
    
    if not entity_dir.exists():
        print(f"Entity not found: {entity_type}/{entity_name}")
        return
    
    items_path = entity_dir / "items.json"
    summary_path = entity_dir / "summary.md"
    
    if not items_path.exists():
        print(f"Error: Entity data missing")
        return
    
    data = json.loads(items_path.read_text())
    
    print(f"\n{'='*50}")
    print(f"Entity: {data.get('display_name', entity_name)}")
    print(f"Type: {entity_type}")
    print(f"Folder: {entity_name}")
    print(f"Created: {data.get('created', 'unknown')}")
    print(f"Facts: {len(data.get('facts', []))}")
    print(f"{'='*50}")
    
    # Show active facts
    facts = data.get("facts", [])
    active_facts = [f for f in facts if f.get("status") == "active"]
    superseded_facts = [f for f in facts if f.get("status") == "superseded"]
    
    if active_facts:
        print("\nActive Facts:")
        for fact in active_facts:
            print(f"  [{fact.get('category', 'status')}] {fact['fact']}")
            print(f"    ID: {fact['id']} | {fact.get('timestamp', 'unknown')}")
    
    if superseded_facts:
        print(f"\nSuperseded Facts: {len(superseded_facts)}")
    
    # Show summary preview
    if summary_path.exists():
        summary = summary_path.read_text()
        print(f"\nSummary Preview:")
        preview = summary[:300] + "..." if len(summary) > 300 else summary
        for line in preview.split("\n")[:10]:
            print(f"  {line}")


def search_entities(query: str) -> List[Dict[str, Any]]:
    """Search for entities matching query."""
    all_entities = list_entities()
    results = []
    
    query_lower = query.lower()
    
    for entity in all_entities:
        # Check name match
        if query_lower in entity["name"].lower():
            results.append(entity)
            continue
        
        # Check display name match
        if query_lower in entity["display_name"].lower():
            results.append(entity)
            continue
        
        # Check facts
        items_path = entity["path"] / "items.json"
        if items_path.exists():
            data = json.loads(items_path.read_text())
            for fact in data.get("facts", []):
                if query_lower in fact.get("fact", "").lower():
                    results.append(entity)
                    break
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Manage entities in the knowledge graph")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new entity")
    create_parser.add_argument("--type", "-t", required=True, choices=["people", "companies", "projects"], help="Entity type")
    create_parser.add_argument("--name", "-n", required=True, help="Entity name (will be sanitized for folder)")
    create_parser.add_argument("--display", "-d", help="Display name (if different from sanitized name)")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List entities")
    list_parser.add_argument("--type", "-t", choices=["people", "companies", "projects"], help="Filter by type")
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show entity details")
    show_parser.add_argument("--type", "-t", required=True, choices=["people", "companies", "projects"], help="Entity type")
    show_parser.add_argument("--name", "-n", required=True, help="Entity name")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete an entity")
    delete_parser.add_argument("--type", "-t", required=True, choices=["people", "companies", "projects"], help="Entity type")
    delete_parser.add_argument("--name", "-n", required=True, help="Entity name")
    delete_parser.add_argument("--force", "-f", action="store_true", help="Confirm deletion")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search entities")
    search_parser.add_argument("query", help="Search query")
    
    args = parser.parse_args()
    
    if args.command == "create":
        create_entity(args.type, args.name, args.display)
    
    elif args.command == "list":
        entities = list_entities(args.type)
        
        if not entities:
            print("No entities found.")
            return
        
        print(f"\n{'Type':<12} {'Name':<25} {'Facts':<8} {'Created'}")
        print("-" * 60)
        
        for e in sorted(entities, key=lambda x: (x["type"], x["name"])):
            print(f"{e['type']:<12} {e['name']:<25} {e['fact_count']:<8} {e['created']}")
    
    elif args.command == "show":
        show_entity(args.type, args.name)
    
    elif args.command == "delete":
        delete_entity(args.type, args.name, args.force)
    
    elif args.command == "search":
        results = search_entities(args.query)
        
        if not results:
            print(f"No entities found matching: {args.query}")
            return
        
        print(f"\nFound {len(results)} entities matching: {args.query}")
        print()
        
        for e in results:
            print(f"  {e['type']}/{e['name']} ({e['fact_count']} facts)")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
