#!/usr/bin/env bash
set -euo pipefail

# verify-and-push.sh — Run checks, commit, push, optionally create PR
#
# Usage:
#   verify-and-push.sh --message "commit msg" [--branch NAME] [--no-pr] [--dry-run]
#
# Steps:
#   1. Detect project type and available checks
#   2. Run checks (lint, typecheck, tests)
#   3. Stage and commit changes
#   4. Push to remote
#   5. Create PR (unless --no-pr)
#
# Exit codes:
#   0 — Success
#   1 — Checks failed (nothing committed)
#   2 — Push failed
#   3 — PR creation failed

COMMIT_MSG=""
BRANCH=""
NO_PR=false
DRY_RUN=false
FILES_TO_STAGE=""

usage() {
  cat <<'EOF'
Usage: verify-and-push.sh [OPTIONS]

Run verification checks, then commit, push, and create a PR.

Options:
  --message MSG     Commit message (required unless --dry-run)
  --branch NAME     Branch name (default: current branch)
  --files FILES     Specific files to stage (default: all modified)
  --no-pr           Skip PR creation
  --dry-run         Run checks only, don't commit or push
  -h, --help        Show this help

Exit codes:
  0  Success
  1  Checks failed
  2  Push failed
  3  PR creation failed
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --message) COMMIT_MSG="$2"; shift 2 ;;
    --branch) BRANCH="$2"; shift 2 ;;
    --files) FILES_TO_STAGE="$2"; shift 2 ;;
    --no-pr) NO_PR=true; shift ;;
    --dry-run) DRY_RUN=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ "$DRY_RUN" == "false" && -z "$COMMIT_MSG" ]]; then
  echo "Error: --message is required (unless --dry-run)" >&2
  exit 1
fi

# Detect project type and available checks
detect_checks() {
  local checks=()

  # Node.js / TypeScript
  if [[ -f "package.json" ]]; then
    if grep -q '"lint"' package.json 2>/dev/null; then
      checks+=("npm run lint")
    fi
    if grep -q '"typecheck"' package.json 2>/dev/null; then
      checks+=("npm run typecheck")
    elif grep -q '"type-check"' package.json 2>/dev/null; then
      checks+=("npm run type-check")
    elif [[ -f "tsconfig.json" ]]; then
      checks+=("npx tsc --noEmit")
    fi
    if grep -q '"test"' package.json 2>/dev/null; then
      checks+=("npm test")
    fi
  fi

  # Python
  if [[ -f "pyproject.toml" || -f "setup.py" || -f "setup.cfg" ]]; then
    if command -v ruff &>/dev/null; then
      checks+=("ruff check .")
    elif command -v flake8 &>/dev/null; then
      checks+=("flake8 .")
    fi
    if command -v mypy &>/dev/null && [[ -f "mypy.ini" || -f "pyproject.toml" ]]; then
      checks+=("mypy .")
    fi
    if command -v pytest &>/dev/null; then
      checks+=("pytest --tb=short -q")
    fi
  fi

  # Go
  if [[ -f "go.mod" ]]; then
    checks+=("go vet ./...")
    checks+=("go test ./...")
  fi

  # Rust
  if [[ -f "Cargo.toml" ]]; then
    checks+=("cargo check")
    checks+=("cargo test")
  fi

  printf '%s\n' "${checks[@]}"
}

echo "=== Verify and Push ===" >&2

# Step 1: Detect checks
echo "Detecting project checks..." >&2
CHECKS=$(detect_checks)

if [[ -z "$CHECKS" ]]; then
  echo "No automated checks detected. Proceeding with manual verification only." >&2
else
  echo "Found checks:" >&2
  echo "$CHECKS" | sed 's/^/  /' >&2
fi

# Step 2: Run checks
CHECKS_PASSED=true
if [[ -n "$CHECKS" ]]; then
  echo "" >&2
  echo "Running checks..." >&2
  while IFS= read -r check; do
    echo "  Running: $check" >&2
    if eval "$check" >&2 2>&1; then
      echo "  PASS: $check" >&2
    else
      echo "  FAIL: $check" >&2
      CHECKS_PASSED=false
    fi
  done <<< "$CHECKS"
fi

if [[ "$CHECKS_PASSED" == "false" ]]; then
  echo "" >&2
  echo "Checks failed. No changes committed." >&2
  exit 1
fi

echo "" >&2
echo "All checks passed." >&2

if [[ "$DRY_RUN" == "true" ]]; then
  echo "Dry run — skipping commit, push, and PR." >&2
  exit 0
fi

# Step 3: Stage and commit
echo "" >&2
echo "Staging changes..." >&2

if [[ -n "$FILES_TO_STAGE" ]]; then
  git add $FILES_TO_STAGE
else
  # Stage all modified and untracked (excluding common noise)
  git add -A
  # Unstage sensitive files if accidentally added
  git reset HEAD -- '*.env' '*.env.*' 'credentials*' '*.pem' '*.key' 2>/dev/null || true
fi

# Check if there's anything to commit
if git diff --cached --quiet; then
  echo "Nothing to commit. Working tree is clean." >&2
  exit 0
fi

echo "Committing..." >&2
git commit -m "$COMMIT_MSG"

# Step 4: Push
CURRENT_BRANCH="${BRANCH:-$(git branch --show-current)}"
echo "Pushing branch '$CURRENT_BRANCH'..." >&2

if ! git push -u origin "$CURRENT_BRANCH" 2>&1; then
  echo "Push failed." >&2
  exit 2
fi

echo "Pushed successfully." >&2

# Step 5: Create PR
if [[ "$NO_PR" == "true" ]]; then
  echo "Skipping PR creation (--no-pr)." >&2
  exit 0
fi

# Check if PR already exists
EXISTING_PR=$(gh pr list --head "$CURRENT_BRANCH" --json number -q '.[0].number' 2>/dev/null || echo "")

if [[ -n "$EXISTING_PR" ]]; then
  echo "PR #$EXISTING_PR already exists for branch '$CURRENT_BRANCH'." >&2
  echo "{\"action\": \"existing_pr\", \"pr_number\": $EXISTING_PR, \"branch\": \"$CURRENT_BRANCH\"}"
  exit 0
fi

echo "Creating PR..." >&2
PR_URL=$(gh pr create --title "$COMMIT_MSG" --body "Automated PR created by verify-and-ship.

## Changes
$(git log origin/main..HEAD --oneline 2>/dev/null || echo 'See diff')

---
Created by \`verify-and-ship\` skill" --fill 2>&1) || {
  echo "PR creation failed." >&2
  exit 3
}

echo "PR created: $PR_URL" >&2
echo "{\"action\": \"created_pr\", \"url\": \"$PR_URL\", \"branch\": \"$CURRENT_BRANCH\"}"
