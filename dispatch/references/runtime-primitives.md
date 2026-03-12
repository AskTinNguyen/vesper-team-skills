# Runtime Primitives for Dispatch

This reference defines the minimum contract a runtime needs in order to support `dispatch`.

The core skill is portable because it depends on primitives, not product names.

## Minimum Primitives

| Primitive | Why it matters | Native example | Manual fallback |
|-----------|----------------|----------------|-----------------|
| Create task | Break work into tracked units | Built-in task create API | Add a row to `dispatch-board.md` or `dispatch-board.json` |
| Update task | Record status, owner, blockers, evidence | Built-in task update API | Edit the shared board |
| List tasks | See what is ready, blocked, or stale | Built-in task list API | Re-read the board |
| Claim owner | Prevent duplicate work | `owner` or equivalent field | Write your worker name into the board before editing |
| Declare dependencies | Prevent premature dispatch | `blockedBy` or equivalent | Maintain blocker IDs manually |
| Spawn worker | Parallelize execution | Native subagent/session tool | Open another agent/session and give it one task |
| Verify output | Decide whether a task is truly done | Tests, screenshots, docs, diffs | Same, attached to the board |
| Recover failure | Retry, split, or re-plan without losing work | Retry/update primitives | Snapshot work, update board, then reassign |

## Adapter Shapes

### 1. Native Task Runtime

Use this when the host already exposes task CRUD and worker spawning.

Checklist:

- There is one shared task ledger for all workers.
- A worker can claim a task before starting.
- The coordinator can list all tasks and blockers at any time.
- A worker can mark completion with evidence.

### 2. Shared App Runtime

Use this when the host is not Claude Code but still has agent sessions, IPC, or persistent workspace state.

Map the dispatch protocol onto whatever the runtime calls its primitives:

- task record
- status update
- owner / assignee
- blocker list
- spawn session / spawn agent
- completion evidence

The names can differ. The behavior must stay the same.

### 3. Manual or Mixed Runtime

Use this when the host has no native task tools.

Create a shared board in the repo:

```markdown
| ID | Subject | Owner | Status | Blocked By | Files | Evidence |
|----|---------|-------|--------|------------|-------|----------|
| 1 | Map schema changes | planner | done | - | db/schema.sql | reviewed |
| 2 | Add migration | worker-a | in_progress | 1 | db/migrations/* | tests pending |
| 3 | Update docs | worker-b | pending | 2 | docs/db.md | - |
```

Status suggestions:

- `pending`
- `in_progress`
- `blocked`
- `done`

## Capability Tiers for Workers

Use capability tiers instead of vendor-specific model names in the core plan:

| Tier | Best for |
|------|----------|
| `planner` | Architecture, sequencing, tricky tradeoffs |
| `builder` | Most coding, testing, integration work |
| `lightweight` | Docs, small cleanup, low-risk follow-up |

Each runtime can map those tiers to its own models or agents.

## Adapter Readiness Check

You are ready to dispatch when you can answer all of these:

1. Where is the single shared task ledger?
2. How does a worker claim a task?
3. How are blockers recorded?
4. How do you launch a parallel worker?
5. How does a worker prove completion?
6. How do you preserve partial work before retrying or reassigning?

If any answer is missing, fix the adapter first instead of dispatching blindly.
