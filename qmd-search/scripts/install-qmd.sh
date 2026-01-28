#!/bin/bash
#
# QMD Installation Script
#
# This script installs QMD (Query My Data) for on-device semantic search.
# Requires: Bun runtime (https://bun.sh)
#
# Usage:
#   ./install-qmd.sh
#
# What this script does:
# 1. Checks if Bun is installed
# 2. Installs QMD globally via Bun
# 3. Verifies the installation
# 4. Shows next steps for setting up collections

set -e

echo "==================================="
echo "   QMD Installation Script"
echo "==================================="
echo ""

# Check for Bun
if ! command -v bun &> /dev/null; then
    echo "ERROR: Bun is not installed."
    echo ""
    echo "Install Bun first:"
    echo "  curl -fsSL https://bun.sh/install | bash"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "✓ Bun found: $(bun --version)"
echo ""

# Install QMD
echo "Installing QMD..."
bun install -g https://github.com/tobi/qmd

echo ""

# Verify installation
if ! command -v qmd &> /dev/null; then
    echo "ERROR: QMD installation failed or not in PATH."
    echo ""
    echo "Try adding to your PATH:"
    echo "  export PATH=\"\$HOME/.bun/bin:\$PATH\""
    exit 1
fi

echo "✓ QMD installed: $(qmd --version 2>/dev/null || echo 'version check failed')"
echo ""

# Show status
echo "Checking QMD status..."
qmd status 2>/dev/null || echo "(No collections indexed yet)"

echo ""
echo "==================================="
echo "   Installation Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Add a collection:"
echo "   qmd collection add ~/Documents/notes --name notes --mask '**/*.md'"
echo ""
echo "2. Generate embeddings:"
echo "   qmd embed"
echo ""
echo "3. Search your documents:"
echo "   qmd search 'your query'        # Keyword search (BM25)"
echo "   qmd vsearch 'your query'       # Semantic search (vectors)"
echo "   qmd query 'your query'         # Hybrid search (best quality)"
echo ""
echo "For MCP integration with Claude Code, add to ~/.claude/settings.json:"
echo '   {
     "mcpServers": {
       "qmd": {
         "command": "qmd",
         "args": ["mcp"]
       }
     }
   }'
echo ""
