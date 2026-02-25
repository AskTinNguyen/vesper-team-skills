---
name: jeff-next
description: Get single highest-priority task with full context
---

# /jeff-next — Get Next Task

Get the single highest-priority task with full context.

## Usage
```
/jeff-next
```

## What This Does

1. **Query** `bv --robot-next` for top pick
2. **Fetch** full task details
3. **Provide** everything needed to execute
4. **Offer** to spawn Coder

## Process

### Step 1: Get Top Task
```bash
~/.local/bin/bv --robot-next
```

### Step 2: Format Output

```
🎯 NEXT TASK

**ID:** AUTH-001
**Title:** Set up auth module structure
**Priority:** high
**Labels:** auth, setup

**Description:**
Create the auth/ directory with index.ts, types.ts, and placeholder 
files for login, logout, and session management.

**Acceptance Criteria:**
☐ Directory structure exists
☐ Exports configured  
☐ TypeScript compiles

**Dependencies:** None (ready to start)

**This Unblocks:** AUTH-002, AUTH-003, AUTH-004 (3 tasks)

---

**Actions:**
1. Work on it yourself
2. Spawn Coder: `sessions_spawn(agentId="coder", task="Execute AUTH-001: [description]. Acceptance: [criteria]")`
3. Skip to next: `bd block AUTH-001 --reason "..."`
```

### Step 3: Offer Coder Spawn

If user confirms, generate spawn command:
```javascript
sessions_spawn({
  agentId: "coder",
  task: `Execute bead AUTH-001: Set up auth module structure.

Acceptance criteria:
- Directory structure exists
- Exports configured
- TypeScript compiles

When done:
1. git commit -am "AUTH-001: Set up auth module structure"
2. Run: bd done AUTH-001
3. Report to WhatsApp CodeSquad`
})
```

## No Tasks Ready?

If all tasks are blocked:
```
⚠️ No tasks ready — all blocked.

**Blockers to resolve:**
1. [TASK-X]: Waiting on [reason]
2. [TASK-Y]: Depends on [external]

Run `/jeff-triage` for full analysis.
```

## Reference
- bv commands: `~/.openclaw/workspace/agents/jeff-agent/knowledge/TOOL_ECOSYSTEM.md`
