# Vesper Style — Implementation Mapping

Use this file when the design decision needs to turn into **real Vesper code changes**.

This is the bridge between the style rules and the actual repo.

## 1. First principle

When a problem repeats across multiple screens, **fix the shared system first**.

Do **not** immediately patch every leaf component if the real issue is:
- token contrast
- shared badge styling
- shared button/input states
- shared panel/header chrome
- theme-surface opacity behavior

## 2. Where to look first

### Global style and semantic tokens
**Use when:** the problem is global warmth, contrast, semantic color behavior, muted text, borders, focus rings, or light/dark parity.

Primary files:
- `packages/ui/src/styles/index.css`
- `docs/developer/theming-architecture.md`
- `specs/vesper-global-design-spec.md`
- `apps/electron/resources/themes/*.json`

Typical decisions here:
- background / foreground balance
- semantic token values
- `*-text` readability behavior
- border and input visibility
- theme-wide light/dark contrast tuning

### Theme-override or renderer-surface bleed
**Use when:** a page looks washed out before its own component styles are even applied.

Primary files:
- `apps/electron/src/renderer/index.css`
- related theme override rules in renderer CSS

Typical decisions here:
- opaque base surfaces in light mode
- scenic vs solid mode behavior
- backdrop and wallpaper bleed

### Shared headers and panel chrome
**Use when:** titles, compact headers, panel actions, or title dropdown behavior feel off across surfaces.

Primary files:
- `apps/electron/src/renderer/components/app-shell/PanelHeader.tsx`
- `packages/ui/src/components/ui/PreviewHeader.tsx`

Typical decisions here:
- compact header rhythm
- title/action balance
- badge placement
- hover/focus behavior in shared header controls

### Shared chips, labels, and tinted micro-surfaces
**Use when:** badges, chips, label pills, highlight pills, or tiny counters are hard to read or stylistically inconsistent.

Primary files:
- `apps/electron/src/renderer/components/ui/label-badge.tsx`
- any shared badge helper / utility used by the affected area
- contrast solution docs in `docs/solutions/ui-bugs/*contrast*.md`

Typical decisions here:
- neutral foreground text on tinted chips
- stronger border tint
- tiny-size readability
- semantic consistency between product areas

### Shared buttons, fields, textareas, and menus
**Use when:** controls feel too faint, too loud, or inconsistent across screens.

Primary files:
- `apps/electron/src/renderer/components/ui/button.tsx`
- `apps/electron/src/renderer/components/ui/input.tsx`
- `apps/electron/src/renderer/components/ui/textarea.tsx`
- `apps/electron/src/renderer/components/ui/styled-dropdown.tsx`

Typical decisions here:
- primary vs secondary action contrast
- border visibility in light mode
- focus/hover treatment
- menu density and destructive-item behavior

### Shared document/artifact work surfaces
**Use when:** the main editing/reading surface, companion rail, or context strip needs calmer structure and stronger document feel.

Primary files:
- `packages/ui/src/components/ui/ArtifactAdaptiveShell.tsx`
- `packages/ui/src/components/ui/ArtifactContextStrip.tsx`
- `packages/ui/src/components/ui/ArtifactCompanionRail.tsx`
- `packages/ui/src/components/ui/OperationPanel.tsx`

Typical decisions here:
- primary work surface hierarchy
- companion-rail restraint
- section spacing
- readable document-centric structure

## 3. Decision table

| Problem | Start here | Why |
|---|---|---|
| Light mode feels washed out | `packages/ui/src/styles/index.css`, `apps/electron/src/renderer/index.css` | Often a token or base-surface problem, not a leaf component problem |
| Chips/badges are pretty but unreadable | `label-badge.tsx`, shared contrast recipes | Tiny semantics should be standardized once |
| Header feels crowded or weak | `PanelHeader.tsx` | Many surfaces inherit the same chrome language |
| Buttons/inputs feel inconsistent | shared `button.tsx` / `input.tsx` / `textarea.tsx` | Shared primitives should carry the posture |
| Popovers/menus feel too flimsy or noisy | `styled-dropdown.tsx` + token layer | Menus should read as solid decision surfaces |
| Work surface feels like generic cards | artifact/work-surface primitives + tokens | Vesper’s main surfaces should feel document-centric |
| One screen only has a local spacing/content problem | leaf component | Use local edits only after ruling out shared-system causes |

## 4. Implementation recipes

### A. Contrast-safe semantic chip
Use this shape first:

```tsx
className="border-info/40 bg-info/15 text-foreground"
```

Rules:
- tint in border/background
- neutral text
- add icon/text if the meaning matters
- do not use `text-info` on `bg-info/15` for tiny text

### B. Calm primary action
Primary buttons should feel decisive without turning the page into a color parade.

Good posture:
- one primary button in a region
- outline/ghost for secondary actions
- destructive reserved for actual risk

### C. Light-mode-safe surface
For a surface that must stay legible on pale backgrounds:
- use `bg-background`
- add a visible `border-border` or equivalent structural edge
- avoid stacking multiple translucent fills
- use `text-foreground` / `text-muted-foreground`, not repeated opacity dimming

### D. Document-centric section
When a surface should feel more like a workbench than a dashboard:
- strengthen the main reading/editing column
- demote metadata into smaller support regions
- increase vertical grouping rhythm before adding more sub-cards
- keep the header quiet and the body readable

## 5. Reusable repo lessons

These lessons are already encoded in shipped Vesper fixes:
- **Light mode needs explicit opacity discipline.** Make base surfaces opaque before adding more styling.
- **Small semantic text should stay neutral.** Hue belongs in the surface and border first.
- **Do not stack extra opacity on already-muted text.**
- **If a pattern repeats, move the fix up into tokens or shared primitives.**

Relevant examples:
- `docs/solutions/ui-bugs/mission-control-light-theme-contrast-20260307.md`
- `docs/solutions/ui-bugs/viewer-settings-feedback-banner-contrast-20260307.md`
- `docs/solutions/ui-bugs/vector-search-highlight-contrast-20260305.md`
- `docs/solutions/ui-bugs/reentry-brief-badge-light-theme-contrast-20260321.md`

## 6. Verification checklist after code changes

After implementing a Vesper-style change, verify:

### Contrast and readability
- light mode first if the component uses chips, tint, borders, or muted text
- dark mode still feels calm and readable
- tiny badges and helper text remain legible

### Hierarchy and disclosure
- one action is clearly primary
- advanced controls are not dominating the default view
- metadata is present but visually subordinate

### Interaction quality
- hover, press, and focus states are visible
- loading and error states are clear
- motion is subtle and purposeful

### Scope correctness
- repeated issues were fixed in shared primitives/tokens where appropriate
- no broad visual drift away from Vesper’s warm editorial system

## 7. Final question before merging

Ask:

> Is this a **real Vesper system fix**, or did we only make one screen look better in isolation?

If the issue is systemic and the patch is local-only, the job is not fully done.
