#!/bin/bash
#
# install-hook.sh - Install the auto-archive SessionEnd hook
#
# Usage: ./install-hook.sh
#
# This adds the SessionEnd hook to ~/.claude/settings.json for automatic
# task archival when sessions end.
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SETTINGS_FILE="$HOME/.claude/settings.json"
HOOK_SCRIPT="$SCRIPT_DIR/auto-archive.sh"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${BLUE}Installing auto-archive SessionEnd hook...${NC}"
echo ""

# Check if hook script exists
if [ ! -f "$HOOK_SCRIPT" ]; then
  echo -e "${YELLOW}Warning: Hook script not found at $HOOK_SCRIPT${NC}"
  echo "Creating it now..."
  mkdir -p "$(dirname "$HOOK_SCRIPT")"
fi

# Make hook executable
chmod +x "$HOOK_SCRIPT" 2>/dev/null
mkdir -p "$(dirname "$SETTINGS_FILE")"

# Check if settings file exists
if [ ! -f "$SETTINGS_FILE" ]; then
  echo "Creating settings.json..."
  cat > "$SETTINGS_FILE" << EOF
{
  "hooks": {
    "SessionEnd": [{
      "hooks": [{
        "type": "command",
        "command": "$HOOK_SCRIPT",
        "async": true,
        "timeout": 30
      }]
    }]
  }
}
EOF
  echo -e "${GREEN}✓${NC} Created settings.json with SessionEnd hook"
  exit 0
fi

# Check if SessionEnd hook already exists
if grep -q '"SessionEnd"' "$SETTINGS_FILE" 2>/dev/null; then
  if grep -q 'auto-archive.sh' "$SETTINGS_FILE" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Auto-archive hook already installed"
    exit 0
  else
    echo -e "${YELLOW}!${NC} SessionEnd hook exists but doesn't include auto-archive"
    echo ""
    echo "Add this to your SessionEnd hooks manually:"
    echo ""
    cat << EOF
{
  "type": "command",
  "command": "$HOOK_SCRIPT",
  "async": true,
  "timeout": 30
}
EOF
    exit 1
  fi
fi

# Use jq if available, otherwise show manual instructions
if command -v jq &> /dev/null; then
  # Add SessionEnd hook using jq
  TEMP_FILE=$(mktemp)
  jq --arg hook_script "$HOOK_SCRIPT" '(.hooks //= {}) | .hooks.SessionEnd = [{
    "hooks": [{
      "type": "command",
      "command": $hook_script,
      "async": true,
      "timeout": 30
    }]
  }]' "$SETTINGS_FILE" > "$TEMP_FILE"

  if [ $? -eq 0 ]; then
    mv "$TEMP_FILE" "$SETTINGS_FILE"
    echo -e "${GREEN}✓${NC} Added SessionEnd hook to settings.json"
  else
    rm -f "$TEMP_FILE"
    echo -e "${YELLOW}!${NC} Failed to update settings.json"
    exit 1
  fi
else
  echo -e "${YELLOW}!${NC} jq not installed - manual installation required"
  echo ""
  echo "Add this to your ~/.claude/settings.json hooks section:"
  echo ""
  cat << EOF
"SessionEnd": [{
  "hooks": [{
    "type": "command",
    "command": "$HOOK_SCRIPT",
    "async": true,
    "timeout": 30
  }]
}]
EOF
  exit 1
fi

echo ""
echo "Auto-archive is now enabled!"
echo "Tasks will be preserved to ~/.claude/tasks-archive/ when sessions end."
echo ""
