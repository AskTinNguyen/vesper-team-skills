---
name: last7days
description: 7-day review of repo activity — surfaces trends, risks, and actionable insights
argument-hint: "[branch, worktree path, or GitHub URL] — defaults to current branch"
---

# last7days

Review the last 7 days of activity in a repo. Surface trends, risks, and actionable insights grounded in real data.

<review_target> #$ARGUMENTS </review_target>

## 1. Setup

Parse the target:
- **Empty** → use current branch in current directory
- **Branch name** → analyze that branch (verify it exists with `git rev-parse --verify`)
- **Path** → verify directory exists, `cd` to worktree
- **GitHub URL** → parse owner/repo, use `gh` CLI

Detect environment:
- Check if inside a git repo: `git rev-parse --is-inside-work-tree`
- Check if `gh` is available and authenticated: `gh auth status 2>&1`
- Set `HAS_GH=true/false` for graceful degradation

Use git's portable relative dates everywhere (no platform-specific `date` commands):
```
--since="7 days ago"
```

**If not a git repo, stop and tell the user.** If `gh` is unavailable, continue with git-only analysis and note that PR/issue data is skipped.

## 2. Data Collection

Run these commands sequentially. Check each for empty output before proceeding.

### 2a. Git Analysis (always available)

**Commits:**
```bash
git log --since="7 days ago" --all --no-merges --format="%H|%an|%ae|%ad|%s" --date=short
```
If empty → report "No commits in the last 7 days" and check `git log -1 --format="%ad" --date=relative` to show when last activity was. Stop here if no commits.

**Diff stats** (only if commits exist):
```bash
OLDEST=$(git log --since="7 days ago" --all --format="%H" --reverse | head -1)
CURRENT=$(git rev-parse HEAD)
git diff "$OLDEST".."$CURRENT" --stat
git diff "$OLDEST".."$CURRENT" --numstat
```

**Hotspots** (files changed most often):
```bash
git log --since="7 days ago" --all --name-only --format="" | sort | uniq -c | sort -rn | head -20
```

**Branches:**
```bash
git for-each-ref --sort=-committerdate --format='%(refname:short)|%(committerdate:short)|%(authorname)|%(subject)' refs/heads/
```

**Patterns** — scan recent commit messages:
```bash
git log --since="7 days ago" --all --oneline --no-merges | grep -iE "revert|hotfix|fix bug|WIP|hack|temp|workaround"
```

Check for TODO/FIXME additions:
```bash
git diff "$OLDEST".."$CURRENT" | grep -E "^\+" | grep -iE "TODO|FIXME" | head -20
```

### 2b. GitHub Analysis (only if HAS_GH=true)

**PRs:**
```bash
gh pr list --state all --search "created:>=YYYY-MM-DD" --json number,title,state,author,createdAt,mergedAt,additions,deletions,changedFiles,reviewDecision,labels
```
Use the date from 7 days ago in YYYY-MM-DD format for the search query.

**Issues:**
```bash
gh issue list --state all --search "created:>=YYYY-MM-DD" --json number,title,state,author,createdAt,closedAt,labels,assignees
gh issue list --state all --search "closed:>=YYYY-MM-DD" --json number,title,state,author,closedAt,labels
```

**Releases:**
```bash
gh release list --limit 5
```

If any `gh` command fails, log the error and continue with remaining data. Don't abort the whole review.

## 3. Analysis

Synthesize findings across all collected data. Focus on:

- **Velocity** — commit/PR/issue rates, any spikes or dropoffs by day
- **Risk signals** — files changed 3+ times (instability), large unreviewed PRs, revert/hotfix patterns, stale PRs open > 3 days
- **Focus areas** — which parts of the codebase got attention, concentrated vs scattered changes
- **Team dynamics** (multi-author only) — review bottlenecks, knowledge silos (files only one person touches)
- **Patterns** — new TODOs accumulating, dependency changes, config churn

Cross-reference signals: high-churn file + no tests = elevated risk. Multiple reverts in same area = instability. Stale PR + high additions = blocked large change.

## 4. Report

Adapt the report structure to actual findings. **Skip sections that have no data.** For a single-author repo, skip contributor breakdown. For repos with no PRs, skip PR activity.

Core structure:

**Header:**
```
## 7-Day Review: [repo-name] ([branch])
Period: [start_date] → [end_date]
```

**Story of the week** — 2-3 sentences summarizing what happened. Ground it in specifics.

**Key metrics** — table with commits, PRs (opened/merged), issues (opened/closed), lines added/removed, active contributors, files changed. Only include rows where data exists.

**Findings by priority:**
- **Red — Needs Attention:** items requiring action (security concerns, blocking PRs, instability patterns). Include specific file paths, commit hashes, PR numbers.
- **Yellow — Worth Watching:** emerging trends that could become problems. Include current data points.
- **Blue — Highlights:** positive signals worth noting.

**Code hotspots** — top 5-10 most-changed files with change count and authors.

**PR activity** (if HAS_GH) — merged, open, and stale PRs with titles and age.

**Actionable next steps** — 3-5 concrete actions derived from findings.

## 5. Todo Creation (Optional)

If Red items exist, **ask the user** whether to create todo files via `skill: file-todos`.

If user confirms, create todos:
- Naming: `{id}-pending-{priority}-{description}.md`
- Tags: `weekly-review` plus relevant tags
- Include: problem statement, evidence from analysis, recommended action

Do not auto-create todos without user confirmation.

## Rules

- Ground every insight in data — commit hashes, file paths, author names, PR numbers, dates. No speculative claims.
- Prioritize signal over noise — surface what matters, not every commit.
- Report objective metrics without judgment — focus on code health, not developer rankings.
- Degrade gracefully — work with whatever data is available (git-only, no PRs, no issues).
- If the repo has no activity in 7 days, say so and show when last activity occurred. Don't produce an empty report.
