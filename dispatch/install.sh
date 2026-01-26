#!/bin/bash
#
# Dispatch Skill Installer
#
# Usage:
#   curl -fsSL <url>/install.sh | bash
#   or
#   ./install.sh
#

set -e

SKILL_NAME="dispatch"
SKILL_DIR="$HOME/.claude/skills/$SKILL_NAME"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check for Bun
if ! command -v bun &> /dev/null; then
    echo "Error: Bun is required but not installed."
    echo "Install it from: https://bun.sh"
    echo "  curl -fsSL https://bun.sh/install | bash"
    exit 1
fi

# Create skills directory
mkdir -p "$HOME/.claude/skills"

# Check if installing from extracted tarball or cloned repo
if [ -f "$SCRIPT_DIR/SKILL.md" ]; then
    # Installing from source directory
    if [ "$SCRIPT_DIR" != "$SKILL_DIR" ]; then
        echo "Installing dispatch skill to $SKILL_DIR..."
        rm -rf "$SKILL_DIR"
        cp -r "$SCRIPT_DIR" "$SKILL_DIR"
    else
        echo "Skill already in correct location."
    fi
else
    echo "Error: SKILL.md not found. Run this script from the skill directory."
    exit 1
fi

# Make scripts executable
chmod +x "$SKILL_DIR/scripts/"*.ts 2>/dev/null || true

echo ""
echo "Dispatch skill installed successfully!"
echo ""
echo "Location: $SKILL_DIR"
echo ""
echo "Quick Start:"
echo "  1. Initialize multi-session coordination:"
echo "     eval \"\$(bun run $SKILL_DIR/scripts/init-session.ts)\""
echo ""
echo "  2. Use /dispatch in Claude Code to coordinate complex tasks"
echo ""
echo "Documentation: $SKILL_DIR/SKILL.md"
