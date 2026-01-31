# Polling Strategies Reference

## Interval Recommendations

| Mode | Recommended Interval | Rationale |
|------|---------------------|-----------|
| Pure Supervisor | 5 min (300s) | Task changes are infrequent; avoid noise |
| PR Status Tracker | 5 min (300s) | GitHub review cycles are slow |
| Review Follower | 3 min (180s) | Review agents complete faster than humans |
| Active Development | 2 min (120s) | When multiple agents are actively working |

**Minimum interval:** 120 seconds. More frequent polling generates noise without actionable data.

## Stall Detection

### What Counts as a Stall

A task is considered stalled when:

1. Status is `in_progress`
2. No field changes for N consecutive poll cycles
3. No related git activity (commits, branch pushes)

### Stall Thresholds

| Context | Cycles Before Flag | Wall Clock (at 5min interval) |
|---------|-------------------|-------------------------------|
| Simple task | 2 cycles | ~10 min |
| Complex task | 4 cycles | ~20 min |
| Long-running task (explicitly marked) | 8 cycles | ~40 min |

### Stall Response Escalation

```
Cycle N+2: Add note to task "Appears stalled"
Cycle N+4: Create diagnostic task "Investigate stall on #X"
Cycle N+6: Flag for human "[STALLED] Task #X unresponsive"
```

## Snapshot Storage

Snapshots are stored in `/tmp/agent-supervisor-snapshots/`:

```
/tmp/agent-supervisor-snapshots/
  ├── {list-id}-latest.json     # Most recent snapshot (for quick diff)
  ├── {list-id}-20260131-143022.json  # Timestamped snapshots
  └── ...
```

Snapshots are ephemeral (cleared on reboot). For persistent history, use `/dispatch` archive system.

## Diff Detection Strategy

The `task-diff.sh` script compares snapshots field-by-field:

| Field | Change Significance |
|-------|-------------------|
| `status` | High — progress or regression |
| `owner` | Medium — agent claimed or released task |
| `subject` | Low — rename, usually cosmetic |
| `blockedBy` | High — dependency resolution |
| `description` | Not tracked — too noisy |

## Adaptive Polling

For long-running supervisory sessions, consider adaptive intervals:

```
If changes detected in last cycle:
  Next interval = min(current, 120s)  # Speed up
If no changes for 3 cycles:
  Next interval = min(current * 1.5, 600s)  # Slow down
If critical flag raised:
  Next interval = 60s  # Urgent mode
```

This is not implemented in the scripts but can be orchestrated by the supervising agent.
