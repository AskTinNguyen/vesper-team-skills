# Codex upstream import notes

Session pattern captured:
- User asked to "find SKILLs from Codex CLI and make it available in Hermes".
- Local Codex npm install existed, but the installed package did not include the upstream `.codex/skills/` directory.
- Upstream GitHub repo `openai/codex` did expose `.codex/skills/`.

## Durable takeaways

1. Check both places:
   - local installed package
   - upstream repository

2. For Codex specifically:
   - upstream skills live under `.codex/skills/`
   - the installed package may still expose only the binary/README and omit those skill assets

3. Safe local naming convention used successfully:
   - `codex-upstream-<skill-name>`

4. Metadata compatibility caveat:
   - Quoted YAML dates are required for safe downstream JSON serialization in Hermes skill inspection.
   - Example:
     - good: `imported_at: "2026-05-27"`
     - bad: `imported_at: 2026-05-27`

5. Verification pattern:
   - confirm imported names show in skills listing
   - load at least one imported skill with `skill_view`

## Imported Codex upstream skills in the reference session

- `codex-upstream-babysit-pr`
- `codex-upstream-code-review`
- `codex-upstream-code-review-breaking-changes`
- `codex-upstream-code-review-change-size`
- `codex-upstream-code-review-context`
- `codex-upstream-code-review-testing`
- `codex-upstream-codex-bug`
- `codex-upstream-codex-issue-digest`
- `codex-upstream-codex-pr-body`
- `codex-upstream-remote-tests`
- `codex-upstream-test-tui`
- `codex-upstream-update-v8-version`

## Scope warning

This import copied only `SKILL.md` instructions. Some upstream skills mention scripts or references adjacent to the skill in the source repo. If a user wants full operational parity, do a second pass to mirror the support files into Hermes under `references/`, `templates/`, or `scripts/` as appropriate.
