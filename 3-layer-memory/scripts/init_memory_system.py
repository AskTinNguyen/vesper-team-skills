#!/usr/bin/env python3
"""
Initialize the three-layer memory system.
Creates folder structure and initial files.
"""

import os
from pathlib import Path
from datetime import datetime


def get_home_dir():
    """Get the user's home directory."""
    return Path.home()


def create_directory_structure():
    """Create the three-layer memory directory structure."""
    home = get_home_dir()
    
    # Layer 1: Knowledge Graph (flat structure)
    entities_dir = home / "life" / "entities"
    
    # Layer 2: Daily Notes
    days_dir = home / "life" / "days"
    
    # Create all directories
    for dir_path in [entities_dir, days_dir]:
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


def create_example_entity(home: Path):
    """Create an example entity to demonstrate structure."""
    example_path = home / "life" / "entities" / "example-person.person.md"
    
    if example_path.exists():
        return
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    content = f"""---
type: person
created_at: {today}
---

# Example Person

> Brief one-line description of who this person is

## Key Facts

- [current] Example fact — {today}
- [was] Previous status that changed — 2025 to {today}

## Context

Add context, notes, and relevant details here.
This is a template entity. You can safely delete this file once you understand the structure.

---
*Entity created: {today}*
"""
    
    example_path.write_text(content)
    print(f"✓ Created example entity: {example_path}")
    print(f"  (You can delete this after reviewing the structure)")


def create_today_note(home: Path):
    """Create today's daily note as an example."""
    today = datetime.now().strftime("%Y-%m-%d")
    note_path = home / "life" / "days" / f"{today}.md"
    
    if note_path.exists():
        return
    
    content = f"""# {today}

- Event or activity
- Another event — with details
- Decision made during the day
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
    create_example_entity(home)
    create_today_note(home)
    
    print()
    print("=" * 60)
    print("Initialization Complete!")
    print("=" * 60)
    print()
    print("Directory structure created:")
    print("  ~/life/entities/         - Knowledge graph entities")
    print("  ~/life/days/             - Daily notes")
    print("  ~/MEMORY.md              - Tacit knowledge")
    print()
    print("Next steps:")
    print("1. Review the example entity in ~/life/entities/example-person.person.md")
    print("2. Add to your AGENTS.md file (see skill documentation)")
    print("3. Start using — create entities and daily notes as needed")
    print()
    print("Optional: Configure automation if manual maintenance becomes painful")


if __name__ == "__main__":
    main()
