# Cross-agent global skill installs

Use when importing a third-party skill into multiple local agents rather than only Hermes.

## Directory conventions observed

- Hermes local class-level skill: `~/.hermes/skills/<category>/<name>/SKILL.md`
- Codex global skill: `~/.codex/skills/<name>/SKILL.md`
- Vesper global skill: `~/.vesper/skills/<name>/SKILL.md`

Copy adjacent support directories as well as `SKILL.md`. Script-backed design/UI skills often require `scripts/` and reference markdown to work.

## Hermes compatibility normalization

Hermes linked-file discovery expects support directories such as `references/`, `templates/`, and `scripts/`. If an upstream package uses `reference/` singular, preserve it for upstream script compatibility but also add a copied `references/` alias so `skill_view(name, file_path='references/foo.md')` works.

When upstream frontmatter contains harness-specific fields (for example Claude `allowed-tools`, `user-invocable`, `argument-hint`), remove or adapt them in the Hermes copy and add Hermes metadata:

```yaml
metadata:
  hermes:
    tags: [...]
    homepage: https://github.com/<owner>/<repo>
    source: https://github.com/<owner>/<repo>/tree/<ref>/<skill-path>
```

## Verification checklist

- Hermes: `skill_view(<name>)` succeeds and `hermes skills list` shows the skill enabled.
- Codex/Vesper: `SKILL.md` exists under the native global skill directory.
- Count files in each target to confirm support files were mirrored.
- If safe, run a lightweight bundled script such as `node <skill>/scripts/context.mjs` to catch missing relative dependencies.
- Clean up any temporary clone after install.
