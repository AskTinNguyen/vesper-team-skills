#!/usr/bin/env bash
#
# generate-todos.sh - Generate TODO files from crawler discoveries
#
# Reads crawler output JSON and generates markdown TODOs in todos/repos/
# directory for each discovered repository.
#

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TODOS_DIR="${PROJECT_ROOT}/todos/repos"
INDEX_FILE="${TODOS_DIR}/INDEX.md"

# Read JSON from stdin or file argument
if [[ $# -gt 0 && -f "$1" ]]; then
    INPUT_JSON=$(cat "$1")
else
    INPUT_JSON=$(cat)
fi

# Validate JSON input
if ! echo "$INPUT_JSON" | jq -e '.' >/dev/null 2>&1; then
    echo "Error: Invalid JSON input" >&2
    exit 1
fi

# Create todos directory
mkdir -p "$TODOS_DIR"

# Get count of repositories
REPO_COUNT=$(echo "$INPUT_JSON" | jq 'length')

if [[ "$REPO_COUNT" -eq 0 ]]; then
    echo "No repositories found in input"
    exit 0
fi

echo "Generating TODOs for $REPO_COUNT repositories..."

# Generate individual TODO files
echo "$INPUT_JSON" | jq -c '.[]' | while read -r repo; do
    # Extract fields
    full_name=$(echo "$repo" | jq -r '.name')
    repo_name=$(echo "$full_name" | tr '/' '-')
    url=$(echo "$repo" | jq -r '.url')
    stars=$(echo "$repo" | jq -r '.stars')
    language=$(echo "$repo" | jq -r '.language // "Unknown"')
    description=$(echo "$repo" | jq -r '.description // "No description"')

    # Generate TODO file
    todo_file="${TODOS_DIR}/${repo_name}.md"

    cat > "$todo_file" << EOF
# Explore: ${full_name}

**URL:** ${url}
**Stars:** ${stars}
**Language:** ${language}
**Description:** ${description}

## Exploration Tasks
- [ ] Clone and explore codebase structure
- [ ] Run code review skill on key files
- [ ] Extract architecture patterns
- [ ] Document valuable logic with compound-docs
- [ ] Identify reusable frameworks/utilities
EOF

    echo "  Created: ${repo_name}.md"
done

# Generate index file sorted by stars
echo "Generating INDEX.md..."

{
    echo "# Repository Exploration Index"
    echo ""
    echo "Repositories discovered for exploration, sorted by stars."
    echo ""
    echo "| Repository | Stars | Language | Description |"
    echo "|------------|-------|----------|-------------|"

    echo "$INPUT_JSON" | jq -r '.[] | "| [\(.name)](\(.url)) | \(.stars) | \(.language // "N/A") | \(.description // "No description" | gsub("[\\n\\r]"; " ") | .[0:80]) |"'
} > "$INDEX_FILE"

echo "Generated INDEX.md with $REPO_COUNT repositories"
echo "Done! TODO files created in: $TODOS_DIR"
