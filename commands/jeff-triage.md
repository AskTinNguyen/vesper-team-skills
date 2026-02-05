---
name: jeff-triage
description: Analyze task graph and explain priorities
---

# /jeff-triage — Smart Task Prioritization

Analyze the task graph and explain what to work on next.

## Usage
```
/jeff-triage
/jeff-triage --label backend
/jeff-triage --verbose
```

## What This Does

1. **Run** `bv --robot-triage` on current beads
2. **Analyze** the graph metrics (PageRank, critical path, blockers)
3. **Explain** recommendations in plain English
4. **Suggest** next actions

## Process

### Step 1: Check for Beads
```bash
if [ ! -f .beads/beads.jsonl ]; then
  echo "No beads found. Run /jeff-plan then /jeff-beads first."
  exit 1
fi
```

### Step 2: Run Triage
```bash
~/.local/bin/bv --robot-triage
```

### Step 3: Parse & Explain

Extract and explain:

**Quick Stats:**
```
Open: X | Ready: Y | Blocked: Z | In Progress: W
```

**Top 3 Recommendations:**
For each top pick, explain:
- What it is
- Why it's prioritized (PageRank score, unblocks count)
- Dependencies status
- Estimated effort

**Blockers to Clear:**
Tasks that unblock the most downstream work.

**Quick Wins:**
Low-effort, high-impact items for momentum.

### Step 4: Actionable Output

```
📊 TRIAGE RESULTS

**Quick Stats:** 47 open | 12 ready | 35 blocked

**Top Pick:** AUTH-001 "Set up auth module structure"
- Why: Unblocks 8 downstream tasks
- Deps: None (ready to start)
- Effort: ~30 min

**Also Ready:**
2. DB-001 "Create database schema" (unblocks 6)
3. CONFIG-001 "Set up environment config" (unblocks 4)

**Blockers to Clear:**
- AUTH-003 is blocking 5 tasks — prioritize after AUTH-001

**Commands:**
- Start top task: `bd start AUTH-001`
- Mark done: `bd done AUTH-001`
- Spawn Coder: `sessions_spawn(agentId="coder", task="Execute AUTH-001...")`
```

## Graph Metrics Explained

| Metric | Meaning |
|--------|---------|
| **PageRank** | "Influence" — tasks many things depend on |
| **Unblocks** | Direct count of tasks this enables |
| **Critical Path** | Longest dependency chain to completion |
| **Betweenness** | Bottleneck score — lies on many paths |

## Filtering

```bash
# Filter by label
~/.local/bin/bv --robot-triage --label backend

# Only actionable (unblocked)
~/.local/bin/bv --recipe actionable --robot-triage
```

## Reference
- bv commands: `~/.openclaw/workspace/agents/jeff-agent/knowledge/TOOL_ECOSYSTEM.md`
- Full methodology: `~/.openclaw/workspace/agents/jeff-agent/AGENTS.md`
