#!/bin/bash
#
# setup.sh - One-command setup for Dispatch skill
#
# Usage: ./setup.sh
#
# This script sets up the Dispatch skill after installation or Team Skills sync.
# It installs:
#   - cc and ccd commands (Claude Code wrappers with task coordination)
#   - Auto-archive Stop hook (preserves tasks when sessions end)
#
# Safe to run multiple times (idempotent).
#

set -e

# Auto-detect script location (works from any install path)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              Dispatch Skill Setup                        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check for Bun runtime
if ! command -v bun &> /dev/null; then
  echo -e "${YELLOW}Warning:${NC} Bun runtime not found."
  echo "Some dispatch scripts require Bun. Install from: https://bun.sh"
  echo "  curl -fsSL https://bun.sh/install | bash"
  echo ""
fi

# Run the cc installer (which also installs the hook)
INSTALL_CC="$SCRIPT_DIR/scripts/install-cc.sh"

if [ -f "$INSTALL_CC" ]; then
  chmod +x "$INSTALL_CC"
  "$INSTALL_CC"
else
  echo -e "${YELLOW}Error:${NC} install-cc.sh not found at $INSTALL_CC"
  exit 1
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Setup Complete!                             ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "You can now use:"
echo ""
echo "  cc                    Start Claude with task coordination"
echo "  cc my-project         Use specific task list"
echo "  cc --new feature      Create new task list"
echo "  ccd                   Same as 'cc --dangerous'"
echo ""
echo "Tasks are auto-archived to ~/.claude/tasks-archive/ when sessions end."
echo ""
