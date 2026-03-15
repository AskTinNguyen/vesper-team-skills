---
name: vesper-option-action-depth
description: "This skill should be used when applying Vesper's desktop lean-in modifier pattern to hover, click, drag, and menu interactions. Triggers: Option hover, Alt hover, scoped delegation, agent actions."
---

# Vesper Option-Action Depth

Treat Vesper's desktop lean-in modifier as the bridge between calm UI and deeper agent help.

On macOS, that modifier is usually `Option`.
On Windows and Linux, it is usually `Alt`.
The interaction model is:
- explanation becomes suggestion
- inspection becomes delegation
- direct manipulation becomes AI-assisted reorganization

## When To Use

Use this skill when:
- adding lean-in hover, click, drag, or right-click behavior
- designing compact agent affordances that should not dominate the default UI
- refining workspace, mission, schedule, artifact, or inspector controls with deeper AI actions
- deciding whether a surface should explain state, propose action, or launch a scoped AI workflow
- reviewing agentic UI for noise, surprise, or poor discoverability

## When Not To Use

Do not use this skill when:
- the action is destructive and hard to preview safely
- the surface already requires high-precision manual input, such as dense settings forms
- the recommendation would be stale, weak, or unscoped
- a domain-specific Vesper skill is the primary driver and this pattern is only secondary

## Read In This Order

1. Doctrine:
   `references/ai-native-interaction-doctrine.md`
2. Pattern library:
   `references/option-action-depth-operating-model.md`
3. Apply workflow:
   `workflows/apply-option-action-depth.md`

## Core Product Model

Use this grammar by default:

- default = show state
- hover/focus = explain state
- lean-in + same action = reveal the deeper agent layer

The lean-in modifier is not a shortcut.
It is the user's signal that says:
- show me what the agent sees
- show me what the agent recommends
- let me delegate from here

## Good Fits In Vesper

Common surfaces:
- cards
- rows
- chips
- menus
- inspectors

Pair this skill with the relevant domain skill when the surface belongs to a larger subsystem such as Mission Control, scheduling, artifacts, or testing-heavy renderer work.

## Deliverable

A finished design or implementation should be easy to summarize as:

- Base interaction:
- Lean-in trigger:
- First deeper reveal:
- Scope:
- Signal source:
- Freshness or evidence:
- Manual fallback:
- Exit path:
