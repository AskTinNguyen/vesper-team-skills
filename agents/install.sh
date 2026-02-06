#!/bin/bash
# OpenClaw Agent Installer
# Usage: ./install.sh <agent-name>

set -e

AGENT_NAME=$1
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENCLAW_DIR="${HOME}/.openclaw"

if [ -z "$AGENT_NAME" ]; then
    echo "Usage: ./install.sh <agent-name>"
    echo "Available agents:"
    ls -d "$SCRIPT_DIR"/*/ 2>/dev/null | xargs -n1 basename | grep -v "^$"
    exit 1
fi

AGENT_DIR="$SCRIPT_DIR/$AGENT_NAME"

if [ ! -d "$AGENT_DIR" ]; then
    echo "Error: Agent '$AGENT_NAME' not found"
    echo "Available agents:"
    ls -d "$SCRIPT_DIR"/*/ 2>/dev/null | xargs -n1 basename
    exit 1
fi

# Determine workspace name
case "$AGENT_NAME" in
    "jeff")
        WORKSPACE_NAME="workspace-jeff"
        ;;
    "research-crawler")
        WORKSPACE_NAME="workspace-research"
        ;;
    "sidekick-main")
        WORKSPACE_NAME="workspace"
        ;;
    *)
        WORKSPACE_NAME="workspace-$AGENT_NAME"
        ;;
esac

TARGET_DIR="$OPENCLAW_DIR/$WORKSPACE_NAME"

echo "Installing agent: $AGENT_NAME"
echo "Source: $AGENT_DIR"
echo "Target: $TARGET_DIR"
echo ""

# Check if target exists
if [ -d "$TARGET_DIR" ]; then
    read -p "Target directory exists. Overwrite? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Create target directory
mkdir -p "$TARGET_DIR"

# Copy files
echo "Copying workspace files..."
cp -r "$AGENT_DIR"/* "$TARGET_DIR/" 2>/dev/null || true

# Remove config.json from workspace (it's for reference, not runtime)
rm -f "$TARGET_DIR/config.json"

# Create PARA structure if needed
mkdir -p "$TARGET_DIR"/{Areas,Projects,Resources,Archives,memory}

echo ""
echo "✅ Agent workspace installed to: $TARGET_DIR"
echo ""
echo "📝 Next steps:"
echo "1. Add the agent to your OpenClaw config (~/.openclaw/openclaw.json)"
echo "   See: $AGENT_DIR/config.json for the config snippet"
echo ""
echo "2. Add to your coordinator's subagents.allowAgents list"
echo ""
echo "3. Restart gateway: openclaw gateway restart"
echo ""
echo "4. Test: sessions_spawn(agentId='$AGENT_NAME', task='Hello!')"
