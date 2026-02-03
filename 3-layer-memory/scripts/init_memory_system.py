#!/usr/bin/env python3
"""
Initialize the three-layer memory system.
Creates folder structure and initial files.
"""

import os
import json
from pathlib import Path
from datetime import datetime


def get_home_dir():
    """Get the user's home directory."""
    return Path.home()


def create_directory_structure():
    """Create the three-layer memory directory structure."""
    home = get_home_dir()
    
    # Layer 1: Knowledge Graph
    knowledge_base_dirs = [
        home / "life" / "areas" / "people",
        home / "life" / "areas" / "companies",
        home / "life" / "areas" / "projects",
    ]
    
    # Layer 2: Daily Notes
    daily_notes_dir = home / "memory"
    
    # Create all directories
    for dir_path in knowledge_base_dirs + [daily_notes_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {dir_path}")
    
    return home


def create_memory_md(home: Path):
    """Create or update MEMORY.md (Layer 3: Tacit Knowledge)."""
    memory_path = home / "MEMORY.md"
    
    if memory_path.exists():
        print(f"⚠ MEMORY.md already exists at {memory_path}")
        return
    
    content = """# My Memory

## How I Work
<!-- Add your work patterns, preferences, and style -->
- 

## Lessons Learned
<!-- Capture insights and lessons from experience -->
- 

## Preferences
<!-- Communication, coding, organization preferences -->
- 

## Important People
<!-- Quick reference to key people in your life -->
- 

## Active Projects
<!-- Current projects and priorities -->
- 

---
*This file is part of the Three-Layer Memory System.*
*Layer 3: Tacit Knowledge — patterns, preferences, lessons learned*
"""
    
    memory_path.write_text(content)
    print(f"✓ Created: {memory_path}")


def create_system_config(home: Path):
    """Create system configuration file."""
    config_path = home / ".memory_system"
    
    config = {
        "version": "1.0.0",
        "created": datetime.now().isoformat(),
        "lastExtractedTimestamp": None,
        "lastSynthesisTimestamp": None,
        "entities": {
            "people": [],
            "companies": [],
            "projects": []
        }
    }
    
    config_path.write_text(json.dumps(config, indent=2))
    print(f"✓ Created: {config_path}")


def create_example_entity(home: Path):
    """Create an example entity to demonstrate structure."""
    example_dir = home / "life" / "areas" / "people" / "example-person"
    example_dir.mkdir(parents=True, exist_ok=True)
    
    # Create items.json
    items = {
        "entity": "example-person",
        "type": "person",
        "created": datetime.now().strftime("%Y-%m-%d"),
        "facts": [
            {
                "id": "example-001",
                "fact": "Example fact - replace with real information",
                "category": "relationship",
                "timestamp": datetime.now().strftime("%Y-%m-%d"),
                "source": "example",
                "status": "active"
            }
        ]
    }
    
    items_path = example_dir / "items.json"
    items_path.write_text(json.dumps(items, indent=2))
    
    # Create summary.md
    summary = f"""# Example Person

Example person entity demonstrating the knowledge graph structure.

## Current Context
- Replace this with actual context about the person
- Add relevant details from their items.json

## Notes
This is a template entity. You can safely delete this folder once you understand the structure.

---
*Entity created: {datetime.now().strftime("%Y-%m-%d")}*
"""
    
    summary_path = example_dir / "summary.md"
    summary_path.write_text(summary)
    
    print(f"✓ Created example entity: {example_dir}")
    print(f"  (You can delete this after reviewing the structure)")


def create_today_note(home: Path):
    """Create today's daily note as an example."""
    today = datetime.now().strftime("%Y-%m-%d")
    note_path = home / "memory" / f"{today}.md"
    
    if note_path.exists():
        return
    
    content = f"""# {today}

## Events
<!-- Log events throughout the day -->
- 

## Decisions
<!-- Record decisions made -->
- 

## Facts to Extract
<!-- Flag facts that should go into the knowledge graph -->
- [ ] 

## Notes
<!-- Additional context -->
- 
"""
    
    note_path.write_text(content)
    print(f"✓ Created: {note_path}")


def main():
    """Main initialization function."""
    print("=" * 60)
    print("Three-Layer Memory System Initialization")
    print("=" * 60)
    print()
    
    home = create_directory_structure()
    create_memory_md(home)
    create_system_config(home)
    create_example_entity(home)
    create_today_note(home)
    
    print()
    print("=" * 60)
    print("Initialization Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Review the example entity in ~/life/areas/people/example-person/")
    print("2. Add to your AGENTS.md file (see skill documentation)")
    print("3. Configure heartbeat for fact extraction")
    print("4. Set up weekly synthesis cron job")
    print()
    print("Directory structure created:")
    print("  ~/life/areas/people/      - People entities")
    print("  ~/life/areas/companies/   - Company entities")
    print("  ~/life/areas/projects/    - Project entities")
    print("  ~/memory/                 - Daily notes")
    print("  ~/MEMORY.md               - Tacit knowledge")


if __name__ == "__main__":
    main()
