---
name: workflows:qa-design-analyzer
description: Analyze game design documents (Soulslike focus) and orchestrate risk-based QA execution with structured workflow
argument-hint: "[mode] [design-target]" e.g., "full boss-design.md" or "combat stamina system" or "pr <url>"
---

# QA Design Analyzer (Soulslike)

Analyze **Game Design Documents** with a QA-first, execution-ready mindset.  
This workflow is optimized for **Soulslike games**, focusing on combat precision, difficulty balance, player punishment loops, and performance risk.

---

## When to Use

- Analyze full design doc  
  `/workflows:qa-design-analyzer full boss-design.md`

- Analyze a single system  
  `/workflows:qa-design-analyzer "Stamina & Dodge System"`

- Review design changes / PR  
  `/workflows:qa-design-analyzer pr <url>`

- Pre-production QA review  
  `/workflows:qa-design-analyzer early design`

---

## High-Level Workflow (7 Steps)

```
┌──────────────────────────────────────────────────────────────┐
│                 QA DESIGN ANALYZER (SOULSLIKE)               │
├──────────────────────────────────────────────────────────────┤
│ Step 0: Input Clarification                                  │
│ Step 1: System & Feature Decomposition                       │
│ Step 2: Risk & Failure Mode Analysis                         │
│ Step 3: Test Strategy Definition                             │
│ Step 4: Detailed Test Case Design                            │
│ Step 5: Execution Guidance (Manual / Tool / Telemetry)      │
│ Step 6: QA Report & Go / No-Go Recommendation                │
└──────────────────────────────────────────────────────────────┘
```

---

## Step 0: Input Clarification

If the design input is vague or incomplete, **do not proceed**.

### Clarification Examples

**If system design is unclear**
- What is the player goal in this system?
- Is this system skill-based, stat-based, or hybrid?
- Is this PvE-only or shared with PvP?

**If boss design**
- Intended difficulty tier? (Early / Mid / Late / Optional)
- Is this boss designed to punish greed, positioning, or timing?
- Expected average fight duration?

---

## Step 1: System & Feature Decomposition

Break the design into **testable subsystems**.

### Example (Boss Design)

| Subsystem | Description |
|---------|------------|
| Combat Loop | Attack → Dodge → Punish |
| Boss AI | State machine, phase transitions |
| Camera | Lock-on behavior, occlusion |
| Collision | Weapon hitbox, environment |
| Performance | VFX density, animation sync |

**Output:** System Map

---

## Step 2: Risk & Failure Mode Analysis

Identify where the game can **break trust** with the player.

### Risk Categories (Soulslike-specific)

| Risk Type | Description |
|---------|-------------|
| Fairness Risk | Unavoidable damage, unclear telegraphs |
| Skill Expression Risk | Timing window too tight or too lenient |
| Camera Risk | Lock-on fails near walls |
| Readability Risk | VFX hides attack startup |
| Performance Risk | Frame drops during phase change |
| Exploit Risk | Safe spots, animation cancel abuse |

### Failure Mode Example

```yaml
risk:
  id: R-BOSS-03
  type: Fairness
  description: Boss AOE hits player behind solid pillar
  impact: High
  likelihood: Medium
  detection:
    - Collision debug
    - Repro positioning test
```

---

## Step 3: Test Strategy Definition

Define **how QA will validate the design**, not just what.

### Strategy Matrix

| Area | Strategy |
|----|---------|
| Combat Timing | Frame-by-frame capture |
| AI | Forced state transitions |
| Camera | Edge positioning tests |
| Performance | Worst-case VFX spam |
| UX | Blind test (no tutorial) |

### QA Focus Level

- **MINIMAL** – Sanity & smoke checks  
- **MORE** – Full coverage (default)  
- **A LOT** – Boss / Core combat pillar

---

## Step 4: Detailed Test Case Design

### Test Case Template

```markdown
TC ID: BOSS-CMB-014
Title: Dodge iframe consistency vs vertical slash
Priority: P0
Preconditions:
- Player stamina > 50%
- Boss Phase 2
Steps:
1. Lock-on boss
2. Trigger vertical slash
3. Dodge sideways at last 5 frames
Expected:
- No damage taken
- Stamina reduced correctly
Notes:
- Capture at 60fps
```

### Mandatory Coverage

- [ ] Perfect play
- [ ] Late input
- [ ] Early input
- [ ] Low stamina
- [ ] Camera edge case
- [ ] Performance under stress

---

## Step 5: Execution Guidance

### Manual Execution
- Controller + keyboard parity
- Slow-motion capture (0.25x)
- Frame stepping

### Tooling
- Frame capture tools
- Collision visualizer
- AI state debug
- Performance HUD

### Telemetry Hooks
- Dodge success rate
- Death heatmap
- Phase duration

---

## Step 6: QA Report & Go / No-Go

### QA Summary

```yaml
system: Boss - Jade Guardian
overall_risk: HIGH
blockers:
  - Unreadable phase 3 AOE
  - Camera breaks near wall
recommendation: NO-GO
```

### Go / No-Go Rules

| Condition | Decision |
|--------|----------|
| P0 Fairness bug exists | ❌ No-Go |
| Frame drop < 50fps | ❌ No-Go |
| Exploit trivializes boss | ❌ No-Go |
| Only cosmetic issues | ✅ Go |

---

## Output Artifacts

- Risk Register (MD)
- Test Case Suite (MD)
- QA Recommendation Summary
- Execution Checklist

---

## Philosophy

> A Soulslike is fair **only if the player believes death was their fault**.  
QA exists to protect that belief.

---
