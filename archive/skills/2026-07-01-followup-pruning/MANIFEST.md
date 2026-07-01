# 2026-07-01 Follow-Up Skill Pruning Manifest

This archive batch records the explicit follow-up pruning requested after the
main 2026-07-01 skill garden pass.

Archived entries are kept with their support files, but every active entrypoint
has been renamed from `SKILL.md` to `SKILL.archived.md` so recursive skill
discovery does not load them by default.

To restore an archived skill, move its package back to the repository root and
rename its entry file back to `SKILL.md`. For nested entries, restore only the
nested skill you intend to make active.

| Original path | Archive path | Reason |
| --- | --- | --- |
| `agent-supervisor/` | `archive/skills/2026-07-01-followup-pruning/agent-supervisor/` | Claude Code task-list supervision workflow. |
| `claude-code-hooks/` | `archive/skills/2026-07-01-followup-pruning/claude-code-hooks/` | Claude Code-specific hook automation. |
| `claude-md-improver/` | `archive/skills/2026-07-01-followup-pruning/claude-md-improver/` | Claude Code-specific `CLAUDE.md` upkeep. |
| `create-agent-skills/` | `archive/skills/2026-07-01-followup-pruning/create-agent-skills/` | Claude Code skill-authoring package superseded by the retained `skill-creator` and upkeep skills. |
| `gstack/` | `archive/skills/2026-07-01-followup-pruning/gstack/` | Claude Code-oriented browser stack requested for archival. |
| `github-sync/` | `archive/skills/2026-07-01-followup-pruning/github-sync/` | Claude Code task-list synchronization workflow. |
| `heartbeat-implementer/` | `archive/skills/2026-07-01-followup-pruning/heartbeat-implementer/` | Requested for archival. |
| `ralph-loop/` | `archive/skills/2026-07-01-followup-pruning/ralph-loop/` | Ralph Loop package requested for archival. |
| `ralph-loop/skills/commit/` | `archive/skills/2026-07-01-followup-pruning/ralph-loop/skills/commit/` | Nested Ralph Loop commit skill archived with its parent. |
| `rclone/` | `archive/skills/2026-07-01-followup-pruning/rclone/` | Requested for archival. |
| `reducing-entropy/` | `archive/skills/2026-07-01-followup-pruning/reducing-entropy/` | Requested for archival. |
| `verify-and-ship/` | `archive/skills/2026-07-01-followup-pruning/verify-and-ship/` | Claude Code task-list verification and shipping workflow. |

Vesper app-focused skills were not archived. They were moved under
`vesper-app-skills/` so the active catalog has a clearer shape.
