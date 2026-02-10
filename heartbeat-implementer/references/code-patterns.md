# Heartbeat Implementation Code Patterns

This document provides language-agnostic pseudocode and concrete TypeScript examples for implementing heartbeat system components.

## 1. Core Runner

### Per-Agent State Structure

```typescript
type HeartbeatAgentState = {
  agentId: string;
  heartbeat?: HeartbeatConfig;
  intervalMs: number;
  lastRunMs?: number;
  nextDueMs: number;
};
```

### Single Timer Scheduler

```typescript
function scheduleNext(agents: HeartbeatAgentState[]) {
  const now = Date.now();
  const soonest = agents.reduce(
    (min, agent) => Math.min(min, agent.nextDueMs),
    Number.POSITIVE_INFINITY
  );

  if (soonest === Number.POSITIVE_INFINITY) return;

  const delay = Math.max(0, soonest - now);
  timer = setTimeout(() => {
    requestHeartbeatNow({ reason: "interval", coalesceMs: 0 });
  }, delay).unref(); // .unref() prevents keeping process alive
}
```

### Guard Chain with Early Exit

```typescript
async function runHeartbeatOnce(params: {
  agentId: string;
  reason?: string;
  cfg: Config;
  deps: HeartbeatDeps;
}): Promise<HeartbeatRunResult> {
  const startMs = Date.now();

  // Guard 1: Global enabled check
  if (!heartbeatsEnabled) {
    emitHeartbeatEvent({ status: "skipped", reason: "disabled" });
    return { status: "skipped", reason: "disabled" };
  }

  // Guard 2: Per-agent enabled check
  if (!isHeartbeatEnabledForAgent(cfg, agentId)) {
    emitHeartbeatEvent({ status: "skipped", reason: "disabled" });
    return { status: "skipped", reason: "disabled" };
  }

  // Guard 3: Valid interval check
  const intervalMs = resolveHeartbeatIntervalMs(heartbeat);
  if (!intervalMs) {
    emitHeartbeatEvent({ status: "skipped", reason: "disabled" });
    return { status: "skipped", reason: "disabled" };
  }

  // Guard 4: Active hours check
  if (!isWithinActiveHours(heartbeat?.activeHours, lastSender)) {
    emitHeartbeatEvent({ status: "skipped", reason: "quiet-hours" });
    return { status: "skipped", reason: "quiet-hours" };
  }

  // Guard 5: Queue empty check
  if (getQueueSize(CommandLane.Main) > 0) {
    emitHeartbeatEvent({ status: "skipped", reason: "requests-in-flight" });
    return { status: "skipped", reason: "requests-in-flight" };
  }

  // Guard 6: Non-empty file check
  const heartbeatMd = await fs.readFile(heartbeatPath, "utf-8").catch(() => undefined);
  if (reason !== "exec-event" && isHeartbeatContentEffectivelyEmpty(heartbeatMd)) {
    emitHeartbeatEvent({ status: "skipped", reason: "empty-heartbeat-file" });
    return { status: "skipped", reason: "empty-heartbeat-file" };
  }

  // Continue to LLM call...
  const reply = await getReplyFromConfig(context, { isHeartbeat: true }, cfg);
  const { stripped, shouldSkip } = stripHeartbeatToken(reply.text, "heartbeat", ackMaxChars);

  // Duplicate check
  if (stripped === entry.lastHeartbeatText && now - entry.lastHeartbeatSentAt < 24 * 60 * 60 * 1000) {
    emitHeartbeatEvent({ status: "skipped", reason: "duplicate" });
    return { status: "skipped", reason: "duplicate" };
  }

  // Delivery
  await deliverOutboundPayloads({ channel, to, payloads: [reply], cfg, deps });

  // Update session
  entry.lastHeartbeatText = stripped;
  entry.lastHeartbeatSentAt = now;
  await store.put(entry);

  // Emit event
  const durationMs = Date.now() - startMs;
  emitHeartbeatEvent({
    status: "sent",
    to,
    preview: stripped.slice(0, 200),
    durationMs,
    channel,
  });

  return { status: "ran", durationMs };
}
```

### Hot-Reload with Preserved Timing

```typescript
function updateConfig(nextCfg: Config) {
  const nextAgents = resolveHeartbeatAgents(nextCfg);
  const now = Date.now();

  const nextState = nextAgents.map((agent) => {
    const prev = state.find((s) => s.agentId === agent.agentId);
    const intervalMs = resolveHeartbeatIntervalMs(agent.heartbeat) ?? 0;

    return {
      agentId: agent.agentId,
      heartbeat: agent.heartbeat,
      intervalMs,
      lastRunMs: prev?.lastRunMs, // Preserve timing state
      nextDueMs: prev?.lastRunMs
        ? prev.lastRunMs + intervalMs
        : now + intervalMs,
    };
  });

  state.splice(0, state.length, ...nextState);
  cfg = nextCfg;
  scheduleNext();
}
```

## 2. Wake System

### Coalescing Scheduler

```typescript
const DEFAULT_COALESCE_MS = 250;
const DEFAULT_RETRY_MS = 1_000;

let handler: HeartbeatWakeHandler | null = null;
let scheduled: NodeJS.Timeout | null = null;
let running = false;

export function setHeartbeatWakeHandler(fn: HeartbeatWakeHandler): void {
  handler = fn;
}

export function requestHeartbeatNow(opts?: {
  reason?: string;
  coalesceMs?: number;
}): void {
  if (!handler) return;

  const delay = opts?.coalesceMs ?? DEFAULT_COALESCE_MS;

  if (scheduled) {
    clearTimeout(scheduled);
  }

  const schedule = () => {
    scheduled = setTimeout(async () => {
      scheduled = null;

      if (running) {
        schedule(); // Re-schedule after current run
        return;
      }

      running = true;
      const result = await handler!({ reason: opts?.reason });
      running = false;

      // Retry on requests-in-flight
      if (result.status === "skipped" && result.reason === "requests-in-flight") {
        setTimeout(() => requestHeartbeatNow(opts), DEFAULT_RETRY_MS);
      } else if (scheduled) {
        // Another wake was scheduled during this run
        schedule();
      }
    }, delay);
  };

  schedule();
}

export function hasPendingHeartbeatWake(): boolean {
  return scheduled !== null;
}

export function hasHeartbeatWakeHandler(): boolean {
  return handler !== null;
}
```

## 3. Event System

### Event Payload & Pub/Sub

```typescript
type HeartbeatEventPayload = {
  ts: number;
  status: "sent" | "ok-empty" | "ok-token" | "skipped" | "failed";
  to?: string;
  preview?: string;
  durationMs?: number;
  hasMedia?: boolean;
  reason?: string;
  channel?: string;
  silent?: boolean;
  indicatorType?: "ok" | "alert" | "error";
};

let lastEvent: HeartbeatEventPayload | null = null;
const listeners = new Set<(evt: HeartbeatEventPayload) => void>();

export function emitHeartbeatEvent(payload: Omit<HeartbeatEventPayload, "ts">): void {
  const evt: HeartbeatEventPayload = { ts: Date.now(), ...payload };
  lastEvent = evt;
  listeners.forEach((listener) => listener(evt));
}

export function onHeartbeatEvent(
  listener: (evt: HeartbeatEventPayload) => void
): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function getLastHeartbeatEvent(): HeartbeatEventPayload | null {
  return lastEvent;
}
```

### Indicator Type Resolution

```typescript
function resolveIndicatorType(
  status: HeartbeatEventPayload["status"],
  reason?: string
): HeartbeatEventPayload["indicatorType"] {
  if (status === "sent") return "alert";
  if (status === "ok-token" || status === "ok-empty") return "ok";
  if (status === "failed") return "error";
  return "ok"; // skipped
}
```

## 4. Token Handling

### Strip Heartbeat Token

```typescript
const HEARTBEAT_TOKEN = "HEARTBEAT_OK";

function stripHeartbeatToken(
  text: string,
  mode: "heartbeat" | "message",
  maxAckChars: number
): { stripped: string; shouldSkip: boolean } {
  let normalized = text
    .replace(/<b>/gi, "<b>")
    .replace(/<\/b>/gi, "</b>")
    .replace(/<i>/gi, "<i>")
    .replace(/<\/i>/gi, "</i>");

  // Strip from start
  while (
    normalized.startsWith(HEARTBEAT_TOKEN) ||
    normalized.startsWith(`<b>${HEARTBEAT_TOKEN}</b>`) ||
    normalized.startsWith(`<i>${HEARTBEAT_TOKEN}</i>`) ||
    normalized.startsWith(`**${HEARTBEAT_TOKEN}**`) ||
    normalized.startsWith(`_${HEARTBEAT_TOKEN}_`)
  ) {
    normalized = normalized
      .replace(new RegExp(`^${HEARTBEAT_TOKEN}`), "")
      .replace(new RegExp(`^<b>${HEARTBEAT_TOKEN}</b>`), "")
      .replace(new RegExp(`^<i>${HEARTBEAT_TOKEN}</i>`), "")
      .replace(new RegExp(`^\\*\\*${HEARTBEAT_TOKEN}\\*\\*`), "")
      .replace(new RegExp(`^_${HEARTBEAT_TOKEN}_`), "")
      .trim();
  }

  // Strip from end
  while (
    normalized.endsWith(HEARTBEAT_TOKEN) ||
    normalized.endsWith(`<b>${HEARTBEAT_TOKEN}</b>`) ||
    normalized.endsWith(`<i>${HEARTBEAT_TOKEN}</i>`) ||
    normalized.endsWith(`**${HEARTBEAT_TOKEN}**`) ||
    normalized.endsWith(`_${HEARTBEAT_TOKEN}_`)
  ) {
    normalized = normalized
      .replace(new RegExp(`${HEARTBEAT_TOKEN}$`), "")
      .replace(new RegExp(`<b>${HEARTBEAT_TOKEN}</b>$`), "")
      .replace(new RegExp(`<i>${HEARTBEAT_TOKEN}</i>$`), "")
      .replace(new RegExp(`\\*\\*${HEARTBEAT_TOKEN}\\*\\*$`), "")
      .replace(new RegExp(`_${HEARTBEAT_TOKEN}_$`), "")
      .trim();
  }

  const stripped = normalized.trim();
  const shouldSkip = mode === "heartbeat" && stripped.length <= maxAckChars;

  return { stripped, shouldSkip };
}
```

### Empty File Detection

```typescript
function isHeartbeatContentEffectivelyEmpty(content: string | undefined): boolean {
  if (content === undefined || content === null) return false; // Missing file should not skip

  const lines = content.split("\n");

  for (const line of lines) {
    const trimmed = line.trim();

    // Skip blank lines
    if (trimmed === "") continue;

    // Skip ATX headers (e.g., "# Heading", "## Section")
    if (/^#+\s/.test(trimmed)) continue;

    // Skip empty list items (e.g., "- [ ]", "- [ ] ")
    if (/^-\s*\[\s*\]$/.test(trimmed)) continue;

    // If we reach here, there's actionable content
    return false;
  }

  // All lines were blank, headers, or empty checkboxes
  return true;
}
```

## 5. Configuration Schema

### Agent Configuration Type

```typescript
type HeartbeatConfig = {
  every?: string;              // Duration string (e.g., "30m", "1h")
  prompt?: string;             // Custom prompt
  target?: "last" | "none" | string; // Channel ID or special value
  to?: string;                 // Recipient override
  model?: string;              // Model override
  session?: string;            // Session key
  ackMaxChars?: number;        // Threshold (default: 300)
  includeReasoning?: boolean;  // Reasoning delivery
  activeHours?: {
    start?: string;            // "HH:MM" 24h format
    end?: string;              // "HH:MM" 24h format
    timezone?: string;         // "user" | "local" | IANA TZ
  };
};
```

### Channel Visibility Type

```typescript
type ChannelHeartbeatVisibility = {
  showOk?: boolean;        // Show HEARTBEAT_OK acks (default: false)
  showAlerts?: boolean;    // Show alerts (default: true)
  useIndicator?: boolean;  // Emit indicator events (default: true)
};

type ResolvedHeartbeatVisibility = {
  showOk: boolean;
  showAlerts: boolean;
  useIndicator: boolean;
};

const DEFAULT_VISIBILITY: ResolvedHeartbeatVisibility = {
  showOk: false,
  showAlerts: true,
  useIndicator: true,
};
```

### Duration Parsing

```typescript
function parseDurationMs(
  value: string,
  options?: { defaultUnit?: "ms" | "s" | "m" | "h" }
): number | null {
  const match = value.match(/^(\d+)([smh]?)$/);
  if (!match) return null;

  const num = parseInt(match[1], 10);
  const unit = match[2] || options?.defaultUnit || "m";

  switch (unit) {
    case "ms": return num;
    case "s": return num * 1000;
    case "m": return num * 60 * 1000;
    case "h": return num * 60 * 60 * 1000;
    default: return null;
  }
}
```

## 6. Active Hours Validation

### Timezone-Aware Active Hours Check

```typescript
function isWithinActiveHours(
  activeHours: HeartbeatConfig["activeHours"],
  lastSender: { timezone?: string }
): boolean {
  if (!activeHours?.start || !activeHours?.end) return true;

  // Resolve timezone
  let tz: string;
  if (activeHours.timezone === "user") {
    tz = lastSender.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone;
  } else if (activeHours.timezone === "local") {
    tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
  } else {
    tz = activeHours.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone;
  }

  // Get current time in target timezone
  const now = new Date();
  const formatter = new Intl.DateTimeFormat("en-US", {
    timeZone: tz,
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });

  const currentTime = formatter.format(now); // "HH:MM"
  const [currentHour, currentMinute] = currentTime.split(":").map(Number);
  const currentMinutes = currentHour * 60 + currentMinute;

  // Parse start/end times
  const [startHour, startMinute] = activeHours.start.split(":").map(Number);
  const [endHour, endMinute] = activeHours.end.split(":").map(Number);
  const startMinutes = startHour * 60 + startMinute;
  const endMinutes = endHour === 24 ? 24 * 60 : endHour * 60 + endMinute;

  // Handle overnight range (e.g., 22:00 - 08:00)
  if (endMinutes <= startMinutes) {
    return currentMinutes >= startMinutes || currentMinutes < endMinutes;
  }

  // Normal range (e.g., 09:00 - 21:00)
  return currentMinutes >= startMinutes && currentMinutes < endMinutes;
}
```

## 7. Duplicate Detection

### Per-Session Duplicate Tracking

```typescript
type SessionEntry = {
  agentId: string;
  sessionKey: string;
  lastHeartbeatText?: string;
  lastHeartbeatSentAt?: number;
  updatedAt: number;
  // ... other session fields
};

function checkDuplicate(
  entry: SessionEntry,
  normalizedText: string,
  nowMs: number
): boolean {
  const dupeWindow = 24 * 60 * 60 * 1000; // 24 hours
  const lastText = entry.lastHeartbeatText;
  const lastSentAt = entry.lastHeartbeatSentAt ?? 0;

  return lastText === normalizedText && nowMs - lastSentAt < dupeWindow;
}
```

## 8. Session Timestamp Restoration

### Preserve Idle Expiry Behavior

```typescript
async function runHeartbeatOnce(params: HeartbeatParams): Promise<HeartbeatRunResult> {
  const entry = await store.get(agentId, sessionKey);
  const originalUpdatedAt = entry.updatedAt;

  // ... run heartbeat ...

  // Restore updatedAt if heartbeat produced no actionable content
  if (
    status === "ok-token" ||
    status === "ok-empty" ||
    (status === "skipped" && reason === "duplicate")
  ) {
    entry.updatedAt = originalUpdatedAt;
    await store.put(entry);
  }

  return { status, durationMs };
}
```

## 9. Delivery Target Resolution

### Resolve "last" Channel

```typescript
function resolveLastChannel(
  sessionHistory: Message[]
): { channel: string; recipient: string } | null {
  // Find most recent message from user
  for (let i = sessionHistory.length - 1; i >= 0; i--) {
    const msg = sessionHistory[i];
    if (msg.direction === "inbound") {
      return {
        channel: msg.provider, // e.g., "telegram", "whatsapp"
        recipient: msg.from,   // e.g., phone number, chat ID
      };
    }
  }
  return null;
}
```

## 10. Integration Patterns

### Gateway Startup

```typescript
// src/gateway/server.ts
import { startHeartbeatRunner, onHeartbeatEvent } from "./heartbeat";

export async function startGateway(cfg: Config) {
  // Start heartbeat runner
  const heartbeatRunner = startHeartbeatRunner({ cfg });

  // Subscribe to events and broadcast to WebSocket clients
  const unsubHeartbeat = onHeartbeatEvent((evt) => {
    broadcast("heartbeat", evt);
  });

  // Return cleanup function
  return {
    stop: () => {
      heartbeatRunner.stop();
      unsubHeartbeat();
    },
  };
}
```

### Cron Integration

```typescript
// src/cron/service.ts
import { requestHeartbeatNow, runHeartbeatOnce } from "./heartbeat";

async function executeCronJob(job: CronJob) {
  // Enqueue system event with job result
  enqueueSystemEvent({ text: job.output, cfg, deps });

  // Wake heartbeat
  if (job.wakeMode === "now") {
    // Retry loop for up to 2 minutes if busy
    const maxWaitMs = 120_000;
    const start = Date.now();

    while (Date.now() - start < maxWaitMs) {
      const result = await runHeartbeatOnce({ cfg, agentId, reason: "cron", deps });

      if (result.status !== "skipped" || result.reason !== "requests-in-flight") {
        break;
      }

      await sleep(1000);
    }
  } else {
    // Piggyback on next scheduled heartbeat
    requestHeartbeatNow({ reason: "cron" });
  }
}
```

### Webhook Integration

```typescript
// src/gateway/hooks.ts
import { requestHeartbeatNow, enqueueSystemEvent } from "./heartbeat";

export function setupWebhooks(app: Express, cfg: Config, deps: Deps) {
  app.post("/hooks/wake", async (req, res) => {
    // Authenticate
    const token = req.headers.authorization?.replace("Bearer ", "");
    if (token !== cfg.webhooks?.token) {
      return res.status(401).json({ error: "Unauthorized" });
    }

    // Parse body
    const { text, mode = "next-heartbeat" } = req.body;

    // Enqueue system event
    enqueueSystemEvent({ text, cfg, deps });

    // Trigger heartbeat wake
    if (mode === "now") {
      requestHeartbeatNow({ reason: "hook:wake" });
    }

    res.json({ status: "ok" });
  });
}
```

## 11. Testing Patterns

### Token Stripping Test

```typescript
import { describe, it, expect } from "vitest";
import { stripHeartbeatToken } from "./heartbeat";

describe("stripHeartbeatToken", () => {
  it("strips bare token", () => {
    const { stripped, shouldSkip } = stripHeartbeatToken(
      "HEARTBEAT_OK",
      "heartbeat",
      300
    );
    expect(stripped).toBe("");
    expect(shouldSkip).toBe(true);
  });

  it("strips HTML-wrapped token", () => {
    const { stripped, shouldSkip } = stripHeartbeatToken(
      "<b>HEARTBEAT_OK</b>",
      "heartbeat",
      300
    );
    expect(stripped).toBe("");
    expect(shouldSkip).toBe(true);
  });

  it("does not strip token in middle of text", () => {
    const { stripped } = stripHeartbeatToken(
      "The status is HEARTBEAT_OK for now.",
      "heartbeat",
      300
    );
    expect(stripped).toBe("The status is HEARTBEAT_OK for now.");
  });

  it("respects ackMaxChars threshold", () => {
    const { stripped, shouldSkip } = stripHeartbeatToken(
      "HEARTBEAT_OK\nShort message",
      "heartbeat",
      50
    );
    expect(stripped).toBe("Short message");
    expect(shouldSkip).toBe(true); // "Short message".length === 13 < 50
  });
});
```

### Scheduler Test with Fake Timers

```typescript
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { startHeartbeatRunner } from "./heartbeat";

describe("heartbeat scheduler", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("schedules multiple agents with different intervals", async () => {
    const cfg = {
      agents: {
        list: [
          { agentId: "agent1", heartbeat: { every: "10m" } },
          { agentId: "agent2", heartbeat: { every: "15m" } },
        ],
      },
    };

    const runner = startHeartbeatRunner({ cfg });
    const runSpy = vi.spyOn(runner, "runHeartbeatOnce");

    // Advance 10 minutes
    vi.advanceTimersByTime(10 * 60 * 1000);
    expect(runSpy).toHaveBeenCalledWith({ agentId: "agent1", reason: "interval" });

    // Advance 5 more minutes (total 15)
    vi.advanceTimersByTime(5 * 60 * 1000);
    expect(runSpy).toHaveBeenCalledWith({ agentId: "agent2", reason: "interval" });
  });
});
```
