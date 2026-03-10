#!/usr/bin/env node

const {
  connectToPage,
  evaluate,
  findMainPage,
  getTargets,
  listTargets,
  parseArgs,
  prepareSession,
  resolveOutputPath,
  takeScreenshot,
} = require('./cdp-common');

async function main() {
  const options = parseArgs(process.argv);
  const { args, port, titlePattern } = options;

  try {
    console.log(`Connecting to CDP on port ${port}...`);
    const targets = await getTargets(port);

    if (args.includes('--list-targets')) {
      console.log(JSON.stringify(listTargets(targets), null, 2));
      return;
    }

    const mainPage = findMainPage(targets, titlePattern);
    if (!mainPage) {
      console.error('No usable Electron page target found.');
      console.error(JSON.stringify(listTargets(targets), null, 2));
      process.exit(1);
    }

    console.log(`Found: ${mainPage.title}`);
    console.log(`URL: ${mainPage.url}`);
    console.log(`Page ID: ${mainPage.id}`);
    console.log(`WebSocket: ${mainPage.webSocketDebuggerUrl}`);
    console.log('');

    if (args.length === 0) return;

    const ws = await connectToPage(mainPage.webSocketDebuggerUrl);
    await prepareSession(ws);

    if (args.includes('--eval')) {
      const expression = args[args.indexOf('--eval') + 1];
      if (!expression) {
        console.error('Usage: --eval "expression"');
        process.exit(1);
      }

      const awaitPromise = args.includes('--await');
      const result = await evaluate(ws, expression, awaitPromise);
      console.log(JSON.stringify(result, null, 2));
    } else if (args.includes('--screenshot')) {
      const outputPath = resolveOutputPath(
        args.includes('--output') ? args[args.indexOf('--output') + 1] : null,
        'cdp-connect-screenshot.png'
      );
      await takeScreenshot(ws, outputPath);
      console.log(`Screenshot saved to: ${outputPath}`);
    } else if (args.includes('--check-api')) {
      const apiType = await evaluate(ws, 'typeof window.electronAPI');
      console.log(`electronAPI: ${apiType === 'object' ? 'Available' : 'Not available'}`);

      if (apiType === 'object') {
        const methods = await evaluate(ws, 'Object.keys(window.electronAPI)');
        console.log(`Method count: ${methods.length}`);
        console.log(JSON.stringify(methods.slice(0, 20), null, 2));
      }
    } else {
      console.log('Commands:');
      console.log('  --list-targets            Print all CDP targets');
      console.log('  --eval "code" [--await]   Evaluate JavaScript');
      console.log('  --screenshot              Take screenshot');
      console.log('  --check-api               Check window.electronAPI');
      console.log('  --title-pattern Vesper    Prefer matching target title');
      console.log('  --port 9222               Use custom port');
    }

    ws.close();
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

main();
