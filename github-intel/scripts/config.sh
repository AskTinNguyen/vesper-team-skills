#!/usr/bin/env bash
#
# config.sh - Configuration settings for the crawler
#
# This file contains customizable settings for discovery and exploration.
# Override these by setting environment variables before running scripts.
#

# Discovery settings
: "${MIN_STARS:=50}"                    # Minimum stars for repositories
: "${DAYS_AGO:=90}"                     # Look for repos updated within N days
: "${RATE_LIMIT_SLEEP:=2}"              # Seconds to sleep between API calls

# Keywords to search for (space-separated, override with CRAWLER_KEYWORDS)
DEFAULT_KEYWORDS=(
    "claude-code"
    "claude code cli"
    "codex cli"
    "openai codex"
    "ai coding assistant"
    "llm code generation"
    "claude anthropic cli"
    "ai pair programming"
)

# Use custom keywords if set, otherwise use defaults
if [[ -n "${CRAWLER_KEYWORDS:-}" ]]; then
    IFS=' ' read -ra KEYWORDS <<< "$CRAWLER_KEYWORDS"
else
    KEYWORDS=("${DEFAULT_KEYWORDS[@]}")
fi

# Directory settings
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TODOS_DIR="${PROJECT_ROOT}/todos/repos"
CLONES_DIR="${PROJECT_ROOT}/.clones"
