# Hook Events Reference

Detailed documentation for each Claude Code hook event, including input format, output options, and examples.

## Common Input Fields

All hooks receive these fields via stdin JSON:

```json
{
  "session_id": "string",
  "transcript_path": "string",
  "cwd": "string",
  "permission_mode": "string",
  "hook_event_name": "string"
}
```

## Hook Options

All command hooks support these options:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `type` | string | required | `"command"` or `"prompt"` |
| `command` | string | required | Shell command to execute |
| `timeout` | number | 60 | Max execution time in seconds |
| `async` | boolean | false | Run without blocking Claude |

### Async Mode (`async: true`)

When `async: true`, the hook:
- Runs in the background without blocking Claude
- Cannot block actions (exit code 2 is ignored)
- Cannot return output to Claude
- Is ideal for logging, archival, notifications

**Best for:** Stop, SessionEnd, PostToolUse (logging only)
**Not recommended for:** PreToolUse (can't block), PermissionRequest (can't decide)

---

## PreToolUse

**Runs:** Before any tool call executes
**Can Block:** Yes (exit code 2)
**Matcher:** Tool name (Bash, Edit, Write, Read, WebFetch, etc.)

### Input

```json
{
  "session_id": "abc123",
  "cwd": "/path/to/project",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "npm run build",
    "description": "Build the project"
  }
}
```

### Output Options

**Block the action:**
```bash
echo "Reason for blocking" >&2
exit 2
```

**Allow with modified input:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "updatedInput": {
      "command": "npm run build --silent"
    }
  }
}
```

**Auto-approve permission:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "Safe command"
  }
}
```

---

## PostToolUse

**Runs:** After tool call completes successfully
**Can Block:** Limited (can stop further processing)
**Matcher:** Tool name

### Input

```json
{
  "session_id": "abc123",
  "cwd": "/path/to/project",
  "hook_event_name": "PostToolUse",
  "tool_name": "Edit",
  "tool_input": {
    "file_path": "/path/to/file.ts",
    "old_string": "...",
    "new_string": "..."
  },
  "tool_response": "File edited successfully"
}
```

### Output Options

**Add context for Claude:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "File was auto-formatted with prettier"
  }
}
```

**Block further processing:**
```json
{
  "decision": "block",
  "reason": "Critical error detected in output"
}
```

### Async PostToolUse (Logging Only)

For logging/telemetry that shouldn't slow down Claude:

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/scripts/log-bash-command.sh",
        "async": true,
        "timeout": 10
      }]
    }]
  }
}
```

**Note:** Async PostToolUse hooks cannot add context to Claude or block processing.

---

## UserPromptSubmit

**Runs:** When user submits a prompt, before Claude processes it
**Can Block:** Yes
**Matcher:** Not applicable

### Input

```json
{
  "session_id": "abc123",
  "cwd": "/path/to/project",
  "hook_event_name": "UserPromptSubmit",
  "user_prompt": "Help me fix the login bug"
}
```

### Output Options

**Add context (simple):**
```bash
echo "Current branch: $(git branch --show-current)"
echo "Last commit: $(git log -1 --oneline)"
exit 0
```

**Add context (JSON):**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "Project uses TypeScript 5.0, React 18"
  }
}
```

**Block prompt:**
```bash
echo "Prompt blocked: contains sensitive data" >&2
exit 2
```

---

## Stop

**Runs:** When Claude finishes responding
**Can Block:** Yes (force continuation)
**Matcher:** Not applicable

### Input

```json
{
  "session_id": "abc123",
  "cwd": "/path/to/project",
  "hook_event_name": "Stop",
  "stop_reason": "end_turn"
}
```

### Output Options

**Force Claude to continue:**
```json
{
  "decision": "block",
  "reason": "Tests are still failing. Please fix remaining errors."
}
```

**Allow stop:**
```bash
exit 0
```

### LLM-Based Stop Hook

```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "prompt",
        "prompt": "Check if all tasks are complete. If not, explain what remains.",
        "timeout": 30
      }]
    }]
  }
}
```

### Async Stop Hook (Archival/Logging)

For tasks that should run on session end without blocking:

```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "~/.claude/scripts/archive-session.sh",
        "async": true,
        "timeout": 30
      }]
    }]
  }
}
```

**Note:** Async hooks cannot force continuation (exit code 2 is ignored).

---

## SubagentStop

**Runs:** When a subagent (Task tool) completes
**Can Block:** Yes (force continuation)
**Matcher:** Not applicable

### Input

```json
{
  "session_id": "abc123",
  "cwd": "/path/to/project",
  "hook_event_name": "SubagentStop",
  "subagent_result": "Task completed successfully"
}
```

### Output Options

Same as Stop hook.

---

## PermissionRequest

**Runs:** When Claude shows a permission dialog
**Can Block:** Yes (auto-allow or auto-deny)
**Matcher:** Tool name

### Input

```json
{
  "session_id": "abc123",
  "cwd": "/path/to/project",
  "hook_event_name": "PermissionRequest",
  "tool_name": "Bash",
  "tool_input": {
    "command": "rm -rf node_modules"
  }
}
```

### Output Options

**Auto-allow:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "allow"
    }
  }
}
```

**Auto-deny:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "deny",
      "message": "This command is not allowed"
    }
  }
}
```

---

## SessionStart

**Runs:** At session start or resume
**Can Block:** No
**Matcher:** Not applicable

### Input

```json
{
  "session_id": "abc123",
  "cwd": "/path/to/project",
  "hook_event_name": "SessionStart"
}
```

### Output Options

**Add context:**
```bash
echo "Welcome! Project: $(basename $PWD)"
echo "Node version: $(node --version)"
exit 0
```

**Set environment variables:**
```bash
if [ -n "$CLAUDE_ENV_FILE" ]; then
  echo 'export NODE_ENV=development' >> "$CLAUDE_ENV_FILE"
  echo 'export DEBUG=true' >> "$CLAUDE_ENV_FILE"
fi
exit 0
```

---

## SessionEnd

**Runs:** When session ends
**Can Block:** No
**Matcher:** Not applicable

### Input

```json
{
  "session_id": "abc123",
  "cwd": "/path/to/project",
  "hook_event_name": "SessionEnd"
}
```

### Use Cases

- Cleanup temporary files
- Log session summary
- Send notifications

### Async SessionEnd (Recommended)

SessionEnd hooks are ideal candidates for `async: true` since they can't block anyway:

```json
{
  "hooks": {
    "SessionEnd": [{
      "hooks": [{
        "type": "command",
        "command": "~/.claude/scripts/cleanup-temp-files.sh",
        "async": true,
        "timeout": 30
      }]
    }]
  }
}
```

---

## Notification

**Runs:** When Claude sends a notification
**Can Block:** No
**Matcher:** Not applicable

### Input

```json
{
  "session_id": "abc123",
  "cwd": "/path/to/project",
  "hook_event_name": "Notification",
  "notification_type": "task_complete",
  "notification_message": "Build finished"
}
```

### Use Cases

- Custom notification sounds
- Slack/Discord webhooks
- Desktop notifications

---

## Setup

**Runs:** With `--init`, `--init-only`, or `--maintenance` flags
**Can Block:** Limited
**Matcher:** Not applicable

### Input

```json
{
  "session_id": "abc123",
  "cwd": "/path/to/project",
  "hook_event_name": "Setup",
  "setup_type": "init"
}
```

### Use Cases

- Project initialization
- Dependency checks
- Environment validation

---

## PreCompact

**Runs:** Before context window compaction
**Can Block:** No
**Matcher:** Not applicable

### Input

```json
{
  "session_id": "abc123",
  "cwd": "/path/to/project",
  "hook_event_name": "PreCompact"
}
```

### Use Cases

- Save important context before compaction
- Log context state
- Export conversation summary
