#!/usr/bin/env python3
"""
Log Commands Hook

PreToolUse hook that logs all bash commands to a file for audit/review.

Usage in settings.json:
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/skills/claude-code-hooks/scripts/log_commands.py"
      }]
    }]
  }
}

Log file location: ~/.claude/command-log.txt
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Log file location
LOG_FILE = Path.home() / '.claude' / 'command-log.txt'


def ensure_log_dir():
    """Ensure log directory exists."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def log_command(session_id: str, cwd: str, command: str, description: str = ""):
    """Append command to log file."""
    ensure_log_dir()

    timestamp = datetime.now().isoformat()

    log_entry = f"""
---
timestamp: {timestamp}
session: {session_id}
cwd: {cwd}
description: {description}
command: |
  {command}
"""

    with open(LOG_FILE, 'a') as f:
        f.write(log_entry)


def main():
    try:
        data = json.load(sys.stdin)

        session_id = data.get('session_id', 'unknown')
        cwd = data.get('cwd', os.getcwd())
        tool_input = data.get('tool_input', {})

        command = tool_input.get('command', '')
        description = tool_input.get('description', '')

        if command:
            log_command(session_id, cwd, command, description)

        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(1)
    except Exception as e:
        # Don't block on logging errors
        print(f"Log hook error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
