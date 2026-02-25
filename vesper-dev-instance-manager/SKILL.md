---
name: vesper-dev-instance-manager
description: This skill should be used when creating, building, launching, or managing isolated numbered Vesper dev instances across git worktrees using Dev Build Marker environment variables, so production and other dev instances are not impacted.
---

# Vesper Dev Instance Manager

Create and manage isolated Vesper dev instances for feature testing across multiple worktrees.

## When To Use

Use this skill when:
- Building a separate Vesper dev app from a specific worktree.
- Launching `Dev #N` side-by-side with production or other dev instances.
- Ensuring isolated config/workspaces/deep links for test safety.
- Stopping or checking status of a specific dev instance.

## Marker Strategy

Always run Electron with explicit instance markers:

- `VESPER_DEV_MODE=1`
- `VESPER_INSTANCE_NUMBER=<N>`
- `VESPER_INSTANCE_ID=dev<N>-<worktree-slug>`
- `VESPER_CONFIG_DIR=~/.vesper-dev/dev<N>-<worktree-slug>`
- `VESPER_WORKSPACES_DIR=$VESPER_CONFIG_DIR/workspaces`
- `VESPER_APP_NAME=Vesper Dev #<N> (<worktree-slug>)`
- `VESPER_DEEPLINK_SCHEME=vesper-dev-<N>-<worktree-slug>`

This preserves strict isolation from:
- Production app (`~/.vesper`, `vesper://`)
- Other dev instances (`~/.vesper-dev/<other-id>`, other schemes)

## Workflow

1. (Optional) Create a new worktree from local `main`.
2. Move to the target worktree.
3. Run the manager script in `build-and-launch` mode.
4. Validate process and log output.
5. Share PID, log path, and stop command.

### Optional worktree creation

```bash
# Creates a clean worktree from local main without stashing or carrying unstaged changes
git worktree add /absolute/path/to/new-worktree main
```

## Install Or Update

Install this skill to global Claude skills so future agent sessions can discover it:

```bash
bun run scripts/install-skill-from-dir.ts \
  --src skills/vesper-dev-instance-manager \
  --dest ~/.claude/skills \
  --force
```

## Script

Use the bundled script:

- `scripts/manage-dev-instance.sh`

### Common commands

```bash
# Build + launch Dev #2 from current worktree
skills/vesper-dev-instance-manager/scripts/manage-dev-instance.sh \
  --instance-number 2 \
  --action build-and-launch

# Check status for Dev #2
skills/vesper-dev-instance-manager/scripts/manage-dev-instance.sh \
  --instance-number 2 \
  --action status

# Stop Dev #2
skills/vesper-dev-instance-manager/scripts/manage-dev-instance.sh \
  --instance-number 2 \
  --action stop
```

### Optional flags

- `--worktree <path>`: target worktree (defaults to current directory)
- `--skip-build`: skip build in `build-and-launch`
- `--profile-label <label>`: override slug used in marker paths/scheme

## Guardrails

- Do not reuse production markers (`vesper://`, `~/.vesper`) for dev testing.
- Prefer numbered instances for visual clarity (`VESPER_INSTANCE_NUMBER`).
- Before launching, stop the same numbered profile if already running.
- If `node_modules` is missing in a worktree, link from the git common root when available.

## Agent Response Contract

After each run, report:
- `instance_number`
- `worktree`
- `instance_id`
- `config_dir`
- `deeplink_scheme`
- `running_pid` (or `not running`)
- `log_file`
- exact `stop` command

## References

- `docs/dev-prod-side-by-side.md`
- `scripts/detect-instance.sh`
- `apps/electron/src/main/index.ts`
