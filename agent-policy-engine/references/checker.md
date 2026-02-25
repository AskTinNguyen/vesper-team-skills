# Checker Reference

## Overview

The `checkHardDeny()` function is called on every tool invocation via the `PreToolUse` hook.
It dispatches on tool name, checks the relevant deny rules, and returns either a structured
`HardDenyPayload` (blocked) or `null` (allowed).

## Deny Payload Structure

```typescript
interface HardDenyPayload {
  toolName: string        // The tool that was blocked
  reason: string          // Human-readable explanation
  policyPath: string      // Path to the policy file (so user knows what to edit)
  matchedRule?: string    // The specific rule that matched (for debugging)
}
```

Always include `policyPath` — the formatted deny message should tell the user exactly which
file to edit to change the policy.

## Tool Category Dispatch

### File Read Tools: Read, Glob, Grep

```typescript
const READ_TOOLS = new Set(['Read', 'Glob', 'Grep'])

if (READ_TOOLS.has(toolName)) {
  const filePath = extractFilePath(toolName, toolInput)
  if (filePath) {
    const normalized = expandHome(filePath).replace(/\\/g, '/')
    for (const regex of policy.deniedReadGlobs) {
      if (regex.test(normalized)) {
        return {
          toolName,
          reason: `Policy denies reading "${filePath}"`,
          policyPath: policy.policyPath,
          matchedRule: `hardDeniedReadPaths: ${regex.source}`,
        }
      }
    }
  }
}
```

### File Write Tools: Write, Edit, MultiEdit, NotebookEdit

Same pattern as read tools but checks `deniedWriteGlobs`. Note `NotebookEdit` uses `notebook_path`
instead of `file_path`.

### Bash Commands (Two-Tier)

```typescript
if (toolName === 'Bash') {
  const command = String(toolInput.command || '')
  if (!command) return null

  // Tier 1: Fast base command lookup (O(1))
  const baseCmd = getBaseCommand(command).toLowerCase()
  if (policy.deniedBashBaseCommands.has(baseCmd)) {
    return {
      toolName,
      reason: `Policy denies bash command "${baseCmd}"`,
      policyPath: policy.policyPath,
      matchedRule: `hardDeniedBashBaseCommands: ${baseCmd}`,
    }
  }

  // Tier 2: Full command regex patterns (O(n))
  for (const { regex, comment } of policy.deniedBashPatterns) {
    if (regex.test(command)) {
      return {
        toolName,
        reason: comment
          ? `Policy denies this command: ${comment}`
          : `Policy denies this bash command pattern`,
        policyPath: policy.policyPath,
        matchedRule: `hardDeniedBashPatterns: ${regex.source}`,
      }
    }
  }
}
```

### MCP Tools (Server-First Fast Path)

MCP tool names follow the format `mcp__<server>__<tool>`:

```typescript
if (toolName.startsWith('mcp__')) {
  const parts = toolName.split('__')
  if (parts.length >= 3) {
    const server = parts[1]
    const tool = parts.slice(2).join('__')

    // Fast path: server-level deny (O(1))
    if (policy.deniedMcpServers.has(server)) {
      return { /* server blocked */ }
    }

    // Tool-level deny (O(1))
    const fullToolName = `${server}/${tool}`
    if (policy.deniedMcpTools.has(fullToolName)) {
      return { /* tool blocked */ }
    }
  }
}
```

Server-level deny is checked first — if the entire server is blocked, skip individual tool checks.

### API Tools

API tool names start with `api_`:

```typescript
if (toolName.startsWith('api_')) {
  const method = ((toolInput.method as string) || 'GET').toUpperCase()
  const path = (toolInput.path as string) || ''

  for (const pattern of policy.deniedApiPatterns) {
    // Method match (undefined = any method)
    if (pattern.method && pattern.method !== method) continue

    // Path match
    if (pattern.pathRegex.test(path)) {
      return {
        toolName,
        reason: `Policy denies API pattern "${pattern.originalPattern}" (matched ${method} ${path})`,
        policyPath: policy.policyPath,
        matchedRule: `hardDeniedApiPatterns: ${pattern.originalPattern}`,
      }
    }
  }
}
```

### WebFetch

```typescript
if (toolName === 'WebFetch' && policy.webFetchDenied) {
  return {
    toolName,
    reason: 'Policy denies WebFetch (all external requests blocked)',
    policyPath: policy.policyPath,
    matchedRule: 'hardDeniedWebFetch: true',
  }
}
```

## File Path Extraction Helper

Different tools store file paths in different input fields:

```typescript
function extractFilePath(toolName: string, toolInput: Record<string, unknown>): string | null {
  if (toolName === 'NotebookEdit') return (toolInput.notebook_path as string) || null
  if (typeof toolInput.file_path === 'string') return toolInput.file_path
  if (typeof toolInput.path === 'string') return toolInput.path
  return null
}
```

## Deny Message Formatting

```typescript
function formatHardDenyMessage(payload: HardDenyPayload): string {
  return (
    `${payload.reason}. ` +
    `To change this, switch to a different persona or edit the policy at ${payload.policyPath}.`
  )
}
```

Always tell the user HOW to fix it — never leave them stuck with just "denied".

## Integration with PreToolUse Hook

```typescript
// In agent SDK query loop
hooks: {
  PreToolUse: [{
    hooks: [async (input) => {
      // HARD-DENY — runs FIRST, overrides all permission modes
      if (this.personaPolicy) {
        const deny = checkHardDeny(
          input.tool_name,
          input.tool_input as Record<string, unknown>,
          this.personaPolicy,
        )
        if (deny) return blockWithReason(formatHardDenyMessage(deny))
      }

      // Permission mode logic follows (safe/ask/auto)
      // ...
    }]
  }]
}
```

## Runtime Policy Updates

The agent class needs a setter for hot-swapping policies when personas change:

```typescript
class Agent {
  private personaPolicy?: CompiledPolicy

  setPersonaPolicy(policy?: CompiledPolicy) {
    this.personaPolicy = policy
  }
}
```

Call `setPersonaPolicy()` when:
- Session starts with a persona that has a `permissions.json`
- User switches persona mid-session
- User clears persona (pass `undefined`)
