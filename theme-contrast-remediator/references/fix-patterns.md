# Fix Pattern Catalog

Reference patterns for common contrast remediation scenarios.

## Pattern A: Low-Contrast Chip

Same-hue text on same-hue tinted background produces poor contrast, especially at small sizes (10-11px).

**Correct** (neutral text + tinted bg + stronger tinted border):

```tsx
className="... border border-purple-500/45 bg-purple-500/20 text-foreground ..."
```

**Avoid** (purple text on purple-tinted background yields ~2.1:1 contrast in Light mode):

```tsx
className="... bg-purple-500/20 text-purple-700 ..."
```

For the full chip formula (opacity ranges, dynamic labels), see `references/chip-contrast-playbook.md`.

## Pattern B: Global Light Opacity Bleed

When `data-theme-override` is active, the backdrop `::before` pseudo-element can bleed through and wash out Light mode surfaces.

In `apps/electron/src/renderer/index.css`, use opaque Light base layer:

```css
/* Light mode: keep base layer opaque */
html[data-theme-override]::before { background: var(--background); }

/* Dark mode: allow slight transparency for wallpaper effect */
html.dark[data-theme-override]::before { background: color-mix(in srgb, var(--background) 82%, transparent); }
```

## Pattern C: Shared Inputs Too Faint

Input fields, textareas, and buttons with weak borders become invisible on pale surfaces.

Apply semantic border/input/ring tokens in shared primitives (`button.tsx`, `input.tsx`, `textarea.tsx`):

```tsx
className="border-input bg-background placeholder:text-muted-foreground/80 focus-visible:border-ring focus-visible:ring-ring/40"
```
