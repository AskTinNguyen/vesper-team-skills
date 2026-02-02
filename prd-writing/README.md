# PRD Writing Skills

Two complementary skills for writing Product Requirements Documents—optimized for speed without sacrificing quality.

---

## Quick Decision Guide

| If you are... | Use |
|---------------|-----|
| Building a side project | **Individual** |
| Writing a quick feature spec | **Individual** |
| Working solo or in a pair | **Individual** |
| Need PRD done in 10-20 min | **Individual** |
| Planning an MVP | **Individual** |
| Building for enterprise customers | **Enterprise** |
| Need stakeholder/budget approval | **Enterprise** |
| Managing cross-team dependencies | **Enterprise** |
| Working on AI/ML with safety concerns | **Enterprise** |
| Have compliance/regulatory requirements | **Enterprise** |

---

## The Skills

### 🚀 [Individual SKILL.md](./individual/SKILL.md)

**Lightweight PRD for developers, side projects, and small teams.**

- ⏱️ **10-20 minutes** to complete
- 🎯 **3 essential questions** for discovery
- 📝 **Concise template** with one complete example
- 🚫 **Out of scope** guardrails
- ✅ **Quick checklist** before coding

**Best for:** Personal projects, hackathons, MVPs, weekend builds

---

### 🏢 [Enterprise SKILL.md](./enterprise/SKILL.md)

**Strategic PRD for team alignment and complex initiatives.**

- ⏱️ **30-45 minutes** to complete (not 1-2 hours!)
- 🎯 **4 strategic questions** with rapid assessment
- 📝 **7 streamlined sections** (removed redundancy)
- 📊 **Quick-reference frameworks** (RICE, MoSCoW, Risk)
- 🤖 **AI/ML add-on** (one section, not separate doc)
- ✅ **Time budget per section** included

**Best for:** Enterprise products, AI features, stakeholder alignment, governance

---

## Philosophy

Both skills share the same DNA—**clarity before coding**—but serve different contexts:

```
┌─────────────────────────────────────────────────────────────┐
│  Individual PRD                    Enterprise PRD           │
│  ─────────────                     ─────────────            │
│                                                             │
│  "What am I building?"            "Why should we invest?"   │
│  For yourself                     For stakeholders          │
│  10-20 min                        30-45 min                 │
│  Ship fast                        Align & de-risk           │
└─────────────────────────────────────────────────────────────┘
```

**Key principle:** A PRD's value is in the *thinking*, not the *length*.

---

## File Structure

```
prd-writing/
├── README.md              # This file
├── individual/
│   └── SKILL.md           # 5KB - Lightweight PRD
└── enterprise/
    └── SKILL.md           # 8KB - Strategic PRD
```

**Total:** ~13KB vs. original ~38KB (66% smaller, faster to use)

---

## Comparison

| Dimension | Individual | Enterprise |
|-----------|------------|------------|
| **Time** | 10-20 min | 30-45 min |
| **Questions** | 3 | 4 |
| **Sections** | 6 | 7 |
| **Discovery** | Essential only | Strategic only |
| **Stories** | Simple checklist | Priority-tagged table |
| **Examples** | 1 complete | Inline snippets |
| **Frameworks** | Sizing guide | RICE, MoSCoW, Risk matrix |
| **AI/ML** | N/A | One optional section |
| **Special sections** | None | Ops readiness, Risk register |

---

## What's Different (v2.1)

### Optimizations Made:

1. **Reduced Enterprise time** from 1-2 hours → 30-45 min
   - Removed redundant tables
   - Combined related sections
   - Provided time budgets per section
   - Simplified templates

2. **Streamlined both skills**
   - Removed verbose explanations
   - Kept only actionable guidance
   - One example instead of two
   - Quick-reference formats

3. **Maintained value**
   - All critical sections preserved
   - Decision frameworks included
   - Compliance/risk still covered
   - AI/ML add-on available

---

## When to Switch

### Upgrade Individual → Enterprise when:
- 🏢 External stakeholders involved
- 💰 Budget/resource approval needed
- 🔒 Compliance requirements exist
- 🤖 AI/ML with safety considerations
- 🌐 Cross-team dependencies

### Downgrade Enterprise → Individual when:
- 👤 Personal/solo project
- ⏱️ Need spec in <20 minutes
- 📝 Simple feature (CRUD, UI polish)
- 🔄 Prototype/spike phase

---

## Usage

### With Kimi Code CLI

```bash
# Quick spec for personal project
@/Users/susan/Documents/GitHub/vesper-team-skills/prd-writing/individual/SKILL.md

# Strategic spec for team alignment
@/Users/susan/Documents/GitHub/vesper-team-skills/prd-writing/enterprise/SKILL.md
```

### Natural Language

**Individual:**
- "Create a quick PRD for..."
- "Simple spec for my side project..."
- "MVP plan for..."

**Enterprise:**
- "Create a team PRD for..."
- "Strategic spec for stakeholder review..."
- "Enterprise feature requirements for..."

---

*"The best PRD is the one that gets used. Optimize for clarity, not completeness."*
