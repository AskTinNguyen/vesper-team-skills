#!/usr/bin/env python3
"""
Format on Save Hook

PostToolUse hook that auto-formats files after Claude edits them.
Supports: prettier (JS/TS/CSS/HTML), black (Python), rubocop (Ruby)

Usage in settings.json:
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/skills/claude-code-hooks/scripts/format_on_save.py",
        "timeout": 30
      }]
    }]
  }
}
"""

import json
import sys
import subprocess
import os
from pathlib import Path

# File extension to formatter mapping
FORMATTERS = {
    # JavaScript/TypeScript (prettier)
    '.js': ['npx', 'prettier', '--write'],
    '.jsx': ['npx', 'prettier', '--write'],
    '.ts': ['npx', 'prettier', '--write'],
    '.tsx': ['npx', 'prettier', '--write'],
    '.mjs': ['npx', 'prettier', '--write'],
    '.cjs': ['npx', 'prettier', '--write'],

    # Web (prettier)
    '.html': ['npx', 'prettier', '--write'],
    '.css': ['npx', 'prettier', '--write'],
    '.scss': ['npx', 'prettier', '--write'],
    '.less': ['npx', 'prettier', '--write'],
    '.json': ['npx', 'prettier', '--write'],
    '.yaml': ['npx', 'prettier', '--write'],
    '.yml': ['npx', 'prettier', '--write'],
    '.md': ['npx', 'prettier', '--write'],

    # Python (black)
    '.py': ['black', '--quiet'],

    # Ruby (rubocop)
    '.rb': ['rubocop', '-A', '--fail-level', 'error'],

    # Go (gofmt)
    '.go': ['gofmt', '-w'],

    # Rust (rustfmt)
    '.rs': ['rustfmt'],
}


def get_formatter(file_path: str) -> list[str] | None:
    """Get the formatter command for a file extension."""
    ext = Path(file_path).suffix.lower()
    return FORMATTERS.get(ext)


def format_file(file_path: str, formatter: list[str]) -> bool:
    """Run formatter on file. Returns True if successful."""
    try:
        cmd = formatter + [file_path]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=25
        )
        return result.returncode == 0
    except FileNotFoundError:
        # Formatter not installed, skip silently
        return True
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False


def main():
    try:
        data = json.load(sys.stdin)
        tool_name = data.get('tool_name', '')
        tool_input = data.get('tool_input', {})

        # Only format after Edit or Write
        if tool_name not in ['Edit', 'Write']:
            sys.exit(0)

        file_path = tool_input.get('file_path', '')
        if not file_path or not os.path.isfile(file_path):
            sys.exit(0)

        formatter = get_formatter(file_path)
        if not formatter:
            sys.exit(0)

        success = format_file(file_path, formatter)

        if success:
            # Optionally notify Claude about formatting
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": f"File auto-formatted with {formatter[0]}"
                }
            }))

        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(1)
    except Exception as e:
        print(f"Format hook error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
