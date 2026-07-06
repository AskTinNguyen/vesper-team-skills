# Cross-app skill sync pattern

Use this reference when a user asks to install or sync skills across Hermes, Codex App, Vesper App, and a backup repo.

## Common runtime roots

- Hermes: `~/.hermes/skills/`
- Codex App: `~/.codex/skills/`
- Vesper App user skills: `~/.vesper/skills/`
- Vesper team skills runtime: `~/.vesper/team-skills/`
- Backup repo, when present: `~/vesper-team-skills/`

## Operating pattern

1. Treat runtime install directories and backup repos as separate targets.
2. Copy the same skill package to each requested runtime root, preserving `SKILL.md` and any `references/`, `templates/`, `scripts/`, or `assets/` directories.
3. Validate every target copy before reporting success:
   - `SKILL.md` exists.
   - YAML frontmatter starts and ends cleanly.
   - `name` matches the intended skill name.
   - `description` is present.
4. If using Hermes, verify visibility with `hermes skills list` when available.
5. In backup repos, stage only the intended skill directories. Do not sweep unrelated dirty files into the commit.
6. Commit and push only after validation succeeds.

## Reporting

Include installed skill names, runtime paths touched, backup repo branch/commit, and any unrelated dirty files intentionally left unstaged.
