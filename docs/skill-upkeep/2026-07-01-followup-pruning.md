# 2026-07-01 Follow-Up Skill Pruning

Follow-up request:

1. Archive Claude Code-related skills, `gstack`, `heartbeat-implementer`,
   Ralph Loop-related skills, `rclone`, and `reducing-entropy`.
2. Move Vesper-specific app-focused skills into their own folder.

## Result

- Active discoverable `SKILL.md` files: 100 -> 88.
- Archived discoverable entries in this pass: 12 active entries, all renamed to
  `SKILL.archived.md`.
- Vesper app-focused entries moved but kept active: 15.
- Archive batch: `archive/skills/2026-07-01-followup-pruning/`.
- Vesper app folder: `vesper-app-skills/`.

## Archived

| Skill | Category | Archive path |
| --- | --- | --- |
| `agent-supervisor` | Claude Code task-list workflow | `archive/skills/2026-07-01-followup-pruning/agent-supervisor/SKILL.archived.md` |
| `claude-code-hooks` | Claude Code-specific | `archive/skills/2026-07-01-followup-pruning/claude-code-hooks/SKILL.archived.md` |
| `claude-md-improver` | Claude Code-specific | `archive/skills/2026-07-01-followup-pruning/claude-md-improver/SKILL.archived.md` |
| `create-agent-skills` | Claude Code skill authoring | `archive/skills/2026-07-01-followup-pruning/create-agent-skills/SKILL.archived.md` |
| `gstack` | Claude Code browser stack | `archive/skills/2026-07-01-followup-pruning/gstack/SKILL.archived.md` |
| `gstack/browse` | Nested gstack browser skill | `archive/skills/2026-07-01-followup-pruning/gstack/browse/SKILL.archived.md` |
| `github-sync` | Claude Code task-list workflow | `archive/skills/2026-07-01-followup-pruning/github-sync/SKILL.archived.md` |
| `heartbeat-implementer` | Requested archive | `archive/skills/2026-07-01-followup-pruning/heartbeat-implementer/SKILL.archived.md` |
| `ralph-loop` | Ralph Loop | `archive/skills/2026-07-01-followup-pruning/ralph-loop/SKILL.archived.md` |
| `ralph-loop/skills/commit` | Nested Ralph Loop skill | `archive/skills/2026-07-01-followup-pruning/ralph-loop/skills/commit/SKILL.archived.md` |
| `rclone` | Requested archive | `archive/skills/2026-07-01-followup-pruning/rclone/SKILL.archived.md` |
| `reducing-entropy` | Requested archive | `archive/skills/2026-07-01-followup-pruning/reducing-entropy/SKILL.archived.md` |
| `verify-and-ship` | Claude Code task-list workflow | `archive/skills/2026-07-01-followup-pruning/verify-and-ship/SKILL.archived.md` |

The active-count reduction is 12 because `gstack/browse` was already archived
before this pass; it moved with its parent package but did not reduce active
discovery again.

## Moved To `vesper-app-skills/`

- `build-electron-features`
- `edit-with-ai-pattern`
- `electron-bun-test-reviewer`
- `electron-cdp-testing`
- `electron-performance-hardening`
- `electron-ui-inspector`
- `ui-inspector-ai-handoff`
- `upgrading-vesper-schedules`
- `vesper-desloppify`
- `vesper-dev-instance-manager`
- `vesper-electron-testing`
- `vesper-monolith-refactor`
- `vesper-release-distribution`
- `vesper-style`
- `vesper-ui-visual-polish`

## Verification

```bash
find /Users/tinnguyen/vesper-team-skills -name SKILL.md -type f | wc -l
# 88

python3 - <<'PY'
from pathlib import Path
print(len(list(Path("/Users/tinnguyen/vesper-team-skills").rglob("SKILL.md"))))
PY
# 88

find /Users/tinnguyen/vesper-team-skills/archive/skills/2026-07-01-followup-pruning -name SKILL.md -type f
# no output
```
