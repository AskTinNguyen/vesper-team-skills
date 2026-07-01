# Observed `sessions.ts` Extraction Sequence

Use this reference when seam order is unclear and you want the chronology from the `sessions.ts` case study.

## Contents

- [Provenance](#provenance)
- [Phase Shape](#phase-shape)
- [Representative Sequence](#representative-sequence)
- [Observed Per-Commit Loop](#observed-per-commit-loop)

## Provenance

This chronology is reconstructed from Tung Nguyen's `apps/electron/src/main/sessions.ts` extraction commits observed on 2026-03-13 through 2026-03-17.

Treat it as a default heuristic unless the active refactor plan for the current task says otherwise.

## Phase Shape

The work appears to move from outer seams toward inner seams:

1. callback and registration groups
2. feature and action families
3. event-family handlers
4. lifecycle and storage seams
5. runtime, config, and state-transition helpers
6. remaining orchestration core

## Representative Sequence

### 1. Split wiring first

Examples:

- `Split session manager callback groups`
- `Extract telegram and source callbacks`
- `Extract slack and messaging callbacks`
- `Extract browser ui callbacks`
- `Extract Vesper UI callbacks`
- `Extract escalation callbacks`
- `Extract mission control callbacks`
- `Extract mission briefing callbacks`

Why this matters:

- these seams already look like one job
- they have lower behavioral risk
- they shrink the monolith quickly

### 2. Split feature and action families

Examples:

- publishing/worktree
- schedule context
- status automation
- OpenPencil helpers
- Slack and Telegram bootstrap
- collaboration and mission callbacks
- canvas action, structure, feedback, runtime, and document handlers
- TillDone command, presentation, lite/pending-plan, and objective helpers

Why this matters:

- the monolith starts reading like a map of domains instead of one wall of code
- each domain can still keep a thin adapter in the facade

### 3. Split event-family processing

Examples:

- `process-event-text`
- `process-event-runtime`
- `process-event-tool-start`

Why this matters:

- event handlers can be partitioned by case family
- the overall event loop can stay intact while inner branches move out

### 4. Split lifecycle and storage

Examples:

- source lifecycle
- detached-session lifecycle
- startup workspace lifecycle
- session storage lifecycle
- proactive compaction
- session transition
- reset session
- processing stop
- processing cancel

Why this matters:

- these seams are more stateful
- earlier extractions make them easier to isolate cleanly

### 5. Split runtime/config/state transitions

Examples:

- provider auth
- model/runtime selection
- persona memory bootstrap
- Pi runtime config
- interactive tool profile
- provider failover
- session creation
- set session persona
- session provider
- agent runtime creation
- session model

Why this matters:

- these seams touch foundational state
- they are safer after the surrounding noise is gone

## Observed Per-Commit Loop

Inside each phase, the recurring loop appears to be:

1. pick one stable seam
2. extract to an adjacent file named after the job
3. keep the facade wrapper thin
4. fix the smallest typing or dependency issue needed at the boundary
5. run targeted verification
6. record the new line count and move on
