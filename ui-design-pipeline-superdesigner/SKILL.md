---
name: ui-design-pipeline-superdesigner
description: This skill should be used when creating or refining UI screens with an AI-assisted design pipeline that requires clear objective framing, parallel variant generation, decisive direction selection, implementation handoff, and decision-history tracking.
---

# UI Design Pipeline — SuperDesigner Pattern

## Overview
Apply a repeatable UI pipeline for faster iteration and higher consistency: frame objective, generate baseline, generate three variants, choose one direction, implement with perceptual correctness, and track decision history.

## When to Use
Trigger this skill when requests involve:
- Building a new page or component with multiple visual directions.
- Improving speed from idea to mockup to implementation.
- Reducing subjective design churn by enforcing a structured selection process.
- Producing commit-ready UI scaffolding before manual polish.

## When NOT to Use
Do NOT use this skill when:
- Building a single component (form, modal, card, nav) with a clear brief — invoke `/gestalt-frontend-design` directly instead.
- Reviewing or auditing existing UI for spacing/contrast/accessibility issues — invoke `/gestalt-frontend-design` directly instead.
- Polishing an already-implemented page — invoke `/gestalt-frontend-design` directly instead.

This skill is for **exploration and direction-setting**. Gestalt Frontend Design is for **implementation quality**. They work together.

## Workflow

### Step 1 — Frame Objective in 3 Lines

Write exactly three lines before generation:
1. Who the page is for.
2. What primary action the page should drive.
3. Which sections are mandatory.

Use this framing template:
```text
Audience: <target user>
Primary action: <single core action>
Mandatory sections: <section 1>, <section 2>, <section 3>
```

**Gate: Do not proceed until all 3 lines are explicit.** If the user has not provided these, ask before continuing.

### Step 2 — Generate Baseline

Generate a baseline layout (web app or IDE extension) to lock:
- Information hierarchy
- Rhythm/spacing structure
- Action zones (primary/secondary CTA placement)

Output requirement:
- Save baseline identifier and preview reference.

### Step 3 — Generate 3 Variants in Parallel

**Required:** Invoke `/gestalt-frontend-design` before generating variants. Each variant MUST apply Gestalt principles — they are not optional style preferences, they are perceptual correctness requirements. Specifically:

- Apply the **Spacing Decision Tree** from Gestalt Frontend Design to establish spacing tiers in each variant.
- Apply the **Container Decision Tree** to determine which content groups need visual boundaries.
- Consult the **Layout-Type Decision Matrix** for the specific layout being designed (form, dashboard, chat, settings, etc.).

Generate exactly 3 directional variants from the same framing:
- Direction A (e.g., dense/compact)
- Direction B (e.g., strategic/spacious)
- Direction C (e.g., tactical/hybrid)

Each variant must differ in density, emphasis distribution, or structural approach — not just color or decoration.

#### Evaluation Rubric

Score each variant 1-5 on these Gestalt-backed criteria:

| Criterion | What to Evaluate | Score 1 | Score 5 |
|-----------|-----------------|---------|---------|
| **Continuity** | Does the eye follow a clear path to the primary action? | Eye wanders; no reading path; misaligned elements | Unbroken top-to-bottom or left-to-right flow; primary action is the terminal point |
| **Figure-Ground** | Are primary elements clearly elevated above secondary? | Flat; no depth hierarchy; primary and secondary content compete | 2+ contrast tiers; primary content unmistakably prominent; overlays dim background |
| **CTA Salience** | Does the CTA stand out and group with its intent? | CTA blends with surrounding elements; ambiguous clickability | CTA is the strongest figure; visually grouped with its context via proximity |
| **Similarity** | Are same-function elements treated identically? | Mixed styling for same-role elements; inconsistent sizing/spacing | All buttons, badges, inputs of the same role share identical treatment |
| **Implementation Readiness** | Can this be built with standard components and spacing tokens? | Requires custom layout hacks; non-standard spacing; unclear component mapping | Maps directly to shadcn/ui components; uses Tailwind spacing scale; clear structure |

**Gate: Each variant must score 3+ on every criterion. If any variant scores below 3, fix it before proceeding to Step 4.**

### Step 4 — Choose One Direction

Select one variant as implementation reference.

Record decision with:
- Chosen variant ID
- Rejected variant IDs
- Reason for selection tied to use case (not aesthetic preference)
- Scores for all three variants

### Step 4.5 — Accessibility Gate

**Required before implementation.** Run the selected variant through the Gestalt Frontend Design **Accessibility Cross-Check**:

| Visual Cue Used | Required Semantic Equivalent |
|----------------|----------------------------|
| Proximity grouping | `<fieldset>`, `<section>`, `role="group"`, `aria-labelledby` |
| Color similarity | Redundant shape/icon/text cue (never color alone) |
| Figure-ground contrast | WCAG contrast ratios met (4.5:1 text, 3:1 UI components) |
| Common fate (motion) | `prefers-reduced-motion` respected |
| Continuity (visual flow) | DOM order matches visual order |
| Closure (implied content) | `aria-expanded` for collapsibles; explicit screen reader labels |

**Gate: If any row fails, fix the variant before proceeding to Step 5.**

### Step 5 — Implement

**Required:** Invoke `/gestalt-frontend-design` for implementation. Do not write production code without applying Gestalt patterns.

Specifically:
1. Use the **Gestalt reference patterns** (`references/reference.md`) for the specific layout type being built (form, dashboard, chat, agent UI, settings, cards, etc.).
2. Apply the **Post-Generation Quality Gate** (7-principle check) to the implemented code.
3. Apply **Dark Mode** guidance if the target supports dark mode.
4. Apply **Responsive Adaptations** if the target has multiple breakpoints.

Treat generated output as scaffold and apply manual micro-polish:
- Spacing (verify Tailwind spacing scale, no arbitrary values)
- Typography (verify hierarchy: heading > subheading > body > caption)
- Contrast (verify WCAG ratios in both light and dark modes)
- Minor alignment/interaction adjustments

### Step 6 — Track Decision History

Persist design trail for reversibility and learning:
- Project ID
- Baseline ID
- Variant IDs with scores
- Selected variant
- Decision rationale
- Accessibility gate results
- Follow-up implementation notes

Use `references/decision-log-template.md` as the standard format.

## Operating Rules
- Use AI generation for system-level exploration.
- Use manual edits for micro-level polish.
- Avoid open-ended iteration loops; enforce single-direction commitment after comparison.
- Prefer use-case fitness over aesthetic preference.
- **Always invoke `/gestalt-frontend-design`** for variant generation (Step 3) and implementation (Step 5). This is mandatory, not suggested.

## Skill Dependencies

| Skill | Required At | Purpose |
|-------|-----------|---------|
| `/gestalt-frontend-design` | Step 3 (variant generation) | Perceptual correctness for each variant |
| `/gestalt-frontend-design` | Step 4.5 (accessibility gate) | Accessibility cross-check |
| `/gestalt-frontend-design` | Step 5 (implementation) | Production code patterns, quality gate, dark mode, responsive |

## References
- `references/source-article.md` — Extracted source article and key excerpts.
- `references/decision-log-template.md` — Reusable template for variant decision tracking.
