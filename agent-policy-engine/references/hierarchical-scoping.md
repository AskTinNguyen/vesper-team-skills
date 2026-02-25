# Hierarchical Permission Scoping Reference

## Overview

The policy engine does not exist in isolation. It operates as the innermost layer of a cascading
configuration hierarchy. Understanding where policies sit in this hierarchy is essential for
correct implementation.

## Five-Level Hierarchy

```
Level 1: GLOBAL DEFAULTS       (app-level config.json)
  ↓ overridden by
Level 2: WORKSPACE CONFIG      (project-level config.json + permissions.json)
  ↓ overridden by
Level 3: PERSONA DEFAULTS      (role-level personas.json + permissions.json)
  ↓ frozen into
Level 4: SESSION SNAPSHOT       (conversation-level, frozen at creation)
  ↓ enforced by
Level 5: RUNTIME ENFORCEMENT    (PreToolUse hook: deny-first, then mode, then allow-list)
```

Each setting resolves using first-wins logic: explicit options beat persona defaults, which beat
workspace defaults, which beat global defaults.

## Resolution Pattern

```typescript
// First non-null value wins
const permissionMode = options?.permissionMode        // Explicit
  ?? personaDefault?.mode                              // Persona
  ?? workspaceConfig?.defaults?.permissionMode          // Workspace
  ?? globalDefaults.workspaceDefaults.permissionMode    // Global fallback
```

This pattern applies to all configurable settings: permission mode, model, thinking level,
working directory, provider ID.

## Dual Permission System

Two distinct permission files serve complementary purposes at different hierarchy levels:

### Workspace Permissions (Allow-List)

**Location:** `{workspace}/permissions.json`
**Direction:** Additive — extends defaults to allow MORE operations
**Purpose:** Customize what's auto-approved in read-only (Explore/safe) mode
**Scope:** All sessions in the workspace

```json
{
  "allowedBashPatterns": [
    { "pattern": "^ls\\b", "comment": "List directory contents" },
    { "pattern": "^git\\s+(status|log|diff)\\b", "comment": "Git read operations" }
  ],
  "allowedMcpPatterns": [
    { "pattern": "search", "comment": "Search operations" },
    { "pattern": "list", "comment": "List operations" }
  ],
  "allowedApiEndpoints": [],
  "allowedWritePaths": []
}
```

### Persona Policy (Deny-List)

**Location:** `{persona-folder}/permissions.json`
**Direction:** Subtractive — blocks operations regardless of mode
**Purpose:** Hard-deny rules that the agent cannot bypass
**Scope:** Single persona (applied to sessions using that persona)

```json
{
  "preset": "engineer",
  "hardDeniedReadPaths": ["**/.env"],
  "hardDeniedBashBaseCommands": ["sudo"]
}
```

### Why They Never Conflict

These systems answer different questions:
- **Allow-list:** "Is this operation safe enough to auto-approve in read-only mode?"
- **Deny-list:** "Should this operation be blocked regardless of any other settings?"

A tool call can be:
1. Denied by persona policy → blocked (never reaches permission mode)
2. Allowed by persona policy, then checked by permission mode:
   - Safe mode → check workspace allow-list
   - Ask mode → prompt user
   - Auto mode → allow

### Additive Merging

Workspace permissions merge additively across levels:

```
Default allow-list (bundled in app resources)
  + Workspace overrides (project-specific permissions.json)
  + Source overrides (per-MCP-server permissions.json)
  = Final Explore mode rules
```

Each level can only ADD more allowed patterns, never remove defaults.

## Session Snapshotting

Sessions freeze their resolved configuration at creation time:

```typescript
// Persisted in session.jsonl header (line 1)
{
  permissionMode: 'ask',
  personaId: 'engineer-bot',
  personaName: 'Engineer',
  providerId: 'claude',
  model: 'claude-sonnet-4-5',
  thinkingLevel: 'think',
  workingDirectory: '/project',
}
```

**Why this matters:**
- Concurrent sessions with different providers/personas don't contaminate each other
- App restarts restore exact session configuration from the snapshot
- Changing workspace defaults doesn't retroactively modify existing sessions
- The persona policy is compiled once at session start and stored on the agent instance

## Permission Escalation Guard

Personas can request `defaultPermissionMode: 'allow-all'`, but this requires explicit opt-in:

```typescript
// In session creation flow
function resolvePersonaPermissionDefault(mode, allowEscalation) {
  if (mode === 'allow-all' && !allowEscalation) {
    return { mode: undefined }  // Falls through to safer workspace/global default
  }
  return { mode }
}
```

**Configuration:**
```json
{
  "name": "Auto Engineer",
  "defaultPermissionMode": "allow-all",
  "allowPermissionModeEscalation": true  // Required for allow-all to take effect
}
```

Without the explicit flag, the persona cannot escalate permissions. This prevents misconfigured
personas from bypassing safety defaults.

## Runtime Enforcement Order

In the agent's PreToolUse hook:

```
Tool call arrives
  ↓
1. PERSONA HARD-DENY (Level 5 - deny-list)
   Denied? → Block immediately, skip everything else
  ↓
2. PERMISSION MODE CHECK (Level 4 - session snapshot)
   Safe mode? → Go to step 3
   Ask mode? → Prompt user for write/bash operations
   Auto mode? → Allow
  ↓
3. WORKSPACE ALLOW-LIST (Level 2 - Explore mode rules)
   Pattern matched? → Allow
   Not matched? → Block (safe mode) or prompt (ask mode)
  ↓
4. Tool executes
```

## Implementation Checklist

When implementing hierarchical scoping in a new application:

- [ ] Define config levels with clear storage locations
- [ ] Implement first-wins resolution (null-coalescing chain)
- [ ] Separate allow-lists (additive, workspace) from deny-lists (subtractive, persona)
- [ ] Snapshot all resolved settings at session creation
- [ ] Guard permission escalation with explicit opt-in flags
- [ ] Make workspace permissions additive-only (can extend, never restrict)
- [ ] Enforce deny-list BEFORE permission mode in the tool hook
- [ ] Persist session snapshots for restart recovery
- [ ] Test concurrent sessions with different configs for isolation
