#!/bin/bash
# Ralph Loop Skill Installer
# Usage: curl -fsSL https://gist.githubusercontent.com/AskTinNguyen/1b6109e01d3c2cb3d565e6b248c5f159/raw/install.sh | bash

set -euo pipefail

GIST_ID="1b6109e01d3c2cb3d565e6b248c5f159"
SKILL_DIR="${HOME}/.claude/skills/ralph-loop"

echo "Installing Ralph Loop skill..."

# Create directory structure
mkdir -p "$SKILL_DIR"/{lib,prompts,hooks,skills/commit,assets}

# Base URL for raw gist files
BASE_URL="https://gist.githubusercontent.com/AskTinNguyen/${GIST_ID}/raw"

# Download files
echo "Downloading files..."
curl -fsSL "$BASE_URL/SKILL.md" -o "$SKILL_DIR/SKILL.md"
curl -fsSL "$BASE_URL/ralph" -o "$SKILL_DIR/ralph"
curl -fsSL "$BASE_URL/loop.sh" -o "$SKILL_DIR/lib/loop.sh"
curl -fsSL "$BASE_URL/build.md" -o "$SKILL_DIR/prompts/build.md"
curl -fsSL "$BASE_URL/plan.md" -o "$SKILL_DIR/prompts/plan.md"
curl -fsSL "$BASE_URL/on-complete.sh" -o "$SKILL_DIR/hooks/on-complete.sh"
curl -fsSL "$BASE_URL/on-start.sh" -o "$SKILL_DIR/hooks/on-start.sh"
curl -fsSL "$BASE_URL/prd-template.md" -o "$SKILL_DIR/assets/prd-template.md"

# Handle commit SKILL.md (gist flattens paths, so filename might vary)
curl -fsSL "$BASE_URL/skills%2Fcommit%2FSKILL.md" -o "$SKILL_DIR/skills/commit/SKILL.md" 2>/dev/null || \
curl -fsSL "$BASE_URL/commit-SKILL.md" -o "$SKILL_DIR/skills/commit/SKILL.md" 2>/dev/null || \
echo "Note: commit skill not found, skipping"

# Make scripts executable
chmod +x "$SKILL_DIR/ralph"
chmod +x "$SKILL_DIR/hooks"/*.sh

echo ""
echo "✓ Installed to $SKILL_DIR"
echo ""
echo "Usage:"
echo "  # Copy to your project"
echo "  cp -r $SKILL_DIR/{ralph,lib,prompts,hooks} /path/to/project/"
echo ""
echo "  # Initialize and run"
echo "  cd /path/to/project"
echo "  ./ralph init"
echo "  # Create .ralph/prd.md with your stories"
echo "  ./ralph build 5"
echo ""
echo "Triggers in Claude Code: 'ralph loop', 'create prd', 'run prd'"
