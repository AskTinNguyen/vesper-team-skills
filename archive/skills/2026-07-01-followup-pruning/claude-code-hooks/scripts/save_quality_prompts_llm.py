#!/usr/bin/env python3
"""
Save Quality Prompts (LLM-Enhanced)

Uses local Qwen 3 model via Ollama to intelligently evaluate prompt quality.
Runs asynchronously so it doesn't block the main Claude session.

Usage in settings.json:
{
  "hooks": {
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/skills/claude-code-hooks/scripts/save_quality_prompts_llm.py"
      }]
    }]
  }
}

Prompts saved to: ~/.claude/saved-prompts-llm.md

Requirements:
- Ollama running locally: `ollama serve`
- Qwen 3 model: `ollama pull qwen3:8b` (or your preferred size)
"""

import json
import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path

# Configuration
LOG_FILE = Path.home() / '.claude' / 'saved-prompts-llm.md'
MIN_LENGTH = 80  # Lower threshold since LLM will judge quality
OLLAMA_MODEL = "qwen25-tiny:latest"  # Fast small model for quick evaluation
OLLAMA_TIMEOUT = 15  # Seconds - keep short to not delay anything

# Simple prompts to skip (don't even send to LLM)
SKIP_PATTERNS = [
    "yes", "no", "ok", "okay", "sure", "thanks", "thank you",
    "great", "good", "perfect", "nice", "continue", "go ahead",
    "proceed", "do it", "y", "n", "hi", "hello", "hey"
]

EVALUATION_PROMPT = """Is this coding instruction prompt worth saving for future reference? Score 7+ means save=true.

PROMPT: {prompt}

Scoring guide:
- 8-10: Excellent - detailed requirements, clear structure, specific files/context
- 6-7: Good - clear intent, some structure or specifics
- 3-5: Basic - vague or simple request
- 1-2: Trivial - single word or unclear

Reply ONLY with JSON (no other text): {{"save": true, "score": 8, "reason": "detailed requirements", "category": "refactor"}}"""


def should_skip(prompt: str) -> bool:
    """Skip obviously simple prompts."""
    prompt_lower = prompt.lower().strip().rstrip('!.?')
    return prompt_lower in SKIP_PATTERNS or len(prompt) < MIN_LENGTH


def evaluate_with_llm(prompt: str) -> dict | None:
    """Use local Qwen model to evaluate prompt quality."""
    try:
        eval_prompt = EVALUATION_PROMPT.format(prompt=prompt[:2000])  # Limit length

        result = subprocess.run(
            ["ollama", "run", OLLAMA_MODEL, eval_prompt],
            capture_output=True,
            text=True,
            timeout=OLLAMA_TIMEOUT
        )

        if result.returncode != 0:
            return None

        # Parse JSON from response
        response = result.stdout.strip()

        # Handle /no_think tags if present (Qwen 3 thinking mode)
        if '/no_think' in response:
            response = response.split('/no_think')[-1].strip()

        # Find JSON in response
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])

        return None

    except subprocess.TimeoutExpired:
        return None
    except json.JSONDecodeError:
        return None
    except FileNotFoundError:
        # Ollama not installed
        return None
    except Exception:
        return None


def ensure_log_file():
    """Create log file with header if it doesn't exist."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not LOG_FILE.exists():
        with open(LOG_FILE, 'w') as f:
            f.write("# Saved Quality Prompts (LLM-Evaluated)\n\n")
            f.write("Prompts evaluated by local Qwen 3 model for quality.\n\n")
            f.write("---\n\n")


def save_prompt(prompt: str, evaluation: dict, cwd: str):
    """Save prompt to log file."""
    ensure_log_file()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    project = os.path.basename(cwd) if cwd else "unknown"
    score = evaluation.get('score', 0)
    reason = evaluation.get('reason', 'N/A')
    category = evaluation.get('category', 'other')

    entry = f"""
## {timestamp} | {project} | {category}

**LLM Score:** {score}/10 | **Reason:** {reason}

```
{prompt}
```

---
"""

    with open(LOG_FILE, 'a') as f:
        f.write(entry)


def process_prompt_sync(prompt: str, cwd: str):
    """Process prompt synchronously (called from subprocess)."""
    evaluation = evaluate_with_llm(prompt)

    if evaluation and evaluation.get('save', False):
        save_prompt(prompt, evaluation, cwd)


def main():
    try:
        # Check if we're being called as the background processor
        if len(sys.argv) > 1 and sys.argv[1] == '--process':
            # Background mode: read prompt from argv and process
            prompt = sys.argv[2] if len(sys.argv) > 2 else ''
            cwd = sys.argv[3] if len(sys.argv) > 3 else ''
            if prompt:
                process_prompt_sync(prompt, cwd)
            sys.exit(0)

        # Normal hook mode: read from stdin, spawn background process
        data = json.load(sys.stdin)
        user_prompt = data.get('user_prompt', '')
        cwd = data.get('cwd', '')

        # Exit immediately - don't block Claude
        if not user_prompt or should_skip(user_prompt):
            sys.exit(0)

        # Spawn a completely separate process to do LLM evaluation
        # This process will outlive the hook and not block anything
        script_path = Path(__file__).resolve()
        subprocess.Popen(
            [sys.executable, str(script_path), '--process', user_prompt, cwd],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True  # Fully detach from parent
        )

        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(0)
    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
