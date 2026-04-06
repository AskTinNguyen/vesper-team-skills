# What to Borrow vs What to Avoid

## Borrow
These are the parts of shadcn-examples worth reusing.

| Borrow | Why |
|---|---|
| **Page skeletons** | Good for quickly finding workable structure |
| **Section ordering** | Helps with scan flow and composition |
| **Primitive combinations** | Shows how cards, inputs, badges, tables, and nav elements can work together |
| **Interaction models** | Useful for tabs, sidebars, toggles, drill-downs, and grouped actions |
| **Density references** | Helps choose compact vs spacious treatment for the target UI |

## Upgrade
These parts usually need improvement before shipping.

| Upgrade | Why |
|---|---|
| **Typography hierarchy** | Demo examples are often functional, not especially elegant |
| **Copy and labels** | Product-grade microcopy should replace generic demo language |
| **Color and contrast** | Some examples rely on thin demo styling or weak semantic color choices |
| **Responsive behavior** | Recheck mobile and tablet behavior instead of inheriting it blindly |
| **States** | Add stronger loading, empty, success, and error handling |
| **Spacing rhythm** | Normalize uneven density and improve grouping clarity |

## Avoid
Do not transfer these blindly.

| Avoid | Why |
|---|---|
| **Literal visual cloning** | Makes the output feel derivative and demo-grade |
| **Placeholder copy and fake product language** | Weakens trust and clarity |
| **Arbitrary colored badges or icons** | Often reads as unrefined or inconsistent |
| **Hard-coded demo data assumptions** | Leaks fake structure into real product UI |
| **Weak demo polish** | The source repo is useful, but not the quality ceiling |

## Important Caveat
Some folders in the source repo are stronger than others. Treat every example as **reference material to inspect**, not as proof that the current implementation is complete or production-ready.

## Davinci Standard
A Davinci result should preserve the **clarity and utility** of the source pattern while improving:
- visual hierarchy
- elegance of spacing
- strength of copy
- accessibility and states
- overall product fit

If the final result looks like “shadcn-examples, but pasted into another app,” the skill was used incorrectly.
