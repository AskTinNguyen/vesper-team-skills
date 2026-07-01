---
name: vesper-premium-ui-remix-davinci
description: Use when turning shadcn-examples or other UI references into premium Vesper-style components, sections, or pages with warm editorial hierarchy, tactile feedback, restrained contrast, and calmer product polish.
---

# Vesper Premium UI Remix — Davinci

## Overview
Turn rough reference UI into **premium Vesper UI**.

This skill is the styling and productization companion to reference-harvesting work. It assumes useful source examples already exist, then translates them into Vesper's design language:
- warm editorial surfaces
- approachable AI complexity
- tactile responsiveness
- progressive disclosure
- premium restraint instead of generic SaaS chrome

**RECOMMENDED COMPANION SKILL:** Use `shadcn-component-reference-davinci` first to identify the strongest source examples. Use this skill next to transform them into refined Vesper-quality output.

## When to Use
Use this skill when the task is:
- make a referenced component feel like Vesper
- upgrade a demo-style interface into premium product UI
- translate shadcn examples into warm editorial AI-native design
- refine a page so it feels calmer, clearer, and more tactile
- remove generic AI/SaaS styling from a borrowed layout

Do **not** use this skill when:
- the task is only to locate examples or references
- the user wants a literal clone of a source design
- the interface is already visually aligned with Vesper and only needs minor bug fixes

## Frame the Translation
Before designing, write exactly these three lines:

```text
Audience: <who this Vesper surface is for>
Primary action: <single core action>
Mandatory sections: <section 1>, <section 2>, <section 3>
```

If these are unclear, define them before styling.

## Apply This Skill
1. Start from 1-3 reference examples or an existing rough implementation.
2. Extract only the useful structure, interaction model, and primitive combinations.
3. Read `references/vesper-style-translation.md` and translate the layout into Vesper's visual language.
4. Use `references/upgrade-recipes.md` to reshape the specific UI type.
5. Run `references/quality-gate.md` before presenting the final result.
6. Prefer one confident direction over multiple half-finished flourishes.

## Routing Guide

| Need | Read |
|---|---|
| Core Vesper style translation rules | `references/vesper-style-translation.md` |
| UI-type-specific upgrade recipes | `references/upgrade-recipes.md` |
| Final Vesper polish and rejection checklist | `references/quality-gate.md` |
| Find the best source references first | Use `shadcn-component-reference-davinci` |

## Operating Rules
- Preserve the **reference pattern logic**, not the reference visual identity.
- Favor **calm confidence** over spectacle.
- Prefer **opaque, legible surfaces** in light mode.
- Use color to guide meaning, not to decorate everything.
- Add tactile feedback through states, depth, and motion restraint.
- Remove filler labels, generic badge colors, and dashboard clutter.
- Push toward fewer, clearer actions with stronger hierarchy.
- Fix shared visual primitives first when repeated problems appear.

## Vesper Translation Priorities
1. **Warm editorial hierarchy** — stronger headings, calmer body text, cleaner grouping.
2. **Tactile depth** — crisp hover/press/focus states, subtle elevation, responsive controls.
3. **Progressive disclosure** — reduce up-front clutter, reveal secondary actions intentionally.
4. **Accessible clarity** — better contrast, better semantic grouping, no color-only meaning.
5. **Premium restraint** — no neon gradients, no sci-fi chrome, no gimmicky AI aesthetics.

## Output Modes
- **Component remix** — card, panel, composer, empty state, toolbar, settings block
- **Section remix** — hero, control area, detail region, assistant workspace section
- **Page remix** — settings, chat workspace, dashboard, onboarding, search, profile, billing

## Success Criteria
This skill is working when:
- the final UI clearly feels like **Vesper**, not like a sourced demo
- borrowed layouts become calmer, more legible, and more intentional
- primary actions are easier to spot and secondary actions recede appropriately
- light mode stays rich and readable without washed-out translucency
- dark mode feels elegant and focused rather than gloomy or neon-heavy
- the result looks premium enough to ship, not merely good enough to demo

## Common Mistakes
- Keeping source-example spacing, copy, and badge treatment unchanged
- Translating visually without simplifying the action hierarchy
- Using same-hue text on tinted surfaces or chips
- Making AI interfaces feel colder or more mechanical than Vesper should
- Overusing gradients, blur, glass, or glow in the name of “premium”

## Final Reminder
The job is not to ask, “How do we reproduce this example?”

The job is to ask, **“How would Vesper express the useful idea inside this example?”**
