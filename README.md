# Vesper Team Skills

A curated collection of skills, commands, and workflows for Claude Code.

## Installation

```
/plugin marketplace add https://github.com/AskTinNguyen/vesper-team-skills
/plugin install vesper-team-skills
```

That's it. All skills and commands are now available in your Claude Code sessions.

## Skills

### Multi-Agent Orchestration

| Skill | Description |
|-------|-------------|
| [dispatch](dispatch/) | Coordinate complex features with parallel subagent execution |
| [agent-supervisor](agent-supervisor/) | Monitor task lists, detect gaps, and track agent status without doing implementation |
| [github-sync](github-sync/) | Synchronize GitHub PRs and issues into the Claude Code task list |
| [ralph-loop](ralph-loop/) | Trigger and manage Ralph Loop autonomous coding workflows |

### Code Quality & Review

| Skill | Description |
|-------|-------------|
| [code-review-expert](code-review-expert/) | Expert code review with a senior engineer lens — SOLID violations, security risks |
| [code-simplifier](code-simplifier/) | Simplify and refine code for clarity and maintainability |
| [code-quality-hook](code-quality-hook/) | PostToolUse hook that checks code quality after Edit/Write operations |
| [reducing-entropy](reducing-entropy/) | Minimize total codebase size — biases toward deletion |
| [verify-and-ship](verify-and-ship/) | Verify agent work output, commit, push, and create PRs |
| [scheduled-codebase-review](scheduled-codebase-review/) | Periodic deep reviews of the entire codebase using multi-agent analysis |

### Project Management & Planning

| Skill | Description |
|-------|-------------|
| [ship-notes](ship-notes/) | Generate release notes from recent git activity |
| [last7days](last7days/) | Review the last 7 days of activity in a git repository |
| [agent-changelog](agent-changelog/) | Compile an agent-optimized changelog from git history |
| [compound-docs](compound-docs/) | Capture solved problems as categorized documentation |
| [feature-specification](feature-specification/) | Write comprehensive feature specifications for product and engineering |

### CLAUDE.md & Skills Authoring

| Skill | Description |
|-------|-------------|
| [claude-md-improver](claude-md-improver/) | Audit and improve CLAUDE.md files in repositories |
| [claudemd-reviewer](claudemd-reviewer/) | Review and analyze CLAUDE.md hierarchy in repositories |
| [create-agent-skills](create-agent-skills/) | Expert guidance for creating and refining Claude Code skills |
| [skill-creator](skill-creator/) | Guide for creating effective skills |
| [skill-enricher](skill-enricher/) | Cross-reference a skill with its source repo to fill gaps |
| [skill-qa-release-guardian](skill-qa-release-guardian/) | Automated release QA with UI testing, regression verification, and bug reporting |
| [claude-code-hooks](claude-code-hooks/) | Implement pre-hooks and post-hooks for Claude Code |

### Video & Media Production

| Skill | Description |
|-------|-------------|
| [remotion](remotion/) | Create programmatic videos using React with Remotion |
| [launchpad-remotion](launchpad-remotion/) | Reusable components and brand assets for the trycua/launchpad Remotion monorepo |
| [ffmpeg](ffmpeg/) | Video and audio processing — format conversion, resizing, compression |
| [playwright-recording](playwright-recording/) | Record browser interactions as video using Playwright |
| [gemini-imagegen](gemini-imagegen/) | Generate and edit images using the Gemini API |

### Browser Automation & Testing

| Skill | Description |
|-------|-------------|
| [agent-browser](agent-browser/) | Browser automation using Vercel's agent-browser CLI |
| [webapp-testing](webapp-testing/) | Test local web applications using Playwright |
| [electron-cdp-testing](electron-cdp-testing/) | Automated E2E testing for Electron apps using Chrome DevTools Protocol |

### Architecture & Design

| Skill | Description |
|-------|-------------|
| [agent-native-architecture](agent-native-architecture/) | Build applications where agents are first-class citizens |
| [model-shaped-harness](model-shaped-harness/) | Design low-token, high-capability model-facing tool harnesses with code mode and profile-driven mounting |
| [architectural-review](architectural-review/) | Review architectural drawings, floor plans, and interior design proposals |
| [frontend-design](frontend-design/) | Create distinctive, production-grade frontend interfaces |
| [edit-with-ai-pattern](edit-with-ai-pattern/) | Build "Edit with AI" features for natural language editing of settings and data |
| [build-electron-features](build-electron-features/) | Build full-stack features for the Vesper Electron app |
| [electron-ui-inspector](electron-ui-inspector/) | Build live Electron UI inspectors with runtime toggles, structured context capture, and agent parity tooling |
| [flowy-flowchart](flowy-flowchart/) | Create flowchart diagrams inline in the conversation |
| [flowy-ui-mockup](flowy-ui-mockup/) | Create UI mockups for iPhone and iPad apps |

### Game & Unreal

| Skill | Description |
|-------|-------------|
| [game-level-building-python](game-level-building-python/) | Generate reusable Unreal Python level-building generators, regional template packs, and configurable detail passes for compounds, gardens, gates, shrines, and other gameplay-first environments |

### Research & Intelligence

| Skill | Description |
|-------|-------------|
| [github-intel](github-intel/) | Discover trending repos, research AI coding tools, extract code patterns |
| [social30days](social30days/) | Research a topic from the last 30 days on social media |
| [news30days](news30days/) | Research a topic from the last 30 days in news outlets |
| [last30days](last30days/) | Research a topic from the last 30 days on Reddit + X + Web |
| [qmd-search](qmd-search/) | On-device semantic search for markdown documents |

### Ruby & Rails

| Skill | Description |
|-------|-------------|
| [dhh-rails-style](dhh-rails-style/) | Write Ruby and Rails code in DHH's 37signals style |
| [andrew-kane-gem-writer](andrew-kane-gem-writer/) | Write Ruby gems following Andrew Kane's patterns |
| [dspy-ruby](dspy-ruby/) | Build type-safe, composable LLM applications with DSPy.rb |

### DevOps & Utilities

| Skill | Description |
|-------|-------------|
| [git-worktree](git-worktree/) | Manage Git worktrees for isolated parallel development |
| [rclone](rclone/) | Upload, sync, and manage files across cloud storage providers |
| [messaging-integration](messaging-integration/) | Production-ready patterns for WhatsApp, Slack, and Telegram integration |
| [setup-statusline-advanced](setup-statusline-advanced/) | Set up an advanced Claude Code statusline with real-time session metrics |
| [3-layer-memory](3-layer-memory/) | Three-layer compounding memory system for AI assistants |
| [heartbeat-implementation](heartbeat-implementation/) | Implement periodic heartbeat systems in AI agent applications |

### Writing & Style

| Skill | Description |
|-------|-------------|
| [every-style-editor](every-style-editor/) | Review and edit copy for Every's style guide compliance |
| [sales-materials-creator](sales-materials-creator/) | Create sales decks and pitch decks using a feelings-first philosophy |

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
| `/skill` | Explicitly invoke a skill by name |
| `/create-agent-skill` | Create or edit Claude Code skills |
| `/heal-skill` | Fix incorrect SKILL.md files |
| `/generate_command` | Create a new custom slash command |
| `/contribute` | Share improvements — issues, PRs, skills, templates |
| `/report-bug` | Report a bug |

## Quick Start

After installation, skills activate automatically based on what you're doing. You can also invoke them explicitly:

```
/skill dispatch         # Coordinate parallel agents
/skill code-review      # Run expert code review
/skill remotion         # Create programmatic videos
```

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
