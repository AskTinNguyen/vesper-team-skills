# Weekly curation validation pattern

Use this reference during proactive weekly skill-library-curation runs when validating Hermes/Codex/Vesper runtime skill roots and the backup repo.

## What to validate

For each scoped root:

- Count `SKILL.md` files recursively with `root.rglob('SKILL.md')`.
- Validate every `SKILL.md` frontmatter:
  - starts with `---`
  - has a closing `---`
  - YAML parses
  - includes non-empty `name` and `description`
- Detect weak descriptions only as triage signals, not automatic failures.
- Scan Markdown links for local resource references and classify broken references as follow-up unless there is an obvious owned target.
- For a skill synced across runtimes, compare content hashes for `SKILL.md` and required support files.
- After any backup repo fetch/rebase/push, re-run this validation. Remote changes can alter inventory or nearby files.

## Avoid false positives

- Do not treat top-level category folders as missing-skill failures. Roots such as `apple/`, `research/`, `openclaw-imports/`, `.archive/`, `devops/`, or `software-development/` often intentionally group nested skills and do not need their own `SKILL.md`.
- Broad local-reference scans are triage signals. Markdown examples and vendored/plugin snapshots can look like broken links.
- Do not auto-fix vendored or plugin snapshot paths unless ownership is clear.
- Do not bulk-sync skills with the same frontmatter name when hashes differ; report them as drift/consolidation candidates.

## Minimal Python validator shape

```python
from pathlib import Path
import hashlib, re, sys, yaml

roots = {
    'Hermes': Path.home()/'.hermes/skills',
    'Codex': Path.home()/'.codex/skills',
    'VesperUser': Path.home()/'.vesper/skills',
    'VesperTeam': Path.home()/'.vesper/team-skills',
    'Backup': Path.home()/'vesper-team-skills',
}
link_re = re.compile(r'(?<!!)\[[^\]]+\]\(([^)]+)\)')

for label, root in roots.items():
    files = list(root.rglob('SKILL.md')) if root.exists() else []
    ok = 0
    broken = []
    for p in files:
        text = p.read_text(errors='replace')
        if not text.startswith('---\n'):
            raise SystemExit(f'{label}: no opening frontmatter: {p}')
        end = text.find('\n---', 4)
        if end == -1:
            raise SystemExit(f'{label}: no closing frontmatter: {p}')
        fm = yaml.safe_load(text[4:end]) or {}
        if not fm.get('name') or not fm.get('description'):
            raise SystemExit(f'{label}: missing name/description: {p}')
        ok += 1
        for m in link_re.finditer(text):
            target = m.group(1).strip().split('#', 1)[0]
            if not target or '://' in target or target.startswith(('#', '/', 'mailto:')):
                continue
            if (target.startswith(('references/', 'scripts/', 'templates/', 'assets/', '../'))
                    or Path(target).suffix in {'.md', '.py', '.sh', '.json', '.yaml', '.yml', '.txt'}):
                if not (p.parent / target).exists():
                    broken.append(f'{p}: {target}')
    print(f'{label}: SKILL.md={len(files)} frontmatter_ok={ok} broken_local_refs={len(broken)}')
```

## Reporting fields

Include:

- Skills changed and runtime install paths touched.
- Backup repo branch, commit hash, and push result when committed.
- Frontmatter validation counts per root.
- Hash comparison for synced files.
- Candidate duplicate/drift/resource-reference follow-ups.
- Unrelated dirty files intentionally skipped.
