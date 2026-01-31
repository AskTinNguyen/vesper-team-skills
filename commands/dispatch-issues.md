---
description: Pull GitHub issues into the task list and dispatch parallel agents to work on them. Optionally filter by label.
argument-hint: "[label:name] — e.g., label:bug, label:enhancement, or blank for all open issues"
allowed-tools: [Skill(github-sync), Skill(verify-and-ship), Task, TaskCreate, TaskUpdate, TaskList, TaskGet, Bash, Read, Grep, Glob]
---

# Dispatch Issues

Sync open GitHub issues into the task list and dispatch parallel agents to work on independent issues.

## What This Command Does

1. **Sync** open issues from GitHub into the task list (via `github-sync`)
2. **Analyze** dependencies between issues (labels, milestones, references)
3. **Dispatch** parallel agents for independent issues
4. **Monitor** progress and report results

## Step 1: Sync Issues

<task_list>

- [ ] Parse arguments for filters:
  - `label:<name>` — filter by label (e.g., `label:bug`)
  - No arguments — sync all open issues
- [ ] Invoke the `github-sync` skill to pull issues into the task list:
  ```
  skill: github-sync
  ```
  Tell the skill: "Sync open issues to the task list" with the appropriate label filter if provided.
  The skill will run `sync-issues-to-tasks.sh` internally and create tasks via `TaskCreate` for each new issue, deduplicating by issue number.
- [ ] Report: N new tasks created, M already existed (skipped)

</task_list>

## Step 2: Analyze Dependencies

<task_list>

- [ ] Read each issue task's description for dependency signals:
  | Signal | Interpretation |
  |--------|---------------|
  | "depends on #N" in body | `addBlockedBy` the task for issue #N |
  | "blocks #N" in body | `addBlocks` the task for issue #N |
  | Same milestone, ordered numbers | Suggest sequential ordering |
  | `priority` or `P0`/`P1` labels | Process higher priority first |
  | `good first issue` label | Independent, good for parallel |
  | `duplicate` label | Skip, do not dispatch |
  | `wontfix` label | Skip, do not dispatch |
- [ ] Set task dependencies with `TaskUpdate(addBlockedBy: [...])` where detected
- [ ] Identify independent issues (no blockedBy, not skipped) as dispatch candidates
- [ ] Display dependency analysis for user confirmation

</task_list>

## Step 3: Dispatch Agents

<task_list>

- [ ] For each independent issue task, spawn a parallel agent:

<agent_task>

```
Task(
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: """
## Assignment: Fix Issue #[number]

Task ID: [task_id]

### Issue Details
[full issue description from task]

### Process
1. TaskUpdate(taskId: "[task_id]", status: "in_progress")
2. Read the issue description carefully
3. Explore the codebase to understand the relevant code
4. Implement the fix or feature described in the issue
5. Run any available tests to verify
6. Stage and commit changes with message: "fix: [issue title] (#[number])"
   (or "feat:" for enhancements)
7. TaskUpdate(taskId: "[task_id]", status: "completed")

### Rules
- Stay focused on THIS issue only
- Follow existing code patterns and conventions
- Read CLAUDE.md for project-specific guidance
- If the issue is unclear or blocked, update the task with a note and mark completed
- Do not create PRs — the verify-and-ship skill handles that
""",
  description: "Issue #[number]: [title]"
)
```

</agent_task>

- [ ] Spawn all independent issue agents in parallel (single message with multiple Task calls)
- [ ] For blocked issues, spawn agents as their dependencies complete

</task_list>

## Step 4: Monitor and Report

<task_list>

- [ ] Poll `TaskList` to track progress
- [ ] As issue tasks complete, check for newly unblocked tasks and dispatch agents
- [ ] When all dispatched tasks complete, generate summary:

```markdown
## Issue Dispatch Report

| Issue | Title | Status | Agent Result |
|-------|-------|--------|-------------|
| #12 | Fix login timeout | Completed | Fixed in auth.ts |
| #15 | Add dark mode | Completed | Added theme toggle |
| #18 | API rate limiting | Blocked | Waiting on #12 |
| #20 | Duplicate of #12 | Skipped | duplicate label |

### Summary
- Dispatched: N issues
- Completed: N
- Blocked: N
- Skipped: N

### Next Steps
- Invoke `skill: verify-and-ship` in auto-ship mode to create PRs for completed work
- Resolve blocked issues manually or re-dispatch after dependencies complete
```

</task_list>

## Rules

- **Use github-sync for issue ingestion** — do not manually parse `gh issue list`
- **Respect dependency signals** — issues referencing other issues should be ordered
- **Skip duplicates and wontfix** — do not dispatch agents for these labels
- **Agents do not create PRs** — the `verify-and-ship` skill handles PR creation separately
- **Follow /dispatch conventions** — task creation, agent spawning, and monitoring patterns
- **Parallel by default** — independent issues run concurrently
- **Report at the end** — always produce a summary of what was dispatched and outcomes
