---
name: Dispatch
description: This skill should be used when coordinating complex features that span multiple tasks requiring parallel subagent execution. It applies when users request large implementations, multi-step refactors, or projects requiring work distribution across agents. Triggers on "coordinate tasks", "spawn agents", "parallelize this work", "break this into tasks", or requests for features requiring 5+ distinct implementation steps.
icon: 🚀
alwaysAllow:
  - TaskCreate
  - TaskUpdate
  - TaskList
  - TaskGet
  - Task
  - Bash
  - Read
  - Glob
  - Grep
---

# Dispatch

Coordinate complex features using Claude Code's Task system and parallel subagent execution.

## Setup After Sync (Team Skills Users)

If you installed this skill via **Vesper Team Skills sync**, run the setup script once:

```bash
# For Team Skills install location:
~/.vesper/team-skills/dispatch/setup.sh

# For manual install location:
~/.claude/skills/dispatch/setup.sh
```

This installs:
- **`cc` and `ccd` commands** - Claude wrappers with automatic task coordination
- **Auto-archive hook** - Preserves task history when sessions end

> **Note:** Skip this if you already ran setup or installed via `install-cc.sh`.

---

## Important: How Task Coordination Works

Claude Code's task system enables multi-agent collaboration:

- **Tasks are persisted** to `~/.claude/tasks/<list-id>/`
- **Updates are broadcasted** to all sessions on the same Task List
- **Subagents inherit** the parent's environment automatically

**Critical:** The `CLAUDE_CODE_TASK_LIST_ID` environment variable must be set **BEFORE starting Claude**, not during a session.

## Installation: The `cc` Command

Install the `cc` wrapper to **never forget** task coordination:

```bash
~/.claude/skills/dispatch/scripts/install-cc.sh
```

Now use `cc` instead of `claude`:

```bash
cc                      # Resume last task list
cc my-feature           # Use specific task list
cc --new big-refactor   # Force new task list
cc --dangerous          # Skip permission prompts
cc --list               # Show all task lists
```

**Shortcut:** `ccd` = `cc --dangerous` (task coordination + skip permissions)

**This is the recommended way to use dispatch.** It ensures task coordination is always enabled.

## Pre-Flight Check (REQUIRED)

**Before creating ANY tasks, Claude MUST:**

1. Check the current task list:
   ```bash
   echo "List: $CLAUDE_CODE_TASK_LIST_ID"
   ```

2. Check for existing tasks:
   ```
   TaskList()
   ```

3. **If tasks exist**, warn the user:
   > ⚠️ **Task list "[list-id]" already has X tasks.**
   > Creating new tasks here will mix with existing work.
   >
   > Options:
   > 1. Continue here (add to existing tasks)
   > 2. Exit and start fresh: `cc new-feature-name`
   >
   > Which would you prefer?

4. Wait for user confirmation before proceeding.

## Quick Start

```bash
# Step 1: Start Claude with cc (task coordination automatic!)
cc my-feature

# Step 2: Create tasks (built-in tools work correctly now)
TaskCreate(subject: "Design API", description: "...", activeForm: "Designing API")
TaskCreate(subject: "Implement endpoints", description: "...", activeForm: "Implementing")

# Step 3: Set dependencies
TaskUpdate(taskId: "2", addBlockedBy: ["1"])

# Step 4: Validate before spawning
bun run $SKILL/scripts/validate-dependency-graph.ts

# Step 5: Spawn agents - they inherit CLAUDE_CODE_TASK_LIST_ID automatically!
Task(
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: "Complete task 1: Design API...",
  description: "Task 1: Design API"
)

# Step 6: Monitor
TaskList()
```

## Starting a Coordinated Session

### Option A: Use `cc` command (Recommended)

After installing with `install-cc.sh`:

```bash
cc                      # Resume last task list (or create new)
cc my-feature           # Use/create specific task list
cc --new big-refactor   # Force create new task list
cc --list               # Show all available task lists

# Pass arguments to claude
cc my-feature -p "fix the login bug"
```

### Option B: Use `start-session.sh`

If you prefer not to install `cc`:

```bash
SKILL=~/.claude/skills/dispatch

$SKILL/scripts/start-session.sh                    # Auto ID
$SKILL/scripts/start-session.sh feature-auth       # Custom ID
$SKILL/scripts/start-session.sh --resume           # Resume recent
```

### Option C: Set environment variable directly

```bash
# New session
CLAUDE_CODE_TASK_LIST_ID=my-project claude

# Resume existing session
CLAUDE_CODE_TASK_LIST_ID=$(cat ~/.claude/tasks/.current-list-id) claude
```

## Decision Matrix

| Condition | Action |
|-----------|--------|
| 5+ implementation steps | Use this skill |
| Parallelizable work | Use this skill |
| Need progress tracking | Use this skill |
| 1-3 steps | Execute directly |
| Single-file change | Execute directly |
| Simple bug fix | Execute directly |

## Constraints

| Model | Timeout | Retries | Use For |
|-------|---------|---------|---------|
| opus | 30 min | 1 | Architecture, complex logic |
| sonnet | 15 min | 2 | Features, tests, integrations, task coordination |

**Do NOT use Haiku for dispatch tasks.** Haiku models lack tool awareness and will search the filesystem for `TaskList`/`TaskUpdate`/`TaskGet` instead of recognizing them as Claude Code's built-in tools. Use Sonnet as the minimum model for any task that requires task coordination.

## Check Current Task List

To find out which task list is active:

```bash
echo $CLAUDE_CODE_TASK_LIST_ID
```

If empty, coordination is NOT enabled. Restart with `cc <list-name>`.

## Task Storage

- **Location:** `~/.claude/tasks/<list-id>/<task-id>.json`
- **Current list:** `~/.claude/tasks/.current-list-id`
- **Dependencies:** `blockedBy` (must complete first), `blocks` (waits for this)

## Workflow

### Step 1: Start with Task Coordination

**Before doing any task management, ensure you started Claude correctly:**

```bash
# Check if coordination is enabled
echo $CLAUDE_CODE_TASK_LIST_ID
```

If empty, you need to restart Claude with the environment variable set.

### Step 2: Decompose Work

- Identify 3-10 discrete tasks
- Each task: atomic, independent files, testable
- Include `Files:` in description for conflict detection

### Step 3: Create Tasks

Use the built-in TaskCreate tool:

```
TaskCreate(
  subject: "Imperative title",
  description: "Requirements:\n- item\n- item\n\nFiles: src/foo.ts, src/bar.ts",
  activeForm: "Present participle title"
)
```

### Step 4: Set Dependencies

```
TaskUpdate(taskId: "2", addBlockedBy: ["1"])
TaskUpdate(taskId: "3", addBlockedBy: ["1"])
TaskUpdate(taskId: "4", addBlockedBy: ["2", "3"])
```

### Step 5: Validate

```bash
bun run $SKILL/scripts/validate-dependency-graph.ts
bun run $SKILL/scripts/detect-file-conflicts.ts
```

### Step 6: Spawn Agents

Subagents automatically inherit `CLAUDE_CODE_TASK_LIST_ID` from the parent session.

**Important: Prompt Syntax for Subagents**

Use **direct tool invocation syntax** in prompts. Subagents interpret verbose descriptions (e.g., "Call TaskList() to see tasks") as functions to search for, not tools to invoke.

| ❌ Ambiguous | ✅ Direct |
|-------------|----------|
| "Call TaskList() to see available tasks" | "Use TaskList to check status" |
| "Use the TaskUpdate function" | "TaskUpdate(taskId: "1", status: "completed")" |

**Simple spawn:**
```
TaskUpdate(taskId: "1", status: "in_progress", owner: "agent-1")

Task(
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: """
## Your Assignment

Task ID: 1
Subject: Design API schema

[Full task description here]

## On Completion

Mark complete: TaskUpdate(taskId: "1", status: "completed")
""",
  description: "Task 1: Design API schema"
)
```

**Parallel spawning:** Include multiple Task() calls in a single message.

### Step 7: Monitor

```bash
TaskList                                          # Quick status
bun run $SKILL/scripts/task-dashboard.ts --watch  # Visual dashboard
bun run $SKILL/scripts/detect-stale-tasks.ts      # Find stuck tasks
```

### Step 8: Report

```markdown
## Progress: 3/7 tasks

**Completed:** 1, 2, 3
**In Progress:** 4, 5
**Blocked:** 6 (waiting: 4, 5)
**Ready:** 7
```

## Error Recovery

| Error Type | Action |
|------------|--------|
| Timeout | Check partial progress, retry or split task |
| Transient | Backoff and retry (up to max retries) |
| Config error | Fix config, retry |
| Logic error | Create blocker task to resolve |
| Unrecoverable | Escalate to user |

**Cascading failure:** Identify blocked tasks, offer user: retry / skip / abort

**Reset stale:** `bun run $SKILL/scripts/detect-stale-tasks.ts --reset`

## Troubleshooting

### "TaskList shows empty" or "Task not found"

**Cause:** Claude was not started with `CLAUDE_CODE_TASK_LIST_ID` set.

**Fix:** Restart Claude with the wrapper script:
```bash
$SKILL/scripts/start-session.sh --resume
```

### "Subagents can't see parent's tasks"

**Cause:** Parent session wasn't started with the env var.

**Fix:** This is inherited automatically when set correctly. Restart parent session:
```bash
CLAUDE_CODE_TASK_LIST_ID=my-project claude
```

### "Tasks disappeared after conversation compacted"

**Cause:** Tasks ARE persisted to disk. If TaskList shows empty, the session is using a different list ID.

**Fix:** Check which list has your tasks:
```bash
ls -la ~/.claude/tasks/*/
```

Then restart Claude with that list ID.

### "Created tasks but forgot to set env var"

**Cause:** You created tasks in a session-scoped list that subagents can't access.

**Fix:** Use the recovery tools to migrate your tasks:

```bash
# Option 1: Migrate current session's tasks
bun run $SKILL/scripts/migrate-session.ts my-project

# Option 2: List all task lists and sync them
bun run $SKILL/scripts/sync-tasks.ts --list
bun run $SKILL/scripts/sync-tasks.ts --target my-project
```

Then restart Claude with the shared list:
```bash
CLAUDE_CODE_TASK_LIST_ID=my-project claude
```

## Recovery Tools

When you forget to set `CLAUDE_CODE_TASK_LIST_ID` before starting Claude, use these tools to recover:

### migrate-session.ts

Migrate tasks from the current session to a shared list:

```bash
# Migrate to a new shared list
bun run $SKILL/scripts/migrate-session.ts my-project

# Preview what would be migrated
bun run $SKILL/scripts/migrate-session.ts my-project --dry-run
```

### sync-tasks.ts

Merge tasks from multiple orphaned session lists:

```bash
# List all task lists
bun run $SKILL/scripts/sync-tasks.ts --list

# Merge all session-scoped lists into one
bun run $SKILL/scripts/sync-tasks.ts --target my-project

# Only sync specific lists
bun run $SKILL/scripts/sync-tasks.ts --target my-project --include session-123,abc-def

# Preview sync
bun run $SKILL/scripts/sync-tasks.ts --target my-project --dry-run
```

## Scripts

```bash
# Set SKILL to your install location:
SKILL=~/.claude/skills/dispatch           # Manual install
SKILL=~/.vesper/team-skills/dispatch      # Team Skills sync
```

| Script | Purpose |
|--------|---------|
| `setup.sh` | **One-command setup** (installs cc + hook) |
| `cc` | **Claude wrapper with auto task coordination** |
| `ccd` | **cc + dangerous mode (skip permissions)** |
| `scripts/install-cc.sh` | Install `cc` and `ccd` to your PATH |
| `start-session.sh [id]` | Start Claude with task coordination |
| `init-session.ts [--check]` | Generate startup command, check status |
| `migrate-session.ts <id>` | **Recovery:** Migrate current session tasks |
| `sync-tasks.ts --target <id>` | **Recovery:** Merge multiple lists |
| `validate-dependency-graph.ts` | Cycle detection, graph validation |
| `pre-spawn-validation.ts <id>` | Pre-flight readiness check |
| `detect-stale-tasks.ts [--reset]` | Find/reset stuck tasks |
| `detect-file-conflicts.ts` | Identify file overlap |
| `task-dashboard.ts [--watch]` | Visual status board |
| `spawn-agent.ts <id> [model]` | Generate Task() call template |
| `get-task-list-id.ts` | Show current task list ID |
| `archive-tasks.ts [--all]` | **Archive tasks as historical logs** |
| `list-archives.ts [--restore]` | List/restore archived tasks |
| `hooks/auto-archive.sh` | **Stop hook: auto-archive on session end** |
| `hooks/install-hook.sh` | Install the auto-archive hook |

## Task Archival (Historical Logs)

Claude Code may clean up task files when sessions end. To preserve tasks as logs, use the archival system.

### Auto-Archive Hook (Recommended)

The `Stop` hook automatically archives tasks when sessions end, running asynchronously to avoid blocking:

```json
// ~/.claude/settings.json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "~/.claude/skills/dispatch/hooks/auto-archive.sh",
        "async": true,
        "timeout": 30
      }]
    }]
  }
}
```

This is the **recommended approach** - tasks are preserved automatically without manual intervention.

### Archive Location

```
~/.claude/tasks-archive/
  └── <list-id>-<timestamp>/
      ├── manifest.json      # Archive metadata
      ├── 1.json             # Task files
      ├── 2.json
      └── ...
```

### Archival Methods

**Method 1: Auto-archive with `cc --new`**

When creating a new task list, the previous list is automatically archived:

```bash
cc --new my-new-feature    # Archives previous list, creates new one
cc --new --no-archive      # Skip auto-archive
```

**Method 2: Manual archive with `cc --archive`**

```bash
cc --archive               # Archive current list, then resume it
cc --archive-all           # Archive ALL non-empty task lists
```

**Method 3: Archive script**

```bash
bun run $SKILL/scripts/archive-tasks.ts                    # Archive current list
bun run $SKILL/scripts/archive-tasks.ts my-feature         # Archive specific list
bun run $SKILL/scripts/archive-tasks.ts --all              # Archive all lists
bun run $SKILL/scripts/archive-tasks.ts --completed        # Archive only completed lists
bun run $SKILL/scripts/archive-tasks.ts --dry-run          # Preview
```

### Viewing Archives

```bash
bun run $SKILL/scripts/list-archives.ts                    # List all archives
bun run $SKILL/scripts/list-archives.ts my-feature-20260125-143022   # View details
```

### Restoring Archives

```bash
bun run $SKILL/scripts/list-archives.ts --restore my-feature-20260125-143022
cc my-feature              # Resume the restored list
```

### Best Practices

- Archive before ending long sessions: `cc --archive`
- Use `cc --new` to auto-archive when switching projects
- Archive completed lists: `archive-tasks.ts --completed`
- Check archives regularly: `list-archives.ts`

## Anti-Patterns

- ❌ Starting Claude without `CLAUDE_CODE_TASK_LIST_ID` set
- ❌ Trying to set env var after Claude is running (doesn't work)
- ❌ Tasks < 30 min work (over-decomposition)
- ❌ Vague descriptions (under-specification)
- ❌ Circular dependencies (validate first)
- ❌ Spawning blocked tasks (check blockedBy)
- ❌ Parallel tasks on same files (serialize via blockedBy)
- ❌ Missing completion in prompt (always include TaskUpdate)

## Multi-Terminal Workflow

For parallel execution across terminal windows, all terminals must use the same list ID:

```bash
# Terminal 1: Coordinator
CLAUDE_CODE_TASK_LIST_ID=my-project claude

# Terminal 2: Worker (same list ID!)
CLAUDE_CODE_TASK_LIST_ID=my-project claude

# Terminal 3: Worker (same list ID!)
CLAUDE_CODE_TASK_LIST_ID=my-project claude
```

All sessions will share tasks and see each other's updates in real-time.

### Multi-Terminal Claiming Protocol

When multiple terminals share the same task list, use this **check-claim-verify** pattern to avoid race conditions where two terminals claim the same task:

#### Step 1: Check Available Tasks

```
TaskList
```

Look for tasks with `status: pending` and no `owner`.

#### Step 2: Claim with Unique Owner ID

```
TaskUpdate(taskId: "3", status: "in_progress", owner: "worker-1")
```

Use a unique owner identifier per terminal.

**Common owner ID patterns:**
- `worker-1`, `worker-2` (simple sequential)
- `agent-macbook-12345` (hostname + PID)

#### Step 3: Verify Ownership

```
TaskList
```

Check that task shows YOUR owner ID (e.g., `(worker-1)`). If it shows a different owner, another terminal claimed it first—pick a different task.

**Note:** Use `TaskList` for verification instead of `TaskGet`. TaskList displays the owner in its output; TaskGet does not.

#### Collision Resolution

If two terminals claim simultaneously, one will "win" (last write). The "loser" detects this on Step 3 and simply picks another task:

```
# Terminal A claims task 3 → owner: "worker-a"
# Terminal B claims task 3 → owner: "worker-b" (overwrites A)
# Terminal A verifies → sees "worker-b" → picks task 4 instead
# Terminal B verifies → sees "worker-b" → proceeds with task 3
```

This is **eventual consistency** without locking—simple and effective for typical multi-terminal workflows.

#### Example Workflow

```
# In each terminal:

1. TaskList
   # → #3 [pending] Design API
   # → #4 [pending] Write tests

2. TaskUpdate(taskId: "3", status: "in_progress", owner: "worker-1")

3. TaskList
   # → #3 [in_progress] Design API (worker-1)  ← You own it, proceed
   # OR
   # → #3 [in_progress] Design API (worker-2)  ← Someone else won, try #4

4. [Do the work]

5. TaskUpdate(taskId: "3", status: "completed")
```

#### When to Use This Pattern

| Scenario | Use Claiming Protocol? |
|----------|------------------------|
| Single terminal | No (unnecessary) |
| 2-3 terminals, manual coordination | Optional (verbal handoff works) |
| 3+ terminals, automated dispatch | **Yes** |
| CI/CD parallel jobs | **Yes** |

## References

- `references/task-tools-api.md` - Tool parameters
- `references/dependency-patterns.md` - Graph patterns
- `references/failure-recovery.md` - Error handling
- `references/example-oauth.md` - Complete example
- `references/task-architecture.md` - How task system works
