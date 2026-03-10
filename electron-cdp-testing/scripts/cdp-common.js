#!/usr/bin/env node

const fs = require('fs');
const http = require('http');
const { createRequire } = require('module');
const path = require('path');

let WebSocketImpl = null;

try {
  const cwdRequire = createRequire(path.join(process.cwd(), 'package.json'));
  WebSocketImpl = cwdRequire('ws');
} catch (error) {
  WebSocketImpl = null;
}

if (!WebSocketImpl) {
  WebSocketImpl = globalThis.WebSocket || null;
}

if (!WebSocketImpl) {
  try {
    WebSocketImpl = require('ws');
  } catch (error) {
    throw new Error(
      'No WebSocket client available. Install the "ws" package in the current workspace or use Node.js 22+.'
    );
  }
}

function addWsListener(ws, event, handler) {
  if (typeof ws.on === 'function') {
    ws.on(event, handler);
    return () => {
      if (typeof ws.off === 'function') {
        ws.off(event, handler);
      }
    };
  }

  ws.addEventListener(event, handler);
  return () => ws.removeEventListener(event, handler);
}

function getMessagePayload(eventOrData) {
  if (eventOrData && typeof eventOrData === 'object' && 'data' in eventOrData) {
    return eventOrData.data;
  }
  return eventOrData;
}

const DEFAULT_PORT = 9222;
const DEFAULT_TITLE_PATTERN = 'Vesper';

function parseArgs(argv) {
  const args = argv.slice(2);
  const options = {
    args,
    port: DEFAULT_PORT,
    titlePattern: process.env.CDP_TITLE_PATTERN || DEFAULT_TITLE_PATTERN,
  };

  if (args.includes('--port')) {
    const value = Number.parseInt(args[args.indexOf('--port') + 1], 10);
    if (Number.isFinite(value)) options.port = value;
  }

  if (args.includes('--title-pattern')) {
    const value = args[args.indexOf('--title-pattern') + 1];
    if (value) options.titlePattern = value;
  }

  return options;
}

async function getTargets(port) {
  return new Promise((resolve, reject) => {
    const request = http.get(`http://127.0.0.1:${port}/json`, (response) => {
      if (response.statusCode !== 200) {
        reject(
          new Error(
            `CDP not available on port ${port}. In Vesper, source scripts/detect-instance.sh and relaunch Electron with --remote-debugging-port=9222.`
          )
        );
        response.resume();
        return;
      }

      let body = '';
      response.setEncoding('utf8');
      response.on('data', (chunk) => {
        body += chunk;
      });
      response.on('end', () => {
        try {
          resolve(JSON.parse(body));
        } catch (error) {
          reject(new Error(`Could not parse CDP target list: ${error.message}`));
        }
      });
    });

    request.on('error', (error) => {
      reject(new Error(`Could not reach CDP on port ${port}: ${error.message}`));
    });
  });
}

function isUsablePageTarget(target) {
  return target.type === 'page' && !String(target.title || '').includes('DevTools');
}

function findMainPage(targets, titlePattern = DEFAULT_TITLE_PATTERN) {
  const usableTargets = targets.filter(isUsablePageTarget);
  if (usableTargets.length === 0) return null;

  const preferred = usableTargets.find((target) =>
    String(target.title || '').includes(titlePattern)
  );

  return preferred || usableTargets[0];
}

function listTargets(targets) {
  return targets.map((target) => ({
    id: target.id,
    type: target.type,
    title: target.title || '',
    url: target.url || '',
  }));
}

async function connectToPage(wsUrl) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocketImpl(wsUrl);
    const timer = setTimeout(() => reject(new Error('Connection timeout')), 5000);

    addWsListener(ws, 'open', () => {
      clearTimeout(timer);
      resolve(ws);
    });
    addWsListener(ws, 'error', (error) => {
      clearTimeout(timer);
      reject(error);
    });
  });
}

function send(ws, method, params = {}, timeoutMs = 10000) {
  return new Promise((resolve, reject) => {
    const id = Date.now() + Math.floor(Math.random() * 1000);
    const timer = setTimeout(() => {
      removeListener();
      reject(new Error(`Timeout waiting for ${method}`));
    }, timeoutMs);

    const handler = (eventOrData) => {
      const result = JSON.parse(getMessagePayload(eventOrData));
      if (result.id !== id) return;
      removeListener();
      clearTimeout(timer);
      if (result.error) {
        reject(new Error(result.error.message));
      } else {
        resolve(result.result);
      }
    };

    const removeListener = addWsListener(ws, 'message', handler);
    ws.send(JSON.stringify({ id, method, params }));
  });
}

async function prepareSession(ws) {
  await send(ws, 'Runtime.enable');
  await send(ws, 'Page.enable');
}

async function evaluate(ws, expression, awaitPromise = false) {
  const result = await send(ws, 'Runtime.evaluate', {
    expression,
    awaitPromise,
    returnByValue: true,
  });

  if (result.exceptionDetails) {
    throw new Error(result.exceptionDetails.text || 'Evaluation failed');
  }

  return result.result ? result.result.value : undefined;
}

async function takeScreenshot(ws, outputPath) {
  const result = await send(ws, 'Page.captureScreenshot', { format: 'png' }, 30000);
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, Buffer.from(result.data, 'base64'));
  return outputPath;
}

function resolveOutputPath(outputPath, fallbackName) {
  if (outputPath) return path.resolve(outputPath);
  return path.resolve(process.cwd(), fallbackName);
}

module.exports = {
  DEFAULT_PORT,
  DEFAULT_TITLE_PATTERN,
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
};
