# GitHub-to-Task Mapping Reference

## PR Mapping

| GitHub PR Field | Task Field | Notes |
|-----------------|------------|-------|
| `number` | Description metadata (`pr_number=N`) | Used for deduplication |
| `title` | Subject (`PR #N: title`) | Prefixed with PR number |
| `body` | Description body | Included after metadata header |
| `author.login` | Description (`Author: @login`) | For attribution |
| `headRefName` | Description (`Branch: head -> base`) | For context |
| `baseRefName` | Description (`Branch: head -> base`) | For context |
| `labels[].name` | Description (`Labels: a, b`) | Comma-separated |
| `url` | Description (`GitHub PR: url`) | Direct link |
| `isDraft` | No task change if draft | Drafts are synced but not flagged |
| `reviewDecision` | Description (`Review: status`) | APPROVED, CHANGES_REQUESTED, etc. |
| `state` (MERGED) | Task status -> completed | Auto-complete on merge |
| `state` (CLOSED) | Task status -> completed | With "closed without merge" note |

## Issue Mapping

| GitHub Issue Field | Task Field | Notes |
|--------------------|------------|-------|
| `number` | Description metadata (`issue_number=N`) | Used for deduplication |
| `title` | Subject (`Issue #N: title`) | Prefixed with issue number |
| `body` | Description body | Included after metadata header |
| `author.login` | Description (`Author: @login`) | For attribution |
| `labels[].name` | Description (`Labels: a, b`) | Comma-separated |
| `milestone.title` | Description (`Milestone: name`) | For grouping |
| `assignees[].login` | Description (`Assignees: @a, @b`) | For tracking |
| `url` | Description (`GitHub Issue: url`) | Direct link |

## Deduplication Strategy

Tasks are deduplicated by checking for the metadata marker in task descriptions:

- PRs: `pr_number=<number>` anywhere in the description
- Issues: `issue_number=<number>` anywhere in the description

The sync scripts scan all task JSON files in the active task directory for these markers before creating new tasks. This avoids duplicates across multiple sync runs.

## Status Transitions

```
PR opened     -> Task created (pending)
PR approved   -> Task note updated
PR merged     -> Task completed
PR closed     -> Task completed (with note)
PR changes    -> Task flagged for attention
requested
```

```
Issue opened  -> Task created (pending)
Issue closed  -> Detected by reconcile, flagged
```

## Label-to-Priority Mapping (Convention)

These labels, when present, suggest task ordering:

| Label | Suggested Priority |
|-------|-------------------|
| `critical`, `P0` | Immediate — address first |
| `bug` | High — before features |
| `enhancement` | Normal |
| `good first issue` | Low — good for new agents |
| `wontfix` | Skip — do not create task |
| `duplicate` | Skip — do not create task |

The sync scripts do not enforce priority ordering but include labels in task descriptions so orchestrating agents can make decisions.

## Reconciliation Rules

1. **New PR/Issue found, no matching task** -> Create task
2. **PR merged, task still pending/in_progress** -> Mark task completed
3. **PR closed without merge, task exists** -> Mark task completed with note
4. **Issue closed, task exists** -> Flag for review (issues may need verification)
5. **Task exists, PR/issue not found (deleted)** -> Flag as orphaned
6. **Task completed, PR still open** -> No action (work may be done differently)
