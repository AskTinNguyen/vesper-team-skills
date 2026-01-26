# Vesper Team Skills

Shared skills for distribution via Vesper's Team Skills feature.

## Available Skills

| Skill | Description | Setup Required |
|-------|-------------|----------------|
| [agent-browser](./agent-browser/) | Browser automation using Vercel's agent-browser CLI | No |
| [agent-native-architecture](./agent-native-architecture/) | Agent-first software design patterns and principles | No |
| [andrew-kane-gem-writer](./andrew-kane-gem-writer/) | Ruby gem writing in Andrew Kane's proven style | No |
| [build-electron-features](./build-electron-features/) | Vesper Electron app feature patterns | No |
| [claude-code-hooks](./claude-code-hooks/) | Pre/post hooks for Claude Code tool executions | No |
| [compound-docs](./compound-docs/) | Categorized documentation for solved problems | No |
| [create-agent-skills](./create-agent-skills/) | Skill authoring guidance and templates | No |
| [dhh-rails-style](./dhh-rails-style/) | DHH/37signals Rails coding style | No |
| [dispatch](./dispatch/) | Multi-agent task coordination with parallel execution | **Yes** |
| [dspy-ruby](./dspy-ruby/) | DSPy.rb LLM framework patterns | No |
| [electron-cdp-testing](./electron-cdp-testing/) | CDP-based E2E testing for Electron apps | No |
| [elevenlabs](./elevenlabs/) | AI voiceover and sound generation | No |
| [every-style-editor](./every-style-editor/) | Every.com style guide compliance | No |
| [ffmpeg](./ffmpeg/) | Video/audio processing patterns | No |
| [file-todos](./file-todos/) | File-based todo tracking system | No |
| [flowy-flowchart](./flowy-flowchart/) | Inline flowchart diagrams in conversations | No |
| [flowy-ui-mockup](./flowy-ui-mockup/) | Inline iOS UI mockups in conversations | No |
| [frontend-design](./frontend-design/) | High-quality frontend UI generation | No |
| [gemini-imagegen](./gemini-imagegen/) | Image generation with Gemini API | No |
| [git-worktree](./git-worktree/) | Git worktree management | No |
| [github-intel](./github-intel/) | GitHub repository discovery and analysis | **Yes** |
| [launchpad-remotion](./launchpad-remotion/) | Launchpad Remotion components and patterns | No |
| [messaging-integration](./messaging-integration/) | WhatsApp/Slack/Telegram integration patterns | No |
| [playwright-recording](./playwright-recording/) | Browser recording with Playwright | No |
| [qmd-search](./qmd-search/) | On-device markdown search engine | No |
| [qwen-edit](./qwen-edit/) | AI image editing with Qwen | No |
| [ralph-loop](./ralph-loop/) | Autonomous coding workflow orchestration | **Yes** |
| [rclone](./rclone/) | Cloud storage file management | No |
| [remotion](./remotion/) | Programmatic video creation with React | No |
| [scheduled-codebase-review](./scheduled-codebase-review/) | Multi-agent codebase analysis | No |
| [skill-creator](./skill-creator/) | Skill creation guidance | No |

## Usage

### For Team Admins

1. Clone this repo
2. Add/update skills (each skill = directory with `SKILL.md`)
3. Commit and push

### For Team Members

1. Open Vesper Settings → Workspace → Team Skills
2. Enter repo URL: `AskTinNguyen/vesper-team-skills`
3. Enter GitHub PAT (with `repo` scope for private repos)
4. Click "Save & Sync"

Skills will appear in your skills list with a "Team" badge.

## Post-Sync Setup

Some skills require additional setup after syncing:

### dispatch
Installs `cc` and `ccd` commands for task coordination:
```bash
~/.vesper/team-skills/dispatch/setup.sh
```

### github-intel
Installs discovery and extraction scripts:
```bash
~/.vesper/team-skills/github-intel/install.sh
```

### ralph-loop
Installs the `ralph` command for autonomous workflows:
```bash
~/.vesper/team-skills/ralph-loop/install.sh
```

## Adding New Skills

1. Create a directory: `my-skill/`
2. Add `SKILL.md` with YAML frontmatter:

```markdown
---
name: My Skill
description: What the skill does
icon: optional-emoji
---

# Instructions here...
```

3. Commit and push
4. Team members click "Sync" to get the new skill

## Skill Structure

```
skill-name/
├── SKILL.md          # Required: YAML frontmatter + instructions
├── setup.sh          # Optional: Post-sync setup script
├── scripts/          # Optional: Helper scripts
├── references/       # Optional: Reference documentation
├── templates/        # Optional: File templates
└── ...               # Any additional files
```
