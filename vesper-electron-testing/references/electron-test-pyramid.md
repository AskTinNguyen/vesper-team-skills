# Electron Test Pyramid (Vesper)

## Layer Choice

Use this decision matrix:

- Pure renderer logic/state mapping: component test.
- Interaction depends on pointer/focus/layout/scroll behavior: Electron E2E.
- Readability/layout density regression: visual snapshot + E2E assertion.
- Unknown renderer state bug and no existing harness: temporary CDP diagnostic.

## Reliability Rules

- Use fixtures, never live workspace state.
- Use `data-testid` for interaction-critical controls.
- Assert behavior, not implementation details.
- Keep tests independent and order-agnostic.
- Avoid time-sensitive assertions without clock control.

## Preferred Selector Contract

- `data-testid="schedule-card-{id}"` for card root.
- `data-testid="schedule-card-title"` for visible title node.
- `data-testid="schedule-card-actions"` for hover/overlay action container.
- `data-testid="schedule-toggle"` for enable/disable switch.
- `data-testid="schedule-overflow"` for menu trigger.

Prefer explicit test IDs over class selectors for stability.

## Anti-Patterns

- Full-page `textContent` dumps in debugging scripts.
- Tests that require personal user data in `~/.vesper`.
- Assertions tied to CSS utility class strings when user-visible behavior can be asserted instead.
- Keeping CDP debug scripts as the only regression safety net.

