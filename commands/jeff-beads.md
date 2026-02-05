---
name: jeff-beads
description: Convert plan to atomic tasks (beads) with dependencies
argument-hint: "<path-to-plan>"
---

# /jeff-beads — Generate Beads from Plan

Convert a technical plan into atomic tasks (beads) with dependencies.

## Usage
```
/jeff-beads <path-to-plan>
/jeff-beads plans/PLAN_auth_system.md
```

## What This Does

1. **Read** the plan document
2. **Decompose** into atomic tasks (30min-2hr each)
3. **Map dependencies** between tasks
4. **Import** into beads database

## Process

### Step 1: Initialize Beads (if needed)
```bash
cd <project-dir>
~/.local/bin/bd init  # Creates .beads/ structure
```

### Step 2: Read the Plan
```
Read: $ARGUMENTS (the plan file path)
```

### Step 3: Generate Beads

Use this prompt:
```
Here is a technical plan:

[PASTE PLAN CONTENT]

Convert this into atomic tasks ("beads") with this structure:

For each task provide (as JSON):
- id: Unique identifier (MODULE-XXX format, e.g., AUTH-001)
- type: "epic" | "task" | "bug" | "chore"  
- status: "open"
- priority: 0 (P0/critical), 1 (P1/high), 2 (P2/medium), 3 (P3/low)
- title: Clear, action-oriented title
- desc: What to do (2-3 sentences)
- deps: Array of task IDs this depends on (empty [] if none)
- labels: Array of categories (e.g., ["auth", "backend", "tests"])
- acceptance: Array of "done" criteria

Rules:
1. Each task: 30min-2hr of work
2. If bigger, split it
3. Include test tasks for each module
4. Include doc tasks
5. Be explicit about dependencies
6. **priority MUST be integer** (0, 1, 2, 3)

Output as JSONL (one JSON object per line, no markdown).
```

### Step 4: Import Beads

```bash
# Save generated JSONL to temp file, then import
cat /tmp/beads.jsonl | ~/.local/bin/bd import -i /dev/stdin --rename-on-import

# Sync to JSONL for bv
~/.local/bin/bd sync --flush-only
```

### Step 5: Verify with bv
```bash
~/.local/bin/bv --robot-triage | jq '.triage.quick_ref'
```

## Bead Format Example
```json
{"id":"AUTH-001","type":"task","status":"open","priority":0,"title":"Set up auth module structure","desc":"Create the auth/ directory with index.ts, types.ts, and placeholder files for login, logout, and session management.","deps":[],"labels":["auth","setup"],"acceptance":["Directory structure exists","Exports configured","TypeScript compiles"]}
{"id":"AUTH-002","type":"task","status":"open","priority":0,"title":"Implement JWT token generation","desc":"Create generateToken() function using HS256 algorithm with configurable expiration.","deps":["AUTH-001"],"labels":["auth","core"],"acceptance":["Function generates valid JWTs","Tokens include user_id, role, exp claims","Unit tests pass"]}
```

**IMPORTANT:** `priority` must be an integer (0-3), not a string!

## Decomposition Rules

✅ **Good bead:**
- "Implement JWT token generation"
- "Add unit tests for login endpoint"
- "Create user migration"

❌ **Bad bead (too big):**
- "Build authentication system" → Split into 10+ beads
- "Implement the API" → Split by endpoint

## Output

Announce when complete:
```
✅ Beads generated: .beads/beads.jsonl
- Total: [count] beads
- Ready (no deps): [count]
- By priority: [breakdown]

Next: Run `bv --robot-triage` or `/jeff-triage`
```

## Reference
- Full methodology: `~/.openclaw/workspace/agents/jeff-agent/AGENTS.md`
- Tips: `~/.openclaw/workspace/agents/jeff-agent/knowledge/TIPS_AND_BEST_PRACTICES.md`
