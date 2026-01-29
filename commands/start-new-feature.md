---
description: Initialize a new feature with task coordination and parallel agent dispatch
argument-hint: <feature-name-or-issue>
---

# Start New Feature

Initialize a feature development environment with task coordination and parallel agent dispatch.

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

### 2. Create Task Environment

Start a new terminal session with task coordination:

```bash
# Create task list for this feature
ccd "$FEATURE_NAME"
```

This creates:
- Task list at `~/.claude/tasks/$FEATURE_NAME/`
- Claude Code session with dangerous mode (skip permission prompts)

### 3. Set Up Context

If working from a GitHub issue, load the issue context:

```markdown
## Issue Context (if applicable)

**Issue:** #$ISSUE_NUM
**Title:** $ISSUE_TITLE
**Labels:** $ISSUE_LABELS

**Description:**
$ISSUE_BODY
```

### 4. Create Implementation Plan

Before coding, create a focused plan:

1. **Understand the scope** - Read the issue or feature description
2. **Identify affected files** - Search codebase for relevant code
3. **Break into tasks** - Split into 2-5 independent sub-tasks
4. **Define success criteria** - What does "done" look like?

Write plan to `.claude/tasks/$FEATURE_NAME/PLAN.md`

### 5. Dispatch Parallel Agents

For each independent sub-task, dispatch an agent:

```
Task("Sub-task 1: [specific scope]")
Task("Sub-task 2: [specific scope]")
...
```

**Dispatch rules:**
- One agent per independent problem domain
- Each agent gets specific scope and clear goal
- Agents should not edit the same files
- Use `dispatching-parallel-agents` skill for guidance

### 6. Monitor and Integrate

1. Wait for all agents to complete
2. Review each agent's summary
3. Check for conflicts between changes
4. Run tests to verify
5. Commit with conventional commit message

## Quick Start Example

```bash
# From issue number
/start-new-feature 48

# From feature name  
/start-new-feature search-installed-skills
```

## Success Criteria

- [ ] Task list created at `~/.claude/tasks/$FEATURE_NAME/`
- [ ] Implementation plan written
- [ ] Sub-tasks identified and dispatched
- [ ] All agents completed successfully
- [ ] Tests pass
- [ ] Changes committed

## Related Skills

- `dispatching-parallel-agents` - For parallel agent dispatch patterns
- `using-git-worktrees` - For isolated workspace setup
- `verification-before-completion` - For final verification
