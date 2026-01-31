---
name: tasklist-env
description: This skill should be used when checking, verifying, or switching the current task list environment. It applies when the user asks about the active task list, wants to see available environments, needs to switch between task lists, or wants to view tasks in a specific environment. Triggers on "check task list", "which task environment", "switch task list", "current tasks", "task environment", "list environments", "show tasks".
---

# Task List Environment Manager

Check, verify, and switch between Claude Code task list environments stored in `~/.claude/tasks/`.

## Quick Start

Run the script at `scripts/tasklist_env.sh` relative to this skill's directory.

```bash
# Show current environment status
bash scripts/tasklist_env.sh status

# List all available environments
bash scripts/tasklist_env.sh list

# Switch to a different environment
bash scripts/tasklist_env.sh switch <env-name>

# Show tasks in the current or a specific environment
bash scripts/tasklist_env.sh tasks [env-name]
```

## Workflow

### 1. Check Current Environment

When the user asks about the current task list or environment:

```bash
bash "$(dirname "$0")/../scripts/tasklist_env.sh" status
```

This reports:
- The environment set in `.current-list-id`
- The `CLAUDE_TASK_LIST` environment variable (if set)
- Any discrepancy between the two
- Task summary (pending/in-progress/completed counts)

### 2. List Available Environments

When the user wants to see all environments:

```bash
bash "$(dirname "$0")/../scripts/tasklist_env.sh" list
```

Shows all task list directories under `~/.claude/tasks/` with task counts. The active environment is marked with `*`. Archived environments under `~/.claude/tasks-archive/` are listed separately.

### 3. Switch Environment

When the user wants to switch to a different task list:

```bash
bash "$(dirname "$0")/../scripts/tasklist_env.sh" switch <env-name>
```

Updates `.current-list-id` and shows the task summary for the new environment. Warns if `CLAUDE_TASK_LIST` env var differs.

### 4. View Tasks

When the user wants to see tasks in an environment:

```bash
bash "$(dirname "$0")/../scripts/tasklist_env.sh" tasks [env-name]
```

Lists all tasks with their status (`[ ]` pending, `[~]` in progress, `[x]` completed) and blocking dependencies.

## Key Paths

- **Tasks root**: `~/.claude/tasks/`
- **Current list ID**: `~/.claude/tasks/.current-list-id`
- **Archive**: `~/.claude/tasks-archive/`
- **Task files**: `~/.claude/tasks/<env-name>/*.json` (each task is a numbered JSON file)

## Scripts

### `scripts/tasklist_env.sh`

Bash script with subcommands: `status`, `list`, `switch`, `tasks`. Requires `python3` for JSON parsing of task files.
