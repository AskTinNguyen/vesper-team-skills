# Repo Hygiene Report Template

```md
# Repo Hygiene Report — {{date}}

## Executive Summary
- Status:
- Repo:
- Base branch:
- Worktrees reviewed:
- Actions taken:
- Items still needing attention:

## Actions Taken
- Removed worktrees:
- Deleted merged branches:
- Forced cleanup performed:
- Nothing changed:

## Safe Cleanup Completed
| Type | Branch | Path | Reason |
|---|---|---|---|
| worktree | feature/foo | /path/to/worktree | merged and clean |

## Safe Cleanup Recommended But Not Applied
| Type | Branch | Path | Reason |
|---|---|---|---|
| branch | feature/bar | — | merged locally but awaiting confirmation |

## Flagged For Action
| Type | Branch | Path | Reason | Recommended next action |
|---|---|---|---|---|
| worktree | feature/baz | /path/to/worktree | dirty worktree | commit / stash / discard |
| branch | feature/qux | — | no upstream and not merged | review ownership |

## Conflicts Flagged
| Branch | Path | Conflict files | Recommendation |
|---|---|---|---|
| tmp/merge-check-123 | /path/to/worktree | `sessions.ts`, `FreeFormInput.tsx` | resolve or remove only if disposable and requested |

## Escalations / Risk Calls
- Root repo dirty:
- Current branch behind upstream:
- Branches without upstream:
- Dirty worktrees:
- Other risks:

## Hygiene Recommendations
1.
2.
3.

## Command Evidence
- `git fetch --prune origin`
- `git remote prune origin`
- `git worktree prune`
- `bun run git:hygiene:json` or `bash scripts/git-hygiene-check.sh --json --refresh`
- `bun run worktree:check` or `bash scripts/worktree-hygiene.sh --check`
- custom merged-branch / conflict scan
```
