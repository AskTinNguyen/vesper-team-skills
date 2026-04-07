# Pipeline

Use this order unless there is a strong reason to skip a stage.

## 1. Frame the UI
Write exactly:

```text
Audience: <target user>
Primary action: <single core action>
Mandatory sections: <section 1>, <section 2>, <section 3>
```

If these are fuzzy, stop and clarify them first.

## 2. Harvest References
Invoke:
- `shadcn-component-reference-davinci`

Goal:
- choose 2-3 strong source examples
- extract structure, interaction model, primitive combinations, and density cues
- avoid literal cloning

Deliverable:
```text
Reference examples:
Borrow from each:
Avoid from each:
```

## 3. Translate to Vesper
Invoke:
- `vesper-premium-ui-remix-davinci`

Goal:
- reinterpret the borrowed pattern through Vesper's visual language
- strengthen hierarchy, warmth, tactility, and progressive disclosure
- remove demo-grade styling and AI/SaaS clichés

Deliverable:
```text
Vesper upgrades:
- hierarchy changes
- surface changes
- copy changes
- interaction changes
- color/contrast changes
```

## 4. Implement with Strong UI Discipline
Invoke:
- `gestalt-frontend-design`
- `ui-design-brain`

Goal:
- choose the right production patterns
- implement with clear grouping, spacing, containers, and responsiveness
- preserve the chosen direction without drifting back toward the raw references

Deliverable:
```text
Implementation approach:
- layout type
- component pattern choices
- spacing/container decisions
- responsive behavior
- accessibility checks
```

## 5. Polish to Ship Quality
Invoke:
- `polish`

Optional, when needed:
- `clarify`
- `harden`
- `animate`
- `adapt`
- `optimize`

Rule: do not use these optional skills as substitutes for Step 2. If the UI still feels like a borrowed example, return to the Vesper translation step before polishing details.

Goal:
- remove rough edges
- fix states, spacing, contrast, copy, and interaction gaps
- ensure the final UI feels premium rather than merely functional

Deliverable:
```text
Polish checks:
- hierarchy
- states
- copy
- contrast
- responsiveness
- motion restraint
```

## 6. Final Review Question
Before considering the work done, ask:

> Does this feel like Vesper expressing a useful reference idea, or does it still feel like a dressed-up example clone?

If it still feels borrowed, go back to Step 3, not Step 5.
