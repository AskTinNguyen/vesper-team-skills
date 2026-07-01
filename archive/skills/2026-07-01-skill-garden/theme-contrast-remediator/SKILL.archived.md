---
name: theme-contrast-remediator
description: Audits and remediates Light/Dark theme contrast, legibility, and opacity-bleed issues in React/Tailwind UIs by patching semantic tokens, chip recipes, and shared input primitives. Use when text is hard to read, chips lack legibility, opacity bleed washes out Light mode, or status badges fail WCAG contrast.
globs:
  - "apps/electron/src/renderer/index.css"
  - "apps/electron/src/renderer/components/ui/label-badge.tsx"
---

# Theme Contrast Remediator

Fix low-legibility UI caused by weak color contrast, hue-matched chips, and excessive transparency in Light and Dark themes.

## When To Use

Activate when:
- Users report "hard to read" text, labels, chips, or badges.
- Light mode looks washed out due to opacity bleed or translucent layering.
- Dark mode loses distinction between surfaces and foreground text.
- UI uses many `bg-*/xx`, `text-*/xx`, `border-*/xx` utilities without semantic token discipline.
- Status chips (persona/source/alert labels) look colorful but not legible.

## Essential Principles

1. Enforce text/background separation first; preserve hue second.
2. Do not use same-hue text on same-hue tinted backgrounds for small chip text.
3. In Light mode, keep global base surfaces opaque unless scenic/glass mode is explicitly active.
4. Prefer semantic tokens (`bg-muted`, `border-input`, `text-foreground`) over ad-hoc alpha chains.
5. Ensure chip recipe uses three layers: low tint bg + stronger tint border + neutral text.
6. Improve shared primitives before patching many leaf components.
7. Verify in both Light and Dark mode before finalizing.

## Routing

| Task | File |
|------|------|
| Step-by-step remediation workflow | `workflows/remediate-contrast.md` |
| Chip recipe formulas and dynamic labels | `references/chip-contrast-playbook.md` |
| Fix pattern catalog (A/B/C) | `references/fix-patterns.md` |

## Anti-Patterns

- Patching individual component chip styles before fixing shared primitives and tokens.
- Using `!important` to force contrast; fix the token cascade instead.
- Adding dark-mode-only overrides without verifying light-mode parity.
- Increasing saturation on both text and background simultaneously (preserves hue closeness).
- Using inline `style=` overrides on chips when a shared `LabelBadge` or utility class exists.
- Adjusting `--muted` or `--border` tokens without checking all consumers (inputs, cards, popovers).

## Success Criteria

- Contrast complaint is resolved in Light and Dark mode.
- All affected text meets WCAG AA contrast ratio (>= 4.5:1 normal text, >= 3:1 large text/UI).
- Shared primitives reflect the new contrast baseline.
- No key metadata chip relies on same-hue text/background pairing.
- Theme layer opacity behavior is intentional (not accidental bleed).
- `bun run lint:electron` and `bun run typecheck:all` pass cleanly.
- Changes documented in `docs/solutions/ui-bugs/{slug}-{YYYYMMDD}.md`.

## Integration

| Scenario | Related Skill |
|----------|--------------|
| Broad layout/spacing/design gate | `/gestalt-frontend-design` (general perceptual design) |
| Visual regression tests after fix | `/vesper-electron-testing` (Electron E2E/snapshot) |

Boundary: `gestalt-frontend-design` handles general perceptual design. This skill handles Vesper-specific token/chip/opacity remediation.

## Next Step

After remediation: invoke `/vesper-electron-testing` for visual regression tests, or `/gestalt-frontend-design` for broader quality gate on affected components.
