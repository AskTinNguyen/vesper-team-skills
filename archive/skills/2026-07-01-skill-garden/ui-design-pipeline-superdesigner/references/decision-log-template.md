# Design Decision Log Template

Use this template after variant comparison.

## Metadata
- Date (ICT):
- Project:
- Surface/Page:
- Owner:

## Objective Framing (3 Lines)
- Audience:
- Primary action:
- Mandatory sections:

## Baseline
- Baseline ID:
- Baseline preview/link:
- Notes on hierarchy/rhythm/action zones:

## Variants Evaluated

### Gestalt-Backed Scoring (1-5 per criterion)

| Variant ID | Direction Label | Continuity | Figure-Ground | CTA Salience | Similarity | Impl. Readiness | Total | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---|
| | | | | | | | | |
| | | | | | | | | |
| | | | | | | | | |

**Scoring definitions:**

- **Continuity**: Does the eye follow a clear, unbroken path to the primary action? (1 = eye wanders, no reading path; 5 = unbroken flow, primary action is the terminal point)
- **Figure-Ground**: Are primary elements clearly elevated above secondary? (1 = flat, no depth hierarchy; 5 = 2+ contrast tiers, primary content unmistakably prominent)
- **CTA Salience**: Does the CTA stand out and group with its intent? (1 = CTA blends in, ambiguous clickability; 5 = CTA is strongest figure, visually grouped with context)
- **Similarity**: Are same-function elements treated identically? (1 = mixed styling for same-role elements; 5 = all same-role elements share identical treatment)
- **Implementation Readiness**: Can this be built with standard components and spacing tokens? (1 = requires custom hacks, non-standard spacing; 5 = maps directly to shadcn/ui + Tailwind scale)

**Gate: Every variant must score 3+ on every criterion before proceeding to selection.**

## Selection
- Selected Variant ID:
- Rejected Variant IDs:
- Selection rationale (use-case-based, not aesthetic):

## Accessibility Gate (Step 4.5)

Run selected variant through `/gestalt-frontend-design` accessibility cross-check:

| Visual Cue | Semantic Equivalent | Pass? | Notes |
|---|---|---|---|
| Proximity grouping | `<fieldset>`, `<section>`, `role="group"`, `aria-labelledby` | | |
| Color similarity | Redundant shape/icon/text cue (never color alone) | | |
| Figure-ground contrast | WCAG ratios (4.5:1 text, 3:1 UI components) | | |
| Common fate (motion) | `prefers-reduced-motion` respected | | |
| Continuity (visual flow) | DOM order matches visual order | | |
| Closure (implied content) | `aria-expanded`; explicit screen reader labels | | |

**Gate: All rows must pass before implementation.**

## Implementation Notes
- Scaffold source:
- Gestalt layout-type patterns applied (from `/gestalt-frontend-design` reference):
- Manual micro-polish applied:
  - Spacing:
  - Typography:
  - Contrast:
  - Alignment/interactions:
- Dark mode verified: yes/no
- Responsive breakpoints verified: yes/no

## Follow-Up
- Open questions:
- Next iteration trigger (if needed):
- Handoff notes:
