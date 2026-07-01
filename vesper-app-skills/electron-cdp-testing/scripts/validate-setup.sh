#!/usr/bin/env bash

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${1:-9222}"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "  Electron CDP Setup Validation"
echo "=========================================="
echo ""

echo -n "1. Checking CDP port ${PORT}... "
if curl -s "http://127.0.0.1:${PORT}/json" > /dev/null 2>&1; then
  echo -e "${GREEN}OK${NC}"
  CDP_AVAILABLE=true
else
  echo -e "${RED}FAIL${NC}"
  echo "   CDP not available on port ${PORT}"
  echo "   In Vesper, source scripts/detect-instance.sh and relaunch Electron with --remote-debugging-port=9222."
  CDP_AVAILABLE=false
fi

MAIN_PAGE=""
if [ "$CDP_AVAILABLE" = true ]; then
  echo ""
  echo "2. Available CDP targets:"
  TARGETS="$(curl -s "http://127.0.0.1:${PORT}/json")"
  echo "$TARGETS" | python3 -c "
import json, sys
targets = json.load(sys.stdin)
for target in targets:
    kind = target.get('type', 'unknown')
    title = target.get('title', 'Untitled')
    url = target.get('url', 'N/A')
    print(f'  [{kind}] {title}')
    print(f'        URL: {url}')
" 2>/dev/null || echo "   Could not parse targets"

  echo ""
  echo -n "3. Finding Vesper page target... "
  MAIN_PAGE="$(echo "$TARGETS" | python3 -c "
import json, sys
targets = json.load(sys.stdin)
pages = [t for t in targets if t.get('type') == 'page' and 'DevTools' not in t.get('title', '')]
preferred = next((t for t in pages if 'Vesper' in t.get('title', '')), None)
match = preferred or (pages[0] if pages else None)
print(match.get('webSocketDebuggerUrl', '') if match else '')
" 2>/dev/null)"

  if [ -n "$MAIN_PAGE" ]; then
    echo -e "${GREEN}FOUND${NC}"
    echo "   WebSocket URL: $MAIN_PAGE"
  else
    echo -e "${YELLOW}NOT FOUND${NC}"
    echo "   No usable page target detected."
  fi

  if [ -n "$MAIN_PAGE" ] && command -v node > /dev/null 2>&1; then
    echo ""
    echo -n "4. Testing WebSocket connection... "
    WS_TEST="$(node -e "
const WebSocketImpl = globalThis.WebSocket || require('ws');
const ws = new WebSocketImpl(process.argv[1]);
ws.on('open', () => { console.log('OK'); ws.close(); process.exit(0); });
ws.on('error', () => { console.log('FAIL'); process.exit(1); });
setTimeout(() => { console.log('TIMEOUT'); process.exit(1); }, 3000);
" "$MAIN_PAGE" 2>/dev/null)"
    if [ "$WS_TEST" = "OK" ]; then
      echo -e "${GREEN}OK${NC}"
    else
      echo -e "${RED}FAIL${NC}"
      echo "   Could not connect via WebSocket"
    fi
  fi
fi

echo ""
echo "5. Checking Vesper repo hints:"

if [ -f "package.json" ] && grep -q '"electron:dev"' package.json; then
  echo -e "   repo-root electron:dev script: ${GREEN}found${NC}"
else
  echo -e "   repo-root electron:dev script: ${YELLOW}not found${NC}"
fi

if [ -f "scripts/detect-instance.sh" ]; then
  echo -e "   scripts/detect-instance.sh: ${GREEN}found${NC}"
else
  echo -e "   scripts/detect-instance.sh: ${YELLOW}not found${NC}"
fi

if [ -f "scripts/e2e/cdp-utils.cjs" ]; then
  echo -e "   scripts/e2e/cdp-utils.cjs: ${GREEN}found${NC}"
else
  echo -e "   scripts/e2e/cdp-utils.cjs: ${YELLOW}not found${NC}"
fi

echo ""
echo "=========================================="
echo "  Validation Complete"
echo "=========================================="
echo ""

if [ "$CDP_AVAILABLE" = true ] && [ -n "$MAIN_PAGE" ]; then
  echo -e "${GREEN}Setup looks good.${NC}"
  echo ""
  echo "Quick commands:"
  echo "  node \"$SCRIPT_DIR/cdp-connect.js\" --check-api"
  echo "  node \"$SCRIPT_DIR/cdp-test.js\" --test-file \"$SCRIPT_DIR/sample-test.json\""
else
  echo -e "${YELLOW}Setup incomplete.${NC}"
  echo ""
  echo "Vesper split-launch reminder:"
  echo "  Shell A: source scripts/detect-instance.sh && bun run electron:build:resources && bun run electron:build:code-worker && bun x concurrently -k \"bun run electron:dev:vite\" \"bun run electron:dev:main\" \"bun run electron:dev:preload\""
  echo "  Shell B: source scripts/detect-instance.sh && VITE_DEV_SERVER_URL=\"http://localhost:\${VESPER_VITE_PORT}\" ./node_modules/.bin/electron --remote-debugging-port=9222 apps/electron"
fi
