#!/usr/bin/env bash
#
# run.sh - Main entry point for the crawler
#
# Commands:
#   ./crawler/run.sh discover  - Run discovery and generate TODOs
#   ./crawler/run.sh explore <repo-name>  - Clone and explore a specific repo
#   ./crawler/run.sh status    - Show discovery stats and pending TODOs
#
# Examples:
#   ./crawler/run.sh discover
#   ./crawler/run.sh explore anthropics-claude-code
#   ./crawler/run.sh status
#
# Configuration:
#   Set environment variables to customize behavior (see config.sh)
#   MIN_STARS=100 ./crawler/run.sh discover
#

set -euo pipefail

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/config.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[OK]${NC} $1"; }
print_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

# Show help text
show_help() {
    cat << 'EOF'
Crawler - Discover and explore AI coding repositories

USAGE:
    ./crawler/run.sh <command> [options]

COMMANDS:
    discover              Run discovery and generate TODOs
    explore <repo-name>   Clone and explore a specific repository
    status                Show discovery stats and pending TODOs
    help                  Show this help message

EXAMPLES:
    # Discover repositories matching keywords
    ./crawler/run.sh discover

    # Explore a specific repository
    ./crawler/run.sh explore anthropics-claude-code

    # Check current status
    ./crawler/run.sh status

    # Customize discovery settings
    MIN_STARS=100 DAYS_AGO=30 ./crawler/run.sh discover

CONFIGURATION:
    Environment variables (set before running):

    MIN_STARS         Minimum stars for repositories (default: 50)
    DAYS_AGO          Look for repos updated within N days (default: 90)
    RATE_LIMIT_SLEEP  Seconds between API calls (default: 2)
    CRAWLER_KEYWORDS  Space-separated custom keywords to search

    See crawler/config.sh for all settings.
EOF
}

# Discover command - run discovery and generate TODOs
cmd_discover() {
    print_info "Starting repository discovery..."
    print_info "Settings: MIN_STARS=${MIN_STARS}, DAYS_AGO=${DAYS_AGO}"

    # Check for gh cli
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI (gh) is required but not installed"
        print_info "Install with: brew install gh"
        exit 1
    fi

    # Check gh auth status
    if ! gh auth status &> /dev/null; then
        print_error "Not authenticated with GitHub CLI"
        print_info "Run: gh auth login"
        exit 1
    fi

    # Create temp file for results
    TEMP_FILE=$(mktemp)
    trap 'rm -f "$TEMP_FILE"' EXIT

    # Run discovery
    print_info "Searching with ${#KEYWORDS[@]} keywords..."
    "${SCRIPT_DIR}/discover.sh" > "$TEMP_FILE"

    # Count results
    REPO_COUNT=$(jq 'length' "$TEMP_FILE")

    if [[ "$REPO_COUNT" -eq 0 ]]; then
        print_warn "No repositories found matching criteria"
        exit 0
    fi

    print_success "Found $REPO_COUNT unique repositories"

    # Generate TODOs
    print_info "Generating TODO files..."
    "${SCRIPT_DIR}/generate-todos.sh" "$TEMP_FILE"

    print_success "Discovery complete!"
    print_info "Run './crawler/run.sh status' to see pending TODOs"
}

# Explore command - clone and explore a specific repository
cmd_explore() {
    local repo_name="$1"

    if [[ -z "$repo_name" ]]; then
        print_error "Repository name required"
        echo "Usage: ./crawler/run.sh explore <repo-name>"
        exit 1
    fi

    # Find the TODO file
    local todo_file="${TODOS_DIR}/${repo_name}.md"

    if [[ ! -f "$todo_file" ]]; then
        print_error "TODO file not found: $todo_file"
        print_info "Available repositories:"
        if [[ -d "$TODOS_DIR" ]]; then
            ls -1 "$TODOS_DIR"/*.md 2>/dev/null | xargs -I{} basename {} .md | head -10
            local count
            count=$(ls -1 "$TODOS_DIR"/*.md 2>/dev/null | wc -l | tr -d ' ')
            if [[ "$count" -gt 10 ]]; then
                print_info "... and $((count - 10)) more"
            fi
        else
            print_warn "No TODOs directory found. Run 'discover' first."
        fi
        exit 1
    fi

    # Extract URL from TODO file
    local repo_url
    repo_url=$(grep -oP '(?<=\*\*URL:\*\* ).*' "$todo_file" 2>/dev/null || \
               grep '^\*\*URL:\*\*' "$todo_file" | sed 's/\*\*URL:\*\* //')

    if [[ -z "$repo_url" ]]; then
        print_error "Could not extract repository URL from TODO file"
        exit 1
    fi

    print_info "Repository: $repo_name"
    print_info "URL: $repo_url"

    # Create clones directory
    mkdir -p "$CLONES_DIR"

    local clone_path="${CLONES_DIR}/${repo_name}"

    if [[ -d "$clone_path" ]]; then
        print_info "Repository already cloned at: $clone_path"
        print_info "Updating..."
        (cd "$clone_path" && git pull --quiet)
    else
        print_info "Cloning repository..."
        git clone --depth 1 "$repo_url" "$clone_path"
    fi

    print_success "Repository ready at: $clone_path"

    # Show exploration prompt
    local explore_prompt="${SCRIPT_DIR}/prompts/explore.md"
    if [[ -f "$explore_prompt" ]]; then
        print_info "Exploration prompt available at: $explore_prompt"
    fi

    print_info ""
    print_info "Next steps:"
    print_info "  cd $clone_path"
    print_info "  # Explore the codebase"
    print_info "  # Use the review and compound prompts from crawler/prompts/"
}

# Status command - show discovery stats and pending TODOs
cmd_status() {
    print_info "Crawler Status"
    echo ""

    # Check if TODOs directory exists
    if [[ ! -d "$TODOS_DIR" ]]; then
        print_warn "No TODOs directory found"
        print_info "Run './crawler/run.sh discover' to get started"
        exit 0
    fi

    # Count TODO files (excluding INDEX.md)
    local total_todos
    total_todos=$(find "$TODOS_DIR" -name "*.md" ! -name "INDEX.md" 2>/dev/null | wc -l | tr -d ' ')

    if [[ "$total_todos" -eq 0 ]]; then
        print_warn "No repository TODOs found"
        print_info "Run './crawler/run.sh discover' to find repositories"
        exit 0
    fi

    echo "Repositories discovered: $total_todos"
    echo ""

    # Count completed vs pending
    local completed=0
    local pending=0

    for file in "$TODOS_DIR"/*.md; do
        [[ "$(basename "$file")" == "INDEX.md" ]] && continue
        [[ ! -f "$file" ]] && continue

        # Check if all tasks are complete (all checkboxes marked)
        if grep -q '\- \[ \]' "$file" 2>/dev/null; then
            ((pending++))
        else
            ((completed++))
        fi
    done

    echo "Pending exploration: $pending"
    echo "Completed: $completed"
    echo ""

    # Show top pending repositories (sorted by stars from INDEX)
    if [[ "$pending" -gt 0 ]]; then
        echo "Top pending repositories:"
        echo "------------------------"

        # Read from INDEX if available
        if [[ -f "$INDEX_FILE" ]]; then
            # Parse the markdown table, skip header rows, show top 10
            tail -n +6 "$INDEX_FILE" | head -10 | while read -r line; do
                # Extract repo name and stars from table row
                if [[ "$line" =~ ^\|.*\| ]]; then
                    repo_name=$(echo "$line" | awk -F'|' '{print $2}' | sed 's/\[//;s/\].*//' | xargs)
                    stars=$(echo "$line" | awk -F'|' '{print $3}' | xargs)
                    echo "  $repo_name ($stars stars)"
                fi
            done
        else
            # Fallback: list files
            ls -1 "$TODOS_DIR"/*.md 2>/dev/null | head -10 | while read -r file; do
                [[ "$(basename "$file")" == "INDEX.md" ]] && continue
                echo "  $(basename "$file" .md)"
            done
        fi
    fi

    echo ""
    print_info "Use './crawler/run.sh explore <repo-name>' to explore a repository"
}

# Main entry point
main() {
    local command="${1:-help}"

    case "$command" in
        discover)
            cmd_discover
            ;;
        explore)
            cmd_explore "${2:-}"
            ;;
        status)
            cmd_status
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
