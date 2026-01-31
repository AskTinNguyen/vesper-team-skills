---
name: agent-supervisor
description: Act as a supervisor agent that monitors the task list, detects gaps, creates tasks, and tracks status without doing implementation work. Use when orchestrating multiple agents and needing oversight — monitoring task completion, tracking PR review status, or following another agent's progress. Triggers on "be a supervisor", "monitor the task list", "follow the agent", "track PR status", "supervise agents", "be the coordinator".
alwaysAllow:
  - TaskCreate
  - TaskUpdate
  - TaskList
  - TaskGet
  - Task
  - Bash
  - Read
  - Grep
  - Glob
---

# Agent Supervisor

Monitor and coordinate multi-agent work through the Claude Code task list. The supervisor observes, creates tasks, flags issues, and reports status — but never does implementation work itself.

## Core Principle

> The supervisor ONLY creates tasks and flags issues. It never writes code, makes commits, or modifies project files.

## Pre-Flight

Before starting any supervision mode:

```bash
# 1. Verify task coordination is enabled
echo "Task list: $CLAUDE_CODE_TASK_LIST_ID"

# 2. Check current task state
TaskList

# 3. Verify /tasklist-env if needed
bash ~/.claude/skills/tasklist-env/scripts/tasklist_env.sh status
```

If `CLAUDE_CODE_TASK_LIST_ID` is empty, restart Claude with `cc <list-name>`.

## Modes

### Mode 1: Pure Supervisor

Monitor the task list, detect stalled or missing work, and create new tasks as needed.

**When to use:** Orchestrating multiple worker agents on a shared task list.

**Behavior loop:**

1. **Snapshot** — `TaskList` to get current state
2. **Analyze** — Identify:
   - Stalled tasks (in_progress too long with no progress)
   - Missing tasks (gaps in the plan)
   - Blocked tasks that could be unblocked
   - Completed tasks that need follow-up
3. **Act** — Create new tasks, update notes, flag blockers
4. **Report** — Output a status summary
5. **Poll** — Wait for the configured interval, then repeat

**Starting pure supervisor:**

```
I need you to act as a supervisor agent.

Mode: Pure Supervisor
Task list: $CLAUDE_CODE_TASK_LIST_ID
Poll interval: 5 minutes

Monitor the task list. When you detect gaps or stalled work:
- Create new tasks for missing work
- Flag stalled tasks (in_progress for >2 poll cycles without change)
- Report status each cycle

Never do implementation work. Only create tasks and flag issues.
```

**Stall detection:**

Run `scripts/task-diff.sh` between poll cycles. If a task has been `in_progress` for multiple cycles with no description/status changes, flag it:

```bash
# Take snapshot
bash scripts/poll-tasklist.sh snapshot

# Wait, then compare
bash scripts/poll-tasklist.sh diff
```

### Mode 2: PR Status Tracker

Monitor PR review and merge status, keeping the task list in sync with GitHub.

**When to use:** After PRs have been created and are awaiting review/merge.

**Behavior loop:**

1. **Sync** — Run `github-sync` PR status check
2. **Update** — Apply status changes to tasks
3. **Flag** — Alert on changes requested, merge conflicts, CI failures
4. **Report** — Output PR status summary
5. **Poll** — Wait, then repeat

**Starting PR tracker:**

```
I need you to act as a supervisor agent.

Mode: PR Status Tracker
Task list: $CLAUDE_CODE_TASK_LIST_ID
Poll interval: 5 minutes

Track PR merge/review status using github-sync scripts.
Update task statuses when PRs are merged/approved/rejected.
Flag any PRs with requested changes for human attention.

Never modify code or PRs. Only update task statuses and flag issues.
```

**Uses `github-sync` scripts:**

```bash
# Check all PR-linked tasks
bash ~/.claude/skills/github-sync/scripts/pr-status-check.sh

# Full reconciliation
bash ~/.claude/skills/github-sync/scripts/reconcile.sh
```

### Mode 3: Review Follower

Follow a review agent's progress, update task statuses, and flag issues that need human intervention.

**When to use:** After dispatching review agents (via `/workflows:review` or `/workflows:bulk-review`).

**Behavior loop:**

1. **Check** — `TaskList` for review task statuses
2. **Detect** — Identify completed reviews, failed reviews, human-needed flags
3. **Escalate** — Create summary tasks for items needing human attention
4. **Report** — Output review progress
5. **Poll** — Wait, then repeat

**Starting review follower:**

```
I need you to act as a supervisor agent.

Mode: Review Follower
Task list: $CLAUDE_CODE_TASK_LIST_ID
Poll interval: 3 minutes

Follow review agent progress. When reviews complete:
- Mark review tasks as completed
- Create fix tasks for issues found
- Flag items needing human review with [HUMAN] prefix in task subject
- Report progress each cycle

Never do reviews or fixes yourself. Only track and create tasks.
```

## Polling

### Using poll-tasklist.sh

The polling script handles interval-based monitoring with diff detection:

```bash
# Start polling at 5-minute intervals (default)
bash scripts/poll-tasklist.sh start

# Custom interval (in seconds)
bash scripts/poll-tasklist.sh start 180

# Take a single snapshot (for comparison later)
bash scripts/poll-tasklist.sh snapshot

# Compare current state to last snapshot
bash scripts/poll-tasklist.sh diff
```

### Using task-diff.sh

For detailed comparison between two task list states:

```bash
# Compare current state to a saved snapshot
bash scripts/task-diff.sh /tmp/tasks-snapshot-prev.json /tmp/tasks-snapshot-curr.json
```

Output shows:
- New tasks created since last snapshot
- Tasks that changed status
- Tasks that changed owner
- Tasks that were deleted

## Status Report Format

Each polling cycle should produce a report:

```markdown
## Supervisor Report — Cycle N

**Time:** [timestamp]
**Mode:** [Pure Supervisor | PR Tracker | Review Follower]

### Task Summary
- Pending: X
- In Progress: Y
- Completed: Z
- Blocked: W

### Changes Since Last Cycle
- [task changes detected by diff]

### Actions Taken
- Created task: "..." (reason)
- Flagged task #N: stalled for 3 cycles
- Updated task #N: PR merged

### Needs Attention
- [items requiring human intervention]
```

## Composing with Other Skills

| Skill | How Supervisor Uses It |
|-------|----------------------|
| `/dispatch` | Inherits task conventions, uses `cc` for session management |
| `/tasklist-env` | Pre-flight environment check |
| `github-sync` | PR tracker mode calls sync scripts each cycle |
| `verify-and-ship` | Supervisor may create verification tasks for completed work |
| `/workflows:review` | Review follower mode tracks dispatched review agents |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/poll-tasklist.sh` | Interval polling with snapshot and diff detection |
| `scripts/task-diff.sh` | Compare two task list snapshots, report changes |

## Anti-Patterns

- **Doing implementation work** — Supervisor creates tasks, never writes code
- **Polling too frequently** — Minimum 2-minute intervals to avoid noise
- **Ignoring stalls** — Flag tasks stuck in_progress for >2 cycles
- **Missing follow-up** — Completed tasks may need verification or next-step tasks
- **Running without task coordination** — Always verify `CLAUDE_CODE_TASK_LIST_ID` first

## References

- `references/supervisor-modes.md` — Detailed mode configuration and examples
- `references/polling-strategies.md` — Tuning poll intervals and stall detection
