#!/bin/bash
#
# Validate Electron CDP Setup
#
# This script checks if your Electron app is properly configured
# for CDP-based testing.
#
# Usage: ./validate-setup.sh [port]
#

PORT=${1:-9222}
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  Electron CDP Setup Validation"
echo "=========================================="
echo ""

# Check 1: Is CDP port accessible?
echo -n "1. Checking CDP port ${PORT}... "
if curl -s "http://localhost:${PORT}/json" > /dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
    CDP_AVAILABLE=true
else
    echo -e "${RED}FAIL${NC}"
    echo "   CDP not available on port ${PORT}"
    echo "   Start Electron with: npm run dev:mcp"
    CDP_AVAILABLE=false
fi

if [ "$CDP_AVAILABLE" = true ]; then
    # Check 2: List available targets
    echo ""
    echo "2. Available CDP targets:"
    TARGETS=$(curl -s "http://localhost:${PORT}/json")
    echo "$TARGETS" | python3 -c "
import sys, json
targets = json.load(sys.stdin)
for t in targets:
    icon = '  [page]' if t['type'] == 'page' else '  [' + t['type'] + ']'
    print(f\"{icon} {t.get('title', 'Untitled')}\")
    print(f\"        URL: {t.get('url', 'N/A')}\")
" 2>/dev/null || echo "   Could not parse targets"

    # Check 3: Find main page
    echo ""
    echo -n "3. Finding main Electron page... "
    MAIN_PAGE=$(echo "$TARGETS" | python3 -c "
import sys, json
targets = json.load(sys.stdin)
for t in targets:
    if t['type'] == 'page' and 'DevTools' not in t.get('title', '') and 'devtools://' not in t.get('url', ''):
        print(t['webSocketDebuggerUrl'])
        break
" 2>/dev/null)

    if [ -n "$MAIN_PAGE" ]; then
        echo -e "${GREEN}FOUND${NC}"
        echo "   WebSocket URL: $MAIN_PAGE"
    else
        echo -e "${YELLOW}NOT FOUND${NC}"
        echo "   No main page detected. The app window may not be open."
    fi

    # Check 4: Test WebSocket connection
    if [ -n "$MAIN_PAGE" ]; then
        echo ""
        echo -n "4. Testing WebSocket connection... "
        # Simple test using node if available
        if command -v node &> /dev/null; then
            WS_TEST=$(node -e "
const WebSocket = require('ws');
const ws = new WebSocket('$MAIN_PAGE');
ws.on('open', () => { console.log('OK'); ws.close(); process.exit(0); });
ws.on('error', (e) => { console.log('FAIL'); process.exit(1); });
setTimeout(() => { console.log('TIMEOUT'); process.exit(1); }, 3000);
" 2>/dev/null)
            if [ "$WS_TEST" = "OK" ]; then
                echo -e "${GREEN}OK${NC}"
            else
                echo -e "${RED}FAIL${NC}"
                echo "   Could not connect via WebSocket"
            fi
        else
            echo -e "${YELLOW}SKIPPED${NC} (node not available)"
        fi
    fi
fi

# Check 5: Environment configuration
echo ""
echo "5. Checking environment configuration:"

# Check .env file
ENV_FILE="apps/backend/.env"
if [ -f "$ENV_FILE" ]; then
    if grep -q "ELECTRON_MCP_ENABLED=true" "$ENV_FILE"; then
        echo -e "   ELECTRON_MCP_ENABLED: ${GREEN}enabled${NC}"
    else
        echo -e "   ELECTRON_MCP_ENABLED: ${YELLOW}not set${NC}"
        echo "   Add ELECTRON_MCP_ENABLED=true to $ENV_FILE for MCP tools"
    fi

    if grep -q "ELECTRON_DEBUG_PORT" "$ENV_FILE"; then
        DEBUG_PORT=$(grep "ELECTRON_DEBUG_PORT" "$ENV_FILE" | cut -d'=' -f2)
        echo "   ELECTRON_DEBUG_PORT: $DEBUG_PORT"
    else
        echo "   ELECTRON_DEBUG_PORT: not set (default: 9222)"
    fi
else
    echo -e "   ${YELLOW}$ENV_FILE not found${NC}"
fi

# Check 6: Package.json scripts
echo ""
echo "6. Checking npm scripts:"
PKG_FILE="apps/frontend/package.json"
if [ -f "$PKG_FILE" ]; then
    if grep -q "dev:mcp" "$PKG_FILE"; then
        echo -e "   npm run dev:mcp: ${GREEN}available${NC}"
    else
        echo -e "   npm run dev:mcp: ${RED}not found${NC}"
    fi

    if grep -q "start:mcp" "$PKG_FILE"; then
        echo -e "   npm run start:mcp: ${GREEN}available${NC}"
    else
        echo -e "   npm run start:mcp: ${YELLOW}not found${NC}"
    fi
else
    echo -e "   ${YELLOW}$PKG_FILE not found${NC}"
fi

echo ""
echo "=========================================="
echo "  Validation Complete"
echo "=========================================="
echo ""

if [ "$CDP_AVAILABLE" = true ] && [ -n "$MAIN_PAGE" ]; then
    echo -e "${GREEN}Setup looks good!${NC}"
    echo ""
    echo "Quick test commands:"
    echo "  node .claude/skills/electron-cdp-testing/scripts/cdp-connect.js --check-api"
    echo "  node .claude/skills/electron-cdp-testing/scripts/cdp-test.js"
else
    echo -e "${YELLOW}Setup incomplete.${NC}"
    echo ""
    echo "To start Electron with CDP:"
    echo "  cd apps/frontend && npm run dev:mcp"
fi
