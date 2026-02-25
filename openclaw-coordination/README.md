# OpenClaw Coordination Extension

Multi-agent file coordination for OpenClaw. Prevents edit conflicts when multiple AI agents work on the same codebase.

## Overview

When multiple agents work simultaneously, they can accidentally edit the same files. This extension solves that with:

- **File Reservations** — Agents claim file patterns before editing
- **Conflict Detection** — Check if a file is reserved before touching it  
- **Mesh View** — See all active agents and what they're working on
- **Swarm Lock** — File-based mutex for atomic operations

Ported from [pi-messenger](https://github.com/AskTinNguyen/pi-messenger)'s battle-tested coordination patterns.

## Installation

```bash
cd ~/.openclaw/extensions/coordination

# Install dependencies
npm install

# Build TypeScript
npx tsc

# Link CLI globally (optional)
npm link
```

The CLI is available at `./bin/coord` or globally as `coord` after linking.

## CLI Usage

All commands output JSON for easy parsing by agents.

### `coord reserve`

Reserve file patterns for an agent. Other agents will see conflicts if they try to reserve overlapping paths.

```bash
# Reserve a directory and a file
coord reserve --patterns "src/api/,package.json" --agent "coder-A" --reason "Implementing auth"

# Output on success:
{
  "success": true,
  "agent": "coder-A",
  "reserved": ["src/api/", "package.json"],
  "reason": "Implementing auth"
}

# Output on conflict:
{
  "success": false,
  "error": "Conflicts detected",
  "conflicts": [
    { "agent": "coder-B", "pattern": "src/api/", "file": "src/api/" }
  ]
}
```

**Pattern rules:**
- `src/api/` (trailing slash) → matches `src/api/*` and all subdirectories
- `package.json` (no slash) → exact file match only

### `coord release`

Release reservations when done editing.

```bash
coord release --patterns "src/api/" --agent "coder-A"

# Output:
{
  "success": true,
  "agent": "coder-A",
  "released": ["src/api/"]
}
```

### `coord mesh`

View all active agents and their reservations.

```bash
coord mesh

# Output:
{
  "agents": [
    {
      "name": "coder-A",
      "sessionKey": "cli:coder-A:1707234567890",
      "model": "cli",
      "startedAt": "2024-02-06T15:30:00.000Z",
      "lastHeartbeat": "2024-02-06T15:35:00.000Z",
      "reservations": [
        { "pattern": "src/api/", "reason": "Implementing auth", "since": "..." }
      ]
    },
    {
      "name": "coder-B",
      "sessionKey": "cli:coder-B:1707234567891",
      "model": "cli",
      "reservations": []
    }
  ],
  "count": 2
}
```

### `coord conflicts`

Check if a specific file conflicts with any reservation.

```bash
coord conflicts --file "src/api/auth.ts"

# No conflict (exit code 0):
{
  "file": "src/api/auth.ts",
  "hasConflict": false,
  "conflicts": []
}

# Has conflict (exit code 1):
{
  "file": "src/api/auth.ts",
  "hasConflict": true,
  "conflicts": [
    { "agent": "coder-A", "pattern": "src/api/", "reason": "Implementing auth" }
  ]
}
```

## Integration with Agents

### Subagent Workflow

Before editing files, agents should:

1. **Reserve** the files/directories they'll modify
2. **Check conflicts** if reservation fails
3. **Do the work**
4. **Release** when done

```bash
# Agent startup
AGENT_NAME="coder-$(date +%s)"
coord reserve --patterns "src/auth/" --agent "$AGENT_NAME" --reason "Auth refactor"

# ... do work ...

# Agent cleanup
coord release --patterns "src/auth/" --agent "$AGENT_NAME"
```

### Checking Before Edit

Before modifying any file, check for conflicts:

```bash
FILE="src/api/users.ts"
if coord conflicts --file "$FILE" 2>/dev/null | jq -e '.hasConflict' > /dev/null; then
  echo "⚠️  $FILE is reserved by another agent"
  exit 1
fi
```

### Parallel Agent Coordination

When spawning multiple agents:

```bash
# Agent A gets src/api/
coord reserve --patterns "src/api/" --agent "agent-A" --reason "API work"

# Agent B gets src/ui/ (no conflict - different paths)
coord reserve --patterns "src/ui/" --agent "agent-B" --reason "UI work"

# Agent C tries src/api/auth.ts (CONFLICT - overlaps with Agent A)
coord reserve --patterns "src/api/auth.ts" --agent "agent-C" --reason "Auth fix"
# Returns error with conflicts array
```

## API Reference

Import functions directly for programmatic use:

```typescript
import {
  // Registration
  register,
  unregister,
  updateRegistration,
  getActiveAgents,
  
  // Reservations
  addReservations,
  removeReservations,
  getConflictsWithOtherAgents,
  
  // Task Claims
  claimTask,
  unclaimTask,
  completeTask,
  getClaims,
  getCompletions,
  
  // Locking
  withSwarmLock,
  
  // Types
  type CoordinationState,
  type AgentRegistration,
  type FileReservation,
  type ReservationConflict,
  type Dirs,
} from "@openclaw/coordination";
```

### Key Functions

#### `register(state, dirs)`
Register an agent in the coordination mesh.

#### `addReservations(patterns, reason, state, dirs)`
Add file pattern reservations for the agent.

#### `getConflictsWithOtherAgents(path, state, dirs)`
Check if a path conflicts with other agents' reservations.

#### `withSwarmLock(dirs, fn)`
Execute a function with exclusive swarm lock (mutex).

### Types

```typescript
interface FileReservation {
  pattern: string;    // "src/api/" or "file.ts"
  reason?: string;    // Why reserved
  since: string;      // ISO timestamp
}

interface ReservationConflict {
  path: string;       // The conflicting path
  agent: string;      // Who owns it
  pattern: string;    // Their reservation pattern
  reason?: string;    // Why they reserved it
}

interface Dirs {
  base: string;       // ~/.openclaw/coordination
  registry: string;   // .../registry
  reservations: string;
  claims: string;
}
```

## Architecture

```
~/.openclaw/coordination/
├── registry/              # Agent registrations
│   ├── coder-A.json
│   └── coder-B.json
├── reservations/          # (Currently embedded in registry)
├── claims/                # Task claim state
│   └── claims.json
└── swarm.lock            # Mutex lock file
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENCLAW_COORD_DIR` | `~/.openclaw/coordination` | Base coordination directory |

## Status

| Component | Status |
|-----------|--------|
| File Reservations | ✅ Complete |
| Conflict Detection | ✅ Complete |
| CLI Interface | ✅ Complete |
| Swarm Lock | ✅ Complete |
| Task Claims | ✅ Complete |
| Session Liveness | ⏳ Placeholder (needs gateway API) |
| Unit Tests | ⏳ Pending |

## License

MIT
