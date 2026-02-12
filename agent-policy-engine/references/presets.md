# Role Presets Reference

## Overview

Presets provide role-based default policies that users can apply with one click, then customize.
The preset name is stored in the policy JSON as metadata — it does not affect enforcement.

## Design Philosophy

- **Conservative by default** — ship safe presets, expand based on user feedback
- **Escalating access** — each preset is strictly more permissive than the previous
- **Customizable** — presets are starting points, not fixed profiles
- **Documented** — each preset has a human-readable description for the UI

## Preset Definitions

### `research` — Read/Search Only

```typescript
{
  preset: 'research',
  hardDeniedReadPaths: [],
  hardDeniedWritePaths: ['**'],              // Block ALL writes
  hardDeniedBashBaseCommands: [
    'rm', 'rmdir', 'mv', 'cp',              // File mutations
    'git push', 'git reset', 'git rebase',  // Git mutations
    'git checkout',                          // Branch switching
    'sudo', 'chmod', 'chown',               // System mutations
  ],
  hardDeniedBashPatterns: [],
}
```

**Use case:** Pure research persona — can read everything, write nothing, run no mutations.

### `reviewer` — Review and Verify

```typescript
{
  preset: 'reviewer',
  hardDeniedReadPaths: [],
  hardDeniedWritePaths: [],                  // Can write (review comments, etc.)
  hardDeniedBashBaseCommands: [
    'rm', 'rmdir',                           // File deletion
    'git push', 'git reset', 'git rebase',  // Git mutations
    'sudo',                                  // System escalation
  ],
  hardDeniedBashPatterns: [
    { pattern: 'rm\\s+-rf\\s+/', comment: 'Block recursive force-delete from root' },
  ],
}
```

**Use case:** Code review persona — can read, write review comments, run safe verification commands.

### `engineer` — Normal Development

```typescript
{
  preset: 'engineer',
  hardDeniedReadPaths: [
    '**/.env', '**/.env.*',                  // Environment secrets
    '**/credentials.enc',                    // Encrypted credentials
    '**/*.pem', '**/*.key',                  // Private keys
  ],
  hardDeniedWritePaths: [],
  hardDeniedBashBaseCommands: ['sudo'],      // Only sudo blocked
  hardDeniedBashPatterns: [
    { pattern: 'rm\\s+-rf\\s+/', comment: 'Block recursive force-delete from root' },
  ],
}
```

**Use case:** Standard engineering persona — full dev workflow, credentials hidden from agent,
catastrophic commands blocked.

### `admin` — Broad Access

```typescript
{
  preset: 'admin',
  // No deny rules — relies on permission modes for gating
}
```

**Use case:** Admin/ops persona — trusted access, relies on permission mode (safe/ask/auto) for
user confirmation rather than hard-deny rules.

## Preset Descriptions (for UI)

```typescript
const PRESET_DESCRIPTIONS = {
  research: 'Read/search only, no writes, no shell mutations',
  reviewer: 'Mostly read-only, safe verification, no direct merge',
  engineer: 'Normal dev workflow, destructive ops blocked, credentials hidden',
  admin: 'Broad access, catastrophic commands still hard-denied by permission modes',
}
```

## UI Integration

Display presets in a dropdown with descriptions:

```
Preset: [engineer]
  research  — Read/search only, no writes
  reviewer  — Safe verification commands
  engineer  — Normal dev, credentials hidden
  admin     — Broad access
```

When a preset is selected:
1. Load the preset's deny rules
2. Merge into the JSON textarea
3. User can customize further
4. Save persists the customized version with `preset` field preserved

## Future Enhancement Notes

Presets intentionally do not use the newer MCP/API/WebFetch deny fields yet (conservative rollout).
Proposed enhancements pending user feedback:

- `research`: Add `hardDeniedMcpTools` for mutation operations
- `reviewer`: Add `hardDeniedApiPatterns` for read-only enforcement
- `engineer`: Add `hardDeniedMcpTools` for credential operations (tool-level, not server-level)
