# Heartbeat System Implementation Checklist

This checklist covers all components needed to implement a production-grade heartbeat system based on the OpenClaw reference implementation.

## Prerequisites

- [ ] AI agent system with session management
- [ ] Multi-turn conversation support
- [ ] Background task scheduling capability
- [ ] Configurable intervals (cron-like or timer-based)
- [ ] Event/notification delivery system

## Phase 1: Core Runner

### State Management
- [ ] Per-agent state tracking structure:
  - `agentId`: string
  - `intervalMs`: number
  - `lastRunMs`: number | undefined
  - `nextDueMs`: number
- [ ] Single timer scheduler (compute soonest due, reschedule after each run)
- [ ] Hot-reload support (preserve `lastRunMs` on config changes)

### Guard Chain (6 Sequential Checks)
- [ ] **Guard 1**: Global enabled check
- [ ] **Guard 2**: Per-agent enabled check
- [ ] **Guard 3**: Valid interval check
- [ ] **Guard 4**: Active hours check (timezone-aware)
- [ ] **Guard 5**: Queue empty check (skip if requests in-flight)
- [ ] **Guard 6**: Non-empty file check (skip LLM calls when idle)

### LLM Integration
- [ ] Heartbeat prompt configuration
- [ ] LLM call with `isHeartbeat: true` flag (suppress typing indicators)
- [ ] Model override support (per-agent model selection)
- [ ] Reasoning payload delivery (optional, separate message)

### Token Stripping
- [ ] Strip sentinel token from edges (e.g., `HEARTBEAT_OK`)
- [ ] Handle HTML wrapping (`<b>TOKEN</b>`, `<i>TOKEN</i>`)
- [ ] Handle markdown wrapping (`**TOKEN**`, `_TOKEN_`)
- [ ] `ackMaxChars` threshold (default: 300)
- [ ] Don't strip token from middle of text

### Duplicate Detection
- [ ] Per-session tracking: `lastHeartbeatText`, `lastHeartbeatSentAt`
- [ ] 24-hour suppression window
- [ ] Comparison logic (normalized text)
- [ ] Reset on different text or >24h elapsed

### Session Timestamp Restoration
- [ ] Store original `updatedAt` before heartbeat
- [ ] Restore `updatedAt` on heartbeat-only replies (OK token, empty, duplicate)
- [ ] Preserves idle expiry behavior

### Delivery Resolution
- [ ] Resolve "last" channel from session history
- [ ] Support explicit channel targets
- [ ] Recipient override (`to` config field)
- [ ] Per-channel recipient resolution (allowFrom, groups)

### Channel Readiness Check
- [ ] Plugin adapter: `checkReady({ cfg, accountId, deps })`
- [ ] Skip delivery if channel not ready (e.g., WhatsApp not authenticated)

## Phase 2: Wake System

### Coalescing Scheduler
- [ ] 250ms debounce window (configurable)
- [ ] Single in-flight run enforcement
- [ ] Queue next run if already in progress
- [ ] 1s retry delay on "requests-in-flight"

### Handler Registration
- [ ] `setHeartbeatWakeHandler(handler)` API
- [ ] `requestHeartbeatNow(opts)` API
- [ ] `hasPendingHeartbeatWake()` introspection
- [ ] `hasHeartbeatWakeHandler()` introspection

## Phase 3: Event System

### Event Payload Structure
- [ ] `ts`: number (timestamp)
- [ ] `status`: "sent" | "ok-empty" | "ok-token" | "skipped" | "failed"
- [ ] `to`: string (recipient, optional)
- [ ] `preview`: string (first 200 chars, optional)
- [ ] `durationMs`: number (LLM call duration, optional)
- [ ] `hasMedia`: boolean (optional)
- [ ] `reason`: string (skip/fail reason, optional)
- [ ] `channel`: string (delivery channel, optional)
- [ ] `silent`: boolean (visibility suppressed, optional)
- [ ] `indicatorType`: "ok" | "alert" | "error" (optional)

### Pub/Sub Implementation
- [ ] `emitHeartbeatEvent(payload)` function
- [ ] `onHeartbeatEvent(listener)` subscription
- [ ] `getLastHeartbeatEvent()` accessor
- [ ] Unsubscribe function returned from `onHeartbeatEvent`
- [ ] Store latest event for new subscribers

### WebSocket Broadcast (Optional)
- [ ] Broadcast events to connected clients
- [ ] macOS/desktop app integration
- [ ] Web UI integration

## Phase 4: Configuration Schema

### Agent Configuration
- [ ] `every`: string (duration, default: "30m")
- [ ] `prompt`: string (default prompt with instructions)
- [ ] `target`: "last" | "none" | channel ID
- [ ] `to`: string (recipient override, optional)
- [ ] `model`: string (model override, optional)
- [ ] `session`: string (session key, default: "main")
- [ ] `ackMaxChars`: number (default: 300)
- [ ] `includeReasoning`: boolean (default: false)
- [ ] `activeHours`:
  - `start`: string ("HH:MM")
  - `end`: string ("HH:MM")
  - `timezone`: "user" | "local" | IANA TZ

### Channel Visibility Configuration
- [ ] `showOk`: boolean (default: false)
- [ ] `showAlerts`: boolean (default: true)
- [ ] `useIndicator`: boolean (default: true)
- [ ] 3-tier precedence: per-account > per-channel > defaults

### Dynamic Defaults
- [ ] Auth-mode-based defaults (e.g., API key: 30m, OAuth: 1h)
- [ ] User preference defaults

### Hot-Reload Support
- [ ] Detect config changes (heartbeat fields)
- [ ] `updateConfig(nextCfg)` method on runner
- [ ] Preserve timing state (`lastRunMs`)
- [ ] Recalculate intervals without restart

## Phase 5: Token Handling

### Sentinel Token
- [ ] Define token constant (e.g., `HEARTBEAT_OK`)
- [ ] Document token in system prompt

### Empty File Detection
- [ ] `isHeartbeatContentEffectivelyEmpty(content)` function
- [ ] Check for blank lines
- [ ] Check for markdown headers only (ATX format)
- [ ] Check for empty list items (`- [ ]`)
- [ ] Skip LLM call if effectively empty

### Strip Token Algorithm
```
1. Normalize HTML tags to lowercase
2. Strip token from edges (handle wrapping)
3. Trim whitespace
4. If mode=heartbeat && remaining.length <= ackMaxChars: mark shouldSkip=true
5. Return { stripped: string, shouldSkip: boolean }
```

## Phase 6: Workspace File

### File Creation
- [ ] Create `HEARTBEAT.md` in agent workspace directory
- [ ] Template with instructions and example tasks
- [ ] User-editable checklist format

### System Prompt Integration
- [ ] Add heartbeat section to system prompt
- [ ] Explain `HEARTBEAT_OK` token behavior
- [ ] Instruct: "If nothing needs attention, reply exactly: HEARTBEAT_OK"
- [ ] Instruct: "If something needs attention, do NOT include HEARTBEAT_OK"

## Phase 7: Integrations

### Gateway/Server Startup
- [ ] `startHeartbeatRunner({ cfg })` on startup
- [ ] Store runner instance for later updates
- [ ] Subscribe to heartbeat events
- [ ] Broadcast events to WebSocket clients (if applicable)

### Cron Integration
- [ ] Inject `runHeartbeatOnce` callback
- [ ] Inject `requestHeartbeatNow` callback
- [ ] Support `wakeMode: "now"` (retry loop for up to 2 minutes if busy)
- [ ] Support `wakeMode: "next-heartbeat"` (piggyback on next cycle)

### Webhook Integration
- [ ] `POST /hooks/wake` endpoint
- [ ] Body: `{ text: string, mode: "now" | "next-heartbeat" }`
- [ ] Authentication (Bearer token, API key)
- [ ] Enqueue system event + trigger heartbeat wake

### External Event Triggers
- [ ] Exec completion events
- [ ] Node events (remote device events)
- [ ] Custom event sources

### Config Reload
- [ ] Detect heartbeat config changes
- [ ] Call `heartbeatRunner.updateConfig(nextConfig)`
- [ ] Preserve timing state

### Shutdown
- [ ] `heartbeatRunner.stop()` method
- [ ] Clear timers
- [ ] Unregister wake handler
- [ ] Unsubscribe event listeners

## Phase 8: Testing

### Unit Tests

#### Token Stripping (20+ cases)
- [ ] Bare token (`HEARTBEAT_OK`)
- [ ] Token with whitespace
- [ ] HTML-wrapped token (`<b>HEARTBEAT_OK</b>`)
- [ ] Markdown-wrapped token (`**HEARTBEAT_OK**`)
- [ ] Multiple layers of wrapping
- [ ] Token in middle of text (not stripped)
- [ ] Short remainder text (under `ackMaxChars`)
- [ ] Long remainder text (over `ackMaxChars`)

#### Runner Logic (40+ cases)
- [ ] Interval resolution (valid, invalid, default)
- [ ] Prompt resolution (default, override)
- [ ] Agent enablement (explicit agents, default agent)
- [ ] Active hours validation (various timezones, overnight ranges)
- [ ] Duplicate detection (24h window, identical text)
- [ ] Session timestamp restoration (OK token, empty, duplicate)
- [ ] Visibility resolution (3-tier precedence, webchat exception)
- [ ] Delivery target resolution (last, explicit, none)
- [ ] Reasoning delivery (enabled, disabled, with OK token)
- [ ] Empty file optimization (skip LLM calls)

#### Scheduler (multi-agent timing)
- [ ] Multi-agent scheduling with different intervals
- [ ] Config updates preserve timing state
- [ ] Fake timers for deterministic testing

### Integration Tests
- [ ] Cron + heartbeat (`wakeMode: "now"`, `wakeMode: "next-heartbeat"`)
- [ ] Webhook + heartbeat
- [ ] Config reload
- [ ] Media delivery with OK token

### E2E Tests
- [ ] WebSocket broadcast
- [ ] Health endpoints (`last-heartbeat`, `set-heartbeats`)
- [ ] Gateway startup/shutdown

## Phase 9: Documentation

- [ ] User-facing documentation (configuration, usage patterns)
- [ ] Developer documentation (architecture, extension points)
- [ ] API reference (runner, wake system, events)
- [ ] Migration guide (from polling/cron to heartbeat)
- [ ] Troubleshooting guide (common issues, debug tips)

## Phase 10: Optimization & Monitoring

### Cost Optimization
- [ ] Empty file optimization (skip LLM calls)
- [ ] Duplicate detection (24h window)
- [ ] Visibility gating (skip LLM if all disabled)
- [ ] Dynamic intervals (longer for low-priority agents)

### Monitoring
- [ ] Event metrics (sent, skipped, failed counts)
- [ ] Duration metrics (LLM call time, total time)
- [ ] Skip reason breakdown (which guards are most active)
- [ ] Duplicate detection rate

### Observability
- [ ] Structured logging (all guard checks, decisions)
- [ ] Event emission (every outcome)
- [ ] Health check endpoints
- [ ] Metrics dashboard (if applicable)

## Common Pitfalls

### Resource Leaks
- [ ] N timers for N agents (use single timer instead)
- [ ] Timer not cleared on shutdown
- [ ] Event listeners not unsubscribed

### Burst Triggers
- [ ] Multiple rapid triggers cause redundant runs
- [ ] Solution: Implement coalescing (250ms debounce)

### Idle Session Inflation
- [ ] Heartbeat activity keeps idle sessions alive
- [ ] Solution: Restore `updatedAt` on heartbeat-only replies

### Duplicate Alerts
- [ ] Same alert sent every cycle
- [ ] Solution: Track `lastHeartbeatText` per session, 24h window

### Cost Explosion
- [ ] LLM calls during idle periods
- [ ] Solution: Empty file optimization, token-based suppression

### Config Change Timing Reset
- [ ] Config reload resets timing, causes immediate heartbeat
- [ ] Solution: Preserve `lastRunMs` when updating config

### Race Conditions
- [ ] Concurrent heartbeat runs
- [ ] Solution: Serialize runs (one at a time)

### Timezone Issues
- [ ] Active hours calculated in wrong timezone
- [ ] Solution: Support user, local, or explicit IANA tz
