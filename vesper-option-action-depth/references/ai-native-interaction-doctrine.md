# AI-Native Interaction Doctrine

Portable doctrine snapshot for the `vesper-option-action-depth` skill package.

Inside the Vesper repo, the authoritative version lives at:
- `docs/internals/ai-native-interaction-doctrine.md`

This bundled copy exists so the skill remains self-contained when installed into:
- `~/.vesper/skills/`
- `~/.codex/skills/`
- skill repositories such as `vesper-team-skills`

## North Star

Vesper should feel:
- calm at a glance
- legible under pressure
- agentic when the user leans in

The default UI should help the user understand state.
The deeper UI should help the user understand what the agent sees, what it recommends, and what it can do next.

## Product Promise

Vesper is not a chat app with AI buttons scattered across it.
Vesper is agent-native software.

That means:
- the visible UI is the governance surface
- the agent layer is nearby, but not always foregrounded
- the product should move users from state -> interpretation -> delegation

## Terms

### Lean-In Trigger

The user action that reveals deeper agent help for the current target.

Desktop examples:
- `Option` + hover
- `Option` + click
- `Option` + drag
- `Option` + right-click

`Option` is the canonical desktop mapping today.
It is not the doctrine itself.
The doctrine is the idea of deepening the current interaction with an explicit lean-in trigger.

### Touched Target

The specific object the user is already interacting with.

Examples:
- workspace header
- card
- list row
- status chip
- schedule cell

### State

What is true right now.

Examples:
- `2 need review`
- `5 unread`
- `1 flagged`

### Interpretation

Why that state matters right now.

Examples:
- `Two chats are waiting on your decision`
- `These items changed since your last pass`

### Agent Action

What Vesper recommends or can do next.

Examples:
- `Summarize the waiting chats and draft replies`
- `Cluster unread work by urgency`

### Scoped Delegation

An agent action that inherits the scope of the touched target.

Examples:
- workspace-scoped triage from a workspace header
- role-scoped rebalancing from a role chip
- row-scoped help from a list item

### Manual Parity

The important path remains reachable without a modifier or AI reveal.

## Immutable Laws

### 1. Calm First

Every surface must make sense without AI depth.

Users should be able to:
- read the state
- inspect the object
- perform critical manual actions

without discovering hidden agent behavior first.

### 2. Same Gesture, Deeper Meaning

The lean-in trigger must deepen the current gesture.
It must not jump to an unrelated subsystem.

If hover explains, lean-in hover should suggest.
If click inspects, lean-in click should delegate.

### 3. Scope Must Stay Local

Agent actions inherit the scope of the touched target.

Never let a tiny local interaction unexpectedly trigger global or unbounded AI behavior.

### 4. Explanation Before Automation

The first deeper layer should usually answer:
- why this matters
- what Vesper recommends
- what would happen next

before it performs automation.

### 5. Manual Mastery Must Survive

The product must remain usable without modifiers.
AI depth enhances control.
It does not replace the base interaction model.

### 6. Discoverability Must Be Gentle

Users should be able to notice that deeper help exists without the interface constantly advertising itself.

Prefer:
- subtle copy such as `Hold Option for agent actions`
- small title shifts such as `Agent suggestion`
- stable preview footprints that deepen rather than transform

### 7. Live Signals Must Earn Trust

If Vesper recommends action from live state such as `needs review`, `flagged`, or `unread`, the user should be able to understand:
- what signal was observed
- what scope it covers
- why it led to this recommendation
- whether the information is current enough to trust

## Depth Ladder

Design AI-native interactions as a ladder, not a jump.

### Layer 1: State

What is true right now.

### Layer 2: Interpretation

Why it matters.

### Layer 3: Suggestion

What Vesper recommends next.

### Layer 4: Delegation

What the user can hand off from this exact scope.

### Layer 5: Automation

What Vesper can safely do with minimal supervision.

Default UI should reliably expose Layers 1 and 2.
Lean-in behavior should usually introduce Layer 3 before escalating to Layers 4 or 5.

## Gesture Decision Tree

When deciding how a surface should deepen, use this order:

1. Is the base user need understanding?
   Use hover or focus for explanation.
   Use lean-in hover for suggestion.
2. Is the base user need inspection or pinning?
   Use click for inspection.
   Use lean-in click for scoped delegation or focused AI workflow.
3. Is the base user need deterministic commands?
   Use right-click or menu for manual actions.
   Use lean-in right-click for agent actions and suggested prompts.
4. Is the base user need spatial manipulation?
   Use drag for direct manipulation.
   Use lean-in drag for AI-assisted regrouping, routing, or reorganization.

Do not add lean-in depth unless the deeper action is a natural extension of the base gesture.

## Surface Contract

Every AI-native surface should define these fields before implementation:

1. Target
2. Base Action
3. Lean-In Trigger
4. First Reveal
5. Scope Boundary
6. Recommendation Source
7. Manual Fallback
8. Exit Path

If any field is vague, the interaction is not ready.

## When Not To Use This Pattern

Avoid lean-in depth when:
- the action is destructive and consequences are hard to preview
- the surface already demands high precision, such as dense settings forms
- the user is in a binary confirm/cancel flow with little interpretive value
- the recommendation would be too weak, stale, or unscoped to be trustworthy
- the deeper layer adds spectacle more than leverage

## Ship Gate

An AI-native interaction is ready to ship only if all of these are true:

1. The base UI stands on its own.
2. The lean-in trigger deepens the current gesture instead of changing the subject.
3. The deeper action is scoped to the touched target.
4. The first reveal improves understanding before pushing automation.
5. Important functionality remains reachable without modifiers.
6. The interaction teaches itself subtly in product, not just in documentation.
7. The source of live recommendations is legible enough to trust.
8. The design reduces decision effort instead of adding noise.
