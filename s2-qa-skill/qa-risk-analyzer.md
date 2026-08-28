# qa-risk-analyzer

## Overview

| name | description | argument-hint |
|------|-------------|---------------|
| workflows:performance-analyzer | Perform deep, system-level risk analysis for game features, mechanics, encounters, and pipelines with Soulslike-oriented severity modeling | [design doc, feature description, system spec, changelog, or test scope] |

## Command Purpose

```xml
<command_purpose>
Identify, classify, and prioritize risks that can cause player frustration, unfair gameplay, technical instability, or production failure.
This workflow focuses on preventing high-impact failures before they reach players.
</command_purpose>
```

## Role

**Principal QA / Risk Architect** with deep experience in Soulslike games, systemic gameplay, live-service failures, and player behavior analysis.

## Core Philosophy

> Not all bugs are equal.
>
> The most dangerous risks are the ones that look acceptable on paper but feel unfair, exhausting, or broken in the hands of real players.

## 1. Define Risk Analysis Scope (MANDATORY)

```xml
<risk_scope>#$ARGUMENTS</risk_scope>
```

```xml
<task_list>
- Identify scope type:
  - Combat mechanic
  - Boss / Enemy encounter
  - Level / Map
  - Progression system
  - Economy / Reward
  - UI / UX
  - Technical / Performance
  - Pipeline / Tooling

- Identify change nature:
  - New feature
  - Rework
  - Balance tweak
  - Optimization
  - Bug fix with side effects

- Identify lifecycle stage:
  - Prototype
  - Production
  - Beta
  - Live
</task_list>
```

⚠️ **DO NOT proceed until scope boundaries are explicit.**

## 2. Risk Taxonomy (Soulslike-Oriented)

```xml
<risk_categories>

### A. Gameplay Fairness Risk
- Unclear telegraphs
- Unavoidable damage
- Camera-caused deaths
- Input buffering inconsistencies
- Hitbox / hurtbox mismatch

### B. Difficulty & Fatigue Risk
- Difficulty spikes without learning
- Excessive punishment
- Long runbacks
- RNG stacking
- Resource starvation loops

### C. Player Psychology Risk
- Perceived unfairness
- Learned helplessness
- Rage-quit triggers
- Skill invalidation
- Build-lock frustration

### D. Exploit & Abuse Risk
- AI bait loops
- Sequence breaks
- Cheese strategies
- Co-op aggro abuse
- Status stacking abuse

### E. Technical & Stability Risk
- Frame drops affecting combat timing
- Animation desync
- State corruption
- Save/load inconsistencies
- Network edge cases (co-op / invasion)

### F. UX & Readability Risk
- Visual overload
- VFX hiding telegraphs
- Audio priority conflicts
- UI lag during combat
- Poor feedback on failure

### G. Production & Pipeline Risk
- Hard-to-test mechanics
- High iteration cost
- Designer-only knowledge
- Missing debug hooks
- No automated coverage

</risk_categories>
```

## 3. Parallel Risk Agents

```xml
<parallel_tasks>
Task fairness-risk-agent(risk_scope)
Task difficulty-risk-agent(risk_scope)
Task exploit-risk-agent(risk_scope)
Task technical-risk-agent(risk_scope)
Task player-psychology-agent(risk_scope)
Task production-risk-agent(risk_scope)
</parallel_tasks>
```

Each agent MUST think independently and assume:
- Players will min-max
- Players will fail repeatedly
- Players will share exploits online
- QA time is limited

## 4. Risk Identification Rules

```xml
<risk_identification_rules>

A risk MUST be logged if:
- It can cause player death without clear learning
- It invalidates player skill or preparation
- It scales badly with difficulty or NG+
- It interacts unpredictably with other systems
- It is hard to reproduce or debug

Even "working as designed" can be HIGH risk.

</risk_identification_rules>
```

## 5. Risk Scoring Model

```xml
<risk_scoring>

For EACH identified risk, score:

### Impact (1–5)
1 = Cosmetic annoyance  
3 = Noticeable frustration  
5 = Game-breaking or rage-quit

### Likelihood (1–5)
1 = Rare edge case  
3 = Common player path  
5 = Inevitable during normal play

### Detectability (1–5)
1 = Easy to detect in testing  
5 = Only appears after long play or specific builds

### Risk Score
Risk Score = Impact × Likelihood × Detectability

</risk_scoring>
```

## 6. Soulslike-Specific Risk Heuristics

```xml
<soulslike_heuristics>

Automatically escalate severity if:
- Risk involves boss encounters
- Risk affects player character death mechanic
- Risk multiplies in NG+ cycles
- Risk appears at high player investment moments
- Risk involves stamina / poise / i-frames
- Risk causes death during learning phase
- Risk stacks with camera issues
- Risk punishes exploration or experimentation

**Soulslike players tolerate difficulty. They do NOT tolerate unfairness.**

</soulslike_heuristics>
```

## 7. Risk Classification

```xml
<risk_levels>

- 🔴 Critical (Blocker)
  - Breaks fairness or core combat loop
  - High rage-quit probability

- 🟠 High
  - Severe frustration or exploit

- 🟡 Medium
  - Noticeable but manageable

- 🟢 Low
  - Edge case or polish

Any 🔴 Critical risk MUST be addressed or explicitly waived.

</risk_levels>
```

## 8. Risk Output Format

| Risk ID | Category | Description | Impact | Likelihood | Detectability | Score | Priority | Mitigation |
|---------|----------|-------------|--------|------------|---------------|-------|----------|------------|
| R001 | A | Hitbox too large on attack | 4 | 4 | 2 | 32 | High | Reduce hitbox by 20% |
| R002 | B | Death runback > 90 seconds | 3 | 5 | 1 | 15 | Medium | Add checkpoint or shortcut |
| R003 | D | Status stack exploit possible | 5 | 3 | 4 | 60 | Critical | Implement stacking cap |

## 9. Priority Tiers

| Score Range | Tier | Action |
|-------------|------|--------|
| 75-125 | 🔴 Critical | Block feature / Immediate fix |
| 40-74 | 🟠 High | Must fix before release |
| 20-39 | 🟡 Medium | Fix if time permits |
| 1-19 | 🟢 Low | Monitor / backlog |

## 10. Mitigation Strategy Definition

```xml
<mitigation_guidelines>

For EACH risk, define:
- Possible design mitigation
- Possible QA mitigation
- Possible tooling or automation
- What NOT to do (anti-solutions)

If mitigation is not possible, risk MUST be documented as accepted debt.

</mitigation_guidelines>
```

## 11. Artifact Output (MANDATORY)

```xml
<critical_requirement>

All risks MUST be written as markdown artifacts.
Verbal summaries are NOT acceptable.

</critical_requirement>
```

Each risk file MUST include:
- Risk ID
- System / Feature
- Risk Description
- Category
- Impact / Likelihood / Detectability
- Risk Score
- Player Impact Narrative
- Repro or Trigger Conditions
- Mitigation Options
- Owner Recommendation

Store under:
`qa-risks/<system-or-feature>/`

## 12. Final Risk Summary

After artifacts are created, provide:

### 📊 Risk Analysis Summary
- Total risks identified
- 🔴 Critical risks
- 🟠 High risks
- Systems with highest risk density
- Testing gaps identified


```xml
<final_warning>

If risks are not tracked, they WILL surface as player complaints.
QA exists to make failure boring and predictable — not surprising.

</final_warning>
```

## 13. Mitigation Strategy Template

```xml
<mitigation_template>

For each HIGH+ risk, provide:
- Root cause (technical or design)
- Proposed fix (short-term)
- Prevention mechanism (long-term)
- Detection method (monitoring, telemetry, test)

</mitigation_template>
```

## Workflow Integration

```
workflows:plan → workflows:risk-analyzer → workflows:compound
```

| Command | Purpose | Output |
|---------|---------|--------|
| `/workflows:risk-analyzer` | Deep risk analysis | Risk register, priority list |
| `/workflows:compound` | Documentation | risk-reports/*.md |

## XML Tag Reference

| Tag | Purpose |
|-----|---------|
| `<risk_scope>` | Define analysis boundaries |
| `<task_list>` | Pre-analysis checklist |
| `<risk_categories>` | Taxonomy of risk types |
| `<parallel_tasks>` | Multi-agent analysis |
| `<risk_identification_rules>` | Logging criteria |
| `<risk_scoring>` | Quantified assessment |
| `<risk_levels>` | Risk priority classification |
| `<soulslike_heuristics>` | Domain-specific escalations |
| `<mitigation_guidelines>` | Strategy definition rules |
| `<critical_requirement>` | Artifact output mandate |
| `<mitigation_template>` | Remediation framework |
| `<final_warning>` | Process closing statement |
