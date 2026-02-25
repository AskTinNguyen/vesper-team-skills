# Path Matching Utilities Reference

## Overview

Shared utilities used by both the policy checker and permission mode logic. These must be in a
separate module so both can import without circular dependencies.

## Functions

### `expandHome(path: string): string`

Replace leading `~` with the actual home directory:

```typescript
import { homedir } from 'os'

function expandHome(path: string): string {
  if (path.startsWith('~/') || path === '~') {
    return path.replace(/^~/, homedir())
  }
  return path
}
```

### `globToRegex(pattern: string): RegExp`

Convert glob patterns to anchored regular expressions:

```typescript
function globToRegex(pattern: string): RegExp {
  const regex = expandHome(pattern)
    .replace(/[.+^${}()|[\]\\]/g, '\\$&')   // Escape regex special chars
    .replace(/\*\*/g, '\0DOUBLE\0')           // Temporarily mark **
    .replace(/\*/g, '[^/]*')                  // * = single segment
    .replace(/\0DOUBLE\0/g, '.*')             // ** = anything
    .replace(/\?/g, '.')                      // ? = single char

  return new RegExp(`^${regex}$`)
}
```

**Glob semantics:**
- `**` — matches anything including path separators (recursive)
- `*` — matches anything except path separators (single directory level)
- `?` — matches a single character

**Important:** The double-star placeholder technique (`\0DOUBLE\0`) prevents `**` from being
partially consumed by the single `*` replacement. Process `**` first, replace with placeholder,
then handle `*`, then restore.

### `matchesGlobPatterns(filePath: string, patterns: string[]): boolean`

Test a file path against an array of glob patterns:

```typescript
function matchesGlobPatterns(filePath: string, patterns: string[]): boolean {
  const normalized = expandHome(filePath).replace(/\\/g, '/')

  for (const pattern of patterns) {
    try {
      if (globToRegex(pattern).test(normalized)) return true
    } catch {
      // Skip invalid glob patterns
    }
  }
  return false
}
```

### `getBaseCommand(command: string): string`

Extract the base command for deny-list matching. Special handling for compound commands
where the subcommand is part of the base identity:

```typescript
function getBaseCommand(command: string): string {
  const trimmed = command.trim()

  // Git-aware: 'git push origin main' to 'git push'
  if (trimmed.startsWith('git ')) {
    const parts = trimmed.split(/\s+/)
    if (parts.length >= 2) {
      return `${parts[0]} ${parts[1]}`
    }
  }

  // Default: first word only
  return trimmed.split(/\s+/)[0] || trimmed
}
```

**Why git is special:** `git` alone is not meaningful — `git status` (safe) and `git push` (dangerous)
are fundamentally different operations. Extract `git <subcommand>` as the base to enable
fine-grained git deny rules.

**Extensible:** Add similar handling for other compound commands as needed (e.g., `docker compose`,
`kubectl`, `npm run`).

## Edge Cases

1. **Windows paths:** Normalize backslashes to forward slashes before matching
2. **Home directory:** Always expand `~` before matching — `~/.env` should match `**/.env`
3. **Trailing slashes:** Glob patterns should work with or without trailing slashes
4. **Empty command:** `getBaseCommand('')` returns `''` — caller should check for empty before deny
5. **Case sensitivity:** Base commands are lowercased for Set lookup; glob patterns are case-sensitive
