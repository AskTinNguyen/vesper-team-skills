# GitHub Intelligence Skill

🔍 Automated discovery and analysis of GitHub repositories to extract valuable code, patterns, and best practices.

## Overview

This Claude Code skill provides a complete pipeline for:
- **Discovery** - Find trending repos with GitHub API
- **Indexing** - Semantic vector search via QMD
- **Exploration** - AI-powered codebase analysis
- **Extraction** - Knowledge compound documentation
- **Orchestration** - Multi-subagent research workflows

## Quick Start

```bash
# Install (see INSTALL.md for details)
tar -xzf github-intel-skill.tar.gz
cd github-intel-skill

# Discover trending repos
./scripts/run.sh discover

# Explore a specific repo
./scripts/run.sh explore anthropics-claude-code
```

## Features

### 🤖 Subagent Orchestration

Launch parallel Sonnet agents for deep analysis:

- **repo-explorer** - Codebase structure analysis
- **code-reviewer** - Pattern extraction & best practices
- **knowledge-extractor** - Compound documentation generation

### 🔎 Semantic Search

Integrates with QMD for vector-based discovery:

```bash
qmd vsearch "multi-agent orchestration" -c ai-coding-repos
```

### 📊 Smart Discovery

- GitHub API integration via `gh` CLI
- Configurable filters (stars, recency, keywords)
- Automatic deduplication
- Rate limit handling

### 📚 Knowledge Pipeline

```
Discover → Index → Explore → Extract → Document
   ↓         ↓        ↓         ↓         ↓
TODOs    Vectors   .clones   Analysis  knowledge/
```

## Commands

| Command | Description |
|---------|-------------|
| `./scripts/run.sh discover` | Find trending repos |
| `./scripts/run.sh explore <repo>` | Clone and prepare repo |
| `./scripts/run.sh status` | Show discovery stats |
| `./scripts/batch-explore.sh --top N` | Batch clone top N repos |
| `./scripts/extract.sh add <cat> <name>` | Extract knowledge entry |

## Skill Triggers

The skill activates on these phrases:
- "discover trending repos"
- "find GitHub repositories"
- "research AI coding tools"
- "crawl GitHub for best practices"
- "extract code patterns from repos"
- "build knowledge from GitHub"
- "find Claude Code extensions"
- "discover MCP servers"

## Configuration

Edit `scripts/config.sh`:

```bash
MIN_STARS=50              # Minimum star threshold
DAYS_AGO=90               # Max days since update
RATE_LIMIT_SLEEP=2        # API rate limiting
CRAWLER_KEYWORDS=(...)    # Search keywords
```

## Example Workflow

### 1. Discover Repos

```bash
./scripts/run.sh discover
# Output: todos/repos/*.md (442 repos)
```

### 2. Index for Search

```bash
qmd collection add todos/repos --name ai-coding-repos --mask "*.md"
qmd embed
```

### 3. Find Relevant Repos

```bash
qmd vsearch "claude skills" -c ai-coding-repos -n 10
```

### 4. Batch Clone

```bash
./scripts/batch-explore.sh --top 10
```

### 5. Launch Exploration Agents

```
In Claude Code:

> Launch 5 repo-explorer agents in parallel to analyze:
> .clones/repo1, .clones/repo2, .clones/repo3, .clones/repo4, .clones/repo5
```

### 6. Extract Knowledge

```bash
./scripts/extract.sh add patterns "hook-interceptor"
```

## Requirements

- **GitHub CLI** (`gh`) - API access
- **jq** - JSON processing
- **QMD** (optional) - Semantic search
- **Claude Code** - Subagent execution

See INSTALL.md for installation details.

## Directory Structure

```
github-intel-skill/
├── SKILL.md                  # Skill definition (triggers, usage)
├── INSTALL.md                # Installation guide
├── README.md                 # This file
├── agents/                   # Subagent definitions
│   ├── repo-explorer.md      # Structure analysis
│   ├── code-reviewer.md      # Deep code review
│   └── knowledge-extractor.md # Documentation generator
├── references/               # Detailed guides
│   ├── workflow.md           # Complete workflow
│   └── subagents.md          # Orchestration patterns
├── examples/
│   └── knowledge-entry.md    # Template
└── scripts/                  # Executable tools
    ├── run.sh                # Main CLI
    ├── discover.sh           # GitHub crawler
    ├── generate-todos.sh     # TODO generator
    ├── extract.sh            # Knowledge extraction
    ├── config.sh             # Configuration
    └── batch-explore.sh      # Batch operations
```

## Real-World Results

Using this skill, we extracted:
- **200+ skills** from 5 repositories
- **3,659 lines** of documentation (132KB)
- Skills from Anthropic, Trail of Bits, Sentry, Hugging Face
- **442 repos** discovered and indexed

See `knowledge/INDEX.md` for examples.

## Contributing

Improvements welcome:
- Add more analysis patterns
- Enhance subagent prompts
- Support additional knowledge categories
- Add integration with other tools

## License

MIT License - See LICENSE file

## Support

- Documentation: See `SKILL.md` and `references/`
- Examples: See `examples/` directory
- Issues: GitHub Issues

---

**Built with Claude Opus 4.5** using the ralph-loop PRD-driven development framework.
