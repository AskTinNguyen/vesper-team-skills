---
description: Initialize a new feature with task coordination using the Dispatch skill
argument-hint: <feature-name-or-issue>
---

# Start New Feature

Initialize a feature development environment using the **Dispatch** skill for multi-agent task coordination.

## Arguments

- `$ARGUMENTS` = feature name OR GitHub issue reference (e.g., `search-skills` or `#48` or `48`)

## Execution Steps

### 1. Parse Input

Determine if input is an issue number or feature name:

```bash
# If starts with # or is pure number, it's an issue reference
if [[ "$ARGUMENTS" =~ ^#?[0-9]+$ ]]; then
  ISSUE_NUM="${ARGUMENTS#\#}"
  # Fetch issue title for context
  ISSUE_INFO=$(gh issue view "$ISSUE_NUM" --json title,body,labels -q '{title: .title, body: .body[0:500], labels: [.labels[].name]}' 2>/dev/null)
  FEATURE_NAME="issue-$ISSUE_NUM"
else
  FEATURE_NAME="$ARGUMENTS"
  ISSUE_NUM=""
fi
```

### 2. Start Coordinated Session with Dispatch

**Use `ccd` (Claude Code with Dispatch + dangerous mode):**

```bash
# Start new terminal or tmux session
tmux new-session -d -s "$FEATURE_NAME" -c "$(pwd)"
tmux send-keys -t "$FEATURE_NAME" "ccd $FEATURE_NAME" Enter
```

This automatically:
- Creates task list at `~/.claude/tasks/$FEATURE_NAME/`
- Sets `CLAUDE_CODE_TASK_LIST_ID` environment variable
- Enables dangerous mode (skip permission prompts)
- Auto-archives previous task list

### 3. Pre-Flight Check (from Dispatch skill)

Before creating tasks, verify:

```bash
echo "List: $CLAUDE_CODE_TASK_LIST_ID"
TaskList
```

If tasks exist, warn before proceeding.

### 4. Load Issue Context (if applicable)

If working from a GitHub issue:

```markdown
## Issue Context

**Issue:** #$ISSUE_NUM
**Title:** $ISSUE_TITLE
**Labels:** $ISSUE_LABELS

**Description:**
$ISSUE_BODY
```

### 5. Decompose into Tasks

**Use Dispatch's TaskCreate for each sub-task:**

```
TaskCreate(
  subject: "Imperative title for sub-task 1",
  description: "Requirements:\n- item\n- item\n\nFiles: src/foo.ts",
  activeForm: "Implementing sub-task 1"
)
```

**Guidelines (from Dispatch skill):**
- 3-10 discrete tasks
- Each task: atomic, independent files, testable
- Include `Files:` in description for conflict detection
- Tasks should be 30min+ of work (avoid over-decomposition)

### 6. Set Dependencies

```
TaskUpdate(taskId: "2", addBlockedBy: ["1"])
TaskUpdate(taskId: "3", addBlockedBy: ["1"])
TaskUpdate(taskId: "4", addBlockedBy: ["2", "3"])
```

### 7. Validate Before Spawning

```bash
SKILL=~/.claude/skills/dispatch
bun run $SKILL/scripts/validate-dependency-graph.ts
bun run $SKILL/scripts/detect-file-conflicts.ts
```

### 8. Spawn Parallel Agents

For each ready task (no blockedBy or all blockedBy completed):

```
TaskUpdate(taskId: "1", status: "in_progress", owner: "agent-1")

Task(
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: """
## Your Assignment

Task ID: 1
Subject: [task subject]

[Full task description]

## On Completion

Mark complete: TaskUpdate(taskId: "1", status: "completed")
""",
  description: "Task 1: [subject]"
)
```

**Model selection:**
| Model | Use For |
|-------|---------|
| opus | Architecture, complex logic |
| sonnet | Features, tests, integrations |

### 9. Monitor Progress

```bash
TaskList                                          # Quick status
bun run $SKILL/scripts/task-dashboard.ts --watch  # Visual dashboard
```

### 10. Report on Completion

```markdown
## Progress: X/Y tasks

**Completed:** 1, 2, 3
**In Progress:** 4, 5
**Blocked:** 6 (waiting: 4, 5)
**Ready:** 7
```

## Quick Start Example

```bash
# From issue number
/start-new-feature 48

# From feature name
/start-new-feature search-installed-skills
```

## Success Criteria

- [ ] Task list created via `ccd $FEATURE_NAME`
- [ ] Issue context loaded (if applicable)
- [ ] Tasks decomposed with TaskCreate
- [ ] Dependencies set with TaskUpdate
- [ ] Dependency graph validated
- [ ] Agents spawned for ready tasks
- [ ] All tasks completed
- [ ] Changes committed

## Related Skills

- **Dispatch** - Core skill for task coordination (`/dispatch`)
- `using-git-worktrees` - For isolated workspace setup
- `verification-before-completion` - For final verification

## Anti-Patterns (from Dispatch)

- ❌ Starting Claude without `CLAUDE_CODE_TASK_LIST_ID` set
- ❌ Tasks < 30 min work (over-decomposition)
- ❌ Vague descriptions (under-specification)
- ❌ Circular dependencies (validate first)
- ❌ Spawning blocked tasks (check blockedBy)
- ❌ Parallel tasks on same files (serialize via blockedBy)
