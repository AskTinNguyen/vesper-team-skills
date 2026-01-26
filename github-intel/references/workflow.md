# GitHub Intelligence Workflow Guide

Complete workflow for discovering, analyzing, and extracting knowledge from GitHub repositories.

## End-to-End Workflow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Discovery  │────▶│   Index     │────▶│  Explore    │────▶│  Extract    │
│  (Crawl)    │     │   (QMD)     │     │  (Agents)   │     │  (Docs)     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
      │                   │                   │                   │
      ▼                   ▼                   ▼                   ▼
 todos/repos/        Vectors          .clones/           knowledge/
```

## Phase 1: Discovery

### Configure Search Parameters

```bash
# Edit crawler/config.sh
export MIN_STARS=50          # Minimum stars
export DAYS_AGO=90           # Max age in days
export RATE_LIMIT_SLEEP=2    # API rate limiting

# Custom keywords
export CRAWLER_KEYWORDS="claude-code codex mcp-server ai-coding"
```

### Run Discovery

```bash
./crawler/run.sh discover
```

**Output:**
- `todos/repos/*.md` - Individual TODO files
- `todos/repos/INDEX.md` - Sorted master list
- Approx 400-500 repos with default settings

### Filter Results

```bash
# Filter by star range
grep -E '\| [0-9]{4} \|' todos/repos/INDEX.md | head -50

# Filter by language
grep "Python" todos/repos/INDEX.md

# Filter by keyword
grep -i "agent" todos/repos/INDEX.md
```

## Phase 2: Semantic Indexing

### Create QMD Collection

```bash
qmd collection add todos/repos --name ai-coding-repos --mask "*.md"
```

### Generate Embeddings

```bash
qmd embed
```

### Verify Index

```bash
qmd status
```

### Search Commands

```bash
# Keyword search (BM25)
qmd search "multi-agent" -c ai-coding-repos

# Semantic search (vectors)
qmd vsearch "orchestration patterns" -c ai-coding-repos

# Combined with reranking
qmd query "how to implement hooks" -c ai-coding-repos
```

## Phase 3: Exploration

### Select Repos for Deep Dive

Use search to find relevant repos:

```bash
# Find agent-related repos
qmd vsearch "autonomous coding agent" -c ai-coding-repos -n 20

# Find MCP-related repos
qmd search "MCP server" -c ai-coding-repos
```

### Clone and Explore

```bash
# Clone repository
./crawler/run.sh explore anthropics-claude-code

# View cloned repo
ls .clones/anthropics-claude-code/
```

### Launch Explorer Agent

In Claude Code session:

```
Explore the codebase at .clones/anthropics-claude-code

Focus on discovering:
1. Plugin architecture
2. Hook system implementation
3. Skill loading mechanism
4. Reusable utilities
```

### Parallel Exploration

For batch analysis, launch multiple agents:

```
Launch 3 repo-explorer agents in parallel:

1. Agent 1: Explore .clones/anthropics-claude-code
   Focus: Plugin architecture

2. Agent 2: Explore .clones/openai-codex
   Focus: CLI framework

3. Agent 3: Explore .clones/cline-cline
   Focus: IDE integration patterns
```

## Phase 4: Code Review

### Deep Analysis

For specific files or modules:

```
Launch code-reviewer agent to analyze:
.clones/anthropics-claude-code/plugins/hookify/core/rule_engine.py

Focus on:
- Pattern matching implementation
- Performance optimizations
- Error handling approach
```

### Review Output

Reviewer provides:
- Best practices found
- Pattern identification
- Extraction candidates
- Quality ratings

## Phase 5: Knowledge Extraction

### Identify Extraction Candidates

From explorer/reviewer output, identify:
- High-value patterns
- Reusable utilities
- Novel architectures

### Create Knowledge Entry

```bash
# Interactive creation
./crawler/extract.sh add patterns "hook-interceptor"

# Manual creation
mkdir -p knowledge/patterns
cat > knowledge/patterns/hook-interceptor.md << 'EOF'
---
title: Hook Interceptor Pattern
source: anthropics-claude-code
...
EOF
```

### Launch Extractor Agent

```
Launch knowledge-extractor agent to document:
"LRU Regex Cache" pattern from anthropics-claude-code

Source file: plugins/hookify/core/rule_engine.py:15
Category: utilities
```

### Update Index

```bash
./crawler/extract.sh update-index
```

## Phase 6: Iteration

### Continuous Discovery

Run discovery weekly/monthly:

```bash
# Re-run with updated date filter
export DAYS_AGO=30
./crawler/run.sh discover

# Update QMD index
qmd update
qmd embed -f  # Force re-embed
```

### Knowledge Maintenance

- Review and update entries
- Add cross-references
- Remove outdated content
- Merge related patterns

## Best Practices

### Discovery

- Start with broad keywords, narrow based on results
- Use star thresholds to focus on quality
- Run discovery during off-peak hours (rate limits)

### Exploration

- Prioritize repos by relevance and star count
- Use parallel agents for batch analysis
- Focus on specific aspects per exploration

### Extraction

- Only extract truly valuable patterns
- Include complete, working code
- Document trade-offs and limitations
- Cross-reference related patterns

### Indexing

- Re-index after new discoveries
- Use collection filters for focused search
- Combine keyword and semantic search

## Troubleshooting

### API Rate Limits

```bash
# Increase delay
export RATE_LIMIT_SLEEP=5

# Check GitHub rate limit
gh api rate_limit
```

### QMD Issues

```bash
# Rebuild index
qmd cleanup
qmd collection remove ai-coding-repos
qmd collection add todos/repos --name ai-coding-repos --mask "*.md"
qmd embed
```

### Missing Repos

```bash
# Check if repo exists
gh repo view owner/repo

# Manual TODO creation
cat > todos/repos/owner-repo.md << 'EOF'
# Explore: owner/repo
...
EOF
```
