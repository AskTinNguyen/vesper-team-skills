# GitHub Intelligence Skill - Installation Guide

Global skill for discovering and analyzing GitHub repositories with AI-powered extraction.

## Quick Install

### Option 1: Claude Code Plugin Directory

```bash
# Download and extract to Claude Code skills directory
cd ~/.claude/skills  # or your custom skills directory
curl -L https://github.com/YOUR_REPO/releases/latest/download/github-intel-skill.tar.gz | tar xz
```

### Option 2: Manual Installation

```bash
# Extract to any location
tar -xzf github-intel-skill.tar.gz

# Add to Claude Code skills path
export CLAUDE_SKILLS_PATH="/path/to/github-intel-skill:$CLAUDE_SKILLS_PATH"
```

### Option 3: Local Install (Development)

```bash
# Clone or copy to your project
cp -r github-intel-skill /your/project/skills/

# Skill will be auto-discovered by Claude Code
```

## Prerequisites

1. **GitHub CLI** - Required for API access
   ```bash
   brew install gh  # macOS
   # or: sudo apt install gh  # Ubuntu/Debian
   ```

2. **GitHub Authentication**
   ```bash
   gh auth login
   ```

3. **QMD (Optional)** - For semantic search
   ```bash
   npm install -g qmd
   # or: pip install qmd
   ```

4. **jq** - JSON processing
   ```bash
   brew install jq  # macOS
   # or: sudo apt install jq  # Ubuntu/Debian
   ```

## Verification

Test the skill is installed:

```bash
# Trigger via natural language
claude
> "discover trending Claude Code repos"

# Or use scripts directly
./github-intel-skill/scripts/run.sh --help
```

## Configuration

Edit `github-intel-skill/scripts/config.sh`:

```bash
# Customize search parameters
export MIN_STARS=50
export DAYS_AGO=90
export CRAWLER_KEYWORDS="claude-code mcp-server ai-coding"
```

## First Run

```bash
# Discover repositories
./github-intel-skill/scripts/run.sh discover

# Check results
./github-intel-skill/scripts/run.sh status

# Index for search (optional)
qmd collection add todos/repos --name ai-coding-repos --mask "*.md"
qmd embed
```

## Usage Examples

### Discover Trending Repos
```bash
./github-intel-skill/scripts/run.sh discover
```

### Explore Specific Repo
```bash
./github-intel-skill/scripts/run.sh explore anthropics-claude-code
```

### Batch Clone
```bash
./github-intel-skill/scripts/batch-explore.sh --top 10
```

### Search Indexed Repos
```bash
qmd vsearch "multi-agent orchestration" -c ai-coding-repos
```

## Directory Structure

```
github-intel-skill/
├── SKILL.md              # Main skill definition
├── INSTALL.md            # This file
├── agents/               # Subagent definitions
│   ├── repo-explorer.md
│   ├── code-reviewer.md
│   └── knowledge-extractor.md
├── references/           # Detailed guides
│   ├── workflow.md
│   └── subagents.md
├── examples/             # Templates
│   └── knowledge-entry.md
└── scripts/              # Executable tools
    ├── run.sh
    ├── discover.sh
    ├── generate-todos.sh
    ├── extract.sh
    ├── config.sh
    └── batch-explore.sh
```

## Troubleshooting

### "gh: command not found"
Install GitHub CLI: https://cli.github.com/

### "API rate limit exceeded"
```bash
# Increase delay in config.sh
export RATE_LIMIT_SLEEP=5

# Check rate limit
gh api rate_limit
```

### "Skill not loading"
```bash
# Verify Claude Code can find the skill
claude --list-skills | grep github-intel
```

## Updating

```bash
# Pull latest version
cd ~/.claude/skills/github-intel-skill
git pull  # if installed from git

# Or re-download
curl -L https://github.com/YOUR_REPO/releases/latest/download/github-intel-skill.tar.gz | tar xz
```

## Uninstall

```bash
# Remove skill directory
rm -rf ~/.claude/skills/github-intel-skill

# Clean up generated data (optional)
rm -rf todos/repos
rm -rf .clones
```

## Support

- Issues: https://github.com/YOUR_REPO/issues
- Documentation: See `SKILL.md` and `references/`
- Examples: See `examples/`

## License

See LICENSE file in the skill directory.
