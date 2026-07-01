# Reference-Harvesting Patterns

## 1. Start with the UI Shape
Before looking at any example, label the request as one of these:
- **Form / settings**
- **Dashboard / data surface**
- **Chat / AI / messaging**
- **Auth / onboarding**
- **Commerce / pricing / checkout**
- **Content / profile / directory**
- **Task / planning / workflow**
- **Media / gallery / discovery**

This prevents random browsing and keeps the reference search intentional.

## 2. Use 2-3 Examples, Not 1
The best output usually comes from combining:
- **one structural reference**
- **one interaction reference**
- **one visual-density reference**

Example:
- take page structure from `settings-page`
- form density from `add-product-form`
- supporting list/toggle treatment from `roles-permissions` or `notifications`

That produces stronger UI than copying any single source file.

## 3. Extract These Layers Separately
When reading an example, pull out only what is reusable.

### A. Layout skeleton
- page split
- sidebar vs stacked layout
- card grouping
- section ordering
- header/action placement

### B. Primitive stack
- which UI primitives create the pattern
- where cards are necessary vs where spacing alone is enough
- how buttons, badges, tabs, inputs, or tables are combined

### C. Interaction model
- inline editing vs modal editing
- persistent side navigation vs local tabs
- toggle, radio, or select choice patterns
- preview, detail, or drill-down behavior

### D. Density and rhythm
- compact vs spacious
- number of controls per region
- where separators or container boundaries appear
- how much text supports each action

## 4. Upgrade Passes for Beauty
After extracting the reference pattern, improve it on purpose.

### Upgrade hierarchy
- make the primary action clearer
- remove equal-weight actions
- increase contrast between headings, body, and metadata

### Upgrade spacing
- enforce consistent within-group and between-group spacing
- remove random density shifts
- let major sections breathe more than the original demo does

### Upgrade copy
- replace demo-grade labels with product-specific language
- reduce filler descriptions
- make CTA labels specific and verb-first

### Upgrade states
- add loading, empty, error, and success states where the example is silent
- fix hover/focus/disabled states if the source is thin

### Upgrade responsiveness
- convert desktop-heavy demo layouts into clear mobile behavior
- simplify columns before shrinking everything

## 5. Reference-to-Output Workflow
Use this sequence:

1. **Classify** the requested UI type.
2. **Select** 2-3 examples from `example-map.md`.
3. **Extract** structure, primitives, and interactions.
4. **Discard** source-specific copy and decorative choices.
5. **Recompose** the target UI around the product's actual goal.
6. **Polish** using Gestalt grouping, stronger hierarchy, and production states.

## 6. Worked Example
### Request
"Create a beautiful account settings page for an AI workspace product."

### Good references
- `settings-page` — overall page structure and section switching
- `add-product-form` — form grouping, right-rail support content, and dense card sections
- `notifications` — settings control patterns and preference rows

### Borrow
- left-nav + main-content split from `settings-page`
- grouped form cards from `add-product-form`
- preference-row interaction treatment from `notifications`

### Upgrade
- reduce demo noise and arbitrary icon treatments
- use warmer typography and calmer contrast
- improve section headers, descriptions, and save flows
- add clearer success feedback and mobile collapse behavior

### Expected output
A settings page that feels editorial and premium, while still clearly rooted in familiar shadcn-style primitives.

## 7. Decision Rule
If a source example gives you:
- the **right structure** but weak polish → keep structure, redesign visuals
- the **right primitives** but wrong page shape → keep components, change composition
- the **right interaction** but wrong density → keep interaction, rebuild spacing and grouping

Never inherit all three blindly.
