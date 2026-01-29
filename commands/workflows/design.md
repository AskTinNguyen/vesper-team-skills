---
name: workflows:design
description: Deep-dive visual refinement for video scenes with parallel design agents
argument-hint: "[scene-id, project path, or empty for discovery]"
---

# Design Refinement

<command_purpose> Deep-dive visual refinement for video scenes using parallel design specialist agents and the frontend-design skill. </command_purpose>

## Introduction

<role>Senior Visual Design Director with expertise in motion graphics, typography, color theory, and brand systems for video production</role>

**Note: The current year is 2026.** Use this when dating design sessions.

Focused design session for improving video scene visuals:
- Elevate generic aesthetics to distinctive, memorable visuals
- Ensure visual narrative coherence across scenes
- Iterate on typography, color, motion, and atmosphere

## Target Scene

<design_target> #$ARGUMENTS </design_target>

**If the target above is empty**, proceed to Step 1 to discover the project and let the user choose a scene.

**If a scene-id is provided**, skip to Step 3 (Understand Scene Context) directly.

---

## Step 1: Discover Project Context

First, find and understand the current project:

1. **Locate the project**
   - Check if in a project directory (has `project.json` or template config)
   - If not, scan `projects/` for active projects
   - If multiple, ask user which project

2. **Read project configuration**
   - `project.json` if exists (scenes, phase, brand)
   - Or template config: `src/config/sprint-config.ts` or `src/config/demo-config.ts`
   - Brand/theme: `src/config/theme.ts`

3. **Build scene inventory**
   - List all scenes from config
   - Identify which are slide-type (designable) vs demo-type (video playback)
   - Note each scene's purpose from config content

---

## Step 2: Identify Target Scene

If no scene specified in `#$ARGUMENTS`, show discovered scenes:

```
## Design Refinement

**Project:** {project_name}
**Template:** {template_type}

Which scene would you like to refine?

| # | Scene ID | Type | Description |
|---|----------|------|-------------|
{list slide-type scenes discovered from config}

(Demo/video scenes are not shown - they display recorded content)

Enter scene ID or number:
```

---

## Step 3: Understand Scene Context

Before invoking frontend-design, gather specific context:

1. **Read the target slide component**
   - Find component file from scene type mapping
   - e.g., `src/components/slides/{Type}Slide.tsx`

2. **Read scene content from config**
   - What text/data does this scene display?
   - What's the intended message?

3. **Understand position in sequence**
   - What scene comes before? What mood does it leave?
   - What scene comes after? What mood should we set up?

4. **Check current mood/intent** (if defined in project.json)
   - If scene has `designNotes.mood`, use that
   - If not, infer from content or ask user

---

## Step 4: Establish Scene Mood

If the scene doesn't have a defined mood, ask the user:

```
## Scene Mood

What feeling should the "{scene_id}" scene evoke?

The scene contains: {brief content summary}
It follows: {previous scene summary}
It leads to: {next scene summary}

Suggested moods based on content:
- {suggestion_1}
- {suggestion_2}

Or describe the mood you want:
```

Common mood dimensions:
- **Energy**: calm ↔ energetic
- **Tone**: serious ↔ playful
- **Warmth**: cool/professional ↔ warm/inviting
- **Trust**: edgy/provocative ↔ safe/reliable

---

## Step 4b: Choose Refinement Level

Use the **AskUserQuestion tool** to present refinement scope:

**Question:** "What level of refinement does this scene need?"

**Options:**

#### ✨ QUICK POLISH (Minor tweaks)

**Best for:** Scenes that are 80% there — just need color, spacing, or timing adjustments.

**Process:** Skip parallel agents. Invoke `frontend-design` directly with specific adjustment request. Single iteration cycle.

**Scope:**
- Adjust 1-2 properties (color, spacing, timing, font size)
- No structural changes
- No agent analysis needed

#### 🎨 SCENE REDESIGN (Full visual overhaul)

**Best for:** Scenes that need a new visual direction — different mood, composition, or treatment.

**Process:** Run all 5 parallel design agents (Step 5). Full synthesis. Multiple iteration cycles.

**Scope:**
- New color palette, typography, motion design
- Background and decorative element changes
- Full agent analysis and synthesis
- Multiple refinement iterations

#### 🎬 NARRATIVE ARC REVIEW (Multi-scene coherence)

**Best for:** Ensuring visual flow across the entire video or a sequence of scenes.

**Process:** Run parallel agents for the target scene AND its neighbors. Cross-scene coherence analysis. May trigger refinement of adjacent scenes.

**Scope:**
- Everything in Scene Redesign
- Adjacent scene analysis and adjustment
- Transition coherence between scenes
- Visual intensity arc across the sequence
- May spawn additional refinement sessions for neighboring scenes

Based on selection:
- **Quick Polish** → Skip to Step 6 (Iterative Refinement) with `frontend-design` only
- **Scene Redesign** → Proceed to Step 5 (Parallel Design Analysis)
- **Narrative Arc Review** → Proceed to Step 5, but extend agents to cover adjacent scenes. After refining the target, offer to refine neighbors.

---

## Step 5: Parallel Design Analysis

<ultrathink_instruction> Before implementing changes, gather multi-perspective design intelligence by launching specialist agents in parallel. Synthesize their recommendations into a unified design direction. </ultrathink_instruction>

<parallel_tasks>

Run ALL of these agents at the same time, passing scene context, mood, brand, and adjacent scene info:

1. Task color-theory-analyst(scene context, mood, brand palette)
   - Palette harmony analysis (complementary, analogous, triadic)
   - Contrast ratios for text readability at video resolution
   - OKLCH color relationships and perceptual uniformity
   - Mood-to-color mapping recommendations
   - Light/dark mode considerations if applicable

2. Task motion-design-specialist(scene context, duration, position in sequence)
   - Entrance/exit animation choreography
   - Remotion spring() and interpolate() parameter recommendations
   - Timing curves and easing functions
   - Duration budget (what fits in scene time)
   - Motion intensity relative to narrative position

3. Task typography-analyst(scene context, brand fonts, content)
   - Font pairing recommendations
   - Scale and hierarchy for video resolution (1080p/4K)
   - Line length and readability at viewing distance
   - Text animation approach (reveal, fade, kinetic)
   - Weight and tracking adjustments for screen

4. Task brand-consistency-reviewer(scene context, brand guidelines, adjacent scenes)
   - Brand color usage compliance
   - Visual language consistency across scenes
   - Logo/mark placement if applicable
   - Tone alignment with brand personality
   - Transition coherence with adjacent scenes

5. Task frontend-design-specialist(scene context, mood, all gathered constraints)
   - Overall visual direction and composition
   - Background treatment (gradients, effects, atmosphere)
   - Decorative elements (particles, shapes, glows)
   - Visual hierarchy and focal points
   - Component-level implementation suggestions

</parallel_tasks>

### Synthesis

<thinking>
After all agents return, synthesize their recommendations into a unified design direction. Resolve any conflicts (e.g., color-theory suggests cool tones but mood calls for warmth). Present a coherent proposal to the user.
</thinking>

Present the synthesized design direction:

```
## Design Direction: "{scene_id}"

**Mood:** {established mood}
**Color Palette:** {synthesized palette with hex/oklch values}
**Typography:** {font choices, sizes, weights}
**Motion:** {animation approach, timing, easing}
**Composition:** {layout, focal points, visual hierarchy}

### Agent Highlights:
- 🎨 Color: {key color recommendation}
- 🎬 Motion: {key motion recommendation}
- 🔤 Type: {key typography recommendation}
- 🏷️ Brand: {compliance status + notes}
- 🖼️ Design: {key composition recommendation}

Proceed with this direction? [Yes / Adjust / Re-analyze specific aspect]
```

---

## Step 6: Iterative Refinement

Work with user in a back-and-forth loop:

1. **Propose changes** - Present the synthesized design direction
2. **Implement** - Edit the component file
3. **Preview** - User checks Remotion Studio (hot-reload)
4. **Feedback** - User responds with what works/doesn't
5. **Refine** - Adjust based on feedback (re-run specific agent if needed)
6. **Repeat** until satisfied

**Common refinement areas:**
- Background (gradients, effects, atmosphere)
- Typography (font choice, size, animation)
- Color palette (mood, contrast, warmth/coolness)
- Motion (timing, easing, entrance/exit)
- Decorative elements (particles, shapes, glows)
- Visual hierarchy (what draws the eye)

**Re-running specific agents:** If the user wants to adjust only one aspect (e.g., "make the colors warmer"), re-run just the relevant agent (color-theory-analyst) rather than all 5.

---

## Step 7: Design Quality Gate

<critical_requirement> Before finishing, validate the refinement against this checklist. Do NOT skip this step. </critical_requirement>

### Design Quality Checklist

```
Scene: "{scene_id}" | Mood: {mood} | Level: {refinement_level}

Visual Quality:
- [ ] Typography readable at 1080p export resolution
- [ ] Color contrast meets WCAG AA (4.5:1 for text, 3:1 for large text)
- [ ] Animation completes within scene duration budget
- [ ] Visual weight balanced across scene composition
- [ ] No clipping or overflow at target resolution

Brand & Coherence:
- [ ] Brand colors used correctly (primary, secondary, accent)
- [ ] Font family matches brand guidelines
- [ ] Mood consistent with narrative position in sequence
- [ ] Transition flow natural from previous scene
- [ ] Transition flow sets up next scene appropriately

Technical:
- [ ] Remotion spring()/interpolate() params are reasonable
- [ ] No hardcoded pixel values that break at different resolutions
- [ ] Component renders without console warnings
- [ ] Performance acceptable (no jank in Remotion Studio preview)
```

If any items fail, address them before proceeding.

---

## Step 8: Document Changes & Next Steps

### Document Changes

Update project.json (if exists) with refinement notes:

```json
{
  "scenes": [
    {
      "id": "{scene_id}",
      "designNotes": {
        "mood": "{established mood}",
        "refinements": "{description of visual changes made}",
        "agentsUsed": ["color-theory", "motion-design", "typography", "brand-consistency", "frontend-design"],
        "refinementLevel": "{quick-polish|scene-redesign|narrative-arc}"
      }
    }
  ]
}
```

Add session entry:
```json
{
  "sessions": [
    {
      "date": "YYYY-MM-DD",
      "summary": "Design refinement on {scene_id}: {brief description}"
    }
  ]
}
```

### Post-Action Routing

After documenting, use the **AskUserQuestion tool** to present next steps:

**Question:** "Design refinement complete for `{scene_id}`. What would you like to do next?"

**Options:**
1. **Refine another scene** - Pick a different scene to refine
2. **Coherence review** - Run brand-consistency-reviewer across ALL scenes to check visual flow
3. **Render preview** - Run `/remotion render` to export a preview video
4. **Commit changes** - Stage and commit the refined component files
5. **Compare before/after** - Take screenshots of before vs after for documentation

Based on selection:
- **Refine another scene** → Loop back to Step 2 (Identify Target Scene)
- **Coherence review** → Launch `brand-consistency-reviewer` for each scene in sequence, report gaps
- **Render preview** → Invoke the `remotion` skill to render
- **Commit changes** → Stage changed files, commit with `style(video): refine {scene_id} - {mood} treatment`
- **Compare before/after** → Use `agent-browser` to screenshot Remotion Studio at the scene timestamp
- **Other** (automatically provided) → Accept free text for additional work

Loop back to options until user is done with the design session.

---

## Design Principles for Video

When working with frontend-design skill on video scenes:

1. **Video scale** - Everything needs to be larger than web UI (viewers are farther from screen)
2. **Motion matters** - Static designs that work on web may feel dead on video
3. **Time constraints** - Each scene has limited duration; don't over-animate
4. **Narrative arc** - Consider how visual intensity builds across scenes
5. **Contrast creates impact** - A calm scene makes the next dramatic scene hit harder

---

## Scene Type Reference

These are common scene types, but projects may have different ones:

| Type | Common Purpose | Design Considerations |
|------|----------------|----------------------|
| title | Opening, brand intro | Set the mood, establish visual language |
| overview | Agenda, summary | Clarity, scannable layout |
| demo | Show functionality | Clean chrome, focus on content |
| summary | Recap, stats | Data visualization, credibility |
| credits | Closing | Graceful exit, brand reinforcement |
| problem | Pain points | Tension (if narrative calls for it) |
| solution | Resolution | Relief, hope |
| cta | Call to action | Energy, memorability |

**Note**: Not all projects use all types. The command discovers what's actually in the project.

---

## Example Session

```
User: /design

Claude: Let me discover your project...

Found project: "q4-release-video"
Template: sprint-review
Brand: digital-samba

## Design Refinement

Which scene would you like to refine?

| # | Scene ID | Type | Description |
|---|----------|------|-------------|
| 1 | title | title | "What's New in v2.5" |
| 2 | overview | overview | 4 feature highlights |
| 3 | summary | summary | Sprint stats |
| 4 | credits | credits | Team acknowledgment |

(3 demo scenes not shown)

User: 1

Claude: [Reads TitleSlide.tsx, sprint-config.ts, theme.ts]
[Reads overview scene to understand what follows]

The title announces "What's New in v2.5" for Digital Samba.
It's followed by an overview of 4 features.

What mood should this title scene set?
- Excited/energetic (big release energy)
- Professional/trustworthy (enterprise feel)
- Warm/welcoming (team celebration)

User: Warm and celebratory - this was a big team effort

Claude: What level of refinement does this scene need?
1. ✨ Quick Polish - minor tweaks
2. 🎨 Scene Redesign - full visual overhaul
3. 🎬 Narrative Arc Review - multi-scene coherence

User: 2 (Scene Redesign)

Claude: Launching 5 parallel design agents...

[color-theory-analyst]: Warm amber palette, oklch(0.85 0.12 75)
[motion-design-specialist]: spring({damping: 15}) text reveal, 0.3s stagger
[typography-analyst]: Inter Bold 72px title, weight 800, tracking -0.02em
[brand-consistency-reviewer]: Brand orange ✓, needs softer secondary
[frontend-design-specialist]: Radial gradient bg, subtle confetti particles

## Design Direction: "title"

**Mood:** Warm, celebratory
**Color Palette:** Amber #F59E0B → Cream #FEF3C7, accent Coral #FB923C
**Typography:** Inter Bold 72px, tracking -0.02em, warm white
**Motion:** spring reveal + 0.3s stagger, gentle confetti loop
**Composition:** Centered title, radial gradient, floating particles

Proceed? [Yes / Adjust / Re-analyze]

User: Yes

Claude: [Implements changes to TitleSlide.tsx]

Running quality checklist...
✓ Typography readable at 1080p
✓ Color contrast 7.2:1 (passes AA)
✓ Animation within 3.5s budget
✓ Brand colors correct

Design refinement complete for "title". What next?
1. Refine another scene
2. Coherence review across all scenes
3. Render preview
4. Commit changes

User: 4

Claude: git commit -m "style(video): refine title scene - warm celebratory treatment"
```

## Related Commands

```
workflows:plan → workflows:design → workflows:work → workflows:review → workflows:compound
```

| Command | When to Use |
|---------|-------------|
| `/workflows:plan` | Plan a new feature or improvement |
| `/design` | Refine visual design of video scenes |
| `/workflows:work` | Execute a plan (implementation) |
| `/workflows:review` | Code review with multi-agent analysis |
| `/workflows:compound` | Document solutions for team knowledge |
| `/scene-review` | Quick scene-level review |
| `/remotion` | Render video output |
