# Edit with AI - Architecture Deep Dive

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              RENDERER PROCESS                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐    ┌─────────────────┐    ┌────────────────────────┐  │
│  │  Feature Panel   │───▶│   EditPopover   │───▶│   Deep Link Handler    │  │
│  │  (Detail View)   │    │   (Text Input)  │    │   (vesper://action/    │  │
│  │                  │    │                 │    │    new-chat?...)       │  │
│  └──────────────────┘    └─────────────────┘    └───────────┬────────────┘  │
│                                                              │               │
│                                                              ▼               │
│                         ┌─────────────────────────────────────┐              │
│                         │        Focused Chat Window          │              │
│                         │   (New session with injected        │              │
│                         │    context + auto-send)             │              │
│                         └───────────────────┬─────────────────┘              │
│                                             │                                │
└─────────────────────────────────────────────┼────────────────────────────────┘
                                              │
                                              ▼ IPC: session-command
┌─────────────────────────────────────────────────────────────────────────────┐
│                               MAIN PROCESS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                         Session Manager                                 │ │
│  │                                                                         │ │
│  │   ┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐  │ │
│  │   │  VesperAgent    │◀──▶│ Session-Scoped   │◀──▶│  Feature Service │  │ │
│  │   │  (Agent SDK)    │    │ Tool Callbacks   │    │  (Business Logic)│  │ │
│  │   └─────────────────┘    └──────────────────┘    └──────────────────┘  │ │
│  │           │                       │                       │             │ │
│  │           │                       │                       │             │ │
│  │           ▼                       ▼                       ▼             │ │
│  │   ┌─────────────────────────────────────────────────────────────────┐  │ │
│  │   │                    Event Broadcaster                             │  │ │
│  │   │              (Notifies all renderer windows)                     │  │ │
│  │   └─────────────────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### 1. EditPopover (Renderer)

**Purpose:** Capture natural language input and launch focused chat session

**Key responsibilities:**
- Display context-aware placeholder text with example
- Build prompt with XML metadata for agent context
- Create deep link URL with encoded parameters
- Open focused chat window via `window.electronAPI.openUrl()`

**Deep Link Parameters:**
```
vesper://workspace/{workspaceId}/action/new-chat
  ?window=focused           # Open smaller focused window (900x700)
  &input={encodedPrompt}    # Pre-filled message with context
  &send=true                # Auto-send the message immediately
  &mode={permissionMode}    # Permission mode (safe/ask/allow-all)
  &badges={encodedBadges}   # Badge metadata for hiding XML in UI
  &workdir={workingDir}     # Working directory (user_default/none/path)
```

### 2. Session-Scoped Tools (Shared Package)

**Purpose:** Provide AI-callable tools with session-isolated callbacks

**Key design patterns:**
- **Factory functions:** Each tool is created by a factory (e.g., `createScheduleUpdateTool(sessionId)`)
- **Callback registry:** `Map<sessionId, SessionScopedToolCallbacks>` for session isolation
- **Zod schemas:** Type-safe parameter validation using zod
- **Error handling:** Return structured `{ content, isError }` responses

**Tool lifecycle:**
1. Session created → `registerSessionScopedToolCallbacks(sessionId, callbacks)`
2. Tool called → Look up callbacks in registry, execute with `await callbacks.onXxx(data)`
3. Session disposed → `unregisterSessionScopedToolCallbacks(sessionId)`

### 3. VesperAgent (Shared Package)

**Purpose:** Bridge between session-scoped tools and main process

**Key responsibilities:**
- Register callbacks during agent initialization
- Expose callback properties for main process to wire up
- Handle session lifecycle (registration, cleanup)

### 4. Session Manager (Main Process)

**Purpose:** Wire up business logic to agent callbacks

**Key responsibilities:**
- Set agent callbacks when session is created
- Call appropriate services to execute operations
- Broadcast events for UI reactivity
- Handle errors and logging

## Context Badge Pattern

The EditPopover uses content badges to hide XML metadata from the user while keeping it in the actual message:

```typescript
// Build prompt with metadata
const { prompt, badges } = buildEditPrompt(context, userInstructions);

// prompt = "<edit_request>...metadata...</edit_request>\n\nUser message"
// badges = [{ type: 'context', label: 'Edit Schedule', start: 0, end: 100, ... }]
```

**In the UI:**
- User sees: Badge showing "Edit Schedule" + their typed message
- Agent sees: Full XML metadata + user message

This creates a clean UX while providing the agent with full context.

## Permission Modes for Edit Sessions

Most edit sessions use `allow-all` mode by default for fast execution:

| Mode | When to Use |
|------|-------------|
| `allow-all` | Default for edit sessions - allows immediate execution |
| `ask` | Use for destructive operations that need confirmation |
| `safe` | Use for read-only/preview operations |

## Event Broadcasting Pattern

After successful operations, broadcast events for UI reactivity:

```typescript
// In session manager callback
broadcast({
  type: 'schedule-updated',
  scheduleId: result.id,
  workspaceId: managed.workspace.id,
}, managed.workspace.id);
```

**Event naming conventions:**
- `{feature}-created` - New item created
- `{feature}-updated` - Existing item modified
- `{feature}-deleted` - Item removed

## Working Directory Configuration

The `workdir` parameter controls session working directory:

| Value | Behavior |
|-------|----------|
| `'none'` | No working directory (session folder only) - best for config edits |
| `'user_default'` | Use workspace's configured default directory |
| `/absolute/path` | Use specific directory path |

Most "Edit with AI" sessions use `'none'` since they're editing app configuration, not project files.
