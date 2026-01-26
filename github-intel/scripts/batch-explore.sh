#!/usr/bin/env bash
#
# batch-explore.sh - Batch clone and prepare repos for exploration
#
# Usage:
#   ./batch-explore.sh <repo-list-file>
#   ./batch-explore.sh --top N
#
# Examples:
#   ./batch-explore.sh repos.txt
#   ./batch-explore.sh --top 10
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
CLONES_DIR="${PROJECT_ROOT}/.clones"
TODOS_DIR="${PROJECT_ROOT}/todos/repos"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[OK]${NC} $1"; }
print_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

show_help() {
    cat << 'EOF'
batch-explore.sh - Batch clone repositories for exploration

USAGE:
    ./batch-explore.sh <repo-list-file>    Clone repos listed in file
    ./batch-explore.sh --top N             Clone top N repos from INDEX.md

OPTIONS:
    --top N         Clone top N repos by star count
    --category CAT  Filter by category (claude, codex, mcp, agent)
    --parallel N    Clone N repos in parallel (default: 3)
    --help          Show this help

EXAMPLES:
    # Clone top 10 repos
    ./batch-explore.sh --top 10

    # Clone repos from a list
    echo "anthropics-claude-code" > repos.txt
    echo "openai-codex" >> repos.txt
    ./batch-explore.sh repos.txt

    # Clone Claude-related repos
    ./batch-explore.sh --top 20 --category claude

EOF
}

clone_repo() {
    local repo_name="$1"
    local todo_file="${TODOS_DIR}/${repo_name}.md"
    local clone_path="${CLONES_DIR}/${repo_name}"

    if [[ ! -f "$todo_file" ]]; then
        print_warn "TODO not found: $repo_name"
        return 1
    fi

    # Extract URL from TODO
    local repo_url
    repo_url=$(grep '^\*\*URL:\*\*' "$todo_file" | sed 's/\*\*URL:\*\* //')

    if [[ -z "$repo_url" ]]; then
        print_warn "No URL found for: $repo_name"
        return 1
    fi

    if [[ -d "$clone_path" ]]; then
        print_info "Already cloned: $repo_name"
        return 0
    fi

    print_info "Cloning: $repo_name"
    git clone --depth 1 "$repo_url" "$clone_path" 2>/dev/null || {
        print_warn "Failed to clone: $repo_name"
        return 1
    }
    print_success "Cloned: $repo_name"
}

get_top_repos() {
    local count="${1:-10}"
    local category="${2:-}"

    local filter_cmd="cat"
    if [[ -n "$category" ]]; then
        filter_cmd="grep -i $category"
    fi

    tail -n +6 "${TODOS_DIR}/INDEX.md" | \
        $filter_cmd | \
        head -n "$count" | \
        sed 's/.*\[\([^]]*\)\].*/\1/' | \
        tr '/' '-'
}

main() {
    local mode=""
    local count=10
    local category=""
    local parallel=3
    local repos=()

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --top)
                mode="top"
                count="${2:-10}"
                shift 2
                ;;
            --category)
                category="$2"
                shift 2
                ;;
            --parallel)
                parallel="$2"
                shift 2
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                if [[ -f "$1" ]]; then
                    mode="file"
                    mapfile -t repos < "$1"
                else
                    repos+=("$1")
                fi
                shift
                ;;
        esac
    done

    mkdir -p "$CLONES_DIR"

    if [[ "$mode" == "top" ]]; then
        print_info "Getting top $count repos${category:+ (filtered: $category)}"
        mapfile -t repos < <(get_top_repos "$count" "$category")
    fi

    if [[ ${#repos[@]} -eq 0 ]]; then
        show_help
        exit 1
    fi

    print_info "Cloning ${#repos[@]} repositories..."

    local success=0
    local failed=0

    for repo in "${repos[@]}"; do
        [[ -z "$repo" ]] && continue
        if clone_repo "$repo"; then
            ((success++))
        else
            ((failed++))
        fi
    done

    echo ""
    print_success "Batch complete: $success cloned, $failed failed"
    print_info "Repos ready at: $CLONES_DIR"
}

main "$@"
