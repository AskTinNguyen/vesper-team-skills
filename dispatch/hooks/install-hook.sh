#!/bin/bash
#
# install-hook.sh - Install the auto-archive Stop hook
#
# Usage: ./install-hook.sh
#
# This adds the Stop hook to ~/.claude/settings.json for automatic
# task archival when sessions end.
#

SETTINGS_FILE="$HOME/.claude/settings.json"
HOOK_SCRIPT="$HOME/.claude/skills/dispatch/hooks/auto-archive.sh"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${BLUE}Installing auto-archive Stop hook...${NC}"
echo ""

# Check if hook script exists
if [ ! -f "$HOOK_SCRIPT" ]; then
  echo -e "${YELLOW}Warning: Hook script not found at $HOOK_SCRIPT${NC}"
  echo "Creating it now..."
  mkdir -p "$(dirname "$HOOK_SCRIPT")"
fi

# Make hook executable
chmod +x "$HOOK_SCRIPT" 2>/dev/null

# Check if settings file exists
if [ ! -f "$SETTINGS_FILE" ]; then
  echo "Creating settings.json..."
  cat > "$SETTINGS_FILE" << 'EOF'
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "~/.claude/skills/dispatch/hooks/auto-archive.sh",
        "async": true,
        "timeout": 30
      }]
    }]
  }
}
EOF
  echo -e "${GREEN}✓${NC} Created settings.json with Stop hook"
  exit 0
fi

# Check if Stop hook already exists
if grep -q '"Stop"' "$SETTINGS_FILE" 2>/dev/null; then
  if grep -q 'auto-archive.sh' "$SETTINGS_FILE" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Auto-archive hook already installed"
    exit 0
  else
    echo -e "${YELLOW}!${NC} Stop hook exists but doesn't include auto-archive"
    echo ""
    echo "Add this to your Stop hooks manually:"
    echo ""
    cat << 'EOF'
{
  "type": "command",
  "command": "~/.claude/skills/dispatch/hooks/auto-archive.sh",
  "async": true,
  "timeout": 30
}
EOF
    exit 1
  fi
fi

# Use jq if available, otherwise show manual instructions
if command -v jq &> /dev/null; then
  # Add Stop hook using jq
  TEMP_FILE=$(mktemp)
  jq '.hooks.Stop = [{
    "hooks": [{
      "type": "command",
      "command": "~/.claude/skills/dispatch/hooks/auto-archive.sh",
      "async": true,
      "timeout": 30
    }]
  }]' "$SETTINGS_FILE" > "$TEMP_FILE"

  if [ $? -eq 0 ]; then
    mv "$TEMP_FILE" "$SETTINGS_FILE"
    echo -e "${GREEN}✓${NC} Added Stop hook to settings.json"
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
  cat << 'EOF'
"Stop": [{
  "hooks": [{
    "type": "command",
    "command": "~/.claude/skills/dispatch/hooks/auto-archive.sh",
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
