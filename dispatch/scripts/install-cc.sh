#!/bin/bash
#
# Install 'cc' and 'ccd' wrapper commands for Claude Code with task coordination
#

SKILL_DIR="$HOME/.claude/skills/dispatch"
CC_SCRIPT="$SKILL_DIR/scripts/cc"
CCD_SCRIPT="$SKILL_DIR/scripts/ccd"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "Installing Claude Code task coordination wrappers"
echo ""

# Check if scripts exist
if [ ! -f "$CC_SCRIPT" ]; then
  echo -e "${RED}Error:${NC} $CC_SCRIPT not found"
  exit 1
fi

# Make scripts executable
chmod +x "$CC_SCRIPT"
chmod +x "$CCD_SCRIPT" 2>/dev/null

# Try to find a good bin directory
BIN_DIRS=("/usr/local/bin" "$HOME/.local/bin" "$HOME/bin")
INSTALL_DIR=""

for dir in "${BIN_DIRS[@]}"; do
  if [ -d "$dir" ] && [ -w "$dir" ]; then
    INSTALL_DIR="$dir"
    break
  fi
done

# Create ~/.local/bin if no writable dir found
if [ -z "$INSTALL_DIR" ]; then
  mkdir -p "$HOME/.local/bin"
  INSTALL_DIR="$HOME/.local/bin"
fi

install_cmd() {
  local name=$1
  local script=$2
  local target="$INSTALL_DIR/$name"

  if [ -L "$target" ] && [ "$(readlink "$target")" = "$script" ]; then
    echo -e "${GREEN}✓${NC} $name already installed"
  elif [ -e "$target" ]; then
    echo -e "${YELLOW}!${NC} $target exists (skipped)"
  else
    ln -s "$script" "$target"
    echo -e "${GREEN}✓${NC} Installed $name to $INSTALL_DIR"
  fi
}

install_cmd "cc" "$CC_SCRIPT"
install_cmd "ccd" "$CCD_SCRIPT"

# Install the auto-archive Stop hook
HOOK_INSTALLER="$SKILL_DIR/hooks/install-hook.sh"
if [ -f "$HOOK_INSTALLER" ]; then
  echo ""
  echo "Installing auto-archive hook..."
  chmod +x "$HOOK_INSTALLER"
  "$HOOK_INSTALLER"
else
  echo -e "${YELLOW}!${NC} Hook installer not found at $HOOK_INSTALLER"
fi

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "Commands:"
echo "  cc                    Task coordination"
echo "  cc my-project         Use specific task list"
echo "  cc --list             Show task lists"
echo "  cc --dangerous        Skip permission prompts"
echo ""
echo "  ccd                   Same as 'cc --dangerous'"
echo "  ccd my-project        Task list + skip permissions"
echo ""

if ! echo "$PATH" | grep -q "$INSTALL_DIR"; then
  echo -e "${YELLOW}Note:${NC} Add to PATH if needed:"
  echo "  export PATH=\"$INSTALL_DIR:\$PATH\""
  echo ""
fi
