# Scheduler Timetable Regression Suite

Use this suite to prevent known Scheduler Timetable failures.

## Must-Cover Cases

1. Hover actions do not collapse card content.
2. Moving pointer across cards does not hide title/prompt metadata.
3. Overlay controls appear on hover/focus and do not reserve permanent layout space.
4. Clicking a timetable card opens detail panel for that schedule.
5. Detail panel hide/show control works and preserves selection state.
6. Disabled schedules remain visible in timetable when `showDisabled` is on.
7. Disabled schedule rendering is subtle (muted text) without title truncation from status tags.
8. Toggle actions do not instantly remove item during current view; removal only follows filter/lane rules.
9. Recurring and one-off lanes stay isolated in their respective views.
10. Filter combinations (persona/category/health/channel) work consistently in list and timetable views.

## Suggested Test Breakdown

Component level:
- Card rendering in enabled and disabled states.
- Action overlay visibility state logic.
- Filter predicate behavior for recurring vs one-off lanes.

Electron E2E level:
- Hover across multiple cards and assert content remains visible.
- Click card and verify detail panel content updates.
- Toggle enable/disable and verify grace behavior in current view.
- Switch lanes/views and verify data separation and filter continuity.

Visual snapshot level:
- Dense week with many cards.
- Empty state.
- Detail panel open full-width.
- Disabled-visible mode.

## Evidence Format

For each fixed bug:

- Failing test name (before fix)
- Passing test name (after fix)
- Screenshot artifact path
- Root cause note (1-3 lines)

