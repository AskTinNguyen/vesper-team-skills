# Slack Integration Reference

> Platform-specific implementation guide for Slack using @slack/bolt.
> Part of the [Messaging Platform Integration](../SKILL.md) skill.

Production-ready patterns for OAuth flows, Socket Mode vs Events API, message handling, threading, interactive components, slash commands, and error handling.

## Architecture Overview

### Foundation: Slack Bolt Framework

Use `@slack/bolt` as your foundation. It provides:
- Event handling abstraction
- Socket Mode and HTTP receiver support
- Built-in retry logic and error handling
- OAuth flow helpers

```typescript
import { App } from "@slack/bolt";
import { WebClient } from "@slack/web-api";
```

### Token Types

Slack uses two distinct token types:

1. **Bot Token** (`xoxb-...`):
   - Required for all operations
   - Authenticates the bot user
   - Used with Web API client
   - Scopes determine permissions

2. **App Token** (`xapp-...`):
   - Required for Socket Mode only
   - WebSocket connection authentication
   - Format: `xapp-{number}-{APP_ID}-{random}`
   - Not needed for HTTP mode

**Token Normalization Pattern**:
```typescript
export function normalizeSlackToken(raw?: string): string | undefined {
  const trimmed = raw?.trim();
  return trimmed ? trimmed : undefined;
}
```

**App ID Extraction** (for validation):
```typescript
function parseApiAppIdFromAppToken(raw?: string): string | undefined {
  const token = raw?.trim();
  if (!token) return undefined;
  const match = /^xapp-\d-([a-z0-9]+)-/i.exec(token);
  return match?.[1]?.toUpperCase();
}
```

## Connection Modes: Decision Matrix

### Socket Mode (WebSocket-Based)

**Use When**:
- Developing locally without public endpoints
- Building internal tools behind firewalls
- No infrastructure for webhook hosting
- Want simplest deployment

**Requirements**:
- Bot token (`xoxb-...`)
- App token (`xapp-...`)
- No public endpoint needed

**Setup**:
```typescript
const app = new App({
  token: botToken,
  appToken,
  socketMode: true,
  clientOptions: {
    retryConfig: {
      retries: 2,
      factor: 2,           // Exponential backoff
      minTimeout: 500,
      maxTimeout: 3000,
      randomize: true      // Jitter to prevent thundering herd
    }
  }
});

await app.start();  // Opens WebSocket connection
```

**Pros**:
- No webhook infrastructure needed
- Works behind NAT/firewalls
- Simpler local development

**Cons**:
- Requires persistent connection
- App token management overhead
- Not suitable for serverless

### HTTP Mode (Webhook-Based)

**Use When**:
- Deploying to production with public endpoints
- Using serverless/function-as-a-service
- Need horizontal scaling
- Want standard HTTP architecture

**Requirements**:
- Bot token (`xoxb-...`)
- Signing secret (for request verification)
- Public HTTPS endpoint

**Setup**:
```typescript
import { HTTPReceiver } from "@slack/bolt";

const receiver = new HTTPReceiver({
  signingSecret,
  endpoints: webhookPath  // Default: "/slack/events"
});

const app = new App({
  token: botToken,
  receiver,
  clientOptions: {
    retryConfig: {
      retries: 2,
      factor: 2,
      minTimeout: 500,
      maxTimeout: 3000,
      randomize: true
    }
  }
});

// Register with your HTTP framework
registerHttpHandler({
  path: webhookPath,
  handler: async (req, res) => {
    await receiver.requestListener(req, res);
  }
});
```

**Pros**:
- Stateless, scales horizontally
- Standard HTTP patterns
- Works with serverless

**Cons**:
- Requires public HTTPS endpoint
- Need to manage webhook routing
- Request verification overhead

## Multi-Account Architecture

Support multiple Slack workspaces from day one. Retrofitting is painful.

### Account Resolution Pattern

```typescript
export type ResolvedSlackAccount = {
  accountId: string;
  enabled: boolean;
  name?: string;
  botToken?: string;
  appToken?: string;
  botTokenSource: "env" | "config" | "none";
  appTokenSource: "env" | "config" | "none";
  config: SlackAccountConfig;
};

// Token resolution hierarchy:
// 1. Explicit parameter
// 2. Account-specific config
// 3. Environment variables (default account only!)
// 4. Error

function resolveToken(params: {
  explicit?: string;
  accountId: string;
  configToken?: string;
  configSource: "env" | "config" | "none";
}): string {
  if (params.explicit) return params.explicit;

  if (params.configToken) {
    if (params.configSource === "config") return params.configToken;
    if (params.configSource === "env" && params.accountId === "default") {
      return params.configToken;
    }
  }

  throw new Error(`No token found for account ${params.accountId}`);
}
```

**Critical Pattern**: Only the default account can use environment variables. All other accounts must specify tokens in configuration.

### HTTP Mode Multi-Account Routing

```typescript
// Global route registry
const slackHttpRoutes = new Map<string, SlackHttpRequestHandler>();

export function registerSlackHttpHandler(params: {
  path?: string | null;
  handler: SlackHttpRequestHandler;
  accountId?: string;
}): () => void {
  const normalizedPath = normalizeWebhookPath(params.path);
  slackHttpRoutes.set(normalizedPath, params.handler);

  // Return cleanup function
  return () => slackHttpRoutes.delete(normalizedPath);
}
```

## OAuth & App Installation

### Scopes You'll Need

**Bot Token Scopes** (minimum):
- `chat:write` - Send messages
- `channels:read` - List public channels
- `groups:read` - List private channels
- `users:read` - Get user info
- `im:read` - List DM channels
- `im:history` - Read DM messages

**Common Additional Scopes**:
- `chat:write.customize` - Custom bot name/icon
- `reactions:read` / `reactions:write` - Reaction support
- `pins:read` / `pins:write` - Pin messages
- `files:write` - Upload files
- `commands` - Slash commands

**Socket Mode Scopes** (app-level):
- `connections:write` - WebSocket connection

### Scope Detection (for health checks)

```typescript
export async function fetchSlackScopes(
  token: string,
  timeoutMs: number
): Promise<{ scopes: string[]; ok: boolean }> {
  const client = new WebClient(token, {
    retryConfig: { retries: 1, minTimeout: 500, maxTimeout: 2000 }
  });

  try {
    // Primary method
    const result = await client.auth.scopes({ token });
    if (result.scopes) {
      return { ok: true, scopes: parseScopes(result.scopes) };
    }
  } catch {
    // Fallback method
    try {
      const result = await client.apps.permissions.info();
      if (result.info?.app?.scopes) {
        return { ok: true, scopes: parseScopes(result.info.app.scopes) };
      }
    } catch {
      // Fall through
    }
  }

  return { ok: false, scopes: [] };
}

function parseScopes(raw: string | string[]): string[] {
  if (Array.isArray(raw)) return raw;
  return raw.split(",").map(s => s.trim()).filter(Boolean);
}
```

## Event Handling Architecture

### Event Registration Pattern

Separate concerns: registration → handling → preparation → dispatch

```typescript
export function registerSlackEvents(params: {
  app: App;
  handlers: {
    onMessage: SlackMessageHandler;
    onReaction: SlackReactionHandler;
    onMemberChange: SlackMemberHandler;
    onChannelChange: SlackChannelHandler;
    onPin: SlackPinHandler;
  };
}) {
  registerMessageEvents({ app: params.app, handler: params.handlers.onMessage });
  registerReactionEvents({ app: params.app, handler: params.handlers.onReaction });
  registerMemberEvents({ app: params.app, handler: params.handlers.onMemberChange });
  registerChannelEvents({ app: params.app, handler: params.handlers.onChannelChange });
  registerPinEvents({ app: params.app, handler: params.handlers.onPin });
}
```

### Message Events

Handle multiple message subtypes correctly:

```typescript
export function registerMessageEvents(params: {
  app: App;
  handler: SlackMessageHandler;
}) {
  // Standard messages
  params.app.event("message", async ({ event }) => {
    const message = event as SlackMessageEvent;

    // Filter unwanted subtypes
    const allowedSubtypes = [undefined, "file_share", "bot_message"];
    if (message.subtype && !allowedSubtypes.includes(message.subtype)) {
      return;
    }

    await params.handler(message, { source: "message" });
  });

  // App mentions (always process)
  params.app.event("app_mention", async ({ event }) => {
    await params.handler(event as SlackMessageEvent, {
      source: "app_mention",
      wasMentioned: true
    });
  });
}
```

**Important Subtypes to Handle**:

- `message_changed`: Message edited
- `message_deleted`: Message deleted
- `thread_broadcast`: Thread reply broadcast to channel
- `file_share`: File attachment
- `bot_message`: Bot-sent message

### Reaction Events

Unified handler for add/remove:

```typescript
export function registerReactionEvents(params: {
  app: App;
  handler: (event: SlackReactionEvent, action: "added" | "removed") => Promise<void>;
}) {
  const handleReaction = async (
    event: SlackReactionEvent,
    action: "added" | "removed"
  ) => {
    // Only handle message reactions
    if (event.item?.type !== "message") return;

    await params.handler(event, action);
  };

  params.app.event("reaction_added", async ({ event }) => {
    await handleReaction(event, "added");
  });

  params.app.event("reaction_removed", async ({ event }) => {
    await handleReaction(event, "removed");
  });
}
```

## Message Processing Pipeline

Implement a staged pipeline: Debounce → Thread Resolution → Prepare → Dispatch

### Deduplication

Prevent double-processing on event retries:

```typescript
const seenMessages = new Map<string, Set<string>>();

function markMessageSeen(channelId: string, messageTs?: string): boolean {
  if (!messageTs) return false;

  const key = `${channelId}:${messageTs}`;
  if (!seenMessages.has(channelId)) {
    seenMessages.set(channelId, new Set());
  }

  const channelSeen = seenMessages.get(channelId)!;
  if (channelSeen.has(messageTs)) return true;  // Already seen

  channelSeen.add(messageTs);
  return false;  // First time
}
```

### Thread Resolution

**Problem**: Slack sometimes omits `thread_ts` on thread replies, but includes `parent_user_id`.

**Solution**: Fetch parent message to get missing `thread_ts`:

```typescript
export function createThreadTsResolver(client: WebClient) {
  return {
    async resolve(message: SlackMessageEvent): Promise<SlackMessageEvent> {
      // If thread_ts missing but parent_user_id present, fetch parent
      if (!message.thread_ts && message.parent_user_id) {
        try {
          const result = await client.conversations.replies({
            channel: message.channel,
            ts: message.ts,
            limit: 1
          });

          const parent = result.messages?.[0];
          if (parent?.thread_ts) {
            return { ...message, thread_ts: parent.thread_ts };
          }
        } catch {
          // Fall through on error
        }
      }

      return message;
    }
  };
}
```

### Inbound Debouncing

Combine rapid sequential messages from the same sender:

```typescript
export function createInboundDebouncer<T>(params: {
  debounceMs: number;
  buildKey: (entry: T) => string;
  shouldDebounce: (entry: T) => boolean;
  onFlush: (entries: T[]) => Promise<void>;
}) {
  const queues = new Map<string, { entries: T[]; timer: NodeJS.Timeout }>();

  return {
    async enqueue(entry: T): Promise<void> {
      if (!params.shouldDebounce(entry)) {
        // Process immediately
        await params.onFlush([entry]);
        return;
      }

      const key = params.buildKey(entry);
      const existing = queues.get(key);

      if (existing) {
        // Add to existing queue, reset timer
        existing.entries.push(entry);
        clearTimeout(existing.timer);
      } else {
        // Create new queue
        queues.set(key, { entries: [entry], timer: undefined as any });
      }

      const queue = queues.get(key)!;
      queue.timer = setTimeout(async () => {
        const entries = queue.entries;
        queues.delete(key);
        await params.onFlush(entries);
      }, params.debounceMs);
    }
  };
}

// Usage:
const debouncer = createInboundDebouncer({
  debounceMs: 1500,
  buildKey: (msg) => {
    const senderId = msg.user ?? msg.bot_id;
    const threadKey = msg.thread_ts ?? msg.channel;
    return `slack:${accountId}:${threadKey}:${senderId}`;
  },
  shouldDebounce: (msg) => {
    // Don't debounce media or commands
    if (msg.files?.length) return false;
    if (hasControlCommand(msg.text)) return false;
    return true;
  },
  onFlush: async (entries) => {
    // Combine messages
    const combinedText = entries.map(e => e.text).join("\n");
    const syntheticMessage = { ...entries[entries.length - 1], text: combinedText };
    await processMessage(syntheticMessage);
  }
});
```

### Thread Context Resolution

Determine threading behavior based on configuration:

```typescript
export type ReplyToMode = "off" | "first" | "all";

export function resolveThreadContext(params: {
  message: SlackMessageEvent;
  replyToMode: ReplyToMode;
}): {
  incomingThreadTs?: string;
  messageTs: string;
  isThreadReply: boolean;
  replyToId: string;        // What to reply to
  messageThreadId?: string; // Thread ID for outgoing message
} {
  const incomingThreadTs = params.message.thread_ts;
  const messageTs = params.message.ts ?? params.message.event_ts;

  const hasThreadTs = typeof incomingThreadTs === "string" && incomingThreadTs.length > 0;
  const isThreadReply = hasThreadTs &&
    (incomingThreadTs !== messageTs || Boolean(params.message.parent_user_id));

  const replyToId = incomingThreadTs ?? messageTs;

  let messageThreadId: string | undefined;
  if (params.replyToMode === "off") {
    messageThreadId = undefined;
  } else if (params.replyToMode === "first") {
    messageThreadId = isThreadReply ? incomingThreadTs : undefined;
  } else if (params.replyToMode === "all") {
    messageThreadId = isThreadReply ? incomingThreadTs : messageTs;
  }

  return { incomingThreadTs, messageTs, isThreadReply, replyToId, messageThreadId };
}
```

**Reply-To Modes**:
- `off`: Never use threads
- `first`: Reply in thread only if incoming message is a thread reply
- `all`: Always create/continue threads (recommended)

## Message Formatting

### Markdown to Slack mrkdwn Conversion

**Slack's mrkdwn Syntax**:
- `*bold*` (asterisks)
- `_italic_` (underscores)
- `~strikethrough~` (tildes)
- `` `code` `` (backticks)
- ``` ```code block``` ``` (triple backticks)
- `<url|label>` (link with label)
- `<url>` (bare link)

**Style Mapping**:
```typescript
const styleMarkers = {
  bold: { open: "*", close: "*" },
  italic: { open: "_", close: "_" },
  strikethrough: { open: "~", close: "~" },
  code: { open: "`", close: "`" },
  code_block: { open: "```\n", close: "```" }
};
```

### Critical: Escape HTML Entities

**Slack's Special Tokens**:
- `<@U123>` - User mention
- `<#C123>` - Channel mention
- `<!here>`, `<!channel>`, `<!everyone>` - Special mentions
- `<http://url|label>` - Links

**Escaping Rules**:
1. Preserve allowed angle-bracket tokens
2. Escape `&`, `<`, `>` in regular text
3. Never escape inside code blocks

```typescript
const SLACK_ANGLE_TOKEN_RE = /<[^>]*>/g;

function isAllowedSlackAngleToken(token: string): boolean {
  // User mention: <@U123>
  if (/^<@[UW][A-Z0-9]+>$/i.test(token)) return true;

  // Channel mention: <#C123>
  if (/^<#[C][A-Z0-9]+(\|[^>]+)?>$/i.test(token)) return true;

  // Special mentions: <!here>, <!channel>, <!everyone>
  if (/^<!(?:here|channel|everyone)>$/i.test(token)) return true;

  // Links: <http://...|label> or <http://...>
  if (/^<(?:https?|mailto|tel):[^>]+>$/i.test(token)) return true;

  return false;
}

function escapeSlackMrkdwnSegment(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

export function escapeSlackMrkdwnContent(text: string): string {
  const out: string[] = [];
  let lastIndex = 0;

  const matches = Array.from(text.matchAll(SLACK_ANGLE_TOKEN_RE));
  for (const match of matches) {
    // Escape text before token
    out.push(escapeSlackMrkdwnSegment(text.slice(lastIndex, match.index)));

    // Preserve or escape token
    const token = match[0];
    out.push(isAllowedSlackAngleToken(token) ? token : escapeSlackMrkdwnSegment(token));

    lastIndex = match.index! + token.length;
  }

  out.push(escapeSlackMrkdwnSegment(text.slice(lastIndex)));
  return out.join("");
}
```

### Link Formatting

```typescript
function buildSlackLink(params: {
  href: string;
  label: string;
}): string {
  const href = params.href.trim();
  const label = params.label.trim();

  // Remove mailto: for comparison
  const comparableHref = href.startsWith("mailto:") ? href.slice(7) : href;

  // Only use markup if label differs from href
  const useMarkup = label.length > 0 && label !== href && label !== comparableHref;
  if (!useMarkup) return escapeSlackMrkdwnSegment(href);

  const safeHref = escapeSlackMrkdwnSegment(href);
  const safeLabel = escapeSlackMrkdwnSegment(label);
  return `<${safeHref}|${safeLabel}>`;
}
```

### Chunking for Length Limits

**Slack API Limit**: 4000 characters per message

**Smart Chunking Pattern**:
```typescript
export function chunkSlackMessage(
  text: string,
  limit: number = 4000
): string[] {
  if (text.length <= limit) return [text];

  const chunks: string[] = [];
  let current = "";

  // Split by paragraphs first
  const paragraphs = text.split("\n\n");

  for (const para of paragraphs) {
    if (current.length + para.length + 2 <= limit) {
      current += (current ? "\n\n" : "") + para;
    } else {
      if (current) chunks.push(current);

      // If single paragraph exceeds limit, split by sentences
      if (para.length > limit) {
        const sentences = para.split(/(?<=[.!?])\s+/);
        current = "";
        for (const sentence of sentences) {
          if (current.length + sentence.length + 1 <= limit) {
            current += (current ? " " : "") + sentence;
          } else {
            if (current) chunks.push(current);
            current = sentence;
          }
        }
      } else {
        current = para;
      }
    }
  }

  if (current) chunks.push(current);
  return chunks;
}
```

## Sending Messages

### Web API Client Setup

```typescript
export const SLACK_DEFAULT_RETRY_OPTIONS = {
  retries: 2,
  factor: 2,           // Exponential backoff multiplier
  minTimeout: 500,
  maxTimeout: 3000,
  randomize: true      // Jitter to prevent thundering herd
};

export function createSlackWebClient(
  token: string,
  options: WebClientOptions = {}
): WebClient {
  return new WebClient(token, {
    ...options,
    retryConfig: options.retryConfig ?? SLACK_DEFAULT_RETRY_OPTIONS
  });
}
```

### Sending Text Messages

```typescript
export async function sendSlackMessage(params: {
  to: string;           // "user:U123" or "channel:C123" or "#general"
  message: string;
  token: string;
  threadTs?: string;    // Reply in thread
  client?: WebClient;
}): Promise<{ ok: boolean; ts?: string; channelId?: string }> {
  const client = params.client ?? createSlackWebClient(params.token);

  const recipient = parseSlackTarget(params.to);
  const { channelId } = await resolveChannelId(client, recipient);

  const chunks = chunkSlackMessage(params.message, 4000);

  let firstTs: string | undefined;
  for (const chunk of chunks) {
    const result = await client.chat.postMessage({
      channel: channelId,
      text: chunk,
      thread_ts: params.threadTs
    });

    if (!firstTs) firstTs = result.ts;
  }

  return { ok: true, ts: firstTs, channelId };
}
```

### DM Channel Resolution

**Pattern**: Use `conversations.open` to get DM channel ID

```typescript
async function resolveChannelId(
  client: WebClient,
  recipient: { kind: "channel" | "user"; id: string }
): Promise<{ channelId: string; isDm?: boolean }> {
  if (recipient.kind === "channel") {
    return { channelId: recipient.id };
  }

  // For users, open DM channel
  const response = await client.conversations.open({ users: recipient.id });
  const channelId = response.channel?.id;
  if (!channelId) throw new Error("Failed to open Slack DM channel");

  return { channelId, isDm: true };
}
```

### Media Upload

**Pattern**: Use `files.uploadV2` with caption support

```typescript
export async function uploadSlackFile(params: {
  client: WebClient;
  channelId: string;
  fileBuffer: Buffer;
  fileName: string;
  caption?: string;
  threadTs?: string;
}): Promise<string> {
  const payload = {
    channel_id: params.channelId,
    file: params.fileBuffer,
    filename: params.fileName,
    ...(params.caption ? { initial_comment: params.caption } : {}),
    ...(params.threadTs ? { thread_ts: params.threadTs } : {})
  };

  const response = await params.client.files.uploadV2(payload);
  return response.files?.[0]?.id ?? "unknown";
}
```

**Combined Message + Media**:
```typescript
export async function sendSlackMessageWithMedia(params: {
  to: string;
  message: string;
  mediaUrl: string;
  token: string;
  threadTs?: string;
}): Promise<void> {
  const client = createSlackWebClient(params.token);
  const recipient = parseSlackTarget(params.to);
  const { channelId } = await resolveChannelId(client, recipient);

  // Download media
  const { buffer, fileName } = await downloadMedia(params.mediaUrl);

  const chunks = chunkSlackMessage(params.message, 4000);
  const [firstChunk, ...restChunks] = chunks;

  // Upload file with first chunk as caption
  await uploadSlackFile({
    client,
    channelId,
    fileBuffer: buffer,
    fileName,
    caption: firstChunk,
    threadTs: params.threadTs
  });

  // Send remaining chunks as text messages
  for (const chunk of restChunks) {
    await client.chat.postMessage({
      channel: channelId,
      text: chunk,
      thread_ts: params.threadTs
    });
  }
}
```

## Slash Commands

### Native Commands with Interactive Menus

**Pattern**: Register per-command with arg validation and button menus

```typescript
export function registerSlashCommands(params: {
  app: App;
  commands: Array<{ name: string; definition: CommandDefinition }>;
  handler: SlashCommandHandler;
}) {
  for (const command of params.commands) {
    params.app.command(`/${command.name}`, async ({ command: cmd, ack, respond }) => {
      await ack();  // Acknowledge immediately (required within 3 seconds)

      const rawText = cmd.text?.trim() ?? "";
      const commandArgs = parseCommandArgs(command.definition, rawText);

      // Check for missing required args
      const menu = resolveCommandArgMenu({
        command: command.definition,
        args: commandArgs
      });

      if (menu) {
        // Show interactive button menu
        const blocks = buildSlackCommandArgMenuBlocks({
          title: menu.title,
          command: command.name,
          arg: menu.arg.name,
          choices: menu.choices,
          userId: cmd.user_id
        });

        await respond({
          text: menu.title,
          blocks,
          response_type: "ephemeral"
        });
        return;
      }

      // Process command
      const prompt = buildCommandTextFromArgs(command.definition, commandArgs);
      await params.handler({ command: cmd, respond, prompt, commandArgs });
    });
  }
}
```

**Interactive Menu Blocks**:
```typescript
const SLACK_COMMAND_ARG_ACTION_ID = "slack_command_arg";

function buildSlackCommandArgMenuBlocks(params: {
  title: string;
  command: string;
  arg: string;
  choices: Array<{ label: string; value: string }>;
  userId: string;
}): any[] {
  return [
    {
      type: "section",
      text: { type: "mrkdwn", text: params.title }
    },
    {
      type: "actions",
      elements: params.choices.map(choice => ({
        type: "button",
        text: { type: "plain_text", text: choice.label },
        action_id: SLACK_COMMAND_ARG_ACTION_ID,
        value: encodeCommandArgValue({
          command: params.command,
          arg: params.arg,
          value: choice.value,
          userId: params.userId
        })
      }))
    }
  ];
}

function encodeCommandArgValue(params: {
  command: string;
  arg: string;
  value: string;
  userId: string;
}): string {
  return `cmdarg|${params.command}|${params.arg}|${params.value}|${params.userId}`;
}
```

**Button Click Handling**:
```typescript
export function registerSlashCommandActions(params: {
  app: App;
  commands: Array<{ name: string; definition: CommandDefinition }>;
  handler: SlashCommandHandler;
}) {
  params.app.action(SLACK_COMMAND_ARG_ACTION_ID, async ({ action, body, ack, respond }) => {
    await ack();

    const parsed = parseCommandArgValue((action as any).value);

    // Security: verify user ID matches
    if (parsed.userId !== body.user.id) {
      await respond({ text: "That menu is for another user.", response_type: "ephemeral" });
      return;
    }

    const command = params.commands.find(c => c.name === parsed.command);
    if (!command) return;

    const commandArgs = { values: { [parsed.arg]: parsed.value } };
    const prompt = buildCommandTextFromArgs(command.definition, commandArgs);

    await params.handler({
      command: body as any,
      respond,
      prompt,
      commandArgs
    });
  });
}
```

### Legacy Single Slash Command

**Pattern**: One configurable command that accepts free-form text

```typescript
export function registerLegacySlashCommand(params: {
  app: App;
  commandName: string;
  handler: (params: { command: SlashCommand; respond: RespondFn; prompt: string }) => Promise<void>;
}) {
  params.app.command(
    new RegExp(`^/${escapeRegex(params.commandName)}$`),
    async ({ command, ack, respond }) => {
      await ack();
      await params.handler({
        command,
        respond,
        prompt: command.text?.trim() ?? ""
      });
    }
  );
}
```

### Authorization Checks

Implement layered authorization:

```typescript
export async function authorizeSlashCommand(params: {
  command: SlashCommand;
  channelId: string;
  userId: string;
  channelAllowlist: string[];
  userAllowlist: string[];
  dmPolicy: "disabled" | "pairing" | "open";
}): Promise<{ authorized: boolean; reason?: string; pairingCode?: string }> {
  const isDm = params.command.channel_name === "directmessage";

  if (isDm) {
    // DM Policy Check
    if (params.dmPolicy === "disabled") {
      return { authorized: false, reason: "DMs are disabled" };
    }

    if (params.dmPolicy === "pairing") {
      const allowed = params.userAllowlist.includes(params.userId);
      if (!allowed) {
        const { code } = await generatePairingCode({ userId: params.userId });
        return { authorized: false, pairingCode: code };
      }
    }

    // "open" or passed pairing check
  } else {
    // Channel Allowlist Check
    const channelAllowed = params.channelAllowlist.includes(params.channelId) ||
                          params.channelAllowlist.includes(params.command.channel_name);

    if (!channelAllowed) {
      return { authorized: false, reason: "Channel not allowed" };
    }
  }

  // User Allowlist Check (if configured)
  if (params.userAllowlist.length > 0 && !params.userAllowlist.includes("*")) {
    const allowed = params.userAllowlist.includes(params.userId);
    if (!allowed) {
      return { authorized: false, reason: "User not allowed" };
    }
  }

  return { authorized: true };
}
```

## Access Control Patterns

### Channel Policy Modes

```typescript
export type GroupPolicy = "closed" | "open";

export function isChannelAllowedByPolicy(params: {
  groupPolicy: GroupPolicy;
  channelAllowlistConfigured: boolean;
  channelAllowed: boolean;
}): boolean {
  if (params.groupPolicy === "closed") {
    // Closed: require explicit allow AND not denied
    return params.channelAllowlistConfigured && params.channelAllowed;
  }

  // Open: allow unless explicitly denied OR allowlist configured without match
  if (!params.channelAllowlistConfigured) return true;
  return params.channelAllowed;
}
```

**Closed Mode** (allowlist):
- Only explicitly allowed channels
- Default: deny all

**Open Mode** (denylist):
- All channels except explicitly denied
- Default: allow all

### DM Policy Modes

```typescript
export type DmPolicy = "disabled" | "pairing" | "open";
```

**Disabled**: Reject all DMs

**Pairing**: Require pairing code on first contact
```typescript
async function handlePairingRequired(params: {
  userId: string;
  userName?: string;
  respond: RespondFn;
}): Promise<void> {
  const { code, created } = await upsertPairingRequest({
    channel: "slack",
    id: params.userId,
    meta: { name: params.userName }
  });

  if (created) {
    await params.respond({
      text: `To enable DMs, provide this pairing code to an admin:\n\nCode: \`${code}\`\nUser ID: ${params.userId}`,
      response_type: "ephemeral"
    });
  }
}
```

**Open**: Allow all DMs

### Allowlist Matching

Support flexible matching: ID, username, email, wildcards

```typescript
export function resolveAllowListMatch(params: {
  allowList: string[];
  id: string;
  name?: string;
  email?: string;
}): { allowed: boolean; matchType?: "id" | "name" | "email" | "wildcard" } {
  if (params.allowList.includes("*")) {
    return { allowed: true, matchType: "wildcard" };
  }

  if (params.allowList.includes(params.id)) {
    return { allowed: true, matchType: "id" };
  }

  if (params.name && params.allowList.includes(params.name.toLowerCase())) {
    return { allowed: true, matchType: "name" };
  }

  if (params.email && params.allowList.includes(params.email.toLowerCase())) {
    return { allowed: true, matchType: "email" };
  }

  return { allowed: false };
}
```

## Interactive Components

### Buttons

```typescript
export function registerButtonHandler(params: {
  app: App;
  actionId: string;
  handler: (params: {
    action: ButtonAction;
    body: any;
    respond: RespondFn;
  }) => Promise<void>;
}) {
  params.app.action(params.actionId, async ({ action, body, ack, respond }) => {
    await ack();
    await params.handler({ action: action as ButtonAction, body, respond });
  });
}

// Send message with buttons
async function sendMessageWithButtons(params: {
  channelId: string;
  text: string;
  buttons: Array<{ label: string; actionId: string; value: string }>;
  client: WebClient;
}): Promise<void> {
  await params.client.chat.postMessage({
    channel: params.channelId,
    text: params.text,
    blocks: [
      {
        type: "section",
        text: { type: "mrkdwn", text: params.text }
      },
      {
        type: "actions",
        elements: params.buttons.map(btn => ({
          type: "button",
          text: { type: "plain_text", text: btn.label },
          action_id: btn.actionId,
          value: btn.value
        }))
      }
    ]
  });
}
```

### Modals

```typescript
export async function openModal(params: {
  triggerId: string;
  title: string;
  callbackId: string;
  blocks: any[];
  client: WebClient;
}): Promise<void> {
  await params.client.views.open({
    trigger_id: params.triggerId,
    view: {
      type: "modal",
      callback_id: params.callbackId,
      title: { type: "plain_text", text: params.title },
      blocks: params.blocks,
      submit: { type: "plain_text", text: "Submit" }
    }
  });
}

export function registerModalHandler(params: {
  app: App;
  callbackId: string;
  handler: (params: { view: any; respond: RespondFn }) => Promise<void>;
}) {
  params.app.view(params.callbackId, async ({ view, ack, respond }) => {
    await ack();
    await params.handler({ view, respond });
  });
}
```

### Shortcuts

**Global Shortcuts**:
```typescript
export function registerGlobalShortcut(params: {
  app: App;
  callbackId: string;
  handler: (params: { shortcut: any; client: WebClient }) => Promise<void>;
}) {
  params.app.shortcut(params.callbackId, async ({ shortcut, ack, client }) => {
    await ack();
    await params.handler({ shortcut, client });
  });
}
```

**Message Shortcuts**:
```typescript
export function registerMessageShortcut(params: {
  app: App;
  callbackId: string;
  handler: (params: {
    shortcut: MessageShortcut;
    message: any;
    client: WebClient;
  }) => Promise<void>;
}) {
  params.app.shortcut(params.callbackId, async ({ shortcut, ack, client }) => {
    await ack();
    const messageShortcut = shortcut as MessageShortcut;
    await params.handler({
      shortcut: messageShortcut,
      message: messageShortcut.message,
      client
    });
  });
}
```

## Rate Limiting & Error Handling

### Rate Limit Strategy

Slack enforces tier-based rate limits. Use exponential backoff with jitter:

```typescript
export const SLACK_DEFAULT_RETRY_OPTIONS = {
  retries: 2,
  factor: 2,           // Exponential: 500ms → 1000ms → 2000ms
  minTimeout: 500,
  maxTimeout: 3000,
  randomize: true      // Add jitter to prevent thundering herd
};
```

**Rate Limit Tiers**:
- Tier 1: 1+ per minute (most methods)
- Tier 2: 20+ per minute (posting messages)
- Tier 3: 50+ per minute (specialized methods)
- Tier 4: 100+ per minute (rarely used)

**Respect `Retry-After` Header**:
```typescript
client.on("rate_limited", (retryAfter) => {
  console.warn(`Rate limited. Retry after ${retryAfter} seconds.`);
});
```

### Error Handling Patterns

**Global Error Boundary**:
```typescript
export function registerEventHandlers(params: {
  app: App;
  handlers: EventHandlers;
  onError: (error: Error, context: string) => void;
}) {
  params.app.event("message", async ({ event }) => {
    try {
      await params.handlers.onMessage(event);
    } catch (err) {
      params.onError(err as Error, "message event");
    }
  });

  // Repeat for all event types
}
```

**Slash Command Error Responses**:
```typescript
try {
  await handleSlashCommand({ command, respond, prompt });
} catch (err) {
  console.error("Slash command error:", err);
  await respond({
    text: "Sorry, something went wrong processing that command.",
    response_type: "ephemeral"
  });
}
```

**Graceful Degradation**:
```typescript
// Auth test failure is non-fatal (fall back to regex mentions)
try {
  const auth = await app.client.auth.test({ token: botToken });
  botUserId = auth.user_id ?? "";
  teamId = auth.team_id ?? "";
} catch (err) {
  console.warn("Auth test failed, mention detection will use regex fallback");
  botUserId = "";
  teamId = "";
}
```

## Channel & User Resolution

### Batch Channel Resolution

Fetch all channels once, then match by ID or name:

```typescript
export async function resolveChannelAllowlist(params: {
  token: string;
  entries: string[];
}): Promise<Array<{
  input: string;
  id?: string;
  resolved: boolean;
  archived?: boolean;
}>> {
  const client = createSlackWebClient(params.token);

  // Fetch all channels (paginated)
  const channels: Array<{
    id?: string;
    name?: string;
    is_archived?: boolean;
  }> = [];

  let cursor: string | undefined;
  do {
    const result = await client.conversations.list({
      exclude_archived: false,
      types: "public_channel,private_channel",
      cursor,
      limit: 1000
    });

    channels.push(...(result.channels ?? []));
    cursor = result.response_metadata?.next_cursor;
  } while (cursor);

  // Match entries
  return params.entries.map(input => {
    const channel = channels.find(c =>
      c.id === input || c.name === input || c.name === input.replace(/^#/, "")
    );

    return {
      input,
      id: channel?.id,
      resolved: Boolean(channel),
      archived: channel?.is_archived
    };
  });
}
```

### Batch User Resolution

Fetch all users once, match by ID, username, display name, or email:

```typescript
export async function resolveUserAllowlist(params: {
  token: string;
  entries: string[];
}): Promise<Array<{
  input: string;
  id?: string;
  resolved: boolean;
  note?: string;
}>> {
  const client = createSlackWebClient(params.token);

  // Fetch all users (paginated)
  const users: Array<{
    id?: string;
    name?: string;
    profile?: { email?: string; display_name?: string };
    deleted?: boolean;
    is_bot?: boolean;
  }> = [];

  let cursor: string | undefined;
  do {
    const result = await client.users.list({ cursor, limit: 1000 });
    users.push(...(result.members ?? []));
    cursor = result.response_metadata?.next_cursor;
  } while (cursor);

  // Match entries
  return params.entries.map(input => {
    const user = users.find(u =>
      u.id === input ||
      u.name === input ||
      u.profile?.display_name === input ||
      u.profile?.email === input
    );

    const note = user?.deleted ? "deleted" : user?.is_bot ? "bot" : undefined;

    return {
      input,
      id: user?.id,
      resolved: Boolean(user),
      note
    };
  });
}
```

### Caching User/Channel Lookups

Reduce API calls during event processing:

```typescript
export function createSlackResolver(client: WebClient) {
  const channelCache = new Map<string, { name?: string; type?: string }>();
  const userCache = new Map<string, { name?: string; email?: string }>();

  return {
    async resolveChannelName(channelId: string): Promise<{ name?: string; type?: string } | null> {
      if (channelCache.has(channelId)) {
        return channelCache.get(channelId)!;
      }

      try {
        const result = await client.conversations.info({ channel: channelId });
        const info = {
          name: result.channel?.name,
          type: result.channel?.is_im ? "im" : result.channel?.is_channel ? "channel" : "group"
        };
        channelCache.set(channelId, info);
        return info;
      } catch {
        return null;
      }
    },

    async resolveUserName(userId: string): Promise<{ name?: string; email?: string } | null> {
      if (userCache.has(userId)) {
        return userCache.get(userId)!;
      }

      try {
        const result = await client.users.info({ user: userId });
        const info = {
          name: result.user?.name,
          email: result.user?.profile?.email
        };
        userCache.set(userId, info);
        return info;
      } catch {
        return null;
      }
    }
  };
}
```

## Common Pitfalls & Solutions

### Pitfall 1: Missing `thread_ts` on Thread Replies

**Problem**: Slack sometimes omits `thread_ts` but includes `parent_user_id`.

**Solution**: Fetch parent message to get missing `thread_ts` (see Thread Resolution section).

### Pitfall 2: Double-Processing Events

**Problem**: Slack retries events on timeout, causing duplicates.

**Solution**: Track seen messages by `(channel, ts)` (see Deduplication section).

### Pitfall 3: Incorrect HTML Escaping

**Problem**: Escaping `<@U123>` breaks mentions; not escaping `<script>` creates XSS.

**Solution**: Parse and preserve allowed angle-bracket tokens, escape everything else (see Escaping section).

### Pitfall 4: Rate Limit Crashes

**Problem**: Hitting rate limits without backoff causes failures.

**Solution**: Use exponential backoff with jitter (see Rate Limiting section).

### Pitfall 5: DM Channel ID Confusion

**Problem**: Can't send DM with user ID directly; need channel ID.

**Solution**: Call `conversations.open({ users: userId })` first (see DM Resolution section).

### Pitfall 6: Slash Command Timeout

**Problem**: Slack requires acknowledgment within 3 seconds.

**Solution**: Always `await ack()` immediately, process asynchronously:
```typescript
app.command("/mycommand", async ({ command, ack, respond }) => {
  await ack();  // MUST be within 3 seconds

  // Long-running work here
  await processCommand(command);
  await respond({ text: "Done!" });
});
```

### Pitfall 7: Multi-Account Token Leakage

**Problem**: Using wrong token for wrong workspace.

**Solution**: Always resolve token from account context, never share tokens across accounts.

### Pitfall 8: Ignoring Event Filters

**Problem**: Processing events from other Slack apps in Socket Mode.

**Solution**: Filter by `api_app_id`:
```typescript
function shouldDropEvent(body: any, expectedAppId: string): boolean {
  const eventAppId = body.api_app_id;
  if (!eventAppId) return false;
  return eventAppId !== expectedAppId;
}
```

## Testing Patterns

### Unit Testing Event Handlers

```typescript
import { describe, test, expect, vi } from "vitest";

describe("Slack message handler", () => {
  test("filters unwanted message subtypes", async () => {
    const handler = vi.fn();
    const ctx = { handleMessage: handler };

    // Allowed subtype: file_share
    await processMessageEvent(ctx, {
      type: "message",
      subtype: "file_share",
      channel: "C123",
      ts: "1234.5678",
      text: "File uploaded"
    });
    expect(handler).toHaveBeenCalledTimes(1);

    // Disallowed subtype: channel_join
    await processMessageEvent(ctx, {
      type: "message",
      subtype: "channel_join",
      channel: "C123",
      ts: "1234.5679"
    });
    expect(handler).toHaveBeenCalledTimes(1);  // Still 1, not called again
  });

  test("detects thread replies correctly", () => {
    const context = resolveThreadContext({
      message: {
        ts: "1234.5678",
        thread_ts: "1234.0000",
        parent_user_id: "U123"
      },
      replyToMode: "first"
    });

    expect(context.isThreadReply).toBe(true);
    expect(context.replyToId).toBe("1234.0000");
    expect(context.messageThreadId).toBe("1234.0000");
  });
});
```

### Integration Testing with Mock Client

```typescript
import { describe, test, expect, vi } from "vitest";

describe("Slack message sending", () => {
  test("chunks long messages correctly", async () => {
    const mockClient = {
      chat: {
        postMessage: vi.fn().mockResolvedValue({ ok: true, ts: "1234.5678" })
      }
    };

    const longMessage = "a".repeat(5000);  // Exceeds 4000 char limit

    await sendSlackMessage({
      to: "channel:C123",
      message: longMessage,
      token: "xoxb-test",
      client: mockClient as any
    });

    // Should be called twice (4000 + 1000)
    expect(mockClient.chat.postMessage).toHaveBeenCalledTimes(2);
    expect(mockClient.chat.postMessage).toHaveBeenNthCalledWith(1, expect.objectContaining({
      channel: "C123",
      text: expect.stringContaining("aaa")
    }));
  });
});
```

### E2E Testing with Real Slack Workspace

```typescript
import { describe, test, expect } from "vitest";

describe("Slack E2E", () => {
  test("sends message and receives via event", async () => {
    const botToken = process.env.SLACK_BOT_TOKEN!;
    const appToken = process.env.SLACK_APP_TOKEN!;
    const testChannel = process.env.SLACK_TEST_CHANNEL!;

    // Start bot
    const app = new App({ token: botToken, appToken, socketMode: true });
    const receivedMessages: string[] = [];

    app.event("message", async ({ event }) => {
      receivedMessages.push((event as any).text);
    });

    await app.start();

    // Send test message
    const testText = `Test message ${Date.now()}`;
    await app.client.chat.postMessage({
      channel: testChannel,
      text: testText
    });

    // Wait for event
    await new Promise(resolve => setTimeout(resolve, 2000));

    expect(receivedMessages).toContain(testText);

    await app.stop();
  });
});
```

## Configuration Examples

### Minimal Socket Mode

```yaml
slack:
  enabled: true
  mode: socket
  botToken: xoxb-your-bot-token
  appToken: xapp-your-app-token
```

### Production HTTP Mode

```yaml
slack:
  enabled: true
  mode: http
  botToken: xoxb-your-bot-token
  signingSecret: your-signing-secret
  webhookPath: /slack/events
```

### Multi-Account Setup

```yaml
slack:
  accounts:
    workspace-alpha:
      enabled: true
      mode: socket
      botToken: xoxb-alpha-token
      appToken: xapp-alpha-token
      groupPolicy: closed
      channels:
        general: { allowed: true }
        engineering: { allowed: true }

    workspace-beta:
      enabled: true
      mode: socket
      botToken: xoxb-beta-token
      appToken: xapp-beta-token
      groupPolicy: open
      dm:
        enabled: true
        policy: pairing
```

### Advanced Features

```yaml
slack:
  enabled: true
  mode: socket
  botToken: xoxb-your-token
  appToken: xapp-your-token

  # Access control
  groupPolicy: closed
  dm:
    enabled: true
    policy: pairing
    allowFrom: ["U123ABC", "alice@example.com"]

  channels:
    general:
      allowed: true
      users: ["U123ABC", "bob@example.com"]
    random:
      allowed: false

  # Threading
  replyToMode: all
  thread:
    historyScope: thread
    inheritParent: false

  # Reactions
  reactionNotifications: own
  reactionAllowlist: ["eyes", "white_check_mark", "tada"]

  # Commands
  slashCommand:
    enabled: true
    name: mybot
    sessionPrefix: slash
    ephemeral: false

  commands:
    native: true
    nativeSkills: true

  # Media
  mediaMaxMb: 20

  # Text formatting
  textChunkLimit: 3000
  markdownTableMode: markdown
```

## Reference Implementation

See Clawdbot's Slack integration for a complete production implementation:
- Entry point: `/Users/tinnguyen/clawd/src/slack/index.ts`
- Event handling: `/Users/tinnguyen/clawd/src/slack/monitor/events/`
- Message processing: `/Users/tinnguyen/clawd/src/slack/monitor/message-handler.ts`
- Formatting: `/Users/tinnguyen/clawd/src/slack/format.ts`
- Slash commands: `/Users/tinnguyen/clawd/src/slack/monitor/slash.ts`

## Additional Resources

- Slack Bolt Framework: https://slack.dev/bolt-js/
- Slack API Reference: https://api.slack.com/methods
- Block Kit Builder: https://app.slack.com/block-kit-builder/
- Event Types: https://api.slack.com/events
- Rate Limits: https://api.slack.com/docs/rate-limits

## Summary Checklist

When implementing Slack integration, ensure you:

- [ ] Choose Socket Mode (dev) or HTTP Mode (production)
- [ ] Implement token normalization and validation
- [ ] Support multi-account architecture from day one
- [ ] Handle all relevant message subtypes (file_share, message_changed, etc.)
- [ ] Implement message deduplication (seen message tracking)
- [ ] Resolve missing `thread_ts` via parent message lookup
- [ ] Escape HTML entities while preserving Slack tokens
- [ ] Chunk messages at 4000 character limit
- [ ] Use exponential backoff with jitter for rate limits
- [ ] Cache user/channel lookups to reduce API calls
- [ ] Implement graceful error boundaries on all event handlers
- [ ] Acknowledge slash commands within 3 seconds
- [ ] Filter events by `api_app_id` in Socket Mode
- [ ] Support interactive components (buttons, modals, shortcuts)
- [ ] Implement layered authorization (channel policy, DM policy, user allowlist)
- [ ] Write unit tests for event handlers and formatters
- [ ] Write integration tests with mock clients
- [ ] Test E2E in real Slack workspace before production
