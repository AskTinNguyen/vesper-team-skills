# Public-docs-derived cross-agent skills

Notes from installing a GSAP workflow skill across Hermes, Codex, and Vesper from `https://gsap.com/` rather than from an upstream `SKILL.md` package.

## When this applies

Use this pattern when the user provides a public documentation site and asks to install a safe global skill for multiple agents, but the site does not provide a packaged skill.

## Safety checks

- Check for an agent-readable docs index first, especially `/llms.txt`.
- Check `/robots.txt` for crawling policy. A permissive robots file, and especially explicit AI crawler allow rules, is a strong safety signal for documentation summarization.
- Prefer a lightweight class-level workflow skill over mirroring large docs verbatim.
- Do not install packages or execute remote code just because a library site has install instructions. The skill should record official docs entry points and working rules.

## Metadata pitfall

Long YAML frontmatter descriptions that contain a colon must be quoted. If not quoted, Hermes can fall back to malformed simple parsing and mark the skill unsupported on the current platform because `platforms: [linux, macos, windows]` is parsed as a string instead of a list.

Bad:

```yaml
description: Use when working with Library: timelines, plugins, examples
platforms: [linux, macos, windows]
```

Good:

```yaml
description: "Use when working with Library: timelines, plugins, examples"
platforms: [linux, macos, windows]
```

## Verification checklist

- `skill_view("<name>")` succeeds for the Hermes copy.
- `hermes skills list` shows the skill enabled.
- Every target copy has `SKILL.md` under:
  - Hermes: `~/.hermes/skills/<category>/<name>/SKILL.md`
  - Codex: `~/.codex/skills/<name>/SKILL.md`
  - Vesper: `~/.vesper/skills/<name>/SKILL.md`
- Parse frontmatter for Codex/Vesper copies if possible and confirm `platforms` is a list and matches the current OS.
