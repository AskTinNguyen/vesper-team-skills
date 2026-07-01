#!/usr/bin/env bash
# analyze-repo.sh — Initial reconnaissance script for repo-deep-dive skill
# Produces a structured overview of a repository's structure, file types, and config files.
#
# Usage: bash analyze-repo.sh <repo-path>
# Output: Structured text to stdout

set -euo pipefail

REPO_PATH="${1:-.}"

if [ ! -d "$REPO_PATH" ]; then
    echo "Error: Directory not found: $REPO_PATH"
    exit 1
fi

cd "$REPO_PATH"

REPO_NAME=$(basename "$(pwd)")

echo "============================================"
echo "REPO RECONNAISSANCE: $REPO_NAME"
echo "============================================"
echo ""

# --- Section 1: Basic Info ---
echo "## Basic Info"
echo ""

if [ -d ".git" ]; then
    echo "Git repo: Yes"
    REMOTE=$(git remote get-url origin 2>/dev/null || echo "No remote configured")
    echo "Remote: $REMOTE"
    BRANCH=$(git branch --show-current 2>/dev/null || echo "detached")
    echo "Current branch: $BRANCH"
    COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo "unknown")
    echo "Total commits: $COMMIT_COUNT"
    LAST_COMMIT=$(git log -1 --format="%ci" 2>/dev/null || echo "unknown")
    echo "Last commit: $LAST_COMMIT"
else
    echo "Git repo: No"
fi
echo ""

# --- Section 2: Directory Tree (depth 3, dirs only) ---
echo "## Directory Structure (depth 3)"
echo ""

if command -v tree &>/dev/null; then
    tree -d -L 3 --noreport -I "node_modules|.git|vendor|__pycache__|.next|dist|build|target|.cache|coverage|tmp" 2>/dev/null || find . -maxdepth 3 -type d -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/vendor/*' -not -path '*/__pycache__/*' | sort
else
    find . -maxdepth 3 -type d \
        -not -path '*/node_modules/*' \
        -not -path '*/.git/*' \
        -not -path '*/vendor/*' \
        -not -path '*/__pycache__/*' \
        -not -path '*/.next/*' \
        -not -path '*/dist/*' \
        -not -path '*/build/*' \
        -not -path '*/target/*' \
        -not -path '*/.cache/*' \
        -not -path '*/coverage/*' \
        -not -path '*/tmp/*' | sort | head -100
fi
echo ""

# --- Section 3: File Type Distribution ---
echo "## File Type Distribution"
echo ""

# Count files by extension (excluding common ignore dirs)
find . -type f \
    -not -path '*/node_modules/*' \
    -not -path '*/.git/*' \
    -not -path '*/vendor/*' \
    -not -path '*/__pycache__/*' \
    -not -path '*/.next/*' \
    -not -path '*/dist/*' \
    -not -path '*/build/*' \
    -not -path '*/target/*' \
    -not -path '*/.cache/*' \
    -not -path '*/coverage/*' | \
    sed -n 's/.*\.\([a-zA-Z0-9]*\)$/\1/p' | \
    sort | uniq -c | sort -rn | head -20

TOTAL_FILES=$(find . -type f \
    -not -path '*/node_modules/*' \
    -not -path '*/.git/*' \
    -not -path '*/vendor/*' \
    -not -path '*/__pycache__/*' \
    -not -path '*/.next/*' \
    -not -path '*/dist/*' \
    -not -path '*/build/*' \
    -not -path '*/target/*' | wc -l | tr -d ' ')
echo ""
echo "Total files (excluding deps/build): $TOTAL_FILES"
echo ""

# --- Section 4: Config File Inventory ---
echo "## Config Files Found"
echo ""

CONFIG_PATTERNS=(
    "package.json" "tsconfig.json" "jsconfig.json"
    "Gemfile" "Rakefile" "Cargo.toml" "go.mod" "go.sum"
    "pyproject.toml" "setup.py" "setup.cfg" "requirements.txt" "Pipfile"
    "pom.xml" "build.gradle" "build.gradle.kts"
    "Makefile" "Taskfile.yml" "justfile"
    "docker-compose.yml" "docker-compose.yaml" "Dockerfile"
    ".eslintrc*" ".prettierrc*" "rubocop.yml" ".rubocop.yml"
    "jest.config.*" "vitest.config.*" "pytest.ini" ".rspec"
    ".env.example" ".env.sample"
    "vercel.json" "netlify.toml" "fly.toml" "Procfile"
    ".github" ".circleci" "Jenkinsfile"
    "README.md" "README.rst" "CONTRIBUTING.md" "ARCHITECTURE.md" "CHANGELOG.md"
    "LICENSE" "LICENSE.md"
)

for pattern in "${CONFIG_PATTERNS[@]}"; do
    matches=$(find . -maxdepth 3 -name "$pattern" \
        -not -path '*/node_modules/*' \
        -not -path '*/.git/*' \
        -not -path '*/vendor/*' 2>/dev/null | head -5)
    if [ -n "$matches" ]; then
        echo "$matches"
    fi
done
echo ""

# --- Section 5: Entry Point Candidates ---
echo "## Entry Point Candidates"
echo ""

ENTRY_PATTERNS=(
    "src/index.ts" "src/index.js" "src/main.ts" "src/main.js"
    "src/app.ts" "src/app.js" "src/server.ts" "src/server.js"
    "index.ts" "index.js" "main.ts" "main.js"
    "app.rb" "config/routes.rb" "config/application.rb"
    "main.go" "cmd/*/main.go"
    "src/main.rs" "src/lib.rs"
    "manage.py" "app.py" "main.py" "wsgi.py" "asgi.py"
    "Program.cs" "Startup.cs"
    "mix.exs" "lib/*/application.ex"
)

for pattern in "${ENTRY_PATTERNS[@]}"; do
    matches=$(find . -path "./$pattern" \
        -not -path '*/node_modules/*' \
        -not -path '*/.git/*' 2>/dev/null | head -3)
    if [ -n "$matches" ]; then
        echo "$matches"
    fi
done
echo ""

# --- Section 6: LOC Estimate ---
echo "## Lines of Code Estimate"
echo ""

if command -v wc &>/dev/null; then
    # Count lines for common source extensions
    for ext in ts tsx js jsx rb py go rs java kt swift cs ex exs php; do
        count=$(find . -name "*.$ext" \
            -not -path '*/node_modules/*' \
            -not -path '*/.git/*' \
            -not -path '*/vendor/*' \
            -not -path '*/dist/*' \
            -not -path '*/build/*' \
            -not -path '*/target/*' \
            -exec cat {} + 2>/dev/null | wc -l | tr -d ' ')
        if [ "$count" -gt 0 ] 2>/dev/null; then
            printf "  %-6s %s lines\n" ".$ext" "$count"
        fi
    done
fi
echo ""

echo "============================================"
echo "Reconnaissance complete. Use these findings"
echo "to guide deeper analysis."
echo "============================================"
