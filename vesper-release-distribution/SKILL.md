---
name: vesper-release-distribution
description: Use this skill to package and distribute a Vesper desktop release (macOS, Windows, Linux) by bumping all release version markers, pushing `main` and `release`, and running the GitHub Desktop build workflow to publish release assets and update manifests.
---

# Vesper Release Distribution

Use this skill when you want to ship a new desktop release to `sipherxyz/vesper` and publish all platform artifacts.

## What This Skill Automates

- Bumps `apps/electron/package.json` version.
- Bumps shared release markers such as `packages/shared/src/version/app-version.ts`.
- Bumps `apps/viewer/package.json` when that legacy workspace still exists.
- Refreshes `bun.lock` so workspace package versions stay in sync.
- Commits and pushes to `main`.
- Mirrors `main` to `release` branch.
- Triggers `.github/workflows/desktop.yml` on `release`.
- Watches workflow completion.
- Verifies GitHub Release and update manifest publication.

## Primary Command

```bash
skills/vesper-release-distribution/scripts/publish-release.sh --version 2.7.3
```

## Preconditions

- Run from repo root on `main`.
- Working tree should be clean.
- `gh` must be authenticated for `sipherxyz/vesper`.
- `bun`, `node`, `git`, and `gh` must be available.

## Notes

- Apple and Windows signing are optional; this flow works unsigned.
- The workflow runs against `release` to avoid `main` workflow concurrency stalls.
- The script verifies that `origin/release` matches the pushed release commit before dispatching the workflow.
- Keep the release version sources in sync; bumping only `apps/electron/package.json` can leave runtime prompts and workspace metadata on stale versions.
- If workflow fails, inspect the run URL and fix CI before retrying.

## Optional Flags

- `--repo owner/repo` to target a different repo.
- `--workflow desktop.yml` to use another workflow file.
- `--no-watch` to trigger and return immediately.
- `--allow-dirty` to bypass clean-tree guard (not recommended).

## Install Or Update (optional)

```bash
bun run scripts/install-skill-from-dir.ts \
  --src skills/vesper-release-distribution \
  --dest ~/.claude/skills \
  --force
```
