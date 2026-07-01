#!/usr/bin/env python3
"""
Block Dangerous Commands Hook

PreToolUse hook that blocks potentially destructive bash commands.
Blocks: rm -rf, format, dd, mkfs, chmod 777, etc.

Usage in settings.json:
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/skills/claude-code-hooks/scripts/block_dangerous.py"
      }]
    }]
  }
}
"""

import json
import sys
import re

# Patterns to block (case-insensitive)
DANGEROUS_PATTERNS = [
    r'rm\s+-rf\s+/',           # rm -rf /
    r'rm\s+-rf\s+~',           # rm -rf ~
    r'rm\s+-rf\s+\*',          # rm -rf *
    r'rm\s+-rf\s+\.',          # rm -rf .
    r':\(\)\s*\{\s*:\|:&\s*\}\s*;', # Fork bomb
    r'>(\/dev\/sd[a-z]|\/dev\/hd[a-z])', # Write to disk device
    r'dd\s+if=.*of=/dev/',     # dd to disk
    r'mkfs\.',                 # Format filesystem
    r'chmod\s+-R\s+777\s+/',   # Dangerous chmod
    r'chown\s+-R.*:.*\s+/',    # Dangerous chown on root
    r'>\s*/etc/passwd',        # Overwrite passwd
    r'>\s*/etc/shadow',        # Overwrite shadow
    r'curl.*\|\s*(ba)?sh',     # Pipe curl to shell
    r'wget.*\|\s*(ba)?sh',     # Pipe wget to shell
    r'eval\s+.*\$\(',          # Dangerous eval
    r'DROP\s+DATABASE',        # SQL drop database
    r'DROP\s+TABLE',           # SQL drop table
    r'TRUNCATE\s+TABLE',       # SQL truncate
    r'--no-preserve-root',     # Dangerous rm flag
]

# Specific commands to block
BLOCKED_COMMANDS = [
    'rm -rf /',
    'rm -rf /*',
    'rm -rf ~',
    'rm -rf ~/*',
    'rm -rf .',
    'rm -rf ..',
    'rm -rf $HOME',
    'shutdown',
    'reboot',
    'halt',
    'poweroff',
    'init 0',
    'init 6',
]


def is_dangerous(command: str) -> tuple[bool, str]:
    """Check if command matches dangerous patterns."""
    command_lower = command.lower().strip()

    # Check exact blocked commands
    for blocked in BLOCKED_COMMANDS:
        if blocked.lower() in command_lower:
            return True, f"Blocked command: {blocked}"

    # Check patterns
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True, f"Matched dangerous pattern: {pattern}"

    return False, ""


def main():
    try:
        data = json.load(sys.stdin)
        tool_input = data.get('tool_input', {})
        command = tool_input.get('command', '')

        if not command:
            sys.exit(0)

        dangerous, reason = is_dangerous(command)

        if dangerous:
            print(f"BLOCKED: {reason}\nCommand: {command}", file=sys.stderr)
            sys.exit(2)  # Exit 2 blocks the action

        sys.exit(0)

    except json.JSONDecodeError:
        print("Hook error: Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
