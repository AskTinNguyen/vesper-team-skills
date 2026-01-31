---
description: Partition tests into zones and dispatch parallel agents per zone. Optionally specify zones as arguments.
argument-hint: "[zone1,zone2,...] — e.g., frontend,api,models or blank for auto-detection"
allowed-tools: [Skill(tasklist-env), Skill(verify-and-ship), Task, TaskCreate, TaskUpdate, TaskList, TaskGet, Bash, Read, Grep, Glob]
---

# Dispatch Tests

Detect project test structure, partition into zones, and use `/dispatch` to spawn parallel test agents per zone.

## What This Command Does

1. **Detect** test structure and partition into zones
2. **Create** a task per zone (parallel test execution)
3. **Dispatch** agents per zone using `/dispatch` conventions
4. **Synthesize** results into a summary report

## Step 1: Detect Test Zones

<task_list>

- [ ] If arguments provided, parse comma-separated zone names
- [ ] If no arguments, auto-detect zones by scanning project structure:
  ```
  Scan for test directories and files:
  - tests/, test/, __tests__/, spec/
  - *_test.go, *_test.py, *.test.ts, *.test.js, *.spec.ts, *.spec.js
  - cypress/, e2e/, integration/, playwright/
  ```
- [ ] Group tests into zones. Common zone patterns:
  | Zone | Matches |
  |------|---------|
  | `unit` | tests/unit/, **/unit/*, fast tests |
  | `integration` | tests/integration/, **/integration/* |
  | `e2e` | cypress/, e2e/, playwright/ |
  | `frontend` | src/**/*.test.tsx, src/components/**, src/pages/** |
  | `api` | tests/api/, src/api/**/*.test.*, routes/**/*.test.* |
  | `models` | tests/models/, src/models/**/*.test.* |
  | `services` | tests/services/, src/services/**/*.test.* |
- [ ] Display detected zones with file counts for user confirmation
- [ ] Read CLAUDE.md for project-specific test conventions

</task_list>

## Step 2: Pre-Flight

<task_list>

- [ ] Verify task coordination: `echo $CLAUDE_CODE_TASK_LIST_ID`
- [ ] If empty, warn user to restart with `cc <list-name>`
- [ ] Check existing tasks with `TaskList` — warn if task list is not empty
- [ ] Verify test runner is available (detect from package.json, Makefile, go.mod, etc.)
- [ ] Invoke task environment check:
  ```
  skill: tasklist-env
  ```
  Verify the active task list environment is correct before creating zone tasks.

</task_list>

## Step 3: Create Zone Tasks

<task_list>

- [ ] For each zone, create a task:
  ```
  TaskCreate(
    subject: "Run [zone] tests",
    description: "Zone: [zone]\nFiles: [file patterns]\nRunner: [detected runner]\n\nRun all tests in this zone. Report pass/fail counts and any failures.\n\n---\nMetadata: test_zone=[zone]",
    activeForm: "Running [zone] tests"
  )
  ```
- [ ] Set dependencies if zones have ordering requirements (e.g., unit before integration)
- [ ] For each zone, also create a follow-up documentation task:
  ```
  TaskCreate(
    subject: "Document [zone] test results",
    description: "After [zone] tests complete, summarize:\n- Total tests run\n- Pass/fail breakdown\n- Failure details with file:line references\n- Suggestions for fixing failures",
    activeForm: "Documenting [zone] test results"
  )
  TaskUpdate(taskId: "[doc-task-id]", addBlockedBy: ["[test-task-id]"])
  ```

</task_list>

## Step 4: Dispatch Agents

<task_list>

- [ ] For each unblocked test zone task, spawn a parallel agent:

<agent_task>

```
Task(
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: """
## Assignment: Run [zone] Tests

Task ID: [id]

Run all tests in the [zone] zone.

### Files/Patterns
[list of test file patterns for this zone]

### Test Runner
[detected test runner command]

### Process
1. TaskUpdate(taskId: "[id]", status: "in_progress")
2. Run the test command for this zone
3. Capture output (pass count, fail count, error details)
4. If failures exist, read failing test files to understand context
5. Report results in task description
6. TaskUpdate(taskId: "[id]", status: "completed")

### Output Format
Report as structured text:
- Total: N tests
- Passed: N
- Failed: N
- Failures:
  - file:line — description
""",
  description: "Test zone: [zone]"
)
```

</agent_task>

- [ ] Spawn all independent zone agents in parallel (single message with multiple Task calls)

</task_list>

## Step 5: Synthesize Results

<task_list>

- [ ] Wait for all zone tasks to complete (poll with `TaskList`)
- [ ] Collect results from each zone task's description
- [ ] Generate summary report:

```markdown
## Test Dispatch Report

| Zone | Total | Passed | Failed | Status |
|------|-------|--------|--------|--------|
| unit | 142 | 140 | 2 | FAIL |
| api | 67 | 67 | 0 | PASS |
| e2e | 23 | 22 | 1 | FAIL |

### Failures

**unit zone:**
- src/auth/validate.test.ts:45 — expected token to be valid
- src/utils/parse.test.ts:12 — timeout exceeded

**e2e zone:**
- e2e/checkout.spec.ts:88 — element not found

### Overall: 232 tests, 229 passed, 3 failed
```

</task_list>

## Step 6: Ship Fixes (Optional)

If test failures were found and fixed by agents, invoke the verify-and-ship skill to commit and push:

```
skill: verify-and-ship
```

Tell the skill: "Auto-ship mode. Verify and push any uncommitted test fixes."

## Rules

- **Invoke skills directly** — Use `skill: github-sync`, `skill: verify-and-ship`, `skill: tasklist-env` instead of hardcoding script paths
- **Dispatch conventions** — Follow `/dispatch` task creation and agent spawning patterns
- **Parallel by default** — Zones without dependencies run concurrently
- **Never skip failing tests** — Report all failures, don't suppress output
- **Use the detected test runner** — Don't assume npm/pytest/go; detect from project config
- **Zone documentation tasks** — Always create follow-up tasks blocked by the test task
- **Synthesis is mandatory** — Collect all zone results into a final summary
