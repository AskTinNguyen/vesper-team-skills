# Vesper Team Skills

A curated collection of skills, commands, and workflows for Claude Code.

## Installation

```
/plugin marketplace add https://github.com/AskTinNguyen/vesper-team-skills
/plugin install vesper-team-skills
```

That's it. All skills and commands are now available in your Claude Code sessions.

## Skills

This repository intentionally keeps the active skill surface capped below **100 discoverable `SKILL.md` files**. Older, narrower, duplicate, or project-specific skill packages are kept recoverable under [`archive/skills/`](archive/skills/) with `SKILL.archived.md` filenames so they do not load by default.

The current active set has **93 discoverable `SKILL.md` files**. Vesper app-focused skills live under [`vesper-app-skills/`](vesper-app-skills/) so they stay active while remaining grouped away from general-purpose skills.

The active set and archive decisions are documented in the latest upkeep reports:

- [2026-07-01 skill garden report](docs/skill-upkeep/2026-07-01-skill-garden.md)
- [2026-07-01 archive manifest](archive/skills/2026-07-01-skill-garden/MANIFEST.md)
- [2026-07-01 follow-up pruning report](docs/skill-upkeep/2026-07-01-followup-pruning.md)
- [2026-07-01 follow-up archive manifest](archive/skills/2026-07-01-followup-pruning/MANIFEST.md)

The retained surface favors broad workhorse skills for agent orchestration, Vesper app development, source-driven implementation, testing, GitHub/release workflow, skill upkeep, and a small media/research utility set. Restore archived skills only when they are actively needed or when they have been consolidated into a stronger umbrella skill.

To verify the active cap:

```bash
find . -name SKILL.md -type f | wc -l
```

## Commands

Run these with `/command-name` in Claude Code.

### Core Workflows

| Command | Description |
|---------|-------------|
| `/workflows:plan` | Transform feature descriptions into well-structured project plans |
| `/workflows:work` | Execute work plans efficiently while maintaining quality |
| `/workflows:review` | Exhaustive code reviews using multi-agent analysis and worktrees |
| `/workflows:compound` | Document a recently solved problem to compound your team's knowledge |
| `/workflows:design` | Deep-dive visual refinement for video scenes |
| `/workflows:bulk-review` | Review multiple PRs efficiently with batched single-agent reviews |

### Development

| Command | Description |
|---------|-------------|
| `/lfg` | Full autonomous engineering workflow |
| `/start-new-feature` | Understand the codebase, then decompose and orchestrate parallel development |
| `/sprint-plan` | Create an AI-agent-optimized sprint plan |
| `/deepen-plan` | Enhance a plan with parallel research agents |
| `/plan_review` | Have multiple specialized agents review a plan in parallel |
| `/simplify-code` | Dual-pass code simplification |
| `/agent-native-audit` | Comprehensive agent-native architecture review with scored principles |

### Issue & PR Management

| Command | Description |
|---------|-------------|
| `/dispatch-issues` | Pull GitHub issues into the task list and dispatch parallel agents |
| `/dispatch-tests` | Partition tests into zones and dispatch parallel agents |
| `/resolve_parallel` | Resolve all TODO comments using parallel processing |
| `/resolve_pr_parallel` | Resolve all PR comments using parallel processing |
| `/resolve_todo_parallel` | Resolve all pending CLI todos using parallel processing |
| `/reproduce-bug` | Reproduce and investigate a bug using logs and browser screenshots |
| `/triage` | Triage and categorize findings for the CLI todo system |

### Video & Media

| Command | Description |
|---------|-------------|
| `/video` | Video projects — list, resume, or create new |
| `/brand` | Brand profiles — list, edit, or create new |
| `/design` | Deep-dive visual refinement for video scenes |
| `/scene-review` | Review video scenes |
| `/record-demo` | Guided Playwright browser recording |
| `/feature-video` | Record a video walkthrough of a feature for the PR description |
| `/generate-voiceover` | Generate AI voiceover from script |
| `/redub` | Redub video with a different voice |

### Testing & QA

| Command | Description |
|---------|-------------|
| `/test-browser` | Run browser tests on pages affected by current PR or branch |
| `/xcode-test` | Build and test iOS apps on simulator |

### Documentation & Ops

| Command | Description |
|---------|-------------|
| `/changelog` | Create engaging changelogs for recent merges to main |
| `/last7days` | 7-day review of repo activity |
| `/deploy-docs` | Validate and prepare documentation for GitHub Pages |
| `/release-docs` | Build and update the documentation site |
| `/setup-statusline` | Set up ccstatusline integration |
| `/versions` | Check dependency versions and toolkit updates |
| `/template` | List available templates and their features |

### Skills Management

| Command | Description |
|---------|-------------|
| `/skills` | List installed skills or create new ones |
| `/create-agent-skill` | Create or edit Claude Code skills |
| `/heal-skill` | Fix incorrect SKILL.md files |
| `/generate_command` | Create a new custom slash command |
| `/contribute` | Share improvements — issues, PRs, skills, templates |
| `/report-bug` | Report a bug |

## Quick Start

After installation, skills activate automatically based on what you're doing. Use `/skills` to inspect the available skill surface in a Claude Code session.

For multi-agent orchestration, start with:

```
/lfg                    # Full autonomous workflow
/start-new-feature      # Break down and parallelize a feature
/dispatch-issues        # Pull GitHub issues and dispatch agents
```

## Alternative Installation

<details>
<summary>Manual installation (without plugin system)</summary>

### Clone and link

```bash
git clone https://github.com/AskTinNguyen/vesper-team-skills.git ~/vesper-team-skills
```

### For OpenClaw

See [openclaw-plugin/README.md](openclaw-plugin/README.md) for full installation and usage instructions.

### Adding new commands

Create `commands/your-command.md` with YAML frontmatter:

```markdown
---
name: your-command
description: What it does
argument-hint: "[optional args]"
---

Your command instructions here.
Use $ARGUMENTS for user input.
```

Commit and push — team members run `git pull`, no restart needed.

</details>

## License

MIT
