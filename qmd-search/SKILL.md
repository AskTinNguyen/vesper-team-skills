---
name: qmd-search
description: On-device search engine for markdown documents using QMD (Query My Data). Use when searching personal notes, meeting transcripts, documentation, or knowledge bases. Supports keyword search (BM25), semantic search (vectors), and hybrid search with LLM re-ranking.
---

# QMD Search Skill

On-device search engine for markdown documents, notes, transcripts, and knowledge bases.

## When to Use This Skill

- Searching personal notes or documentation indexed by QMD
- Finding meeting transcripts or conversation logs
- Querying knowledge bases with semantic understanding
- Retrieving context from indexed markdown collections
- When the user mentions "search my notes", "find in my docs", or references QMD

## Prerequisites

QMD must be installed globally:

```bash
bun install -g https://github.com/tobi/qmd
```

Verify installation:

```bash
qmd --version
qmd status
```

## Three Search Modes

| Mode | Command | Speed | Quality | Best For |
|------|---------|-------|---------|----------|
| **search** | `qmd search "query"` | Fastest | Good | Keyword matching, exact terms |
| **vsearch** | `qmd vsearch "query"` | Fast | Better | Semantic similarity, concepts |
| **query** | `qmd query "query"` | Slower | Best | Complex queries, highest accuracy |

### When to Use Each Mode

- **search (BM25)**: User knows exact keywords. "Find files mentioning API rate limiting"
- **vsearch (vectors)**: Conceptual queries. "Notes about being productive"
- **query (hybrid)**: Important queries needing best results. Combines FTS + vectors + LLM re-ranking

## CLI Commands

### Check What's Indexed

```bash
# Show all collections and index health
qmd status

# List documents in a collection
qmd ls <collection-name>
```

### Search Commands

```bash
# Keyword search (BM25) - fastest
qmd search "authentication login"

# Semantic search (vectors) - conceptual
qmd vsearch "how to be more productive"

# Hybrid search (best quality) - uses re-ranking
qmd query "best practices for API design"
```

### Search Options

```bash
# Limit results
qmd search "query" -n 10

# Filter by collection
qmd search "query" -c meetings

# Get all matches above threshold
qmd search "query" --all --min-score 0.5

# Output formats
qmd search "query" --json      # Structured JSON with snippets
qmd search "query" --files     # docid, score, filepath, context
qmd search "query" --md        # Markdown formatted
qmd search "query" --full      # Complete document content
```

### Retrieve Documents

```bash
# Get by file path
qmd get ~/notes/meeting.md

# Get by document ID (6-char hash shown in search results)
qmd get #abc123

# Get specific lines
qmd get ~/notes/meeting.md -l 50 --from 100

# Batch retrieval with glob pattern
qmd multi-get "meetings/*.md" --max-bytes 50000
```

### Collection Management

```bash
# Add a directory to index
qmd collection add ~/Documents/notes --name notes --mask "**/*.md"

# List collections
qmd collection list

# Add context description (helps search understand content)
qmd context add qmd://notes "Personal daily notes and journal entries"

# Re-index after changes
qmd update

# Generate embeddings (required for vsearch/query)
qmd embed
```

## MCP Server Integration

QMD can run as an MCP server for AI agent integration.

### Configure for Claude Code

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "qmd": {
      "command": "qmd",
      "args": ["mcp"]
    }
  }
}
```

### Available MCP Tools

| Tool | Purpose |
|------|---------|
| `mcp__qmd__qmd_search` | BM25 keyword search |
| `mcp__qmd__qmd_vsearch` | Vector semantic search |
| `mcp__qmd__qmd_query` | Hybrid search with re-ranking |
| `mcp__qmd__qmd_get` | Retrieve document by path or docid |
| `mcp__qmd__qmd_multi_get` | Batch retrieval via glob/list |
| `mcp__qmd__qmd_status` | Index health and collection info |

### MCP Tool Examples

```
Tool: mcp__qmd__qmd_query
Args: {"query": "API authentication best practices", "n": 5}

Tool: mcp__qmd__qmd_get
Args: {"path": "#abc123", "lines": 100}

Tool: mcp__qmd__qmd_status
Args: {}
```

## Understanding Scores

Search results include relevance scores from 0.0 to 1.0:

| Score Range | Meaning |
|-------------|---------|
| 0.8 - 1.0 | Highly relevant, strong match |
| 0.5 - 0.8 | Moderately relevant |
| 0.2 - 0.5 | Somewhat relevant, tangential |
| 0.0 - 0.2 | Low relevance, may be noise |

Use `--min-score 0.5` to filter out low-quality matches.

## Workflow Examples

### Find and Retrieve Relevant Notes

```bash
# 1. Search for relevant documents
qmd query "project planning best practices" --json -n 5

# 2. Get the most relevant document
qmd get #abc123 --full

# 3. Or get specific lines for context
qmd get #abc123 -l 50 --from 20
```

### Search Within a Collection

```bash
# Only search meeting transcripts
qmd query "action items from last week" -c meetings

# Only search documentation
qmd search "installation guide" -c docs
```

### Add New Content to Index

```bash
# Add new directory
qmd collection add ~/new-notes --name project-x

# Generate embeddings for semantic search
qmd embed

# Verify it's indexed
qmd status
```

## Troubleshooting

### "No collections found"

Index hasn't been set up yet:

```bash
qmd collection add ~/Documents/notes --name notes
qmd embed
```

### Vector search returns no results

Embeddings need to be generated:

```bash
qmd embed
# Or force re-embed
qmd embed -f
```

### Stale results after file changes

Re-index the content:

```bash
qmd update
```

### Check index health

```bash
qmd status
```

Shows: collection count, document count, embedding coverage, and any issues.

## Performance Tips

1. **Start with `search`** for quick keyword lookups
2. **Use `query`** only when you need highest quality results (it's slower due to LLM re-ranking)
3. **Filter by collection** (`-c`) to reduce search space
4. **Set `--min-score`** to avoid processing low-quality matches
5. **Use `--files` output** for agent workflows - it's parseable and includes docids

## Reference

- [QMD Repository](https://github.com/tobi/qmd)
- Index location: `~/.cache/qmd/index.sqlite`
- Models auto-download on first use (~1.5GB total)
