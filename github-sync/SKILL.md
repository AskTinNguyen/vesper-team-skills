---
name: github-sync
description: Synchronize GitHub PRs and issues into the Claude Code task list. Use when orchestrating multi-agent work that maps to GitHub artifacts — pulling open PRs into tasks, tracking issue status, or reconciling merged PRs with completed tasks. Triggers on "pull PRs into task list", "sync issues", "populate tasks from GitHub", "reconcile tasks with GitHub", "PR status check".
alwaysAllow:
  - TaskCreate
  - TaskUpdate
  - TaskList
  - TaskGet
  - Bash
  - Read
  - Grep
  - Glob
---

# GitHub Sync

Synchronize GitHub PRs and issues with the Claude Code task list, enabling multi-agent orchestration against real repository state.

## Overview

This skill bridges GitHub and the Claude Code task system. It pulls PRs and issues into the task list (deduplicating by number), checks merge/review status, and reconciles state changes bidirectionally. Other orchestration skills (`agent-supervisor`, `verify-and-ship`, dispatch commands) consume this as a shared utility layer.

## Pre-Flight

Before syncing, verify the environment:

```bash
# 1. Confirm gh CLI is authenticated
gh auth status

# 2. Confirm task coordination is enabled
echo "Task list: $CLAUDE_CODE_TASK_LIST_ID"

# 3. Confirm repo context
gh repo view --json nameWithOwner -q '.nameWithOwner'
```

If `CLAUDE_CODE_TASK_LIST_ID` is empty, start Claude with `cc <list-name>` (see `/dispatch`).

## Quick Start

```bash
SKILL_DIR="$(dirname "$0")"  # adjust to skill install path

# Sync open PRs into task list
bash "$SKILL_DIR/scripts/sync-prs-to-tasks.sh"

# Sync open issues into task list
bash "$SKILL_DIR/scripts/sync-issues-to-tasks.sh"

# Check PR merge/review status and update tasks
bash "$SKILL_DIR/scripts/pr-status-check.sh"

# Full bidirectional reconciliation
bash "$SKILL_DIR/scripts/reconcile.sh"
```

## Modes

### 1. Sync PRs to Tasks

Pull all open PRs (or a filtered set) into the task list. Each PR becomes one task with PR metadata stored for deduplication.

```bash
# All open PRs
bash scripts/sync-prs-to-tasks.sh

# Filter by label
bash scripts/sync-prs-to-tasks.sh --label "needs-review"

# Filter by author
bash scripts/sync-prs-to-tasks.sh --author "@me"
```

**Task format created:**

```
Subject: "PR #42: Add user authentication"
Description: |
  GitHub PR: https://github.com/owner/repo/pull/42
  Author: @username
  Branch: feature/auth -> main
  Labels: enhancement, needs-review

  [PR description body]

  ---
  Metadata: pr_number=42
ActiveForm: "Reviewing PR #42"
```

**Deduplication:** Tasks with matching `pr_number=N` in the description are skipped on subsequent syncs.

### 2. Sync Issues to Tasks

Pull open issues into the task list, one task per issue.

```bash
# All open issues
bash scripts/sync-issues-to-tasks.sh

# Filter by label
bash scripts/sync-issues-to-tasks.sh --label "bug"

# Filter by milestone
bash scripts/sync-issues-to-tasks.sh --milestone "v2.0"
```

**Deduplication:** Tasks with matching `issue_number=N` in the description are skipped.

### 3. PR Status Check

Update task statuses based on current PR state (merged, approved, changes requested, etc.).

```bash
bash scripts/pr-status-check.sh
```

**State mapping:**

| PR State | Task Action |
|----------|-------------|
| Merged | Mark task completed |
| Approved | Add note: "Approved, ready to merge" |
| Changes requested | Add note: "Changes requested by @reviewer" |
| Draft | No change (keep pending) |
| Closed without merge | Mark task completed with note |

### 4. Reconcile

Full bidirectional sync: pull new PRs/issues, update statuses, flag discrepancies.

```bash
bash scripts/reconcile.sh

# Dry run — show what would change without modifying tasks
bash scripts/reconcile.sh --dry-run
```

## Composing with Other Skills

This skill is consumed by other orchestration skills:

| Consumer | Usage |
|----------|-------|
| `agent-supervisor` (PR tracker mode) | Calls `pr-status-check.sh` on each polling cycle |
| `verify-and-ship` (review-gate mode) | Calls `sync-prs-to-tasks.sh` to populate review queue |
| `/dispatch-issues` command | Calls `sync-issues-to-tasks.sh` then dispatches agents |
| `/dispatch-tests` command | Uses reconcile to track test-related PRs |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/sync-prs-to-tasks.sh` | Pull open PRs into task list (dedup by PR number) |
| `scripts/sync-issues-to-tasks.sh` | Pull open issues into task list (dedup by issue number) |
| `scripts/pr-status-check.sh` | Check PR merge/review status, update task states |
| `scripts/reconcile.sh` | Bidirectional reconciliation (all of the above + flag discrepancies) |

## References

- `references/github-task-mapping.md` — Detailed mapping rules between GitHub entities and task fields
