# Three-Layer Memory System — Folder Structure

## Overview

```
~/
├── life/
│   └── areas/
│       ├── people/              # Person entities
│       │   ├── maria/
│       │   │   ├── summary.md   # Living summary (rewritten weekly)
│       │   │   └── items.json   # Atomic facts
│       │   ├── james-smith/
│       │   │   ├── summary.md
│       │   │   └── items.json
│       │   └── example-person/  # Template/example (can delete)
│       │       ├── summary.md
│       │       └── items.json
│       ├── companies/           # Company entities
│       │   ├── acme-corp/
│       │   │   ├── summary.md
│       │   │   └── items.json
│       │   └── newco/
│       │       ├── summary.md
│       │       └── items.json
│       └── projects/            # Project entities
│           ├── ai-platform/
│           │   ├── summary.md
│           │   └── items.json
│           └── website-redesign/
│               ├── summary.md
│               └── items.json
├── memory/                      # Daily notes (Layer 2)
│   ├── 2026-01-27.md
│   ├── 2026-01-28.md
│   └── 2026-01-29.md
├── MEMORY.md                    # Tacit knowledge (Layer 3)
└── .memory_system               # System configuration (hidden)
```

## Layer 1: Knowledge Graph (`~/life/areas/`)

### Entity Types

| Type | Path | Example |
|------|------|---------|
| People | `~/life/areas/people/` | `~/life/areas/people/maria/` |
| Companies | `~/life/areas/companies/` | `~/life/areas/companies/acme-corp/` |
| Projects | `~/life/areas/projects/` | `~/life/areas/projects/ai-platform/` |

### Entity Folder Naming

- Use lowercase
- Replace spaces with hyphens
- Keep it concise but readable
- Examples: `james-smith`, `acme-corp`, `ai-platform`, `website-redesign`

### Entity Files

#### `items.json`
- Contains all atomic facts about the entity
- Machine-readable format
- Append-only (never delete, only supersede)
- Schema: See `atomic_fact_schema.json`

#### `summary.md`
- Living summary rewritten weekly
- Human-readable overview
- Loaded first for quick context
- Should be concise (ideally < 500 words)

## Layer 2: Daily Notes (`~/memory/`)

### File Naming

Format: `YYYY-MM-DD.md`

Examples:
- `2026-01-27.md`
- `2026-01-28.md`

### Content Structure

```markdown
# 2026-01-27

## Events
- 10:30am: Shopping trip
- 2:00pm: Doctor follow-up

## Decisions
- Calendar events now use emoji categories

## Facts to Extract
- [ ] Follow-up appointment in 3 months
- [ ] New medication prescribed

## Notes
Additional context here...
```

### Sections

| Section | Purpose |
|---------|---------|
| Events | What happened, when |
| Decisions | Choices made with reasoning |
| Facts to Extract | Durable facts flagged for Layer 1 |
| Notes | Additional context |

## Layer 3: Tacit Knowledge (`~/MEMORY.md`)

### Content Structure

```markdown
# My Memory

## How I Work
- Sprint worker — intense bursts, then rest
- Contact preference: Call > SMS > Email

## Lessons Learned
- Don't create cron jobs for one-off reminders

## Preferences
- Code style: DHH Rails style
- Communication: Async first

## Important People
- Quick reference to key people

## Active Projects
- Current priorities
```

### Characteristics

- **Static** — Updated manually as needed
- **Pattern-based** — How the user operates
- **Long-term** — Rarely changes
- **Behavioral** — Preferences and lessons

## System Configuration (`.memory_system`)

Hidden file storing system state:

```json
{
  "version": "1.0.0",
  "created": "2026-01-15T10:30:00",
  "lastExtractedTimestamp": "2026-01-27T14:00:00",
  "lastSynthesisTimestamp": "2026-01-26T09:00:00",
  "entities": {
    "people": ["maria", "james-smith"],
    "companies": ["acme-corp", "newco"],
    "projects": ["ai-platform"]
  }
}
```

## Integration with AGENTS.md

Add this section to your repo's AGENTS.md:

```markdown
## Memory — Three Layers

### Layer 1: Knowledge Graph (`~/life/areas/`)
- `people/` — Person entities
- `companies/` — Company entities  
- `projects/` — Project entities

Tiered retrieval:
1. summary.md — quick context (load first)
2. items.json — atomic facts (load when detail needed)

Rules:
- Save facts immediately to items.json
- Weekly: rewrite summary.md from active facts
- Never delete — supersede instead

### Layer 2: Daily Notes (`~/memory/YYYY-MM-DD.md`)
- Raw timeline of events
- Written continuously during conversations
- Durable facts extracted to Layer 1

### Layer 3: Tacit Knowledge (`~/MEMORY.md`)
- Patterns, preferences, lessons learned
- Long-term behavioral knowledge
```

## Backup and Portability

The entire system is:
- **Text-based** — All files are human-readable
- **Git-friendly** — Can be version controlled
- **Portable** — Easy to backup or migrate
- **Searchable** — Standard text search works

Recommended backup:
```bash
# Backup the entire memory system
tar -czf memory-backup-$(date +%Y%m%d).tar.gz ~/life ~/memory ~/MEMORY.md ~/.memory_system
```
