#!/usr/bin/env bash
#
# discover.sh - Discover repositories related to Claude Code and Codex
#
# Uses GitHub API via gh cli to search for repositories matching
# keywords related to Claude Code and Codex CLI tools.
#

set -euo pipefail

# Configuration
MIN_STARS=50
DAYS_AGO=90
RATE_LIMIT_SLEEP=2

# Keywords to search for
KEYWORDS=(
    "claude-code"
    "claude code cli"
    "codex cli"
    "openai codex"
    "ai coding assistant"
    "llm code generation"
    "claude anthropic cli"
    "ai pair programming"
)

# Calculate date 90 days ago
if [[ "$(uname)" == "Darwin" ]]; then
    DATE_CUTOFF=$(date -v-${DAYS_AGO}d +%Y-%m-%d)
else
    DATE_CUTOFF=$(date -d "${DAYS_AGO} days ago" +%Y-%m-%d)
fi

# Temporary file to store all results
TEMP_FILE=$(mktemp)
trap 'rm -f "$TEMP_FILE"' EXIT

# Function to search repositories for a keyword
search_repos() {
    local keyword="$1"
    local query="$keyword in:name,description,readme stars:>=${MIN_STARS} pushed:>=${DATE_CUTOFF}"

    # Search and extract relevant fields, sorted by stars
    gh api -X GET search/repositories \
        -f q="$query" \
        -f sort=stars \
        -f order=desc \
        -f per_page=100 \
        --jq '.items[] | {
            name: .full_name,
            url: .html_url,
            description: (.description // ""),
            stars: .stargazers_count,
            language: (.language // ""),
            topics: (.topics // [])
        }' 2>/dev/null || true
}

# Search all keywords and collect results
for keyword in "${KEYWORDS[@]}"; do
    search_repos "$keyword" >> "$TEMP_FILE"
    sleep "$RATE_LIMIT_SLEEP"
done

# Deduplicate by repository name and output as JSON array
jq -s 'unique_by(.name) | sort_by(-(.stars // 0))' "$TEMP_FILE"
