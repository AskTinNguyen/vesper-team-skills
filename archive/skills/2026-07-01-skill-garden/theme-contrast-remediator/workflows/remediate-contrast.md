# Remediate Contrast Workflow

Step-by-step procedure for fixing Light/Dark theme contrast issues.

<required_reading>
- `references/chip-contrast-playbook.md` — chip formula and dynamic label recipe
- `references/fix-patterns.md` — catalog of fix patterns A/B/C
</required_reading>

## Step 1: Define the Failure

Write a one-sentence summary of the readability failure.

Example: "Persona chips in the session list use purple-on-purple text in Light mode, failing WCAG AA at 10px."

## Step 2: Audit Theme Token Sources

Check these locations for token definitions and overrides:

1. `apps/electron/src/renderer/index.css` — `@theme inline` block, `:root`/`.dark` CSS custom properties (`--background`, `--foreground`, `--muted`, `--border`, `--input`, `--ring`)
2. ThemeProvider in `apps/electron/src/renderer/contexts/` — runtime overrides
3. Component-level token remapping (any component redefining CSS vars locally)

Key tokens:

| Token | Purpose |
|-------|---------|
| `--background` / `--foreground` | Base page bg and default text |
| `--muted` / `--muted-foreground` | Subdued surfaces and their text |
| `--border` / `--input` / `--ring` | Border, input border, focus ring |
| `data-theme-override` | Activates wallpaper/scenic backdrop on `<html>` |
| `data-scenic` | Enables glass/translucent mode on `<html>` |

## Step 3: Locate Opacity/Contrast Hotspots

Run these search commands to find problematic patterns:

```bash
# Find all opacity-modified color utilities
rg -n "bg-.*\\/|text-.*\\/|border-.*\\/" apps/electron/src/renderer/components

# Find muted-foreground opacity usage
rg -n "text-muted-foreground/|placeholder:text-muted-foreground/" apps/electron/src/renderer/components

# Find theme token definitions and overrides
rg -n "data-theme-override|data-scenic|--muted|--border|--input|--ring" apps/electron/src/renderer/index.css apps/electron/src/renderer/context
```

## Step 4: Patch Global Semantic Tokens

Fix token values in `apps/electron/src/renderer/index.css` first:
- `--muted`, `--border`, `--input`, `--ring` — strengthen if too faint
- Backdrop handling — make Light mode base opaque (see Pattern B in `references/fix-patterns.md`)

Before changing any token, audit all consumers:
```bash
rg -n "var(--muted)" apps/electron/src/renderer/
```

## Step 5: Patch Shared Primitives

Update shared UI components to use semantic contrast-safe classes:
- `apps/electron/src/renderer/components/ui/button.tsx`
- `apps/electron/src/renderer/components/ui/input.tsx`
- `apps/electron/src/renderer/components/ui/textarea.tsx`
- `apps/electron/src/renderer/components/ui/label-badge.tsx`

Apply Pattern C from `references/fix-patterns.md` for inputs.

## Step 6: Patch High-Impact Surfaces

Fix remaining component-level issues:
- Session list rows (`apps/electron/src/renderer/components/app-shell/SessionList.tsx`)
- Metadata chips (persona, source, topic, alert labels)
- Popovers and search fields (`apps/electron/src/renderer/components/app-shell/input/FreeFormInput.tsx`)

Apply chip formula from `references/chip-contrast-playbook.md`.

## Step 7: Validate

### Lint and Type Check
```bash
bun run lint:electron
bun run typecheck:all
```

### Contrast Verification
- Grep for remaining same-hue text/bg pairs:
  ```bash
  rg -n "text-(sky|purple|green|red|amber)-" apps/electron/src/renderer/components
  ```
- Confirm all chip classes include `text-foreground` (not a hue-specific text color).
- Verify both `:root` and `.dark` CSS rules exist for any modified token.
- Check hover/focus/selected state classes maintain contrast.

### Accessibility Gate
- Normal text: >= 4.5:1 contrast ratio (WCAG AA).
- Chip text at 10-11px: must meet 4.5:1 minimum.
- Color is never the only signal; preserve icon/text semantics.
- Focus outlines visible against both theme backgrounds.

## Step 8: Document

Create `docs/solutions/ui-bugs/{slug}-{YYYYMMDD}.md` with:
- Problem description and symptoms
- Root cause analysis
- What didn't work (failed approaches)
- Solution with code snippets
- Prevention guardrails
- List of files modified

## Troubleshooting

### `color-mix()` not rendering
- Check Electron Chromium version. `color-mix(in oklab, ...)` requires Chromium 111+.
- Use the fallback path in `references/chip-contrast-playbook.md`.

### Token change breaks unrelated components
- Audit all consumers before changing `--muted`, `--border`, `--input`, `--ring`.
- Prefer narrowing the token change scope (add a new token) over modifying a global one.

### `data-theme-override` not activating
- Verify the attribute is set on `<html>` and the CSS selector matches exactly.
- Check for specificity conflicts in `index.css` or Tailwind layers.

### Issue is scenic/glass mode, not token contrast
- Confirm whether `data-scenic` is active. If so, translucency is intentional.
- Adjust the glass overlay opacity rather than the base token values.
