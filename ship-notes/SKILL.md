---
name: ship-notes
description: "Generate dual-audience release notes (technical + user-facing) from recent git activity with semver bump suggestions. Use after a development sprint or before a release. Triggers: 'ship notes', 'write release notes', 'what shipped this week', 'prepare release'."
alwaysAllow: ["Bash", "Read", "Glob", "Grep"]
---

# ship-notes: Release Notes Generator

<objective>
Generate dual-audience release notes from the last 7 days of git activity — a technical version for developers and a plain-language version for users — with a semver bump suggestion based on change classification.
</objective>

## Prerequisites

- **git** >= 2.12 (for `--date=short` and `--sort=-v:refname`)
- **gh** >= 2.0 (optional; enables merged PR data)
- **Python 3** (optional; portable date fallback)

Check: `git --version` and `gh --version`

## 1. Data Collection

<target> #$ARGUMENTS </target>

(`$ARGUMENTS` is replaced at runtime with whatever the user typed after the skill name.)

Parse the target:
- **Empty** → use current branch in current directory
- **Branch name** → verify with `git rev-parse --verify`, analyze that branch
- **Path** → verify directory exists, `cd` to worktree

Examples: `ship-notes` (current branch), `ship-notes main` (branch), `ship-notes /path/to/repo` (path). Stop if not inside a git repo.

**Git log (primary source):**
```bash
git log --since="7 days ago" --no-merges --format="%h|%an|%ad|%s" --date=short --numstat
```
If empty → report "No commits in the last 7 days" with `git log -1 --format="%ad" --date=relative` and stop.

**Latest version tag:**
```bash
git tag --sort=-v:refname | grep -E "^v?[0-9]+\.[0-9]+\.[0-9]+$" | head -n 1
```

**Merged PRs (if `gh` is available):**
```bash
SINCE_DATE=$(python3 -c "from datetime import date, timedelta; print((date.today()-timedelta(7)).isoformat())")
gh pr list --state merged --search "merged:>=$SINCE_DATE" --json number,title,author,mergedAt,labels --limit 100
```
If `gh` fails, continue with git-only data and note the omission.

## 2. Classify and Analyze

Read the collected commit messages and PR titles. Categorize each change into one group:

1. **Breaking Changes** — only when commit message contains `BREAKING CHANGE:` in the footer, `<type>!:` or `<type>(scope)!:` (conventional commits bang notation), or the diff removes public API surface. Do not classify routine renames, internal removals, or refactors as breaking.
2. **Features** — new user-facing functionality
3. **Fixes** — corrections to existing behavior
4. **Other** — subcategories: performance improvements, refactoring, dependency updates, documentation, chore/CI. Mention notable items; omit trivial ones (typos, formatting).

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

## Error Handling

| Situation | Action |
|-----------|--------|
| Not a git repo | Stop and tell the user |
| No commits in 7 days | Report last activity date via `git log -1 --format="%ad" --date=relative`, stop |
| `gh` not installed or not authenticated | Continue with git-only data, note "PR data not available" |
| No version tags found | State "no version tags found" in semver section, skip `vCurrent → vNext` |
| Shallow clone detected | Warn results may be incomplete, continue |
| `gh pr list` returns 100 results | Warn that results may be truncated |

## Rules

- Both versions must be consistent — every non-technical item traces to a technical item, but many technical items are omitted from non-technical notes.
- Combine trivial commits (typos, formatting) into summary lines.
- If the repo is a shallow clone (`git rev-parse --is-shallow-repository`), warn that results may be incomplete.
- This skill scopes to the entire repo root. For monorepos, filter commits by path if a specific package is targeted.

## Anti-Patterns

- **Do not classify internal refactors as breaking.** Removing a private helper function is not a breaking change. Only public API surface removals count.
- **Do not include every commit in non-technical notes.** Users don't care about CI config changes or test additions. Omit changes with no user-visible impact.
- **Do not guess the semver bump.** Base it strictly on the classification: breaking → MAJOR, features → MINOR, fixes-only → PATCH.
- **Do not use `git diff HEAD~N..HEAD` as a shortcut.** It ignores the 7-day window and breaks for repos with fewer than N commits.
- **Do not prompt the user with multiple follow-up questions.** Mention `gh release create --draft` once and let the user drive.

## Example Output

Given a repo with 8 commits over the last 7 days (2 features, 1 fix, 5 chores), latest tag `v1.4.2`:

### Technical Version
```markdown
# Release Notes — vesper v1.5.0
**Period:** 2026-02-16 → 2026-02-23 | **Bump:** MINOR (v1.4.2 → v1.5.0)
**Stats:** 8 commits, +342/-89 lines

## Features
- **Add Kimi provider support** — session-level provider isolation with encrypted credentials (`a9046851`, PR #87)
- **Auto-screenshot on build complete** — captures preview and renders Build Complete card (`4c9dbff4`)

## Fixes
- **Fix browser proxy URL validation** — add defense-in-depth URL and key validation to code mode browser proxy (`2219e0f9`)

## Other
- Hardened agent-teams mailbox auth and recovery (`a9046851`)
- Removed Team Watch notification system (`1a8a6d04`)
```

### Non-Technical Version
```markdown
# What's New — Vesper
**Released:** 2026-02-23

## New Features
- **Kimi AI Support** — you can now use Kimi as an AI provider alongside Claude
- **Build Previews** — completed builds now show an automatic screenshot preview

## Fixes
- **Browser Tool Security** — improved validation in the browser automation tool
```

## Success Criteria

- [ ] Both technical and non-technical versions produced in a single response
- [ ] Every non-technical item traces to a technical item
- [ ] Semver bump is justified by classification (not guessed)
- [ ] Commit hashes (7-char) included in technical notes
- [ ] No hashes, file paths, or jargon in non-technical notes
- [ ] Empty categories are skipped (not shown with "None")
- [ ] If no activity in 7 days, report states this and shows last activity date
- [ ] If `gh` unavailable, report notes "PR data not available"

## Next Steps

- Review the last 7 days of activity first: `skill: last7days`
- Compile agent-optimized changelog: `skill: agent-changelog`
- Persist findings as todos: `skill: file-todos`
