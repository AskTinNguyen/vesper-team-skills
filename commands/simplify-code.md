---
description: Run dual-pass code simplification using Reducing Entropy + Code Simplifier skills via sequential sub-agents, then synthesize results.
argument-hint: [target] — branch:name, file:path, pr:number, or blank for git diff
---

# Simplify Code

Compose two existing skills — **Reducing Entropy** and **Code Simplifier** — via sequential sub-agents to minimize and clean code without changing functionality.

> **Design note:** Early testing on 833 lines of TypeScript showed 41.6% reduction.
> The reducing-entropy skill focuses on three core questions and red flags —
> no additional context loading needed.

## What This Command Does

1. **Identify target files** from the argument
2. **Count baseline** line counts
3. **Snapshot** — stash uncommitted work for rollback safety
4. **Agent 1: Reducing Entropy** — sub-agent applies the skill's core heuristics to delete and shrink
5. **Agent 2: Code Simplifier** — sub-agent applies the skill to clarify and polish (runs after Agent 1 completes)
6. **Synthesis** — verify no functionality changed, type-check; rollback if broken
7. **Report** — before/after line counts, % reduction, what changed

## Step 1: Identify Target Files

<task_list>

- [ ] Parse the argument to determine target:
  - **No argument**: `git diff --name-only HEAD` for uncommitted changes; if none, `git diff --name-only main..HEAD` for branch changes. Filter to source code extensions.
  - **`branch:<name>`**: `git diff --name-only main..<name>` — filter to source code files
  - **`file:<path>`**: Use the specified file
  - **`pr:<number>`**: `gh pr diff <number> --name-only` — filter to source code files
- [ ] Filter to source code files only (skip configs, lockfiles, generated files, images, fonts). Include common extensions: `*.ts *.tsx *.js *.jsx *.py *.rb *.go *.rs *.java *.kt *.swift *.c *.cpp *.h`
- [ ] Read CLAUDE.md for project conventions
- [ ] If no target files found, report "No files to simplify" and stop
- [ ] Write the final file list to `/tmp/simplify-target-files.txt` (one absolute path per line) for sub-agents to consume

</task_list>

## Step 2: Count Baseline

<task_list>

- [ ] For each target file, count ONLY the target file lines with `wc -l` (not entire files if targeting new code on a branch)
- [ ] Record `baseline_lines` per file and `total_baseline`
- [ ] Display file list and total lines to establish the scoreboard

</task_list>

## Step 2.5: Snapshot for Rollback

<task_list>

- [ ] Create a rollback checkpoint before agents make destructive edits:
  ```bash
  git stash push -m "pre-simplify-snapshot" --include-untracked
  git stash pop
  git tag _pre_simplify_checkpoint HEAD 2>/dev/null || true
  ```
  This creates a tagged checkpoint. If synthesis fails in Step 5, rollback with:
  ```bash
  git checkout _pre_simplify_checkpoint -- .
  ```
- [ ] Confirm checkpoint exists before proceeding

</task_list>

## Step 3: Agent 1 — Reducing Entropy

Spawn a sub-agent to run the first pass:

<agent_task>

```
Task(
  subagent_type: "general-purpose",
  prompt: """
## Assignment: Reducing Entropy Pass

Invoke `skill: reducing-entropy` on the target files listed in `/tmp/simplify-target-files.txt`.
Read that file first to get the full list of absolute paths.

### Process:
1. Read `/tmp/simplify-target-files.txt` to get the target file list
2. Load the reducing-entropy skill
3. For each file, apply the three questions:
   - What's the smallest codebase that solves this?
   - Does this code result in more code than needed?
   - What can we delete?
5. Watch for red flags: status quo bias, unnecessary flexibility, over-separation, type safety costing too many lines
6. Be aggressive — replace verbose control flow (switch/case) with data structures (lookup tables/maps) where possible
7. Inline helper functions called only once
8. Delete dead code, unnecessary abstractions, verbose JSDoc on self-documenting code
9. Edit files directly — do NOT just report findings
10. NEVER change functionality — only reduce code size
11. After all edits, run `wc -l` on each TARGET FILE and report line counts

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
  subagent_type: "code-simplifier",
  prompt: """
## Assignment: Code Simplifier Pass

Apply code simplification to the target files listed in `/tmp/simplify-target-files.txt`.
These files have already been trimmed by a prior entropy reduction pass.

### Process:
1. Read `/tmp/simplify-target-files.txt` to get the target file list
2. Read CLAUDE.md for project-specific conventions and standards
3. For each file, analyze and fix:
   - Unnecessary complexity and nesting
   - Redundant code and abstractions
   - Overly clever solutions
   - Variable/function naming clarity
   - Opportunities to consolidate related logic
   - Unnecessary comments describing obvious code
   - Nested ternaries (prefer if/else or switch)
4. Apply project standards from CLAUDE.md
5. Prioritize clarity over brevity
6. Edit files directly — do NOT just report findings
7. NEVER change functionality — only improve clarity and consistency
8. After all edits, run `wc -l` on each TARGET FILE and report line counts

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
- [ ] Run type checking if available — detect the right command:
  - Check `package.json` scripts for `typecheck`, `type-check`, `tsc`, or similar
  - Fallback order: `bun run typecheck:all` → `npx tsc --noEmit` → `tsc --noEmit`
  - For Python: `mypy` or `pyright` if configured
  - For Go: `go vet ./...`
  - No NEW errors should be introduced
- [ ] Verify no functionality was changed — code does exactly what it did before
- [ ] Ensure imports are still correct after deletions
- [ ] If verification fails:
  ```bash
  git checkout _pre_simplify_checkpoint -- .
  ```
  Report what broke and stop. Do not commit broken code.
- [ ] Fix any minor issues found during verification
- [ ] Clean up checkpoint tag: `git tag -d _pre_simplify_checkpoint 2>/dev/null || true`

</task_list>

## Step 5.5: Quality Score

Calculate a heuristic quality score (0–100) for each target file, before and after simplification. This quantifies improvement beyond line counts.

<task_list>

- [ ] For each target file, compute `Score = 100 - penalties` (floor at 0) using the baseline snapshot and current state:

| Metric | Threshold | Penalty |
|--------|-----------|---------|
| Cyclomatic complexity per function (if/else/for/while/case/&&/\|\|/catch/ternary) | >10 per function | -5 each |
| Cyclomatic complexity per function | >20 per function | -10 each (instead of -5) |
| Function size | >50 lines | -3 each |
| File size | >500 lines | -5 per file |
| Nesting depth (indentation levels) | >3 levels | -3 each |
| Parameter count | >4 params per function | -2 each |

- [ ] Use heuristic grep/awk checks — exact AST parsing is not required:
  ```bash
  # Cyclomatic complexity: count branching keywords per function
  grep -cP '\b(if|else|for|while|case|catch)\b|\?\s|&&|\|\|' FILE
  # Function size: count lines between function boundaries
  # Nesting depth: measure leading whitespace/indentation depth
  awk '{ match($0, /^[ \t]*/); depth=RLENGTH/2; if(depth>max) max=depth } END { print max }' FILE
  # Parameter count: count commas+1 in function signatures
  grep -oP '\([^)]{20,}\)' FILE  # long parameter lists
  ```
- [ ] Record `before_score` (from git stash or checkpoint) and `after_score` (current state) per file
- [ ] Interpretation: 90–100 Excellent, 70–89 Acceptable, <70 Needs Work

</task_list>

## Step 6: Commit and Report

<task_list>

- [ ] Stage only the target files (read the list from `/tmp/simplify-target-files.txt`):
  ```bash
  xargs git add < /tmp/simplify-target-files.txt
  git commit -m "refactor: simplify [scope] (reducing-entropy + code-simplifier)"
  ```
  Where `[scope]` describes the target (branch name, feature name, or file scope)
- [ ] Clean up: `rm -f /tmp/simplify-target-files.txt`

</task_list>

### Report Format

Display a summary table:

```markdown
## Simplification Report

| File | Baseline | After Entropy | After Simplifier | Δ |
|------|----------|---------------|------------------|---|
| ... | ... | ... | ... | ... |

**Total: [baseline] → [final] lines ([X]% change)**

### Quality Score

| File | Before | After | Change |
|------|--------|-------|--------|
| ... | ... | ... | ... |

**Overall: [before_avg] → [after_avg] ([interpretation])**

### What was removed (Pass 1 — Entropy):
- [List key removals — dead code, unnecessary abstractions, YAGNI, etc.]

### What was clarified (Pass 2 — Simplifier):
- [List key improvements — naming, structure, consolidation, etc.]
- Note: Pass 2 may increase line count if expanding dense code for clarity.
```

## Rules

- **NEVER change functionality** — only change HOW code does things, not WHAT it does
- **Both agents must run sequentially** — Agent 2 depends on Agent 1's output
- **Each agent invokes its skill directly** — don't recreate skill logic in this command
- **Agent 2 uses the native `code-simplifier` subagent type** — not `general-purpose`
- **File list via `/tmp/simplify-target-files.txt`** — sub-agents read this file, no placeholder interpolation
- **Be aggressive on Pass 1** — prefer data structures over control flow, inline single-use helpers, delete verbose comments
- **Edit directly** — agents make changes, not just report findings
- **Count only target files** — don't report line counts for entire pre-existing files
- **Measure everything** — line counts at baseline, after each pass, and final
- **Type-check after** — ensure no compilation errors were introduced
- **Rollback if broken** — use the pre-simplify checkpoint to revert on failure
- **Stage only target files** — never use `git add -A` or `git add .`
- **Commit the result** — leave a clean git trail
- **Calculate quality scores** — quantify improvement beyond line counts
