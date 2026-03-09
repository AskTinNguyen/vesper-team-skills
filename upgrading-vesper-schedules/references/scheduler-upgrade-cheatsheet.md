# Scheduler Upgrade Cheatsheet

Use this reference when upgrading or explaining legacy Vesper schedules.

## Core Rule

Treat schedule upgrade work as two separate jobs:

1. Schema/runtime normalization that Vesper already performs automatically.
2. Behavioral/routing decisions that still need inspection and often user approval.

## Legacy To Current Mapping

| Legacy concept | Current concept | Notes |
|---|---|---|
| `executionMode: "yolo_loop"` | `executionMode: "issue_run"` + `executionStrategy: "loop"` | Current reliable runtime contract |
| legacy single session reference via `lastRunSessionId` | `targetSessionId` plus `scheduleSessionId` | Delivery/routing and continuity are now distinct |
| implicit delivery via active session | `deliveryPolicy: "session-bound"` | Safest compatibility model for session-following behavior |
| explicit external thread delivery | `deliveryPolicy: "thread-bound"` + `deliveryRoute` | Requires explicit Telegram/Slack route |
| `seedSessionId` in older mutation flows | `targetSessionId` | Older alias remains accepted in update paths |

## What Vesper Already Normalizes

Expect Vesper to auto-normalize many legacy records on load or update, including:

- `yolo_loop` runtime normalization
- defaulting modern reliable runtime metadata
- promoting legacy session references into `targetSessionId`
- defaulting `scheduleSessionId`
- normalizing `deliveryPolicy`
- normalizing `bindingIntent`
- normalizing `executionContextMode`

Do not rewrite a schedule just to restate what the runtime already corrected.

## Use `schedule_repair` For These Cases

Reach for `schedule_repair` first when the problem is operational health:

- missing `targetSessionId`
- missing `scheduleSessionId`
- missing owner metadata that can be inferred
- thread-bound schedule missing `deliveryRoute`
- disconnected Telegram/Slack route
- timeout history or other repair-style health findings

Run audit mode first:

```text
schedule_repair({ apply: false })
```

Apply only after user approval:

```text
schedule_repair({ apply: true, scheduleIds: ["..."] })
```

## Use `schedule_update` For These Cases

Reach for `schedule_update` when the user is intentionally changing behavior:

- prompt text
- cadence or time
- timezone-sensitive schedule setup
- `deliveryPolicy`
- `deliveryRoute`
- `executionContextMode`
- persona selection
- whether the schedule should target a different chat/session

## Common Failure Patterns

### Missing continuity session

Symptom:
- schedule can still have a target, but append/history behavior is broken

Preferred handling:
- inspect `scheduleSessionId`
- let `schedule_repair` suggest a rebind
- use `schedule_update` only for approved continuity redesign

### Missing target session

Symptom:
- delivery cannot follow the original chat binding

Preferred handling:
- run `schedule_repair`
- rebind only to a verified replacement session

### Thread-bound without explicit route

Symptom:
- delivery policy requires more routing information than the record has

Preferred handling:
- either set a valid `deliveryRoute`
- or switch back to `deliveryPolicy: "session-bound"` if the user wants follow-session behavior

### Owner inference is ambiguous

Symptom:
- one target session maps to multiple messaging contexts

Preferred handling:
- do not guess
- surface the ambiguity and ask which context should own the schedule

## Safe Explanation Pattern

When explaining an upgrade, use this order:

1. State what Vesper already normalized automatically.
2. State what is still broken or ambiguous in the actual schedule record.
3. State whether `schedule_repair` can fix it deterministically.
4. State what choices require the user's approval.
