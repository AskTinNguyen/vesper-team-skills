---
name: 3-layer-memory
description: This skill should be used when setting up or managing a compounding three-layer memory system for AI assistants. It applies when users want to create a self-maintaining knowledge graph with automatic fact extraction, entity-based storage, and weekly synthesis. Triggers on "set up memory system", "knowledge graph", "automatic memory", "compounding memory", or requests to manage persistent context across conversations.
license: Complete terms in LICENSE.txt
---

# 3-Layer Memory System

Transform static memory into a self-maintaining, compounding knowledge graph that evolves automatically as life changes.

## What This System Provides

- **Automatic fact extraction** — Cheap sub-agents scan conversations every ~30 minutes and save durable facts
- **Entity-based storage** — Facts organized by person, company, project — not dumped into a single blob
- **Weekly synthesis** — Sunday cron rewrites summaries from raw facts and prunes stale context automatically
- **Superseding, not deleting** — When facts change, old ones are marked historical; full history preserved

**Result**: Understanding updates itself. Context stays current without manual edits.

## The Three-Layer Architecture

```
Layer 1: Knowledge Graph   (/life/areas/)
   └── Entities with atomic facts + living summaries

Layer 2: Daily Notes       (memory/YYYY-MM-DD.md)
   └── Raw event logs — what happened, when

Layer 3: Tacit Knowledge   (MEMORY.md)
   └── Patterns, preferences, lessons learned
```

Every conversation adds signal. Every week, that signal is distilled.

## When to Use This Skill

Use this skill when:
- Setting up the three-layer memory system for the first time
- Creating new entities (people, companies, projects) in the knowledge graph
- Running fact extraction from recent conversations
- Performing weekly synthesis and summary updates
- Querying the knowledge graph for context
- Migrating or maintaining the memory system

## Quick Start

### 1. Initialize the System

Run the initialization script to create the folder structure:

```bash
python3 ~/.claude/skills/3-layer-memory/scripts/init_memory_system.py
```

This creates:
```
~/life/areas/
├── people/
├── companies/
└── projects/
~/memory/
~/MEMORY.md (if not exists)
```

### 2. Add to AGENTS.md

Include this section in the repo's AGENTS.md:

```markdown
## Memory — Three Layers

### Layer 1: Knowledge Graph (`/life/areas/`)
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

### Layer 2: Daily Notes (`memory/YYYY-MM-DD.md`)
- Raw timeline of events
- Written continuously during conversations
- Durable facts extracted to Layer 1

### Layer 3: Tacit Knowledge (`MEMORY.md`)
- Patterns, preferences, lessons learned
- Long-term behavioral knowledge
```

### 3. Configure Heartbeat for Fact Extraction

Add to HEARTBEAT.md or cron configuration:

```markdown
## Fact Extraction

On each heartbeat:
1. Check for new conversations since lastExtractedTimestamp
2. Spawn cheap sub-agent to extract durable facts
3. Write to relevant entity items.json
4. Update lastExtractedTimestamp

Focus: relationships, status changes, milestones
Skip: casual chat, temporary info
```

### 4. Configure Weekly Synthesis

Add Sunday cron job:

```markdown
## Weekly Memory Review (Sunday)

For each entity with new facts:
1. Load summary.md
2. Load active items.json
3. Rewrite summary.md for current state
4. Mark contradicted facts as superseded
```

Or run manually:
```bash
python3 ~/.claude/skills/3-layer-memory/scripts/weekly_synthesis.py
```

## Layer 1: Knowledge Graph

### Entity Structure

Each entity lives in its own folder:

```
/life/areas/people/maria/
├── summary.md      # Living summary (rewritten weekly)
└── items.json      # Atomic facts

/life/areas/companies/acme-corp/
├── summary.md
└── items.json
```

### Atomic Facts (items.json)

```json
{
  "entity": "maria",
  "type": "person",
  "created": "2026-01-15",
  "facts": [
    {
      "id": "maria-001",
      "fact": "Business partner on AI project",
      "category": "relationship",
      "timestamp": "2026-01-15",
      "source": "conversation",
      "status": "active"
    },
    {
      "id": "maria-002", 
      "fact": "Company hired two developers",
      "category": "milestone",
      "timestamp": "2026-01-20",
      "source": "conversation",
      "status": "active"
    },
    {
      "id": "maria-003",
      "fact": "Former colleague at OldCo",
      "category": "relationship",
      "timestamp": "2025-06-01",
      "status": "superseded",
      "supersededBy": "maria-001",
      "supersededDate": "2026-01-15"
    }
  ]
}
```

### Living Summary (summary.md)

```markdown
# Maria

Business partner on AI project (since Jan 2026).

## Current Context
- Company growing: hired 2 developers recently
- Met through previous role at OldCo

## Relationship Timeline
- 2025: Colleague at OldCo
- 2026: Became business partner on AI project
```

### Creating New Entities

Use the entity management script:

```bash
python3 ~/.claude/skills/3-layer-memory/scripts/manage_entity.py create --type person --name "james-smith"
```

Or manually create the folder and files using templates from `assets/templates/`.

## Layer 2: Daily Notes

Daily notes capture the raw timeline. Create them during or after conversations:

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
```

Durable facts are later extracted into Layer 1 entities.

## Layer 3: Tacit Knowledge

MEMORY.md captures how the user operates:

```markdown
# My Memory

## How I Work
- Sprint worker — intense bursts, then rest
- Contact preference: Call > SMS > Email
- Early riser, prefers brief messages

## Lessons Learned
- Don't create cron jobs for one-off reminders
- Weekly reviews are more effective than daily

## Preferences
- Code style: DHH Rails style
- Communication: Async first, urgent = call
```

## Fact Extraction Process

### Automated (via Heartbeat)

The extraction script runs on each heartbeat:

```bash
python3 ~/.claude/skills/3-layer-memory/scripts/extract_facts.py --since <timestamp>
```

Process:
1. Load conversation history since last extraction
2. Spawn cheap sub-agent (e.g., Haiku, ~$0.001) to identify durable facts
3. Map facts to existing entities or flag for new entity creation
4. Append to relevant items.json
5. Update lastExtractedTimestamp

### Manual

Extract facts from a specific conversation:

```bash
python3 ~/.claude/skills/3-layer-memory/scripts/extract_facts.py --file conversation.md
```

## Weekly Synthesis Process

The synthesis script runs every Sunday (or on demand):

```bash
python3 ~/.claude/skills/3-layer-memory/scripts/weekly_synthesis.py
```

Process:
1. Find all entities with new facts since last synthesis
2. For each entity:
   - Load current summary.md
   - Load all active facts from items.json
   - Identify contradictions (facts that override previous ones)
   - Mark superseded facts
   - Rewrite summary.md with current state
3. Log synthesis completion

## Schema Reference

See `references/atomic_fact_schema.json` for complete JSON schema.

See `references/folder_structure.md` for full directory layout.

## Templates

Use templates in `assets/templates/` for creating new entities:

- `entity_summary.md` — Template for summary.md
- `daily_notes.md` — Template for daily notes
- `memory_tacit.md` — Template for MEMORY.md

## Best Practices

1. **Always supersede, never delete** — Preserves history and allows tracing how understanding evolved

2. **Load tiered context** — Always start with summary.md; load items.json only when detail needed

3. **Write daily notes continuously** — Capture events while fresh; extract facts later

4. **Run extraction frequently** — Small, frequent extractions are more accurate than large batches

5. **Review weekly synthesis output** — Ensure summaries accurately reflect current state

6. **Keep MEMORY.md focused** — Patterns and preferences only; specific facts belong in knowledge graph

## Migration from Static Memory

If migrating from a static MEMORY.md:

1. Run initialization script
2. Read existing MEMORY.md
3. Extract entity-specific facts into Layer 1 entities
4. Keep patterns/preferences in MEMORY.md (Layer 3)
5. Set up heartbeat and cron jobs

## Troubleshooting

**Issue: Facts not being extracted**
- Check lastExtractedTimestamp is being updated
- Verify extraction script has access to conversation history
- Review extraction logs

**Issue: Summaries going stale**
- Ensure weekly synthesis is running
- Check that superseded facts are properly marked
- Verify summary.md is being rewritten

**Issue: Context window overflow**
- Load only summary.md initially
- Load items.json only when specific facts needed
- Archive old entities if no longer relevant
