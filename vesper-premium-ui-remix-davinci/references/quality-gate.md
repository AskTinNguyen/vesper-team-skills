# Quality Gate

Use this gate before presenting final UI.

## 1. Vesper Identity Check
- Does the interface feel **classy, tactile, and responsive**?
- Does it avoid generic SaaS or AI-demo styling?
- Would it fit naturally beside the rest of Vesper?

## 2. Hierarchy Check
- Can the main action be identified within 2 seconds?
- Are heading, support copy, and metadata visually distinct?
- Are secondary actions quieter than the primary action?

## 3. Gestalt Check
- Related items are grouped clearly
- Similar controls share treatment
- important regions have clear figure-ground separation
- spacing tiers are consistent and intentional
- no orphan controls float without context

## 4. Light Mode Check
- Base surfaces are legible and mostly opaque
- no washed-out layered translucency
- text/background pairings maintain strong contrast
- chips and labels remain readable

## 5. Dark Mode Check
- dark surfaces stack clearly
- the screen feels focused, not gloomy
- accent usage remains restrained
- small text keeps strong readability

## 6. Interaction Check
- hover, focus, active, disabled states are all present
- buttons acknowledge input immediately
- motion is subtle and purposeful
- `prefers-reduced-motion` is respected

## 7. Copy Check
- labels are specific
- helper text is concise
- CTAs are verb-first
- no placeholder demo copy leaks through
- terminology is consistent across the surface

## 8. Product Fit Check
- Does this reduce intimidation for a non-technical knowledge worker?
- Does it help the user feel oriented and capable?
- Are advanced controls disclosed progressively instead of dumped upfront?

## 9. Rejection Triggers
Reject or revise if any of these are true:
- it still looks like a direct clone of the source example
- light mode feels washed out
- dark mode relies on glow/neon to feel “premium”
- badge and chip colors are doing too much work
- there are too many equally loud actions
- the design feels colder or more technical than Vesper should

## 10. Final Standard
The interface should feel like:
- **clearer** than the source example
- **warmer** than the source example
- **more premium** than the source example
- **more product-specific** than the source example

If it is only “similar but nicer,” keep pushing.
