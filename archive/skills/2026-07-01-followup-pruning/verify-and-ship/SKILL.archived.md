---
name: verify-and-ship
description: Verify agent work output, commit, push, and create PRs — or review existing PRs and fix/flag issues. Use when shipping work produced by other agents, verifying uncommitted changes, batch-reviewing PRs, or acting as the final quality gate before merge. Triggers on "verify and push", "be the verifier", "check and create PRs", "review and ship", "ship agent work", "verify and commit".
alwaysAllow:
  - TaskCreate
  - TaskUpdate
  - TaskList
  - TaskGet
  - Task
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
---

# Verify and Ship

Act as the verification and shipping layer for multi-agent work. Detect uncommitted changes, run checks, commit, push, create PRs, and manage the review-to-merge pipeline.

## Overview

Three modes cover the full shipping pipeline:

| Mode | Purpose | When to Use |
|------|---------|-------------|
| **Auto-Ship** | Verify -> commit -> push -> create PR | Agent left uncommitted work |
| **Review-Gate** | Pull PRs -> review -> fix or flag | PRs awaiting review |
| **Status-Update** | Follow review agent -> update tasks -> flag | Tracking review progress |

## Pre-Flight

```bash
# 1. Verify git state
git status
git remote -v

# 2. Verify task coordination
echo "Task list: $CLAUDE_CODE_TASK_LIST_ID"

# 3. Verify gh CLI
gh auth status
```

## Mode 1: Auto-Ship

Detect uncommitted agent work, verify it, commit, push, and create PRs.

**Behavior loop:**

1. **Detect** — Check for uncommitted changes, untracked files, unpushed commits
2. **Verify** — Run tests, linting, type checks
3. **Fix** — Auto-fix trivial issues (formatting, lint fixes)
4. **Commit** — Stage and commit with conventional commit message
5. **Push** — Push branch to remote
6. **PR** — Create PR if none exists for this branch
7. **Report** — Update task status, output summary
8. **Loop** — Check for more uncommitted work

**Starting auto-ship:**

```
I need you to act as a verifier and shipper.

Mode: Auto-Ship
Task list: $CLAUDE_CODE_TASK_LIST_ID

Check for uncommitted agent work:
1. Run scripts/check-agent-output.sh to detect uncommitted changes
2. For each set of changes:
   a. Review the diff for correctness
   b. Run tests/checks via scripts/verify-and-push.sh
   c. If checks pass: commit, push, create PR
   d. If checks fail and fixable: fix, then commit
   e. If checks fail and not fixable: flag for human with [NEEDS FIX] task
3. Update task statuses as you ship
4. Loop until no more uncommitted work

Never skip verification. Every commit must pass checks first.
```

**Using check-agent-output.sh:**

```bash
# Detect uncommitted work
bash scripts/check-agent-output.sh

# Output: JSON with uncommitted files, untracked files, unpushed commits
```

**Using verify-and-push.sh:**

```bash
# Verify, commit, and push
bash scripts/verify-and-push.sh --message "feat: add user auth" --branch feature/auth

# Dry run (verify only, no commit)
bash scripts/verify-and-push.sh --dry-run

# Skip PR creation
bash scripts/verify-and-push.sh --message "fix: typo" --no-pr
```

### Auto-Ship Decision Table

| Situation | Action |
|-----------|--------|
| Clean diff, tests pass | Commit -> push -> PR |
| Lint errors only | Auto-fix -> commit -> push -> PR |
| Test failures, obvious fix | Fix -> verify again -> commit |
| Test failures, unclear cause | Create `[NEEDS FIX]` task, skip |
| Merge conflicts | Create `[CONFLICT]` task, skip |
| No changes detected | Report clean, move to next task |

## Mode 2: Review-Gate

Pull PRs from GitHub, dispatch reviews, fix what's fixable, flag what needs human attention.

**Behavior loop:**

1. **Sync** — Pull open PRs into task list (via `github-sync`)
2. **Review** — Dispatch `/workflows:review` per PR
3. **Triage** — For each review result:
   - Clean: approve PR
   - Fixable issues: apply fixes, push, re-request review
   - Unfixable: create `[HUMAN]` task
4. **Report** — Summary of reviewed, fixed, and flagged PRs

**Starting review-gate:**

```
I need you to act as a verifier.

Mode: Review-Gate
Task list: $CLAUDE_CODE_TASK_LIST_ID

1. Sync open PRs using github-sync
2. For each PR task:
   a. Dispatch /workflows:review for the PR
   b. If review passes: add "Approved" note to task
   c. If review finds fixable issues: check out branch, fix, push, re-review
   d. If review finds unfixable issues: create [HUMAN] task
3. Use /workflows:bulk-review for batch mode if >3 PRs

Never merge PRs. Only review, fix, and flag.
```

**Composing with existing review skills:**

```
# Single PR review
Skill(workflows:review, args: "PR #42")

# Batch review
Skill(workflows:bulk-review)
```

## Mode 3: Status-Update

Follow a review agent's progress and keep the task list current.

**Behavior loop:**

1. **Check** — TaskList for review/verification task statuses
2. **Update** — Sync task statuses with actual outcomes
3. **Flag** — Create tasks for items needing human attention
4. **Report** — Progress summary

This mode is lighter than the other two — it only updates task metadata, never touches code or PRs.

**Starting status-update:**

```
I need you to act as a verifier in status-update mode.

Mode: Status-Update
Task list: $CLAUDE_CODE_TASK_LIST_ID

Follow review and verification tasks:
1. Check for completed review tasks
2. Update related implementation tasks based on review outcomes
3. Flag any issues that need human attention
4. Report status each cycle

Never do reviews or fixes yourself. Only update task statuses.
```

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/check-agent-output.sh` | Detect uncommitted changes, untracked files, unpushed commits |
| `scripts/verify-and-push.sh` | Run checks, commit, push, optionally create PR |

## Composing with Other Skills

| Skill | Usage |
|-------|-------|
| `github-sync` | Review-gate mode uses sync-prs-to-tasks.sh to populate review queue |
| `/workflows:review` | Review-gate dispatches per-PR reviews |
| `/workflows:bulk-review` | Review-gate batch mode for multiple PRs |
| `agent-supervisor` | Supervisor may dispatch verify-and-ship tasks |
| `/dispatch` | Task conventions and session management |

## Anti-Patterns

- **Shipping without verification** — Always run checks before committing
- **Force-pushing** — Never use `--force`; create a new commit instead
- **Merging PRs** — Verifier creates and reviews PRs but does not merge (human gate)
- **Skipping the task list** — Always update task statuses when shipping
- **Ignoring test failures** — If tests fail, fix or flag; never skip

## References

- `references/verification-modes.md` — Detailed mode workflows and decision trees
