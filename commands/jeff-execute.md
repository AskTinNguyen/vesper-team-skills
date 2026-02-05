---
name: jeff-execute
description: Spawn Coder to execute tasks from bead queue
argument-hint: "[task-id] [--parallel N]"
---

# /jeff-execute — Spawn Coder with Beads

Spawn Coder to execute tasks from the bead queue.

## Usage
```
/jeff-execute
/jeff-execute AUTH-001
/jeff-execute --parallel 3
```

## What This Does

1. **Check** bead queue for ready tasks
2. **Generate** Coder spawn command with full context
3. **Spawn** Coder with task details
4. **Track** execution

## Process

### Step 1: Get Ready Tasks
```bash
~/.local/bin/bv --robot-triage | jq '.triage.quick_ref.top_picks'
```

### Step 2: If Specific Task Given
```bash
grep "$ARGUMENTS" .beads/beads.jsonl
```

### Step 3: Build Coder Task Prompt

For single task:
```
Execute bead [ID]: [Title]

**Description:**
[desc from bead]

**Acceptance Criteria:**
[acceptance array, formatted as checklist]

**Context:**
- Workspace: [current directory]
- Beads file: .beads/beads.jsonl
- This unblocks: [list dependent tasks]

**When Complete:**
1. Ensure all acceptance criteria met
2. git add -A && git commit -m "[ID]: [title]"
3. git push
4. Run: bd done [ID]
5. Report to WhatsApp CodeSquad

**If Blocked:**
1. Run: bd block [ID] --reason "[what's blocking]"
2. Move to next ready task via: bv --robot-next
```

### Step 4: Spawn Coder

```javascript
sessions_spawn({
  agentId: "coder",
  task: "[generated prompt above]",
  runTimeoutSeconds: 1800  // 30 min per task
})
```

### Step 5: For Parallel Execution

If `--parallel N` specified:
```
Get top N tasks from different tracks:
~/.local/bin/bv --robot-plan | jq '.plan.tracks[:N]'

Spawn N Coder instances, each on separate track.
```

## Output

```
🚀 Spawning Coder for AUTH-001

Task: Set up auth module structure
Acceptance: 3 criteria
Timeout: 30 min

Session: agent:coder:subagent:xxx
Status: Running

---

Track progress:
- WhatsApp CodeSquad for updates
- `sessions_list` to check status
- Results announce back when complete
```

## Parallel Execution

```
/jeff-execute --parallel 3

🚀 Spawning 3 Coder instances on parallel tracks:

Track 1: AUTH-001 (auth setup)
Track 2: DB-001 (database schema)  
Track 3: CONFIG-001 (environment config)

These tasks have no dependency conflicts.
```

## After Execution

When Coder completes:
1. Bead marked done automatically (if Coder followed protocol)
2. Dependent tasks become unblocked
3. Run `/jeff-triage` to see new priorities

## Reference
- Coder protocol: `~/.openclaw/workspace-coder/AGENTS.md` (Working with Jeff section)
- Parallel tracks: `~/.openclaw/workspace/agents/jeff-agent/knowledge/TIPS_AND_BEST_PRACTICES.md`
