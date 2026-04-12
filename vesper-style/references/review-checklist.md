# Vesper Review Checklist

Use this checklist before considering a Vesper-style screen, component, flow, or prompt-facing surface ready. This is a **quality gate**, not a brainstorming worksheet.

A design passes only when it supports Vesper’s core outcome: users feel **oriented, capable, and in control** while working with advanced AI.

---

## How to Use This Checklist

1. Review the work in **both light and dark mode**.
2. Evaluate the default path before looking at advanced states.
3. Test the interface as a first-time user and as a repeat user.
4. Reject screens that look visually polished but still feel intimidating, generic, or low-clarity.
5. Record failures concretely so they can be fixed in shared primitives, tokens, layout patterns, or copy.

---

## 1. Brand Fit

- [ ] The surface feels **warm editorial**, not sterile enterprise and not sci-fi AI.
- [ ] The overall impression is **classy, tactile, and responsive**.
- [ ] The design feels **quietly premium**, not loud or gimmicky.
- [ ] The screen could plausibly belong to Vesper even with the logo hidden.
- [ ] The interface avoids generic AI SaaS sameness.

**Fail if:** the design looks like a trend-forward AI dashboard template, command center, or generic startup landing page.

## 2. User Orientation

- [ ] The user can tell where they are within two seconds.
- [ ] The main task or purpose of the screen is obvious.
- [ ] The current state is legible: loading, ready, paused, failed, disconnected, completed, etc.
- [ ] The user can tell what changed after an action.
- [ ] The next best action is apparent without reading the whole screen.

**Fail if:** users must inspect multiple regions before understanding the page.

## 3. Hierarchy and Composition

- [ ] There is one clearly dominant primary region or action.
- [ ] Secondary controls are present but quieter.
- [ ] Tertiary metadata does not compete with content or actions.
- [ ] Section spacing creates a calm, readable flow.
- [ ] Related items are grouped intentionally, not just placed near each other.
- [ ] The layout uses fewer, stronger regions rather than many weak containers.

**Fail if:** everything feels equally important, or if the layout relies on many cards, chips, and dividers to simulate structure.

## 4. Progressive Disclosure

- [ ] The default experience is approachable.
- [ ] Advanced controls are discoverable without dominating the first-run path.
- [ ] Complexity appears only when the user needs it.
- [ ] The interface does not dump every option onto the screen at once.
- [ ] Technical details are available on demand rather than forced upfront.

**Fail if:** a non-technical founder would feel like they need an operator manual to continue.

## 5. Light Mode Quality

- [ ] Light mode feels materially solid and inviting.
- [ ] Base surfaces are opaque or near-opaque.
- [ ] Text remains crisp in bright conditions.
- [ ] Surface layering is easy to parse.
- [ ] Warmth comes from color balance and material treatment, not from washed-out translucency.

**Fail if:** light mode looks elegant only in a mockup and weak in real use.

## 6. Dark Mode Quality

- [ ] Dark mode feels focused and elegant.
- [ ] Surface elevation is clear without neon theatrics.
- [ ] Text contrast supports long-session reading.
- [ ] Accent usage is restrained and purposeful.
- [ ] The screen maintains parity with light mode rather than becoming a separate personality.

**Fail if:** dark mode turns into a dramatic glow-heavy stage set.

## 7. Color and Contrast

- [ ] Color supports hierarchy, state, and warmth.
- [ ] Accent color is used selectively.
- [ ] Semantic color is understandable and consistent.
- [ ] Important information is never conveyed by color alone.
- [ ] Text and UI elements meet accessible contrast expectations.
- [ ] Chips and badges preserve hue in the background/border while keeping text neutral and high-contrast.

**Fail if:** the screen uses rainbow status color, low-contrast tints, or accent color on nearly everything.

## 8. Copy and Tone

- [ ] Headings orient rather than market.
- [ ] CTAs are verb-first and specific.
- [ ] Helper text answers the user’s likely next question.
- [ ] Error messages explain what happened and what to do next.
- [ ] Copy sounds calm, capable, and human.
- [ ] The interface avoids hype, novelty jokes, and AI theater.

**Fail if:** the copy sounds like generic startup marketing or anthropomorphic AI banter.

## 9. Interaction Quality

- [ ] Hover, press, focus, loading, success, and error states are all clear.
- [ ] Interactions acknowledge input immediately.
- [ ] Motion is restrained and useful.
- [ ] Focus states are visible and polished.
- [ ] Disabled states remain understandable.
- [ ] The interface feels touchable and precise, not inert.

**Fail if:** interaction feedback is missing, delayed, or over-animated.

## 10. Accessibility and Resilience

- [ ] The screen supports WCAG 2.2 AA expectations or better.
- [ ] Keyboard navigation works through the full primary flow.
- [ ] Visual grouping has semantic equivalents where needed.
- [ ] Reduced-motion preferences are respected.
- [ ] Long text, empty states, and error states are handled gracefully.
- [ ] The design remains legible under realistic conditions, not just ideal screenshots.

**Fail if:** accessibility is postponed to later or handled only cosmetically.

## 11. Human Agency in AI Workflows

- [ ] The user remains clearly in charge.
- [ ] Agent actions are inspectable enough to trust.
- [ ] Automated behavior does not obscure consequences.
- [ ] The interface shows what happened without overwhelming the user with internals.
- [ ] The system feels assistive, not domineering or mysterious.

**Fail if:** the screen emphasizes automation spectacle more than human understanding.

## 12. Anti-Pattern Sweep

Reject immediately if the design includes any of the following:

- [ ] Cyberpunk styling
- [ ] Neon AI dashboard tropes
- [ ] Generic AI SaaS sameness
- [ ] Stacked translucency in light mode
- [ ] Low-contrast tinted chips or labels
- [ ] Dense control bars with equal-weight actions
- [ ] Wall-of-settings layouts without progressive disclosure
- [ ] Rainbow status systems
- [ ] Decorative motion without informational value
- [ ] Hype-heavy copy about intelligence, magic, or the future

If any box would be checked, the design is not ready.

## 13. Final Pass Questions

Before approval, answer these questions:

- [ ] Would a smart non-technical user feel more capable after landing here?
- [ ] Is the main action obvious within two seconds?
- [ ] Does the design feel distinctly Vesper rather than generically AI?
- [ ] Is light mode just as intentional as dark mode?
- [ ] Does the product express power through clarity instead of extra controls?
- [ ] Would this still feel good after daily use, not just on first impression?

If any answer is no, keep iterating.

---

## Quick Verdict Template

Use this summary when handing off review notes:

```md
### Vesper Review Verdict
- **Brand fit:** pass | needs work
- **Orientation:** pass | needs work
- **Hierarchy:** pass | needs work
- **Light/dark parity:** pass | needs work
- **Copy/tone:** pass | needs work
- **Accessibility:** pass | needs work
- **Anti-pattern sweep:** clear | failed

**Top fixes before ship**
1. ...
2. ...
3. ...
```

---

## Standard for Approval

Approve only when the work feels:
- **clear before clever**
- **warm before sterile**
- **premium before flashy**
- **powerful without intimidation**
- **agent-native with human agency intact**
