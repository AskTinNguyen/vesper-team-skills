# Chip Contrast Recipes

Reference formulas for colorful-but-illegible badges, labels, and metadata chips.

## Default Chip Formula

1. `text`: neutral (`var(--foreground)` or `text-foreground`)
2. `background`: semantic hue at 14-22% opacity (e.g., `bg-sky-500/18`)
3. `border`: same hue at 35-50% opacity (e.g., `border-sky-500/45`)

Example:

```tsx
className="border border-sky-500/45 bg-sky-500/18 text-foreground"
```

## Dynamic Label Formula

```tsx
const chipStyles: React.CSSProperties = {
  backgroundColor: `color-mix(in oklab, ${label.color} 18%, var(--background))`,
  borderColor: `color-mix(in oklab, ${label.color} 48%, var(--background))`,
  color: 'var(--foreground)',
}
```

Fallback when `color-mix` is unsupported (Chromium < 111):

```tsx
function getContrastTextColor(bgHex: string): string {
  const r = parseInt(bgHex.slice(1, 3), 16);
  const g = parseInt(bgHex.slice(3, 5), 16);
  const b = parseInt(bgHex.slice(5, 7), 16);
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  return luminance > 0.5 ? '#000000' : '#ffffff';
}

const chipStyles: React.CSSProperties = {
  backgroundColor: label.color,
  color: getContrastTextColor(label.color),
  borderColor: 'transparent',
};
```

## Anti-Patterns

- `bg-color/20` + `text-same-color-700` for tiny text (same-hue, low separation).
- Multiple nested translucent containers in Light mode (opacity compounds: 80% inside 80% = ~64%).
- Placeholder/helper text with opacity below 70-80% of foreground color (e.g., `text-muted-foreground/60`).
- Inconsistent chip recipes across sibling components.

## Validation Checklist

- Grep for remaining same-hue text/bg pairs: `rg -n "text-(sky|purple|green|red|amber)-" apps/electron/src/renderer/components`
- Confirm all chip classes include `text-foreground` (not a hue-specific text color).
- Verify both `:root` and `.dark` CSS rules exist for any modified token.
- Check hover/focus/selected state classes maintain contrast.
- Alert chips (`Needs You`, warning badges) use higher opacity borders (>= 60%) than standard chips.
