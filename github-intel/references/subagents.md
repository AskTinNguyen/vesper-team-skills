# Subagent Orchestration Patterns

Guide for orchestrating subagents to perform parallel research and knowledge extraction.

## Available Agents

| Agent | Purpose | Model | Use When |
|-------|---------|-------|----------|
| `repo-explorer` | Codebase analysis | sonnet | Initial exploration |
| `code-reviewer` | Deep code review | sonnet | Detailed analysis |
| `knowledge-extractor` | Doc generation | sonnet | Creating knowledge entries |

## Single Agent Launch

### Basic Pattern

```
Launch repo-explorer agent to analyze .clones/repo-name

Focus on:
- Architecture patterns
- Key file locations
- Reusable code
```

### With Specific Instructions

```
Launch code-reviewer agent for .clones/repo/src/core/

Specific focus:
1. Error handling patterns
2. Caching strategies
3. API design choices

Output format: markdown with code snippets
```

## Parallel Agent Launch

### Pattern: Multiple Repos

```
Launch 3 repo-explorer agents in parallel:

Agent 1:
- Repo: .clones/anthropics-claude-code
- Focus: Plugin system architecture

Agent 2:
- Repo: .clones/openai-codex
- Focus: CLI command structure

Agent 3:
- Repo: .clones/cline-cline
- Focus: IDE extension patterns
```

### Pattern: Same Repo, Different Aspects

```
Launch 3 agents in parallel to analyze .clones/anthropics-claude-code:

Agent 1 (repo-explorer):
- Focus: Overall architecture
- Output: Structure overview

Agent 2 (code-reviewer):
- Focus: plugins/hookify/core/
- Output: Pattern analysis

Agent 3 (knowledge-extractor):
- Focus: Document the hook system
- Output: Compound doc entry
```

### Pattern: Pipeline

```
Sequential agent pipeline:

1. Launch repo-explorer for .clones/repo
   Wait for: Structure analysis complete

2. Launch code-reviewer for identified key files
   Wait for: Best practices documented

3. Launch knowledge-extractor
   Input: Reviewer findings
   Output: Knowledge entries
```

## Agent Communication

### Passing Context

Agents can share findings through:

1. **File-based**: Write to shared location
```
Agent 1: Write findings to .clones/repo/ANALYSIS.md
Agent 2: Read .clones/repo/ANALYSIS.md as context
```

2. **Prompt-based**: Include previous output
```
Given the following architecture analysis:
[Output from Agent 1]

Now perform deep code review of identified key files.
```

### Aggregating Results

```
After parallel exploration, aggregate:

1. Read all agent outputs
2. Identify common patterns
3. Rank by extraction value
4. Create unified knowledge plan
```

## Best Practices

### Agent Selection

| Task | Agent | Why |
|------|-------|-----|
| "What's in this repo?" | repo-explorer | Structure first |
| "How does X work?" | code-reviewer | Deep analysis |
| "Document pattern Y" | knowledge-extractor | Structured output |

### Prompt Engineering

**Good:**
```
Launch repo-explorer to analyze .clones/repo

Focus areas:
1. Entry point (main.ts or index.js)
2. Core logic (src/core/)
3. Utilities (src/utils/)

Expected output:
- File tree with annotations
- Key file descriptions
- Pattern identification
```

**Avoid:**
```
Explore this repo and tell me what's interesting.
```

### Resource Management

- Limit parallel agents to 3-5 for responsiveness
- Use haiku model for simple tasks
- Reserve opus for complex analysis
- Set reasonable timeouts

### Error Handling

```
Launch agent with fallback:

Primary: Analyze .clones/large-repo with repo-explorer
If timeout: Focus only on src/ directory
If missing: Report and suggest alternatives
```

## Common Workflows

### New Repo Analysis

```bash
# 1. Clone repo
./crawler/run.sh explore repo-name

# 2. Launch explorer
> Launch repo-explorer for .clones/repo-name

# 3. Based on findings, launch reviewer
> Launch code-reviewer for identified key files

# 4. Extract valuable patterns
> Launch knowledge-extractor for discovered patterns
```

### Batch Knowledge Building

```bash
# 1. Select repos from search
qmd vsearch "target pattern" -c ai-coding-repos -n 10

# 2. Clone all
for repo in repo1 repo2 repo3; do
  ./crawler/run.sh explore $repo
done

# 3. Parallel exploration
> Launch 3 repo-explorer agents in parallel for:
> .clones/repo1, .clones/repo2, .clones/repo3

# 4. Aggregate and extract
> Synthesize findings into knowledge entries
```

### Pattern Mining

```
Goal: Find all implementations of "X pattern"

1. Search: qmd vsearch "X pattern" -c ai-coding-repos
2. Clone top results
3. Launch parallel reviewers focused on X
4. Compare implementations
5. Extract best version to knowledge store
```

## Subagent Output Formats

### repo-explorer Output

```markdown
# Repository Analysis: repo-name

## Structure
[Directory tree]

## Key Components
[List with file paths]

## Patterns Found
[Named patterns with locations]

## Recommendations
[What to explore deeper]
```

### code-reviewer Output

```markdown
# Code Review: file-path

## Summary
[What the code does]

## Best Practices
[With code snippets]

## Extraction Candidates
[Table of valuable code]
```

### knowledge-extractor Output

```markdown
---
frontmatter
---

# Pattern Name

## Overview
## Problem
## Solution
## Usage
## References
```
