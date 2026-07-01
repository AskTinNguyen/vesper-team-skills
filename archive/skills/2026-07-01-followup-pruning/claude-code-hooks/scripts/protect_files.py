#!/usr/bin/env python3
"""
Protect Sensitive Files Hook

PreToolUse hook that blocks edits to sensitive files like .env, credentials, keys, etc.

Usage in settings.json:
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/skills/claude-code-hooks/scripts/protect_files.py"
      }]
    }]
  }
}
"""

import json
import sys
import os

# File patterns to protect (case-insensitive matching)
PROTECTED_PATTERNS = [
    '.env',
    '.env.local',
    '.env.production',
    '.env.development',
    'credentials',
    'secrets',
    '.git/',
    '.ssh/',
    'id_rsa',
    'id_ed25519',
    '.pem',
    '.key',
    '.p12',
    '.pfx',
    'password',
    'token',
    'api_key',
    'apikey',
    'secret_key',
    'private_key',
    '.htpasswd',
    'shadow',
    'passwd',
    'known_hosts',
    'authorized_keys',
]

# Exact filenames to protect
PROTECTED_FILES = [
    '.env',
    '.env.local',
    '.env.production',
    '.env.development',
    '.env.staging',
    '.env.test',
    'credentials.json',
    'secrets.json',
    'service-account.json',
    'firebase-adminsdk.json',
    '.npmrc',
    '.pypirc',
    '.netrc',
]


def is_protected(file_path: str) -> tuple[bool, str]:
    """Check if file path matches protected patterns."""
    if not file_path:
        return False, ""

    # Normalize path
    normalized = file_path.lower()
    basename = os.path.basename(normalized)

    # Check exact filenames
    for protected in PROTECTED_FILES:
        if basename == protected.lower():
            return True, f"Protected file: {protected}"

    # Check patterns
    for pattern in PROTECTED_PATTERNS:
        if pattern.lower() in normalized:
            return True, f"Matches protected pattern: {pattern}"

    # Block path traversal attempts
    if '..' in file_path:
        return True, "Path traversal detected"

    return False, ""


def main():
    try:
        data = json.load(sys.stdin)
        tool_input = data.get('tool_input', {})
        file_path = tool_input.get('file_path', '')

        if not file_path:
            sys.exit(0)

        protected, reason = is_protected(file_path)

        if protected:
            print(f"BLOCKED: {reason}\nFile: {file_path}", file=sys.stderr)
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
