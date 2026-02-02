# Vesper Team Skills

Shared skills and commands for distribution via Vesper's Team Skills feature or direct installation with Claude Code CLI.

## 🔌 Recommended: Anthropic's Official Knowledge Work Plugins

Anthropic open-sourced **11 enterprise plugins** for Claude Cowork & Claude Code — covering sales, finance, legal, data, marketing, support, product management, and more. These are high-quality, officially maintained plugins with connectors to popular tools (Slack, Notion, Jira, HubSpot, Snowflake, etc.).

**GitHub:** https://github.com/anthropics/knowledge-work-plugins
**Blog:** https://claude.com/blog/cowork-plugins

```bash
# Add the marketplace
claude plugin marketplace add anthropics/knowledge-work-plugins

# Install all 11 plugins
for p in productivity sales finance data legal marketing customer-support product-management enterprise-search bio-research cowork-plugin-management; do
  claude plugin install "$p@knowledge-work-plugins"
done
```

These complement our team skills — use Anthropic's plugins for general business workflows and our skills below for Ather-specific development workflows.

---

## Quick Start

### For Claude Code CLI Users (No Vesper Required)

Install skills and commands directly to your Claude Code directories:

```bash
# Clone the repository
git clone https://github.com/AskTinNguyen/vesper-team-skills ~/.claude/team-skills

# Symlink skills to Claude Code skills directory
ln -sf ~/.claude/team-skills/*/ ~/.claude/skills/ 2>/dev/null

# Copy commands to Claude Code commands directory
mkdir -p ~/.claude/commands
cp -r ~/.claude/team-skills/commands/* ~/.claude/commands/

# Run setup scripts for skills that require them (optional)
~/.claude/team-skills/dispatch/setup.sh      # cc and ccd commands
~/.claude/team-skills/github-intel/install.sh # GitHub discovery tools
~/.claude/team-skills/ralph-loop/install.sh   # ralph command
```

**To update later:**
```bash
cd ~/.claude/team-skills && git pull
cp -r commands/* ~/.claude/commands/
```

### For Vesper Users

See [Vesper Team Skills Setup](#for-vesper-users-auto-sync) below.

---

## Claude Code CLI Installation (Detailed)

This section provides detailed instructions for Claude Code CLI users who want to use these skills without the Vesper desktop app.

### Prerequisites

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed
- Git installed
- GitHub account with repository access (for private repos, a PAT with `repo` scope)

### Installation Methods

#### Method 1: Clone and Symlink (Recommended)

This method keeps skills updated via git pull and maintains the repository structure:

```bash
# 1. Clone to a dedicated directory
git clone https://github.com/AskTinNguyen/vesper-team-skills ~/.claude/team-skills

# 2. Create skills directory if it doesn't exist
mkdir -p ~/.claude/skills

# 3. Symlink each skill directory (excludes README and commands)
for skill in ~/.claude/team-skills/*/; do
  skill_name=$(basename "$skill")
  if [[ "$skill_name" != "commands" && -f "$skill/SKILL.md" ]]; then
    ln -sf "$skill" ~/.claude/skills/
    echo "Linked: $skill_name"
  fi
done

# 4. Copy commands (these need to be actual files, not symlinks)
mkdir -p ~/.claude/commands
cp -r ~/.claude/team-skills/commands/* ~/.claude/commands/
```

**Updating:**
```bash
cd ~/.claude/team-skills && git pull
# Skills auto-update via symlinks
# Commands need to be re-copied
cp -r commands/* ~/.claude/commands/
```

#### Method 2: Direct Copy

If you prefer not to use symlinks:

```bash
# Clone temporarily
git clone https://github.com/AskTinNguyen/vesper-team-skills /tmp/vesper-team-skills

# Copy skills (excluding non-skill directories)
mkdir -p ~/.claude/skills
for skill in /tmp/vesper-team-skills/*/; do
  skill_name=$(basename "$skill")
  if [[ "$skill_name" != "commands" && -f "$skill/SKILL.md" ]]; then
    cp -r "$skill" ~/.claude/skills/
    echo "Copied: $skill_name"
  fi
done

# Copy commands
mkdir -p ~/.claude/commands
cp -r /tmp/vesper-team-skills/commands/* ~/.claude/commands/

# Clean up
rm -rf /tmp/vesper-team-skills
```

#### Method 3: Selective Installation

Install only specific skills you need:

```bash
# Clone the repo
git clone https://github.com/AskTinNguyen/vesper-team-skills /tmp/vesper-team-skills

# Copy specific skills
mkdir -p ~/.claude/skills
cp -r /tmp/vesper-team-skills/remotion ~/.claude/skills/
cp -r /tmp/vesper-team-skills/ffmpeg ~/.claude/skills/
cp -r /tmp/vesper-team-skills/frontend-design ~/.claude/skills/

# Copy specific commands
mkdir -p ~/.claude/commands
cp /tmp/vesper-team-skills/commands/lfg.md ~/.claude/commands/
cp -r /tmp/vesper-team-skills/commands/workflows ~/.claude/commands/
```

### Post-Installation Setup

Some skills require additional setup after installation:

#### dispatch (Task Coordination)
```bash
# Installs 'cc' and 'ccd' commands for multi-agent task coordination
~/.claude/skills/dispatch/setup.sh
# Or if using symlink method:
~/.claude/team-skills/dispatch/setup.sh
```

#### github-intel (Repository Discovery)
```bash
# Installs discovery and extraction scripts
~/.claude/skills/github-intel/install.sh
# Or if using symlink method:
~/.claude/team-skills/github-intel/install.sh
```

#### ralph-loop (Autonomous Workflows)
```bash
# Installs the 'ralph' command for autonomous coding workflows
~/.claude/skills/ralph-loop/install.sh
# Or if using symlink method:
~/.claude/team-skills/ralph-loop/install.sh
```

### Verifying Installation

```bash
# List installed skills
ls -la ~/.claude/skills/

# List installed commands
ls -la ~/.claude/commands/

# In Claude Code, check available skills
# Type: "what skills do you have available?"
```

### Directory Structure After Installation

```
~/.claude/
├── skills/                    # Skills directory
│   ├── agent-browser/         # Symlink or copy
│   ├── dispatch/
│   ├── frontend-design/
│   ├── remotion/
│   └── ...
├── commands/                  # Commands directory
│   ├── lfg.md
│   ├── changelog.md
│   ├── workflows/
│   │   ├── work.md
│   │   ├── plan.md
│   │   ├── review.md
│   │   ├── bulk-review.md
│   │   └── compound.md
│   └── ...
└── team-skills/               # Source repo (if using Method 1)
    ├── README.md
    ├── commands/
    └── <skill-directories>/
```

### Updating Skills

**Method 1 (Symlink):**
```bash
cd ~/.claude/team-skills
git pull
# Skills update automatically via symlinks
# Re-copy commands
cp -r commands/* ~/.claude/commands/
```

**Method 2/3 (Direct Copy):**
```bash
git clone https://github.com/AskTinNguyen/vesper-team-skills /tmp/vesper-team-skills
# Re-copy desired skills and commands
cp -r /tmp/vesper-team-skills/<skill-name> ~/.claude/skills/
cp -r /tmp/vesper-team-skills/commands/* ~/.claude/commands/
rm -rf /tmp/vesper-team-skills
```

### Uninstalling

```bash
# Remove all team skills
rm -rf ~/.claude/skills/*
rm -rf ~/.claude/commands/*
rm -rf ~/.claude/team-skills

# Or remove specific skills
rm -rf ~/.claude/skills/dispatch
rm ~/.claude/commands/lfg.md
```

---

## For Vesper Users (Auto-Sync)

Vesper provides automatic syncing of team skills from this repository.

### Setup in Vesper

1. Open Vesper Settings (CMD+,)
2. Navigate to **Workspace** → **Team Skills**
3. Enter repo URL: `AskTinNguyen/vesper-team-skills`
4. Enter GitHub PAT (with `repo` scope for private repos)
5. Click **Save & Sync**

Skills will appear in your skills list with a "Team" badge.

### Manual Sync

To get the latest skills:
1. Open Vesper Settings
2. Go to Team Skills section
3. Click the **Sync** button

### Commands Installation (Manual)

Commands are not auto-synced by Vesper and need manual installation:

```bash
# Clone repo (if not already)
git clone https://github.com/AskTinNguyen/vesper-team-skills /tmp/vesper-team-skills

# Copy commands to Claude Code
cp -r /tmp/vesper-team-skills/commands/* ~/.claude/commands/

# Verify
ls ~/.claude/commands/
```

---

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

## Available Commands

Slash commands invoked with `/command-name` in Claude Code.

| Command | Description |
|---------|-------------|
| `/agent-native-audit` | Run comprehensive agent-native architecture review |
| `/brand` | Brand profile management |
| `/changelog` | Generate changelogs from recent merges |
| `/contribute` | Share improvements (issues, PRs, skills) |
| `/create-agent-skill` | Create or edit Claude Code skills |
| `/deepen-plan` | Enhance plans with parallel research agents |
| `/deploy-docs` | Validate and prepare docs for deployment |
| `/design` | Design refinement workflow |
| `/feature-video` | Record feature walkthrough for PR |
| `/generate_command` | Create new custom slash commands |
| `/generate-voiceover` | Generate AI voiceover from script |
| `/heal-skill` | Fix incorrect SKILL.md files |
| `/lfg` | Full autonomous engineering workflow |
| `/plan_review` | Multi-agent plan review |
| `/record-demo` | Guided Playwright browser recording |
| `/redub` | Redub video with different voice |
| `/release-docs` | Build and update documentation site |
| `/report-bug` | Report a bug workflow |
| `/reproduce-bug` | Bug investigation workflow |
| `/resolve_parallel` | Resolve TODO comments in parallel |
| `/resolve_pr_parallel` | Resolve PR comments in parallel |
| `/resolve_todo_parallel` | Resolve CLI todos in parallel |
| `/scene-review` | Scene review workflow |
| `/setup-statusline` | Setup ccstatusline integration |
| `/skills` | List installed skills or create new |
| `/template` | List available templates |
| `/test-browser` | Run browser tests for PR |
| `/triage` | Triage and categorize findings |
| `/versions` | Check dependency versions |
| `/video` | Video project management |
| `/xcode-test` | Build and test iOS apps on simulator |

### Workflows

Core workflows in `commands/workflows/`:

| Workflow | Command | Description |
|----------|---------|-------------|
| Work | `/workflows:work` | Execute work plans efficiently |
| Plan | `/workflows:plan` | Transform features into structured project plans |
| Review | `/workflows:review` | Exhaustive multi-agent code reviews |
| Bulk Review | `/workflows:bulk-review` | Batched single-agent reviews for 4+ PRs |
| Compound | `/workflows:compound` | Document solved problems to compound knowledge |

---

## For Team Admins

### Adding New Skills

1. Create a directory: `my-skill/`
2. Add `SKILL.md` with YAML frontmatter:

```markdown
---
name: My Skill
description: What the skill does
icon: optional-emoji
globs:           # Optional: auto-activate for matching files
  - "**/*.tsx"
alwaysAllow:     # Optional: tools to always allow
  - Read
  - Grep
---

# Skill Instructions

Your instructions here...
```

3. Commit and push
4. Vesper users click "Sync", CLI users run `git pull`

### Adding New Commands

1. Create a markdown file: `commands/my-command.md`
2. Add command content (no frontmatter needed)
3. Commit and push
4. Users copy to `~/.claude/commands/`

### Skill Directory Structure

```
my-skill/
├── SKILL.md       # Required: YAML frontmatter + instructions
├── setup.sh       # Optional: Post-install setup script
├── install.sh     # Optional: Alternative setup script name
├── scripts/       # Optional: Helper scripts
├── references/    # Optional: Reference documentation
└── templates/     # Optional: File templates
```

---

## Skill Precedence (Vesper)

When using Vesper, skills are loaded with **first-wins** precedence:

| Priority | Source | Location |
|----------|--------|----------|
| 1 (highest) | Workspace | `~/.vesper/workspaces/{id}/skills/` |
| 2 | Team | `~/.vesper/team-skills/` |
| 3 (lowest) | Claude Code | `~/.claude/skills/` |

Skills are deduplicated by **slug** (directory name). If a skill exists in multiple locations, only the highest-priority version loads.

### For Claude Code CLI Users

Claude Code loads skills from `~/.claude/skills/` only. If you have multiple skills with the same name from different sources, resolve conflicts manually by keeping only the version you want.

---

## Troubleshooting

### Skills Not Appearing in Claude Code

1. Verify the skill directory exists: `ls ~/.claude/skills/`
2. Check that `SKILL.md` exists in each skill directory
3. Ensure the SKILL.md has valid YAML frontmatter
4. Restart Claude Code CLI

### Git Clone Fails (Private Repository)

For private repositories, authenticate with GitHub:

```bash
# Option 1: HTTPS with PAT
git clone https://<PAT>@github.com/AskTinNguyen/vesper-team-skills ~/.claude/team-skills

# Option 2: SSH (if configured)
git clone git@github.com:AskTinNguyen/vesper-team-skills.git ~/.claude/team-skills

# Option 3: GitHub CLI
gh repo clone AskTinNguyen/vesper-team-skills ~/.claude/team-skills
```

### Symlinks Not Working

If symlinks don't work on your system:

```bash
# Remove symlinks and copy instead
rm ~/.claude/skills/*
for skill in ~/.claude/team-skills/*/; do
  skill_name=$(basename "$skill")
  if [[ "$skill_name" != "commands" && -f "$skill/SKILL.md" ]]; then
    cp -r "$skill" ~/.claude/skills/
  fi
done
```

### Commands Not Found

Ensure commands are in the correct directory:

```bash
ls ~/.claude/commands/
# Should show .md files like lfg.md, changelog.md, etc.
```

Commands must be `.md` files directly in `~/.claude/commands/` (workflows go in `~/.claude/commands/workflows/`).

---

## Repository Structure

```
vesper-team-skills/
├── README.md
├── commands/           # Slash commands (manual install required)
│   ├── *.md           # Individual commands
│   └── workflows/     # Core workflow commands
│       ├── work.md
│       ├── plan.md
│       ├── review.md
│       ├── bulk-review.md
│       └── compound.md
└── <skill-name>/      # Skills (auto-sync via Vesper or manual install)
    ├── SKILL.md       # Required: YAML frontmatter + instructions
    ├── setup.sh       # Optional: Post-sync setup script
    ├── scripts/       # Optional: Helper scripts
    ├── references/    # Optional: Reference documentation
    └── templates/     # Optional: File templates
```
