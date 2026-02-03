# Three-Layer Memory System — Folder Structure

## Overview

```
~/
├── life/
│   ├── entities/                # Knowledge graph (Layer 1)
│   │   ├── maria.person.md
│   │   ├── acme-corp.company.md
│   │   ├── ai-platform.project.md
│   │   └── example-person.person.md  # Template/example (can delete)
│   └── days/                    # Daily notes (Layer 2)
│       ├── 2026-01-27.md
│       ├── 2026-01-28.md
│       └── 2026-01-29.md
└── MEMORY.md                    # Tacit knowledge (Layer 3)
```

## Layer 1: Knowledge Graph (`~/life/entities/`)

### Entity File Naming

Format: `{name}.{type}.md`

Entity types are **flexible and extensible** — use any type that makes sense for your context:

| Type | Example | Use Case |
|------|---------|----------|
| person | `maria.person.md` | People you know |
| company | `acme-corp.company.md` | Organizations |
| project | `ai-platform.project.md` | Active projects |
| idea | `mobile-app.idea.md` | Ideas to explore |
| book | `design-patterns.book.md` | Books read/reading |
| product | `launchpad.product.md` | Products you use/build |
| *any* | `vacation-japan.plan.md` | Create your own types |

### Naming Conventions

- Use lowercase
- Replace spaces with hyphens
- Keep it concise but readable
- Examples: `james-smith`, `acme-corp`, `ai-platform`

### Entity File Format

Single markdown file with optional YAML frontmatter:

```markdown
---
type: person
created_at: 2026-01-15
---

# Maria

> Business partner on AI project (since Jan 2026)

## Key Facts

- [current] Business partner on AI project — Jan 2026
- [current] Company hired 2 developers — Jan 2026
- [was] Former colleague at OldCo — 2025 to Jan 2026

## Context

Met through previous role at OldCo. Company is growing fast.
```

### Fact Status Prefixes

| Prefix | Meaning |
|--------|---------|
| `[current]` | Active, current fact |
| `[was]` | Historical, superseded fact |

## Layer 2: Daily Notes (`~/life/days/`)

### File Naming

Format: `YYYY-MM-DD.md`

Examples:
- `2026-01-27.md`
- `2026-01-28.md`

### Content Structure

Simple bullet list format:

```markdown
# 2026-01-27

- 10:30am: Shopping trip
- 2:00pm: Doctor follow-up — follow-up in 3 months
- Decided: Calendar events now use emoji categories
```

No structured sections required — just capture events as they happen.

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

## Integration with AGENTS.md

Add this section to your repo's AGENTS.md:

```markdown
## Memory — Three Layers

### Layer 1: Knowledge Graph (`~/life/entities/`)
Single-file entities with YAML frontmatter:
- `maria.person.md` — Person entities
- `acme-corp.company.md` — Company entities  
- `ai-platform.project.md` — Project entities

Format: human-readable markdown with optional YAML frontmatter.

Rules:
- Save facts immediately during conversations
- Mark outdated facts with `[was]` prefix
- Clean up summaries when they feel stale

### Layer 2: Daily Notes (`~/life/days/YYYY-MM-DD.md`)
- Raw timeline of events
- Written during or after conversations
- Simple bullet list format

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
tar -czf memory-backup-$(date +%Y%m%d).tar.gz ~/life ~/MEMORY.md
```

## Philosophy

This simplified structure follows the principle:

> **Manual until it hurts.** Start simple, add automation only when needed.

- Single-file entities eliminate sync issues
- Flat structure reduces cognitive overhead
- Human-readable first — if you can't `cat` it, it's too complex
