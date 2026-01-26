# Failure Recovery Guide

This reference documents how to handle failures in task coordination.

## Failure Types

### 1. Agent Timeout

**Symptoms:**
- No output from agent for extended period
- Task stuck in `in_progress` status

**Detection:**
```bash
bun run scripts/detect-stale-tasks.ts --threshold=30
```

**Recovery:**
1. Check if partial work exists (git status, file changes)
2. Reset task to pending:
   ```
   TaskUpdate(taskId: "X", status: "pending", owner: undefined)
   ```
3. Respawn with same or different model
4. If repeated failures, escalate to user

### 2. Agent Error

**Symptoms:**
- Agent returns error message
- Task not marked completed

**Recovery:**
1. Read error details from agent output
2. Categorize error:
   - **Transient** (network, rate limit): Retry after backoff
   - **Configuration** (missing env var, permission): Fix config, retry
   - **Logic** (code error, invalid state): Create blocker task
   - **Unrecoverable** (impossible requirement): Escalate to user

**Retry Protocol:**
```
attempt = 1
max_retries = 3  // Adjust based on model

while attempt <= max_retries:
    result = spawn_agent(task)

    if result.success:
        break
    elif is_transient_error(result.error):
        wait(backoff_seconds * attempt)
        attempt += 1
    else:
        escalate_to_user(task, result.error)
        break

if attempt > max_retries:
    mark_task_blocked(task, "Exceeded retry limit")
```

### 3. Cascading Failure

**Symptoms:**
- Task fails, blocking multiple downstream tasks
- Dependency chain stalled

**Recovery:**
1. Identify all blocked tasks:
   ```
   TaskList()  // Find tasks with blockedBy containing failed task
   ```

2. Present options to user:
   ```
   Task X failed: [error description]

   Blocked tasks: Y, Z, W

   Options:
   1. Retry task X
   2. Skip X and manually unblock Y, Z, W
   3. Abort entire feature
   4. Create workaround task
   ```

3. If skipping, update downstream tasks:
   ```
   // Remove failed task from blockedBy
   TaskUpdate(taskId: "Y", blockedBy: [...without X...])
   ```

### 4. File Conflict

**Symptoms:**
- Two agents modified same file
- Merge conflict in git
- Inconsistent code state

**Prevention:**
```bash
bun run scripts/detect-file-conflicts.ts
```

**Recovery:**
1. Identify conflicting changes
2. Determine which agent's work to keep
3. Revert other agent's changes:
   ```bash
   git checkout HEAD -- <conflicting-file>
   ```
4. Reset losing task to pending
5. Add dependency to prevent recurrence:
   ```
   TaskUpdate(taskId: "TASK_B", addBlockedBy: ["TASK_A"])
   ```

### 5. Partial Completion

**Symptoms:**
- Agent completed some work but not all
- Tests partially passing
- Implementation incomplete

**Recovery:**
1. Assess completed work:
   ```bash
   git diff HEAD
   git status
   ```

2. Options:
   - **Commit partial**: If useful standalone
   - **Continue**: Spawn new agent with "continue from..." prompt
   - **Revert**: If partial work is problematic

**Continue Prompt Template:**
```
Continue task X: [subject]

Prior work completed:
- [x] Created file A
- [x] Implemented function B
- [ ] Need to add tests
- [ ] Need to update documentation

Files modified:
- src/foo.ts (created)
- src/bar.ts (modified)

Continue from current state. Focus on remaining items.
```

---

## Timeout Configuration

### Recommended Timeouts by Model

| Model | Default Timeout | Extended Timeout | Max Retries |
|-------|-----------------|------------------|-------------|
| Haiku | 5 minutes | 10 minutes | 3 |
| Sonnet | 15 minutes | 30 minutes | 2 |
| Opus | 30 minutes | 60 minutes | 1 |

### When to Extend Timeout

Extend timeout if:
- Task involves large file operations
- Task requires external API calls
- Agent shows progress (check output)

### Timeout Detection Loop

```
Check agent status every 60 seconds:

  if no_new_output for 3 consecutive checks:
    if task_has_partial_progress:
      extend_timeout(1.5x)
      log("Extended timeout for task X")
    else:
      terminate_agent()
      mark_task_for_retry()
```

---

## Error Classification

### Transient Errors (Retry)

- Rate limit exceeded
- Network timeout
- Temporary service unavailable
- Token limit hit (can split task)

### Configuration Errors (Fix & Retry)

- Missing API key
- Invalid credentials
- Permission denied
- Missing dependency

### Logic Errors (Create Blocker)

- Invalid assumptions in task
- Conflicting requirements
- Missing context/information
- Dependency on non-existent code

### Unrecoverable Errors (Escalate)

- Impossible requirement
- Security violation
- Out of scope for agent
- Requires human decision

---

## Status Reporting During Recovery

When recovery is needed, report to user with clear structure:

```markdown
## ⚠️ Task Failure Report

**Task:** X - [subject]
**Status:** Failed after 2 retries
**Model:** sonnet

### Error Details
[Specific error message or timeout information]

### Partial Progress
- [x] Created user model
- [x] Added database migration
- [ ] API endpoints (failed here)
- [ ] Tests

### Impact
- Tasks Y, Z blocked (depend on X)
- Current phase stalled

### Recommended Actions
1. **Retry with Opus** - Complex logic may need stronger model
2. **Split task** - Break into smaller pieces
3. **Manual intervention** - [Specific guidance]

### Files Modified
- `src/models/user.ts` (created)
- `db/migrations/001_users.ts` (created)
```

---

## Automated Recovery Scripts

### Reset Stale Tasks

```bash
# Find and reset tasks stuck over 30 minutes
bun run scripts/detect-stale-tasks.ts --threshold=30 --reset
```

### Validate Before Retry

```bash
# Check if task is ready to retry
bun run scripts/pre-spawn-validation.ts <task-id>
```

### Check for Conflicts Before Spawning

```bash
# Ensure no file conflicts with running tasks
bun run scripts/detect-file-conflicts.ts
```

---

## Best Practices

1. **Always validate before spawning** - Run pre-spawn-validation.ts
2. **Set reasonable timeouts** - Match to task complexity and model
3. **Limit retries** - 1-3 based on model to avoid infinite loops
4. **Preserve partial work** - Commit useful changes before retry
5. **Communicate failures clearly** - Give user actionable options
6. **Learn from failures** - If a task type repeatedly fails, decompose differently
