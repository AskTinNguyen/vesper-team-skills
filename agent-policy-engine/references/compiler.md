# Compiler Reference

## Overview

The compiler transforms a validated `PersonaPolicy` JSON config into an optimized `CompiledPolicy`
runtime structure. Compilation happens **once** at session start — the compiled structure is stored
on the agent instance and reused for every tool call check.

## Compilation Functions

### `compileGlobs(patterns: string[]): RegExp[]`

Convert glob patterns to RegExp array, skipping invalid patterns:

```typescript
function compileGlobs(patterns: string[] | undefined): RegExp[] {
  const result: RegExp[] = []
  for (const pattern of patterns ?? []) {
    try { result.push(globToRegex(pattern)) } catch { /* skip invalid */ }
  }
  return result
}
```

### `compileApiPattern(pattern: string): CompiledApiPattern | null`

Parse API pattern string into method + path regex. Returns null for invalid patterns.

**Format:** `"[METHOD] /path/pattern"` where METHOD is optional.

**Parsing logic:**
1. Split on whitespace
2. If 1 part — path only, any method
3. If 2 parts — first is method (or `*` for any), second is path
4. If 3+ parts — invalid, return null

**Glob-to-regex for paths:**
- `*` alone — `.*` (any path)
- `*` in path — `[^/]+` (single segment)
- `**` — `.*` (anything including slashes)
- Slashes escaped: `/` to `\\/`
- Pattern anchored with `^` and `$`

```typescript
function compileApiPattern(pattern: string) {
  const parts = pattern.trim().split(/\s+/)

  let method: string | undefined
  let pathPattern: string

  if (parts.length === 1) {
    pathPattern = parts[0]
  } else if (parts.length === 2) {
    method = parts[0] === '*' ? undefined : parts[0].toUpperCase()
    pathPattern = parts[1]
  } else {
    return null
  }

  // Convert glob to regex
  let regexStr: string
  if (pathPattern === '*') {
    regexStr = '.*'
  } else {
    regexStr = pathPattern
      .replace(/\*\*/g, '<!DOUBLE!>')
      .replace(/\*/g, '[^/]+')
      .replace(/<!DOUBLE!>/g, '.*')
      .replace(/\//g, '\\/')
  }

  return {
    method,
    pathRegex: new RegExp(`^${regexStr}$`),
    originalPattern: pattern,
  }
}
```

### `compilePersonaPolicy(config: PersonaPolicy, meta?): CompiledPolicy`

Main compilation entry point:

```typescript
function compilePersonaPolicy(config, meta?) {
  // Bash patterns: string or { pattern, comment } to { regex, comment }
  const deniedBashPatterns = []
  for (const entry of config.hardDeniedBashPatterns ?? []) {
    try {
      if (typeof entry === 'string') {
        deniedBashPatterns.push({ regex: new RegExp(entry) })
      } else {
        deniedBashPatterns.push({ regex: new RegExp(entry.pattern), comment: entry.comment })
      }
    } catch { /* skip invalid regex */ }
  }

  // API patterns
  const deniedApiPatterns = []
  for (const pattern of config.hardDeniedApiPatterns ?? []) {
    const compiled = compileApiPattern(pattern)
    if (compiled) deniedApiPatterns.push(compiled)
  }

  return {
    policyPath: meta?.basePath ? join(meta.basePath, 'permissions.json') : 'permissions.json',
    deniedReadGlobs: compileGlobs(config.hardDeniedReadPaths),
    deniedWriteGlobs: compileGlobs(config.hardDeniedWritePaths),
    deniedBashBaseCommands: new Set(
      (config.hardDeniedBashBaseCommands ?? []).map(cmd => cmd.toLowerCase())
    ),
    deniedBashPatterns,
    deniedMcpServers: new Set(config.hardDeniedMcpServers ?? []),
    deniedMcpTools: new Set(config.hardDeniedMcpTools ?? []),
    deniedApiPatterns,
    webFetchDenied: config.hardDeniedWebFetch ?? false,
    rawConfig: config,
  }
}
```

## Performance Characteristics

| Structure | Lookup | Used For |
|-----------|--------|----------|
| `Set<string>` | O(1) | Base commands, MCP servers, MCP tools |
| `RegExp[]` | O(n) per check | File globs, bash patterns, API paths |
| `boolean` | O(1) | WebFetch kill switch |

For typical policies (5-20 rules per category), the per-tool-call check cost is negligible.

## Error Handling

- Invalid glob pattern — skip silently, do not add to compiled array
- Invalid regex string — skip silently in bash patterns
- Invalid API pattern format — return null from `compileApiPattern`, skip
- Missing optional fields — default to empty array or false
- Never throw during compilation — a partially compiled policy is better than a crash
