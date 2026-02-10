---
name: heartbeat-implementer
description: This skill should be used when implementing a periodic heartbeat system in AI agent applications. Use when the user wants to add periodic agent awareness, cost-optimized LLM calls, multi-channel delivery, duplicate alert suppression, or timezone-aware active hours to their application. The skill provides architecture patterns, implementation checklists, code examples, and testing strategies based on the OpenClaw reference implementation.
---

# Heartbeat System Implementer

Implement a production-grade periodic heartbeat system that allows AI agents to autonomously check for pending tasks and surface alerts without spamming users.

## When to Use This Skill

Use this skill when implementing features that require:

- **Periodic agent awareness** - Agent checks tasks on a timer (e.g., every 30 minutes)
- **Cost-optimized LLM calls** - Skip unnecessary API calls when nothing needs attention
- **Multi-channel delivery** - Deliver alerts to various channels (WhatsApp, Telegram, Slack, etc.)
- **Duplicate alert suppression** - Prevent sending the same alert repeatedly
- **Timezone-aware active hours** - Respect quiet hours (e.g., 9am-9pm user timezone)
- **Hot-reload configuration** - Update intervals and settings without restarting

## Core Concepts

### The Heartbeat Loop

```
Timer fires (30m default) → Guard checks (6 sequential) → LLM call →
Token stripping → Duplicate check → Channel readiness → Delivery →
Session update → Event emission → Reschedule
```

### Key Innovation: Token-Based Suppression

Instead of heuristics to detect "nothing to report", use an explicit sentinel token (`HEARTBEAT_OK`) that the LLM returns:

- **Deterministic** (no false positives/negatives)
- **Explicit** (clear contract with LLM)
- **Cost-effective** (no additional inference)

Example system prompt addition:
```
If you receive a heartbeat poll and there is nothing that needs attention,
reply exactly: HEARTBEAT_OK

If something needs attention, do NOT include HEARTBEAT_OK; reply with the
alert text instead.
```

### Architecture Components

1. **Core Runner** - Per-agent state management, guard chain, LLM integration
2. **Wake System** - Coalescing scheduler (250ms debounce, 1s retry)
3. **Event System** - Pub/sub for lifecycle events (sent, skipped, failed)
4. **Token Handling** - Strip `HEARTBEAT_OK`, empty file detection
5. **Visibility Resolver** - 3-tier precedence (per-account > per-channel > defaults)
6. **Delivery Target** - Resolve "last" channel or explicit target

## Implementation Process

### Phase 1: Understand Requirements

Ask the user:

1. **What should trigger heartbeats?**
   - Periodic timer (default: every 30 minutes)
   - External events (cron jobs, webhooks, exec completion)
   - Manual triggers (API endpoint, CLI command)

2. **What checks should the agent perform?**
   - Read workspace file (e.g., `HEARTBEAT.md`) for tasks
   - Query database for pending items
   - Monitor system metrics
   - Aggregate notifications

3. **How should alerts be delivered?**
   - Single channel (e.g., Telegram only)
   - Multi-channel (last-used, explicit target)
   - Multiple recipients (groups, broadcast)

4. **What cost optimizations are needed?**
   - Skip LLM calls when workspace file is empty
   - Suppress duplicate alerts (24h window)
   - Longer intervals for low-priority agents
   - Visibility gating (skip if all output disabled)

5. **What configuration is required?**
   - Per-agent intervals (e.g., agent A: 15m, agent B: 1h)
   - Active hours (timezone-aware quiet hours)
   - Model overrides (e.g., use Haiku for simple checks)
   - Hot-reload support (update without restart)

### Phase 2: Implementation Checklist

Use the comprehensive checklist in `references/implementation-checklist.md` to track progress across 10 phases:

1. **Core Runner** - State management, guard chain, LLM integration
2. **Wake System** - Coalescing scheduler, retry logic
3. **Event System** - Pub/sub, WebSocket broadcast
4. **Configuration Schema** - Agent config, channel visibility, dynamic defaults
5. **Token Handling** - Sentinel token, empty file detection
6. **Workspace File** - User-editable checklist, system prompt integration
7. **Integrations** - Gateway startup, cron, webhooks, external events, config reload
8. **Testing** - Unit tests (80+ cases), integration tests, E2E tests
9. **Documentation** - User guides, API reference, troubleshooting
10. **Optimization & Monitoring** - Cost optimization, metrics, observability

To begin implementation:

```
Read references/implementation-checklist.md for detailed task breakdown.
```

### Phase 3: Code Implementation

Use code patterns from `references/code-patterns.md` for:

- Per-agent state structure and single timer scheduler
- Guard chain with 6 sequential checks and early exit
- Token stripping algorithm (handles HTML/markdown wrapping)
- Duplicate detection (24h window, per-session tracking)
- Session timestamp restoration (preserve idle expiry)
- Active hours validation (timezone-aware)
- Coalescing wake system (250ms debounce, 1s retry)
- Event pub/sub implementation
- Integration patterns (gateway startup, cron, webhooks)

To reference code patterns:

```
Read references/code-patterns.md for TypeScript examples and language-agnostic pseudocode.
```

### Phase 4: Testing

Implement comprehensive test coverage:

#### Unit Tests (~80+ cases)

**Token stripping (20+ cases)**:
- Bare token, HTML-wrapped, markdown-wrapped
- Token in middle of text (not stripped)
- Short remainder (under `ackMaxChars`), long remainder
- Multiple layers of wrapping

**Runner logic (40+ cases)**:
- Interval/prompt resolution
- Agent enablement rules
- Active hours validation (various timezones, overnight ranges)
- Duplicate detection (24h window)
- Session timestamp restoration
- Visibility resolution (3-tier precedence)
- Delivery target resolution (last, explicit, none)
- Empty file optimization

**Scheduler (multi-agent timing)**:
- Different intervals schedule correctly
- Config updates preserve timing state
- Fake timers for deterministic testing

#### Integration Tests
- Cron + heartbeat (`wakeMode: "now"`, `wakeMode: "next-heartbeat"`)
- Webhook + heartbeat
- Config reload
- Media delivery with OK token

#### E2E Tests
- WebSocket broadcast
- Health endpoints
- Gateway startup/shutdown

### Phase 5: Documentation & Iteration

Create user-facing documentation:

1. **Getting Started** - Configuration examples, first heartbeat
2. **Configuration Reference** - All config fields with defaults
3. **Common Patterns** - Time-based reminders, metric monitoring, daily summaries
4. **Troubleshooting** - Common issues, debug tips
5. **API Reference** - Runner, wake system, events

Test the implementation with real-world scenarios and iterate based on feedback.

## Guard Chain Pattern

The heartbeat runner implements 6 sequential guard checks with early exit:

### Guard 1: Global Enabled Check
```typescript
if (!heartbeatsEnabled) {
  emitHeartbeatEvent({ status: "skipped", reason: "disabled" });
  return { status: "skipped", reason: "disabled" };
}
```

### Guard 2: Per-Agent Enabled Check
```typescript
if (!isHeartbeatEnabledForAgent(cfg, agentId)) {
  emitHeartbeatEvent({ status: "skipped", reason: "disabled" });
  return { status: "skipped", reason: "disabled" };
}
```

### Guard 3: Valid Interval Check
```typescript
const intervalMs = resolveHeartbeatIntervalMs(heartbeat);
if (!intervalMs) {
  emitHeartbeatEvent({ status: "skipped", reason: "disabled" });
  return { status: "skipped", reason: "disabled" };
}
```

### Guard 4: Active Hours Check
```typescript
if (!isWithinActiveHours(heartbeat?.activeHours, lastSender)) {
  emitHeartbeatEvent({ status: "skipped", reason: "quiet-hours" });
  return { status: "skipped", reason: "quiet-hours" };
}
```

### Guard 5: Queue Empty Check
```typescript
if (getQueueSize(CommandLane.Main) > 0) {
  emitHeartbeatEvent({ status: "skipped", reason: "requests-in-flight" });
  return { status: "skipped", reason: "requests-in-flight" };
}
```

### Guard 6: Non-Empty File Check
```typescript
const heartbeatMd = await fs.readFile(heartbeatPath, "utf-8").catch(() => undefined);
if (reason !== "exec-event" && isHeartbeatContentEffectivelyEmpty(heartbeatMd)) {
  emitHeartbeatEvent({ status: "skipped", reason: "empty-heartbeat-file" });
  return { status: "skipped", reason: "empty-heartbeat-file" };
}
```

## Cost Optimization Strategies

### 1. Empty File Optimization
Skip LLM calls when the workspace file (`HEARTBEAT.md`) contains only:
- Blank lines
- Markdown headers (ATX format: `# Heading`)
- Empty list items (`- [ ]`)

**Savings**: ~$0.001-0.01 per heartbeat cycle when idle

### 2. Duplicate Detection
Track `lastHeartbeatText` and `lastHeartbeatSentAt` per session. Suppress identical alerts within 24 hours.

**Savings**: Delivery costs + user annoyance prevention

### 3. Visibility Gating
If `showOk: false`, `showAlerts: false`, and `useIndicator: false`, skip LLM call entirely.

### 4. Dynamic Default Intervals
Adjust intervals based on auth mode:
- API key: 30 minutes (default)
- OAuth token: 1 hour (lower cost)

### 5. Session Timestamp Restoration
Restore `updatedAt` on heartbeat-only replies (OK token, empty, duplicate) so idle sessions don't stay alive artificially.

## Common Patterns

### Pattern 1: Time-Based Reminders

**Use case**: Remind user of tasks at specific times

**HEARTBEAT.md**:
```markdown
# Reminders

- [ ] If it's Monday morning (9am-12pm), remind about team standup
- [ ] If it's Friday afternoon and no timesheet submitted, remind user
- [ ] If it's the last day of the month, remind about expense reports
```

**Config**:
```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "1h",
        activeHours: { start: "09:00", end: "18:00", timezone: "user" }
      }
    }
  }
}
```

### Pattern 2: Metric Monitoring

**Use case**: Monitor system metrics, alert on thresholds

**HEARTBEAT.md**:
```markdown
# Monitoring

- [ ] Check system metrics (CPU, memory, disk)
- [ ] Alert if CPU > 90% for 5+ minutes
- [ ] Alert if disk usage > 85%
- [ ] Only alert once per issue per day
```

**Config**:
```json5
{
  agents: {
    list: [
      {
        agentId: "monitoring",
        heartbeat: {
          every: "5m",
          model: "haiku",  // Fast, cheap
          target: "telegram"
        }
      }
    ]
  }
}
```

### Pattern 3: Daily Summary

**Use case**: Provide daily digest of activity

**HEARTBEAT.md**:
```markdown
# Daily Summary

- [ ] If it's 8pm, provide a brief summary of today's activity:
  - Messages handled
  - Tasks completed
  - Any pending items for tomorrow
- [ ] Only send once per day
```

**Config** (using active hours):
```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        activeHours: { start: "19:30", end: "21:00", timezone: "user" }
      }
    }
  }
}
```

**Alternative** (using cron):
```json5
{
  cron: {
    jobs: [
      {
        name: "daily-summary",
        schedule: "0 20 * * *",  // Every day at 8pm
        prompt: "Provide a brief summary of today's activity",
        wakeMode: "now"
      }
    ]
  }
}
```

## Adaptation for Different Stacks

### Non-LLM Systems
Replace LLM call with custom check function:

```typescript
const checkResult = await customCheckFunction(agentId, context);
const shouldAlert = checkResult.hasAlerts;
const message = checkResult.message || "HEARTBEAT_OK";
```

### Single-Agent Systems
Simplify to single state instead of per-agent tracking:

```typescript
let lastRunMs: number | undefined;
let nextDueMs: number;
const intervalMs = resolveInterval(config);
```

### Systems Without Sessions
Store duplicate tracking in external state:

```typescript
const lastHeartbeats = new Map<string, { text: string, sentAt: number }>();
```

### Systems Without Channels
Simplify delivery to single target:

```typescript
await deliverAlert(message);  // No channel resolution needed
```

## Troubleshooting

### Issue: Heartbeats Not Firing
**Checklist**:
1. Global enabled? Check `heartbeatsEnabled` flag
2. Per-agent enabled? Check agent config
3. Valid interval? Check `intervalMs` is not null
4. Within active hours? Check current time vs. config
5. Queue empty? Check for pending requests
6. Non-empty file? Check `HEARTBEAT.md` content

**Debug**: Check event stream for skip reasons

### Issue: Duplicate Alerts
**Cause**: Duplicate detection too aggressive (24h window)

**Workaround**: Include counter or timestamp in alert text:
```
🚨 High CPU (alert #3 today, last seen 2:15pm)
```

### Issue: Cost Explosion
**Causes**:
1. Empty file not detected (LLM calls during idle)
2. Intervals too short (too many checks)
3. Duplicate detection not working (same alerts repeated)

**Solutions**:
1. Verify empty file detection logic
2. Increase intervals (30m → 1h)
3. Check duplicate tracking implementation

### Issue: Timing Reset on Config Change
**Cause**: Config reload doesn't preserve `lastRunMs`

**Solution**: Implement `updateConfig()` that preserves timing state:
```typescript
const prev = state.find((s) => s.agentId === agent.agentId);
agent.lastRunMs = prev?.lastRunMs; // Preserve timing
```

## Resources

This skill includes comprehensive reference materials:

### references/
Documentation to guide implementation across all phases:

- **implementation-checklist.md** - Complete task breakdown across 10 phases with 100+ specific checklist items covering core runner, wake system, event system, configuration, token handling, workspace files, integrations, testing, documentation, and optimization
- **code-patterns.md** - TypeScript code examples and language-agnostic pseudocode for all major components: per-agent state, single timer scheduler, guard chain, token stripping, duplicate detection, active hours validation, coalescing wake, event pub/sub, and integration patterns

Load these references when beginning implementation to understand the complete architecture and specific code patterns.

## Next Steps

After implementing the heartbeat system:

1. **Test with real scenarios** - Run the system with actual agent tasks
2. **Monitor metrics** - Track skip reasons, LLM call counts, delivery success
3. **Iterate on configuration** - Adjust intervals, active hours, visibility based on usage
4. **Document patterns** - Capture common use cases and configurations
5. **Extend integrations** - Add webhook hooks, external event triggers as needed

## References

- **OpenClaw Repository**: https://github.com/openclaw/openclaw
- **Heartbeat Runner**: `src/infra/heartbeat-runner.ts` (970 lines, reference implementation)
- **Tests**: 13 test files, ~80+ test cases covering all components
- **Documentation**: `docs/gateway/heartbeat.md` (user-facing guide)
