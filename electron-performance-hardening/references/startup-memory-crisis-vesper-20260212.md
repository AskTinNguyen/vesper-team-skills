# Startup Memory Crisis Reference (Vesper, 2026-02-12)

## Incident Summary

- Symptom: macOS showed "Your system has run out of application memory" during Vesper + iTerm usage.
- Signals:
  - Telegram auto-connect/retry burst (`EFATAL: AggregateError`) across multiple accounts.
  - Heartbeat runs repeatedly creating/destroying internal worker sessions.
  - Repeated secure-storage credential reads during startup fan-out.

## Applied Fixes

### 1) Heartbeat worker pooling

- `apps/electron/src/main/heartbeat/heartbeat-service.ts`
  - Added per-target worker reuse map (`workerSessionByTarget`).
  - Added `getOrCreateWorkerSession(...)` and `releaseWorkerSession(...)`.
  - Switched target lookup to metadata path (`getSessionMetadata`) to avoid loading session message payloads.

- `apps/electron/src/main/sessions.ts`
  - Added `resetSessionForReuse(...)` to clear transient runtime state in-place.
  - Skipped persistence for `internalType === 'heartbeat-run'` sessions.

- `packages/shared/src/agent/vesper-agent.ts`
  - Added `resetConversation()` to clear SDK resume and pending runtime state without reconstructing agent objects.

### 2) Startup credential deduplication

- `packages/shared/src/credentials/manager.ts`
  - Added short-lived read cache (`readCache`) and in-flight dedupe (`readInFlight`).
  - Added `VESPER_CREDENTIAL_CACHE_TTL_MS` (default `5000`).

### 3) Telegram reconnect storm control

- `apps/electron/src/main/telegram-ipc.ts`
  - Staggered startup auto-connect across accounts.
  - Added `VESPER_TELEGRAM_STARTUP_STAGGER_MS` (default `700`).

- `apps/electron/src/main/telegram-service.ts`
  - Added global reconnect slot reservation across instances.
  - Added `VESPER_TELEGRAM_GLOBAL_RECONNECT_GAP_MS` (default `1200`).
  - Added `VESPER_TELEGRAM_GLOBAL_RECONNECT_JITTER_MS` (default `250`).

## Why It Reduced Memory Pressure

1. Fewer repeated object/session creations lowered transient allocations and watcher churn.
2. Shared credential reads collapsed duplicate secure-storage I/O bursts.
3. Reconnect storms stopped competing for resources at the same instant.
4. Internal heartbeat sessions no longer generated unnecessary persistence churn.

## Tuning Checklist

- If startup still spikes:
  - Increase `VESPER_TELEGRAM_STARTUP_STAGGER_MS`.
  - Increase `VESPER_TELEGRAM_GLOBAL_RECONNECT_GAP_MS`.
  - Increase credential cache TTL modestly (5s -> 10s) if startup phases overlap.

- If reconnect recovery feels too slow:
  - Reduce reconnect gap/jitter gradually and re-measure retry overlap.

## Follow-up Hardening Candidates

- Lazy/bounded Telegram binding monitoring at startup.
- Session message eviction for inactive sessions in memory manager.
- Dev log rate limiting and iTerm scrollback caps.

## Linked Documentation

- `docs/solutions/performance-issues/startup-memory-crisis-telegram-reconnect-churn-vesper-electron-20260212.md`
