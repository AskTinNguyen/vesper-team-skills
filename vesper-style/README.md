# Vesper Style Skill Pack

A reusable design-system skill pack for **Vesper** and **Claude-style skill runtimes**.

This pack turns Vesper’s design language into a portable skill: not just a mood board, but a **working UI brain** for designing, critiquing, and implementing Vesper surfaces with the right hierarchy, contrast, layout discipline, and component choices.

It is grounded in Vesper’s actual repo context:
- the product and brand guidance in `CLAUDE.md`
- the canonical system rules in `specs/vesper-global-design-spec.md`
- the shared theme tokens in `packages/ui/src/styles/index.css`
- contrast-safe renderer patterns already shipped in the app

## What you get

Tell the agent to use **`vesper-style`** when the task is about making a surface feel like Vesper.

The pack provides:
- a **canonical Vesper UI design skill**
- a **token reference** for color, typography, spacing, and motion
- **layout patterns** for Vesper’s document-centric, agent-native workflows
- **component guidance** for chips, headers, panels, forms, menus, and work surfaces
- an **implementation mapping** that points designers and coders to the right files and primitives

## What this skill is for

Use this pack when you need to:
- design a new Vesper panel, page, or workflow
- make a generic UI feel like Vesper
- fix weak hierarchy, clutter, or control overload
- correct light-mode contrast problems
- choose the right Vesper layout and component patterns before implementation
- preserve a human-led, calm, premium experience while exposing advanced AI capability

This pack is **not** a generic aesthetic preset for unrelated brands.

## Install

Copy the `vesper-style` folder into your skills directory.

```sh
cp -r generated-skills/vesper-style-skill-pack/vesper-style ~/.claude/skills/
# or
cp -r generated-skills/vesper-style-skill-pack/vesper-style ~/.vesper/skills/
```

Or symlink it into the Vesper skills location used by your local setup.

## Recommended usage

Prompt examples:
- `Use vesper-style to redesign this settings page.`
- `Make this shadcn layout feel like Vesper.`
- `Review this panel for Vesper hierarchy, contrast, and progressive disclosure.`
- `Apply vesper-style before implementing this workflow.`

## What’s inside

| File | Purpose |
|---|---|
| `vesper-style/SKILL.md` | Main Vesper design brain and workflow |
| `vesper-style/icon.svg` | Skill icon |
| `vesper-style/references/brand-foundation.md` | Product and brand baseline for Vesper |
| `vesper-style/references/tokens.md` | Shared color, type, spacing, surface, and motion rules |
| `vesper-style/references/layout-patterns.md` | Canonical Vesper layout and information-architecture patterns |
| `vesper-style/references/components.md` | Component-level guidance for common Vesper UI building blocks |
| `vesper-style/references/copy-and-tone.md` | Voice, microcopy, and UX writing guidance for Vesper surfaces |
| `vesper-style/references/anti-patterns.md` | Hard rejects that pull Vesper toward generic AI SaaS or weak usability |
| `vesper-style/references/review-checklist.md` | Fast review rubric for hierarchy, contrast, disclosure, motion, and polish |
| `vesper-style/references/implementation-mapping.md` | Repo-grounded mapping from design problems to actual Vesper primitives/files |
| `THIRD_PARTY_NOTICES.md` | Lineage and attribution notes for the pack structure inspiration |

## Lineage

This pack was inspired by the structure and packaging approach of the MIT-licensed [`nothing-design-skill`](https://github.com/dominikmartn/nothing-design-skill) repository.

The Vesper Style pack content is newly authored for Vesper and grounded in Vesper's own repo, brand guidance, theme system, and shipped UI patterns. See `THIRD_PARTY_NOTICES.md` for attribution details.

## Mental model

Vesper should feel like:
- **warm editorial clarity**, not generic SaaS chrome
- **tactile responsiveness**, not theatrical animation
- **agentic depth with human control**, not operator-dashboard overload
- **premium restraint**, not sci-fi AI spectacle

If a design looks “cool” but makes the user feel less oriented, less capable, or less in control, it is not Vesper enough.
