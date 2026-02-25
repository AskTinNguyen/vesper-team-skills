---
name: jeff-index
description: Jeff commands overview and quick reference
---

# Jeff Commands — Overview

Slash commands implementing Jeffrey Emanuel's Agent Flywheel methodology.

## Quick Reference

| Command | Purpose |
|---------|---------|
| `/jeff-plan <feature>` | Generate comprehensive technical plan |
| `/jeff-beads <plan-path>` | Convert plan to atomic tasks (beads) |
| `/jeff-triage` | Analyze task graph, show priorities |
| `/jeff-next` | Get single top task with full context |
| `/jeff-decompose <task>` | Break big task into atomic subtasks |
| `/jeff-execute [task-id]` | Spawn Coder to execute beads |
| `/jeff-review` | Review progress against plan |

## Typical Workflow

```
1. /jeff-plan "Build plugin system for Vesper"
   ↓ Creates: plans/PLAN_plugin_system.md

2. /jeff-beads plans/PLAN_plugin_system.md
   ↓ Creates: .beads/beads.jsonl (50+ tasks)

3. /jeff-triage
   ↓ Shows: Top priorities, blockers, quick wins

4. /jeff-execute
   ↓ Spawns: Coder with top task

5. /jeff-review
   ↓ Shows: Progress, quality, recommendations
```

## Key Concepts

**Beads:** Atomic tasks (30min-2hr) with dependencies
**bv:** Graph analytics tool for task prioritization
**bd:** CLI for task status updates

## Reference Documentation

All commands can access:
- `~/.openclaw/workspace/agents/jeff-agent/AGENTS.md` — Full methodology
- `~/.openclaw/workspace/agents/jeff-agent/knowledge/WORKFLOW_DETAILS.md` — Process details
- `~/.openclaw/workspace/agents/jeff-agent/knowledge/TOOL_ECOSYSTEM.md` — All 22 tools
- `~/.openclaw/workspace/agents/jeff-agent/knowledge/TIPS_AND_BEST_PRACTICES.md` — Tips

## Tools Required

- `bv` (beads_viewer): `~/.local/bin/bv`
- `bd` (beads CLI): Available after bv install

Install: `brew install dicklesworthstone/tap/bv` or download from GitHub releases.
