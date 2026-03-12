# Dispatch Skill

`dispatch` is a universal multi-agent orchestration skill. It teaches a portable protocol for decomposition, dependency management, worker assignment, monitoring, and recovery, then maps that protocol onto runtime-specific adapters.

## Install

### Team Skills

Sync the skill into Vesper Team Skills, then run:

```bash
~/.vesper/team-skills/dispatch/setup.sh
```

### Manual

```bash
mkdir -p ~/.claude/skills
cp -r dispatch ~/.claude/skills/
~/.claude/skills/dispatch/setup.sh
```

### Tarball or source checkout

```bash
./install.sh
./setup.sh
```

`setup.sh` auto-detects the installed skill path and installs:

- `cc` and `ccd`
- the archive hook installer

## Start Here

- Core skill: [SKILL.md](/Users/tinnguyen/vesper-team-skills/dispatch/SKILL.md)
- Universal workflow: [workflows/universal-dispatch.md](/Users/tinnguyen/vesper-team-skills/dispatch/workflows/universal-dispatch.md)
- Runtime contract: [references/runtime-primitives.md](/Users/tinnguyen/vesper-team-skills/dispatch/references/runtime-primitives.md)
- Claude Code adapter: [references/claude-code-adapter.md](/Users/tinnguyen/vesper-team-skills/dispatch/references/claude-code-adapter.md)

## Package Layout

```text
dispatch/
├── SKILL.md
├── README.md
├── setup.sh
├── install.sh
├── hooks/
├── references/
├── scripts/
└── workflows/
```

## Notes

- The core skill is runtime-agnostic.
- Claude-specific mechanics live in adapter docs and helper scripts.
- Manual installs target `~/.claude/skills/dispatch/`; Team Skills installs target `~/.vesper/team-skills/dispatch/`.
