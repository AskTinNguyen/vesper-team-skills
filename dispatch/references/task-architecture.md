# Task System Architecture

This document explains how Claude Code's task system works and how to use it correctly for multi-agent coordination.

## How Task List IDs Work

Every Claude Code session has a **task list ID** that determines where tasks are stored:

```
~/.claude/tasks/<list-id>/
├── 1.json
├── 2.json
├── 3.json
└── ...
```

### List ID Resolution

Claude Code determines the task list ID at **startup** using this priority:

1. `CLAUDE_CODE_TASK_LIST_ID` environment variable (if set)
2. Session ID (auto-generated UUID for each Claude session)

**Critical:** Once Claude starts, the list ID is fixed for that session. You cannot change it by running `export` commands inside the session.

## Environment Variable Behavior

### Setting Before Startup (Correct)

```bash
# The env var is read when Claude starts
CLAUDE_CODE_TASK_LIST_ID=my-project claude

# All tasks will be stored in:
# ~/.claude/tasks/my-project/
```

### Setting After Startup (Does NOT Work)

```bash
# Start Claude without env var
claude

# Inside Claude, this runs in a Bash subprocess
export CLAUDE_CODE_TASK_LIST_ID=my-project  # ❌ Has no effect!

# Tasks still go to:
# ~/.claude/tasks/<session-uuid>/
```

The `export` command runs in a **subprocess** that exits immediately. It doesn't affect Claude's environment.

## Subagent Environment Inheritance

When you spawn a subagent using the `Task()` tool, the subagent **inherits the parent's environment**:

```
Parent Claude (CLAUDE_CODE_TASK_LIST_ID=my-project)
    │
    └── Task() spawns subagent
            │
            └── Subagent inherits CLAUDE_CODE_TASK_LIST_ID=my-project
```

This means:
- If parent was started with the env var → subagents share the same task list
- If parent was started without → each subagent gets its own isolated list

## Task File Format

Each task is stored as a JSON file:

```json
{
  "id": "1",
  "subject": "Implement user authentication",
  "description": "Create login/logout endpoints with JWT tokens",
  "activeForm": "Implementing user authentication",
  "status": "pending",
  "owner": null,
  "blockedBy": [],
  "blocks": ["2", "3"],
  "metadata": {}
}
```

### Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Not started |
| `in_progress` | Being worked on |
| `completed` | Finished |

### Dependency Fields

| Field | Meaning |
|-------|---------|
| `blockedBy` | Tasks that must complete before this one can start |
| `blocks` | Tasks waiting for this one to complete |

## Cross-Session Communication

When multiple sessions share the same task list ID:

1. **File-based persistence**: All changes are written to disk immediately
2. **Broadcast mechanism**: Updates are pushed to other sessions
3. **Atomic operations**: Writes are atomic to prevent corruption

```
Session A (CLAUDE_CODE_TASK_LIST_ID=proj)
    │
    ├── TaskUpdate(taskId: "1", status: "completed")
    │       ↓
    │   Write to ~/.claude/tasks/proj/1.json
    │       ↓
    │   Broadcast to other sessions
    │       ↓
Session B (CLAUDE_CODE_TASK_LIST_ID=proj)
    │
    └── Receives update, reflects in TaskList()
```

## Common Patterns

### Pattern 1: Coordinator with Subagents

```bash
# Start coordinator with shared list
CLAUDE_CODE_TASK_LIST_ID=feature-x claude

# Coordinator creates tasks
TaskCreate(subject: "Task 1", ...)
TaskCreate(subject: "Task 2", ...)

# Coordinator spawns subagents
Task(prompt: "Complete task 1...", ...)
Task(prompt: "Complete task 2...", ...)

# Subagents inherit list ID and can update tasks
```

### Pattern 2: Multiple Terminals

```bash
# Terminal 1
CLAUDE_CODE_TASK_LIST_ID=big-refactor claude
# Creates tasks, monitors progress

# Terminal 2
CLAUDE_CODE_TASK_LIST_ID=big-refactor claude
# Works on task 1

# Terminal 3
CLAUDE_CODE_TASK_LIST_ID=big-refactor claude
# Works on task 2
```

All three terminals see the same tasks and updates.

### Pattern 3: Resume Previous Session

```bash
# Check what lists exist
ls ~/.claude/tasks/

# Resume specific list
CLAUDE_CODE_TASK_LIST_ID=feature-x claude

# Or use wrapper script
~/.claude/skills/dispatch/scripts/start-session.sh --resume feature-x
```

## Troubleshooting

### Problem: TaskList shows empty after compaction

**Cause:** Context compaction doesn't affect task persistence. Tasks are on disk.

**Diagnosis:**
```bash
# Check current list ID
echo $CLAUDE_CODE_TASK_LIST_ID

# Check what's on disk
ls ~/.claude/tasks/*/
```

**Solution:** If list ID is correct, tasks should appear. If not, you may be using a different list.

### Problem: Subagents can't see parent's tasks

**Cause:** Parent wasn't started with `CLAUDE_CODE_TASK_LIST_ID`.

**Diagnosis:**
```bash
# In parent session
bun run ~/.claude/skills/dispatch/scripts/init-session.ts --check
```

**Solution:** Restart parent with env var set.

### Problem: "Task not found" after spawning agent

**Cause:** Agent is using a different task list than expected.

**Diagnosis:** Check which list the agent is using by looking at the task path in error messages.

**Solution:** Ensure parent was started with `CLAUDE_CODE_TASK_LIST_ID`.

## File Locations

| File | Purpose |
|------|---------|
| `~/.claude/tasks/` | Base directory for all task lists |
| `~/.claude/tasks/.current-list-id` | Stores the most recently used list ID |
| `~/.claude/tasks/<list-id>/` | Directory containing tasks for a specific list |
| `~/.claude/tasks/<list-id>/<n>.json` | Individual task file |

## Best Practices

1. **Always start Claude with the env var** for multi-agent work
2. **Use meaningful list IDs** like `feature-auth` instead of timestamps
3. **Check coordination status** with `init-session.ts --check`
4. **Use the wrapper script** `start-session.sh` for convenience
5. **Don't try to change list ID mid-session** - it won't work
