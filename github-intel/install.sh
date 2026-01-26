#!/usr/bin/env bash
#
# install.sh - Install GitHub Intelligence Skill globally
#
# Usage:
#   ./install.sh [--path PATH]
#
# Options:
#   --path PATH   Custom installation path (default: ~/.claude/skills)
#

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[OK]${NC} $1"; }
print_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_PATH="${HOME}/.claude/skills"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --path)
            INSTALL_PATH="$2"
            shift 2
            ;;
        --help|-h)
            cat << 'EOF'
GitHub Intelligence Skill - Installer

USAGE:
    ./install.sh [OPTIONS]

OPTIONS:
    --path PATH     Custom installation path
                    Default: ~/.claude/skills
    --help, -h      Show this help

EXAMPLES:
    # Install to default location
    ./install.sh

    # Install to custom path
    ./install.sh --path ~/my-skills

AFTER INSTALLATION:
    # Verify installation
    claude --list-skills | grep github-intel

    # Run discovery
    ~/.claude/skills/github-intel/scripts/run.sh discover
EOF
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

print_info "Installing GitHub Intelligence Skill..."
print_info "Target: $INSTALL_PATH"

# Check prerequisites
print_info "Checking prerequisites..."

if ! command -v gh &> /dev/null; then
    print_warn "GitHub CLI (gh) not found"
    print_info "Install with: brew install gh (macOS) or apt install gh (Linux)"
    print_info "See: https://cli.github.com/"
fi

if ! command -v jq &> /dev/null; then
    print_warn "jq not found"
    print_info "Install with: brew install jq (macOS) or apt install jq (Linux)"
fi

if ! command -v qmd &> /dev/null; then
    print_warn "qmd not found (optional for semantic search)"
    print_info "Install with: npm install -g qmd"
fi

# Create installation directory
mkdir -p "$INSTALL_PATH"

# Install skill
TARGET_DIR="${INSTALL_PATH}/github-intel"

if [[ -d "$TARGET_DIR" ]]; then
    print_warn "Skill already exists at $TARGET_DIR"
    read -p "Overwrite? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Installation cancelled"
        exit 0
    fi
    rm -rf "$TARGET_DIR"
fi

print_info "Copying skill files..."
cp -r "$SCRIPT_DIR" "$TARGET_DIR"

# Make scripts executable
chmod +x "$TARGET_DIR"/scripts/*.sh

# Create symlink for easy access (optional)
if [[ -d "$HOME/.local/bin" ]]; then
    ln -sf "$TARGET_DIR/scripts/run.sh" "$HOME/.local/bin/github-intel" 2>/dev/null || true
fi

print_success "Installation complete!"
echo ""
print_info "Installation directory: $TARGET_DIR"
echo ""
print_info "Next steps:"
echo "  1. Authenticate with GitHub: gh auth login"
echo "  2. Test discovery: $TARGET_DIR/scripts/run.sh discover"
echo "  3. Check status: $TARGET_DIR/scripts/run.sh status"
echo ""
print_info "Usage in Claude Code:"
echo '  > "discover trending Claude Code repos"'
echo '  > "research AI coding tools on GitHub"'
echo ""
print_success "Ready to use!"
