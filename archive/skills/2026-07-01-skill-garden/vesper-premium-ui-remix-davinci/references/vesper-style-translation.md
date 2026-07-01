# Vesper Style Translation

Use these rules to translate reference UI into Vesper's design language.

## 1. Emotional Shift
Move the design from:
- demo-like → product-grade
- generic SaaS → warm editorial
- control-heavy → calmly guided
- flashy AI → composed and premium

## 2. Surface Translation
### Light mode
- Prefer **opaque** base surfaces.
- Avoid stacked translucency and same-hue foreground/background pairings.
- Use warm neutrals rather than sterile grayscale.
- Let the main reading surface feel inviting and touchable.

### Dark mode
- Use depth through layered surfaces, not neon highlights.
- Keep contrast strong enough for long sessions.
- Make dark mode feel focused and elegant, not dramatic for its own sake.

## 3. Hierarchy Translation
When a source example feels flat:
- enlarge the primary title tier
- reduce visual competition from metadata and support copy
- make one action obviously primary
- group supporting controls into quieter regions

Use a 3-level hierarchy minimum:
1. **Primary** — title, main action, key content
2. **Secondary** — descriptions, tabs, supporting controls
3. **Tertiary** — metadata, helper text, low-priority actions

## 4. Spacing Translation
Upgrade demo spacing into stronger rhythm:
- label/helper to field: `space-y-1` or `space-y-2`
- field to field in same group: `space-y-3` or `space-y-4`
- group to group in same section: `space-y-6` or `space-y-8`
- section to section: `space-y-10` to `space-y-16`

If a source layout feels noisy, the first fix is usually **fewer competing groups + bigger sectional separation**.

## 5. Color Translation
### Keep
- one confident accent
- semantic status colors with restraint
- tinted neutrals for warmth

### Avoid
- rainbow badges
- purple-blue AI gradients
- same-hue text on tinted chips
- using accent color on every interactive element equally

### Chip rule
For chips/badges/labels:
- preserve hue in background/border
- keep small text neutral and high-contrast
- never rely on hue alone to convey meaning

## 6. Interaction Translation
Vesper should feel tactile, not noisy.

Add:
- immediate hover/press acknowledgment
- visible focus states
- crisp button hierarchy
- subtle shadow/elevation changes where meaningful
- restrained motion (150-250ms for small transitions)

Avoid:
- elastic/bouncy motion
- long theatrical transitions
- decorative animations that do not improve understanding

## 7. AI Interface Translation
When adapting AI/chat/assistant references:
- make the main action feel approachable, not technical
- avoid overwhelming users with too many controls at once
- put advanced controls behind progressive disclosure
- make input, output, and next-step actions visually distinct
- favor orientation and trust over gadget energy

## 8. Copy Translation
Replace demo-grade copy with:
- clearer labels
- shorter helper text
- human, calm language
- action-oriented CTAs

Examples:
- "Submit" → "Save changes"
- "Generate" → "Draft response" or "Create summary" when context allows
- "Integration" → "Integrations"
- "Notification" → "Notifications"

## 9. Anti-Patterns to Remove
Strip these out during translation:
- sci-fi AI styling
- gloomy hacker dark mode
- dense control bars with equal-weight buttons
- arbitrary emoji/icon colors that do not map to meaning
- generic card grids where hierarchy should be stronger
- light-mode washed-out translucency

## 10. Final Test
Ask:
1. Does this feel like Vesper rather than borrowed UI?
2. Does the main action become clearer within 2 seconds?
3. Would a non-technical founder feel more oriented, not more intimidated?
4. Is light mode still beautiful and readable?
5. Is the output classy, tactile, and restrained?

If any answer is no, the translation is incomplete.
