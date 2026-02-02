---
name: sales-materials-creator
description: Create sales decks, pitch decks, and sales materials using a feelings-first philosophy. Works with any product repository - the agent reads your codebase to understand features and transforms them into emotional narratives for B2B sales.
triggers:
  - create sales deck
  - make a pitch deck
  - sales presentation
  - create sales materials
  - feelings-first sales
  - sales narrative
  - value proposition
  - customer pain points
  - sales story
---

# Sales Materials Creator

Create sales decks, pitch decks, and sales materials using a feelings-first philosophy.

## Philosophy

> *"Good sales people sell features, great sales people sell outcomes, and really great sales people sell feelings."*

### The Three Layers of Sales

1. **Feelings** (Layer 3) — What we lead with
2. **Outcomes** (Layer 2) — What we use as proof
3. **Features** (Layer 1) — What we mention only when asked

### The Transformation Framework

| Before (Pain) | After (Pleasure) |
|---------------|------------------|
| 😰 Anxious | 😌 Confident |
| 😤 Frustrated | 🚀 Energized |
| 😔 Disappointed | 💪 Proud |
| 😵 Overwhelmed | 🤝 Supported |
| 😞 Paralyzed | 🧘 In Flow |

---

## When to Use

Use this skill when:
- Creating a sales deck for a product or service
- Building a pitch deck for investors or partners
- Developing cold outreach messages
- Crafting value propositions
- Preparing for sales calls or demos
- Creating one-pagers or leave-behinds

---

## Installation

### Option 1: Vesper Team Skills (Recommended)

If your team uses [Vesper](https://vesper.ai):

1. Open **Settings** → **Workspace** → **Team Skills**
2. Enter repo: `AskTinNguyen/vesper-team-skills`
3. Click **Save & Sync**
4. The skill appears automatically with a "Team" badge

### Option 2: Claude Code CLI (Manual)

Install directly to your Claude Code:

```bash
# Clone the team skills repo
git clone https://github.com/AskTinNguyen/vesper-team-skills ~/.claude/team-skills

# Copy the skill to your skills directory
cp -r ~/.claude/team-skills/sales-materials-creator ~/.claude/skills/

# Restart Claude Code to load the skill
```

### Option 3: Selective Install (Just This Skill)

```bash
# Create skills directory if needed
mkdir -p ~/.claude/skills

# Download just this skill
curl -L https://github.com/AskTinNguyen/vesper-team-skills/archive/main.tar.gz | \
  tar -xz --strip-components=1 -C ~/.claude/skills vesper-team-skills-main/sales-materials-creator

# Or use svn for single folder checkout
svn export https://github.com/AskTinNguyen/vesper-team-skills/trunk/sales-materials-creator \
  ~/.claude/skills/sales-materials-creator
```

### Verify Installation

In Claude Code, type:
```
"what skills do you have available?"
```

You should see `sales-materials-creator` in the list.

---

## How to Use This Skill

### Quick Start: Install Once, Use Anywhere

This skill works with **any product repository**. Simply navigate to your project and ask:

```
"Create a sales deck for this product"
```

The agent will:
1. Read your repo (README, docs, code) to understand the product
2. Identify key features, target audience, and value proposition
3. Apply the feelings-first framework
4. Generate a complete 11-slide sales deck

### Usage Patterns

**Basic:**
```
"Create a sales deck"
"Make a pitch deck for investors"
"Create sales materials"
```

**With audience:**
```
"Create a sales deck for enterprise CTOs"
"Make a pitch deck for seed investors"
```

**Specific format:**
```
"Create a one-pager I can email to prospects"
"Create cold outreach messages"
```

**Full suite:**
```
"Create complete sales materials: deck, one-pager, and email templates"
```

### What the Agent Reads

When you use this skill in a repo, the agent automatically analyzes:

| File | What It Learns |
|------|----------------|
| `README.md` | Product description, key features |
| `package.json` / `Cargo.toml` / `pyproject.toml` | Tech stack, dependencies |
| `docs/` or `docs/` | Architecture, use cases, guides |
| `src/` or `app/` | Core functionality, capabilities |
| `CHANGELOG.md` | Recent features, improvements |
| `CONTRIBUTING.md` | Target audience, community |
| GitHub issues (if available) | User pain points, feature requests |

---

## Bundled Resources

This skill includes reference materials and templates:

### Assets (`assets/`)
Ready-to-use templates for immediate customization:
- `sales-deck-template.md` — 11-slide feelings-first sales deck
- `pitch-deck-template.md` — Investor/partner pitch deck
- `one-pager-template.md` — Single-page summary

### Examples (`assets/examples/`)
Real-world examples for reference:
- `tender-management-deck.md` — AI tender management platform example
- `tenderflow-gamma-ready.md` — Gamma-optimized version

### References (`references/`)
Detailed guides and methodology:
- `INDEX.md` — Master navigation for all materials
- `sales-strategy.md` — Complete methodology and playbook
- `cold-outreach-messages.md` — LinkedIn, email sequences, templates
- `gamma-guide.md` — Guide for creating presentations with Gamma
- `quick-reference.md` — Daily use one-pager

---

## Sales Deck Structure

### 11-Slide Sales Deck Template

```markdown
## SLIDE 1: The Opening (Feel the Problem)

### Before We Talk About Solutions...

**How many times have you watched your [target audience]:**
- [Specific pain point 1]?
- [Specific pain point 2]?
- [Specific pain point 3]?

**The feeling:** [Emotional state before solution]

> *"[Customer quote reflecting the pain]"*
> — [Title], [Company type]

---

## SLIDE 2: The Emotional Transformation

### From This → To This

| **Before** | **After** |
|------------|-----------|
| 😰 [Pain state 1] | 😌 [Desired state 1] |
| 😤 [Pain state 2] | 🚀 [Desired state 2] |
| 😔 [Pain state 3] | ✨ [Desired state 3] |
| 😵 [Pain state 4] | 🧘 [Desired state 4] |
| 🤔 [Pain state 5] | 💪 [Desired state 5] |

**The feeling we're selling:** *[Single emotional headline]*

---

## SLIDE 3: The Outcome (Not The Features)

### Your [Target Audience] Will Feel:

🎯 **[Feeling 1]** — [Outcome description]

⚡ **[Feeling 2]** — [Outcome description]

🤝 **[Feeling 3]** — [Outcome description]

🔥 **[Feeling 4]** — [Outcome description]

---

## SLIDE 4: The Quiet Moments That Matter

### Picture This:

**[Day], [Time]**
> [Persona] needs to [task]. Previously: [old way with time/frustration]
> 
> Now: [New way with time savings]
> 
> *The feeling: "[Emotional payoff]"*

**[Another scenario]**
> [Similar structure]

**[Third scenario]**
> [Similar structure]

---

## SLIDE 5: What You Actually Get (The Features, Briefly)

[Number] [Capability Category] Including:

| Category | Capabilities | Feeling |
|----------|--------------|---------|
| **[Category 1]** | [Features] | *"[Feeling]"* |
| **[Category 2]** | [Features] | *"[Feeling]"* |
| **[Category 3]** | [Features] | *"[Feeling]"* |

---

## SLIDE 6: The Real ROI

### Not [Metric]. Feelings That Scale.

**[Use case 1]?**
- Old way: [Problem]
- New way: [Solution]
- *Feeling: [Emotional outcome]*

**[Use case 2]?**
- Old way: [Problem]
- New way: [Solution]
- *Feeling: [Emotional outcome]*

**[Use case 3]?**
- Old way: [Problem]
- New way: [Solution]
- *Feeling: [Emotional outcome]*

---

## SLIDE 7: How It Works (The Experience)

### As Simple As:

```
1. [Step 1] → 2. [Step 2] → 3. [Step 3]
```

**For [Segment 1]:**
```
[Process description]
```

**For [Segment 2]:**
```
[Process description]
```

---

## SLIDE 8: Who This Is For

### [Target Audience] Who Feel:

✅ **"[Pain point quote 1]"**

✅ **"[Pain point quote 2]"**

✅ **"[Pain point quote 3]"**

✅ **"[Pain point quote 4]"**

✅ **"[Pain point quote 5]"**

---

## SLIDE 9: The Risk of Waiting

### Every [Time Period] Without This:

- [Consequence 1]
- [Consequence 2]
- [Consequence 3]

**The compound cost:** Not just [metric]. *[Emotional cost].*

> *"[Urgency quote]"*

---

## SLIDE 10: The Ask

### Let's Give Your [Target Audience] the Feeling They Deserve

**Next Steps:**

1. **[Step 1]** — [Description]
2. **[Step 2]** — [Description]
3. **[Step 3]** — [Description]

---

## SLIDE 11: Remember

### People Won't Remember The Features.
### They'll Remember How It Felt to Finally:

- 🎯 [Feeling/outcome 1]
- ⚡ [Feeling/outcome 2]
- 🤝 [Feeling/outcome 3]
- 🚀 [Feeling/outcome 4]

**That's what we're selling.**
```

---

## Key Feeling Words

### Power Words for B2B Sales

**Confidence:**
- Certain, Assured, Confident, Capable, Masterful, In control

**Efficiency:**
- Effortless, Smooth, Streamlined, Automatic, Frictionless, Flow

**Status:**
- Professional, Polished, Premium, Elite, Best-in-class, Ahead

**Relief:**
- Peace of mind, Sleep well, Finally, At last, No more, Never again

**Empowerment:**
- Superpowers, Unstoppable, Empowered, Enabled, Equipped, Ready

---

## Translation Exercise

### Feature → Outcome → Feeling

**Step 1:** Identify the feature
- *"AI-powered tender analysis"*

**Step 2:** Translate to outcome
- *"Compare vendors in minutes instead of days"*

**Step 3:** Lead with feeling
- *"The confidence of knowing you made the right choice, backed by data"*

---

## Customer Discovery Questions

Use these to gather raw material for the deck:

### Pain Discovery
1. "Walk me through the last time you [did relevant task]. What was frustrating?"
2. "What takes way longer than it should?"
3. "What do you dread doing?"
4. "What are you doing manually that feels like a computer should do?"
5. "What decisions keep you up at night?"

### Outcome Discovery
1. "If you had a magic wand, how would this work?"
2. "What would make you feel like a hero?"
3. "How do you know you've had a good day?"
4. "What do you wish you could tell your [boss/board/team]?"
5. "What would make you proud to show this to a colleague?"

---

## Output Formats

### 1. Markdown (for Gamma)
Export as clean markdown for importing into [Gamma.app](https://gamma.app):
- Paste into "Create New AI" → "Paste in text"
- Choose Professional/Minimal theme
- Generate slides automatically

📚 **See `references/gamma-guide.md` for detailed Gamma integration instructions.**

### 2. Speaker Notes
Include notes for each slide:
```
**[SLIDE TITLE]**

**Say:** [Key talking points]
**Ask:** [Discovery question]
**Transition:** [Bridge to next slide]
```

### 3. One-Pager
Condense to single page:
- Problem (2 sentences)
- Solution (2 sentences)
- Outcomes (3 bullet points)
- CTA (1 sentence)

---

## The Mantra

> *"People will forget what you said.
> People will forget what you did.
> But people will never forget how you made them feel."*

**Every interaction. Every email. Every demo.**

Make them feel understood.
Make them feel hopeful.
Make them feel capable.
