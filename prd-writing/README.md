# PRD Writing Skills

Two complementary skills for writing Product Requirements Documents—choose based on your context.

---

## Quick Decision Guide

| If you are... | Use |
|---------------|-----|
| Building a side project | **Individual** |
| Writing a quick feature spec | **Individual** |
| Working solo or in a pair | **Individual** |
| Need PRD done in 15-30 min | **Individual** |
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

- ⏱️ **15-30 minutes** to complete
- 🎯 **3 essential questions** for discovery
- 📝 **Focused template** with examples
- 🚫 **Out of scope** guardrails
- ✅ **Quick checklist** before coding

**Best for:** Personal projects, hackathons, MVPs, weekend builds, small features

---

### 🏢 [Enterprise SKILL.md](./enterprise/SKILL.md)

**Investment-grade PRD for strategic product initiatives.**

- ⏱️ **1-2 hours** to complete
- 🎯 **7 strategic dimensions** with assessment matrix
- 📝 **10 comprehensive sections** (Executive Summary to Appendix)
- 📊 **Decision frameworks** (RICE, MoSCoW, Risk scoring)
- 🤖 **AI/ML special section** for safety & ethics
- ✅ **20+ point checklist** across 6 quality dimensions

**Best for:** Enterprise products, AI features, stakeholder alignment, governance

---

## Philosophy

Both skills share the same DNA—**clarity before coding**—but serve different needs:

```
┌─────────────────────────────────────────────────────────────┐
│  Individual PRD                    Enterprise PRD           │
│  ─────────────                     ─────────────            │
│                                                             │
│  "What am I building?"            "Why should we invest?"   │
│  For yourself                     For stakeholders          │
│  Ship fast                        De-risk strategically     │
│  Remember decisions               Align organizations       │
└─────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
prd-writing/
├── README.md              # This file
├── individual/
│   └── SKILL.md           # Lightweight PRD skill
└── enterprise/
    └── SKILL.md           # Enterprise PRD skill
```

---

## Usage

### With Kimi Code CLI

Reference the specific skill by path:

```bash
# For individual/small projects
@/Users/susan/Documents/GitHub/vesper-team-skills/prd-writing/individual/SKILL.md

# For enterprise/strategic projects  
@/Users/susan/Documents/GitHub/vesper-team-skills/prd-writing/enterprise/SKILL.md
```

### Natural Language Triggers

**Individual:**
- "Create a quick PRD for..."
- "Write a simple spec for..."
- "I need an MVP plan for..."

**Enterprise:**
- "Create an enterprise PRD for..."
- "Write a strategic product doc for..."
- "I need a comprehensive spec for..."

---

## Comparison at a Glance

| Dimension | Individual | Enterprise |
|-----------|------------|------------|
| **Time investment** | 15-30 min | 1-2 hours |
| **Document sections** | 5-6 | 10 |
| **Discovery questions** | 3 | 7 |
| **User story format** | Simple checklist | Structured table |
| **Risk assessment** | Out of scope list | Risk register with scoring |
| **Metrics** | Success check | KPI framework |
| **Post-launch** | Watch & decide | Measure & iterate |
| **Review checklist** | 6 items | 20+ items |
| **Examples included** | 2 detailed examples | Frameworks & templates |
| **Special sections** | None | AI/ML, Compliance, Ops readiness |

---

## When to Switch

### Upgrade from Individual → Enterprise when:
- Project grows beyond 1 person
- Need budget or resource approval
- External stakeholders get involved
- Compliance becomes relevant
- Going to production with customers

### Downgrade from Enterprise → Individual when:
- Spike/prototype phase
- Personal learning project
- Time pressure for quick iteration
- Scope is truly trivial

---

## Contributing

Both skills are living documents. As you use them:

1. **Note what works** and what doesn't
2. **Adapt templates** to your context
3. **Share improvements** back to the team

---

*Choose the right tool for the job. The best PRD is the one that helps you ship value—not the one that checks the most boxes.*
