# Option-Action Depth Operating Model

Practical reference for applying Vesper's lean-in interaction pattern.

This file is the pattern library.
It translates the doctrine into concrete interaction choices, preview anatomy, and surface recipes.

Read this after:
- `ai-native-interaction-doctrine.md`

## Purpose

Use this reference when you need to decide:
- which gesture gets the deeper layer
- what the first deeper reveal should contain
- how to keep the interaction scoped, teachable, and reversible

## Status

This is the target operating model for Vesper's desktop lean-in interactions.

Current repo evidence most clearly proves the pattern in workspace-group hover and click previews.
Treat right-click and drag variants as pattern candidates unless the product area has implemented them explicitly.

## Canonical Desktop Mapping

On desktop, the lean-in modifier is:
- `Option` on macOS
- `Alt` on Windows/Linux

Implementation guidance:
- implement behavior against `event.altKey`
- render platform-aware copy such as `Hold Option for agent actions` or `Hold Alt for agent actions`

Use the same action, then deepen it with the lean-in modifier:

| Base action | Default meaning | Lean-in meaning |
| --- | --- | --- |
| hover | explain | suggest |
| click | inspect | delegate |
| right-click | manual actions | agent actions |
| drag | direct manipulation | AI-assisted reorganization |

This mapping is the default.
Break it only when continuity would be stronger with a different choice.

## Preview Anatomy

Whenever possible, the deeper layer should reuse the same preview footprint as the default layer.

A good AI-native preview usually has four parts:

1. Signal
   The live fact or state the preview is grounded in.
2. Why It Matters
   A short interpretation of that signal.
3. Recommended Next Move
   The agent's suggestion or scoped prompt.
4. Manual Escape Hatch
   A clear close, ignore, or manual alternative.

Example:

- Signal: `2 chats need review`
- Why it matters: `Both are waiting on your decision`
- Recommended next move: `Summarize both and draft replies`
- Manual escape hatch: `Open chats manually`

## Depth Choice Guide

Use this guide when choosing the first lean-in behavior.

### Lean-In Hover

Best when the user is already scanning or trying to understand status.

Use for:
- signals
- badges
- rows
- small cards
- tooltips

Good first reveal:
- suggestion
- short scoped prompt
- why-now explanation

Avoid when:
- the target is tiny and easy to lose
- the preview would become dense or multi-step

### Lean-In Click

Best when the user wants a persistent agent workspace.

Use for:
- focused AI workflows
- prefilled chat handoff
- scoped delegation entry points

Good first reveal:
- pinned agent panel
- pre-composed prompt
- actionable recommendation set

Avoid when:
- the same outcome should happen automatically on hover
- the target is too minor to justify state change

### Lean-In Right-Click

Best when the user is already in command mode and expects a menu.

Use for:
- contextual agent actions
- generated prompt options
- `Let Vesper handle this` variants

Good first reveal:
- suggested actions at the top
- manual actions preserved below

Avoid when:
- the surface already hides too much behind menus

### Lean-In Drag

Best when the base action already implies intent through movement.

Use for:
- regrouping
- routing
- clustering
- lane reorganization

Good first reveal:
- ghost preview of proposed grouping
- labeled drop target meaning
- reversible confirmation

Avoid when:
- user intent cannot be inferred from spatial movement
- the cost of a wrong guess is high

## Surface Recipes

### Cards

Examples:
- workspace cards
- mission cards
- agent cards

Default:
- show current state
- show one clear next manual step

Lean-in:
- hover reveals what the agent sees in this card
- click opens a card-scoped AI workflow

Recommended preview anatomy:
- signal summary
- why this card matters now
- one suggested move
- one manual fallback

### Schedule

Examples:
- schedule rows
- run status chips
- forecast cells

Default:
- inspect timing, health, drift, and last result

Lean-in:
- hover suggests optimization, repair, or rerouting
- click opens a schedule-scoped AI edit flow
- drag can imply AI-assisted rescheduling or regrouping

Recommended preview anatomy:
- signal: lateness, failure, drift, overload
- why it matters
- recommended fix
- open schedule manually

### Roles

Examples:
- persona chips
- role badges
- staffing labels

Default:
- explain role, owner, load, or current responsibility

Lean-in:
- hover suggests reassignment, triage, or balancing
- click opens a role-scoped control flow

Recommended preview anatomy:
- current load
- risk or opportunity
- suggested rebalance
- inspect manually

### List Items

Examples:
- session rows
- artifact rows
- inbox entries
- checklist rows

Default:
- show row details and allow manual actions

Lean-in:
- hover explains why the row matters now
- right-click reveals row-scoped agent actions
- drag asks Vesper to sort or cluster similar rows

Recommended preview anatomy:
- row signal
- why this row surfaced
- recommended action
- open row normally

### Help Tooltips

Examples:
- status help
- icon tooltips
- `what does this mean?` affordances

Default:
- explain the UI object

Lean-in:
- hover upgrades explanation into recommendation

Recommended preview anatomy:
- meaning
- why it matters now
- what Vesper suggests

### Menus And Popovers

Examples:
- context menus
- kebab menus
- action popovers

Default:
- deterministic manual commands

Lean-in:
- shows agent suggestions, generated prompts, and scoped delegation actions

Recommended structure:
- agent suggestions first
- divider
- deterministic manual actions after

## Live Signal Rules

When a recommendation comes from live signals such as `needs review`, `flagged`, `unread`, or `overloaded`, the preview should make the source legible.

Include at least two of:
- explicit count
- time freshness
- scope label
- reason phrase

Example:
- `2 chats need review in Default`
- `Both changed since your last pass 8 minutes ago`

## Error, Empty, And Stale States

If the deeper layer cannot provide confident guidance, degrade gracefully.

### No Signal

Use when the target has no meaningful recommendation source yet.

Show:
- what the surface means
- that no stronger recommendation is available
- the manual fallback

Example:
- `No active recommendation right now`
- `Open this item manually to inspect it`

### Stale Signal

Use when the recommendation may no longer reflect current state.

Show:
- freshness warning
- last known evidence
- safe manual next step

Example:
- `Recommendation may be stale`
- `Last reviewed 2 hours ago`
- `Refresh or open manually`

### Launch Failed

Use when scoped AI handoff cannot open or execute.

Show:
- what failed
- the manual path
- a retry action if appropriate

### Manual Fallback Only

Use when permissions, missing data, or policy prevent the lean-in action.

Show:
- why delegation is unavailable
- the manual action that still works

## Discoverability Cues

Teach the pattern subtly in product.

Good cues:
- `Hold Option/Alt for agent actions`
- `Agent suggestion`
- icon or label shift while the modifier is pressed
- unchanged preview shell with deeper content swapped in

Bad cues:
- constant AI badges everywhere
- giant assistant chrome
- unexplained secret power features

## Worked Example

### Workspace Signal In Session List

This example reflects the current proven interaction shape in the workspace group popover.

Target:
- workspace signal row inside the workspace actions popover

Base interaction:
- hover previews the signal
- click pins the preview

Lean-in trigger:
- hold `Option` on macOS or `Alt` on Windows/Linux

Lean-in behavior:
- lean-in click launches a scoped agent chat for that signal
- lean-in hover keeps the same preview footprint but shifts the meaning toward recommendation

Signal source:
- workspace counts such as `need review`, `unread`, or `active`

Freshness or evidence:
- explicit count
- workspace scope
- why-now phrasing in the preview copy

Manual fallback:
- pin the preview
- open or inspect the related chats manually

Exit path:
- move pointer away
- blur focus
- release the modifier
- close the popover

Implementation notes:
- listen to `event.altKey`
- never let plain hover launch agent actions
- keep the preview anchored to the touched signal row

Verification:
1. Plain hover previews without mutation.
2. Plain click pins or unpins the preview.
3. Lean-in click launches the scoped agent action.
4. Keyboard focus can reach the same preview state.
5. Releasing the modifier returns the UI to the non-agent layer.

## Motion And Timing

Recommended defaults:
- hover dwell: `150-250ms`
- hover close delay: `100-150ms`
- reveal transition: `150-200ms`
- no bounce
- no theatrical motion

The deeper layer should feel precise, not performative.

## Accessibility Cross-Check

This pattern only holds if:
- hover reveals are reachable on focus
- important actions remain available without `Option`
- color is never the only signal
- DOM order matches reading order
- modifier behavior does not trap keyboard users
- motion respects `prefers-reduced-motion`

## Anti-Patterns

Avoid:
- plain hover that opens windows or causes mutations
- lean-in actions that change scope unexpectedly
- jittery hover targets
- previews that grow so much they become mini apps
- recommendations without enough signal context to trust
- personality layers before utility is proven

## Surface Spec Template

Use this mini template when adding a new AI-native surface:

1. Target:
2. Base gesture:
3. Lean-in trigger:
4. Default reveal:
5. Lean-in reveal:
6. Scope boundary:
7. Signal source:
8. Manual fallback:
9. Exit path:

## Success Test

The pattern is working when the user can say:

1. I understand the default UI without needing the modifier.
2. Leaning in gives me better judgment, not just more UI.
3. The deeper layer stays scoped to what I was already touching.
4. I can move from state -> interpretation -> delegation without context switching.
