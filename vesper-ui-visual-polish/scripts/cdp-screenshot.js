#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const WebSocket = require('ws');

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith('--')) continue;
    const key = token.slice(2);
    const next = argv[i + 1];
    if (!next || next.startsWith('--')) {
      args[key] = true;
      continue;
    }
    args[key] = next;
    i += 1;
  }
  return args;
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const port = args.port || '9222';
  const host = args.host || '127.0.0.1';
  const route = args.route;
  const requestedWorkspaceId = args['workspace-id'];
  const waitFor = args['wait-for'];
  const clickText = args['click-text'];
  const out = args.out || `/tmp/vesper-cdp-${Date.now()}.png`;
  const waitMs = Number(args['wait-ms'] || (route ? 2200 : 800));
  const timeoutMs = Number(args['timeout-ms'] || 15000);
  const endpoint = `http://${host}:${port}/json`;

  const response = await fetch(endpoint);
  if (!response.ok) {
    throw new Error(`CDP endpoint failed: ${response.status} ${response.statusText}`);
  }

  const targets = await response.json();
  const pageTarget = targets.find((target) => target.type === 'page')
    || targets[0];

  if (!pageTarget?.webSocketDebuggerUrl) {
    throw new Error('No debuggable Electron page target found');
  }

  const ws = new WebSocket(pageTarget.webSocketDebuggerUrl);
  let messageId = 0;
  const pending = new Map();

  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++messageId;
    pending.set(id, { resolve, reject });
    ws.send(JSON.stringify({ id, method, params }));
    setTimeout(() => {
      if (pending.has(id)) {
        pending.delete(id);
        reject(new Error(`Timeout waiting for ${method}`));
      }
    }, timeoutMs);
  });

  ws.on('message', (buffer) => {
    const msg = JSON.parse(buffer.toString());
    if (msg.id && pending.has(msg.id)) {
      const { resolve, reject } = pending.get(msg.id);
      pending.delete(msg.id);
      if (msg.error) reject(new Error(msg.error.message));
      else resolve(msg.result);
    }
  });

  await new Promise((resolve, reject) => {
    ws.once('open', resolve);
    ws.once('error', reject);
  });

  const evaluate = async (expression, awaitPromise = true) => {
    const result = await send('Runtime.evaluate', {
      expression,
      awaitPromise,
      returnByValue: true,
    });

    if (result.exceptionDetails) {
      throw new Error(result.exceptionDetails.text || 'Renderer evaluation failed');
    }

    return result.result?.value;
  };

  await send('Runtime.enable');
  await send('Page.enable');

  const currentInfo = await evaluate(`(async () => ({
    href: window.location.href,
    workspaceId: typeof window.electronAPI?.getWindowWorkspace === 'function'
      ? await window.electronAPI.getWindowWorkspace()
      : null,
  }))()`);

  const workspaceId = requestedWorkspaceId || currentInfo.workspaceId || '';

  if (route) {
    await evaluate(`(() => {
      const url = new URL(window.location.href);
      ${workspaceId ? `url.searchParams.set('workspaceId', ${JSON.stringify(workspaceId)});` : ''}
      url.searchParams.set('route', ${JSON.stringify(route)});
      window.location.href = url.toString();
      return true;
    })()`);
  }

  await delay(waitMs);

  if (waitFor) {
    const deadline = Date.now() + timeoutMs;
    while (Date.now() < deadline) {
      const found = await evaluate(`document.body?.innerText?.includes(${JSON.stringify(waitFor)})`, false);
      if (found) break;
      await delay(250);
    }
  }

  if (clickText) {
    await evaluate(`(() => {
      const normalized = ${JSON.stringify(clickText)}.trim().toLowerCase();
      const exact = Array.from(document.querySelectorAll('button,[role="button"],a,span,div'))
        .find((el) => (el.textContent || '').trim().toLowerCase() === normalized);
      const partial = Array.from(document.querySelectorAll('button,[role="button"],a,span,div'))
        .find((el) => (el.textContent || '').trim().toLowerCase().includes(normalized));
      const target = exact || partial;
      if (target instanceof HTMLElement) {
        target.click();
        return true;
      }
      return false;
    })()`);
    await delay(500);
  }

  const screenshot = await send('Page.captureScreenshot', { format: 'png' });
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, Buffer.from(screenshot.data, 'base64'));

  const finalInfo = await evaluate(`({
    href: window.location.href,
    title: document.title,
  })`, false);

  console.log(JSON.stringify({
    out,
    route: route || null,
    workspaceId,
    ...finalInfo,
  }, null, 2));

  ws.close();
}

main().catch((error) => {
  console.error(error.message || error);
  process.exit(1);
});
