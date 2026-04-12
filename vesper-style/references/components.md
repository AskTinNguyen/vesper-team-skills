# Vesper Style — Components

Use this file for **component-level decisions** once the layout and hierarchy are clear.

The goal is not to invent decorative variants. The goal is to make common Vesper primitives feel **calm, tactile, readable, and consistent**.

## 1. Panel headers

Vesper headers are compact orientation tools.

### Good header anatomy
- concise title
- optional leading visual
- optional small badge/state marker
- a small set of right-side actions

### Rules
- title stays primary
- action count stays low
- metadata should not crowd the title line
- dropdown affordances should be clear but quiet

### Avoid
- multi-row toolbars in the header by default
- equal emphasis between title and utility actions
- decorative hero treatments in routine panels

## 2. Buttons and action hierarchy

Buttons in Vesper should make priority obvious.

### Button roles
- **Primary** — the one strongest action
- **Secondary / outline** — supporting actions
- **Ghost** — utility or low-priority actions in dense surfaces
- **Destructive** — reserved for dangerous actions only

### Rules
- do not use multiple semantic colors just to make controls look varied
- one primary action per zone is usually enough
- destructive styling should be rare and meaningful
- icon-only buttons still need obvious affordance and accessible labels

## 3. Chips, badges, and labels

Vesper uses many chips, so discipline matters.

### Rules
- keep chip text **neutral and readable**
- use semantic hue in background tint and border first
- keep chips short and scannable
- pair color with text or icon when meaning matters

### Good chip recipe
- background tint: soft semantic wash
- border: stronger semantic tint
- text: `text-foreground`

### Avoid
- same-hue text on same-hue surfaces
- tiny unreadable pills
- rainbow badge sets unless meaning truly requires it

## 4. Panels and cards

Panels should feel like **solid working surfaces**, not demo cards.

### Rules
- prefer quiet surfaces with clear borders or subtle separation
- let the content establish the hierarchy rather than decorative chrome
- use spacing to group content before adding more boxes inside boxes
- in light mode, make the surface solid enough to read cleanly

### Good use cases
- settings sections
- detail surfaces
- assistant output containers
- artifact/work surfaces

## 5. Inputs and textareas

Forms should feel calm and trustworthy.

### Rules
- labels must be readable and close to the field
- focus rings must be visible without being harsh
- helper text should clarify, not narrate at length
- error states should be specific and easy to spot

### Good posture
- short label
- short helper text only when uncertainty is likely
- grouped fields with clear section titles
- semantic color reserved for validation and state, not decoration

## 6. Dropdowns and menus

Menus are where advanced actions often live.

### Rules
- treat menus as solid decision surfaces
- keep spacing compact but not cramped
- destructive items should be visually distinct, not loud by default
- group related actions with separators only when they help scanning

### Avoid
- turning the main header into a menu cemetery
- putting primary actions behind menus unless there is a strong reason

## 7. Lists, rows, and tables

Rows should reward scanning.

### Rules
- make the row’s main label obvious
- demote timestamps, metadata, and secondary controls
- preserve clear hover/selected states
- use alignment and spacing to communicate structure before adding more ornament

### For tables
- prioritize readable headers
- keep numeric vs textual content visually distinct when useful
- avoid zebra-striping if spacing and hierarchy already solve the scan problem

## 8. Tabs, filters, and segmented controls

These should reduce clutter, not add it.

### Rules
- use them to reveal structure or mode, not as decoration
- active state should be unmistakable
- keep option counts small when possible
- avoid long horizontal strings of equally styled controls

## 9. Companion surfaces and context strips

A companion surface should support the work, not rival it.

### Good for
- current context
- related metadata
- supporting actions
- lightweight summaries

### Rules
- keep the companion quieter than the primary surface
- summarize instead of duplicating the main area
- avoid overly dense badge clusters

## 10. Callouts, alerts, and feedback banners

Vesper feedback surfaces should feel stable and readable.

### Rules
- use semantic tint for background/border
- keep copy neutral/high-contrast
- reserve strong red or loud warning treatment for real risk
- short explanatory text beats dramatic visuals

### Avoid
- hue-matched small text on tinted banners
- using banner color as the only signal
- introducing one-off alert recipes when a shared badge/callout formula would work

## 11. Empty states

Empty states are part of the product experience.

### Include
- clear purpose statement
- one strong CTA
- optional short supporting sentence

### Avoid
- multiple competing CTAs
- long onboarding essays
- cute illustration styles that clash with Vesper’s premium restraint

## 12. Motion and states

Components should feel tactile.

### Good component-state behavior
- hover acknowledges possibility
- press confirms intent
- focus is visible and keyboard-usable
- loading/progress is explicit
- success/error states are calm but unmistakable

### Avoid
- theatrical micro-interactions
- springy motion on routine controls
- ambiguous disabled states that look broken rather than intentionally unavailable

## 13. Component anti-patterns

Reject these quickly:
- chip text relying on semantic hue for readability
- fields with barely visible borders in light mode
- too many filled buttons competing in one region
- headers that act like control bars
- panels whose chrome is louder than their content
- component-specific color hacks that should be handled in shared primitives

## 14. Final component check

Before shipping, ask:
1. Does the component make the next action clearer?
2. Is small text still readable in both themes?
3. Does the component feel tactile without being noisy?
4. Is the visual weight proportional to the component’s importance?
5. Should this behavior/style live in a shared primitive instead of a one-off?
