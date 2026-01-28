---
name: qmd-search
description: This skill should be used when implementing on-device semantic search for markdown documents using QMD (Query My Data). It applies when building search features for personal notes, meeting transcripts, documentation, or knowledge bases. Provides patterns for Electron app integration, IPC handlers, React components, and security sanitization. Triggers on requests like "add vector search", "implement semantic search", "integrate QMD", "search my notes", or building local document search features.
---

# QMD Search Skill

On-device semantic search engine for markdown documents, notes, transcripts, and knowledge bases. Created by Tobi Lütke ([@tobi](https://github.com/tobi)).

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

**Requirements:**
- Bun >= 1.0.0
- macOS users need Homebrew SQLite for extension support
- Windows support available (cross-platform paths)

Verify installation:

```bash
qmd --version
qmd status
```

## Three Search Modes

| Mode | Command | Speed | Quality | Best For |
|------|---------|-------|---------|----------|
| **search** | `qmd search "query"` | Fastest | Good | Keyword matching, exact terms (BM25) |
| **vsearch** | `qmd vsearch "query"` | Fast | Better | Semantic similarity, concepts |
| **query** | `qmd query "query"` | Slower | Best | Complex queries, highest accuracy |

### When to Use Each Mode

- **search (BM25)**: User knows exact keywords. "Find files mentioning API rate limiting"
- **vsearch (vectors)**: Conceptual queries. "Notes about being productive"
- **query (hybrid)**: Important queries needing best results. Combines FTS + vectors + query expansion + LLM re-ranking

## Complete CLI Reference

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

| Option | Purpose |
|--------|---------|
| `-n <num>` | Results count (default: 5; 20 for --files/--json) |
| `-c, --collection` | Restrict to specific collection |
| `--all` | Return all matches |
| `--min-score <num>` | Minimum relevance threshold |
| `--full` | Display complete document content |
| `--line-numbers` | Include line numbers in output |
| `--index <name>` | Use named index |

### Output Formats

```bash
qmd search "query" --json      # Structured JSON with snippets
qmd search "query" --files     # Tab-separated: docid, score, filepath, context
qmd search "query" --md        # Markdown formatted
qmd search "query" --csv       # Comma-separated values
qmd search "query" --xml       # XML structure
qmd search "query" --full      # Complete document content
```

Default output is colorized CLI (honors `NO_COLOR` env variable).

### Document Retrieval

```bash
# Get by file path
qmd get ~/notes/meeting.md

# Get by document ID (6-char hash shown in search results)
qmd get #abc123

# Get with quotes (flexible lookup)
qmd get "#abc123"
qmd get "abc123"

# Get specific lines
qmd get ~/notes/meeting.md -l 50 --from 100

# Batch retrieval with glob pattern
qmd multi-get "meetings/*.md" --max-bytes 50000

# Batch retrieval by docids
qmd multi-get "#abc123,#def456"
```

### Collection Management

```bash
# Add a directory to index
qmd collection add ~/Documents/notes --name notes --mask "**/*.md"

# List all collections
qmd collection list

# Rename a collection
qmd collection rename old-name new-name

# Remove a collection
qmd collection remove notes

# List files in a collection
qmd ls notes
qmd ls notes/subfolder
```

### Context Management

Add descriptions to help search understand your content:

```bash
# Add context description
qmd context add qmd://notes "Personal daily notes and journal entries"
qmd context add ~/Documents/api-docs "REST API documentation for our backend"

# List all contexts
qmd context list

# Remove context
qmd context rm qmd://notes
```

### Index Management

```bash
# Generate/update vector embeddings (800-token chunks, 15% overlap)
qmd embed

# Force re-embed all documents
qmd embed -f

# Re-index collections (detect file changes)
qmd update

# Re-index and pull latest from git repos
qmd update --pull

# Show index health and stats
qmd status

# Clean up cache and orphaned data
qmd cleanup
```

## Hybrid Search Architecture

The `query` command implements sophisticated multi-stage ranking:

```
┌─────────────────────────────────────────────────────────────┐
│  1. QUERY EXPANSION                                         │
│     Original query (×2 weight) + LLM-generated variation    │
├─────────────────────────────────────────────────────────────┤
│  2. PARALLEL RETRIEVAL                                      │
│     BM25 search ──┐                                         │
│                   ├──▶ Results pool                         │
│     Vector search─┘                                         │
├─────────────────────────────────────────────────────────────┤
│  3. RRF FUSION (k=60)                                       │
│     Reciprocal Rank Fusion with top-rank bonuses            │
├─────────────────────────────────────────────────────────────┤
│  4. LLM RE-RANKING                                          │
│     Evaluates top 30 candidates with confidence scores      │
├─────────────────────────────────────────────────────────────┤
│  5. POSITION-AWARE BLENDING                                 │
│     Ranks 1-3:  75% retrieval, 25% reranker (exact matches) │
│     Ranks 4-10: 60% retrieval, 40% reranker                 │
│     Ranks 11+:  40% retrieval, 60% reranker (trust LLM)     │
└─────────────────────────────────────────────────────────────┘
```

## Local Models

Three GGUF models auto-download to `~/.cache/qmd/models/`:

| Model | Role | Size |
|-------|------|------|
| embeddinggemma-300M-Q8_0 | Vector embeddings | ~300MB |
| qwen3-reranker-0.6b-q8_0 | Relevance scoring | ~640MB |
| Qwen3-1.7B-Q8_0 | Query expansion | ~2.2GB |

**Total: ~3.1GB** (downloaded on first use)

### EmbeddingGemma Prompt Format

- Queries: `"task: search result | query: {query}"`
- Documents: `"title: {title} | text: {content}"`

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

### Configure for Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

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
| `qmd_search` | BM25 keyword search (supports collection filter) |
| `qmd_vsearch` | Semantic vector search (supports collection filter) |
| `qmd_query` | Hybrid search with reranking (supports collection filter) |
| `qmd_get` | Retrieve document by path or docid (with fuzzy matching suggestions) |
| `qmd_multi_get` | Batch retrieval by glob pattern, list, or docids |
| `qmd_status` | Index health and collection info |

## Understanding Scores

Search results include relevance scores from 0.0 to 1.0:

| Score Range | Meaning |
|-------------|---------|
| 0.8 - 1.0 | Highly relevant, strong match |
| 0.5 - 0.8 | Moderately relevant |
| 0.2 - 0.5 | Somewhat relevant, tangential |
| 0.0 - 0.2 | Low relevance, may be noise |

Use `--min-score 0.5` to filter out low-quality matches.

## Supported File Types

- **Markdown** (`.md`) - Full support with title extraction
- **Org-mode** (`.org`) - Title extraction support (added Jan 2026)
- **Text files** (`.txt`) - Plain text indexing
- Custom patterns via `--mask` glob

## Storage Locations

| Data | Location |
|------|----------|
| SQLite index | `~/.cache/qmd/index.sqlite` |
| Configuration | `~/.config/qmd/index.yml` |
| Models | `~/.cache/qmd/models/` |

Documents are identified by 6-character content hash (docid).

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
│  │    QMD CLI      │  (Bun/TypeScript binary)               │
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
  docid?: string
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
- QMD binary path resolution (cross-platform)
- Safe execution with `execFile` (shell: false)
- Config file parsing from `~/.config/qmd/index.yml`

**Allowed subcommands:**
```typescript
const allowedSubcommands = [
  'search', 'vsearch', 'query',  // Search operations
  'collection', 'ls', 'status',   // Management
  'embed', 'update', 'cleanup',   // Indexing
  'context', 'get', 'multi-get'   // Retrieval & context
]
```

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

# Add context to help search understand
qmd context add qmd://project-x "Project X planning docs and meeting notes"

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

### CPU-only systems running slow

QMD uses sequential embedding on CPU-only systems to avoid race conditions. This is slower but more reliable.

### Check index health

```bash
qmd status
```

Shows: collection count, document count, embedding coverage, and any issues.

### Clean up corrupted cache

```bash
qmd cleanup
```

## Performance Tips

1. **Start with `search`** for quick keyword lookups
2. **Use `query`** only when you need highest quality results (it's slower due to LLM re-ranking)
3. **Filter by collection** (`-c`) to reduce search space
4. **Set `--min-score`** to avoid processing low-quality matches
5. **Use `--files` output** for agent workflows - it's parseable and includes docids
6. **Add context descriptions** to improve search relevance

## Recent Updates (Jan 2026)

- **Windows support** - Cross-platform path handling (#51)
- **Org-mode support** - Title extraction for `.org` files (#50)
- **CPU-only fix** - Sequential embedding prevents race conditions (#54)
- **Collection filtering** - Fixed `collectionName` parameter in vector search (#61)
- **Docid lookup** - More lenient matching with quotes support (#39)

## Reference

- [QMD Repository](https://github.com/tobi/qmd)
- Index location: `~/.cache/qmd/index.sqlite`
- Config location: `~/.config/qmd/index.yml`
- Models location: `~/.cache/qmd/models/`
- Total model size: ~3.1GB (auto-downloads on first use)

## Resources

This skill includes reference implementations:

### references/
- `ipc-handler.ts` - Complete IPC handler implementation with security patterns
- `react-components.md` - React/Jotai component implementations
- `security-tests.ts` - Security test suite for input sanitization

### scripts/
- `install-qmd.sh` - Installation script with verification
- `setup-collection.sh` - Quick collection setup helper
