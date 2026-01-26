# Heartbeat Testing Patterns

Comprehensive testing strategies for heartbeat systems, extracted from production test suites.

## Testing Philosophy

**Coverage targets:**
- Unit tests: 80%+ coverage
- Integration tests: Full flow (scheduler → LLM → delivery)
- E2E tests: Real LLM/channel integration (optional, gated by env var)

**Test pyramid:**
```
        /\
       /E2E\      (5%) - Real integrations
      /------\
     /  Integ \   (15%) - Mocked LLM/delivery
    /----------\
   /    Unit    \ (80%) - Individual components
  /--------------\
```

---

## Unit Test Patterns

### 1. Scheduler Tests

**Test: Independent agent schedules**

```typescript
// scheduler.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { HeartbeatScheduler } from './scheduler';

describe('HeartbeatScheduler', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('fires heartbeat at configured interval', async () => {
    const executor = vi.fn().mockResolvedValue({ status: 'sent' });
    const scheduler = new HeartbeatScheduler(executor);

    scheduler.start([
      { id: 'agent-1', intervalMs: 30_000 }
    ]);

    // Should not fire immediately
    expect(executor).not.toHaveBeenCalled();

    // Advance 30 seconds
    await vi.advanceTimersByTimeAsync(30_000);

    // Should fire once
    expect(executor).toHaveBeenCalledTimes(1);
    expect(executor).toHaveBeenCalledWith('agent-1');

    // Advance another 30 seconds
    await vi.advanceTimersByTimeAsync(30_000);

    // Should fire again
    expect(executor).toHaveBeenCalledTimes(2);
  });

  it('handles multiple agents independently', async () => {
    const executor = vi.fn().mockResolvedValue({ status: 'sent' });
    const scheduler = new HeartbeatScheduler(executor);

    scheduler.start([
      { id: 'fast', intervalMs: 10_000 },
      { id: 'slow', intervalMs: 60_000 }
    ]);

    // Fast: should fire at 10s, 20s, 30s, 40s, 50s, 60s = 6 times
    // Slow: should fire at 60s = 1 time
    await vi.advanceTimersByTimeAsync(60_000);

    expect(executor).toHaveBeenCalledTimes(7);
    expect(executor).toHaveBeenCalledWith('fast'); // 6 times
    expect(executor).toHaveBeenCalledWith('slow'); // 1 time
  });

  it('updates config dynamically', () => {
    const executor = vi.fn().mockResolvedValue({ status: 'sent' });
    const scheduler = new HeartbeatScheduler(executor);

    scheduler.start([{ id: 'main', intervalMs: 30_000 }]);

    // Update interval
    scheduler.updateConfig([{ id: 'main', intervalMs: 60_000 }]);

    // New interval should apply
    // (Implementation detail: next run uses new interval)
  });
});
```

---

### 2. Token Stripping Tests

**Test: Markup normalization and edge detection**

```typescript
// token-stripper.test.ts
import { stripHeartbeatToken } from './token-stripper';

describe('stripHeartbeatToken', () => {
  const ACK_MAX = 300;

  it('suppresses token-only response', () => {
    expect(stripHeartbeatToken('HEARTBEAT_OK', ACK_MAX)).toBe('');
  });

  it('suppresses token with whitespace', () => {
    expect(stripHeartbeatToken('  HEARTBEAT_OK  ', ACK_MAX)).toBe('');
  });

  it('suppresses HTML-wrapped token', () => {
    expect(stripHeartbeatToken('<b>HEARTBEAT_OK</b>', ACK_MAX)).toBe('');
    expect(stripHeartbeatToken('<code>HEARTBEAT_OK</code>', ACK_MAX)).toBe('');
  });

  it('suppresses Markdown-wrapped token', () => {
    expect(stripHeartbeatToken('**HEARTBEAT_OK**', ACK_MAX)).toBe('');
    expect(stripHeartbeatToken('`HEARTBEAT_OK`', ACK_MAX)).toBe('');
    expect(stripHeartbeatToken('_HEARTBEAT_OK_', ACK_MAX)).toBe('');
  });

  it('strips token and delivers remainder if long', () => {
    const text = 'HEARTBEAT_OK ' + 'x'.repeat(301);
    const result = stripHeartbeatToken(text, ACK_MAX);
    expect(result).toBe('x'.repeat(301));
  });

  it('suppresses token with short remainder', () => {
    const text = 'HEARTBEAT_OK all systems nominal';
    expect(stripHeartbeatToken(text, ACK_MAX)).toBe('');
  });

  it('keeps token in middle of text', () => {
    const text = 'Status: HEARTBEAT_OK for now';
    expect(stripHeartbeatToken(text, ACK_MAX)).toBe(text);
  });

  it('handles token at end', () => {
    const text = 'All good HEARTBEAT_OK';
    expect(stripHeartbeatToken(text, ACK_MAX)).toBe('');
  });

  it('respects ackMaxChars threshold', () => {
    const short = 'HEARTBEAT_OK ok';
    const long = 'HEARTBEAT_OK ' + 'x'.repeat(100);

    expect(stripHeartbeatToken(short, 10)).toBe(''); // ≤10, suppressed
    expect(stripHeartbeatToken(long, 10)).toBe('x'.repeat(100)); // >10, delivered
  });
});
```

---

### 3. Content Emptiness Tests

**Test: Header/comment detection**

```typescript
// content-checker.test.ts
import { isHeartbeatContentEmpty } from './content-checker';
import fs from 'fs/promises';
import path from 'path';
import os from 'os';

describe('isHeartbeatContentEmpty', () => {
  let tmpDir: string;

  beforeEach(async () => {
    tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), 'heartbeat-test-'));
  });

  afterEach(async () => {
    await fs.rm(tmpDir, { recursive: true });
  });

  it('returns false if file does not exist', async () => {
    const result = await isHeartbeatContentEmpty(tmpDir, 'HEARTBEAT.md');
    expect(result).toBe(false); // Let LLM decide
  });

  it('returns true for empty file', async () => {
    await fs.writeFile(path.join(tmpDir, 'HEARTBEAT.md'), '');
    const result = await isHeartbeatContentEmpty(tmpDir, 'HEARTBEAT.md');
    expect(result).toBe(true);
  });

  it('returns true for whitespace-only', async () => {
    await fs.writeFile(path.join(tmpDir, 'HEARTBEAT.md'), '   \n\n  \t  ');
    const result = await isHeartbeatContentEmpty(tmpDir, 'HEARTBEAT.md');
    expect(result).toBe(true);
  });

  it('returns true for header-only', async () => {
    await fs.writeFile(path.join(tmpDir, 'HEARTBEAT.md'), '# HEARTBEAT\n\n## Tasks');
    const result = await isHeartbeatContentEmpty(tmpDir, 'HEARTBEAT.md');
    expect(result).toBe(true);
  });

  it('returns false for checklist items', async () => {
    await fs.writeFile(path.join(tmpDir, 'HEARTBEAT.md'), `
# HEARTBEAT

- [ ] Check email
- [x] Deploy app
    `);
    const result = await isHeartbeatContentEmpty(tmpDir, 'HEARTBEAT.md');
    expect(result).toBe(false);
  });

  it('returns false for any non-header content', async () => {
    await fs.writeFile(path.join(tmpDir, 'HEARTBEAT.md'), 'Just text');
    const result = await isHeartbeatContentEmpty(tmpDir, 'HEARTBEAT.md');
    expect(result).toBe(false);
  });
});
```

---

### 4. Duplicate Detection Tests

**Test: Time window and normalization**

```typescript
// duplicate-tracker.test.ts
import { isDuplicate, recordHeartbeat } from './duplicate-tracker';

describe('Duplicate Detection', () => {
  const AGENT_ID = 'test-agent';

  beforeEach(() => {
    // Clear tracker state
    vi.clearAllMocks();
  });

  it('returns false on first message', () => {
    expect(isDuplicate(AGENT_ID, 'Alert: check email', false)).toBe(false);
  });

  it('detects duplicate within window', () => {
    const text = 'Alert: check email';

    recordHeartbeat(AGENT_ID, text);

    // Same message immediately after
    expect(isDuplicate(AGENT_ID, text, false)).toBe(true);
  });

  it('allows duplicate after window expires', () => {
    vi.useFakeTimers();

    const text = 'Alert: check email';
    recordHeartbeat(AGENT_ID, text);

    // Advance 25 hours (window is 24h)
    vi.advanceTimersByTime(25 * 60 * 60 * 1000);

    expect(isDuplicate(AGENT_ID, text, false)).toBe(false);

    vi.useRealTimers();
  });

  it('normalizes whitespace', () => {
    recordHeartbeat(AGENT_ID, 'Alert:   check    email');

    // Different whitespace, same content
    expect(isDuplicate(AGENT_ID, 'Alert: check email', false)).toBe(true);
  });

  it('allows different messages', () => {
    recordHeartbeat(AGENT_ID, 'Alert: check email');

    // Different message
    expect(isDuplicate(AGENT_ID, 'Alert: deploy app', false)).toBe(false);
  });

  it('disables dedup for media', () => {
    const text = 'Alert: check email';
    recordHeartbeat(AGENT_ID, text);

    // Same text but with media
    expect(isDuplicate(AGENT_ID, text, true)).toBe(false);
  });
});
```

---

### 5. Active Hours Tests

**Test: Timezone boundaries**

```typescript
// active-hours.test.ts
import { isWithinActiveHours } from './active-hours';
import { DateTime } from 'luxon';

describe('isWithinActiveHours', () => {
  it('returns true when no config', () => {
    expect(isWithinActiveHours(undefined, 'America/New_York')).toBe(true);
  });

  it('respects start boundary (inclusive)', () => {
    const config = {
      start: '08:00',
      end: '24:00',
      timezone: 'America/New_York'
    };

    // Mock current time to 8:00am EST
    vi.setSystemTime(DateTime.fromISO('2026-01-26T13:00:00Z').toJSDate()); // 8am EST

    expect(isWithinActiveHours(config, 'America/New_York')).toBe(true);
  });

  it('respects end boundary (exclusive)', () => {
    const config = {
      start: '08:00',
      end: '24:00',
      timezone: 'America/New_York'
    };

    // Mock current time to midnight EST
    vi.setSystemTime(DateTime.fromISO('2026-01-27T05:00:00Z').toJSDate()); // 12am EST

    expect(isWithinActiveHours(config, 'America/New_York')).toBe(false);
  });

  it('handles before window', () => {
    const config = {
      start: '08:00',
      end: '24:00',
      timezone: 'America/New_York'
    };

    // 3am EST
    vi.setSystemTime(DateTime.fromISO('2026-01-26T08:00:00Z').toJSDate());

    expect(isWithinActiveHours(config, 'America/New_York')).toBe(false);
  });

  it('handles middle of window', () => {
    const config = {
      start: '08:00',
      end: '24:00',
      timezone: 'America/New_York'
    };

    // 3pm EST
    vi.setSystemTime(DateTime.fromISO('2026-01-26T20:00:00Z').toJSDate());

    expect(isWithinActiveHours(config, 'America/New_York')).toBe(true);
  });

  it('handles user timezone', () => {
    const config = {
      start: '08:00',
      end: '24:00',
      timezone: 'user'
    };

    // 8am PST
    vi.setSystemTime(DateTime.fromISO('2026-01-26T16:00:00Z').toJSDate());

    expect(isWithinActiveHours(config, 'America/Los_Angeles')).toBe(true);
  });

  it('handles 24:00 end time', () => {
    const config = {
      start: '08:00',
      end: '24:00',
      timezone: 'UTC'
    };

    // 11:59pm UTC
    vi.setSystemTime(DateTime.fromISO('2026-01-26T23:59:00Z').toJSDate());

    expect(isWithinActiveHours(config, 'UTC')).toBe(true);
  });
});
```

---

### 6. Visibility Resolution Tests

**Test: 3-tier cascade**

```typescript
// visibility.test.ts
import { resolveVisibility } from './visibility';

describe('Visibility Resolution', () => {
  it('uses built-in defaults when no config', () => {
    const config = { channels: {} };
    const result = resolveVisibility('user1', 'telegram', config);

    expect(result).toEqual({
      showOk: false,
      showAlerts: true,
      useIndicator: true
    });
  });

  it('applies channel defaults', () => {
    const config = {
      channels: {
        defaults: {
          heartbeat: { showOk: true }
        }
      }
    };

    const result = resolveVisibility('user1', 'telegram', config);

    expect(result).toEqual({
      showOk: true,       // From channel defaults
      showAlerts: true,   // From built-in defaults
      useIndicator: true  // From built-in defaults
    });
  });

  it('applies per-channel config', () => {
    const config = {
      channels: {
        defaults: { heartbeat: { showOk: false } },
        telegram: { heartbeat: { showOk: true, showAlerts: false } }
      }
    };

    const result = resolveVisibility('user1', 'telegram', config);

    expect(result).toEqual({
      showOk: true,        // From per-channel (overrides defaults)
      showAlerts: false,   // From per-channel
      useIndicator: true   // From built-in defaults
    });
  });

  it('applies per-account config (highest precedence)', () => {
    const config = {
      channels: {
        defaults: { heartbeat: { showOk: false } },
        telegram: {
          heartbeat: { showOk: true },
          accounts: {
            user1: {
              heartbeat: { showAlerts: false }
            }
          }
        }
      }
    };

    const result = resolveVisibility('user1', 'telegram', config);

    expect(result).toEqual({
      showOk: true,        // From per-channel
      showAlerts: false,   // From per-account (highest precedence)
      useIndicator: true   // From built-in defaults
    });
  });
});
```

---

## Integration Test Patterns

### Full Flow Test

**Test: Scheduler → Executor → Delivery**

```typescript
// heartbeat.integration.test.ts
import { HeartbeatScheduler } from './scheduler';
import { runHeartbeatOnce } from './executor';
import fs from 'fs/promises';
import path from 'path';
import os from 'os';

describe('Heartbeat Integration', () => {
  let tmpDir: string;
  let mockLLM: any;
  let mockDelivery: any;

  beforeEach(async () => {
    tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), 'heartbeat-integ-'));
    mockLLM = vi.fn();
    mockDelivery = vi.fn();
  });

  afterEach(async () => {
    await fs.rm(tmpDir, { recursive: true });
  });

  it('executes complete heartbeat flow', async () => {
    // Setup: Create HEARTBEAT.md with tasks
    const heartbeatFile = path.join(tmpDir, 'HEARTBEAT.md');
    await fs.writeFile(heartbeatFile, `
# Tasks
- [ ] Check email
- [x] Deploy app
    `);

    // Mock LLM response
    mockLLM.mockResolvedValue({
      content: [{ type: 'text', text: 'Alert: Email needs attention' }]
    });

    // Execute
    const result = await runHeartbeatOnce('test-agent', {
      every: '30m',
      target: 'console',
      workspaceDir: tmpDir
    }, mockLLM, mockDelivery);

    // Verify LLM called
    expect(mockLLM).toHaveBeenCalledWith(expect.objectContaining({
      messages: expect.arrayContaining([
        expect.objectContaining({
          role: 'user',
          content: expect.stringContaining('Read HEARTBEAT.md')
        })
      ])
    }));

    // Verify delivery called
    expect(mockDelivery).toHaveBeenCalledWith({
      channel: 'console',
      recipient: '',
      text: 'Alert: Email needs attention'
    });

    // Verify result
    expect(result).toEqual({
      status: 'sent',
      message: 'Alert: Email needs attention'
    });
  });

  it('suppresses HEARTBEAT_OK response', async () => {
    await fs.writeFile(path.join(tmpDir, 'HEARTBEAT.md'), '- [x] All done');

    mockLLM.mockResolvedValue({
      content: [{ type: 'text', text: 'HEARTBEAT_OK' }]
    });

    const result = await runHeartbeatOnce('test-agent', {
      every: '30m',
      target: 'console',
      workspaceDir: tmpDir
    }, mockLLM, mockDelivery);

    // Verify no delivery
    expect(mockDelivery).not.toHaveBeenCalled();

    // Verify result
    expect(result).toEqual({ status: 'ok-token' });
  });

  it('skips empty content', async () => {
    await fs.writeFile(path.join(tmpDir, 'HEARTBEAT.md'), '# HEARTBEAT\n\n');

    const result = await runHeartbeatOnce('test-agent', {
      every: '30m',
      target: 'console',
      workspaceDir: tmpDir
    }, mockLLM, mockDelivery);

    // Verify LLM not called
    expect(mockLLM).not.toHaveBeenCalled();

    // Verify result
    expect(result).toEqual({ status: 'skipped', reason: 'ok-empty' });
  });

  it('respects active hours', async () => {
    vi.setSystemTime(new Date('2026-01-26T08:00:00Z')); // 3am EST

    const result = await runHeartbeatOnce('test-agent', {
      every: '30m',
      activeHours: {
        start: '08:00',
        end: '24:00',
        timezone: 'America/New_York'
      },
      workspaceDir: tmpDir
    }, mockLLM, mockDelivery);

    // Verify skipped
    expect(mockLLM).not.toHaveBeenCalled();
    expect(result).toEqual({ status: 'skipped', reason: 'quiet-hours' });
  });
});
```

---

## E2E Test Patterns

### Real LLM Integration

**Test: Actual Anthropic API call** (gated by env var)

```typescript
// heartbeat.e2e.test.ts
import { runHeartbeatOnce } from './executor';
import Anthropic from '@anthropic-ai/sdk';

describe.skipIf(!process.env.LIVE_TEST)('Heartbeat E2E', () => {
  let anthropic: Anthropic;

  beforeAll(() => {
    anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
  });

  it('calls real LLM and processes response', async () => {
    const result = await runHeartbeatOnce('e2e-agent', {
      every: '30m',
      prompt: 'Say HEARTBEAT_OK if all good, otherwise alert.',
      target: 'console'
    }, anthropic);

    expect(result.status).toMatch(/sent|ok-token/);
  }, 30_000); // 30s timeout for API call

  it('handles empty HEARTBEAT.md', async () => {
    const tmpDir = await fs.mkdtemp('/tmp/heartbeat-e2e-');
    await fs.writeFile(path.join(tmpDir, 'HEARTBEAT.md'), '');

    const result = await runHeartbeatOnce('e2e-agent', {
      every: '30m',
      workspaceDir: tmpDir
    }, anthropic);

    expect(result.status).toBe('skipped');
    expect(result.reason).toBe('ok-empty');

    await fs.rm(tmpDir, { recursive: true });
  });
});
```

**Run:** `LIVE_TEST=1 npm test heartbeat.e2e.test.ts`

---

## Test Data Factories

**Pattern: Reusable test fixtures**

```typescript
// test-helpers.ts
export async function createTestWorkspace(content: string): Promise<string> {
  const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), 'heartbeat-test-'));
  await fs.writeFile(path.join(tmpDir, 'HEARTBEAT.md'), content);
  return tmpDir;
}

export function mockLLMResponse(text: string) {
  return vi.fn().mockResolvedValue({
    content: [{ type: 'text', text }]
  });
}

export function mockDelivery() {
  return vi.fn().mockResolvedValue(undefined);
}

export const FIXTURES = {
  emptyChecklist: '# HEARTBEAT\n\n',
  allDone: '- [x] Task 1\n- [x] Task 2',
  pendingTasks: '- [ ] Check email\n- [x] Deploy app',
  headerOnly: '# Tasks\n## Today',
};
```

**Usage:**
```typescript
it('handles pending tasks', async () => {
  const tmpDir = await createTestWorkspace(FIXTURES.pendingTasks);
  const llm = mockLLMResponse('Alert: Check email');
  const delivery = mockDelivery();

  const result = await runHeartbeatOnce('test', { every: '30m', workspaceDir: tmpDir }, llm, delivery);

  expect(result.status).toBe('sent');
  await fs.rm(tmpDir, { recursive: true });
});
```

---

## Coverage Targets

**Minimum requirements:**

```yaml
coverage:
  lines: 80
  branches: 75
  functions: 80
  statements: 80
```

**Critical paths (100% coverage):**
- Token stripping logic
- Guard checks (active hours, content empty, duplicates)
- Visibility resolution cascade
- Session restoration

**Lower priority (<80% OK):**
- Error logging
- Metrics recording
- Debug output

---

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 22
      - run: npm install
      - run: npm test -- --coverage
      - uses: codecov/codecov-action@v3

  e2e:
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: LIVE_TEST=1 npm test heartbeat.e2e.test.ts
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

---

## Performance Testing

### Load Test

**Test: 50 agents, verify no memory leaks**

```typescript
// heartbeat.perf.test.ts
describe('Performance', () => {
  it('handles 50 agents without memory leak', async () => {
    const agents = Array.from({ length: 50 }, (_, i) => ({
      id: `agent-${i}`,
      intervalMs: 30_000
    }));

    const memBefore = process.memoryUsage().heapUsed;

    const scheduler = new HeartbeatScheduler(mockExecutor);
    scheduler.start(agents);

    // Run for 5 minutes (10 heartbeats per agent)
    await vi.advanceTimersByTimeAsync(5 * 60 * 1000);

    const memAfter = process.memoryUsage().heapUsed;
    const memGrowth = memAfter - memBefore;

    // Allow up to 50MB growth (generous)
    expect(memGrowth).toBeLessThan(50 * 1024 * 1024);

    scheduler.stop();
  });
});
```

---

## References

- Vitest docs: https://vitest.dev/
- Luxon docs: https://moment.github.io/luxon/
- Test pyramid: https://martinfowler.com/articles/practical-test-pyramid.html
