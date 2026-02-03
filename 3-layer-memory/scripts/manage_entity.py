#!/usr/bin/env python3
"""
Manage entities in the knowledge graph.
Create, list, delete, and inspect entities.
"""

import os
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional


def get_home_dir() -> Path:
    """Get the user's home directory."""
    return Path.home()


def sanitize_name(name: str) -> str:
    """Convert a display name to a safe filename."""
    # Lowercase, replace spaces with hyphens, remove special chars
    safe = name.lower().strip()
    safe = safe.replace(" ", "-")
    safe = "".join(c for c in safe if c.isalnum() or c == "-")
    safe = safe.strip("-")
    return safe


def parse_entity_file(file_path: Path) -> Dict[str, Any]:
    """Parse an entity markdown file and extract metadata."""
    content = file_path.read_text()
    
    # Parse YAML frontmatter if present
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
    
    # Extract title from first heading
    title_match = re.search(r"^# (.+)$", body, re.MULTILINE)
    title = title_match.group(1) if title_match else file_path.stem
    
    # Count facts
    current_facts = len(re.findall(r"^\s*-\s*\[current\]", body, re.MULTILINE))
    was_facts = len(re.findall(r"^\s*-\s*\[was\]", body, re.MULTILINE))
    
    return {
        "path": file_path,
        "filename": file_path.name,
        "title": title,
        "type": frontmatter.get("type", "unknown"),
        "created_at": frontmatter.get("created_at", "unknown"),
        "current_facts": current_facts,
        "was_facts": was_facts,
    }


def create_entity(entity_type: str, entity_name: str, display_name: Optional[str] = None) -> Path:
    """Create a new entity with all necessary files."""
    home = get_home_dir()
    
    # Sanitize name for filename
    base_name = sanitize_name(entity_name)
    if not base_name:
        print("Error: Invalid entity name")
        return None
    
    # Create filename with type suffix
    filename = f"{base_name}.{entity_type}.md"
    entity_path = home / "life" / "entities" / filename
    
    if entity_path.exists():
        print(f"Entity already exists: {filename}")
        return entity_path
    
    # Use provided display name or derive from sanitized name
    name = display_name or base_name.replace("-", " ").title()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Create entity file
    content = f"""---
type: {entity_type}
created_at: {today}
---

# {name}

> Brief description of this {entity_type}

## Key Facts

- [current] Add your first fact here — {today}

## Context

<!-- Add context, notes, and relevant details here -->

---
*Created: {today}*
*Type: {entity_type}*
"""
    
    entity_path.write_text(content)
    
    print(f"✓ Created entity: {filename}")
    print(f"  Location: {entity_path}")
    
    return entity_path


def list_entities(entity_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all entities or entities of a specific type."""
    home = get_home_dir()
    entities_dir = home / "life" / "entities"
    
    if not entities_dir.exists():
        return []
    
    entities = []
    
    for file_path in entities_dir.iterdir():
        if not file_path.is_file() or not file_path.suffix == ".md":
            continue
        
        # Parse filename: name.type.md
        parts = file_path.stem.split(".")
        if len(parts) < 2:
            continue
        
        file_type = parts[-1]
        
        if entity_type and file_type != entity_type:
            continue
        
        entity_data = parse_entity_file(file_path)
        entity_data["file_type"] = file_type
        entities.append(entity_data)
    
    return entities


def delete_entity(filename: str, force: bool = False) -> bool:
    """Delete an entity."""
    home = get_home_dir()
    entity_path = home / "life" / "entities" / filename
    
    if not entity_path.exists():
        print(f"Entity not found: {filename}")
        return False
    
    if not force:
        entity_data = parse_entity_file(entity_path)
        print(f"Warning: This will delete {filename}")
        print(f"  Title: {entity_data['title']}")
        print(f"  Facts: {entity_data['current_facts']} current, {entity_data['was_facts']} historical")
        print(f"  Location: {entity_path}")
        print()
        print("Use --force to confirm deletion")
        return False
    
    entity_path.unlink()
    
    print(f"✓ Deleted entity: {filename}")
    return True


def show_entity(filename: str):
    """Display detailed information about an entity."""
    home = get_home_dir()
    entity_path = home / "life" / "entities" / filename
    
    if not entity_path.exists():
        print(f"Entity not found: {filename}")
        return
    
    entity_data = parse_entity_file(entity_path)
    
    print(f"\n{'='*50}")
    print(f"Entity: {entity_data['title']}")
    print(f"File: {filename}")
    print(f"Type: {entity_data['type']}")
    print(f"Created: {entity_data['created_at']}")
    print(f"Facts: {entity_data['current_facts']} current, {entity_data['was_facts']} historical")
    print(f"{'='*50}")
    
    # Show file preview
    content = entity_path.read_text()
    preview_lines = content.split("\n")[:15]
    print("\nPreview:")
    for line in preview_lines:
        print(f"  {line}")
    
    if len(content.split("\n")) > 15:
        print("  ...")


def search_entities(query: str) -> List[Dict[str, Any]]:
    """Search for entities matching query."""
    all_entities = list_entities()
    results = []
    
    query_lower = query.lower()
    
    for entity in all_entities:
        # Check filename match
        if query_lower in entity["filename"].lower():
            results.append(entity)
            continue
        
        # Check title match
        if query_lower in entity["title"].lower():
            results.append(entity)
            continue
        
        # Check file content
        content = entity["path"].read_text()
        if query_lower in content.lower():
            results.append(entity)
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Manage entities in the knowledge graph")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new entity")
    create_parser.add_argument("--type", "-t", required=True, 
                               choices=["person", "company", "project", "idea", "book", "product"], 
                               help="Entity type")
    create_parser.add_argument("--name", "-n", required=True, help="Entity name")
    create_parser.add_argument("--display", "-d", help="Display name (if different from sanitized name)")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List entities")
    list_parser.add_argument("--type", "-t", 
                             choices=["person", "company", "project", "idea", "book", "product"], 
                             help="Filter by type")
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show entity details")
    show_parser.add_argument("filename", help="Entity filename (e.g., maria.person.md)")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete an entity")
    delete_parser.add_argument("filename", help="Entity filename (e.g., maria.person.md)")
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
        
        print(f"\n{'Filename':<35} {'Type':<12} {'Facts':<10} {'Title'}")
        print("-" * 80)
        
        for e in sorted(entities, key=lambda x: x["filename"]):
            total_facts = e['current_facts'] + e['was_facts']
            title = e['title'][:30] + "..." if len(e['title']) > 30 else e['title']
            print(f"{e['filename']:<35} {e['type']:<12} {total_facts:<10} {title}")
    
    elif args.command == "show":
        show_entity(args.filename)
    
    elif args.command == "delete":
        delete_entity(args.filename, args.force)
    
    elif args.command == "search":
        results = search_entities(args.query)
        
        if not results:
            print(f"No entities found matching: {args.query}")
            return
        
        print(f"\nFound {len(results)} entities matching: {args.query}")
        print()
        
        for e in results:
            total_facts = e['current_facts'] + e['was_facts']
            print(f"  {e['filename']} ({total_facts} facts) - {e['title']}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
