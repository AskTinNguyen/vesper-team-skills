---
name: ship-notes
description: This skill should be used when generating release notes from recent git activity. It produces both technical (developer-focused) and non-technical (user-facing) release notes from the last 7 days of commits and merged PRs, with a suggested semver version bump. Triggers include "ship notes", "write release notes", "generate changelog", "what shipped this week", "prepare release".
---

# ship-notes: Release Notes Generator

Generate dual-audience release notes from the last 7 days of git activity — a technical version for developers and a plain-language version for users.

## 1. Data Collection

<target> #$ARGUMENTS </target>

Target defaults to the current branch. If a branch name is provided, verify with `git rev-parse --verify`. Stop if not inside a git repo.

**Git log (primary source):**
```bash
git log --since="7 days ago" --no-merges --format="%h|%an|%ad|%s" --date=short --numstat
```
If empty → report "No commits in the last 7 days" with `git log -1 --format="%ad" --date=relative` and stop.

**Latest version tag:**
```bash
git tag --sort=-v:refname | grep -E "^v?[0-9]+\.[0-9]+" | head -n 1
```

**Merged PRs (if `gh` is available):**
```bash
gh pr list --state merged --search "merged:>=$(date -u -v-7d +%Y-%m-%d 2>/dev/null || date -u -d '7 days ago' +%Y-%m-%d)" --json number,title,author,mergedAt,labels --limit 100
```
If `gh` fails, continue with git-only data and note the omission.

## 2. Classify and Analyze

Read the collected commit messages and PR titles. Categorize each change into one group:

1. **Breaking Changes** — only when commit message contains `BREAKING CHANGE:`, `!:` (conventional commits), or the diff removes public API surface. Do not classify routine renames, internal removals, or refactors as breaking.
2. **Features** — new user-facing functionality
3. **Fixes** — corrections to existing behavior
4. **Other** — improvements, refactoring, deps, docs, chore. Mention notable items; omit trivial ones.

**Semver suggestion** based on classified changes:
- Any Breaking Changes → MAJOR
- Any Features (no breaking) → MINOR
- Only Fixes/Other → PATCH

If a version tag exists, parse it (strip `v` prefix if present), increment the appropriate component, and show `vCurrent → vNext`. If no tags exist, state that.

## 3. Output

Generate both versions in a single response. Skip empty categories.

### Technical Release Notes

```markdown
# Release Notes — [repo-name] vX.Y.Z
**Period:** YYYY-MM-DD → YYYY-MM-DD | **Bump:** PATCH (v1.2.3 → v1.2.4)
**Stats:** X commits, +A/-D lines

## Breaking Changes
- **description** — migration path if known (`a1b2c3d`)

## Features
- **description** (`a1b2c3d`, PR #N)

## Fixes
- **description** (`a1b2c3d`)

## Other
- Summary of improvements, deps, docs
```

Include 7-char commit hashes and PR numbers. Include file paths only for breaking changes.

### Non-Technical Release Notes

```markdown
# What's New — [product-name]
**Released:** YYYY-MM-DD

## New Features
- **Name** — what users can now do

## Fixes
- **Issue** — what was broken, now resolved

## Action Required
> Only if breaking changes affect users
- What to do, in plain language
```

No hashes, no file paths, no jargon. Combine related commits into single entries. Omit changes with no user-visible impact.

## 4. Follow-up

After output, mention that `gh release create --draft` is available if `gh` is present. Let the user drive next steps — do not prompt with multiple questions.

## Rules

- Both versions must be consistent — every non-technical item traces to a technical item, but many technical items are omitted from non-technical notes.
- Combine trivial commits (typos, formatting) into summary lines.
- If the repo is a shallow clone (`git rev-parse --is-shallow-repository`), warn that results may be incomplete.
