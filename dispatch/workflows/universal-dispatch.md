# Universal Dispatch Workflow

<required_reading>
- /Users/tinnguyen/vesper-team-skills/dispatch/references/runtime-primitives.md
- /Users/tinnguyen/vesper-team-skills/dispatch/references/dependency-patterns.md
- /Users/tinnguyen/vesper-team-skills/dispatch/references/failure-recovery.md
</required_reading>

Use this workflow when you need to coordinate a complex request across multiple workers or sessions.

## Step 1: Confirm Dispatch Is Worth It

Use dispatch when:

- the work has 5+ meaningful steps
- at least two workstreams can proceed in parallel
- coordination and status tracking matter

Do not dispatch when one focused agent can finish the work directly.

## Step 2: Choose the Shared Ledger

Pick exactly one:

- native task system
- workspace app task system
- shared markdown / JSON board

Every worker must update the same ledger.

## Step 3: Capture the Target Outcome

Write down:

- what must be delivered
- how success will be checked
- what files or systems are risky
- what constraints cannot be violated

## Step 4: Decompose the Work

Create 3-10 tasks.

Each task should include:

- `subject`
- `outcome`
- `files`
- `blockedBy`
- `owner`
- `evidence`

If two tasks edit the same fragile surface, keep them serialized.

## Step 5: Shape the Dependency Graph

Use the simplest graph that matches the work:

- linear chain for tightly coupled sequences
- fork for one foundation and several parallel branches
- diamond for parallel branches that must reconverge
- independent parallel for completely separate work

Verify:

- no circular dependencies
- no hidden blockers
- no overlapping ownership without a plan

## Step 6: Claim and Dispatch

For each ready task:

1. Claim the task
2. Record the owner
3. Give the worker the exact task description
4. Tell the worker what evidence is required to mark completion

Worker prompts should be direct and operational, not vague.

## Step 7: Monitor the Board

At each checkpoint:

- list completed tasks
- list in-progress tasks with owners
- list blocked tasks and what they are waiting on
- list newly ready tasks

If a task stalls, split it, retry it, or create a blocker-resolution task.

## Step 8: Recover Without Losing Work

When something goes wrong:

- inspect partial work first
- preserve both sides of a conflict before reverting anything
- re-plan downstream tasks explicitly
- document why a task was retried, split, skipped, or replaced

## Step 9: Publish the Dispatch Report

Close with:

```markdown
## Dispatch Report

- Completed: ...
- In progress: ...
- Blocked: ...
- Risks: ...
- Evidence: ...
- Next actions: ...
```

The next coordinator should be able to resume from this report without guessing.
