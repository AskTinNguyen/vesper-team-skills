---
name: jeff-decompose
description: Break down a large task into atomic subtasks
argument-hint: "<task description or ID>"
---

# /jeff-decompose — Break Down a Task

Split a large task into atomic beads.

## Usage
```
/jeff-decompose <task description or ID>
/jeff-decompose "Build user authentication system"
/jeff-decompose AUTH-010
```

## What This Does

1. **Analyze** the task scope
2. **Identify** subtasks and dependencies
3. **Generate** atomic beads (30min-2hr each)
4. **Append** to existing beads file

## Process

### Step 1: Read Decomposition Rules
```
Read: ~/.openclaw/workspace/agents/jeff-agent/knowledge/TIPS_AND_BEST_PRACTICES.md
Focus on: "Bead Generation Tips"
```

### Step 2: Analyze the Task

If given a bead ID, fetch it:
```bash
grep "AUTH-010" .beads/beads.jsonl
```

If given a description, analyze scope.

### Step 3: Apply Decomposition Rules

**The Atomic Test:**
- Can say "and" in title? → Split it
- Takes > 2 hours? → Split it
- Has multiple acceptance criteria types? → Probably split it

**Split by:**
- Setup vs Implementation vs Testing vs Docs
- Data layer vs Logic layer vs API layer vs UI layer
- Happy path vs Error handling vs Edge cases

### Step 4: Generate Sub-Beads

Use this prompt:
```
Break down this task into atomic subtasks:

TASK: $ARGUMENTS

Rules:
1. Each subtask: 30min-2hr
2. Clear dependencies between subtasks
3. Each has specific acceptance criteria
4. Include test subtasks

Output as JSONL with:
- id: [PARENT]-[A/B/C] format (e.g., AUTH-010-A, AUTH-010-B)
- deps: Include parent dependencies + internal deps
- All other standard bead fields

The original task becomes an epic linking to these.
```

### Step 5: Update Beads File

```bash
# Backup
cp .beads/beads.jsonl .beads/beads.jsonl.bak

# Update original task to epic type
# Append new subtasks

# Verify
~/.local/bin/bv --robot-insights | jq '.Cycles'  # Check for circular deps
```

## Example

**Before:**
```json
{"id":"AUTH-010","title":"Build user authentication","desc":"Implement full auth flow","deps":[],"acceptance":["Users can register","Users can login","Sessions work"]}
```

**After:**
```json
{"id":"AUTH-010","type":"epic","title":"Build user authentication","desc":"Epic: Full auth flow","deps":[]}
{"id":"AUTH-010-A","type":"task","title":"Create user registration endpoint","deps":["AUTH-010"],"acceptance":["POST /register works","Validates email format","Hashes password"]}
{"id":"AUTH-010-B","type":"task","title":"Create login endpoint","deps":["AUTH-010-A"],"acceptance":["POST /login works","Returns JWT on success","Returns 401 on failure"]}
{"id":"AUTH-010-C","type":"task","title":"Implement session middleware","deps":["AUTH-010-B"],"acceptance":["Validates JWT","Attaches user to request","Handles expiration"]}
{"id":"AUTH-010-D","type":"task","title":"Add auth unit tests","deps":["AUTH-010-A","AUTH-010-B","AUTH-010-C"],"acceptance":["Registration tests pass","Login tests pass","Session tests pass"]}
```

## Output

```
✅ Decomposed AUTH-010 into 4 subtasks:
- AUTH-010-A: Create user registration endpoint
- AUTH-010-B: Create login endpoint  
- AUTH-010-C: Implement session middleware
- AUTH-010-D: Add auth unit tests

Dependency chain: A → B → C → D (tests)

Run `/jeff-triage` to see updated priorities.
```

## Reference
- Tips: `~/.openclaw/workspace/agents/jeff-agent/knowledge/TIPS_AND_BEST_PRACTICES.md`
- Workflow: `~/.openclaw/workspace/agents/jeff-agent/knowledge/WORKFLOW_DETAILS.md`
