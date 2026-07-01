#!/usr/bin/env python3
"""
Compound Docs Trigger Hook

UserPromptSubmit hook that detects "problem solved" phrases and adds context
to remind Claude to invoke the compound-docs skill.

Usage in settings.json:
{
  "hooks": {
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/skills/claude-code-hooks/scripts/compound_docs_trigger.py"
      }]
    }]
  }
}
"""

import json
import sys
import re

# Phrases that indicate a problem was solved
CONFIRMATION_PHRASES = [
    r'\bthat worked\b',
    r'\bit\'?s fixed\b',
    r'\bworking now\b',
    r'\bproblem solved\b',
    r'\bthat did it\b',
    r'\bfixed it\b',
    r'\bworks now\b',
    r'\ball good\b',
    r'\bperfect\b.*\bworks\b',
    r'\bnice\b.*\bfixed\b',
]


def detect_confirmation(prompt: str) -> bool:
    """Check if prompt contains confirmation phrases."""
    prompt_lower = prompt.lower()
    for pattern in CONFIRMATION_PHRASES:
        if re.search(pattern, prompt_lower):
            return True
    return False


def main():
    try:
        data = json.load(sys.stdin)
        user_prompt = data.get('user_prompt', '')

        if not user_prompt:
            sys.exit(0)

        if detect_confirmation(user_prompt):
            # Add context to remind Claude about compound-docs
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": (
                        "The user confirmed a problem was solved. "
                        "Consider using the compound-docs skill to document this solution "
                        "if it was non-trivial (multiple investigation attempts, "
                        "tricky debugging, non-obvious solution)."
                    )
                }
            }))

        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(1)
    except Exception as e:
        print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
