---
name: workflows:bulk-review
description: Review multiple PRs efficiently using batched single-agent reviews with file-based result collection
argument-hint: "[PR numbers or URLs, comma-separated, e.g. 101,102,103 or PR #101 PR #102]"
---

# Bulk Review Command

<command_purpose> Review multiple PRs efficiently without context overflow. Uses flat 2-level agent architecture with file-based results instead of nested multi-agent coordinators. </command_purpose>

## Introduction

<role>Senior Code Review Coordinator specializing in efficient multi-PR triage and cross-cutting pattern detection</role>

This workflow is designed for reviewing many PRs at scale. Unlike `/workflows:review` (which spawns 13+ sub-agents per PR), this uses a single generalist agent per PR that writes results to files, keeping the parent context lean.

**When to use this vs `/workflows:review`:**
| Scenario | Use |
|----------|-----|
| 1-3 critical PRs needing deep analysis | `/workflows:review` |
| 4+ PRs for triage or batch review | `/workflows:bulk-review` |
| Regular review cadence (weekly, daily) | `/workflows:bulk-review` |

## Prerequisites

<requirements>
- Git repository with GitHub CLI (`gh`) installed and authenticated
- PRs must be accessible via `gh pr view`
</requirements>

## Input

<review_target> #$ARGUMENTS </review_target>

## Phase 1: Parse PR List

<thinking>
Extract PR numbers from the user input. Accept formats:
- Comma-separated numbers: 101,102,103
- Space-separated: 101 102 103
- With # prefix: #101 #102 #103
- GitHub URLs: https://github.com/owner/repo/pull/101
- Ranges: 101-105
- "latest N" or "last N": fetch the N most recent open PRs
</thinking>

<task_list>

- [ ] Parse user input to extract PR numbers
- [ ] If input says "latest N" or "last N", run `gh pr list --limit N --json number` to get PR numbers
- [ ] Validate each PR exists using `gh pr view {number} --json number,title,state`
- [ ] Skip closed/merged PRs with a warning
- [ ] Print the list of PRs to review with titles
- [ ] Create the `reviews/` directory in the current working directory for output files

</task_list>

**Validation output format:**
```
Found N PRs to review:
  PR #101 - Add user authentication
  PR #102 - Fix payment processing bug
  PR #103 - Update dashboard layout
  ...
  Skipped: PR #99 (merged), PR #100 (closed)
```

## Phase 2: Batched Single-Agent Reviews

<critical_requirement>
Each review agent is a SINGLE agent — it must NOT spawn sub-agents, use /workflows:review, or use the dispatch skill internally. Each agent performs a one-pass comprehensive review and writes findings to a file.

Batch size: 5 PRs in parallel. Wait for each batch to complete before starting the next.
</critical_requirement>

### Dispatch Strategy

For each batch of up to 5 PRs, dispatch Task agents in parallel. Each agent receives these instructions:

```
You are reviewing PR #{number} in this repository.

IMPORTANT: Do NOT spawn sub-agents. Do NOT use /workflows:review or dispatch.
Perform a single-pass review covering ALL of these areas.

## Steps

1. Get PR metadata:
   gh pr view {number} --json title,body,files,additions,deletions,baseRefName,headRefName

2. Get the full diff:
   gh pr diff {number}

3. Review the diff for ALL of these categories:
   - **Security**: injection, auth bypass, secrets exposure, OWASP top 10
   - **Architecture**: coupling, cohesion, separation of concerns, patterns
   - **Code Quality**: readability, naming, duplication, complexity
   - **Performance**: N+1 queries, unnecessary allocations, missing indexes
   - **Testing**: coverage gaps, missing edge cases, test quality
   - **Data Integrity**: migrations, schema changes, backwards compatibility
   - **Error Handling**: missing error cases, swallowed exceptions

4. Write your findings to: reviews/pr-{number}.md

## Output File Format

Write the file with this exact structure:

---
pr_number: {number}
title: "{PR title}"
author: "{PR author}"
files_changed: {count}
additions: {count}
deletions: {count}
verdict: "approve" | "request-changes" | "needs-discussion"
p1_count: {number}
p2_count: {number}
p3_count: {number}
---

# PR #{number}: {title}

## Summary
{2-3 sentence summary of what the PR does}

## Findings

### P1 — Critical (Blocks Merge)
{List each finding with file path, line reference, and explanation}
{If none: "No critical findings."}

### P2 — Important (Should Fix)
{List each finding}
{If none: "No important findings."}

### P3 — Nice to Have
{List each finding}
{If none: "No minor findings."}

## Verdict
{One paragraph: approve/request-changes/needs-discussion with justification}


5. Return ONLY this one-line status (do not return the full review):
   PR #{number}: {verdict} — {p1_count} P1, {p2_count} P2, {p3_count} P3
```

### Execution

<task_list>

- [ ] Create `reviews/` directory if it doesn't exist
- [ ] Split PR list into batches of 5
- [ ] For each batch:
  - [ ] Dispatch up to 5 Task agents in parallel (one per PR)
  - [ ] Each agent: fetch diff, review, write to `reviews/pr-{number}.md`
  - [ ] Each agent returns ONE LINE: `PR #{number}: {verdict} — {counts}`
  - [ ] Wait for all agents in batch to complete
  - [ ] Print batch status before starting next batch
- [ ] After all batches complete, print status table

</task_list>

**Batch progress output:**
```
Batch 1/3: Reviewing PRs #101, #102, #103, #104, #105...
  ✓ PR #101: approve — 0 P1, 1 P2, 2 P3
  ✓ PR #102: request-changes — 2 P1, 3 P2, 1 P3
  ✓ PR #103: approve — 0 P1, 0 P2, 1 P3
  ✓ PR #104: needs-discussion — 1 P1, 2 P2, 0 P3
  ✓ PR #105: approve — 0 P1, 1 P2, 0 P3

Batch 2/3: Reviewing PRs #106, #107, #108, #109, #110...
  ...
```

## Phase 3: Synthesis

<thinking>
After all reviews are written to files, read them all and identify cross-PR patterns. This is the only phase that reads the full review content — the parent agent's context was kept lean during Phase 2 because it only received one-line status updates.
</thinking>

<task_list>

- [ ] Read all `reviews/pr-*.md` files
- [ ] Identify cross-PR patterns:
  - [ ] Same security issue appearing in multiple PRs
  - [ ] Shared architectural concerns
  - [ ] Related PRs that should be reviewed together
  - [ ] Systemic code quality patterns
- [ ] Generate combined report at `reviews/SUMMARY.md`

</task_list>

### Summary Report Format

Write `reviews/SUMMARY.md` with this structure:

```markdown
# Bulk Review Summary

**Date:** {date}
**PRs Reviewed:** {count}
**Repository:** {owner/repo}

## Overview

| PR | Title | Verdict | P1 | P2 | P3 | Author |
|----|-------|---------|----|----|-----|--------|
| #101 | Add auth | ✅ approve | 0 | 1 | 2 | @user |
| #102 | Fix payments | ❌ changes | 2 | 3 | 1 | @user |
| ... | ... | ... | ... | ... | ... | ... |

**Totals:** X P1, Y P2, Z P3 across N PRs

## P1 Findings That Block Merge

{List ALL P1 findings across all PRs, grouped by PR}

## Cross-PR Patterns

{Patterns detected across multiple PRs — shared issues, related changes, systemic concerns}

## Individual Reviews

- [PR #101](pr-101.md)
- [PR #102](pr-102.md)
- ...

## Recommended Merge Order

{If PRs have dependencies or conflicts, suggest an order}
```

## Phase 4: Todo Creation (Optional)

<task_list>

- [ ] Ask user: "Create todo files for P1/P2 findings? (yes/no)"
- [ ] If yes: use file-todos skill to create `todos/` entries for all P1 and P2 findings
  - [ ] P1 findings: `{id}-pending-p1-{description}.md`
  - [ ] P2 findings: `{id}-pending-p2-{description}.md`
  - [ ] Tag all with `bulk-review` and `code-review`
  - [ ] Include PR number in each todo's metadata

</task_list>

## Phase 5: Present Results

Print final summary to the user:

```
## Bulk Review Complete

Reviewed {N} PRs → reviews/SUMMARY.md

| PR | Verdict | P1 | P2 | P3 |
|----|---------|----|----|-----|
| ... |

{P1 count} findings block merge.
{P2 count} findings should be addressed.
{P3 count} minor suggestions.

Individual reviews: reviews/pr-{number}.md
Summary report: reviews/SUMMARY.md
{If todos created: "Todo files: todos/"}
```

---

## Design Rationale

This workflow avoids context overflow by:

1. **Flat agent tree**: 1 parent + N leaf agents (no nested multi-agent workflows)
2. **File-based results**: Each agent writes to `reviews/pr-{N}.md` — parent only sees one-line status
3. **Batched parallelism**: Max 5 concurrent agents prevents resource exhaustion
4. **Late synthesis**: Full review content only loaded once, after all agents complete
5. **No sub-spawning**: Each leaf agent does a single-pass review, never invokes dispatch or other workflows

---

## Workflow Pipeline

```
workflows:plan → workflows:work → workflows:bulk-review → workflows:compound
                                        ↑
                                  You are here
```

| Command | Purpose | Artifacts |
|---------|---------|-----------|
| `/workflows:review` | Deep multi-agent review (1-3 PRs) | `todos/*.md` |
| `/workflows:bulk-review` | **You are here** — Efficient batch review (4+ PRs) | `reviews/*.md` |
