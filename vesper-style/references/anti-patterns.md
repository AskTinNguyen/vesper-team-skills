# Vesper Anti-Patterns

Use this document as a **hard reject list** when designing, reviewing, or translating interfaces into the Vesper style. These are not minor taste disagreements. They are recurring failure modes that pull the product toward generic AI SaaS aesthetics, weaker usability, or lower trust.

## 1. The Main Failure Mode

The biggest risk is building something that looks like **an AI product about AI** instead of a premium product that helps people get work done with AI.

In practice, this usually shows up as:
- too many controls
- too much visual noise
- too much eagerness to signal “futuristic”
- too little attention to readability, orientation, and human agency

When in doubt, choose **clarity, warmth, and hierarchy** over novelty.

## 2. Hard Rejects

### 2.1 Cyberpunk or sci-fi styling
**Reject:** neon glows, holographic motifs, matrix-style grids, glowing wireframes, chrome gradients, terminal cosplay, “future console” framing.

**Why it fails:**
- makes the product feel intimidating
- confuses spectacle for sophistication
- ages quickly
- clashes with Vesper’s warm editorial identity

**Prefer instead:**
- warm neutral surfaces
- restrained accents
- crisp typography
- subtle depth and tactile feedback

### 2.2 Neon AI dashboard tropes
**Reject:** electric cyan/purple palettes, glowing KPI tiles, saturated metric walls, accent color on everything, AI “control tower” compositions.

**Why it fails:**
- looks like generic 2025 AI startup output
- flattens hierarchy because everything shouts
- makes advanced workflows feel less approachable

**Prefer instead:**
- one clear primary action
- quieter secondary controls
- semantic color used sparingly
- layout-driven hierarchy instead of color-driven noise

### 2.3 Generic AI SaaS sameness
**Reject:** templates that could belong to any AI startup after a logo swap.

Common signals:
- purple-blue gradients by default
- identical rounded card grids
- hero copy about “unlocking intelligence”
- overuse of badges to simulate structure
- generic “assistant panel + analytics cards + glowing CTA” layouts

**Why it fails:**
- erases product character
- weakens trust
- makes the interface feel mass-produced

**Prefer instead:**
- editorial layout
- clear document/work surface metaphors
- Vesper-specific copy and hierarchy
- restrained, durable visual language

### 2.4 Stacked translucency in light mode
**Reject:** translucent cards on translucent panels on tinted page backgrounds, especially in light mode.

**Why it fails:**
- destroys text contrast
- makes the interface feel washed out and fragile
- reduces tactile solidity
- creates visual mud when layered repeatedly

**Prefer instead:**
- opaque or near-opaque surfaces
- one clear material layer per region
- scenic glass only as an intentional exception, never the baseline

### 2.5 Low-contrast tinted chips and badges
**Reject:** same-hue text on tinted backgrounds, especially for small labels, statuses, or metadata.

**Why it fails:**
- fails readability in real use
- collapses further in bright environments or low-quality displays
- turns status communication into decoration

**Prefer instead:**
- tinted background + border + neutral high-contrast text
- hue used as support, not as the sole carrier of meaning
- a chip system that remains legible in both light and dark modes

### 2.6 Dense control bars and equal-weight actions
**Reject:** top bars or panels full of buttons, toggles, pills, and dropdowns with little distinction between primary and secondary actions.

**Why it fails:**
- increases intimidation
- slows decision-making
- hides the important action in a sea of optional ones

**Prefer instead:**
- one obvious primary action
- progressive disclosure for advanced controls
- grouped secondary tools in quieter regions

### 2.7 Wall-of-settings layouts
**Reject:** long forms or settings screens where every option is visible by default and grouped only by proximity accidents.

**Why it fails:**
- creates cognitive overload
- makes advanced systems feel brittle
- turns setup into a tax instead of a guided flow

**Prefer instead:**
- section-based grouping
- helpful section intros where needed
- advanced options collapsed or deferred
- clearer defaults and explanations

### 2.8 Flat hierarchy
**Reject:** screens where titles, metadata, helper text, controls, and tertiary information all compete at similar visual weight.

**Why it fails:**
- users cannot identify the main action quickly
- the interface feels “busy” even when it contains little
- scanning becomes effortful

**Prefer instead:**
- strong primary title tier
- visible action hierarchy
- quieter support copy and metadata
- layout spacing that establishes reading order

### 2.9 Color-only meaning
**Reject:** status systems that depend only on hue or low-contrast tint differences.

**Why it fails:**
- weak accessibility
- poor reliability across themes
- high ambiguity under real-world conditions

**Prefer instead:**
- color + text label + icon/shape when useful
- readable badges and alert styles
- clear semantic language like Ready, Paused, Needs attention

### 2.10 Decorative motion without informational value
**Reject:** flourish animations, long fades, bounce effects, elastic transitions, animated backgrounds, and staged choreography for routine tasks.

**Why it fails:**
- makes the UI feel less precise
- slows expert usage
- weakens the sense of control

**Prefer instead:**
- quick feedback
- restrained motion
- transition timing that supports understanding
- reduced-motion respect by default

### 2.11 Dark mode as a theatrical stage set
**Reject:** ultra-black backgrounds with glowing accents, neon edge lighting, intense gradients, or over-dramatized contrast.

**Why it fails:**
- reduces long-session comfort
- feels more performative than practical
- breaks parity with the brand’s composed tone

**Prefer instead:**
- elegant twilight surfaces
- layered depth
- controlled highlights
- readable text and stable contrast

### 2.12 Light mode as washed-out luxury
**Reject:** pale tinted surfaces with faint text, subtle-on-subtle dividers, or “minimalist” treatments that depend on perfect display conditions.

**Why it fails:**
- beautiful in mockups, weak in real usage
- harms accessibility and legibility
- erodes trust because the product feels fragile

**Prefer instead:**
- opaque material definition
- crisp text/background separation
- restrained warmth with strong readability

### 2.13 Terminal-first metaphors for general users
**Reject:** interfaces that assume users want shells, logs, raw JSON, or developer-console framing as the primary entrypoint.

**Why it fails:**
- alienates non-technical users
- confuses system internals with user value
- makes powerful features feel inaccessible

**Prefer instead:**
- human-readable summaries first
- detail-on-demand
- raw technical detail only where it truly helps

### 2.14 Overwritten copy
**Reject:** startup hype, AI evangelism, novelty jokes, “magical” phrasing, or verbose paragraphs that restate headings.

**Why it fails:**
- wastes attention
- lowers credibility
- makes the product sound generic or juvenile

**Prefer instead:**
- calm, direct language
- concise helper text
- action-oriented CTAs
- copy that clarifies consequences and next steps

### 2.15 Card nesting and container clutter
**Reject:** cards inside cards inside panels, each with its own border, radius, and shadow.

**Why it fails:**
- fragments hierarchy
- introduces visual noise
- makes the interface feel assembled rather than designed

**Prefer instead:**
- fewer, clearer container boundaries
- spacing as a grouping tool
- one dominant container per logical region

### 2.16 Rainbow status systems
**Reject:** using many unrelated bright colors to create the illusion of structure.

**Why it fails:**
- overwhelms the eye
- makes semantic color less trustworthy
- creates visual clutter fast

**Prefer instead:**
- restrained semantic palette
- most UI in neutrals
- color reserved for state, emphasis, and key actions

## 3. Review Heuristics

If you are unsure whether something has drifted off-brand, use these tests.

### 3.1 Screenshot test
Hide the logo. Could the interface be mistaken for:
- a generic AI startup demo?
- a cyberpunk dashboard template?
- an investor-facing “future of AI” landing page?

If yes, it needs rework.

### 3.2 Squint test
Squint at the interface.

Ask:
- is one action clearly dominant?
- are the main regions obvious?
- does the page feel calm or noisy?

If everything is competing, hierarchy is broken.

### 3.3 Light mode reality test
Would this still feel crisp on a bright laptop in daylight? If not, remove translucency, increase contrast, or simplify surface stacking.

### 3.4 Non-technical founder test
Would a smart founder feel capable here, or feel like they need an operator standing beside them? If the latter, simplify and reframe.

### 3.5 Repeat-use test
Would this still feel good after the hundredth use, or is it relying on first-impression spectacle? Durable product quality matters more than novelty.

## 4. Red-Flag Phrases During Review

If a design discussion includes these justifications, slow down:
- "We need it to feel more futuristic"
- "Let’s add more glow"
- "The cards feel empty, so add more badges"
- "Let’s surface every control for power users"
- "It looks premium because it’s very subtle" when contrast is poor
- "It needs more AI energy"

These often signal drift away from Vesper’s principles.

## 5. Safer Corrections

When a screen is off-brand, the right fix is usually one of these:
- reduce visible controls
- strengthen primary/secondary hierarchy
- replace translucent surfaces with solid ones
- demote decorative color
- improve chip/badge contrast
- rewrite headings and CTAs to be calmer and clearer
- separate advanced options from the default path
- make light mode materially stronger

## 6. Final Standard

A Vesper interface should never need neon, spectacle, or generic AI signifiers to feel advanced.

If the screen is truly good, users will feel the power through:
- clarity
- trust
- speed
- hierarchy
- responsiveness
- restraint
