#!/usr/bin/env node
/**
 * CDP Connection Helper
 *
 * Connects to a running Electron app via Chrome DevTools Protocol.
 *
 * Usage:
 *   node cdp-connect.js                    # List targets and show connection info
 *   node cdp-connect.js --eval "code"      # Evaluate JavaScript in renderer
 *   node cdp-connect.js --screenshot       # Take screenshot
 *   node cdp-connect.js --port 9223        # Use custom port
 */

const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');

const DEFAULT_PORT = 9222;

async function getTargets(port) {
  const response = await fetch(`http://localhost:${port}/json`);
  if (!response.ok) {
    throw new Error(`CDP not available on port ${port}. Start Electron with: npm run dev:mcp`);
  }
  return response.json();
}

function findMainPage(targets) {
  // Find the main page (not DevTools, not background)
  return targets.find(t =>
    t.type === 'page' &&
    !t.title.includes('DevTools') &&
    !t.url.includes('devtools://')
  );
}

async function connectToPage(wsUrl) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(wsUrl);

    ws.on('open', () => resolve(ws));
    ws.on('error', reject);

    setTimeout(() => reject(new Error('Connection timeout')), 5000);
  });
}

async function evaluate(ws, expression, awaitPromise = false) {
  return new Promise((resolve, reject) => {
    const id = Date.now();

    ws.send(JSON.stringify({
      id,
      method: 'Runtime.evaluate',
      params: { expression, awaitPromise }
    }));

    const handler = (data) => {
      const result = JSON.parse(data);
      if (result.id === id) {
        ws.off('message', handler);
        if (result.result?.exceptionDetails) {
          reject(new Error(result.result.exceptionDetails.text));
        } else {
          resolve(result.result?.result?.value);
        }
      }
    };

    ws.on('message', handler);
    setTimeout(() => reject(new Error('Evaluation timeout')), 10000);
  });
}

async function takeScreenshot(ws, outputPath) {
  return new Promise((resolve, reject) => {
    const id = Date.now();

    ws.send(JSON.stringify({
      id,
      method: 'Page.captureScreenshot',
      params: { format: 'png' }
    }));

    const handler = (data) => {
      const result = JSON.parse(data);
      if (result.id === id) {
        ws.off('message', handler);
        if (result.result?.data) {
          fs.writeFileSync(outputPath, Buffer.from(result.result.data, 'base64'));
          resolve(outputPath);
        } else {
          reject(new Error('Screenshot failed'));
        }
      }
    };

    ws.on('message', handler);
    setTimeout(() => reject(new Error('Screenshot timeout')), 10000);
  });
}

async function main() {
  const args = process.argv.slice(2);
  const port = args.includes('--port')
    ? parseInt(args[args.indexOf('--port') + 1])
    : DEFAULT_PORT;

  try {
    // Get targets
    console.log(`Connecting to CDP on port ${port}...`);
    const targets = await getTargets(port);

    const mainPage = findMainPage(targets);
    if (!mainPage) {
      console.error('No Electron page found. Available targets:');
      targets.forEach(t => console.log(`  - ${t.type}: ${t.title} (${t.url})`));
      process.exit(1);
    }

    console.log(`Found: ${mainPage.title}`);
    console.log(`URL: ${mainPage.url}`);
    console.log(`Page ID: ${mainPage.id}`);
    console.log(`WebSocket: ${mainPage.webSocketDebuggerUrl}`);
    console.log('');

    // Handle commands
    if (args.includes('--eval')) {
      const evalIndex = args.indexOf('--eval');
      const expression = args[evalIndex + 1];
      if (!expression) {
        console.error('Usage: --eval "expression"');
        process.exit(1);
      }

      const ws = await connectToPage(mainPage.webSocketDebuggerUrl);
      const result = await evaluate(ws, expression);
      console.log('Result:', result);
      ws.close();
    } else if (args.includes('--screenshot')) {
      const outputPath = args.includes('--output')
        ? args[args.indexOf('--output') + 1]
        : path.join(process.cwd(), 'screenshot.png');

      const ws = await connectToPage(mainPage.webSocketDebuggerUrl);
      await takeScreenshot(ws, outputPath);
      console.log(`Screenshot saved to: ${outputPath}`);
      ws.close();
    } else if (args.includes('--check-api')) {
      const ws = await connectToPage(mainPage.webSocketDebuggerUrl);
      const apiType = await evaluate(ws, 'typeof window.electronAPI');
      console.log(`electronAPI: ${apiType === 'object' ? 'Available' : 'Not available'}`);

      if (apiType === 'object') {
        const methods = await evaluate(ws, 'Object.keys(window.electronAPI).join(", ")');
        console.log(`Methods: ${methods}`);
      }
      ws.close();
    } else {
      // Just show connection info
      console.log('Commands:');
      console.log('  --eval "code"      Evaluate JavaScript');
      console.log('  --screenshot       Take screenshot');
      console.log('  --check-api        Check electronAPI availability');
      console.log('  --port 9223        Use custom port');
      console.log('  --output path      Screenshot output path');
    }

  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

main();
