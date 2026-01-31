# Supervisor Modes — Detailed Reference

## Mode 1: Pure Supervisor

### Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| Poll interval | 300s (5min) | Time between task list checks |
| Stall threshold | 2 cycles | Cycles before flagging a stalled task |
| Auto-create tasks | yes | Create missing tasks when gaps detected |
| Implementation work | **never** | Supervisor never writes code |

### Decision Table

| Observation | Action |
|-------------|--------|
| Task in_progress, same state for >2 cycles | Flag as stalled, add note |
| All dependencies of a blocked task are completed | Notify (task should auto-unblock) |
| Gap in plan (e.g., no test task for new feature) | Create missing task |
| Task completed with errors mentioned | Create follow-up fix task |
| All tasks completed | Final report, ask user for next steps |
| Worker agent appears stuck (no task claimed in 2 cycles) | Create diagnostic task |

### Example Session

```
Cycle 1: Snapshot taken. 7 tasks (3 pending, 2 in_progress, 2 completed).
Cycle 2: Task #4 still in_progress. Task #5 completed. No new issues.
Cycle 3: Task #4 still in_progress (stall count: 2). FLAGGED.
         Created task #8: "Investigate stall on task #4"
Cycle 4: Task #4 completed. Task #8 can be dismissed.
         Task #6 unblocked. All dependencies met.
```

## Mode 2: PR Status Tracker

### Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| Poll interval | 300s (5min) | Time between PR status checks |
| Auto-complete merged | yes | Mark tasks completed when PR merges |
| Flag changes requested | yes | Alert on review feedback |
| Track CI status | optional | Also check CI pass/fail |

### GitHub-to-Task State Mapping

```
PR State        -> Task Action
────────────────────────────────
OPEN + DRAFT    -> No change (keep monitoring)
OPEN + PENDING  -> No change (awaiting review)
OPEN + APPROVED -> Add note "Approved, ready to merge"
OPEN + CHANGES  -> Flag "[ACTION NEEDED] Changes requested on PR #N"
MERGED          -> TaskUpdate(status: "completed")
CLOSED          -> TaskUpdate(status: "completed") + note "Closed without merge"
CI FAILING      -> Flag "[CI FAIL] PR #N"
```

### Integration with github-sync

Each polling cycle runs:

```bash
# 1. Check existing PR-linked tasks
bash ~/.claude/skills/github-sync/scripts/pr-status-check.sh

# 2. Optionally sync new PRs
bash ~/.claude/skills/github-sync/scripts/sync-prs-to-tasks.sh

# 3. Full reconciliation (every N cycles)
bash ~/.claude/skills/github-sync/scripts/reconcile.sh
```

## Mode 3: Review Follower

### Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| Poll interval | 180s (3min) | Time between review checks |
| Human flag prefix | `[HUMAN]` | Prefix for tasks needing human review |
| Auto-create fix tasks | yes | Create fix tasks for review findings |
| Escalation threshold | 2 failed fixes | Escalate to human after N fix attempts |

### Review Task Lifecycle

```
Review dispatched -> Task created (pending)
Review started    -> Task in_progress (agent claimed)
Review complete   -> Task completed
  - Issues found  -> Create fix tasks
  - Clean review  -> Mark as shipped
  - Can't fix     -> Create [HUMAN] task
```

### Escalation Rules

1. **Auto-fixable issue:** Create fix task, assign to worker agent
2. **Second fix attempt fails:** Add `[HUMAN]` prefix, flag for human
3. **Security concern:** Immediately flag as `[HUMAN][SECURITY]`
4. **Design question:** Flag as `[HUMAN][DESIGN]`

### Example Workflow

```
Cycle 1: Review agent started on PR #42. Task #10 in_progress.
Cycle 2: Review agent completed PR #42. Found 2 issues.
         Created task #11: "Fix: unused import in auth.ts" (auto-fixable)
         Created task #12: "[HUMAN] Design: auth flow uses deprecated pattern"
Cycle 3: Task #11 completed by worker agent. Task #12 awaiting human.
```
