---
name: electron-cdp-testing
description: Automated E2E testing for Electron apps using Chrome DevTools Protocol (CDP). Use this when testing Electron frontend features, clicking buttons, filling forms, validating UI state, taking screenshots, or running QA verification. Supports both MCP tools and direct WebSocket CDP connections.
---

# Electron CDP Testing Skill

Automated E2E testing for Electron applications via Chrome DevTools Protocol.

## When to Use This Skill

- Testing Electron app UI interactions (clicks, form fills, navigation)
- Validating visual feedback and state changes
- Running QA verification workflows
- Taking screenshots for visual testing
- Testing `window.electronAPI` IPC methods
- Debugging Electron renderer process issues

## Important: CDP vs Regular Browser

**Critical Understanding**: `window.electronAPI` is ONLY available in the Electron renderer process where the preload script runs. Regular browsers accessing `localhost:5173` won't have it.

**Common Pitfall**: Using `agent-browser open http://localhost:5173` opens a separate browser WITHOUT access to `window.electronAPI`. Always use CDP to connect to the actual Electron window.

## Setup

### Step 1: Start Electron with Remote Debugging

```bash
# From apps/frontend directory
npm run dev:mcp
# This runs: electron-vite dev -- --remote-debugging-port=9222

# Or for production build
npm run start:mcp
```

### Step 2: Verify CDP is Available

```bash
# List available CDP targets
curl -s http://localhost:9222/json
```

Look for the target with `"type": "page"` and your app title (e.g., "Auto Claude"):

```json
{
  "id": "BA1A364B10B4180539DD84E06565901B",
  "title": "Auto Claude",
  "type": "page",
  "url": "http://localhost:5173/",
  "webSocketDebuggerUrl": "ws://localhost:9222/devtools/page/BA1A364B10B4180539DD84E06565901B"
}
```

### Step 3: Enable MCP Tools (Optional but Recommended)

Set in `apps/backend/.env`:
```bash
ELECTRON_MCP_ENABLED=true
ELECTRON_DEBUG_PORT=9222
```

## Two Approaches for CDP Testing

### Approach 1: MCP Tools (Recommended for Agent Use)

When `ELECTRON_MCP_ENABLED=true`, these tools are available:

| Tool | Purpose |
|------|---------|
| `mcp__electron__get_electron_window_info` | Get info about running windows |
| `mcp__electron__take_screenshot` | Capture screenshot |
| `mcp__electron__send_command_to_electron` | Send commands (click, fill, eval) |
| `mcp__electron__read_electron_logs` | Read console logs |

**Commands for `send_command_to_electron`:**

```
click_by_text       - Click element by visible text
click_by_selector   - Click element by CSS selector
fill_input          - Fill input by selector or placeholder
select_option       - Select dropdown option
send_keyboard_shortcut - Send Enter, Escape, Ctrl+N, etc.
navigate_to_hash    - Navigate to hash routes (#settings)
get_page_structure  - Get overview of interactive elements
debug_elements      - Get debugging info about buttons/forms
verify_form_state   - Check form state and validation
eval                - Execute custom JavaScript
```

### Approach 2: Direct WebSocket CDP (For Scripts/Automation)

Use when MCP tools aren't available or for custom automation scripts.

**Quick Test Script:**

```javascript
// Run with: node scripts/cdp-test.js
const WebSocket = require('ws');

async function testElectronApp() {
  // 1. Get available targets
  const response = await fetch('http://localhost:9222/json');
  const targets = await response.json();
  const mainPage = targets.find(t => t.type === 'page' && !t.title.includes('DevTools'));

  if (!mainPage) {
    console.error('Electron app not found. Start with: npm run dev:mcp');
    process.exit(1);
  }

  console.log('Found page:', mainPage.title);

  // 2. Connect via WebSocket
  const ws = new WebSocket(mainPage.webSocketDebuggerUrl);

  return new Promise((resolve, reject) => {
    ws.on('open', () => {
      // Test if electronAPI exists
      ws.send(JSON.stringify({
        id: 1,
        method: 'Runtime.evaluate',
        params: { expression: 'typeof window.electronAPI' }
      }));
    });

    ws.on('message', (data) => {
      const result = JSON.parse(data);
      if (result.id === 1) {
        const apiType = result.result?.result?.value;
        console.log('electronAPI type:', apiType);
        console.log(apiType === 'object' ? 'SUCCESS: electronAPI available' : 'FAIL: electronAPI not available');
        ws.close();
        resolve();
      }
    });

    ws.on('error', reject);
    setTimeout(() => reject(new Error('Timeout')), 10000);
  });
}

testElectronApp().catch(console.error);
```

## Common CDP Operations

### Test if electronAPI Exists

```javascript
expression: 'typeof window.electronAPI'
// Returns: "object" if exists
```

### Call an Async IPC Method

```javascript
ws.send(JSON.stringify({
  id: 1,
  method: 'Runtime.evaluate',
  params: {
    expression: 'window.electronAPI.listDocumentation("project-id").then(r => JSON.stringify(r))',
    awaitPromise: true
  }
}));
```

### Click a Button by Text

```javascript
expression: `(function() {
  const btn = Array.from(document.querySelectorAll("button"))
    .find(b => b.textContent.includes("Create New"));
  if (btn) { btn.click(); return "Clicked"; }
  return "Not found";
})()`
```

### Fill an Input Field

```javascript
expression: `(function() {
  const input = document.querySelector('input[placeholder="Enter task description"]');
  if (input) {
    input.value = "Test task";
    input.dispatchEvent(new Event('input', { bubbles: true }));
    return "Filled";
  }
  return "Not found";
})()`
```

### Take a Screenshot

```javascript
ws.send(JSON.stringify({
  id: 1,
  method: 'Page.captureScreenshot',
  params: { format: 'png' }
}));

// Handle response
ws.on('message', (data) => {
  const result = JSON.parse(data);
  if (result.result?.data) {
    const fs = require('fs');
    fs.writeFileSync('/tmp/screenshot.png', Buffer.from(result.result.data, 'base64'));
    console.log('Screenshot saved to /tmp/screenshot.png');
  }
});
```

### Navigate to a Hash Route

```javascript
expression: `window.location.hash = '#settings'`
```

### Get Page Structure

```javascript
expression: `(function() {
  const elements = {
    buttons: Array.from(document.querySelectorAll('button')).map(b => ({
      text: b.textContent.trim().slice(0, 50),
      disabled: b.disabled
    })),
    inputs: Array.from(document.querySelectorAll('input, textarea')).map(i => ({
      type: i.type,
      placeholder: i.placeholder,
      value: i.value.slice(0, 20)
    })),
    links: Array.from(document.querySelectorAll('a')).map(a => ({
      text: a.textContent.trim().slice(0, 30),
      href: a.href
    }))
  };
  return JSON.stringify(elements, null, 2);
})()`
```

## Validation Flow

### Step 1: Connect and Verify

```
Tool: mcp__electron__get_electron_window_info
```

Verify the app is running. If not found, document that Electron validation was skipped.

### Step 2: Take Screenshot

```
Tool: mcp__electron__take_screenshot
```

Capture current state for visual verification.

### Step 3: Analyze Page Structure

```
Tool: mcp__electron__send_command_to_electron
Command: get_page_structure
```

Get overview of all interactive elements.

### Step 4: Interact and Verify

Use `send_command_to_electron` with appropriate commands:

```
Command: click_by_text
Args: {"text": "Button Text"}

Command: fill_input
Args: {"placeholder": "Enter value", "value": "test input"}

Command: send_keyboard_shortcut
Args: {"text": "Enter"}
```

### Step 5: Check Logs

```
Tool: mcp__electron__read_electron_logs
Args: {"logType": "console", "lines": 50}
```

Check for JavaScript errors or warnings.

## Document Findings

```
ELECTRON VALIDATION:
- App Connection: PASS/FAIL
  - Debug port accessible: YES/NO
  - Connected to correct window: YES/NO
- UI Verification: PASS/FAIL
  - Screenshots captured: [list]
  - Visual elements correct: PASS/FAIL
  - Interactions working: PASS/FAIL
- Console Errors: [list or "None"]
- electronAPI Features: PASS/FAIL
  - [Feature]: PASS/FAIL
- Issues: [list or "None"]
```

## Troubleshooting

### "Cannot start http server for devtools" Error

CDP port already in use. Kill existing processes:

```bash
lsof -ti:9222 | xargs kill -9
pkill -f "electron"
```

### "window.electronAPI is undefined"

You're likely connecting to a regular browser window instead of the Electron window. Use the WebSocket approach with the correct page ID from `curl http://localhost:9222/json`.

### agent-browser Connects to Wrong Target

Don't use `agent-browser --cdp 9222`. Use the direct WebSocket connection to the specific page target.

### App Not Running

If Electron app is not running:
1. Start with `npm run dev:mcp` from `apps/frontend`
2. Verify with `curl http://localhost:9222/json`
3. Document that Electron validation was skipped if unavailable

### Headless Environment (CI/CD)

If running without display:
1. Skip interactive Electron validation
2. Document: "Electron UI validation skipped - headless environment"
3. Rely on unit/integration tests

## Helper Scripts

See the `scripts/` directory for ready-to-use utilities:

- `cdp-connect.js` - Connect and get page info
- `cdp-test.js` - Complete test runner with common operations
- `validate-setup.sh` - Verify CDP setup is correct

## Reference

- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [CDP Domains](https://chromedevtools.github.io/devtools-protocol/tot/)
- [Electron Remote Debugging](https://www.electronjs.org/docs/latest/tutorial/debugging-main-process)
