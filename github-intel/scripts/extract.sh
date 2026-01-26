#!/usr/bin/env bash
#
# extract.sh - Move insights from TODO exploration to knowledge store
#
# This script helps extract and organize knowledge from explored repositories
# into the appropriate knowledge store categories.
#
# Usage:
#   ./crawler/extract.sh <type> <name> [source-url]
#   ./crawler/extract.sh list
#   ./crawler/extract.sh update-index
#
# Types: architecture, patterns, utilities, frameworks

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
KNOWLEDGE_DIR="${PROJECT_ROOT}/knowledge"
INDEX_FILE="${KNOWLEDGE_DIR}/INDEX.md"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Valid knowledge types
VALID_TYPES=("architecture" "patterns" "utilities" "frameworks")

show_help() {
    cat << 'EOF'
Knowledge Store Extraction Tool

Usage:
  extract.sh <command> [options]

Commands:
  create <type> <name> [source-url]   Create a new knowledge entry from template
  list [type]                         List all knowledge entries (optionally by type)
  update-index                        Regenerate the INDEX.md file
  help                                Show this help message

Types:
  architecture   System designs and architectural patterns
  patterns       Reusable design patterns and coding techniques
  utilities      Standalone utility functions and helpers
  frameworks     Framework concepts and implementations

Examples:
  # Create a new architecture entry
  extract.sh create architecture agent-loop https://github.com/user/repo

  # Create a new pattern entry
  extract.sh create patterns retry-with-backoff https://github.com/user/repo

  # List all knowledge entries
  extract.sh list

  # List only utilities
  extract.sh list utilities

  # Update the master index
  extract.sh update-index
EOF
}

# Validate knowledge type
validate_type() {
    local type="$1"
    for valid in "${VALID_TYPES[@]}"; do
        if [[ "$type" == "$valid" ]]; then
            return 0
        fi
    done
    return 1
}

# Create a new knowledge entry
create_entry() {
    local type="$1"
    local name="$2"
    local source_url="${3:-}"

    if ! validate_type "$type"; then
        echo -e "${RED}Error: Invalid type '$type'${NC}" >&2
        echo "Valid types: ${VALID_TYPES[*]}" >&2
        exit 1
    fi

    # Sanitize name for filename
    local filename=$(echo "$name" | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]//g')
    local filepath="${KNOWLEDGE_DIR}/${type}/${filename}.md"

    if [[ -f "$filepath" ]]; then
        echo -e "${YELLOW}Warning: Entry already exists at ${filepath}${NC}"
        read -p "Overwrite? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Aborted."
            exit 0
        fi
    fi

    # Get today's date
    local today=$(date +%Y-%m-%d)

    # Read template and substitute placeholders
    local template="${KNOWLEDGE_DIR}/${type}/TEMPLATE.md"
    if [[ ! -f "$template" ]]; then
        echo -e "${RED}Error: Template not found at ${template}${NC}" >&2
        exit 1
    fi

    # Create entry from template with basic substitutions
    sed -e "s|{Name}|${name}|g" \
        -e "s|{repository-url}|${source_url:-TBD}|g" \
        -e "s|{date}|${today}|g" \
        "$template" > "$filepath"

    echo -e "${GREEN}Created knowledge entry: ${filepath}${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Edit the file to add your extracted knowledge"
    echo "  2. Run 'extract.sh update-index' to update the master index"
}

# List knowledge entries
list_entries() {
    local filter_type="${1:-}"

    echo -e "${BLUE}Knowledge Store Contents${NC}"
    echo "========================"
    echo ""

    local total=0

    for type in "${VALID_TYPES[@]}"; do
        if [[ -n "$filter_type" && "$filter_type" != "$type" ]]; then
            continue
        fi

        local type_dir="${KNOWLEDGE_DIR}/${type}"
        local count=0

        echo -e "${YELLOW}${type^}:${NC}"

        if [[ -d "$type_dir" ]]; then
            while IFS= read -r -d '' file; do
                local basename=$(basename "$file" .md)
                if [[ "$basename" != "TEMPLATE" ]]; then
                    echo "  - $basename"
                    ((count++))
                    ((total++))
                fi
            done < <(find "$type_dir" -maxdepth 1 -name "*.md" -print0 2>/dev/null | sort -z)
        fi

        if [[ $count -eq 0 ]]; then
            echo "  (no entries)"
        fi
        echo ""
    done

    echo "Total entries: $total"
}

# Update the master index
update_index() {
    echo "Updating knowledge index..."

    local arch_count=0
    local pattern_count=0
    local util_count=0
    local framework_count=0

    # Count entries (excluding templates)
    for type in "${VALID_TYPES[@]}"; do
        local type_dir="${KNOWLEDGE_DIR}/${type}"
        if [[ -d "$type_dir" ]]; then
            local count=$(find "$type_dir" -maxdepth 1 -name "*.md" ! -name "TEMPLATE.md" 2>/dev/null | wc -l | tr -d ' ')
            case "$type" in
                architecture) arch_count=$count ;;
                patterns) pattern_count=$count ;;
                utilities) util_count=$count ;;
                frameworks) framework_count=$count ;;
            esac
        fi
    done

    local total=$((arch_count + pattern_count + util_count + framework_count))

    # Generate index file
    {
        cat << EOF
# Knowledge Store Index

Master index of all extracted knowledge from explored repositories.

## Statistics

- **Total Entries:** ${total}
- **Architecture:** ${arch_count}
- **Patterns:** ${pattern_count}
- **Utilities:** ${util_count}
- **Frameworks:** ${framework_count}

---

EOF

        # Generate section for each type
        for type in "${VALID_TYPES[@]}"; do
            local type_dir="${KNOWLEDGE_DIR}/${type}"
            local type_title="${type^}"

            echo "## ${type_title}"
            echo ""

            case "$type" in
                architecture) echo "Extracted system designs and architectural patterns." ;;
                patterns) echo "Reusable design patterns and coding techniques." ;;
                utilities) echo "Standalone utility functions and helpers." ;;
                frameworks) echo "Extracted framework concepts and implementations." ;;
            esac

            echo ""
            echo "| Name | Source | Tags | Date |"
            echo "|------|--------|------|------|"

            local has_entries=false

            if [[ -d "$type_dir" ]]; then
                while IFS= read -r -d '' file; do
                    local basename=$(basename "$file" .md)
                    if [[ "$basename" != "TEMPLATE" ]]; then
                        has_entries=true

                        # Extract metadata from file
                        local name=$(head -1 "$file" | sed 's/^# [^:]*: //')
                        local source=$(grep -m1 "^\*\*Source:\*\*" "$file" | sed 's/\*\*Source:\*\* //' || echo "N/A")
                        local tags=$(grep -m1 "^\*\*Tags:\*\*" "$file" | sed 's/\*\*Tags:\*\* //' || echo "")
                        local date=$(grep -m1 "^\*\*Extracted:\*\*" "$file" | sed 's/\*\*Extracted:\*\* //' || echo "")

                        echo "| [${name}](${type}/${basename}.md) | ${source} | ${tags} | ${date} |"
                    fi
                done < <(find "$type_dir" -maxdepth 1 -name "*.md" -print0 2>/dev/null | sort -z)
            fi

            if [[ "$has_entries" == "false" ]]; then
                echo "| *No entries yet* | | | |"
            fi

            echo ""
            echo "---"
            echo ""
        done

        echo "## Recently Added"
        echo ""

        # Find recently added entries (last 7 days)
        local recent_entries=()
        for type in "${VALID_TYPES[@]}"; do
            local type_dir="${KNOWLEDGE_DIR}/${type}"
            if [[ -d "$type_dir" ]]; then
                while IFS= read -r file; do
                    if [[ -n "$file" ]]; then
                        local basename=$(basename "$file" .md)
                        if [[ "$basename" != "TEMPLATE" ]]; then
                            recent_entries+=("${type}/${basename}.md")
                        fi
                    fi
                done < <(find "$type_dir" -maxdepth 1 -name "*.md" ! -name "TEMPLATE.md" -mtime -7 2>/dev/null)
            fi
        done

        if [[ ${#recent_entries[@]} -eq 0 ]]; then
            echo "*No entries yet*"
        else
            for entry in "${recent_entries[@]}"; do
                echo "- [${entry}](${entry})"
            done
        fi

        echo ""
        echo "---"
        echo ""
        echo "## By Source Repository"
        echo ""

        # Group by source repository
        local sources=()
        for type in "${VALID_TYPES[@]}"; do
            local type_dir="${KNOWLEDGE_DIR}/${type}"
            if [[ -d "$type_dir" ]]; then
                while IFS= read -r -d '' file; do
                    local basename=$(basename "$file" .md)
                    if [[ "$basename" != "TEMPLATE" ]]; then
                        local source=$(grep -m1 "^\*\*Source:\*\*" "$file" | sed 's/\*\*Source:\*\* //' || echo "")
                        if [[ -n "$source" && "$source" != "TBD" && "$source" != "{repository-url}" ]]; then
                            sources+=("$source")
                        fi
                    fi
                done < <(find "$type_dir" -maxdepth 1 -name "*.md" -print0 2>/dev/null)
            fi
        done

        if [[ ${#sources[@]} -eq 0 ]]; then
            echo "*No repositories indexed yet*"
        else
            # Get unique sources
            printf '%s\n' "${sources[@]}" | sort -u | while read -r source; do
                echo "- ${source}"
            done
        fi

    } > "$INDEX_FILE"

    echo -e "${GREEN}Updated: ${INDEX_FILE}${NC}"
    echo "Total entries: $total"
}

# Main command handler
main() {
    if [[ $# -eq 0 ]]; then
        show_help
        exit 0
    fi

    local command="$1"
    shift

    case "$command" in
        create)
            if [[ $# -lt 2 ]]; then
                echo -e "${RED}Error: 'create' requires type and name${NC}" >&2
                echo "Usage: extract.sh create <type> <name> [source-url]" >&2
                exit 1
            fi
            create_entry "$@"
            ;;
        list)
            list_entries "${1:-}"
            ;;
        update-index)
            update_index
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}Error: Unknown command '$command'${NC}" >&2
            show_help
            exit 1
            ;;
    esac
}

main "$@"
