#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const readline = require('readline');
const {
  connectToPage,
  evaluate,
  findMainPage,
  getTargets,
  listTargets,
  parseArgs,
  prepareSession,
  resolveOutputPath,
  send,
  takeScreenshot,
} = require('./cdp-common');

function js(value) {
  return JSON.stringify(value);
}

class CDPClient {
  constructor(ws) {
    this.ws = ws;
  }

  async evaluate(expression, awaitPromise = false) {
    return evaluate(this.ws, expression, awaitPromise);
  }

  async screenshot(outputPath) {
    return takeScreenshot(this.ws, outputPath);
  }

  async clickByText(text) {
    return this.evaluate(`(() => {
      const needle = ${js(String(text).toLowerCase())};
      const nodes = Array.from(document.querySelectorAll('button, a, [role="button"], [onclick]'));
      const match = nodes.find((node) => (node.textContent || '').toLowerCase().includes(needle));
      if (!match) return ${js(`Not found: ${text}`)};
      match.click();
      return ${js('Clicked: ')} + (match.textContent || '').trim().slice(0, 80);
    })()`);
  }

  async clickBySelector(selector) {
    return this.evaluate(`(() => {
      const match = document.querySelector(${js(selector)});
      if (!match) return ${js(`Not found: ${selector}`)};
      match.click();
      return ${js('Clicked selector: ')} + ${js(selector)};
    })()`);
  }

  async fill(selector, value) {
    return this.evaluate(`(() => {
      const match = document.querySelector(${js(selector)});
      if (!match) return ${js(`Not found: ${selector}`)};
      match.value = ${js(value)};
      match.dispatchEvent(new Event('input', { bubbles: true }));
      match.dispatchEvent(new Event('change', { bubbles: true }));
      return ${js('Filled selector: ')} + ${js(selector)};
    })()`);
  }

  async fillByPlaceholder(placeholder, value) {
    return this.evaluate(`(() => {
      const match = Array.from(document.querySelectorAll('input, textarea')).find((node) =>
        (node.placeholder || '').includes(${js(placeholder)})
      );
      if (!match) return ${js(`Not found placeholder: ${placeholder}`)};
      match.value = ${js(value)};
      match.dispatchEvent(new Event('input', { bubbles: true }));
      match.dispatchEvent(new Event('change', { bubbles: true }));
      return ${js('Filled placeholder: ')} + (match.placeholder || '');
    })()`);
  }

  async getPageStructure() {
    return this.evaluate(`(() => ({
      title: document.title,
      url: window.location.href,
      hash: window.location.hash,
      buttons: Array.from(document.querySelectorAll('button')).slice(0, 20).map((node) => ({
        text: (node.textContent || '').trim().slice(0, 80),
        disabled: !!node.disabled,
      })),
      inputs: Array.from(document.querySelectorAll('input, textarea, select')).slice(0, 20).map((node) => ({
        tag: node.tagName.toLowerCase(),
        type: node.type || '',
        placeholder: node.placeholder || '',
        id: node.id || '',
      })),
    }))()`);
  }

  async checkElectronAPI() {
    const type = await this.evaluate('typeof window.electronAPI');
    if (type !== 'object') {
      return { available: false, type };
    }

    const methods = await this.evaluate('Object.keys(window.electronAPI)');
    return { available: true, type, methods };
  }

  async wait(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  async rawSend(method, params = {}, timeoutMs = 10000) {
    return send(this.ws, method, params, timeoutMs);
  }

  close() {
    this.ws.close();
  }
}

async function connectClient(options) {
  const targets = await getTargets(options.port);
  const mainPage = findMainPage(targets, options.titlePattern);
  if (!mainPage) {
    throw new Error(`No usable page target found.\n${JSON.stringify(listTargets(targets), null, 2)}`);
  }

  const ws = await connectToPage(mainPage.webSocketDebuggerUrl);
  await prepareSession(ws);
  return { client: new CDPClient(ws), mainPage };
}

async function runBasicTest(client) {
  console.log('\n--- Basic Vesper CDP Smoke ---\n');

  const apiStatus = await client.checkElectronAPI();
  console.log(
    `1. window.electronAPI: ${apiStatus.available ? 'PASS' : 'FAIL'} (${apiStatus.type || 'unknown'})`
  );

  const structure = await client.getPageStructure();
  console.log(`2. Title: ${structure.title}`);
  console.log(`3. Hash: ${structure.hash || '(empty)'}`);
  console.log(`4. Buttons: ${structure.buttons.length}`);
  console.log(`5. Inputs: ${structure.inputs.length}`);

  const screenshotPath = resolveOutputPath(null, 'cdp-test-screenshot.png');
  await client.screenshot(screenshotPath);
  console.log(`6. Screenshot: PASS (${screenshotPath})`);
}

async function runTestFile(client, testFilePath) {
  const content = fs.readFileSync(testFilePath, 'utf-8');
  const testSuite = JSON.parse(content);

  console.log(`\n--- Running: ${testSuite.name || 'Test Suite'} ---\n`);

  for (let index = 0; index < testSuite.steps.length; index += 1) {
    const step = testSuite.steps[index];
    const label = `Step ${index + 1}: ${step.description || step.action}`;
    process.stdout.write(`${label}... `);

    try {
      if (step.action === 'screenshot') {
        const screenshotPath = resolveOutputPath(step.output || null, `screenshot-${index + 1}.png`);
        await client.screenshot(screenshotPath);
        console.log(`PASS (${screenshotPath})`);
      } else if (step.action === 'click') {
        const result = step.text
          ? await client.clickByText(step.text)
          : await client.clickBySelector(step.selector);
        console.log(`PASS (${result})`);
      } else if (step.action === 'fill') {
        const result = step.placeholder
          ? await client.fillByPlaceholder(step.placeholder, step.value)
          : await client.fill(step.selector, step.value);
        console.log(`PASS (${result})`);
      } else if (step.action === 'eval') {
        const result = await client.evaluate(step.expression, step.await === true);
        console.log(`PASS (${JSON.stringify(result)})`);
      } else if (step.action === 'wait') {
        await client.wait(step.ms || 500);
        console.log(`PASS (${step.ms || 500}ms)`);
      } else if (step.action === 'assert') {
        const result = await client.evaluate(step.expression, step.await === true);
        if (result !== step.expected) {
          throw new Error(`Expected ${JSON.stringify(step.expected)}, got ${JSON.stringify(result)}`);
        }
        console.log('PASS');
      } else {
        throw new Error(`Unknown action: ${step.action}`);
      }
    } catch (error) {
      console.log(`FAIL (${error.message})`);
      if (step.required !== false) {
        throw error;
      }
    }
  }
}

async function runInteractive(client) {
  return new Promise((resolve) => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    console.log('\nCommands: screenshot [path], click <text>, eval <code>, structure, api, quit\n');

    const prompt = () => {
      rl.question('cdp> ', async (input) => {
        const [command, ...rest] = input.trim().split(' ');

        try {
          if (command === 'screenshot' || command === 's') {
            const screenshotPath = resolveOutputPath(rest[0] || null, 'interactive-screenshot.png');
            await client.screenshot(screenshotPath);
            console.log(screenshotPath);
          } else if (command === 'click' || command === 'c') {
            console.log(await client.clickByText(rest.join(' ')));
          } else if (command === 'eval' || command === 'e') {
            console.log(await client.evaluate(rest.join(' ')));
          } else if (command === 'structure' || command === 'st') {
            console.log(JSON.stringify(await client.getPageStructure(), null, 2));
          } else if (command === 'api') {
            console.log(JSON.stringify(await client.checkElectronAPI(), null, 2));
          } else if (command === 'quit' || command === 'q') {
            rl.close();
            resolve();
            return;
          } else if (command === 'help' || command === 'h') {
            console.log('screenshot [path], click <text>, eval <code>, structure, api, quit');
          } else {
            console.log('Unknown command. Type "help" for commands.');
          }
        } catch (error) {
          console.log(`Error: ${error.message}`);
        }

        prompt();
      });
    };

    prompt();
  });
}

async function main() {
  const options = parseArgs(process.argv);
  const { args } = options;
  let client = null;

  try {
    const connection = await connectClient(options);
    client = connection.client;
    const { mainPage } = connection;
    console.log(`Connected to: ${mainPage.title} (${mainPage.url})`);

    if (args.includes('--interactive') || args.includes('-i')) {
      await runInteractive(client);
      return;
    }

    if (args.includes('--test-file')) {
      const testFilePath = args[args.indexOf('--test-file') + 1];
      if (!testFilePath) {
        throw new Error('Usage: --test-file ./scripts/sample-test.json');
      }
      await runTestFile(client, path.resolve(testFilePath));
      return;
    }

    await runBasicTest(client);
  } catch (error) {
    console.error(`Error: ${error.message}`);
    console.error('Tip: run ./scripts/validate-setup.sh first, then retry against a live Vesper page target.');
    process.exit(1);
  } finally {
    if (client) {
      client.close();
    }
  }
}

main();
