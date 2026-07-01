#!/usr/bin/env python3
"""
Save Quality Prompts Hook

UserPromptSubmit hook that automatically detects and saves high-quality prompts
to a log file for future reference.

Quality indicators:
- Length (detailed prompts)
- Structure (bullet points, numbered lists)
- Technical specificity (code, file paths, requirements)
- Instruction keywords (must, should, ensure, criteria)

Usage in settings.json:
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

Prompts saved to: ~/.claude/saved-prompts.md
"""

import json
import sys
import re
import os
from datetime import datetime
from pathlib import Path

# Configuration
LOG_FILE = Path.home() / '.claude' / 'saved-prompts.md'
MIN_LENGTH = 100  # Minimum characters to consider
MIN_SCORE = 3     # Minimum quality score to save

# Quality indicators and their weights
QUALITY_PATTERNS = {
    # Structure indicators (weight: 1 each)
    r'^\s*[-*]\s+': 1,           # Bullet points
    r'^\s*\d+\.\s+': 1,          # Numbered lists
    r'```': 1,                    # Code blocks
    r'\n\n': 0.5,                 # Paragraphs (multiple)

    # Instruction keywords (weight: 1 each)
    r'\bmust\b': 1,
    r'\bshould\b': 0.5,
    r'\bensure\b': 1,
    r'\brequire(ment|d|s)?\b': 1,
    r'\bcriteria\b': 1,
    r'\bconstraint': 1,
    r'\baccept(ance)?\b': 0.5,
    r'\bvalidat(e|ion)\b': 0.5,

    # Technical indicators (weight: 1 each)
    r'\.(py|js|ts|rb|go|rs|java|tsx|jsx)\b': 1,  # File extensions
    r'[A-Z][a-z]+[A-Z]': 0.5,    # CamelCase (class names)
    r'[a-z]+_[a-z]+': 0.5,       # snake_case
    r'def |function |class |const |let |var ': 1,  # Code keywords
    r'https?://': 0.5,            # URLs
    r'/[\w/]+\.': 0.5,            # File paths

    # Specificity indicators
    r'\bexample\b': 0.5,
    r'\bstep\s*\d': 1,            # "step 1", "step 2"
    r'\bfirst\b.*\bthen\b': 1,    # Sequential instructions
    r'\bif\b.*\bthen\b': 0.5,     # Conditional logic
    r'\bbefore\b.*\bafter\b': 0.5,
}

# Phrases that indicate a high-quality prompt (full match bonus)
QUALITY_PHRASES = [
    r'here\'?s (what|how|the)',
    r'i want you to',
    r'please (make sure|ensure|verify)',
    r'the (goal|objective|requirement) is',
    r'follow(ing)? (these|the) (steps|instructions|rules)',
    r'do not|don\'t|never|always',
    r'important:',
    r'note:',
    r'context:',
]

# Skip saving these types of prompts
SKIP_PATTERNS = [
    r'^(yes|no|ok|okay|sure|thanks|thank you|great|good|perfect|nice)[\s!.]*$',
    r'^(hi|hello|hey)[\s!.]*$',
    r'^\d+$',  # Just a number
    r'^[yn]$',  # Single y/n
    r'^(continue|go ahead|proceed|do it)[\s!.]*$',
]


def should_skip(prompt: str) -> bool:
    """Check if prompt should be skipped (too simple/short)."""
    prompt_lower = prompt.lower().strip()

    for pattern in SKIP_PATTERNS:
        if re.match(pattern, prompt_lower, re.IGNORECASE):
            return True

    return False


def calculate_quality_score(prompt: str) -> tuple[float, list[str]]:
    """
    Calculate quality score based on various indicators.
    Returns (score, list of matched indicators).
    """
    score = 0.0
    indicators = []

    # Length bonus
    length = len(prompt)
    if length >= 500:
        score += 2
        indicators.append(f"detailed ({length} chars)")
    elif length >= 200:
        score += 1
        indicators.append(f"substantial ({length} chars)")

    # Check quality patterns
    for pattern, weight in QUALITY_PATTERNS.items():
        matches = re.findall(pattern, prompt, re.MULTILINE | re.IGNORECASE)
        if matches:
            score += weight * min(len(matches), 3)  # Cap at 3 matches per pattern
            if weight >= 1:
                indicators.append(pattern.replace('\\b', '').replace('\\', ''))

    # Check quality phrases
    for pattern in QUALITY_PHRASES:
        if re.search(pattern, prompt, re.IGNORECASE):
            score += 1.5
            indicators.append(f"phrase: {pattern[:20]}...")

    # Line count bonus (structured content)
    lines = [l for l in prompt.split('\n') if l.strip()]
    if len(lines) >= 5:
        score += 1
        indicators.append(f"{len(lines)} lines")

    return score, indicators


def ensure_log_file():
    """Create log file with header if it doesn't exist."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not LOG_FILE.exists():
        with open(LOG_FILE, 'w') as f:
            f.write("# Saved Quality Prompts\n\n")
            f.write("Auto-saved prompts that scored high on quality indicators.\n\n")
            f.write("---\n\n")


def save_prompt(prompt: str, score: float, indicators: list[str], cwd: str):
    """Save prompt to log file."""
    ensure_log_file()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    date_header = datetime.now().strftime("%Y-%m-%d")
    project = os.path.basename(cwd) if cwd else "unknown"

    # Format indicators
    indicator_str = ", ".join(indicators[:5])  # Limit to 5

    entry = f"""
## {timestamp} | {project}

**Quality Score:** {score:.1f} | **Indicators:** {indicator_str}

```
{prompt}
```

---
"""

    with open(LOG_FILE, 'a') as f:
        f.write(entry)


def main():
    try:
        data = json.load(sys.stdin)
        user_prompt = data.get('user_prompt', '')
        cwd = data.get('cwd', '')

        if not user_prompt:
            sys.exit(0)

        # Skip simple prompts
        if should_skip(user_prompt):
            sys.exit(0)

        # Skip short prompts
        if len(user_prompt) < MIN_LENGTH:
            sys.exit(0)

        # Calculate quality
        score, indicators = calculate_quality_score(user_prompt)

        # Save if high quality
        if score >= MIN_SCORE:
            save_prompt(user_prompt, score, indicators, cwd)

            # Optionally notify (comment out if too noisy)
            # print(json.dumps({
            #     "hookSpecificOutput": {
            #         "hookEventName": "UserPromptSubmit",
            #         "additionalContext": f"[Prompt saved - score: {score:.1f}]"
            #     }
            # }))

        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(1)
    except Exception as e:
        # Don't block on errors, just log
        print(f"Save prompt hook error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
