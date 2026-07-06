# Weekly curation: frontmatter and sync lessons

Use this reference when running proactive weekly skill-library-curation across Hermes, Codex, Vesper user/team skills, and a backup repo.

## Durable checks

- Validate YAML frontmatter in every scoped `SKILL.md`, not only files touched in the backup repo.
- Quote long `description:` values when they contain colons, inline config labels, app paths, or other YAML-sensitive punctuation.
- Treat a missing `name:` in frontmatter as a safe metadata fix when the skill identity is obvious from the command/skill name.
- After runtime fixes, re-run frontmatter validation across all scoped roots and report counts per root.

## Backup repo staging pitfall

Some backup repos store command skills as lowercase command files, for example `commands/skill.md`, while runtime installs may use `commands/SKILL.md`. When staging backup changes, inspect `git status --short` and stage the tracked path actually reported by git. Do not assume every skill package uses a directory-level `SKILL.md` path.

## Safe sync rule

Only sync drift automatically when evidence is clear that one copy is newer and the change is low-risk, such as fixing invalid metadata or replacing stale release instructions with the already-curated backup copy. Large drift between app-specific runtimes should be reported as candidate follow-up rather than bulk-copied.

## Reporting reminders

Include:
- exact runtime paths touched
- backup branch and commit hash(es)
- validation counts for each root
- unresolved duplicate/drift/resource-reference candidates
- unrelated dirty files intentionally skipped
