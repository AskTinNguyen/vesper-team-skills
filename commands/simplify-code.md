---
description: Run dual-pass code simplification using Reducing Entropy + Code Simplifier skills. Composes both skills sequentially, then combines results.
argument-hint: [target] — branch:name, file:path, pr:number, or blank for git diff
---

# Simplify Code

Compose two existing skills — **Reducing Entropy** and **Code Simplifier** — in sequence to minimize and clean code without changing functionality.

## What This Command Does

1. **Identify target files** from the argument
2. **Count baseline** line counts for all target files
3. **Pass 1: Reducing Entropy** — invoke the skill to delete, shrink, and remove unnecessary code
4. **Pass 2: Code Simplifier** — invoke the skill to clarify, clean, and polish what remains
5. **Final combination** — review both passes together, resolve any conflicts, ensure nothing was broken
6. **Report** — before/after line counts, % reduction, what was removed

## Step 1: Identify Target Files

Parse the argument to determine which files to simplify:

- **No argument**: Run `git diff --name-only HEAD` to find recently modified files. If no uncommitted changes, use `git diff --name-only main..HEAD` for branch changes.
- **`branch:<name>`**: Run `git diff --name-only main..<name> -- '*.ts' '*.tsx' '*.js' '*.jsx' '*.py'` to find all changed source files on that branch.
- **`file:<path>`**: Use the single specified file.
- **`pr:<number>`**: Run `gh pr diff <number> --name-only` to find files changed in that PR.

Filter to only source code files (skip configs, lockfiles, generated files). Read CLAUDE.md for project conventions before proceeding.

If no target files are found, report "No files to simplify" and stop.

## Step 2: Count Baseline

For each target file, count lines with `wc -l`. Record as `baseline_lines` per file and `total_baseline`. Display the file list and total lines to establish the scoreboard.

## Step 3: Pass 1 — Reducing Entropy

Invoke `skill: reducing-entropy` on all target files.

1. Load the skill and follow its full process — including loading reference mindsets from its `references/` directory
2. Apply to all target files identified in Step 1
3. Edit files directly as the skill instructs

After all edits, count lines again. Record as `post_entropy_lines`.

## Step 4: Pass 2 — Code Simplifier

Invoke `skill: code-simplifier` on the same files (now already trimmed by Pass 1).

1. Load the skill and follow its full process — it will guide analysis and edits for clarity, consistency, and maintainability
2. Apply to all target files identified in Step 1
3. Edit files directly as the skill instructs

After all edits, count lines again. Record as `post_simplifier_lines`.

## Step 5: Final Combination

Review the cumulative changes from both passes together:

1. Run type checking if available (`bun run typecheck:all`, `tsc --noEmit`, `npx tsc`, or equivalent) — the output should show no NEW errors introduced by the simplification
2. Verify no functionality was changed — the code should do exactly what it did before, just with less code and more clarity
3. If both passes touched the same code in conflicting ways, prefer the version that is both smaller AND clearer
4. Ensure imports are still correct after deletions

## Step 6: Commit and Report

Commit all changes with:
```
git add -A && git commit -m "refactor: simplify [scope] (reducing-entropy + code-simplifier)"
```

Where `[scope]` describes the target (e.g., "session context maps", "heatmap parser", the branch name).

### Report Format

Display a summary table:

```
## Simplification Report

| File | Before | After Entropy | After Simplifier | Δ |
|------|--------|---------------|------------------|---|
| ... | ... | ... | ... | ... |

**Total: [baseline] → [final] lines ([X]% reduction)**

### What was removed:
- [List key removals — dead code, unnecessary abstractions, verbose comments, etc.]

### What was clarified:
- [List key clarity improvements — naming, structure, consolidation, etc.]
```

## Rules

- **NEVER change functionality** — only change HOW code does things, not WHAT it does
- **Both skills must run** — don't skip either pass
- **Edit directly** — don't just report findings, make the changes
- **Measure everything** — line counts before, between, and after
- **Type-check after** — ensure no compilation errors were introduced
- **Commit the result** — leave a clean git trail
