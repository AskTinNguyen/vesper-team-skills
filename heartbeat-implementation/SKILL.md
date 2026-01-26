# heartbeat-implementation Skill

**Purpose:** Guide implementation of heartbeat periodic awareness systems in applications and repositories, following proven architectural patterns from production systems.

## Overview

This skill helps you implement a "heartbeat" system - a periodic awareness loop that allows AI agents to proactively check on tasks and surface important information without being explicitly messaged. Think of it as giving your AI assistant peripheral vision.

**When to use this skill:**
- Building AI assistant applications that need proactive awareness
- Adding background monitoring to existing AI systems
- Implementing task reminder/checklist systems
- Creating agent-driven notification systems
- Setting up periodic health checks with AI contextualization

**When NOT to use this skill:**
- Simple cron jobs (use system cron instead)
- Real-time event streaming (use WebSockets/SSE instead)
- Exact-time scheduling requirements (use task scheduler instead)
- Non-AI background jobs (use workers/queues instead)

---

<critical_sequence name="heartbeat-implementation" enforce_order="strict">

## Implementation Workflow

<step number="1" required="true">
### Step 1: Requirements Gathering

**Understand the use case:**

Ask the user these questions (use AskUserQuestion if not already clear):

1. **What should the heartbeat monitor?**
   - Task checklist in file
   - System health/logs
   - Background job status
   - Custom data source

2. **How often should it run?**
   - Default: 30 minutes
   - Options: 15m, 30m, 1h, 2h, custom

3. **Where should alerts be delivered?**
   - Chat platform (Slack, Telegram, Discord, WhatsApp)
   - Web UI notification
   - Email
   - Webhook
   - Console/log only (for testing)

4. **What tech stack?**
   - TypeScript/Node.js
   - Python
   - Ruby
   - Go
   - Other

5. **Existing agent/LLM integration?**
   - Already integrated (which SDK?)
   - Need to add (recommend providers)
   - Custom API

**Create implementation checklist:**

Based on answers, create a task list:

```markdown
- [ ] Phase 1: Core scheduler setup
- [ ] Phase 2: LLM integration & token stripping
- [ ] Phase 3: Smart suppression (duplicates, empty content)
- [ ] Phase 4: Active hours & quiet time
- [ ] Phase 5: Delivery integration
- [ ] Phase 6: Testing & validation
```

**BLOCKING GATE:** Do not proceed to Step 2 until requirements are clear and user has approved the implementation plan.
</step>

<step number="2" required="true" depends_on="1">
### Step 2: Setup Core Scheduler

**Goal:** Create a timer-based scheduler that wakes at configured intervals.

**Implementation pattern (adapt to language):**

<language="typescript">
```typescript
// heartbeat-scheduler.ts
interface AgentSchedule {
  agentId: string;
  intervalMs: number;
  lastRunAt: number;
  nextRunAt: number;
}

export class HeartbeatScheduler {
  private schedules = new Map<string, AgentSchedule>();
  private timer: NodeJS.Timeout | null = null;

  start(agents: Array<{ id: string; intervalMs: number }>) {
    // Initialize schedules
    for (const agent of agents) {
      const now = Date.now();
      this.schedules.set(agent.id, {
        agentId: agent.id,
        intervalMs: agent.intervalMs,
        lastRunAt: now,
        nextRunAt: now + agent.intervalMs,
      });
    }

    // Poll every 10 seconds
    this.timer = setInterval(() => {
      this.tick();
    }, 10_000);
  }

  private tick() {
    const now = Date.now();
    for (const schedule of this.schedules.values()) {
      if (now >= schedule.nextRunAt) {
        this.executeHeartbeat(schedule.agentId);
        schedule.lastRunAt = now;
        schedule.nextRunAt = now + schedule.intervalMs;
      }
    }
  }

  private async executeHeartbeat(agentId: string) {
    console.log(`[Heartbeat] Running for agent: ${agentId}`);
    // TODO: Implement in next step
  }

  stop() {
    if (this.timer) clearInterval(this.timer);
  }
}
```
</language>

<language="python">
```python
# heartbeat_scheduler.py
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List

class AgentSchedule:
    def __init__(self, agent_id: str, interval_ms: int):
        self.agent_id = agent_id
        self.interval_ms = interval_ms
        now = datetime.now()
        self.last_run_at = now
        self.next_run_at = now + timedelta(milliseconds=interval_ms)

class HeartbeatScheduler:
    def __init__(self):
        self.schedules: Dict[str, AgentSchedule] = {}
        self.running = False

    async def start(self, agents: List[dict]):
        # Initialize schedules
        for agent in agents:
            schedule = AgentSchedule(agent['id'], agent['interval_ms'])
            self.schedules[agent['id']] = schedule

        # Poll every 10 seconds
        self.running = True
        while self.running:
            await self.tick()
            await asyncio.sleep(10)

    async def tick(self):
        now = datetime.now()
        for schedule in self.schedules.values():
            if now >= schedule.next_run_at:
                await self.execute_heartbeat(schedule.agent_id)
                schedule.last_run_at = now
                schedule.next_run_at = now + timedelta(milliseconds=schedule.interval_ms)

    async def execute_heartbeat(self, agent_id: str):
        print(f"[Heartbeat] Running for agent: {agent_id}")
        # TODO: Implement in next step

    def stop(self):
        self.running = False
```
</language>

**Configuration file structure:**

```json5
// config.json5
{
  agents: [
    {
      id: "main",
      heartbeat: {
        every: "30m",  // Will parse to 1800000ms
        enabled: true
      }
    }
  ]
}
```

**Add duration parser:**

```typescript
// utils/duration.ts
export function parseDuration(duration: string): number {
  const match = duration.match(/^(\d+)(m|h|s)$/);
  if (!match) throw new Error(`Invalid duration: ${duration}`);

  const [, value, unit] = match;
  const num = parseInt(value, 10);

  switch (unit) {
    case 's': return num * 1000;
    case 'm': return num * 60 * 1000;
    case 'h': return num * 60 * 60 * 1000;
    default: throw new Error(`Unknown unit: ${unit}`);
  }
}
```

**Test the scheduler:**

```typescript
// test-scheduler.ts
const scheduler = new HeartbeatScheduler();
scheduler.start([
  { id: 'main', intervalMs: 30_000 } // 30 seconds for testing
]);

// Let it run for 2 minutes, should see ~4 heartbeats
setTimeout(() => scheduler.stop(), 120_000);
```

**Verification:**
- [ ] Scheduler starts without errors
- [ ] `executeHeartbeat` logs appear at correct intervals
- [ ] Multiple agents have independent schedules
</step>

<step number="3" required="true" depends_on="2">
### Step 3: LLM Integration & Token Stripping

**Goal:** Call LLM with heartbeat prompt and implement smart suppression via acknowledgment token.

**Define the heartbeat contract:**

```typescript
// constants.ts
export const HEARTBEAT_TOKEN = 'HEARTBEAT_OK';
export const DEFAULT_HEARTBEAT_PROMPT = `
Read HEARTBEAT.md if it exists in the workspace. Follow the checklist strictly.

If nothing needs attention, reply with exactly: HEARTBEAT_OK

If something requires action, provide a brief alert message.
`.trim();
```

**Implement LLM call:**

```typescript
// heartbeat-executor.ts
import Anthropic from '@anthropic-ai/sdk';

interface HeartbeatConfig {
  prompt?: string;
  model?: string;
  ackMaxChars?: number;
}

export async function executeHeartbeat(
  agentId: string,
  config: HeartbeatConfig,
  anthropic: Anthropic
): Promise<{ status: string; message?: string }> {
  const prompt = config.prompt ?? DEFAULT_HEARTBEAT_PROMPT;

  // Call LLM
  const response = await anthropic.messages.create({
    model: config.model ?? 'claude-sonnet-4-5-20250929',
    max_tokens: 1024,
    messages: [{
      role: 'user',
      content: prompt
    }]
  });

  const reply = response.content[0].type === 'text'
    ? response.content[0].text
    : '';

  // Strip HEARTBEAT_OK token
  const processed = stripHeartbeatToken(reply, config.ackMaxChars ?? 300);

  if (processed.length === 0) {
    return { status: 'ok-token' }; // Suppressed
  }

  return { status: 'sent', message: processed };
}
```

**Implement token stripping with markup handling:**

```typescript
// token-stripper.ts
export function stripHeartbeatToken(text: string, ackMaxChars: number): string {
  const TOKEN = 'HEARTBEAT_OK';

  // Step 1: Normalize markup (HTML/Markdown)
  let normalized = text
    .replace(/<[^>]+>/g, '') // Strip HTML tags
    .replace(/[*_~`]/g, '')  // Strip Markdown formatting
    .trim();

  // Step 2: Check for token at edges only
  const hasTokenAtStart = normalized.startsWith(TOKEN);
  const hasTokenAtEnd = normalized.endsWith(TOKEN);

  if (!hasTokenAtStart && !hasTokenAtEnd) {
    return text; // Token not at edges, keep as-is
  }

  // Step 3: Strip token
  let remainder = normalized
    .replace(new RegExp(`^${TOKEN}\\s*`, 'i'), '')
    .replace(new RegExp(`\\s*${TOKEN}$`, 'i'), '')
    .trim();

  // Step 4: Suppress if remainder is short acknowledgment
  if (remainder.length <= ackMaxChars) {
    return ''; // Suppress delivery
  }

  return remainder; // Deliver remainder
}
```

**Test token stripping:**

```typescript
// token-stripper.test.ts
import { stripHeartbeatToken } from './token-stripper';

describe('stripHeartbeatToken', () => {
  it('suppresses HEARTBEAT_OK only', () => {
    expect(stripHeartbeatToken('HEARTBEAT_OK', 300)).toBe('');
  });

  it('suppresses markup-wrapped token', () => {
    expect(stripHeartbeatToken('<b>HEARTBEAT_OK</b>', 300)).toBe('');
    expect(stripHeartbeatToken('**HEARTBEAT_OK**', 300)).toBe('');
  });

  it('delivers content after short ack', () => {
    const text = 'HEARTBEAT_OK all systems nominal';
    expect(stripHeartbeatToken(text, 300)).toBe('all systems nominal');
  });

  it('keeps token in middle', () => {
    const text = 'Status: HEARTBEAT_OK for now';
    expect(stripHeartbeatToken(text, 300)).toBe(text);
  });
});
```

**Verification:**
- [ ] LLM call executes successfully
- [ ] `HEARTBEAT_OK` responses suppressed
- [ ] Markup-wrapped tokens detected and stripped
- [ ] Content after short acks delivered correctly
</step>

<step number="4" required="true" depends_on="3">
### Step 4: Smart Suppression (Empty Content & Duplicates)

**Goal:** Skip expensive LLM calls when content is empty; prevent nagging with duplicate detection.

**Implement content emptiness check:**

```typescript
// content-checker.ts
import { readFile } from 'fs/promises';
import { existsSync } from 'fs';

export async function isHeartbeatContentEmpty(
  workspaceDir: string,
  filename: string = 'HEARTBEAT.md'
): Promise<boolean> {
  const filePath = `${workspaceDir}/${filename}`;

  // If file doesn't exist, let LLM decide (not empty)
  if (!existsSync(filePath)) {
    return false;
  }

  const content = await readFile(filePath, 'utf-8');

  // Remove comments (lines starting with #)
  // Remove whitespace
  const actionable = content
    .split('\n')
    .filter(line => !line.trim().startsWith('#'))
    .join('\n')
    .trim();

  return actionable.length === 0;
}
```

**Implement duplicate detection:**

```typescript
// duplicate-tracker.ts
interface DuplicateTracker {
  lastText: string | null;
  lastSentAt: number | null;
  windowMs: number;
}

const trackers = new Map<string, DuplicateTracker>();

export function isDuplicate(
  agentId: string,
  text: string,
  hasMedia: boolean = false
): boolean {
  // Media presence disables deduplication
  if (hasMedia) return false;

  const tracker = trackers.get(agentId) ?? {
    lastText: null,
    lastSentAt: null,
    windowMs: 24 * 60 * 60 * 1000 // 24 hours
  };

  if (!tracker.lastText || !tracker.lastSentAt) {
    return false;
  }

  const now = Date.now();
  const isWithinWindow = (now - tracker.lastSentAt) < tracker.windowMs;

  if (!isWithinWindow) return false;

  // Normalize whitespace for comparison
  const normalize = (s: string) => s.replace(/\s+/g, ' ').trim();

  return normalize(text) === normalize(tracker.lastText);
}

export function recordHeartbeat(agentId: string, text: string) {
  const tracker = trackers.get(agentId) ?? { windowMs: 24 * 60 * 60 * 1000, lastText: null, lastSentAt: null };
  tracker.lastText = text;
  tracker.lastSentAt = Date.now();
  trackers.set(agentId, tracker);
}
```

**Update executor with guards:**

```typescript
// heartbeat-executor.ts (updated)
export async function runHeartbeatOnce(
  agentId: string,
  config: HeartbeatConfig,
  workspaceDir: string,
  anthropic: Anthropic
): Promise<HeartbeatResult> {
  // Guard 1: Content emptiness (save API cost)
  if (await isHeartbeatContentEmpty(workspaceDir)) {
    return { status: 'skipped', reason: 'ok-empty' };
  }

  // Execute LLM call
  const result = await executeHeartbeat(agentId, config, anthropic);

  // Guard 2: Duplicate detection
  if (result.message && isDuplicate(agentId, result.message)) {
    return { status: 'skipped', reason: 'duplicate' };
  }

  // Record for future duplicate checks
  if (result.message) {
    recordHeartbeat(agentId, result.message);
  }

  return result;
}
```

**Verification:**
- [ ] Empty HEARTBEAT.md files skip LLM call
- [ ] Files with only headers skip LLM call
- [ ] Files with checklist items trigger LLM call
- [ ] Duplicate messages within 24h suppressed
- [ ] New messages after window delivered
</step>

<step number="5" required="true" depends_on="4">
### Step 5: Active Hours & Quiet Time

**Goal:** Respect user's quiet hours with timezone-aware scheduling.

**Add timezone dependency:**

```bash
# TypeScript/Node
npm install luxon
npm install -D @types/luxon

# Python
pip install pytz
```

**Implement active hours check:**

<language="typescript">
```typescript
// active-hours.ts
import { DateTime } from 'luxon';

interface ActiveHoursConfig {
  start: string;   // "08:00"
  end: string;     // "24:00"
  timezone: string; // "America/New_York" or "user" or "local"
}

export function isWithinActiveHours(
  config: ActiveHoursConfig | undefined,
  userTimezone: string = 'America/New_York'
): boolean {
  if (!config) return true; // No active hours = always active

  // Resolve timezone
  const tz = config.timezone === 'user'
    ? userTimezone
    : config.timezone === 'local'
    ? DateTime.local().zoneName
    : config.timezone;

  // Get current time in resolved timezone
  const now = DateTime.now().setZone(tz);

  // Parse start/end times
  const [startH, startM] = config.start.split(':').map(Number);
  const [endH, endM] = config.end === '24:00'
    ? [24, 0]
    : config.end.split(':').map(Number);

  const start = now.set({ hour: startH, minute: startM, second: 0 });
  const end = now.set({ hour: endH, minute: endM, second: 0 });

  // Check if now is within window
  return now >= start && now < end;
}
```
</language>

<language="python">
```python
# active_hours.py
from datetime import datetime
import pytz
from typing import Optional

class ActiveHoursConfig:
    def __init__(self, start: str, end: str, timezone: str):
        self.start = start
        self.end = end
        self.timezone = timezone

def is_within_active_hours(
    config: Optional[ActiveHoursConfig],
    user_timezone: str = 'America/New_York'
) -> bool:
    if not config:
        return True  # No active hours = always active

    # Resolve timezone
    if config.timezone == 'user':
        tz = pytz.timezone(user_timezone)
    elif config.timezone == 'local':
        tz = pytz.timezone('UTC')  # Or detect system TZ
    else:
        tz = pytz.timezone(config.timezone)

    # Get current time in resolved timezone
    now = datetime.now(tz)

    # Parse start/end times
    start_h, start_m = map(int, config.start.split(':'))
    if config.end == '24:00':
        end_h, end_m = 24, 0
    else:
        end_h, end_m = map(int, config.end.split(':'))

    start = now.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
    end = now.replace(hour=end_h, minute=end_m, second=0, microsecond=0)

    # Check if now is within window
    return start <= now < end
```
</language>

**Update config schema:**

```json5
// config.json5
{
  agents: [
    {
      id: "main",
      timezone: "America/New_York",
      heartbeat: {
        every: "30m",
        activeHours: {
          start: "08:00",
          end: "24:00",
          timezone: "user"  // Use agent's timezone
        }
      }
    }
  ]
}
```

**Add guard to executor:**

```typescript
// heartbeat-executor.ts (updated)
export async function runHeartbeatOnce(
  agentId: string,
  config: HeartbeatConfig,
  workspaceDir: string,
  anthropic: Anthropic
): Promise<HeartbeatResult> {
  // Guard 1: Active hours check
  if (!isWithinActiveHours(config.activeHours, config.userTimezone)) {
    return { status: 'skipped', reason: 'quiet-hours' };
  }

  // Guard 2: Content emptiness
  if (await isHeartbeatContentEmpty(workspaceDir)) {
    return { status: 'skipped', reason: 'ok-empty' };
  }

  // ... rest of execution
}
```

**Test across timezones:**

```typescript
// active-hours.test.ts
describe('isWithinActiveHours', () => {
  it('respects Eastern Time active hours', () => {
    // Mock time to 3am EST
    const config = {
      start: '08:00',
      end: '24:00',
      timezone: 'America/New_York'
    };
    // Should skip at 3am
    expect(isWithinActiveHours(config)).toBe(false);
  });

  it('respects Pacific Time active hours', () => {
    const config = {
      start: '08:00',
      end: '24:00',
      timezone: 'America/Los_Angeles'
    };
    // Test at various hours
  });
});
```

**Verification:**
- [ ] Heartbeat skips outside active hours
- [ ] Timezone conversion works correctly (test EST, PST, UTC)
- [ ] "24:00" end time handled correctly
- [ ] DST transitions handled (test spring/fall)
</step>

<step number="6" required="true" depends_on="5">
### Step 6: Delivery Integration

**Goal:** Connect heartbeat output to actual delivery channels (chat, email, webhook, etc.).

**Define delivery interface:**

```typescript
// delivery.ts
export interface DeliveryTarget {
  channel: string;    // "telegram", "slack", "discord", "webhook", etc.
  recipient: string;  // Chat ID, phone number, email, URL
}

export interface DeliveryPayload {
  text: string;
  hasMedia?: boolean;
  mediaUrls?: string[];
}

export async function deliverHeartbeat(
  target: DeliveryTarget,
  payload: DeliveryPayload
): Promise<void> {
  switch (target.channel) {
    case 'telegram':
      await deliverToTelegram(target.recipient, payload);
      break;
    case 'slack':
      await deliverToSlack(target.recipient, payload);
      break;
    case 'discord':
      await deliverToDiscord(target.recipient, payload);
      break;
    case 'webhook':
      await deliverToWebhook(target.recipient, payload);
      break;
    case 'console':
      console.log(`[Heartbeat] ${payload.text}`);
      break;
    default:
      throw new Error(`Unknown channel: ${target.channel}`);
  }
}
```

**Implement channel adapters (example: Telegram):**

```typescript
// channels/telegram.ts
import TelegramBot from 'node-telegram-bot-api';

let bot: TelegramBot | null = null;

export function initTelegram(token: string) {
  bot = new TelegramBot(token, { polling: false });
}

export async function deliverToTelegram(
  chatId: string,
  payload: DeliveryPayload
): Promise<void> {
  if (!bot) throw new Error('Telegram not initialized');

  await bot.sendMessage(chatId, payload.text, {
    parse_mode: 'Markdown'
  });

  // Send media if present
  if (payload.hasMedia && payload.mediaUrls) {
    for (const url of payload.mediaUrls) {
      await bot.sendPhoto(chatId, url);
    }
  }
}
```

**Add target resolution:**

```typescript
// target-resolver.ts
export function resolveDeliveryTarget(
  config: HeartbeatConfig,
  sessionContext?: { lastChannel?: string; lastRecipient?: string }
): DeliveryTarget {
  // Explicit target in config
  if (config.target && config.target !== 'last' && config.target !== 'none') {
    return {
      channel: config.target,
      recipient: config.to ?? ''
    };
  }

  // "last" = use session context
  if (config.target === 'last' && sessionContext) {
    return {
      channel: sessionContext.lastChannel ?? 'console',
      recipient: sessionContext.lastRecipient ?? ''
    };
  }

  // "none" = skip delivery
  if (config.target === 'none') {
    throw new Error('Delivery target is "none"');
  }

  // Default: console
  return { channel: 'console', recipient: '' };
}
```

**Integrate with executor:**

```typescript
// heartbeat-executor.ts (final)
export async function runHeartbeatOnce(
  agentId: string,
  config: HeartbeatConfig,
  workspaceDir: string,
  anthropic: Anthropic,
  sessionContext?: SessionContext
): Promise<HeartbeatResult> {
  // All guards...
  if (!isWithinActiveHours(config.activeHours, config.userTimezone)) {
    return { status: 'skipped', reason: 'quiet-hours' };
  }

  if (await isHeartbeatContentEmpty(workspaceDir)) {
    return { status: 'skipped', reason: 'ok-empty' };
  }

  // Execute LLM call
  const result = await executeHeartbeat(agentId, config, anthropic);

  if (!result.message) {
    return { status: 'ok-token' }; // Suppressed
  }

  // Duplicate check
  if (isDuplicate(agentId, result.message)) {
    return { status: 'skipped', reason: 'duplicate' };
  }

  // Resolve delivery target
  const target = resolveDeliveryTarget(config, sessionContext);

  // Deliver
  await deliverHeartbeat(target, { text: result.message });

  // Record
  recordHeartbeat(agentId, result.message);

  return { status: 'sent', message: result.message };
}
```

**Verification:**
- [ ] Console delivery works (logging)
- [ ] At least one real channel integrated (Telegram/Slack/etc.)
- [ ] Target resolution works ("last", explicit channel, "none")
- [ ] Media attachments delivered correctly (if applicable)
</step>

<step number="7" required="true" depends_on="6">
### Step 7: Testing & Validation

**Goal:** Comprehensive testing across all components.

**Unit tests:**

```typescript
// Complete test suite
describe('Heartbeat System', () => {
  describe('Scheduler', () => {
    it('fires at configured intervals');
    it('handles multiple agents independently');
    it('updates config dynamically');
  });

  describe('Token Stripping', () => {
    it('suppresses HEARTBEAT_OK only');
    it('handles markup-wrapped tokens');
    it('respects ackMaxChars threshold');
  });

  describe('Content Checker', () => {
    it('detects empty files');
    it('ignores header-only content');
    it('allows checklist items');
  });

  describe('Duplicate Detection', () => {
    it('suppresses within 24h window');
    it('allows after window expires');
    it('normalizes whitespace');
  });

  describe('Active Hours', () => {
    it('respects timezone boundaries');
    it('handles DST transitions');
    it('supports "24:00" end time');
  });

  describe('Delivery', () => {
    it('resolves target from config');
    it('falls back to session context');
    it('handles "none" target');
  });
});
```

**Integration test:**

```typescript
// e2e.test.ts
describe('Full Heartbeat Flow', () => {
  it('executes complete heartbeat cycle', async () => {
    // Setup
    const tmpDir = await fs.mkdtemp('/tmp/heartbeat-test-');
    const heartbeatFile = `${tmpDir}/HEARTBEAT.md`;
    await fs.writeFile(heartbeatFile, '- [ ] Check email');

    const mockLLM = vi.fn().mockResolvedValue({ text: 'Alert: Email needs attention' });
    const mockDelivery = vi.fn();

    const config = {
      every: '30m',
      target: 'console',
      activeHours: { start: '00:00', end: '24:00', timezone: 'UTC' }
    };

    // Execute
    const result = await runHeartbeatOnce('test-agent', config, tmpDir, mockLLM);

    // Assert
    expect(result.status).toBe('sent');
    expect(mockDelivery).toHaveBeenCalled();

    // Cleanup
    await fs.rm(tmpDir, { recursive: true });
  });
});
```

**Manual testing checklist:**

```markdown
## Manual Test Plan

### Basic Flow
- [ ] Start scheduler
- [ ] Verify heartbeat runs at interval
- [ ] Confirm LLM called with correct prompt
- [ ] Check delivery to console

### Token Suppression
- [ ] LLM returns "HEARTBEAT_OK" only → no delivery
- [ ] LLM returns "HEARTBEAT_OK all good" → delivered
- [ ] LLM returns "<b>HEARTBEAT_OK</b>" → suppressed

### Empty Content
- [ ] Empty HEARTBEAT.md → skipped
- [ ] Header-only HEARTBEAT.md → skipped
- [ ] Checklist HEARTBEAT.md → executed

### Duplicates
- [ ] Same message twice within 1 hour → second suppressed
- [ ] Same message after 25 hours → both delivered

### Active Hours
- [ ] Set start: "20:00", end: "24:00"
- [ ] Run at 3pm → skipped (quiet-hours)
- [ ] Run at 9pm → executed

### Delivery
- [ ] target: "console" → logs to console
- [ ] target: "telegram" → delivers to Telegram
- [ ] target: "none" → skips delivery but runs LLM

### Multi-Agent
- [ ] Agent A: every 30m
- [ ] Agent B: every 1h
- [ ] Verify independent schedules
```

**Verification:**
- [ ] All unit tests pass
- [ ] Integration test passes
- [ ] Manual test plan completed
- [ ] No errors in production-like environment
</step>

<step number="8" required="false" depends_on="7">
### Step 8: Production Readiness (Optional)

**Add logging:**

```typescript
// logger.ts
import winston from 'winston';

export const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'heartbeat.log' }),
    new winston.transports.Console({ format: winston.format.simple() })
  ]
});

// In executor
logger.info('Heartbeat executed', { agentId, status: result.status, durationMs });
logger.warn('Heartbeat skipped', { agentId, reason: result.reason });
logger.error('Heartbeat failed', { agentId, error: err.message });
```

**Add metrics:**

```typescript
// metrics.ts
export const metrics = {
  heartbeatsExecuted: 0,
  heartbeatsSkipped: 0,
  heartbeatsFailed: 0,
  heartbeatDurations: [] as number[],

  record(status: string, durationMs?: number) {
    if (status === 'sent') this.heartbeatsExecuted++;
    if (status === 'skipped') this.heartbeatsSkipped++;
    if (status === 'failed') this.heartbeatsFailed++;
    if (durationMs) this.heartbeatDurations.push(durationMs);
  },

  getStats() {
    return {
      executed: this.heartbeatsExecuted,
      skipped: this.heartbeatsSkipped,
      failed: this.heartbeatsFailed,
      avgDurationMs: this.heartbeatDurations.reduce((a, b) => a + b, 0) / this.heartbeatDurations.length
    };
  }
};
```

**Add error handling:**

```typescript
// heartbeat-executor.ts (with error handling)
export async function runHeartbeatOnce(...): Promise<HeartbeatResult> {
  const startTime = Date.now();

  try {
    // All guards and execution...
    const result = await executeHeartbeat(...);

    metrics.record(result.status, Date.now() - startTime);
    logger.info('Heartbeat completed', { agentId, status: result.status });

    return result;
  } catch (error) {
    metrics.record('failed', Date.now() - startTime);
    logger.error('Heartbeat failed', { agentId, error: error.message, stack: error.stack });

    return { status: 'failed', reason: error.message };
  }
}
```

**Add graceful shutdown:**

```typescript
// index.ts
const scheduler = new HeartbeatScheduler();

// Start
scheduler.start(config.agents);

// Graceful shutdown
process.on('SIGTERM', async () => {
  logger.info('Shutting down heartbeat system');
  scheduler.stop();
  await flushLogs();
  process.exit(0);
});
```

**Verification:**
- [ ] Logs written to file and console
- [ ] Metrics tracked and queryable
- [ ] Errors caught and logged (not crashing)
- [ ] Graceful shutdown works (SIGTERM)
</step>

</critical_sequence>

---

## Configuration Reference

### Full Schema

```typescript
interface HeartbeatConfig {
  // Scheduling
  every: string;              // "30m", "1h", "2h", etc.
  enabled?: boolean;          // Default: true

  // Active Hours (optional)
  activeHours?: {
    start: string;            // "08:00" (HH:MM, inclusive)
    end: string;              // "24:00" (HH:MM or "24:00", exclusive)
    timezone: string;         // "user" | "local" | IANA timezone ID
  };

  // LLM Config
  model?: string;             // "claude-sonnet-4-5-20250929", etc.
  prompt?: string;            // Custom prompt (default: HEARTBEAT_PROMPT)
  ackMaxChars?: number;       // Max chars after HEARTBEAT_OK (default: 300)

  // Delivery
  target?: string;            // "last" | "none" | channel ID
  to?: string;                // Recipient override (phone/chat ID/email)

  // Content Source
  contentFile?: string;       // Default: "HEARTBEAT.md"
  workspaceDir?: string;      // Path to workspace
}
```

### Example Configs

**Minimal:**
```json5
{
  agents: [{
    id: "main",
    heartbeat: { every: "30m" }
  }]
}
```

**With Active Hours:**
```json5
{
  agents: [{
    id: "main",
    timezone: "America/New_York",
    heartbeat: {
      every: "30m",
      activeHours: {
        start: "08:00",
        end: "24:00",
        timezone: "user"
      }
    }
  }]
}
```

**Multi-Agent:**
```json5
{
  agents: [
    {
      id: "personal",
      heartbeat: { every: "30m", target: "telegram", to: "12345" }
    },
    {
      id: "ops",
      heartbeat: { every: "1h", target: "slack", to: "#ops-alerts" }
    }
  ]
}
```

---

## Troubleshooting

### Heartbeat Not Running

**Symptoms:** No logs, no execution

**Check:**
1. Is scheduler started? (`scheduler.start()` called?)
2. Is `enabled: true` in config?
3. Are there errors in startup logs?

**Debug:**
```typescript
// Add debug logging in tick()
console.log('Tick', { now, schedules: Array.from(this.schedules.values()) });
```

### Heartbeat Skipped Every Time

**Symptoms:** Status always "skipped"

**Check:**
1. Active hours: Are you outside the window?
2. Content empty: Is HEARTBEAT.md empty?
3. Visibility config: All flags false?

**Debug:**
```typescript
// Log each guard check
logger.debug('Active hours', { within: isWithinActiveHours(...) });
logger.debug('Content empty', { isEmpty: await isHeartbeatContentEmpty(...) });
```

### HEARTBEAT_OK Not Suppressed

**Symptoms:** "HEARTBEAT_OK" delivered as message

**Check:**
1. Is token stripping implemented?
2. Is `ackMaxChars` too low?
3. Is token wrapped in unsupported markup?

**Debug:**
```typescript
// Log token stripping
const stripped = stripHeartbeatToken(text, ackMaxChars);
logger.debug('Token strip', { original: text, stripped, suppressed: stripped === '' });
```

### Duplicate Detection Not Working

**Symptoms:** Same message delivered multiple times

**Check:**
1. Is `recordHeartbeat()` called after delivery?
2. Is window configured correctly (default: 24h)?
3. Is text normalized consistently?

**Debug:**
```typescript
// Log duplicate check
logger.debug('Duplicate check', {
  current: text,
  last: tracker.lastText,
  isDupe: isDuplicate(...)
});
```

---

## Migration Patterns

### From Cron Jobs

**Before (cron):**
```bash
# Crontab
*/30 * * * * /usr/bin/check-tasks.sh
```

**After (heartbeat):**
```json5
{
  agents: [{
    id: "task-checker",
    heartbeat: {
      every: "30m",
      prompt: "Check tasks and alert if any are overdue"
    }
  }]
}
```

**Benefits:**
- AI contextualization (not just raw alerts)
- Smart suppression (no spam)
- Multi-channel delivery
- Active hours support

### From Polling Loops

**Before:**
```typescript
// Infinite loop
setInterval(async () => {
  const status = await checkSystemHealth();
  if (!status.ok) {
    await sendAlert(status.message);
  }
}, 30_000);
```

**After:**
```typescript
// Heartbeat system
const config = {
  every: "30s",
  prompt: "Check system health. Alert if any issues detected.",
  target: "slack",
  to: "#alerts"
};
```

**Benefits:**
- Duplicate suppression (no repeated alerts)
- Token-based acknowledgment (suppress OKs)
- Active hours (no alerts at 3am)

---

## Extension Points

### Custom Content Sources

Instead of `HEARTBEAT.md` file, fetch from:

```typescript
// Database
async function fetchHeartbeatContent(agentId: string): Promise<string> {
  const tasks = await db.tasks.findMany({ agentId, status: 'pending' });
  return tasks.map(t => `- [ ] ${t.title}`).join('\n');
}

// API
async function fetchHeartbeatContent(agentId: string): Promise<string> {
  const response = await fetch(`https://api.example.com/tasks/${agentId}`);
  return response.text();
}
```

### Custom Delivery Channels

Add new channels:

```typescript
// SMS via Twilio
export async function deliverToSMS(phone: string, payload: DeliveryPayload) {
  const twilio = new Twilio(accountSid, authToken);
  await twilio.messages.create({
    to: phone,
    from: twilioNumber,
    body: payload.text
  });
}

// Email
export async function deliverToEmail(email: string, payload: DeliveryPayload) {
  const transporter = nodemailer.createTransport(smtpConfig);
  await transporter.sendMail({
    to: email,
    subject: 'Heartbeat Alert',
    text: payload.text
  });
}
```

### Multi-Modal Content

Support images/files in heartbeat:

```typescript
interface HeartbeatResult {
  status: string;
  message?: string;
  media?: Array<{ type: 'image' | 'file'; url: string }>;
}

// In LLM response handler
if (response.content.some(c => c.type === 'image')) {
  result.media = response.content
    .filter(c => c.type === 'image')
    .map(c => ({ type: 'image', url: c.source.url }));
}
```

---

## Best Practices

### DO

✅ Start with minimal implementation (Phase 1-3)
✅ Add guards in order of cheapness (active hours → content check → LLM)
✅ Test across timezones early
✅ Use single timer loop for multiple agents
✅ Log at appropriate levels (INFO for key events, DEBUG for guards)
✅ Handle errors gracefully (catch, log, continue)
✅ Make token stripping configurable (`ackMaxChars`)
✅ Record metrics for production monitoring

### DON'T

❌ Skip empty content check (wastes API costs)
❌ Create separate timers per agent (resource waste)
❌ Forget session restoration after ACK-only runs
❌ Ignore timezone handling (breaks active hours)
❌ Use exact text match for duplicates without normalization
❌ Skip error handling (crashes on API failures)
❌ Hardcode delivery channels (make pluggable)
❌ Forget to test markup-wrapped tokens

---

## Success Criteria

Implementation is successful when:

- [ ] Scheduler runs reliably at configured intervals
- [ ] LLM calls execute with heartbeat prompt
- [ ] `HEARTBEAT_OK` responses suppressed correctly
- [ ] Empty content files skip LLM calls (cost optimization)
- [ ] Duplicate messages suppressed within window
- [ ] Active hours respected (timezone-aware)
- [ ] At least one delivery channel integrated
- [ ] All unit tests pass
- [ ] Integration test passes
- [ ] Manual test plan completed
- [ ] Production logging/metrics in place

---

## References

- **Learning doc:** `/compound-docs/docs/solutions/architecture-patterns/heartbeat-periodic-awareness-system-20260126.md`
- **Source implementation:** Clawdbot heartbeat system (`src/infra/heartbeat-*.ts`)
- **Related patterns:** Cron jobs, event-driven architecture, pub/sub systems

---

## Support

If you encounter issues during implementation:

1. Check troubleshooting section above
2. Review learning doc for architectural patterns
3. Test each phase independently (don't skip ahead)
4. Add debug logging at each guard/decision point
5. Verify config schema matches examples

Common pitfalls:
- Timezone mismatches (test with multiple TZs)
- Token stripping edge cases (test markup-wrapped)
- Duplicate detection normalization (whitespace handling)
- Session restoration timing (test ACK-only vs alert flows)
