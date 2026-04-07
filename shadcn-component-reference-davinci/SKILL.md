---
name: shadcn-component-reference-davinci
description: Use when designing a polished React/Tailwind component, section, or page by using shadcn-examples as reference material for layout, interaction, and composition rather than literal copying.
---

# Shadcn Component Reference — Davinci

## Overview
Use **shadcn-examples** as a **reference library**, not as a product to recreate.

This skill helps Davinci:
- find the closest example patterns for a requested UI
- extract the useful structure, primitives, and interaction ideas
- recombine them into a **more refined, more beautiful** component for the target product

**This is not a skill for building example galleries.** It is a skill for using the example repo as visual and architectural reference material while designing stronger final UI.

## When to Use
Use this skill when the task is:
- build a beautiful component from references
- design a section, screen, or page using shadcn examples as inspiration
- translate rough demo examples into production-quality UI
- find the closest shadcn-examples pattern for a requested interface
- remix multiple examples into one stronger component

Do **not** use this skill when:
- the goal is to clone the shadcn-examples site itself
- the task is pure gallery/catalog architecture
- one clear local design-system pattern already exists and external references are unnecessary

## Core Principle
**Borrow structure, not identity.**

Extract from the source repo:
- layout skeleton
- grouping strategy
- primitive combinations
- interaction patterns
- density and section ordering

Then upgrade for the target product:
- typography
- spacing rhythm
- contrast
- copy
- responsive behavior
- states and polish

The final output should feel **better than the source example**, not merely similar to it.

## Apply This Skill
1. Classify the requested UI shape.
2. Pick **2-3 relevant examples** from `references/example-map.md`.
3. Read `references/patterns.md` to extract reusable structure.
4. Read `references/keep-omit.md` to avoid cargo-culting demo repo weaknesses.
5. Rebuild the target UI with local primitives and the active design skills (`gestalt-frontend-design`, `ui-design-brain`, `polish`).
6. Verify that the result matches the target product better than the original example did.

## Routing Guide

| Need | Read |
|---|---|
| Find the closest source examples by UI type | `references/example-map.md` |
| Learn the reference-harvesting workflow | `references/patterns.md` |
| Know what to borrow, upgrade, or avoid | `references/keep-omit.md` |
| Implement the final interface with stronger design quality | Use this skill + `gestalt-frontend-design` + `ui-design-brain` |

## Quick Use Pattern
Use this prompt shape internally before implementation:

```text
Requested UI:
Closest source examples:
Borrow from each:
Upgrade for target product:
Final component/page shape:
```

## Output Modes
Choose one of these output modes based on the request:
- **Single component** — card, form block, settings panel, empty state, table section
- **Section** — hero, dashboard section, onboarding block, billing section, chat composer area
- **Full page** — settings page, dashboard, auth flow, product detail, search results, chat UI

## Success Criteria
This skill is working when:
- the chosen examples are clearly relevant to the requested UI
- the final UI reuses the **pattern logic**, not the literal source design
- the result uses the target app's copy, tokens, and interaction priorities
- visual hierarchy, grouping, and affordances are stronger than in the raw example
- the final output looks intentional and product-ready rather than like a demo remix

## Common Mistakes
- Treating the repo as a template library to copy verbatim
- Reusing weak demo copy, placeholder content, or arbitrary badge colors
- Borrowing only visuals while missing the underlying layout logic
- Taking one example too literally when the better answer is a hybrid of two or three
- Shipping demo-grade polish instead of upgrading spacing, states, and contrast

## Final Reminder
**shadcn-examples is reference material.** Davinci's job is to turn that reference material into UI that is calmer, clearer, and more beautiful for the actual product context.
