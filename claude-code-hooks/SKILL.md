---
name: claude-code-hooks
description: This skill should be used when implementing pre-hooks and post-hooks for Claude Code. It applies when users want to add automation, validation, formatting, logging, or custom behavior that triggers before or after Claude's tool executions. Triggers on requests like "add a hook", "run prettier after edits", "validate commands", "log bash commands", "block dangerous operations", or mentions of PreToolUse, PostToolUse, Stop, UserPromptSubmit hooks.
---

# Claude Code Hooks

## Overview

Claude Code hooks are user-defined shell commands that execute automatically at various points in Claude's lifecycle. They provide deterministic control over behavior—ensuring certain actions always happen rather than relying on the LLM to decide.

## When to Use Hooks

| Use Case | Hook Event | Example |
|----------|------------|---------|
| Auto-format code after edits | PostToolUse | Run prettier on saved files |
| Validate commands before execution | PreToolUse | Block dangerous rm -rf commands |
| Log all bash commands | PreToolUse | Audit trail for compliance |
| Add context to prompts | UserPromptSubmit | Inject project-specific info |
| Ensure task completion | Stop | Verify all tests pass before stopping |
| Block edits to sensitive files | PreToolUse | Protect .env, credentials |
| Run linters after writes | PostToolUse | ESLint, Rubocop, etc. |

## Hook Events Reference

| Event | When It Runs | Can Block? | Common Uses |
|-------|--------------|------------|-------------|
| **PreToolUse** | Before tool calls | Yes | Validation, security, logging |
| **PostToolUse** | After tool calls | Limited | Formatting, linting, notifications |
| **UserPromptSubmit** | When user submits prompt | Yes | Add context, validate input |
| **Stop** | When Claude finishes | Yes | Force continuation if incomplete |
| **SubagentStop** | When subagent completes | Yes | Verify subagent work |
| **PermissionRequest** | Permission dialog shown | Yes | Auto-allow/deny patterns |
| **Notification** | Claude sends notification | No | Custom notification handling |
| **SessionStart** | Session begins | No | Environment setup |
| **SessionEnd** | Session ends | No | Cleanup, logging |
| **Setup** | With --init flags | Limited | Initial configuration |
| **PreCompact** | Before context compaction | No | Save important context |

## Configuration

Hooks are configured in JSON settings files (in order of precedence):
1. `.claude/settings.local.json` - Local project (gitignored)
2. `.claude/settings.json` - Project settings
3. `~/.claude/settings.json` - User settings (global)

### Basic Structure

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolPattern",
        "hooks": [
          {
            "type": "command",
            "command": "your-bash-command",
            "timeout": 60,
            "async": false
          }
        ]
      }
    ]
  }
}
```

### Hook Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `type` | string | required | `"command"` (shell) or `"prompt"` (LLM-based) |
| `command` | string | required | Shell command to execute (for `type: "command"`) |
| `prompt` | string | required | LLM prompt (for `type: "prompt"`) |
| `timeout` | number | 60 | Maximum execution time in seconds |
| `async` | boolean | false | Run asynchronously without blocking Claude |

### Async Hooks

When `async: true`, the hook runs in the background without blocking Claude's execution. This is ideal for:

- **Logging and analytics** - Write to files or send telemetry
- **Archival** - Save state before session ends
- **Notifications** - Send Slack/Discord webhooks
- **Long-running tasks** - Operations that don't need to complete before Claude continues

**Important:** Async hooks cannot:
- Block or modify Claude's actions (exit code 2 is ignored)
- Return output to Claude (stdout/stderr is discarded)
- Guarantee completion before the session ends

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

### Matcher Patterns

- `*` or `""` - Match all tools
- `Bash` - Match only Bash tool
- `Edit|Write` - Match Edit OR Write tools
- `mcp__server__.*` - Match MCP tools (regex)

**Note:** `matcher` is not used for `UserPromptSubmit`, `Stop`, `SubagentStop`, `Setup`, `SessionStart`, `SessionEnd`.

## Quick Start Examples

### Auto-Format with Prettier

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write \"$CLAUDE_PROJECT_DIR\"",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### Log All Bash Commands

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.command' >> ~/.claude/bash-log.txt"
          }
        ]
      }
    ]
  }
}
```

### Block Dangerous Commands

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/skills/claude-code-hooks/scripts/block_dangerous.py"
          }
        ]
      }
    ]
  }
}
```

### Protect Sensitive Files

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/skills/claude-code-hooks/scripts/protect_files.py"
          }
        ]
      }
    ]
  }
}
```

### Archive Tasks on Session End (Async)

```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "~/.claude/skills/dispatch/hooks/auto-archive.sh",
        "async": true,
        "timeout": 30
      }]
    }]
  }
}
```

This archives task lists to `~/.claude/tasks-archive/` when sessions end, running asynchronously so it doesn't delay Claude's response.

### Send Slack Notification (Async)

```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "curl -X POST -d '{\"text\":\"Claude session complete\"}' $SLACK_WEBHOOK_URL",
        "async": true,
        "timeout": 10
      }]
    }]
  }
}
```

## Hook Input/Output

### Input (via stdin)

Hooks receive JSON with context:

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

### Output (via exit code + stdout/stderr)

| Exit Code | Meaning | Behavior |
|-----------|---------|----------|
| **0** | Success | Continue, parse JSON stdout for control |
| **2** | Block | Stop action, show stderr to Claude |
| **Other** | Error | Log stderr, continue execution |

### Control via JSON Output

For advanced control, output JSON with exit code 0:

```json
{
  "continue": true,
  "suppressOutput": false,
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "additionalContext": "Extra info for Claude"
  }
}
```

## Writing Hook Scripts

### Template for PreToolUse Validation

```python
#!/usr/bin/env python3
import json
import sys

def main():
    try:
        data = json.load(sys.stdin)
        tool_input = data.get('tool_input', {})

        # Your validation logic here
        if should_block(tool_input):
            print("Blocked: reason here", file=sys.stderr)
            sys.exit(2)  # Block the action

        # Optionally add context
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": "Hook approved this action"
            }
        }))
        sys.exit(0)

    except Exception as e:
        print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(1)

def should_block(tool_input):
    # Implement your logic
    return False

if __name__ == "__main__":
    main()
```

### Template for PostToolUse Actions

```python
#!/usr/bin/env python3
import json
import sys
import subprocess

def main():
    try:
        data = json.load(sys.stdin)
        tool_name = data.get('tool_name', '')
        tool_input = data.get('tool_input', {})

        # Example: Run formatter on edited files
        if tool_name in ['Edit', 'Write']:
            file_path = tool_input.get('file_path', '')
            if file_path.endswith(('.ts', '.tsx', '.js', '.jsx')):
                subprocess.run(['npx', 'prettier', '--write', file_path])

        sys.exit(0)

    except Exception as e:
        print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Environment Variables

Available in hook scripts:

| Variable | Description |
|----------|-------------|
| `$CLAUDE_PROJECT_DIR` | Absolute path to project root |
| `$CLAUDE_CODE_REMOTE` | `"true"` for web, empty for CLI |
| `$CLAUDE_ENV_FILE` | File to write env vars (SessionStart only) |

## Debugging Hooks

1. **Use debug mode**: `claude --debug`
2. **Check verbose output**: Press `ctrl+o` in Claude Code
3. **Test hooks manually**: Pipe test JSON to your script

```bash
echo '{"tool_input":{"command":"rm -rf /"}}' | python3 my_hook.py
echo $?  # Check exit code
```

4. **Use the `/hooks` command** in Claude Code to review active hooks

## Best Practices

1. **Always quote variables**: Use `"$VAR"` not `$VAR`
2. **Use absolute paths**: Reference scripts with full paths or `$CLAUDE_PROJECT_DIR`
3. **Set reasonable timeouts**: Default is 60s, adjust as needed
4. **Handle errors gracefully**: Exit 1 for non-blocking errors, 2 to block
5. **Test thoroughly**: Hooks run automatically—bugs can be disruptive
6. **Keep hooks fast**: They run synchronously and affect responsiveness
7. **Use `async: true` for non-blocking tasks**: Logging, archival, notifications, and analytics that don't need to block Claude

## Security Considerations

- Hooks execute with your credentials
- Always review hook code before adding
- Validate and sanitize all inputs
- Block path traversal (`..` in paths)
- Protect sensitive files (.env, .git/, keys)

## Resources

This skill includes helper scripts in the `scripts/` directory:

| Script | Hook Event | Purpose |
|--------|------------|---------|
| `block_dangerous.py` | PreToolUse | Block dangerous bash commands (rm -rf, etc.) |
| `protect_files.py` | PreToolUse | Protect sensitive files (.env, credentials) |
| `format_on_save.py` | PostToolUse | Auto-format files after edits |
| `log_commands.py` | PreToolUse | Log all bash commands to audit file |
| `save_quality_prompts.py` | UserPromptSubmit | Auto-save high-quality prompts (regex) |
| `save_quality_prompts_llm.py` | UserPromptSubmit | Auto-save high-quality prompts (LLM) |
| `save_implementation_plans.py` | PostToolUse | Save approved plans to separate repo |
| `compound_docs_trigger.py` | UserPromptSubmit | Remind about compound-docs after fixes |

### Save Quality Prompts

Automatically saves your high-quality prompts to `~/.claude/saved-prompts.md`:

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/skills/claude-code-hooks/scripts/save_quality_prompts.py"
      }]
    }]
  }
}
```

**LLM-enhanced version** (uses local Qwen model, runs in background):
```json
"command": "python3 ~/.claude/skills/claude-code-hooks/scripts/save_quality_prompts_llm.py"
```

### Save Implementation Plans

Automatically saves approved Claude Code plans to a separate repository:

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/skills/claude-code-hooks/scripts/save_implementation_plans.py"
      }]
    }]
  }
}
```

**Configuration:**
```bash
# Set custom repo location (default: ~/.claude/saved-plans/)
export CLAUDE_PLANS_REPO=~/repos/my-plans

# Enable git auto-commit
export CLAUDE_PLANS_GIT_COMMIT=true

# Enable git auto-push (requires CLAUDE_PLANS_GIT_COMMIT)
export CLAUDE_PLANS_GIT_PUSH=true
```

**Repository structure:**
```
~/.claude/saved-plans/
├── index.md                    # Auto-generated index
└── 2026/01/
    ├── 2026-01-21-project-auth-refactor.md
    └── 2026-01-21-api-rate-limiting.md
```

See `references/hook_events.md` for detailed documentation on each hook event and its specific input/output format.
