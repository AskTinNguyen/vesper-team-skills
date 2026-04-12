# Run Repo Hygiene

<required_reading>
Read `references/git-command-playbook.md` for the canonical command snippets.
</required_reading>

<required_reading>
Read `references/report-template.md` before writing the final report so the output buckets match the workflow buckets.
</required_reading>

Use this workflow to inspect one repository, its local branches, and its worktrees, then clean the safe bucket and report the rest.

## 0. Prerequisites

Define:
- `REPO_ROOT`
- `BASE_BRANCH` (default: `main`)
- `BASE_REMOTE` (default: `origin/main`)
- report path such as `reports/repo-hygiene-YYYY-MM-DD.md`

Before cleanup:
- `cd "$REPO_ROOT"` before running repo-local helper scripts
- if the repo ships `.worktree-policy.local.json.example`, create `.worktree-policy.local.json` once and review your protected paths/prefixes
- if the repo ships a worktree hygiene guide, read it before cleanup

In Vesper, start with:

```bash
cd "$REPO_ROOT"
cp .worktree-policy.local.json.example .worktree-policy.local.json
```

Then review:
- `docs/dev/worktree-hygiene.md`
- `.worktree-policy.local.json`

## 1. Refresh refs safely

Run the explicit git refresh first:

```bash
git -C "$REPO_ROOT" fetch --prune origin
git -C "$REPO_ROOT" remote prune origin
git -C "$REPO_ROOT" worktree prune
```

Then run repo-native helpers when present.

```bash
cd "$REPO_ROOT"
if [ -f package.json ] && grep -q '"git:hygiene:json"' package.json; then
  bun run git:hygiene:json
elif [ -f scripts/git-hygiene-check.sh ]; then
  bash scripts/git-hygiene-check.sh --json --refresh
fi

if [ -f package.json ] && grep -q '"worktree:check"' package.json; then
  bun run worktree:check
elif [ -f scripts/worktree-hygiene.sh ]; then
  bash scripts/worktree-hygiene.sh --check
fi
```

Notes:
- `git:hygiene:json` / `git-hygiene-check.sh --json --refresh` gives a fast status baseline
- it does **not** replace the explicit fetch/prune step above
- `worktree:check` / `worktree-hygiene.sh --check` applies the repo's policy layer before any cleanup

## 2. Run three specialist passes

### A. Branch scout

Questions:
- which local branches are already merged into `main`?
- which are merged into `origin/main`?
- which have no upstream?
- which remotes are gone?

Core commands:

```bash
git -C "$REPO_ROOT" branch -vv
git -C "$REPO_ROOT" for-each-ref --format='%(refname:short)' refs/heads
git -C "$REPO_ROOT" branch --merged "$BASE_BRANCH"
```

For each branch of interest, capture:
- attached worktree path if any
- merged into local base
- merged into remote base
- ahead/behind local base

### B. Worktree scout

Questions:
- how many worktrees exist?
- which are clean vs dirty?
- which are duplicates?
- which attached branches no longer matter?

Core commands:

```bash
git -C "$REPO_ROOT" worktree list --porcelain
git -C "$REPO_ROOT" status --short --branch
```

For each worktree, capture:
- path
- branch
- clean/dirty
- ahead/behind base
- candidate classification: keep / review / remove

### C. Conflict scout

Questions:
- which worktrees contain unresolved merge states?
- are they still active or already merged elsewhere?

Core command pattern:

```bash
while IFS= read -r wt; do
  git -C "$wt" status --porcelain
done < <(git -C "$REPO_ROOT" worktree list --porcelain | awk '/^worktree /{print substr($0,10)}')
```

Look for unmerged markers:
- `UU`
- `AA`
- `DD`
- `AU`
- `UA`
- `DU`
- `UD`

## 3. Merge findings into buckets

### Remove now

Use this only for safe cleanup:
- clean worktree + branch merged into both local `main` and `origin/main`
- merged local branch with no attached worktree
- duplicate clean worktree with a preserved keeper

### Flag for action

Do not auto-delete these unless the user explicitly wants aggressive cleanup:
- dirty worktree with unique commits
- dirty root repo
- branch not merged and no upstream
- conflict worktree with unclear ownership

### Escalate

Call out these risks explicitly:
- current branch behind upstream
- root repo dirty while on `main`
- many branches without upstream tracking
- conflicted worktrees that may contain unsaved intent

## 4. Apply cleanup

Default to the repo's policy-driven cleanup path when it exists.

### Preferred: policy-driven cleanup

```bash
cd "$REPO_ROOT"
bun run worktree:check
bun run worktree:apply
```

Fallback when Bun aliases do not exist:

```bash
cd "$REPO_ROOT"
bash scripts/worktree-hygiene.sh --check
bash scripts/worktree-hygiene.sh --apply
```

### Manual branch cleanup after policy-driven worktree cleanup

Use this for merged local branches with no attached worktree:

```bash
git -C "$REPO_ROOT" branch -d <branch>
```

### Advanced fallback: bypassing the policy helper

Only use raw `git worktree remove` or `git branch -d` directly when all are true:
- the repo has no policy helper
- the cleanup target was already reviewed manually
- the branch is already merged into both local `main` and `origin/main`
- the user asked for manual cleanup rather than report-only review

Example:

```bash
git -C "$REPO_ROOT" worktree remove <worktree-path>
git -C "$REPO_ROOT" branch -d <branch>
```

For a clearly temporary conflicted worktree, use force only when all are true:
- the branch is already merged into both local `main` and `origin/main`
- the worktree is clearly disposable (`tmp/`, scratch, merge-check, etc.)
- the user asked for cleanup

```bash
git -C "$REPO_ROOT" worktree remove --force <worktree-path>
git -C "$REPO_ROOT" branch -d <branch>
```

## 5. Verify the cleanup state

After any cleanup step, rerun the status helpers so the report is grounded in the final state:

```bash
cd "$REPO_ROOT"
bun run git:hygiene:json
bun run worktree:check
```

Fallback when Bun aliases do not exist:

```bash
cd "$REPO_ROOT"
bash scripts/git-hygiene-check.sh --json --refresh
bash scripts/worktree-hygiene.sh --check
```

Expected outcome:
- safe removals no longer appear in the worktree list
- remaining dirty worktrees are still present and clearly flagged
- unresolved conflicts are either still intentionally present or intentionally removed

## 6. Flag unstaged changes

For every dirty repo or worktree, capture:
- branch
- path
- whether conflicts exist
- whether unique commits exist
- recommended next action: commit / stash / discard / review

## 7. Examples

### Example: safe removal

- branch: `feature/foo`
- worktree: clean
- merged into local `main`: yes
- merged into `origin/main`: yes
- result: **Remove now**

### Example: dirty worktree

- branch: `feature/bar`
- worktree: dirty
- merged into local `main`: yes
- merged into `origin/main`: yes
- result: **Flag for action** — commit, stash, or discard intentionally before cleanup

### Example: conflicted temporary worktree

- branch: `tmp/merge-check-123`
- worktree: conflicted
- merged into local `main`: yes
- merged into `origin/main`: yes
- clearly disposable: yes
- result: **Remove now only if the user asked for cleanup**

## 8. Troubleshooting

| Problem | Likely cause | What to do |
|---|---|---|
| `Not inside a git repository.` | helper script run from outside the repo | `cd "$REPO_ROOT"` first, then rerun |
| `origin` does not exist | local-only or unusual repo setup | skip origin-based checks, flag the repo shape in the report, and ask before deleting |
| base branch is not `main` | repo uses `develop`, `trunk`, or another base | set `BASE_BRANCH` and `BASE_REMOTE` explicitly before running merged checks |
| helper scripts are missing | repo does not ship local hygiene helpers | use the playbook commands directly and note that policy helpers were unavailable |
| worktree path contains spaces | fragile shell loop | use the `while IFS= read -r wt` pattern from this workflow and playbook |

## 9. Write the summary report

Follow `references/report-template.md`.

Minimum contents:
- repo and timestamp
- actions taken
- safe removals completed
- flagged items that still need action
- escalations and risk calls
- worktree hygiene recommendations
