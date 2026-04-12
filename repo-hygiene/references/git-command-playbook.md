# Git Command Playbook

Use these commands to build a repo hygiene snapshot.

## Repo snapshot

```bash
git rev-parse --show-toplevel
git remote get-url origin
git status --short --branch
git branch -vv
git worktree list --porcelain
```

## Refresh refs

```bash
git fetch --prune origin
git remote prune origin
git worktree prune
```

## Local branches already merged

```bash
git branch --merged main
```

## Branches with gone upstream

```bash
git branch -vv | grep ': gone' || true
```

## Branches without upstream

```bash
git for-each-ref --format='%(refname:short)' refs/heads |
while read -r branch; do
  git rev-parse --abbrev-ref "${branch}@{upstream}" >/dev/null 2>&1 || echo "$branch"
done
```

## Worktree cleanliness

```bash
while IFS= read -r wt; do
  dirty=$(git -C "$wt" status --porcelain | wc -l | tr -d ' ')
  branch=$(git -C "$wt" branch --show-current)
  printf '%s\t%s\tdirty=%s\n' "$wt" "$branch" "$dirty"
done < <(git worktree list --porcelain | awk '/^worktree /{print substr($0,10)}')
```

## Conflict scan across worktrees

```bash
while IFS= read -r wt; do
  status=$(git -C "$wt" status --porcelain || true)
  if printf '%s\n' "$status" | grep -qE '^(UU|AA|DD|AU|UA|DU|UD)'; then
    printf 'CONFLICT\t%s\n' "$wt"
    printf '%s\n' "$status" | grep -E '^(UU|AA|DD|AU|UA|DU|UD)'
    echo
  fi
done < <(git worktree list --porcelain | awk '/^worktree /{print substr($0,10)}')
```

## Check whether a branch is merged

```bash
git merge-base --is-ancestor <branch> main
git merge-base --is-ancestor <branch> origin/main
```

## Ahead / behind relative to main

```bash
git rev-list --left-right --count main...<branch>
```

## Safe cleanup primitives

### Remove a clean worktree

```bash
git worktree remove <path>
```

### Force-remove a disposable conflicted worktree

```bash
git worktree remove --force <path>
```

### Delete a merged branch

```bash
git branch -d <branch>
```

## Existing Vesper helpers

Prefer repo-native aliases when present:

```bash
bun run git:hygiene:json
bun run worktree:check
```

Fallback when the repo does not expose those aliases:

```bash
bash scripts/git-hygiene-check.sh --json --refresh
bash scripts/worktree-hygiene.sh --check
```

Notes:
- these helpers give a fast baseline before targeted cleanup
- they do not replace the explicit fetch/prune step shown above
