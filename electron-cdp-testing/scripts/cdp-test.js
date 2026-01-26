#!/usr/bin/env node
/**
 * CDP Test Runner
 *
 * Complete test runner for Electron apps with common operations.
 *
 * Usage:
 *   node cdp-test.js                       # Run basic connectivity test
 *   node cdp-test.js --interactive         # Interactive mode with commands
 *   node cdp-test.js --test-file test.json # Run tests from JSON file
 *
 * Test file format (test.json):
 * {
 *   "name": "My Test Suite",
 *   "steps": [
 *     { "action": "screenshot", "output": "before.png" },
 *     { "action": "click", "text": "Settings" },
 *     { "action": "wait", "ms": 500 },
 *     { "action": "fill", "selector": "#name", "value": "Test" },
 *     { "action": "eval", "expression": "document.title" }
 *   ]
 * }
 */

const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const DEFAULT_PORT = 9222;

class CDPClient {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.ws = null;
    this.messageId = 0;
    this.handlers = new Map();
  }

  async connect() {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.wsUrl);

      this.ws.on('open', () => {
        console.log('Connected to Electron app');
        resolve();
      });

      this.ws.on('message', (data) => {
        const result = JSON.parse(data);
        const handler = this.handlers.get(result.id);
        if (handler) {
          this.handlers.delete(result.id);
          handler(result);
        }
      });

      this.ws.on('error', reject);
      setTimeout(() => reject(new Error('Connection timeout')), 5000);
    });
  }

  async send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = ++this.messageId;

      this.handlers.set(id, (result) => {
        if (result.error) {
          reject(new Error(result.error.message));
        } else {
          resolve(result.result);
        }
      });

      this.ws.send(JSON.stringify({ id, method, params }));
      setTimeout(() => {
        if (this.handlers.has(id)) {
          this.handlers.delete(id);
          reject(new Error('Request timeout'));
        }
      }, 10000);
    });
  }

  async evaluate(expression, awaitPromise = false) {
    const result = await this.send('Runtime.evaluate', { expression, awaitPromise });
    if (result.exceptionDetails) {
      throw new Error(result.exceptionDetails.text);
    }
    return result.result?.value;
  }

  async screenshot(outputPath) {
    const result = await this.send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(outputPath, Buffer.from(result.data, 'base64'));
    return outputPath;
  }

  async clickByText(text) {
    return this.evaluate(`
      (function() {
        const elements = document.querySelectorAll('button, a, [role="button"], [onclick]');
        const el = Array.from(elements).find(e =>
          e.textContent.toLowerCase().includes('${text.toLowerCase()}')
        );
        if (el) { el.click(); return 'Clicked: ' + el.textContent.trim().slice(0, 50); }
        return 'Not found: ${text}';
      })()
    `);
  }

  async clickBySelector(selector) {
    return this.evaluate(`
      (function() {
        const el = document.querySelector('${selector}');
        if (el) { el.click(); return 'Clicked: ' + el.tagName; }
        return 'Not found: ${selector}';
      })()
    `);
  }

  async fill(selector, value) {
    return this.evaluate(`
      (function() {
        const el = document.querySelector('${selector}');
        if (el) {
          el.value = '${value.replace(/'/g, "\\'")}';
          el.dispatchEvent(new Event('input', { bubbles: true }));
          el.dispatchEvent(new Event('change', { bubbles: true }));
          return 'Filled: ' + el.tagName;
        }
        return 'Not found: ${selector}';
      })()
    `);
  }

  async fillByPlaceholder(placeholder, value) {
    return this.evaluate(`
      (function() {
        const el = document.querySelector('[placeholder*="${placeholder}"]');
        if (el) {
          el.value = '${value.replace(/'/g, "\\'")}';
          el.dispatchEvent(new Event('input', { bubbles: true }));
          el.dispatchEvent(new Event('change', { bubbles: true }));
          return 'Filled: ' + el.placeholder;
        }
        return 'Not found: ${placeholder}';
      })()
    `);
  }

  async getPageStructure() {
    return this.evaluate(`
      (function() {
        return JSON.stringify({
          title: document.title,
          url: window.location.href,
          buttons: Array.from(document.querySelectorAll('button')).map(b => ({
            text: b.textContent.trim().slice(0, 50),
            disabled: b.disabled,
            className: b.className.slice(0, 30)
          })).slice(0, 20),
          inputs: Array.from(document.querySelectorAll('input, textarea, select')).map(i => ({
            type: i.type || i.tagName.toLowerCase(),
            placeholder: i.placeholder,
            name: i.name,
            id: i.id
          })).slice(0, 20),
          links: Array.from(document.querySelectorAll('a[href]')).map(a => ({
            text: a.textContent.trim().slice(0, 30),
            href: a.href
          })).slice(0, 10)
        }, null, 2);
      })()
    `);
  }

  async checkElectronAPI() {
    const type = await this.evaluate('typeof window.electronAPI');
    if (type !== 'object') {
      return { available: false };
    }

    const methods = await this.evaluate('Object.keys(window.electronAPI)');
    return { available: true, methods };
  }

  async wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  close() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

async function getMainPage(port) {
  const response = await fetch(`http://localhost:${port}/json`);
  if (!response.ok) {
    throw new Error(`CDP not available on port ${port}`);
  }
  const targets = await response.json();

  const mainPage = targets.find(t =>
    t.type === 'page' &&
    !t.title.includes('DevTools') &&
    !t.url.includes('devtools://')
  );

  if (!mainPage) {
    console.log('Available targets:');
    targets.forEach(t => console.log(`  ${t.type}: ${t.title}`));
    throw new Error('No main page found');
  }

  return mainPage;
}

async function runBasicTest(client) {
  console.log('\n--- Basic Connectivity Test ---\n');

  // Test 1: Check electronAPI
  console.log('1. Checking electronAPI...');
  const apiStatus = await client.checkElectronAPI();
  if (apiStatus.available) {
    console.log(`   OK: electronAPI available with ${apiStatus.methods?.length || 0} methods`);
  } else {
    console.log('   WARN: electronAPI not available (may be expected for some pages)');
  }

  // Test 2: Get page structure
  console.log('2. Getting page structure...');
  const structure = await client.getPageStructure();
  const parsed = JSON.parse(structure);
  console.log(`   Title: ${parsed.title}`);
  console.log(`   Buttons: ${parsed.buttons.length}`);
  console.log(`   Inputs: ${parsed.inputs.length}`);
  console.log(`   Links: ${parsed.links.length}`);

  // Test 3: Take screenshot
  console.log('3. Taking screenshot...');
  const screenshotPath = path.join(process.cwd(), 'cdp-test-screenshot.png');
  await client.screenshot(screenshotPath);
  console.log(`   Saved to: ${screenshotPath}`);

  console.log('\n--- Test Complete ---\n');
}

async function runTestFile(client, testFilePath) {
  const content = fs.readFileSync(testFilePath, 'utf-8');
  const testSuite = JSON.parse(content);

  console.log(`\n--- Running: ${testSuite.name || 'Test Suite'} ---\n`);

  for (let i = 0; i < testSuite.steps.length; i++) {
    const step = testSuite.steps[i];
    console.log(`Step ${i + 1}: ${step.action}`);

    try {
      switch (step.action) {
        case 'screenshot':
          await client.screenshot(step.output || `screenshot-${i + 1}.png`);
          console.log(`   Saved: ${step.output || `screenshot-${i + 1}.png`}`);
          break;

        case 'click':
          if (step.text) {
            const result = await client.clickByText(step.text);
            console.log(`   ${result}`);
          } else if (step.selector) {
            const result = await client.clickBySelector(step.selector);
            console.log(`   ${result}`);
          }
          break;

        case 'fill':
          if (step.placeholder) {
            const result = await client.fillByPlaceholder(step.placeholder, step.value);
            console.log(`   ${result}`);
          } else if (step.selector) {
            const result = await client.fill(step.selector, step.value);
            console.log(`   ${result}`);
          }
          break;

        case 'eval':
          const evalResult = await client.evaluate(step.expression, step.await || false);
          console.log(`   Result: ${JSON.stringify(evalResult)}`);
          break;

        case 'wait':
          await client.wait(step.ms || 1000);
          console.log(`   Waited ${step.ms || 1000}ms`);
          break;

        case 'assert':
          const assertResult = await client.evaluate(step.expression);
          if (assertResult === step.expected) {
            console.log(`   PASS: ${step.message || 'Assertion passed'}`);
          } else {
            console.log(`   FAIL: Expected ${step.expected}, got ${assertResult}`);
          }
          break;

        default:
          console.log(`   Unknown action: ${step.action}`);
      }
    } catch (error) {
      console.log(`   ERROR: ${error.message}`);
      if (step.required !== false) {
        throw error;
      }
    }
  }

  console.log('\n--- Test Suite Complete ---\n');
}

async function runInteractive(client) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  console.log('\n--- Interactive Mode ---');
  console.log('Commands: screenshot, click <text>, fill <selector> <value>, eval <code>, structure, api, quit\n');

  const prompt = () => {
    rl.question('cdp> ', async (input) => {
      const parts = input.trim().split(' ');
      const cmd = parts[0].toLowerCase();

      try {
        switch (cmd) {
          case 'screenshot':
          case 's':
            const path = parts[1] || 'interactive-screenshot.png';
            await client.screenshot(path);
            console.log(`Saved: ${path}`);
            break;

          case 'click':
          case 'c':
            const text = parts.slice(1).join(' ');
            console.log(await client.clickByText(text));
            break;

          case 'fill':
          case 'f':
            const selector = parts[1];
            const value = parts.slice(2).join(' ');
            console.log(await client.fill(selector, value));
            break;

          case 'eval':
          case 'e':
            const code = parts.slice(1).join(' ');
            console.log(await client.evaluate(code));
            break;

          case 'structure':
          case 'st':
            console.log(await client.getPageStructure());
            break;

          case 'api':
            console.log(JSON.stringify(await client.checkElectronAPI(), null, 2));
            break;

          case 'quit':
          case 'q':
            client.close();
            rl.close();
            process.exit(0);
            return;

          case 'help':
          case 'h':
            console.log('Commands:');
            console.log('  screenshot [path]      - Take screenshot');
            console.log('  click <text>           - Click element by text');
            console.log('  fill <selector> <val>  - Fill input');
            console.log('  eval <code>            - Evaluate JavaScript');
            console.log('  structure              - Show page structure');
            console.log('  api                    - Check electronAPI');
            console.log('  quit                   - Exit');
            break;

          default:
            console.log('Unknown command. Type "help" for available commands.');
        }
      } catch (error) {
        console.log('Error:', error.message);
      }

      prompt();
    });
  };

  prompt();
}

async function main() {
  const args = process.argv.slice(2);
  const port = args.includes('--port')
    ? parseInt(args[args.indexOf('--port') + 1])
    : DEFAULT_PORT;

  try {
    console.log(`Connecting to CDP on port ${port}...`);
    const mainPage = await getMainPage(port);
    console.log(`Found: ${mainPage.title} (${mainPage.url})`);

    const client = new CDPClient(mainPage.webSocketDebuggerUrl);
    await client.connect();

    if (args.includes('--interactive') || args.includes('-i')) {
      await runInteractive(client);
    } else if (args.includes('--test-file')) {
      const testFileIndex = args.indexOf('--test-file');
      const testFile = args[testFileIndex + 1];
      await runTestFile(client, testFile);
      client.close();
    } else {
      await runBasicTest(client);
      client.close();
    }

  } catch (error) {
    console.error('Error:', error.message);
    console.log('\nMake sure Electron is running with: npm run dev:mcp');
    process.exit(1);
  }
}

main();
