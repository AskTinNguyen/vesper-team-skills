# Telegram Bot Integration Reference

> Platform-specific implementation guide for Telegram using Grammy.
> Part of the [Messaging Platform Integration](../SKILL.md) skill.

Production-ready patterns for authentication, webhook/polling decisions, message handling, media processing, inline keyboards, reactions, forum topics, and error recovery.

## Prerequisites

- Telegram Bot Token (from @BotFather)
- Node.js 18+ or Bun runtime
- TypeScript project setup
- Understanding of async/await patterns

## Core Dependencies

```json
{
  "dependencies": {
    "grammy": "^1.x",
    "@grammyjs/runner": "^2.x",
    "@grammyjs/transformer-throttler": "^1.x"
  }
}
```

**Why Grammy?**
- Modern TypeScript-first framework
- Built-in middleware system
- Automatic API rate limiting
- Better type safety than node-telegram-bot-api
- Active maintenance and plugin ecosystem

## Authentication & Token Management

### Token Resolution Priority

Implement a cascading token resolution system:

```typescript
// Priority order (highest to lowest):
// 1. Account-specific tokenFile (read from filesystem)
// 2. Account-specific botToken (in config)
// 3. Legacy global tokenFile (default account only)
// 4. Legacy global botToken (default account only)
// 5. Environment variable TELEGRAM_BOT_TOKEN (default account only)

export type TelegramTokenSource = "env" | "tokenFile" | "config" | "none";

export function resolveTelegramToken(
  cfg: Config,
  accountId: string = "default"
): { token: string; source: TelegramTokenSource } {
  const telegramCfg = cfg.channels?.telegram;
  const accountCfg = telegramCfg?.accounts?.[accountId];

  // 1. Account tokenFile
  if (accountCfg?.tokenFile) {
    if (fs.existsSync(accountCfg.tokenFile)) {
      const token = fs.readFileSync(accountCfg.tokenFile, "utf-8").trim();
      if (token) return { token, source: "tokenFile" };
    }
  }

  // 2. Account botToken
  if (accountCfg?.botToken?.trim()) {
    return { token: accountCfg.botToken.trim(), source: "config" };
  }

  // 3-5. Legacy fallbacks (default account only)
  if (accountId === "default") {
    if (telegramCfg?.tokenFile && fs.existsSync(telegramCfg.tokenFile)) {
      const token = fs.readFileSync(telegramCfg.tokenFile, "utf-8").trim();
      if (token) return { token, source: "tokenFile" };
    }

    if (telegramCfg?.botToken?.trim()) {
      return { token: telegramCfg.botToken.trim(), source: "config" };
    }

    const envToken = process.env.TELEGRAM_BOT_TOKEN?.trim();
    if (envToken) return { token: envToken, source: "env" };
  }

  return { token: "", source: "none" };
}
```

### Multi-Account Architecture

Support multiple bot instances within a single application:

```typescript
export type TelegramAccountConfig = {
  enabled?: boolean;
  name?: string;
  botToken?: string;
  tokenFile?: string;
  // All channel-level settings can be overridden per-account
  dmPolicy?: "pairing" | "allowlist" | "open" | "disabled";
  allowFrom?: string[];
  // ... other settings
};

export type ResolvedTelegramAccount = {
  accountId: string;
  enabled: boolean;
  name?: string;
  token: string;
  tokenSource: TelegramTokenSource;
  config: TelegramAccountConfig;
};

export function resolveTelegramAccount(params: {
  cfg: Config;
  accountId?: string;
}): ResolvedTelegramAccount {
  const telegramCfg = params.cfg.channels?.telegram;

  // Determine effective account ID
  let effectiveAccountId = params.accountId || "default";

  // If no explicit account and default has no token, use first configured account
  if (!params.accountId) {
    const defaultToken = resolveTelegramToken(params.cfg, "default");
    if (!defaultToken.token && telegramCfg?.accounts) {
      const firstAccount = Object.keys(telegramCfg.accounts)[0];
      if (firstAccount) effectiveAccountId = firstAccount;
    }
  }

  const accountCfg = telegramCfg?.accounts?.[effectiveAccountId] || {};
  const { token, source } = resolveTelegramToken(params.cfg, effectiveAccountId);

  // Merge base config with account-specific overrides
  const mergedConfig = {
    ...telegramCfg, // base settings
    ...accountCfg,  // account overrides
  };

  return {
    accountId: effectiveAccountId,
    enabled: accountCfg.enabled ?? telegramCfg?.enabled ?? false,
    name: accountCfg.name,
    token,
    tokenSource: source,
    config: mergedConfig,
  };
}
```

## Webhook vs Long Polling Decision Matrix

| Factor | Webhook | Long Polling |
|--------|---------|--------------|
| **Latency** | Lower (instant push) | Higher (polling interval) |
| **Infrastructure** | Requires public HTTPS endpoint | Works anywhere |
| **Scalability** | Better for high traffic | Limited by polling rate |
| **Development** | Complex local setup | Easy local development |
| **Cost** | Server + SSL cert | Minimal |
| **Reliability** | Depends on uptime | Automatic reconnect |
| **Best For** | Production deployments | Development, low traffic |

### Webhook Implementation

```typescript
import { Bot, webhookCallback } from "grammy";
import { createServer } from "node:http";

export async function startTelegramWebhook(opts: {
  token: string;
  path?: string;          // default: "/telegram-webhook"
  port?: number;          // default: 8787
  host?: string;          // default: "0.0.0.0"
  secret?: string;        // webhook secret token
  publicUrl: string;      // e.g., "https://bot.example.com/telegram-webhook"
  healthPath?: string;    // default: "/healthz"
}) {
  const path = opts.path ?? "/telegram-webhook";
  const port = opts.port ?? 8787;
  const host = opts.host ?? "0.0.0.0";
  const healthPath = opts.healthPath ?? "/healthz";

  // 1. Create bot instance
  const bot = createTelegramBot({ token: opts.token });

  // 2. Create webhook callback handler
  const handler = webhookCallback(bot, "http", {
    secretToken: opts.secret,
  });

  // 3. Create HTTP server
  const server = createServer(async (req, res) => {
    // Health check endpoint
    if (req.url === healthPath) {
      res.writeHead(200, { "Content-Type": "text/plain" });
      res.end("OK");
      return;
    }

    // Webhook endpoint
    if (req.url === path && req.method === "POST") {
      await handler(req, res);
      return;
    }

    // 404 for other paths
    res.writeHead(404);
    res.end("Not Found");
  });

  // 4. Register webhook with Telegram
  await bot.api.setWebhook(opts.publicUrl, {
    secret_token: opts.secret,
    allowed_updates: [
      "message",
      "edited_message",
      "callback_query",
      "message_reaction",
    ],
  });

  // 5. Start listening
  await new Promise<void>((resolve) => {
    server.listen(port, host, () => {
      console.log(`Telegram webhook server listening on ${host}:${port}`);
      resolve();
    });
  });

  return { bot, server };
}
```

### Long Polling Implementation

```typescript
import { Bot } from "grammy";

export async function startTelegramPolling(opts: {
  token: string;
}) {
  const bot = createTelegramBot({ token: opts.token });

  // Start long polling
  await bot.start({
    allowed_updates: [
      "message",
      "edited_message",
      "callback_query",
      "message_reaction",
    ],
    onStart: ({ username }) => {
      console.log(`Bot @${username} started with long polling`);
    },
  });

  return { bot };
}
```

## Bot Creation & Middleware Setup

### Core Bot Factory

```typescript
import { Bot } from "grammy";
import { sequentialize } from "@grammyjs/runner";
import { apiThrottler } from "@grammyjs/transformer-throttler";

export function createTelegramBot(opts: {
  token: string;
  proxyFetch?: typeof fetch;
}) {
  // 1. Create Grammy Bot instance
  const clientOptions = opts.proxyFetch
    ? { client: { fetch: opts.proxyFetch } }
    : undefined;

  const bot = new Bot(opts.token, clientOptions);

  // 2. Install API throttler (automatic rate limiting)
  // Handles Telegram limits:
  // - 30 msgs/sec to different chats
  // - 1 msg/sec to same chat
  // - 20 msgs/min to same group
  bot.api.config.use(apiThrottler());

  // 3. Install sequentialize middleware (per-chat ordering)
  bot.use(sequentialize(getTelegramSequentialKey));

  // 4. Install update deduplication
  const recentUpdates = createUpdateDedupe();
  bot.use(async (ctx, next) => {
    const key = buildUpdateKey(ctx);
    if (key && recentUpdates.has(key)) {
      console.log(`Skipping duplicate update: ${key}`);
      return; // Skip duplicate
    }

    await next();

    if (key) recentUpdates.add(key);
  });

  return bot;
}
```

### Sequential Processing Key

**Critical:** Messages from the same chat/topic must be processed in order to prevent race conditions in conversations.

```typescript
export function getTelegramSequentialKey(ctx): string {
  // 1. Reactions use chat ID only (no message context)
  const reaction = ctx.update?.message_reaction;
  if (reaction?.chat?.id) {
    return `telegram:${reaction.chat.id}`;
  }

  // 2. Extract message from various update types
  const msg =
    ctx.message ??
    ctx.update?.message ??
    ctx.update?.edited_message ??
    ctx.update?.callback_query?.message;

  const chatId = msg?.chat?.id ?? ctx.chat?.id;
  const rawText = msg?.text ?? msg?.caption;

  // 3. Control commands get isolated queue (prevents blocking regular messages)
  const isControlCommand = rawText && /^\/(start|help|pause|resume)\b/.test(rawText);
  if (isControlCommand && chatId) {
    return `telegram:${chatId}:control`;
  }

  // 4. Forum topics get isolated queue per thread
  const isForum = msg?.chat?.is_forum;
  const threadId = isForum ? msg?.message_thread_id : undefined;

  if (chatId) {
    return threadId != null
      ? `telegram:${chatId}:topic:${threadId}`
      : `telegram:${chatId}`;
  }

  return "telegram:unknown";
}
```

### Update Deduplication

```typescript
export function createUpdateDedupe() {
  const cache = new Map<string, number>();
  const TTL_MS = 5 * 60_000; // 5 minutes
  const MAX_SIZE = 2000;

  return {
    has(key: string): boolean {
      const timestamp = cache.get(key);
      if (!timestamp) return false;

      if (Date.now() - timestamp > TTL_MS) {
        cache.delete(key);
        return false;
      }

      return true;
    },

    add(key: string): void {
      // Evict oldest entries if cache is full
      if (cache.size >= MAX_SIZE) {
        const firstKey = cache.keys().next().value;
        if (firstKey) cache.delete(firstKey);
      }

      cache.set(key, Date.now());
    },
  };
}

export function buildUpdateKey(ctx): string | null {
  // Dedupe by update_id (numeric sequence from Telegram)
  if (ctx.update?.update_id) {
    return `update:${ctx.update.update_id}`;
  }

  // Dedupe callback queries by callback_id
  if (ctx.callbackQuery?.id) {
    return `callback:${ctx.callbackQuery.id}`;
  }

  // Dedupe messages by chat+message_id
  const msg = ctx.message ?? ctx.update?.message;
  if (msg?.chat?.id && msg?.message_id) {
    return `message:${msg.chat.id}:${msg.message_id}`;
  }

  return null;
}
```

## Message Handling Architecture

### Three-Stage Processing Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ Stage 1: Handler (bot-handlers.ts)                         │
│ - Media group buffering (500ms window)                     │
│ - Text fragment buffering (1.5s window for long pastes)    │
│ - Inbound debouncing (configurable for rapid messages)     │
│ - Access control (group policy, allowlist)                 │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Stage 2: Context Building (bot-message-context.ts)         │
│ - Extract message metadata                                 │
│ - Resolve routing (agent, session key)                     │
│ - Apply DM policy (pairing, allowlist, open, disabled)     │
│ - Apply group mention gating                               │
│ - Build envelope format                                    │
│ - Record inbound session                                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Stage 3: Dispatch (bot-message-dispatch.ts)                │
│ - Create typing callbacks                                  │
│ - Setup draft streaming                                    │
│ - Dispatch to auto-reply system                            │
│ - Deliver replies                                          │
│ - Remove ACK reaction after reply                          │
└─────────────────────────────────────────────────────────────┘
```

### Media Group Buffering

Telegram sends album (multiple photos/videos) as separate messages with the same `media_group_id`. Buffer and combine them:

```typescript
const MEDIA_GROUP_TIMEOUT_MS = 500;

const mediaGroupBuffer = new Map<string, {
  messages: Array<{ msg: Message; ctx: Context }>;
  timer: NodeJS.Timeout;
}>();

bot.on("message", async (ctx) => {
  const msg = ctx.message;
  const mediaGroupId = msg.media_group_id;

  if (mediaGroupId) {
    const existing = mediaGroupBuffer.get(mediaGroupId);

    if (existing) {
      // Append to buffer, reset timer
      clearTimeout(existing.timer);
      existing.messages.push({ msg, ctx });
      existing.timer = setTimeout(() => {
        processMediaGroup(mediaGroupId);
      }, MEDIA_GROUP_TIMEOUT_MS);
    } else {
      // Create new buffer entry
      mediaGroupBuffer.set(mediaGroupId, {
        messages: [{ msg, ctx }],
        timer: setTimeout(() => {
          processMediaGroup(mediaGroupId);
        }, MEDIA_GROUP_TIMEOUT_MS),
      });
    }

    return; // Don't process immediately
  }

  // Single message (no media group)
  await processSingleMessage(ctx);
});

async function processMediaGroup(mediaGroupId: string) {
  const entry = mediaGroupBuffer.get(mediaGroupId);
  if (!entry) return;

  mediaGroupBuffer.delete(mediaGroupId);

  // Sort by message_id to maintain order
  entry.messages.sort((a, b) => a.msg.message_id - b.msg.message_id);

  // Download all media
  const allMedia = await Promise.all(
    entry.messages.map(({ msg }) => downloadMedia(msg))
  );

  // Use caption from first message with caption
  const caption = entry.messages.find(m => m.msg.caption)?.msg.caption;

  // Process as single message with multiple attachments
  await processMessage({
    ctx: entry.messages[0].ctx,
    text: caption,
    media: allMedia,
  });
}
```

### Text Fragment Buffering

Telegram splits long pasted text (>4096 chars) into multiple sequential messages. Buffer and combine:

```typescript
const FRAGMENT_START_THRESHOLD_CHARS = 4000;
const FRAGMENT_MAX_GAP_MS = 1500;
const FRAGMENT_MAX_ID_GAP = 1;
const FRAGMENT_MAX_PARTS = 12;
const FRAGMENT_MAX_TOTAL_CHARS = 50_000;

const textFragmentBuffer = new Map<number, {
  parts: string[];
  lastMessageId: number;
  timer: NodeJS.Timeout;
  chatId: number;
}>();

bot.on("message:text", async (ctx) => {
  const text = ctx.message.text;
  const chatId = ctx.chat.id;
  const messageId = ctx.message.message_id;

  const existing = textFragmentBuffer.get(chatId);

  // Check if this continues an existing fragment
  if (existing) {
    const idGap = messageId - existing.lastMessageId;
    const totalChars = existing.parts.join("").length + text.length;

    const shouldAppend =
      idGap <= FRAGMENT_MAX_ID_GAP &&
      existing.parts.length < FRAGMENT_MAX_PARTS &&
      totalChars <= FRAGMENT_MAX_TOTAL_CHARS;

    if (shouldAppend) {
      // Append to buffer
      clearTimeout(existing.timer);
      existing.parts.push(text);
      existing.lastMessageId = messageId;
      existing.timer = setTimeout(() => {
        flushTextFragments(chatId);
      }, FRAGMENT_MAX_GAP_MS);

      return; // Don't process yet
    } else {
      // Gap too large or limits exceeded, flush existing and start new
      await flushTextFragments(chatId);
    }
  }

  // Start new fragment buffer if text is long enough
  if (text.length >= FRAGMENT_START_THRESHOLD_CHARS) {
    textFragmentBuffer.set(chatId, {
      parts: [text],
      lastMessageId: messageId,
      chatId,
      timer: setTimeout(() => {
        flushTextFragments(chatId);
      }, FRAGMENT_MAX_GAP_MS),
    });

    return; // Wait for potential continuation
  }

  // Regular message
  await processSingleMessage(ctx);
});

async function flushTextFragments(chatId: number) {
  const entry = textFragmentBuffer.get(chatId);
  if (!entry) return;

  textFragmentBuffer.delete(chatId);
  clearTimeout(entry.timer);

  // Combine all fragments
  const combinedText = entry.parts.join("");

  // Process as single message
  await processMessage({
    chatId,
    text: combinedText,
    isCombinedFragment: true,
  });
}
```

### Inbound Debouncing

For rapid text messages from the same user in the same chat, combine them:

```typescript
export function createInboundDebouncer<T>(opts: {
  debounceMs: number;
  buildKey: (entry: T) => string;
  shouldDebounce: (entry: T) => boolean;
  onFlush: (entries: T[]) => Promise<void>;
}) {
  const buffer = new Map<string, {
    entries: T[];
    timer: NodeJS.Timeout;
  }>();

  return {
    async add(entry: T): Promise<void> {
      if (!opts.shouldDebounce(entry)) {
        // Process immediately
        await opts.onFlush([entry]);
        return;
      }

      const key = opts.buildKey(entry);
      const existing = buffer.get(key);

      if (existing) {
        // Append to buffer, reset timer
        clearTimeout(existing.timer);
        existing.entries.push(entry);
        existing.timer = setTimeout(() => {
          flush(key);
        }, opts.debounceMs);
      } else {
        // Create new buffer
        buffer.set(key, {
          entries: [entry],
          timer: setTimeout(() => {
            flush(key);
          }, opts.debounceMs),
        });
      }
    },
  };

  async function flush(key: string) {
    const entry = buffer.get(key);
    if (!entry) return;

    buffer.delete(key);
    clearTimeout(entry.timer);

    await opts.onFlush(entry.entries);
  }
}

// Usage:
const debouncer = createInboundDebouncer({
  debounceMs: 1000, // 1 second
  buildKey: (entry) => `${entry.chatId}:${entry.userId}`,
  shouldDebounce: (entry) => {
    // Don't debounce media or commands
    if (entry.hasMedia) return false;
    if (entry.isCommand) return false;
    return true;
  },
  onFlush: async (entries) => {
    // Combine text messages with newlines
    const combinedText = entries.map(e => e.text).join("\n");
    await processMessage({
      chatId: entries[0].chatId,
      text: combinedText,
    });
  },
});
```

## Access Control Patterns

### DM (Direct Message) Policy

```typescript
export type DMPolicy = "pairing" | "allowlist" | "open" | "disabled";

export async function checkDMAccess(params: {
  chatId: number;
  userId: number;
  username?: string;
  policy: DMPolicy;
  allowFrom: string[];
}): Promise<{ allowed: boolean; reason?: string }> {
  // 1. Disabled: block all DMs
  if (params.policy === "disabled") {
    return { allowed: false, reason: "DM policy is disabled" };
  }

  // 2. Open: allow all DMs
  if (params.policy === "open") {
    return { allowed: true };
  }

  // 3. Allowlist: check if user is in allowFrom
  const hasWildcard = params.allowFrom.includes("*");
  const isAllowed =
    hasWildcard ||
    params.allowFrom.includes(String(params.userId)) ||
    (params.username && params.allowFrom.includes(params.username)) ||
    params.allowFrom.includes(`tg:${params.userId}`);

  if (params.policy === "allowlist") {
    return isAllowed
      ? { allowed: true }
      : { allowed: false, reason: "User not in allowlist" };
  }

  // 4. Pairing: use pairing code system
  if (params.policy === "pairing") {
    if (isAllowed) {
      return { allowed: true };
    }

    // Generate pairing code
    const pairingCode = await generatePairingCode({
      chatId: params.chatId,
      userId: params.userId,
    });

    // Send instructions to user
    await bot.api.sendMessage(params.chatId, [
      "Access not configured.",
      `Your Telegram user ID: ${params.userId}`,
      `Pairing code: ${pairingCode}`,
      "",
      "Ask the bot owner to approve with:",
      `pairing approve telegram ${pairingCode}`,
    ].join("\n"));

    return { allowed: false, reason: "Pairing required" };
  }

  return { allowed: false, reason: "Unknown policy" };
}
```

### Group Policy

```typescript
export type GroupPolicy = "open" | "allowlist" | "disabled";

export function checkGroupAccess(params: {
  chatId: number;
  userId: number;
  username?: string;
  policy: GroupPolicy;
  allowFrom: string[];
}): { allowed: boolean; reason?: string } {
  // 1. Disabled: block all group messages
  if (params.policy === "disabled") {
    return { allowed: false, reason: "Group policy is disabled" };
  }

  // 2. Open: allow all group messages
  if (params.policy === "open") {
    return { allowed: true };
  }

  // 3. Allowlist: sender must be in allowFrom
  const hasWildcard = params.allowFrom.includes("*");
  const isAllowed =
    hasWildcard ||
    params.allowFrom.includes(String(params.userId)) ||
    (params.username && params.allowFrom.includes(params.username)) ||
    params.allowFrom.includes(`tg:${params.userId}`);

  return isAllowed
    ? { allowed: true }
    : { allowed: false, reason: "User not in group allowlist" };
}
```

### Mention Gating

In groups, optionally require bot mention/reply before responding:

```typescript
export function checkMentionGate(params: {
  isGroup: boolean;
  requireMention: boolean;
  wasMentioned: boolean;
  isReplyToBot: boolean;
  isCommand: boolean;
}): { shouldSkip: boolean; reason?: string } {
  // Don't gate DMs
  if (!params.isGroup) {
    return { shouldSkip: false };
  }

  // Don't gate if mention not required
  if (!params.requireMention) {
    return { shouldSkip: false };
  }

  // Allow if bot was mentioned
  if (params.wasMentioned) {
    return { shouldSkip: false };
  }

  // Allow if replying to bot message (implicit mention)
  if (params.isReplyToBot) {
    return { shouldSkip: false };
  }

  // Allow commands through
  if (params.isCommand) {
    return { shouldSkip: false };
  }

  // Skip processing (but record to history for context)
  return { shouldSkip: true, reason: "Mention required but not present" };
}
```

## Media Handling

### Downloading Media

```typescript
export async function getTelegramFile(
  token: string,
  fileId: string
): Promise<{ file_id: string; file_path: string; file_size?: number }> {
  const url = `https://api.telegram.org/bot${token}/getFile?file_id=${encodeURIComponent(fileId)}`;
  const res = await fetch(url);
  const json = await res.json();

  if (!json.ok) {
    throw new Error(`getFile failed: ${json.description}`);
  }

  return json.result;
}

export async function downloadTelegramFile(
  token: string,
  fileInfo: { file_path: string; file_size?: number },
  maxBytes?: number
): Promise<{ buffer: Buffer; mimeType: string }> {
  // Check size limit before downloading
  if (fileInfo.file_size && maxBytes && fileInfo.file_size > maxBytes) {
    const limitMb = Math.round(maxBytes / (1024 * 1024));
    throw new Error(
      `File size ${fileInfo.file_size} bytes exceeds ${limitMb}MB limit`
    );
  }

  // Download file
  const url = `https://api.telegram.org/file/bot${token}/${fileInfo.file_path}`;
  const res = await fetch(url);
  const buffer = Buffer.from(await res.arrayBuffer());

  // Detect MIME type
  const mimeType = res.headers.get("content-type") || "application/octet-stream";

  return { buffer, mimeType };
}

export async function resolveMedia(
  ctx: Context,
  token: string,
  maxBytes?: number
): Promise<{ buffer: Buffer; mimeType: string } | null> {
  const msg = ctx.message;
  if (!msg) return null;

  // Extract file_id from various message types
  let fileId: string | undefined;

  if (msg.photo?.length) {
    // Use largest photo
    const largest = msg.photo.reduce((prev, curr) =>
      curr.file_size > prev.file_size ? curr : prev
    );
    fileId = largest.file_id;
  } else if (msg.video) {
    fileId = msg.video.file_id;
  } else if (msg.audio) {
    fileId = msg.audio.file_id;
  } else if (msg.voice) {
    fileId = msg.voice.file_id;
  } else if (msg.document) {
    fileId = msg.document.file_id;
  } else if (msg.sticker) {
    fileId = msg.sticker.file_id;
  } else if (msg.animation) {
    fileId = msg.animation.file_id;
  } else if (msg.video_note) {
    fileId = msg.video_note.file_id;
  }

  if (!fileId) return null;

  // Get file info and download
  const fileInfo = await getTelegramFile(token, fileId);
  return await downloadTelegramFile(token, fileInfo, maxBytes);
}
```

### Sending Media

```typescript
export async function sendTelegramMedia(params: {
  chatId: number;
  mediaType: "photo" | "video" | "audio" | "voice" | "document";
  file: Buffer | string; // Buffer or file_id
  caption?: string;
  threadId?: number;
}): Promise<Message> {
  const { chatId, mediaType, file, caption, threadId } = params;

  const commonParams = {
    message_thread_id: threadId,
    caption,
    parse_mode: "HTML" as const,
  };

  // Use InputFile for buffers
  const inputFile = Buffer.isBuffer(file)
    ? new InputFile(file)
    : file; // file_id string

  switch (mediaType) {
    case "photo":
      return await bot.api.sendPhoto(chatId, inputFile, commonParams);

    case "video":
      return await bot.api.sendVideo(chatId, inputFile, commonParams);

    case "audio":
      return await bot.api.sendAudio(chatId, inputFile, commonParams);

    case "voice":
      // Voice requires OGG/Opus format
      return await bot.api.sendVoice(chatId, inputFile, commonParams);

    case "document":
      return await bot.api.sendDocument(chatId, inputFile, commonParams);

    default:
      throw new Error(`Unsupported media type: ${mediaType}`);
  }
}
```

### Caption Splitting

Telegram captions are limited to 1024 characters. Split long captions:

```typescript
const TELEGRAM_CAPTION_LIMIT = 1024;

export function splitTelegramCaption(text: string): {
  caption?: string;
  followUpText?: string;
} {
  if (text.length <= TELEGRAM_CAPTION_LIMIT) {
    return { caption: text };
  }

  // Find safe split point (prefer paragraph, sentence, or word boundary)
  let splitIndex = TELEGRAM_CAPTION_LIMIT;

  // Try paragraph boundary
  const paragraphBreak = text.lastIndexOf("\n\n", TELEGRAM_CAPTION_LIMIT);
  if (paragraphBreak > 0 && paragraphBreak >= TELEGRAM_CAPTION_LIMIT * 0.7) {
    splitIndex = paragraphBreak + 2;
  }
  // Try sentence boundary
  else {
    const sentenceEnd = Math.max(
      text.lastIndexOf(". ", TELEGRAM_CAPTION_LIMIT),
      text.lastIndexOf("! ", TELEGRAM_CAPTION_LIMIT),
      text.lastIndexOf("? ", TELEGRAM_CAPTION_LIMIT)
    );
    if (sentenceEnd > 0 && sentenceEnd >= TELEGRAM_CAPTION_LIMIT * 0.7) {
      splitIndex = sentenceEnd + 2;
    }
    // Try word boundary
    else {
      const spaceIndex = text.lastIndexOf(" ", TELEGRAM_CAPTION_LIMIT);
      if (spaceIndex > 0) {
        splitIndex = spaceIndex + 1;
      }
    }
  }

  return {
    caption: text.slice(0, splitIndex).trim(),
    followUpText: text.slice(splitIndex).trim(),
  };
}

// Usage:
async function sendMediaWithLongCaption(params: {
  chatId: number;
  file: Buffer;
  text: string;
  threadId?: number;
}) {
  const { caption, followUpText } = splitTelegramCaption(params.text);

  // Send media with caption (up to 1024 chars)
  await bot.api.sendPhoto(params.chatId, new InputFile(params.file), {
    caption,
    message_thread_id: params.threadId,
    parse_mode: "HTML",
  });

  // Send follow-up text message if needed
  if (followUpText) {
    await bot.api.sendMessage(params.chatId, followUpText, {
      message_thread_id: params.threadId,
      parse_mode: "HTML",
    });
  }
}
```

## Inline Keyboards & Callback Queries

### Sending Inline Buttons

```typescript
import type { InlineKeyboardMarkup, InlineKeyboardButton } from "grammy";

export function buildInlineKeyboard(
  buttons: Array<Array<{ text: string; callback_data: string }>>
): InlineKeyboardMarkup {
  const rows = buttons
    .map(row =>
      row
        .filter(btn => btn?.text && btn?.callback_data)
        .map((btn): InlineKeyboardButton => ({
          text: btn.text,
          callback_data: btn.callback_data,
        }))
    )
    .filter(row => row.length > 0);

  return { inline_keyboard: rows };
}

// Usage:
await bot.api.sendMessage(chatId, "Choose an option:", {
  reply_markup: buildInlineKeyboard([
    [{ text: "✅ Approve", callback_data: "approve" }],
    [{ text: "❌ Reject", callback_data: "reject" }],
    [
      { text: "1️⃣ Option 1", callback_data: "opt1" },
      { text: "2️⃣ Option 2", callback_data: "opt2" },
    ],
  ]),
});
```

### Handling Callback Queries

```typescript
bot.on("callback_query", async (ctx) => {
  const callback = ctx.callbackQuery;

  // CRITICAL: Answer immediately to prevent Telegram retries
  await ctx.answerCallbackQuery().catch(() => {});

  // Extract callback data
  const data = callback.data;
  const chatId = callback.message?.chat?.id;
  const userId = callback.from.id;

  // Apply access control (optional)
  const allowed = checkAccess(userId);
  if (!allowed) {
    await ctx.answerCallbackQuery({
      text: "You don't have permission to use this button.",
      show_alert: true,
    });
    return;
  }

  // Process callback as a synthetic message
  // Treat callback_data as user input
  await processMessage({
    chatId,
    userId,
    text: data,
    isCallback: true,
  });

  // Optionally update the button message
  await ctx.editMessageReplyMarkup({
    inline_keyboard: [], // Remove buttons after click
  });
});
```

### Scope-Based Button Enablement

```typescript
export type InlineButtonsScope = "off" | "dm" | "group" | "all" | "allowlist";

export function shouldEnableInlineButtons(params: {
  scope: InlineButtonsScope;
  isGroup: boolean;
  userId: number;
  allowFrom: string[];
}): boolean {
  if (params.scope === "off") return false;
  if (params.scope === "all") return true;

  if (params.scope === "dm") return !params.isGroup;
  if (params.scope === "group") return params.isGroup;

  if (params.scope === "allowlist") {
    return params.allowFrom.includes(String(params.userId));
  }

  return false;
}
```

## Emoji Reactions

### Sending Reactions

```typescript
export async function reactToMessage(params: {
  chatId: number;
  messageId: number;
  emoji: string;
  remove?: boolean;
}): Promise<void> {
  const reactions = params.remove || !params.emoji.trim()
    ? [] // Empty array removes all reactions
    : [{ type: "emoji", emoji: params.emoji.trim() }];

  await bot.api.setMessageReaction(
    params.chatId,
    params.messageId,
    reactions
  );
}

// Usage:
await reactToMessage({
  chatId: 123456,
  messageId: 789,
  emoji: "👀", // ACK reaction
});

// Remove reaction later:
await reactToMessage({
  chatId: 123456,
  messageId: 789,
  emoji: "👀",
  remove: true,
});
```

### ACK Reaction Pattern

Show users that the bot is processing their message:

```typescript
export async function handleMessageWithAck(ctx: Context) {
  const chatId = ctx.chat.id;
  const messageId = ctx.message.message_id;

  // Add ACK reaction immediately
  const ackPromise = reactToMessage({
    chatId,
    messageId,
    emoji: "👀",
  });

  try {
    // Process message (may take time)
    await processMessage(ctx);

    // Wait for ACK to complete
    await ackPromise;

    // Remove ACK reaction after reply is sent
    await reactToMessage({
      chatId,
      messageId,
      emoji: "👀",
      remove: true,
    });
  } catch (err) {
    // Remove ACK on error
    await ackPromise;
    await reactToMessage({
      chatId,
      messageId,
      emoji: "👀",
      remove: true,
    });

    throw err;
  }
}
```

### Reaction Notifications

Listen for reactions to bot messages:

```typescript
bot.on("message_reaction", async (ctx) => {
  const reaction = ctx.messageReaction;
  const chatId = reaction.chat.id;
  const messageId = reaction.message_id;
  const userId = reaction.user?.id;

  // Check if reaction is on a bot message
  const wasBotMessage = await wasSentByBot(chatId, messageId);
  if (!wasBotMessage) return;

  // Detect added reactions (new_reaction - old_reaction)
  const oldEmojis = new Set(
    reaction.old_reaction.map(r => r.type === "emoji" ? r.emoji : null)
  );
  const addedReactions = reaction.new_reaction.filter(r =>
    r.type === "emoji" && !oldEmojis.has(r.emoji)
  );

  // Process each added reaction
  for (const r of addedReactions) {
    if (r.type === "emoji") {
      console.log(
        `User ${userId} added reaction ${r.emoji} to message ${messageId}`
      );

      // Optional: notify system or trigger action
      await handleReaction({
        chatId,
        messageId,
        emoji: r.emoji,
        userId,
      });
    }
  }
});
```

## Forum Topics (Supergroups)

### Detecting Forum Threads

```typescript
export function resolveTelegramForumThreadId(params: {
  isForum?: boolean;
  messageThreadId?: number;
}): number | undefined {
  // Only use messageThreadId if chat is actually a forum
  if (!params.isForum) return undefined;
  if (typeof params.messageThreadId !== "number") return undefined;

  return params.messageThreadId;
}

// Usage in handler:
bot.on("message", async (ctx) => {
  const isForum = ctx.chat?.is_forum;
  const threadId = resolveTelegramForumThreadId({
    isForum,
    messageThreadId: ctx.message?.message_thread_id,
  });

  console.log(`Message in forum: ${isForum}, thread: ${threadId}`);
});
```

### Thread-Aware Replies

**Critical:** Always include `message_thread_id` when replying in forum topics, or replies will go to the wrong thread.

```typescript
export function buildThreadParams(
  threadId?: number
): { message_thread_id: number } | undefined {
  if (typeof threadId !== "number") return undefined;
  return { message_thread_id: threadId };
}

// Usage:
async function sendReply(params: {
  chatId: number;
  text: string;
  threadId?: number;
}) {
  const threadParams = buildThreadParams(params.threadId);

  await bot.api.sendMessage(params.chatId, params.text, {
    ...threadParams,
    parse_mode: "HTML",
  });
}
```

### Per-Topic Configuration

```typescript
export type TopicConfig = {
  enabled?: boolean;
  requireMention?: boolean;
  allowFrom?: string[];
  systemPrompt?: string;
  skills?: string[];
};

export type GroupConfig = {
  enabled?: boolean;
  requireMention?: boolean;
  allowFrom?: string[];
  systemPrompt?: string;
  skills?: string[];
  topics?: Record<string, TopicConfig>;
};

export function resolveTopicConfig(params: {
  chatId: number;
  threadId?: number;
  groupConfig?: Record<string, GroupConfig>;
}): TopicConfig | undefined {
  const group = params.groupConfig?.[String(params.chatId)];
  if (!group || !params.threadId) return undefined;

  return group.topics?.[String(params.threadId)];
}

// Resolution order (most specific wins):
export function resolveEffectiveSetting<T>(
  topicSetting: T | undefined,
  groupSetting: T | undefined,
  accountSetting: T | undefined,
  channelSetting: T | undefined,
  defaultValue: T
): T {
  return (
    topicSetting ??
    groupSetting ??
    accountSetting ??
    channelSetting ??
    defaultValue
  );
}
```

## Markdown & Formatting

### Telegram HTML Conversion

Telegram supports a subset of HTML. Convert Markdown to Telegram-safe HTML:

```typescript
export function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

export function markdownToTelegramHtml(markdown: string): string {
  let html = markdown;

  // Bold: **text** or __text__ -> <b>text</b>
  html = html.replace(/\*\*(.+?)\*\*/g, "<b>$1</b>");
  html = html.replace(/__(.+?)__/g, "<b>$1</b>");

  // Italic: *text* or _text_ -> <i>text</i>
  html = html.replace(/\*(.+?)\*/g, "<i>$1</i>");
  html = html.replace(/_(.+?)_/g, "<i>$1</i>");

  // Code: `text` -> <code>text</code>
  html = html.replace(/`(.+?)`/g, "<code>$1</code>");

  // Code block: ```text``` -> <pre><code>text</code></pre>
  html = html.replace(/```([\s\S]+?)```/g, "<pre><code>$1</code></pre>");

  // Links: [text](url) -> <a href="url">text</a>
  html = html.replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2">$1</a>');

  // Strikethrough: ~~text~~ -> <s>text</s>
  html = html.replace(/~~(.+?)~~/g, "<s>$1</s>");

  return html;
}

// Supported Telegram HTML tags:
// <b>, <strong>, <i>, <em>, <u>, <s>, <strike>, <del>
// <code>, <pre>
// <a href="...">
// <tg-spoiler>, <tg-emoji emoji-id="...">
```

### Message Chunking

Telegram messages are limited to 4096 characters. Split long messages:

```typescript
const TELEGRAM_MESSAGE_LIMIT = 4096;

export function chunkTelegramMessage(text: string): string[] {
  if (text.length <= TELEGRAM_MESSAGE_LIMIT) {
    return [text];
  }

  const chunks: string[] = [];
  let remaining = text;

  while (remaining.length > 0) {
    if (remaining.length <= TELEGRAM_MESSAGE_LIMIT) {
      chunks.push(remaining);
      break;
    }

    // Find safe split point
    let splitIndex = TELEGRAM_MESSAGE_LIMIT;

    // Try to split at paragraph boundary
    const paragraphBreak = remaining.lastIndexOf("\n\n", TELEGRAM_MESSAGE_LIMIT);
    if (paragraphBreak > TELEGRAM_MESSAGE_LIMIT * 0.7) {
      splitIndex = paragraphBreak + 2;
    }
    // Try to split at sentence boundary
    else {
      const sentenceEnd = Math.max(
        remaining.lastIndexOf(". ", TELEGRAM_MESSAGE_LIMIT),
        remaining.lastIndexOf("! ", TELEGRAM_MESSAGE_LIMIT),
        remaining.lastIndexOf("? ", TELEGRAM_MESSAGE_LIMIT)
      );
      if (sentenceEnd > TELEGRAM_MESSAGE_LIMIT * 0.7) {
        splitIndex = sentenceEnd + 2;
      }
      // Split at word boundary
      else {
        const spaceIndex = remaining.lastIndexOf(" ", TELEGRAM_MESSAGE_LIMIT);
        if (spaceIndex > 0) {
          splitIndex = spaceIndex + 1;
        }
      }
    }

    chunks.push(remaining.slice(0, splitIndex).trim());
    remaining = remaining.slice(splitIndex);
  }

  return chunks;
}

// Usage:
async function sendLongMessage(chatId: number, text: string) {
  const chunks = chunkTelegramMessage(text);

  for (const chunk of chunks) {
    await bot.api.sendMessage(chatId, chunk, {
      parse_mode: "HTML",
    });
  }
}
```

## Error Handling & Flood Limits

### Retry Policy

```typescript
export type RetryConfig = {
  maxAttempts: number;
  delayMs: number;
  backoffFactor: number;
};

export function createRetryRunner(config: RetryConfig) {
  return async function retry<T>(
    fn: () => Promise<T>,
    label: string
  ): Promise<T> {
    let lastError: unknown;

    for (let attempt = 1; attempt <= config.maxAttempts; attempt++) {
      try {
        return await fn();
      } catch (err) {
        lastError = err;

        if (attempt < config.maxAttempts) {
          const delayMs = config.delayMs * Math.pow(config.backoffFactor, attempt - 1);
          console.warn(
            `[telegram:${label}] retry ${attempt}/${config.maxAttempts} after ${delayMs}ms`
          );
          await new Promise(resolve => setTimeout(resolve, delayMs));
        }
      }
    }

    throw lastError;
  };
}

// Usage:
const retry = createRetryRunner({
  maxAttempts: 3,
  delayMs: 1000,
  backoffFactor: 2,
});

await retry(async () => {
  return await bot.api.sendMessage(chatId, text);
}, "sendMessage");
```

### Grammy Throttler

Grammy's throttler automatically handles Telegram API rate limits:

```typescript
import { apiThrottler } from "@grammyjs/transformer-throttler";

bot.api.config.use(apiThrottler());

// Automatically handles:
// - 30 messages/second to different chats
// - 1 message/second to same chat
// - 20 messages/minute to same group
// Requests exceeding limits are queued and retried
```

### Common Error Patterns

```typescript
export function handleTelegramError(err: unknown, context: string): Error {
  const message = String(err);

  // Chat not found
  if (/400: Bad Request: chat not found/i.test(message)) {
    return new Error([
      `Telegram ${context} failed: chat not found.`,
      "Possible causes:",
      "1. User hasn't started bot (DM requires /start first)",
      "2. Bot removed from group",
      "3. Group migrated to supergroup (chat ID changed)",
      "4. Wrong bot token",
    ].join(" "));
  }

  // Bot blocked by user
  if (/403: Forbidden: bot was blocked by the user/i.test(message)) {
    return new Error(`Telegram ${context} failed: bot blocked by user`);
  }

  // Invalid file_id
  if (/400: Bad Request: wrong file identifier/i.test(message)) {
    return new Error(`Telegram ${context} failed: invalid file_id`);
  }

  // Message to delete not found
  if (/400: Bad Request: message to delete not found/i.test(message)) {
    return new Error(`Telegram ${context} failed: message already deleted`);
  }

  // Message can't be edited
  if (/400: Bad Request: message can't be edited/i.test(message)) {
    return new Error(`Telegram ${context} failed: message too old to edit`);
  }

  // Parse error (malformed HTML)
  if (/400: Bad Request: can't parse entities/i.test(message)) {
    return new Error(`Telegram ${context} failed: malformed HTML formatting`);
  }

  return err instanceof Error ? err : new Error(String(err));
}

// Usage with fallback to plain text:
async function sendMessage(chatId: number, text: string) {
  const html = markdownToTelegramHtml(text);

  try {
    return await bot.api.sendMessage(chatId, html, {
      parse_mode: "HTML",
    });
  } catch (err) {
    // Fallback to plain text on parse error
    if (/can't parse entities/i.test(String(err))) {
      console.warn("HTML parse error, falling back to plain text");
      return await bot.api.sendMessage(chatId, text);
    }

    throw handleTelegramError(err, "sendMessage");
  }
}
```

## Group Migration Handling

When a Telegram group is upgraded to a supergroup, the chat ID changes from positive to negative (starting with `-100`). Handle this automatically:

```typescript
bot.on("message:migrate_to_chat_id", async (ctx) => {
  const msg = ctx.message;
  const oldChatId = String(msg.chat.id);
  const newChatId = String(msg.migrate_to_chat_id);

  console.log(`Group migrated: ${oldChatId} → ${newChatId}`);

  // Migrate config automatically
  await migrateGroupConfig({
    oldChatId,
    newChatId,
  });
});

export async function migrateGroupConfig(params: {
  oldChatId: string;
  newChatId: string;
}): Promise<{ migrated: boolean; skippedExisting: boolean }> {
  const config = await loadConfig();
  const groups = config.telegram?.groups;

  if (!groups) {
    return { migrated: false, skippedExisting: false };
  }

  const oldConfig = groups[params.oldChatId];
  if (!oldConfig) {
    return { migrated: false, skippedExisting: false };
  }

  // Don't overwrite existing config for new chat ID
  if (groups[params.newChatId]) {
    console.warn(
      `Config already exists for new chat ID ${params.newChatId}, skipping migration`
    );
    return { migrated: false, skippedExisting: true };
  }

  // Copy old config to new chat ID
  groups[params.newChatId] = { ...oldConfig };

  // Optionally delete old config
  delete groups[params.oldChatId];

  // Save config
  await saveConfig(config);

  console.log(`Group config migrated successfully`);
  return { migrated: true, skippedExisting: false };
}
```

## Testing & Probing

### Channel Probe

Verify bot credentials and retrieve bot info:

```typescript
export async function probeTelegramChannel(params: {
  token: string;
}): Promise<{
  ok: true;
  botInfo: {
    id: number;
    username: string;
    first_name: string;
    can_join_groups: boolean;
    can_read_all_group_messages: boolean;
    supports_inline_queries: boolean;
  };
}> {
  const bot = new Bot(params.token);

  try {
    const me = await bot.api.getMe();

    return {
      ok: true,
      botInfo: {
        id: me.id,
        username: me.username,
        first_name: me.first_name,
        can_join_groups: me.can_join_groups,
        can_read_all_group_messages: me.can_read_all_group_messages,
        supports_inline_queries: me.supports_inline_queries,
      },
    };
  } catch (err) {
    throw new Error(`Bot probe failed: ${String(err)}`);
  }
}

// Usage:
const probe = await probeTelegramChannel({ token: "YOUR_BOT_TOKEN" });
console.log(`Bot @${probe.botInfo.username} is ready`);
```

## Common Pitfalls & Solutions

### Pitfall 1: Processing Media Groups Immediately

**Problem:** Processing each photo in an album as a separate message.

**Solution:** Buffer messages with the same `media_group_id` for 500ms, then process as a single message with multiple attachments.

### Pitfall 2: Missing `message_thread_id` in Forum Replies

**Problem:** Replies go to the wrong thread in forum groups.

**Solution:** Always include `message_thread_id` when replying in forums. Store it from the inbound message.

### Pitfall 3: Not Handling Group Migration

**Problem:** Bot stops working after group upgrade to supergroup.

**Solution:** Listen for `message:migrate_to_chat_id` event and migrate config/data to new chat ID.

### Pitfall 4: Exceeding Caption Limit

**Problem:** 400 error when caption exceeds 1024 characters.

**Solution:** Split caption: send media with first 1024 chars, then send follow-up text message with remainder.

### Pitfall 5: Ignoring Rate Limits

**Problem:** 429 Too Many Requests errors.

**Solution:** Use Grammy's `apiThrottler()` middleware to automatically queue and throttle requests.

### Pitfall 6: Not Answering Callback Queries

**Problem:** Telegram retries callback queries, causing duplicate processing.

**Solution:** Call `answerCallbackQuery()` immediately, before processing the callback.

### Pitfall 7: Blocking DMs Before /start

**Problem:** Bot can't send DMs to users who haven't started the bot.

**Solution:** Detect "chat not found" errors and provide clear instructions to users.

### Pitfall 8: Race Conditions in Conversations

**Problem:** Messages processed out of order, causing context confusion.

**Solution:** Use `sequentialize()` middleware with per-chat keys to ensure sequential processing.

### Pitfall 9: Voice Message Format Issues

**Problem:** Voice messages sent as audio files instead of voice bubbles.

**Solution:** Voice bubbles require OGG container with Opus codec. Use `sendVoice()` with proper format, or fall back to `sendAudio()`.

### Pitfall 10: Malformed HTML Formatting

**Problem:** 400 error: "can't parse entities".

**Solution:** Properly escape HTML entities (`<`, `>`, `&`). Implement fallback to plain text on parse errors.

## Configuration Reference

```yaml
channels:
  telegram:
    # Global settings
    enabled: true

    # DM policy: "pairing" (default), "allowlist", "open", "disabled"
    dmPolicy: "pairing"

    # Group policy: "open" (default), "allowlist", "disabled"
    groupPolicy: "open"

    # Allowlist for DMs (user IDs, usernames, or "tg:123456" format)
    allowFrom: ["*"]  # Wildcard allows all

    # Allowlist for groups (defaults to allowFrom)
    groupAllowFrom: ["admin_username", "123456"]

    # Media download limit (MB)
    mediaMaxMb: 5

    # Message history limit for groups
    historyLimit: 10

    # Reply threading: "first", "last", "none"
    replyToMode: "first"

    # Reaction settings
    reactionNotifications: "own"  # "off", "own", "all"
    reactionLevel: "ack"          # "off", "ack", "minimal", "extensive"

    # Inline buttons scope
    capabilities:
      inlineButtons: "allowlist"  # "off", "dm", "group", "all", "allowlist"

    # Retry policy
    retry:
      maxAttempts: 3
      delayMs: 1000
      backoffFactor: 2

    # Multi-account support
    accounts:
      default:
        enabled: true
        name: "Main Bot"
        botToken: "YOUR_BOT_TOKEN"
        # OR use tokenFile:
        # tokenFile: "/path/to/token"

      secondary:
        enabled: true
        name: "Admin Bot"
        botToken: "ANOTHER_BOT_TOKEN"
        dmPolicy: "allowlist"
        allowFrom: ["admin_user"]

    # Per-group configuration
    groups:
      "-1001234567890":
        enabled: true
        requireMention: true
        allowFrom: ["team_member1", "team_member2"]
        systemPrompt: "You are a helpful assistant in the Engineering group."
        skills: ["code-review", "documentation"]

        # Per-topic configuration (forum groups)
        topics:
          "123":
            enabled: true
            requireMention: false
            systemPrompt: "You are answering general questions."
            skills: ["general", "faq"]

          "456":
            enabled: true
            requireMention: true
            systemPrompt: "You are providing technical support."
            skills: ["support", "troubleshooting"]
```

## Integration Patterns

### Pattern 1: Simple Bot

```typescript
// Minimal long-polling bot
const bot = createTelegramBot({ token: process.env.TELEGRAM_BOT_TOKEN! });

bot.on("message:text", async (ctx) => {
  const text = ctx.message.text;
  const reply = await processMessage(text);
  await ctx.reply(reply);
});

await bot.start();
```

### Pattern 2: Webhook Deployment (Production)

```typescript
// Production webhook setup
await startTelegramWebhook({
  token: process.env.TELEGRAM_BOT_TOKEN!,
  publicUrl: "https://bot.example.com/telegram-webhook",
  port: 8787,
  secret: process.env.WEBHOOK_SECRET,
  healthPath: "/healthz",
});
```

### Pattern 3: Multi-Account Routing

```typescript
// Route messages to different handlers based on account
const accounts = {
  main: createTelegramBot({ token: process.env.MAIN_BOT_TOKEN! }),
  support: createTelegramBot({ token: process.env.SUPPORT_BOT_TOKEN! }),
};

accounts.main.on("message", async (ctx) => {
  await handleCustomerMessage(ctx);
});

accounts.support.on("message", async (ctx) => {
  await handleSupportMessage(ctx);
});

// Start all bots
await Promise.all([
  accounts.main.start(),
  accounts.support.start(),
]);
```

### Pattern 4: Forum Group with Per-Topic Handlers

```typescript
bot.on("message", async (ctx) => {
  const isForum = ctx.chat?.is_forum;
  const threadId = resolveTelegramForumThreadId({
    isForum,
    messageThreadId: ctx.message?.message_thread_id,
  });

  if (threadId === 123) {
    // General topic - always respond
    await handleGeneralMessage(ctx);
  } else if (threadId === 456) {
    // Support topic - require mention
    const wasMentioned = ctx.message?.entities?.some(
      e => e.type === "mention" || e.type === "text_mention"
    );

    if (wasMentioned) {
      await handleSupportMessage(ctx);
    }
  }
});
```

## Summary

This skill provides a comprehensive guide to implementing production-ready Telegram bot integrations using Grammy. Key takeaways:

1. **Use Grammy framework** for modern TypeScript support and built-in middleware
2. **Implement proper authentication** with multi-account support and cascading token resolution
3. **Choose deployment mode wisely**: webhooks for production, long polling for development
4. **Handle buffering correctly**: media groups (500ms), text fragments (1.5s), inbound debouncing
5. **Implement access control layers**: DM policy, group policy, mention gating, per-group allowlists
6. **Process messages sequentially** per chat/topic to prevent race conditions
7. **Handle media properly**: download with size limits, send with caption splitting
8. **Support interactive features**: inline keyboards, reactions, forum topics
9. **Implement robust error handling**: retries, rate limiting, parse error fallbacks
10. **Handle group migration** automatically to prevent broken configs

Reference the Clawdbot implementation at `/Users/tinnguyen/clawd/src/telegram/` for production-proven patterns.

## Reference Files

- Compound doc: `/Users/tinnguyen/clawd/docs/solutions/integration-architecture/telegram-integration-patterns-20260125.md`
- Bot creation: `/Users/tinnguyen/clawd/src/telegram/bot.ts`
- Message handlers: `/Users/tinnguyen/clawd/src/telegram/bot-handlers.ts`
- Token resolution: `/Users/tinnguyen/clawd/src/telegram/token.ts`
- Account management: `/Users/tinnguyen/clawd/src/telegram/accounts.ts`
- Send implementation: `/Users/tinnguyen/clawd/src/telegram/send.ts`
