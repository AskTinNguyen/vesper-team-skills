---
name: start-new-feature
description: Understand the codebase deeply, then decompose and orchestrate parallel feature development
argument-hint: "[feature name, GitHub issue (#48), or plan file path (plans/feat-xyz.md)]"
---

# Start New Feature

<command_purpose> The definitive entry point for feature development. Runs parallel research agents to deeply understand the codebase BEFORE decomposing work, then orchestrates parallel implementation agents with proper isolation, dependency management, and quality gates. </command_purpose>

<role>Principal Engineer and Feature Architect who understands systems holistically, decomposes work along natural fault lines, and orchestrates parallel execution without conflicts</role>

## Input

<feature_input> #$ARGUMENTS </feature_input>

**If the feature input above is empty, ask the user:** "What feature would you like to build? Provide a feature name, GitHub issue number (#48), or path to a plan file (plans/feat-xyz.md)."

Do not proceed until you have a clear feature input.

## Phase 0: Parse Input and Gather Context

<thinking>
Determine the input type and load all available context before any decisions.
The input could be: (1) a plan file path, (2) a GitHub issue number, or (3) a feature name/description.
</thinking>

Detect input type automatically:
- **Plan file** (contains `/` or `.md`): Read the plan completely. Extract feature description, acceptance criteria, technical approach, and referenced files. **Skip Phase 1 research** — plans from `/workflows:plan` already contain research findings.
- **GitHub issue** (starts with `#` or is digits): Fetch with `gh issue view` including title, body, labels, and first 3 comments.
- **Feature name** (everything else): Use directly. If 1-3 words, ask for a brief description.

## Phase 1: Parallel Codebase Research

<critical_requirement> NEVER decompose a feature without first understanding the codebase. Shallow decomposition leads to conflicting tasks, missed patterns, and rework. Run ALL research agents in parallel BEFORE any task creation. </critical_requirement>

<ultrathink_instruction> Before spawning research agents, spend maximum cognitive effort to identify WHAT you need to learn about the codebase. What architectural patterns matter? What files will be touched? What conventions must be followed? What could go wrong if agents work in parallel on the wrong boundaries? </ultrathink_instruction>

<parallel_tasks>

Run ALL four research agents simultaneously:

1. **Task codebase-analyst(feature_description)**
   - Identify all files, modules, and directories relevant to this feature
   - Map existing code that will be modified or extended
   - Find similar features already implemented (study their structure)
   - List all imports, exports, and public APIs in the affected area
   - Output: File map with line counts, modification probability, and coupling assessment

2. **Task architecture-reviewer(feature_description)**
   - Determine the architectural layer(s) this feature touches (main process, renderer, shared, IPC)
   - Identify data flow paths (user action -> IPC -> business logic -> persistence -> UI update)
   - Find boundary interfaces where new code must integrate
   - Check for architectural constraints (permission modes, encryption, session isolation)
   - Review CLAUDE.md for relevant conventions and recent changes
   - Output: Architecture context document with integration points and constraints

3. **Task pattern-matcher(feature_description)**
   - Find the 2-3 most similar features already in the codebase
   - Extract their implementation patterns (file structure, naming, testing approach)
   - Identify shared utilities, hooks, or base classes to reuse
   - Note any anti-patterns or tech debt in similar features to avoid repeating
   - Output: Pattern guide with concrete examples and file references

4. **Task dependency-mapper(feature_description)**
   - Map which files import from which other files in the affected area
   - Identify shared state (Jotai atoms, context providers, IPC channels)
   - Find potential conflict zones where parallel agents might clash
   - Determine the natural serialization points (what MUST be done first)
   - Check for database/schema changes, migration needs, or config changes
   - Output: Dependency graph with conflict zones highlighted

</parallel_tasks>

### Research Synthesis

<thinking>
After all research agents complete, synthesize their findings into a unified understanding.
Key questions to answer:
- What is the natural decomposition boundary? (by layer? by feature slice? by data flow?)
- Which files are "hot" (touched by multiple potential tasks) and need serialization?
- What existing patterns must be followed for consistency?
- What is the minimum set of changes needed?
</thinking>

Combine agent findings into a **Feature Context Brief** covering: affected areas, integration points, patterns to follow, conflict zones, and key constraints. This brief feeds directly into Phase 2 — do not pause for user validation here (the task graph in Phase 3 serves as the approval checkpoint).

## Phase 2: Feature Complexity and Environment Setup

### 2a. Auto-Recommend Feature Tier

Based on the research findings, recommend a tier to the user:

| Signal from Research | Recommended Tier |
|---------------------|-----------------|
| 1-3 files modified, single module, no shared state conflicts | **Quick** (1-2 tasks) |
| 4-10 files, 2-3 modules, some integration points | **Standard** (3-7 tasks) |
| 10+ files, cross-cutting concerns, schema changes, new subsystem | **Major** (7+ tasks) |

Use the **AskUserQuestion tool** with the recommended tier marked:

**Question:** "Based on research, this looks like a [recommended] feature. Agree or adjust?"

**Options:**
1. **Quick Feature** -- Single-agent, no dispatch. For: focused changes, bug fixes.
2. **Standard Feature** (Recommended if matched) -- Parallel dispatch with TaskCreate. For: most multi-file features.
3. **Major Feature** -- Dispatch + worktree isolation + phased execution. For: architectural changes, new subsystems.

### 2b. Environment Setup

**All tiers:** Check current branch. If on default branch, create `feat/[feature-name]`. If on a feature branch, ask whether to continue or create new.

**Standard and Major tiers additionally:** Set up task coordination with TaskCreate/TaskUpdate.

**Major tier additionally:** Offer worktree isolation via `skill: git-worktree` for parallel development without interference.

## Phase 3: Task Decomposition

<ultrathink_instruction>
This is the most critical phase. Spend MAXIMUM cognitive effort on decomposition.

Think about:
- What are the NATURAL boundaries in this feature? (Not artificial splits like "frontend" and "backend" -- think about what can truly run independently)
- Which tasks produce artifacts that other tasks consume? (These are real dependencies, not theoretical ones)
- Where are the conflict zones from the dependency-mapper? (Tasks touching the same files MUST be serialized)
- What is the critical path? (The longest chain of dependent tasks determines total time)
- Can any tasks be merged to reduce coordination overhead? (Fewer well-scoped tasks beat many tiny tasks)
- What does each agent need to know to succeed WITHOUT asking questions? (Context completeness)

Anti-patterns to avoid:
- Splitting by file instead of by behavior (leads to incomplete features per task)
- Creating tasks that are too small (<30 min work = over-decomposition)
- Vague descriptions that require agents to re-research what you already know
- Missing file conflict serialization (two agents editing the same file = merge hell)
- Forgetting integration tasks (individual pieces work but don't connect)
</ultrathink_instruction>

### For Quick Feature (Tier 1)

No formal decomposition. Execute directly:
- Implement the feature following patterns from research
- Write tests
- Make incremental commits
- Skip to Phase 6 (Quality Gate)

### For Standard and Major Features (Tiers 2 and 3)

Create tasks using TaskCreate. Each task MUST include:
- **subject**: Imperative deliverable description
- **description**: Objective, files to modify (with paths), patterns to follow (with file references from research), acceptance criteria (testable), and constraints (files NOT to touch)
- **activeForm**: Present continuous form for progress display

### Set Dependencies

After creating all tasks, establish the dependency graph:

```
TaskUpdate(taskId: "2", addBlockedBy: ["1"])  # Task 2 needs Task 1's output
TaskUpdate(taskId: "3", addBlockedBy: ["1"])  # Task 3 also needs Task 1
TaskUpdate(taskId: "4", addBlockedBy: ["2", "3"])  # Integration task waits for both
```

**Rules for dependencies:**
- If Task B reads a file that Task A creates or heavily modifies: B depends on A
- If Task B uses an API/interface that Task A defines: B depends on A
- If two tasks modify the same file: serialize them (one blocks the other)
- If tasks are truly independent (different files, no shared state): no dependency needed

### Validate Decomposition

<critical_requirement>
Before spawning any agents, validate the task graph:

- [ ] Every task has clear, non-overlapping file ownership
- [ ] No circular dependencies exist
- [ ] Critical path is identified (longest dependency chain)
- [ ] Each task description includes enough context to execute without re-researching
- [ ] Integration points between tasks are explicitly documented
- [ ] Total task count matches the selected tier (Quick: 1-2, Standard: 3-7, Major: 7+)
</critical_requirement>

Present the task list with dependency graph to the user:

```
Task Graph:
  [1] Set up data model (no deps) ──┐
  [2] Implement service layer (no deps) ──┤
  [3] Build UI components (blocked by: 1) ─┤
  [4] Add IPC handlers (blocked by: 1, 2) ─┤
  [5] Integration + tests (blocked by: 3, 4) ──→ DONE

Critical path: 1 → 3 → 5 (or 1 → 4 → 5)
Estimated parallel speedup: 5 tasks in ~3 task-lengths
```

Present the task graph to the user, then proceed to spawn agents immediately (no separate approval gate — the graph itself is the checkpoint).

## Phase 4: Parallel Agent Execution

<parallel_tasks>

For each task with no unresolved blockedBy dependencies, spawn in parallel:

1. Mark as in_progress: `TaskUpdate(taskId: "[id]", status: "in_progress")`
2. Launch via Task tool with:
   - Full task description from TaskCreate
   - Relevant subset of the Feature Context Brief
   - Working agreement: commit incrementally, run tests, stay in file scope, mark complete when done
   - Model hint: use `opus` for architecture/complex logic, `sonnet` for implementation/tests

</parallel_tasks>

### Monitor and Unblock

- Use `TaskList` to check progress
- When a task completes, immediately spawn any newly unblocked tasks
- When a task fails: read output, retry with more context or escalate to user
- Report progress: "Task [id] complete. [X/Y] done. Spawning [newly unblocked]."

## Phase 5: Quality Gate

<critical_requirement> After all tasks complete, verify the feature works as an integrated whole. Individual tasks passing does not mean the feature works end-to-end. This gate is mandatory before shipping. </critical_requirement>

### Checklist

- [ ] All tasks show "completed" in TaskList
- [ ] All acceptance criteria from the original feature input are met
- [ ] Full test suite passes (run project's test command)
- [ ] Type checking passes (if applicable)
- [ ] No new lint warnings or errors
- [ ] Code follows patterns identified by research (no style drift)
- [ ] Feature works end-to-end (happy path verification)
- [ ] No TODO/FIXME/HACK comments without tracking issues

If integration issues arise, fix directly if small or create a new task if substantial. Re-run verification after fixes.

## Phase 6: Ship and Route

### Commit and Push

Stage relevant files, commit with conventional format (`feat(scope): description`), and push to origin with `-u` flag.

### Choose Next Step

Use the **AskUserQuestion tool**:

**Question:** "Feature complete and pushed. What's next?"

**Options:**
1. **Self-review** (Recommended) -- Run `/workflows:review` to catch issues before PR
2. **Create PR** -- Create pull request with summary, task breakdown, and testing notes
3. **Document learnings** -- Run `/workflows:compound` to capture novel solutions
4. **Continue iterating** -- Make additional changes, then loop back to Phase 5

Based on selection:
- **Self-review** -- Invoke `/workflows:review`. Address P1 findings, then return to this menu.
- **Create PR** -- Use `gh pr create` with summary, task breakdown, testing notes, and related issues/plans.
- **Document learnings** -- Invoke `/workflows:compound`, then return to this menu.
- **Continue iterating** -- Stay on branch, loop back to Phase 5 when ready.

After PR merge, suggest: `/workflows:compound` for knowledge capture, close related issues, update CLAUDE.md if significant, clean up worktree if used.

---

## Anti-Patterns

| Do NOT | Instead |
|--------|---------|
| Decompose before researching | Run Phase 1 research agents first |
| Create tasks < 30 min of work | Merge small tasks into meaningful units |
| Give agents vague descriptions | Include files, patterns, context, and acceptance criteria |
| Let parallel agents edit the same file | Serialize via blockedBy dependencies |
| Skip integration verification | Always run Phase 5 after all tasks complete |
| Ship without running tests | Phase 6 quality gate is mandatory |
| Over-decompose simple features | Use Quick Feature tier for 1-2 task work |

---

## Workflow Pipeline

```
workflows:plan → workflows:design → workflows:work → workflows:review → workflows:compound
                                         ↑
                                  start-new-feature (parallel dispatch)
```

| Command | Purpose | Artifacts |
|---------|---------|-----------|
| `/workflows:plan` | Research and plan | `plans/*.md` |
| `/workflows:design` | Visual refinement (video/UI scenes) | Updated components |
| `/workflows:work` | Execute a plan sequentially | Code + tests |
| `/start-new-feature` | **You are here** -- Parallel task dispatch | Task list + agents |
| `/workflows:review` | Multi-agent code review | `todos/*.md` |
| `/workflows:compound` | Document solutions | `docs/solutions/*.md` |
