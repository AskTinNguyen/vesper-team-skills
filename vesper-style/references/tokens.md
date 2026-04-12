# Vesper Style — Tokens

Source of truth for the default Vesper token system:
- `packages/ui/src/styles/index.css`
- `docs/developer/theming-architecture.md`
- `specs/vesper-global-design-spec.md`

Use this file when making color, typography, spacing, surface, or motion decisions for Vesper UI.

## 1. Atmosphere

Vesper’s default mood is **golden hour to twilight**.

- **Light mode** should feel like warm parchment, cream, or editorial paper.
- **Dark mode** should feel like focused twilight: elegant, calm, and readable for long sessions.
- The product should feel **layered and tactile**, not glossy, neon, or washed out.

## 2. Core semantic palette

Vesper’s shared system is built around a small semantic set.

### Light mode (`:root`)

| Token | Value | Role |
|---|---|---|
| `--background` | `oklch(0.93 0.02 60)` | Warm parchment base |
| `--foreground` | `oklch(0.20 0.05 50)` | Primary text, icons, outlines |
| `--accent` | `oklch(0.68 0.16 55)` | Brand emphasis, primary highlight |
| `--info` | `oklch(0.75 0.16 70)` | Ask/warning-style attention |
| `--success` | `oklch(0.55 0.17 145)` | Positive/connected state |
| `--destructive` | `oklch(0.58 0.24 28)` | Errors and dangerous actions |
| `--warning` | `oklch(0.70 0.18 50)` | Secondary caution / Ralph-style mode |

### Dark mode (`.dark`)

| Token | Value | Role |
|---|---|---|
| `--background` | `oklch(0.18 0.02 300)` | Deep twilight background |
| `--foreground` | `oklch(0.92 0.01 55)` | Warm light text |
| `--accent` | `oklch(0.65 0.18 300)` | Twilight purple emphasis |
| `--info` | `oklch(0.70 0.16 70)` | Warm alert/info |
| `--success` | `oklch(0.60 0.17 145)` | Positive state |
| `--destructive` | `oklch(0.70 0.19 22)` | Error state |
| `--warning` | `oklch(0.75 0.18 50)` | Secondary caution |

## 3. Text and tint rules

Vesper separates **semantic color** from **readable foreground color**.

### Use `*-text` variants for standalone semantic text
When semantic color appears as text on a mostly neutral background, prefer:
- `--accent-text`
- `--success-text`
- `--info-text`
- `--warning-text`
- `--destructive-text`

These are mixed toward `--foreground` for readability.

### Do not use hue-matched tiny text on tinted chips
For chips, badges, and tiny metadata pills:
- keep text **neutral/high-contrast** (`text-foreground`)
- put hue in the **background tint** and **border**
- never rely on hue alone for meaning

### Safe chip recipe

```tsx
className="border-success/40 bg-success/15 text-foreground"
```

Or, for custom label colors, follow the `LabelBadge` strategy:

```ts
const bg = `color-mix(in oklab, ${label.color} 18%, var(--background))`
const border = `color-mix(in oklab, ${label.color} 48%, var(--background))`
```

## 4. Surface tokens and layering

Key derived tokens already exist:
- `--card`
- `--popover`
- `--muted`
- `--border`
- `--input`
- `--ring`
- `--muted-foreground`

### Surface guidance
- In **light mode**, default to **opaque or near-opaque surfaces**.
- Use explicit borders when separation would otherwise feel too soft.
- Let elevated panels feel like paper on a desk, not floating glass.
- Scenic/glass surfaces are optional; solid surfaces are the default baseline.

### Avoid
- `bg-muted/50` as a main reading surface
- multiple translucent layers stacked in light mode
- further dimming already-muted text with `/50` or `/70` opacity utilities

## 5. Typography

### Shared font posture
From the shared UI stylesheet:
- **Sans UI**: system stack by default
- **Mono / code**: `JetBrains Mono`
- Optional: Inter can be enabled explicitly for UI

### Hierarchy rules
Vesper typography should feel **editorial and calm**, not loud.

Use a simple four-tier model:
1. **Overline / eyebrow** — small context or section label
2. **Heading** — concise, strong, readable title
3. **Body** — main instructions, content, controls
4. **Meta** — timestamps, status, helper text

### Usage rules
- Prefer **sentence case** for UI labels.
- Reserve **monospace** for code, paths, IDs, structured state, and terminal-like data.
- Keep metadata readable; muted does not mean faint.
- Do not create hierarchy only through color. Size, weight, spacing, and placement should do most of the work.

## 6. Density and spacing

The app should feel **information-rich but breathable**.

Recommended spacing rhythm:
- **4px** — micro alignment only
- **8px** — tightly related items
- **12–16px** — common inline/control grouping
- **24px** — subgroup separation
- **32px** — section separation inside a panel
- **40–48px** — page-level or major context break

### Header density
Many Vesper panels use compact headers around **40px** tall. The goal is quiet orientation, not hero-banner chrome.

## 7. Shape and radius

Vesper is **small-radius to squared-off**, not playful or bubbly.

Prefer:
- crisp corners
- restrained rounding
- shape used to clarify affordance, not to decorate every surface

Avoid:
- oversized pill buttons everywhere
- soft consumer-app rounding on dense work surfaces

## 8. Motion and tactile feedback

Motion should confirm interaction, not perform personality.

Recommended range:
- **150–250ms** for micro-transitions
- slightly longer only when helping the eye follow a structural change

Prioritize:
- crisp hover feedback
- clear press acknowledgment
- visible focus rings
- short, quiet transitions

Avoid:
- springy/bouncy motion
- dramatic page theatrics
- decorative shimmer or float without informational value

## 9. Tailwind-friendly guidance

Common shared classes/tokens that usually belong in Vesper surfaces:
- `bg-background text-foreground`
- `border-border`
- `bg-muted text-muted-foreground`
- `border-input bg-background`
- `focus-visible:ring-ring`
- `text-accent-text`, `text-success-text`, `text-destructive-text` for standalone semantic text

### Good defaults
- primary text: `text-foreground`
- secondary/meta text: `text-muted-foreground`
- primary container: `bg-background border-border`
- tinted semantic callout/chip: `bg-*/15 border-*/40 text-foreground`

## 10. Token-level anti-patterns

Reject these quickly:
- same-hue text on same-hue semantic backgrounds
- light-mode alpha stacking that makes the screen feel washed out
- muted text that is muted **again** with opacity
- using accent color on every clickable element equally
- inventing one-off hex colors before checking the semantic system

## 11. Final token check

Before shipping, ask:
1. Does light mode still feel rich and readable?
2. Are chips and badges readable at tiny sizes?
3. Is semantic color guiding meaning instead of decorating everything?
4. Should this be fixed in a shared token or primitive instead of a leaf component?
