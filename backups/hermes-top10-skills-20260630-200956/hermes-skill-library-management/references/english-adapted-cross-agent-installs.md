# English-adapted cross-agent skill installs

Use this when installing an upstream skill for Hermes plus Codex/Vesper and the source is non-English or partly non-English.

## Pattern

1. Resolve the actual skill repository from the user's link.
   - X/Twitter posts may only contain an article URL or `t.co`; use oEmbed/API mirrors if needed to find the GitHub repo.
   - Record the source repo and commit in installed metadata.
2. Clone/fetch the repository into a temporary directory.
3. Audit before installing.
   - Read `SKILL.md`, README/license, package metadata, executable scripts, templates, and references.
   - Search for network calls, shell execution, secret handling, prompt-injection language, and destructive commands.
   - Distinguish approval/risk-gate text from executable behavior.
4. Translate/adapt operational files for English users.
   - Prioritize `SKILL.md`, `references/*.md`, `agents/*.yaml`, templates, validators, and user-facing snippets.
   - README/HANDOFF/PRODUCT are lower priority unless they are part of runtime guidance.
   - Preserve code identifiers, class names, file paths, dimensions, URLs, command syntax, and HTML/CSS/JS behavior.
   - Translate user-facing prompts in code fences; keep platform names clear, e.g. `Xiaohongshu/Rednote` and `WeChat Official Account`.
   - After machine translation, scan for remaining CJK in operational files and patch manually. Some original-language examples may be useful only when explicitly labeled, but the user's default preference is English usability.
5. Normalize Hermes-compatible frontmatter.
   - Quote long descriptions when needed.
   - Add `platforms: [linux, macos, windows]` when platform-neutral.
   - Add metadata with `source`, `source_commit`, and an adaptation note.
   - Preserve the upstream license exactly. For AGPL skills, note attribution/source-availability obligations in the installed note.
6. Install full packages, not only `SKILL.md`.
   - Hermes: `~/.hermes/skills/<category>/<skill-name>/`
   - Codex: `~/.codex/skills/<skill-name>/`
   - Vesper: `~/.vesper/skills/<skill-name>/`
   - Mirror `assets/`, `references/`, `scripts/`, `agents/`, templates, and validators unless unsafe.
7. Verify.
   - Hermes: `skill_view(<name>)`, load at least one linked reference, and check `hermes skills list`.
   - Codex/Vesper: parse YAML frontmatter, count files, confirm key support files exist.
   - For translated installs, count remaining CJK in operational files and report the count.
   - Run a lightweight script/validator smoke test if safe and dependencies are available.
8. Clean up temporary clones and generated credential/runtime files.

## Pitfalls

- Do not assume an English README means the operational skill files are English. Count CJK across `SKILL.md` and references.
- Do not over-translate code or design tokens. Preserve CSS classes, data attributes, package names, and command syntax.
- Do not erase the upstream license while adapting. License can materially affect safe redistribution.
- Avoid claiming full translation of every repository note if only operational files were translated; say exactly what was adapted.
