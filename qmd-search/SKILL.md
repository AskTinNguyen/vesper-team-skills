---
name: qmd-search
description: This skill should be used when implementing on-device semantic search for markdown documents using QMD (Query My Data). It applies when building search features for personal notes, meeting transcripts, documentation, or knowledge bases. Provides patterns for Electron app integration, IPC handlers, React components, and security sanitization. Triggers on requests like "add vector search", "implement semantic search", "integrate QMD", "search my notes", or building local document search features.
---

# QMD Search Skill

On-device semantic search engine for markdown documents, notes, transcripts, and knowledge bases.

## When to Use This Skill

**For Users:**
- Searching personal notes or documentation indexed by QMD
- Finding meeting transcripts or conversation logs
- Querying knowledge bases with semantic understanding

**For Developers:**
- Integrating QMD into Electron/desktop applications
- Building local semantic search features
- Implementing secure CLI wrapper patterns

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

## Understanding Scores

Search results include relevance scores from 0.0 to 1.0:

| Score Range | Meaning |
|-------------|---------|
| 0.8 - 1.0 | Highly relevant, strong match |
| 0.5 - 0.8 | Moderately relevant |
| 0.2 - 0.5 | Somewhat relevant, tangential |
| 0.0 - 0.2 | Low relevance, may be noise |

Use `--min-score 0.5` to filter out low-quality matches.

---

# Developer Integration Guide

This section covers how to integrate QMD into Electron/desktop applications.

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    RENDERER PROCESS                          │
│                                                              │
│  ┌─────────────────┐    ┌─────────────────┐                 │
│  │   VectorSearch  │───▶│  Jotai Atoms    │                 │
│  │   Component     │    │  (State)        │                 │
│  └────────┬────────┘    └─────────────────┘                 │
│           │                                                  │
│           │ window.electronAPI.vectorSearchExecute()        │
│           ▼                                                  │
└───────────┼──────────────────────────────────────────────────┘
            │ IPC
┌───────────┼──────────────────────────────────────────────────┐
│           ▼                   MAIN PROCESS                   │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    IPC Handler                          ││
│  │  1. Validate subcommand against allowlist               ││
│  │  2. Sanitize arguments (remove shell metacharacters)    ││
│  │  3. Resolve QMD binary path                             ││
│  │  4. Execute via execFile (shell: false)                 ││
│  │  5. Return { stdout, stderr }                           ││
│  └────────┬────────────────────────────────────────────────┘│
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────┐                                        │
│  │    QMD CLI      │  (External Rust binary)                │
│  └─────────────────┘                                        │
└──────────────────────────────────────────────────────────────┘
```

## Implementation Components

### 1. Type Definitions

```typescript
// Search modes supported by QMD
type SearchMode = 'keyword' | 'semantic' | 'hybrid'

// Result from QMD CLI execution
interface VectorSearchExecuteResult {
  stdout: string
  stderr: string
}

// Search result from QMD
interface VectorSearchResult {
  filePath: string
  snippet: string
  score: number
  collection: string
  title?: string
}

// Collection info from QMD
interface CollectionInfo {
  name: string
  url: string           // qmd://collection-name/
  pattern: string       // Glob pattern e.g., **/*.md
  files: number
  updated: string
  rootPath?: string     // Absolute root path for resolving relative paths
}

// QMD collection configuration
interface VectorSearchCollectionConfig {
  name: string
  path: string          // Absolute root path
  pattern: string
}

// Search state for UI
interface SearchState {
  query: string
  mode: SearchMode
  results: VectorSearchResult[]
  error: string | null
  isSearching: boolean
}
```

### 2. IPC Handler (Main Process)

See `references/ipc-handler.ts` for complete implementation including:
- Subcommand allowlist validation
- Argument sanitization against shell injection
- QMD binary path resolution
- Safe execution with `execFile` (shell: false)
- Config file parsing from `~/.config/qmd/index.yml`

### 3. React Components (Renderer)

See `references/react-components.md` for:
- VectorSearch main component
- AddCollectionModal for indexing new folders
- CollectionList for management
- State atoms (Jotai)

### 4. Security Considerations

**Critical:** Always sanitize user input before passing to CLI:

```typescript
// Sanitize function - removes shell metacharacters
function sanitizeArg(arg: string): string {
  return arg.replace(/[`$(){}|;&\n\r\0]/g, '').slice(0, 1000)
}
```

**Security patterns:**
- Allowlist valid subcommands
- Use `execFile()` with `shell: false`
- Sanitize ALL user-provided arguments
- Limit argument length (1000 chars)
- Handle ENOENT gracefully

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
- Config location: `~/.config/qmd/index.yml`
- Models auto-download on first use (~1.5GB total)

## Resources

This skill includes reference implementations:

### references/
- `ipc-handler.ts` - Complete IPC handler implementation with security patterns
- `react-components.md` - React/Jotai component implementations
- `security-tests.ts` - Security test suite for input sanitization
