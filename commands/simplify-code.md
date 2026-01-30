---
description: Run dual-pass code simplification using Reducing Entropy + Code Simplifier skills via sequential sub-agents, then synthesize results.
argument-hint: [target] — branch:name, file:path, pr:number, or blank for git diff
---

# Simplify Code

Compose two existing skills — **Reducing Entropy** and **Code Simplifier** — via sequential sub-agents to minimize and clean code without changing functionality.

## What This Command Does

1. **Identify target files** from the argument
2. **Count baseline** line counts
3. **Agent 1: Reducing Entropy** — sub-agent applies the skill to delete and shrink
4. **Agent 2: Code Simplifier** — sub-agent applies the skill to clarify and polish (runs after Agent 1 completes)
5. **Synthesis** — verify no functionality changed, type-check, commit
6. **Report** — before/after line counts, % reduction, what changed

## Step 1: Identify Target Files

<task_list>

- [ ] Parse the argument to determine target:
  - **No argument**: `git diff --name-only HEAD` for uncommitted changes; if none, `git diff --name-only main..HEAD` for branch changes
  - **`branch:<name>`**: `git diff --name-only main..<name> -- '*.ts' '*.tsx' '*.js' '*.jsx' '*.py'`
  - **`file:<path>`**: Use the specified file
  - **`pr:<number>`**: `gh pr diff <number> --name-only`
- [ ] Filter to source code files only (skip configs, lockfiles, generated files)
- [ ] Read CLAUDE.md for project conventions
- [ ] If no target files found, report "No files to simplify" and stop

</task_list>

## Step 2: Count Baseline

<task_list>

- [ ] For each target file, count lines with `wc -l`
- [ ] Record `baseline_lines` per file and `total_baseline`
- [ ] Display file list and total lines to establish the scoreboard
- [ ] Save the file list to a variable for passing to agents

</task_list>

## Step 3: Agent 1 — Reducing Entropy

Spawn a sub-agent to run the first pass:

<agent_task>

```
Task(
  subagent_type: "general-purpose",
  prompt: """
## Assignment: Reducing Entropy Pass

Apply `skill: reducing-entropy` to simplify the following files:

[LIST TARGET FILES HERE]

### Instructions:
1. Load the reducing-entropy skill and follow its FULL process
2. Load at least one reference mindset from the skill's references/ directory
3. State which mindset you loaded and its core principle
4. For each file, apply the skill's three questions:
   - What's the smallest codebase that solves this?
   - Does this code result in more code than needed?
   - What can we delete?
5. Edit files directly — delete dead code, remove unnecessary abstractions, inline single-use helpers, collapse verbose structures
6. NEVER change functionality — only reduce code size
7. After all edits, run `wc -l` on each file and report line counts

### Output:
Report per-file line counts (before → after) and list what was removed.
""",
  description: "Pass 1: Reducing Entropy"
)
```

</agent_task>

Wait for Agent 1 to complete before proceeding. Record `post_entropy_lines`.

## Step 4: Agent 2 — Code Simplifier

Spawn a sub-agent to run the second pass on the already-trimmed code:

<agent_task>

```
Task(
  subagent_type: "general-purpose",
  prompt: """
## Assignment: Code Simplifier Pass

Apply `skill: code-simplifier` to refine the following files (already trimmed by a prior entropy reduction pass):

[LIST TARGET FILES HERE]

### Instructions:
1. Load the code-simplifier skill and follow its FULL process
2. Read CLAUDE.md for project-specific conventions and standards
3. Analyze each file for:
   - Unnecessary complexity and nesting
   - Redundant code and abstractions
   - Overly clever solutions
   - Variable/function naming clarity
   - Opportunities to consolidate related logic
   - Unnecessary comments describing obvious code
   - Nested ternaries (prefer if/else or switch)
4. Apply project standards from CLAUDE.md
5. Prioritize clarity over brevity
6. Edit files directly
7. NEVER change functionality — only improve clarity and consistency
8. After all edits, run `wc -l` on each file and report line counts

### Output:
Report per-file line counts (before → after) and list what was clarified.
""",
  description: "Pass 2: Code Simplifier"
)
```

</agent_task>

Wait for Agent 2 to complete. Record `post_simplifier_lines`.

## Step 5: Synthesis

After both agents complete:

<task_list>

- [ ] Review the cumulative changes from both passes
- [ ] Run type checking if available (`bun run typecheck:all`, `tsc --noEmit`, `npx tsc`, or equivalent) — no NEW errors should be introduced
- [ ] Verify no functionality was changed — code does exactly what it did before
- [ ] Ensure imports are still correct after deletions
- [ ] Fix any issues found during verification

</task_list>

## Step 6: Commit and Report

<task_list>

- [ ] Commit all changes:
  ```
  git add -A && git commit -m "refactor: simplify [scope] (reducing-entropy + code-simplifier)"
  ```
  Where `[scope]` describes the target (branch name, feature name, or file scope)

</task_list>

### Report Format

Display a summary table:

```markdown
## Simplification Report

| File | Baseline | After Entropy | After Simplifier | Δ |
|------|----------|---------------|------------------|---|
| ... | ... | ... | ... | ... |

**Total: [baseline] → [final] lines ([X]% reduction)**

### What was removed (Pass 1 — Entropy):
- [List key removals — dead code, unnecessary abstractions, YAGNI, etc.]

### What was clarified (Pass 2 — Simplifier):
- [List key improvements — naming, structure, consolidation, etc.]
```

## Rules

- **NEVER change functionality** — only change HOW code does things, not WHAT it does
- **Both agents must run sequentially** — Agent 2 depends on Agent 1's output
- **Each agent invokes its skill directly** — don't recreate skill logic in this command
- **Edit directly** — agents make changes, not just report findings
- **Measure everything** — line counts at baseline, after each pass, and final
- **Type-check after** — ensure no compilation errors were introduced
- **Commit the result** — leave a clean git trail
