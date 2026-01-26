# WhatsApp Web Integration Reference

> Platform-specific implementation guide for WhatsApp Web using Baileys.
> Part of the [Messaging Platform Integration](../SKILL.md) skill.

Production-ready patterns for authentication (QR code, session persistence), message routing, media handling, group chat support, real-time event handling, reconnection strategies, and error recovery.

## Architecture Patterns

### Core Design Principles

1. **Gateway Ownership**: The gateway process owns all Baileys sockets; clients never directly instantiate sockets
2. **Active Listener Pattern**: Outbound sends require an active listener registered via a central registry
3. **Multi-Account Support**: Multiple WhatsApp accounts managed via `accountId` routing
4. **Credential Isolation**: Each account has its own auth directory with backup/restore capability
5. **Automatic Recovery**: Credentials are backed up on each save; corrupted files auto-restore from `.bak`

### Component Structure

```
whatsapp/
├── session.ts              # Core Baileys socket creation & lifecycle
├── login.ts               # CLI login flow (QR scan, wait for connection)
├── login-qr.ts            # Programmatic QR login (UI integration)
├── auth-store.ts          # Credential storage & backup/restore
├── accounts.ts            # Multi-account resolution
├── active-listener.ts     # Active listener registry (outbound sends)
├── inbound/               # Inbound message processing
│   ├── monitor.ts         # Main inbox monitor
│   ├── extract.ts         # Message content extraction
│   ├── media.ts           # Inbound media download
│   ├── access-control.ts  # Allowlist/pairing/DM policy
│   └── dedupe.ts          # Message deduplication
├── outbound.ts            # Outbound message sends
├── media.ts               # Media loading & optimization
├── reconnect.ts           # Reconnection policy & backoff
└── qr-image.ts            # QR code rendering
```

## Authentication & Session Management

### Session Creation Pattern

**Core function signature**:
```typescript
export async function createWaSocket(
  printQr: boolean,
  verbose: boolean,
  opts: { authDir?: string; onQr?: (qr: string) => void } = {},
)
```

**Multi-file auth state** (Baileys):
- Uses `useMultiFileAuthState(authDir)` from Baileys
- Files: `creds.json` (credentials), `app-state-sync-*.json` (state), `session-*.json`
- Directory: `~/.app/credentials/whatsapp/<accountId>/` (adjust to your app)

**Critical: Credential save queueing** (prevents race conditions):
```typescript
let credsSaveQueue: Promise<void> = Promise.resolve();

function enqueueSaveCreds(authDir, saveCreds, logger) {
  credsSaveQueue = credsSaveQueue
    .then(() => safeSaveCreds(authDir, saveCreds, logger))
    .catch((err) => logger.warn({ error: String(err) }, "creds save queue error"));
}

sock.ev.on("creds.update", () => {
  enqueueSaveCreds(authDir, saveCreds, logger);
});
```

**Automatic backup on save** (prevent corruption):
```typescript
const raw = readCredsJsonRaw(credsPath);
if (raw) {
  try {
    JSON.parse(raw); // Validate before backing up
    fsSync.copyFileSync(credsPath, backupPath);
  } catch {
    // Keep existing backup if new creds are corrupted
  }
}
```

**Automatic restore on corruption** (startup resilience):
```typescript
export function maybeRestoreCredsFromBackup(authDir: string): void {
  const credsPath = path.join(authDir, "creds.json");
  const backupPath = `${credsPath}.bak`;

  const raw = readCredsJsonRaw(credsPath);
  if (raw) {
    try {
      JSON.parse(raw); // Throws if corrupted
      return; // Valid, no restore needed
    } catch {
      // Corrupted - continue to restore
    }
  }

  // Restore from backup
  const backupRaw = readCredsJsonRaw(backupPath);
  if (backupRaw) {
    JSON.parse(backupRaw); // Validate backup
    fsSync.copyFileSync(backupPath, credsPath);
  }
}
```

### Login Flows

**CLI login** (terminal QR):
```typescript
// Print QR to terminal via qrcode-terminal
const sock = await createWaSocket(true, verbose, { authDir });
await waitForWaConnection(sock);
```

**Programmatic login** (UI integration):
```typescript
// Returns QR as base64-encoded PNG
const { qrDataUrl } = await startWebLoginWithQr({ accountId, verbose });
// Poll for completion
const result = await waitForWebLogin({ accountId, timeoutMs: 180000 });
```

**Code 515 handling** (restart after pairing):
```typescript
if (code === 515) {
  console.log("WhatsApp asked for a restart after pairing (code 515)");
  sock.ws?.close();
  const retry = await createWaSocket(false, verbose, { authDir });
  await waitForWaConnection(retry);
  console.log("Linked after restart; session ready.");
}
```

### QR Login State Management

**Problem**: Multiple concurrent QR login requests
**Solution**: Singleton active login per `accountId` with TTL

```typescript
const activeLogins = new Map<string, ActiveLogin>();
const ACTIVE_LOGIN_TTL_MS = 3 * 60_000; // 3 minutes

export async function startWebLoginWithQr(opts) {
  const existing = activeLogins.get(accountId);
  if (existing && isLoginFresh(existing) && existing.qrDataUrl) {
    return { qrDataUrl: existing.qrDataUrl, message: "QR already active" };
  }

  await resetActiveLogin(accountId); // Close old socket

  const sock = await createWaSocket(false, verbose, {
    authDir,
    onQr: (qr) => {
      const current = activeLogins.get(accountId);
      if (current && !current.qr) current.qr = qr;
      resolveQr(qr);
    },
  });

  const login: ActiveLogin = {
    id: randomUUID(),
    sock,
    startedAt: Date.now(),
    // ...
  };
  activeLogins.set(accountId, login);

  const qr = await qrPromise;
  const base64 = await renderQrPngBase64(qr);
  login.qrDataUrl = `data:image/png;base64,${base64}`;
  return { qrDataUrl: login.qrDataUrl, message: "Scan this QR" };
}
```

## Message Flow

### Inbound Pipeline

**Entry point**:
```typescript
export async function monitorWebInbox(options: {
  verbose: boolean;
  accountId: string;
  authDir: string;
  onMessage: (msg: WebInboundMessage) => Promise<void>;
  mediaMaxMb?: number;
  sendReadReceipts?: boolean;
  debounceMs?: number;
  shouldDebounce?: (msg: WebInboundMessage) => boolean;
})
```

**Pipeline stages**:

1. **Socket creation & connection**:
```typescript
const sock = await createWaSocket(false, verbose, { authDir });
await waitForWaConnection(sock);
await sock.sendPresenceUpdate("available");
```

2. **Event subscription**:
```typescript
sock.ev.on("messages.upsert", handleMessagesUpsert);
sock.ev.on("connection.update", handleConnectionUpdate);
```

3. **Message filtering**:
- Ignore `type !== 'notify' && type !== 'append'`
- Ignore status/broadcast chats (`remoteJid.endsWith('@status'|'@broadcast')`)
- Dedupe via `isRecentInboundMessage(dedupeKey)` (10-minute window)

4. **Access control**:
- DM policy: `pairing`, `allowlist`, `open`, `disabled`
- Group policy: `open`, `allowlist`, `disabled`
- Pairing code generation for unknown senders

5. **Read receipts** (optional):
```typescript
if (id && !access.isSelfChat && sendReadReceipts !== false) {
  await sock.readMessages([{ remoteJid, id, participant, fromMe: false }]);
}
```

6. **Content extraction**:
- Text: `extractText(msg.message)` (conversation, extendedText, captions)
- Location: `extractLocationData(msg.message)` → formatted text
- Media: `extractMediaPlaceholder(msg.message)` → `<media:image|video|...>`
- Reply context: `describeReplyContext(msg.message)` → quoted message

7. **Media download** (optional):
```typescript
const inboundMedia = await downloadInboundMedia(msg, sock);
if (inboundMedia) {
  const saved = await saveMediaBuffer(
    inboundMedia.buffer,
    inboundMedia.mimetype,
    "inbound",
    maxBytes,
  );
  mediaPath = saved.path;
}
```

8. **Message delivery to callback**:
```typescript
const inboundMessage: WebInboundMessage = {
  id, from, conversationId, to, accountId, body,
  chatType: group ? "group" : "direct",
  chatId: remoteJid,
  senderJid: participantJid,
  senderE164, senderName,
  replyToId, replyToBody, replyToSender,
  groupSubject, groupParticipants,
  mentionedJids, selfJid, selfE164,
  location, mediaPath, mediaType,
  sendComposing, reply, sendMedia,
};
await onMessage(inboundMessage);
```

### Outbound Pipeline

**Entry point**:
```typescript
export async function sendMessageWhatsApp(
  to: string,
  body: string,
  options: {
    verbose: boolean;
    mediaUrl?: string;
    gifPlayback?: boolean;
    accountId?: string;
  },
)
```

**Pipeline stages**:

1. **Active listener retrieval**:
```typescript
const { listener, accountId } = requireActiveWebListener(options.accountId);
// Throws if no active listener for accountId
```

2. **Media loading** (if provided):
```typescript
const media = await loadWebMedia(options.mediaUrl);
mediaBuffer = media.buffer;
mediaType = media.contentType;
```

3. **Typing indicator**:
```typescript
await active.sendComposingTo(to);
```

4. **Message send**:
```typescript
const result = await active.sendMessage(to, text, mediaBuffer, mediaType, sendOptions);
const messageId = result.messageId;
```

### Active Listener Registry Pattern

**Problem**: Outbound sends need access to the live Baileys socket
**Solution**: Global registry of active listeners per `accountId`

```typescript
const listeners = new Map<string, ActiveWebListener>();

export function setActiveWebListener(accountId: string, listener: ActiveWebListener | null): void {
  const id = resolveWebAccountId(accountId);
  if (!listener) {
    listeners.delete(id);
  } else {
    listeners.set(id, listener);
  }
}

export function requireActiveWebListener(accountId?: string): {
  accountId: string;
  listener: ActiveWebListener
} {
  const id = resolveWebAccountId(accountId);
  const listener = listeners.get(id);
  if (!listener) {
    throw new Error(`No active WhatsApp listener (account: ${id}). Start gateway.`);
  }
  return { accountId: id, listener };
}
```

**Lifecycle**:
1. Gateway starts inbox monitor → `setActiveWebListener(accountId, listener)`
2. Outbound send → `requireActiveWebListener(accountId)` → uses listener
3. Connection closes → `setActiveWebListener(accountId, null)`

## Media Handling

### Inbound Media Download

```typescript
export async function downloadInboundMedia(
  msg: proto.IWebMessageInfo,
  sock: Awaited<ReturnType<typeof createWaSocket>>,
): Promise<{ buffer: Buffer; mimetype?: string } | undefined> {
  const buffer = await downloadMediaMessage(msg, "buffer", {}, {
    reuploadRequest: sock.updateMediaMessage,
    logger: sock.logger,
  });

  const mimetype =
    msg.message?.imageMessage?.mimetype ??
    msg.message?.videoMessage?.mimetype ??
    msg.message?.documentMessage?.mimetype ??
    msg.message?.audioMessage?.mimetype ??
    msg.message?.stickerMessage?.mimetype;

  return { buffer, mimetype };
}
```

### Outbound Media Optimization

**Image optimization strategy** (resize + quality sweep):
```typescript
async function optimizeImageToJpeg(buffer, maxBytes) {
  const sides = [2048, 1536, 1280, 1024, 800];
  const qualities = [80, 70, 60, 50, 40];

  for (const side of sides) {
    for (const quality of qualities) {
      const out = await resizeToJpeg({ buffer, maxSide: side, quality });
      if (out.length <= maxBytes) {
        return { buffer: out, size: out.length, resizeSide: side, quality };
      }
    }
  }
  throw new Error("Failed to optimize image below cap");
}
```

**HEIC conversion**:
- Auto-detect HEIC/HEIF via MIME or file extension
- Convert to JPEG via `convertHeicToJpeg(buffer)`
- Update filename: `photo.heic` → `photo.jpg`

**Size caps** (recommended):
- Image: 5MB (configurable)
- Video: 16MB
- Audio: 16MB
- Document: 16MB

## Group Chat Support

### Group Metadata Caching

```typescript
const groupMetaCache = new Map<string, {
  subject?: string;
  participants?: string[];
  expires: number
}>();
const GROUP_META_TTL_MS = 5 * 60 * 1000; // 5 minutes

const getGroupMeta = async (jid: string) => {
  const cached = groupMetaCache.get(jid);
  if (cached && cached.expires > Date.now()) return cached;

  const meta = await sock.groupMetadata(jid);
  const participants = await Promise.all(
    meta.participants.map(async (p) => {
      const mapped = await resolveInboundJid(p.id);
      return mapped ?? p.id;
    })
  );

  const entry = {
    subject: meta.subject,
    participants,
    expires: Date.now() + GROUP_META_TTL_MS
  };
  groupMetaCache.set(jid, entry);
  return entry;
};
```

### Mention Detection Pattern

```typescript
export function buildMentionConfig(cfg: AppConfig) {
  const patterns = cfg.messages?.groupChat?.mentionPatterns ?? [];
  const regexes = patterns.map((pattern) => new RegExp(pattern, "i"));
  return { patterns, regexes };
}

export function isMentioned(
  body: string,
  mentionedJids: string[],
  selfJid: string,
  mentionConfig
) {
  // Check @mention JIDs
  if (mentionedJids.includes(selfJid)) return true;

  // Check regex patterns
  for (const regex of mentionConfig.regexes) {
    if (regex.test(body)) return true;
  }

  return false;
}
```

### Group History Injection

**Pattern**: Provide context from recent messages before bot's last reply

```typescript
const historyLimit = config.groupChat?.historyLimit ?? 50;
const history = groupHistories.get(chatId) ?? [];
const pendingHistory = history.slice(-historyLimit);

let historyBlock = "";
if (pendingHistory.length > 0) {
  historyBlock = "[Chat messages since your last reply - for context]\n";
  for (const entry of pendingHistory) {
    const senderLabel = formatGroupSender(entry.sender, groupMemberNames);
    historyBlock += `${entry.body} [from: ${senderLabel}]\n`;
  }
  historyBlock += "[/Chat messages]\n\n";
}

const currentBlock = `[Current message - respond to this]\n${body}\n[/Current message]`;
const finalBody = historyBlock + currentBlock;

// After bot replies, clear history
groupHistories.set(chatId, []);
```

## Reconnection & Resilience

### Reconnect Policy

```typescript
export const DEFAULT_RECONNECT_POLICY: ReconnectPolicy = {
  initialMs: 2_000,
  maxMs: 30_000,
  factor: 1.8,
  jitter: 0.25,
  maxAttempts: 12,
};

export function computeBackoff(policy: BackoffPolicy, attempt: number): number {
  const base = Math.min(
    policy.initialMs * Math.pow(policy.factor, attempt - 1),
    policy.maxMs
  );
  const jitterRange = base * policy.jitter;
  const jitter = (Math.random() - 0.5) * 2 * jitterRange;
  return Math.max(0, Math.floor(base + jitter));
}
```

### Reconnect Loop Pattern

```typescript
while (true) {
  if (stopRequested()) break;

  const listener = await monitorWebInbox({ /* ... */ });
  setActiveWebListener(accountId, listener);

  const reason = await Promise.race([
    listener.onClose,
    abortPromise,
  ]);

  const uptimeMs = Date.now() - startedAt;
  if (uptimeMs > heartbeatSeconds * 1000) {
    reconnectAttempts = 0; // Healthy stretch; reset backoff
  }

  if (stopRequested() || reason === "aborted") break;

  if (reason.isLoggedOut) {
    logger.error("WhatsApp session logged out. Relink required.");
    break;
  }

  reconnectAttempts += 1;
  if (reconnectAttempts >= reconnectPolicy.maxAttempts) {
    logger.error("Max reconnect attempts reached.");
    break;
  }

  const delay = computeBackoff(reconnectPolicy, reconnectAttempts);
  await sleep(delay, abortSignal);
}
```

### Watchdog Timer Pattern

**Purpose**: Detect stuck message processing (event emitter died)

```typescript
const MESSAGE_TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes
const WATCHDOG_CHECK_MS = 60 * 1000; // Check every minute

let lastMessageAt: number | null = null;

watchdogTimer = setInterval(() => {
  if (!lastMessageAt) return;

  const timeSinceLastMessage = Date.now() - lastMessageAt;
  if (timeSinceLastMessage <= MESSAGE_TIMEOUT_MS) return;

  logger.warn("Message timeout detected - forcing reconnect");
  listener.signalClose({
    status: 499,
    isLoggedOut: false,
    error: "watchdog-timeout"
  });
}, WATCHDOG_CHECK_MS);

// Update on each message
sock.ev.on("messages.upsert", () => {
  lastMessageAt = Date.now();
});
```

## Error Handling

### WebSocket Error Handling

**Problem**: Unhandled WebSocket errors crash the process
**Solution**: Attach error handler to `sock.ws`

```typescript
if (sock.ws && typeof sock.ws.on === "function") {
  sock.ws.on("error", (err: Error) => {
    logger.error({ error: String(err) }, "WebSocket error");
  });
}
```

### Boom Error Extraction (Baileys)

```typescript
function extractBoomDetails(err: unknown): {
  statusCode?: number;
  error?: string;
  message?: string;
} | null {
  const output = err?.output;
  const payload = output?.payload;
  const statusCode = output?.statusCode ?? payload?.statusCode;
  const error = payload?.error;
  const message = payload?.message;
  return { statusCode, error, message };
}

export function formatError(err: unknown): string {
  if (err instanceof Error) return err.message;
  if (typeof err === "string") return err;

  const boom = extractBoomDetails(err) ??
    extractBoomDetails(err?.error) ??
    extractBoomDetails(err?.lastDisconnect?.error);
  const status = boom?.statusCode ?? getStatusCode(err);
  const code = err?.code;

  const pieces: string[] = [];
  if (typeof status === "number") pieces.push(`status=${status}`);
  if (boom?.error) pieces.push(boom.error);
  if (boom?.message) pieces.push(boom.message);
  if (code) pieces.push(`code=${code}`);

  return pieces.length > 0 ? pieces.join(" ") : JSON.stringify(err);
}
```

### Crypto Error Detection

**Pattern**: Detect WhatsApp crypto errors (signal key store issues) for reconnect

```typescript
export function isLikelyWhatsAppCryptoError(reason: unknown): boolean {
  const errorStr = String(reason).toLowerCase();
  return (
    errorStr.includes("no valid") && errorStr.includes("key pair found") ||
    errorStr.includes("signal") && errorStr.includes("decrypt") ||
    errorStr.includes("prekey")
  );
}

// Register handler
const unregisterUnhandled = registerUnhandledRejectionHandler((reason) => {
  if (!isLikelyWhatsAppCryptoError(reason)) return false;

  logger.warn("Crypto error detected; forcing reconnect");
  listener.signalClose({
    status: 499,
    isLoggedOut: false,
    error: reason
  });
  return true; // Handled
});
```

## Common Patterns & Solutions

### Message Deduplication

**Problem**: Baileys may emit duplicate `messages.upsert` events
**Solution**: In-memory cache with TTL

```typescript
const recentMessages = new Map<string, number>(); // dedupeKey → timestamp
const DEDUPE_TTL_MS = 10 * 60 * 1000; // 10 minutes

export function isRecentInboundMessage(dedupeKey: string): boolean {
  const now = Date.now();
  const timestamp = recentMessages.get(dedupeKey);
  if (timestamp && now - timestamp < DEDUPE_TTL_MS) return true;

  recentMessages.set(dedupeKey, now);

  // Prune old entries
  for (const [key, ts] of recentMessages.entries()) {
    if (now - ts >= DEDUPE_TTL_MS) recentMessages.delete(key);
  }

  return false;
}

// Dedupe key format: ${accountId}:${remoteJid}:${messageId}
```

### Echo Tracking (Prevent Self-Reply Loops)

**Problem**: Bot's own messages appear in `messages.upsert` (fromMe=true)
**Solution**: Track outbound message IDs; skip if echoed back

```typescript
export function createEchoTracker(opts: {
  maxItems: number;
  logVerbose: (msg: string) => void
}) {
  const echoIds = new Map<string, number>(); // messageId → timestamp
  const TTL_MS = 5 * 60 * 1000; // 5 minutes

  return {
    track: (messageId: string) => {
      echoIds.set(messageId, Date.now());
      if (echoIds.size > opts.maxItems) {
        const oldest = [...echoIds.entries()].sort((a, b) => a[1] - b[1])[0];
        echoIds.delete(oldest[0]);
      }
    },

    isEcho: (messageId: string): boolean => {
      const timestamp = echoIds.get(messageId);
      if (!timestamp) return false;

      if (Date.now() - timestamp > TTL_MS) {
        echoIds.delete(messageId);
        return false;
      }

      return true;
    },
  };
}

// Usage
const echoTracker = createEchoTracker({ maxItems: 100, logVerbose });

// After sending
const result = await active.sendMessage(to, text);
echoTracker.track(result.messageId);

// On inbound
if (msg.key.fromMe && echoTracker.isEcho(msg.key.id)) {
  logVerbose(`Skipping echo: ${msg.key.id}`);
  continue;
}
```

## Critical Pitfalls to Avoid

### 1. Forgetting to Call `maybeRestoreCredsFromBackup()`

**Problem**: Corrupted `creds.json` causes login loop
**Solution**: Always call before `useMultiFileAuthState()`

```typescript
maybeRestoreCredsFromBackup(authDir);
const { state, saveCreds } = await useMultiFileAuthState(authDir);
```

### 2. Not Handling Code 515 (Restart After Pairing)

**Problem**: Login appears to fail after QR scan
**Solution**: Detect code 515, close socket, retry once

```typescript
if (code === 515) {
  sock.ws?.close();
  const retry = await createWaSocket(false, verbose, { authDir });
  await waitForWaConnection(retry);
}
```

### 3. Race Conditions in `creds.update`

**Problem**: Multiple rapid `creds.update` events can corrupt `creds.json`
**Solution**: Queue credential saves (see authentication section)

### 4. Ignoring WebSocket Errors

**Problem**: Unhandled WebSocket errors crash the process
**Solution**: Attach error handler (see error handling section)

### 5. Not Validating Backup Before Overwriting

**Problem**: Corrupted `creds.json` overwrites good backup
**Solution**: Only backup if new creds are valid JSON

```typescript
const raw = fsSync.readFileSync(credsPath, "utf-8");
try {
  JSON.parse(raw); // Validate before backing up
  fsSync.copyFileSync(credsPath, backupPath);
} catch {
  // Keep existing backup
}
```

### 6. Not Checking `upsert.type`

**Problem**: Processing history/offline messages as live messages
**Solution**: Only process `type === 'notify'` for auto-reply

```typescript
if (upsert.type !== "notify" && upsert.type !== "append") return;
// Mark read for both notify and append
if (upsert.type === "append") continue; // Skip auto-reply for history
```

### 7. Not Detaching Event Listeners on Shutdown

**Problem**: Listener leak in tests/restarts
**Solution**: Detach on close

```typescript
const ev = sock.ev as unknown as {
  off?: (event: string, listener: (...args: unknown[]) => void) => void
};

if (typeof ev.off === "function") {
  ev.off("messages.upsert", handleMessagesUpsert);
  ev.off("connection.update", handleConnectionUpdate);
}
```

### 8. Ignoring `DisconnectReason.loggedOut`

**Problem**: Reconnect loop when session is logged out
**Solution**: Detect logged-out status, break loop

```typescript
if (reason.isLoggedOut) {
  logger.error("WhatsApp session logged out. Relink required.");
  break; // Exit reconnect loop
}
```

## Testing Patterns

### Mock Baileys Socket

```typescript
const mockSock = {
  ev: {
    on: vi.fn(),
    off: vi.fn(),
  },
  ws: { close: vi.fn() },
  sendMessage: vi.fn(),
  sendPresenceUpdate: vi.fn(),
  user: { id: "1234567890@s.whatsapp.net" },
  logger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn()
  },
};
```

### Simulate Connection Events

```typescript
const emitConnectionUpdate = (update: Partial<ConnectionState>) => {
  const handler = mockSock.ev.on.mock.calls
    .find(([event]) => event === "connection.update")?.[1];
  handler?.(update);
};

emitConnectionUpdate({ connection: "open" });
emitConnectionUpdate({
  connection: "close",
  lastDisconnect: {
    error: { output: { statusCode: 401 } }
  }
});
```

### Simulate Inbound Messages

```typescript
const emitMessagesUpsert = (upsert: {
  type: string;
  messages: Array<WAMessage>
}) => {
  const handler = mockSock.ev.on.mock.calls
    .find(([event]) => event === "messages.upsert")?.[1];
  handler?.(upsert);
};

emitMessagesUpsert({
  type: "notify",
  messages: [{
    key: {
      id: "msg-123",
      remoteJid: "15551234567@s.whatsapp.net",
      fromMe: false
    },
    message: { conversation: "Hello" },
    messageTimestamp: Date.now() / 1000,
  }],
});
```

## Decision Trees

### When to Implement Which Pattern

**Authentication Flow**:
- CLI app → Use `login.ts` pattern (terminal QR)
- Web/Desktop UI → Use `login-qr.ts` pattern (programmatic QR)
- Headless/Server → Use programmatic login with QR display URL

**Message Processing**:
- Simple bot → Implement basic inbound monitor
- Multi-account → Add active listener registry
- Production resilience → Add watchdog timer + reconnect loop

**Media Handling**:
- Text-only → Skip media pipeline
- Images → Implement optimization (HEIC conversion, resize, quality sweep)
- All media types → Full media pipeline with size caps

**Group Chat**:
- DM-only bot → Skip group metadata caching
- Group bot with @mentions → Implement mention detection
- Conversation context → Add group history injection

## Quick Reference

### Essential Lifecycle Hooks

1. **Before socket creation**: `maybeRestoreCredsFromBackup(authDir)`
2. **On socket creation**: Attach `creds.update`, `messages.upsert`, `connection.update` handlers
3. **On connection open**: `sock.sendPresenceUpdate("available")`
4. **On shutdown**: Detach event listeners with `ev.off()`
5. **On reconnect**: Reset backoff after healthy uptime

### Configuration Checklist

- [ ] Auth directory path configured per account
- [ ] Credential backup/restore implemented
- [ ] Credential save queueing implemented
- [ ] Code 515 handling implemented
- [ ] WebSocket error handler attached
- [ ] Message deduplication implemented
- [ ] Echo tracking implemented (prevent self-reply loops)
- [ ] Reconnect policy configured
- [ ] Watchdog timer configured
- [ ] Event listener cleanup on shutdown

## Resources

### references/

See `references/implementation-details.md` for additional implementation details from the clawdbot codebase, including:
- Complete code examples
- Edge case handling
- Performance optimization techniques
- Debugging strategies
