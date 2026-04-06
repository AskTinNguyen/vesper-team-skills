---
name: vesper-reference-ui-pipeline-davinci
description: Use when building premium Vesper UI from reference examples and the work needs a clear sequence across reference selection, Vesper-style translation, implementation, and final polish.
---

# Vesper Reference UI Pipeline — Davinci

## Overview
Orchestrate the full path from **reference example** to **premium Vesper UI**.

This skill does not replace the companion skills. It tells Davinci **when to use each one and in what order** so the work stays coherent:
1. harvest the right references
2. translate them into Vesper's design language
3. implement with strong layout and component discipline
4. polish until the result feels ship-ready

## Companion Skills
- `shadcn-component-reference-davinci` — choose and extract the right source examples
- `vesper-premium-ui-remix-davinci` — translate those references into Vesper's visual language
- `gestalt-frontend-design` — enforce perceptual correctness in the implementation
- `ui-design-brain` — choose the right component patterns and interaction models
- `polish` — run the final premium-quality pass

## Recommended Sequence
### Step 1 — Reference discovery
Use `shadcn-component-reference-davinci` to find the strongest example patterns and extract only the reusable structure, interaction model, and primitive combinations.

### Step 2 — Vesper translation
Use `vesper-premium-ui-remix-davinci` to reinterpret those patterns through Vesper's design language: warm editorial hierarchy, tactile depth, progressive disclosure, and premium restraint.

### Step 3 — Implementation discipline
Use `gestalt-frontend-design` and `ui-design-brain` to turn the chosen direction into perceptually correct, production-grade UI.

### Step 4 — Final polish
Use `polish`, then optionally `clarify`, `harden`, `animate`, `adapt`, or `optimize` if the surface still needs targeted refinement.

## When to Use
Use this skill when:
- the task starts from references or inspiration rather than a blank canvas
- multiple UI skills could apply and Davinci needs sequencing
- the goal is not just to build something working, but to make it feel like Vesper
- the work spans discovery, redesign, implementation, and polish

Do **not** use this skill when:
- only one isolated component needs a straightforward implementation
- the correct companion skill is already obvious and no orchestration help is needed
- the task is bug-fixing rather than reference-driven UI creation

## Pipeline Order
1. **Frame the UI**
2. **Harvest references**
3. **Translate to Vesper**
4. **Implement with Gestalt correctness**
5. **Polish to ship quality**

Read `references/pipeline.md` before applying the sequence.

## Routing Guide

| Need | Read |
|---|---|
| Full step order and handoff format | `references/pipeline.md` |
| Which skill to invoke for which situation | `references/decision-matrix.md` |
| Reusable prompt scaffold for multi-skill UI work | `references/handoff-template.md` |

## Quick Use Pattern
```text
Audience:
Primary action:
Mandatory sections:
Reference examples:
Borrowed patterns:
Vesper upgrades:
Implementation approach:
Polish checks:
```

## Output Contract
A good run through this pipeline produces:
- a clear reference set
- one chosen direction, not many competing ones
- a Vesper-specific translation of the borrowed ideas
- production-grade implementation decisions
- final polish criteria before shipping
- an implementation path that is obviously sequenced rather than improvised

## Success Criteria
This pipeline is working when:
- the source references are chosen intentionally rather than casually
- the final design feels like Vesper, not like a remix of demos
- layout and hierarchy stay strong during implementation
- the work moves in a clean order instead of bouncing randomly between sourcing, redesign, and code
- the final UI is refined enough to present as a confident product surface

## Common Mistakes
- going straight from reference discovery to code without translating the design language
- using the Vesper remix skill without first choosing strong references
- polishing before hierarchy and grouping are solved
- keeping multiple stylistic directions alive too long
- treating this orchestration skill as a substitute for the companion skills themselves

## Final Reminder
This skill is the **conductor**, not the orchestra.

Use it to decide the order of work. Use the companion skills to do the specialized work well.
