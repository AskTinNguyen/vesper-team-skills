# Policy Schema Reference

## Zod Schema Definition

The persona policy schema uses all-optional fields so an empty `{}` is valid (denies nothing).

```typescript
import { z } from 'zod'

// Preset enum for role-based defaults
const PolicyPresetSchema = z.enum(['research', 'reviewer', 'engineer', 'admin'])

// Bash patterns support both plain strings and documented objects
const BashPatternSchema = z.union([
  z.string(),
  z.object({ pattern: z.string(), comment: z.string().optional() }),
])

// Main policy schema
const PersonaPolicySchema = z.object({
  // Optional preset identifier — applied first, then customized
  preset: PolicyPresetSchema.optional(),

  // File system deny globs (supports **, *, ?)
  hardDeniedReadPaths:  z.array(z.string()).optional(),
  hardDeniedWritePaths: z.array(z.string()).optional(),

  // Bash command denial
  hardDeniedBashBaseCommands: z.array(z.string()).optional(),  // e.g. ['rm', 'sudo', 'git push']
  hardDeniedBashPatterns:     z.array(BashPatternSchema).optional(),

  // MCP tool denial
  hardDeniedMcpServers: z.array(z.string()).optional(),  // Server names (blocks all tools)
  hardDeniedMcpTools:   z.array(z.string()).optional(),  // 'server/tool' format

  // API endpoint denial
  hardDeniedApiPatterns: z.array(z.string()).optional(),  // '[METHOD] /path/*' format

  // Network kill switch
  hardDeniedWebFetch: z.boolean().optional(),
})

type PersonaPolicy = z.infer<typeof PersonaPolicySchema>
type PolicyPreset = z.infer<typeof PolicyPresetSchema>
type BashPattern = z.infer<typeof BashPatternSchema>
```

## Field Documentation

### `preset` (optional)

Identifier for the base preset applied. When set, UI can show which preset was used. Customizations
after preset application are preserved — the preset field is just metadata.

### `hardDeniedReadPaths` (optional, string[])

Glob patterns for files the agent cannot read. Uses `**` for recursive, `*` for single segment,
`?` for single character. Paths are normalized (backslash to forward slash) and `~` expanded
before matching.

Examples:
- `"**/.env"` — block all .env files at any depth
- `"**/*.key"` — block all private key files
- `"~/secrets/**"` — block entire secrets directory

### `hardDeniedWritePaths` (optional, string[])

Same glob syntax as read paths, but for write operations (Write, Edit, MultiEdit, NotebookEdit).

Special value: `"**"` blocks ALL writes (used by research preset).

### `hardDeniedBashBaseCommands` (optional, string[])

Base commands to deny. Matched case-insensitively against the extracted base command.

Git-aware: `"git push"` matches `git push origin main --force` because `getBaseCommand()` extracts
the git subcommand as part of the base.

Examples: `["rm", "rmdir", "sudo", "chmod", "git push", "git reset"]`

### `hardDeniedBashPatterns` (optional, BashPattern[])

Regex patterns matched against the full command string. Each entry is either:
- A plain string: `"rm\\s+-rf\\s+/"`
- An object with comment: `{ "pattern": "rm\\s+-rf\\s+/", "comment": "Block recursive force-delete from root" }`

Comments appear in deny messages to help users understand why a command was blocked.

### `hardDeniedMcpServers` (optional, string[])

MCP server names to block entirely. When a server is denied, ALL tools on that server are blocked
without checking individual tool rules (fast path).

MCP tool names follow format `mcp__<server>__<tool>`. Server name is extracted from the second segment.

### `hardDeniedMcpTools` (optional, string[])

Individual MCP tools in `server/tool` format. Only checked if the server itself is not denied (server
deny takes precedence as a fast path).

### `hardDeniedApiPatterns` (optional, string[])

API endpoint patterns with optional HTTP method prefix:
- `"POST /issues/*"` — block POST to /issues/anything
- `"DELETE *"` — block all DELETE requests
- `"* /admin/*"` — block any method on /admin paths
- `"/readonly/*"` — block any method on /readonly paths (no method = any)

Glob conversion: `*` to `[^/]+` (single segment), `**` to `.*` (anything).

### `hardDeniedWebFetch` (optional, boolean)

When `true`, blocks ALL WebFetch tool calls. A kill switch for network access.

## Summary Helper

For UI badges showing deny rule counts:

```typescript
interface PolicySummary {
  preset: PolicyPreset | undefined
  deniedReadPathCount: number
  deniedWritePathCount: number
  deniedBashCommandCount: number
  deniedBashPatternCount: number
  deniedMcpServerCount: number
  deniedMcpToolCount: number
  deniedApiPatternCount: number
  webFetchDenied: boolean
  totalDenyRules: number
}
```

Compute by counting array lengths and summing. Display as a badge like "12 deny rules" or
"research preset + 3 custom rules".

## Example Policy JSON

```json
{
  "preset": "engineer",
  "hardDeniedReadPaths": [
    "**/.env", "**/.env.*",
    "**/credentials.enc",
    "**/*.pem", "**/*.key"
  ],
  "hardDeniedWritePaths": [],
  "hardDeniedBashBaseCommands": ["sudo"],
  "hardDeniedBashPatterns": [
    { "pattern": "rm\\s+-rf\\s+/", "comment": "Block recursive force-delete from root" }
  ],
  "hardDeniedMcpServers": ["dangerous-server"],
  "hardDeniedMcpTools": ["github/delete_repo"],
  "hardDeniedApiPatterns": ["DELETE *", "POST /admin/*"],
  "hardDeniedWebFetch": false
}
```
