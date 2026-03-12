# Claude Code Adapter

This document adapts the universal `dispatch` protocol to Claude Code.

Treat everything here as Claude-specific implementation guidance, not as the definition of dispatch itself.

## What This Adapter Assumes

- Claude Code is available as `claude`
- The runtime supports the `TaskCreate`, `TaskUpdate`, `TaskList`, `TaskGet`, and `Task` tools
- A shared task list is selected before the session starts

For the universal workflow, read [universal-dispatch.md](/Users/tinnguyen/vesper-team-skills/dispatch/workflows/universal-dispatch.md) first.

## Setup

After installation or Team Skills sync, run the setup script once from the installed location:

```bash
~/.vesper/team-skills/dispatch/setup.sh
~/.claude/skills/dispatch/setup.sh
```

`setup.sh` auto-detects where the skill is installed. It installs:

- `cc` and `ccd` wrapper commands
- the archive hook installer

## Recommended Start Paths

### Option A: `cc` wrapper

```bash
cc
cc my-feature
cc --new big-refactor
cc --list
cc --dangerous
```

`ccd` is shorthand for `cc --dangerous`.

### Option B: Start-session script

```bash
~/.vesper/team-skills/dispatch/scripts/start-session.sh feature-auth
~/.claude/skills/dispatch/scripts/start-session.sh feature-auth
```

### Option C: Direct environment variable

```bash
CLAUDE_CODE_TASK_LIST_ID=my-project claude
```

## Pre-Flight Check

Before creating new tasks:

1. Check the active list:

```bash
echo "$CLAUDE_CODE_TASK_LIST_ID"
```

2. Inspect current tasks:

```text
TaskList()
```

3. If unrelated tasks already exist, warn before mixing work.

## Claude-Specific Primitives

| Dispatch primitive | Claude Code tool / mechanism |
|--------------------|------------------------------|
| Create task | `TaskCreate` |
| Update task | `TaskUpdate` |
| List task status | `TaskList` |
| Read full task | `TaskGet` |
| Spawn worker | `Task(...)` |
| Shared ledger | `CLAUDE_CODE_TASK_LIST_ID` + `~/.claude/tasks/<list-id>/` |

Detailed syntax lives in [task-tools-api.md](/Users/tinnguyen/vesper-team-skills/dispatch/references/task-tools-api.md).

## Claude Workflow Notes

- Use direct tool syntax in worker prompts.
- Claim the task with `TaskUpdate(... owner: "...", status: "in_progress")` before spawning.
- For tool-heavy coding, `sonnet` is the safe default. Lighter models may work for low-risk tasks; validate in your environment.
- Run validators before parallel spawning when possible:

```bash
SKILL=~/.vesper/team-skills/dispatch   # or ~/.claude/skills/dispatch
bun run "$SKILL/scripts/validate-dependency-graph.ts"
bun run "$SKILL/scripts/detect-file-conflicts.ts"
```

## Recovery Tools

If the session started without the intended shared list, use:

```bash
SKILL=~/.vesper/team-skills/dispatch   # or ~/.claude/skills/dispatch
bun run "$SKILL/scripts/migrate-session.ts" my-project
bun run "$SKILL/scripts/sync-tasks.ts" --target my-project
```

Use these only as repair tools, not as the normal workflow.

## Task Archival

The archive hook preserves task JSON files to `~/.claude/tasks-archive/`.

Preferred hook event: `SessionEnd`

The installer writes the hook using the actual installed skill path, so Team Skills and manual installs both work.

## Script Inventory

| Script | Purpose |
|--------|---------|
| `setup.sh` | Install wrappers and archive hook |
| `scripts/install-cc.sh` | Install `cc` and `ccd` into a writable bin dir |
| `scripts/start-session.sh` | Start Claude Code with a chosen task list |
| `scripts/validate-dependency-graph.ts` | Check dependency cycles and graph issues |
| `scripts/detect-file-conflicts.ts` | Find overlapping file ownership |
| `scripts/detect-stale-tasks.ts` | Find or reset stale tasks |
| `scripts/migrate-session.ts` | Move orphaned session tasks into a shared list |
| `scripts/sync-tasks.ts` | Merge multiple orphaned lists |
| `scripts/archive-tasks.ts` | Archive task lists manually |
| `hooks/install-hook.sh` | Install the archive hook |

## Troubleshooting

- `TaskList` is empty:
  Start Claude with the intended shared list, then retry.
- Subagents cannot see the same tasks:
  Confirm the parent session started with `CLAUDE_CODE_TASK_LIST_ID`.
- Tasks were created in the wrong list:
  Use `migrate-session.ts` or `sync-tasks.ts`, then restart with the right list.
