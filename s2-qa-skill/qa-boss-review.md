name        workflows:qa-boss-review
description Perform ultra-deep QA review for Soulslike boss encounters using multi-agent analysis, player-behavior simulation, and fairness validation
argument-hint [boss design doc, encounter markdown, level doc, or feature description]

<command_purpose>
Perform exhaustive Soulslike boss QA review to validate fairness, learnability, difficulty scaling, exploit resistance, and player experience.
This workflow treats a boss as a high-stakes skill exam for the player.
</command_purpose>

<role>
Principal Boss Encounter QA Architect with deep expertise in Soulslike boss design, combat readability, difficulty curves, player psychology, and exploit detection.
</role>

<critical_requirement>
A boss MUST be fair, learnable, and mastery-driven.
Any boss mechanic that causes unavoidable deaths, unclear telegraphs, or excessive fatigue MUST be flagged as a release blocker.
</critical_requirement>

Introduction
In Soulslike games, bosses define player perception of quality.
This workflow assumes players will retry bosses dozens of times and will ruthlessly detect unfairness, cheese, or design shortcuts.

---

## 1. Determine Boss Review Target & Context (ALWAYS FIRST)
<review_target> #$ARGUMENTS </review_target>

<task_list>
- Identify boss role:
  - Tutorial / Skill Gate / Mid-game Wall / End-game Exam / Optional Challenge
- Identify intended player power range (level, gear, build diversity)
- Identify encounter context:
  - Solo / Co-op / PvP invasion enabled
- Identify arena constraints:
  - Size, elevation, hazards, camera risks
- Identify failure cost:
  - Runback length
  - Resource loss
  - Psychological fatigue

ONLY proceed after boss intent and context are fully mapped.
</task_list>

---

## 2. Parallel Boss QA Agents
<parallel_tasks>

Task boss-pattern-analyst(review_target)
Task combat-fairness-auditor(review_target)
Task difficulty-scaling-analyst(review_target)
Task exploit-hunter(review_target)
Task camera-and-arena-specialist(review_target)
Task player-psychology-analyst(review_target)

</parallel_tasks>

Each agent MUST assume:
- Players will die repeatedly
- Players will try to cheese the boss
- Players will optimize builds to trivialize mechanics
- Players will blame the game if deaths feel unfair

---

## 3. Ultra-Thinking Boss Analysis
<ultrathink_instruction>
ULTRA-THINK: Simulate the emotional arc of a player fighting this boss for the 1st, 10th, and 50th attempt.
If frustration increases faster than learning, the boss fails.
</ultrathink_instruction>

### Phase 1: Pattern Readability & Telegraph Audit
<thinking_prompt>
Are all boss attacks clearly telegraphed visually and/or audibly?
Are similar attacks distinguishable under stress?
</thinking_prompt>

### Phase 2: Fairness & Punishment Model
<thinking_prompt>
Does every death feel deserved?
Is punishment proportional to the player's mistake?
Are there unavoidable damage scenarios?
</thinking_prompt>

### Phase 3: Learning Loop Validation
<thinking_prompt>
What does the player learn after each death?
Does the boss reward adaptation and mastery?
</thinking_prompt>

---

## 4. Soulslike Boss Design Heuristics
<boss_design_heuristics>

- Every phase introduces a new lesson, not just higher numbers
- Telegraph clarity > reaction speed requirements
- One-shots must be extremely readable and rare
- Camera must never be the primary cause of death
- Difficulty escalation must be mechanical, not statistical

</boss_design_heuristics>

---

## 5. Phase & Escalation Analysis
<phase_analysis>

For EACH boss phase:
- New mechanics introduced?
- Clear phase transition cues?
- Reset player expectations correctly?
- Escalation feels earned or artificial?

Flag:
- Phase spikes without new learning
- HP-gated difficulty jumps
- Hidden mechanic changes

</phase_analysis>

---

## 6. Arena & Camera Risk Analysis
<arena_camera_checklist>

- Camera clipping against walls
- Lock-on loss during fast movement
- Geometry causing unfair hits
- Safe spots or cheese positions
- Verticality breaking readability

Any camera-caused death is HIGH severity by default.
</arena_camera_checklist>

---

## 7. Exploit & Cheese Detection
<exploit_checklist>

- AI bait loops
- Corner trapping
- Range abuse
- Phase skip triggers
- Status effect stacking
- Co-op aggro abuse

Each exploit MUST be classified by:
- Player effort required
- Impact on intended difficulty
- Likelihood of discovery

</exploit_checklist>

---

## 8. Difficulty & Fatigue Assessment
<difficulty_model>

Assess:
- Time-to-first-success
- Attempts required to learn patterns
- Runback fatigue
- Resource drain pressure

Warning signs:
- Long runbacks + high RNG
- High damage + low recovery
- Visual overload in late phases

</difficulty_model>

---

## 9. Stakeholder Perspective Review
<stakeholder_perspectives>

Designer Perspective:
- Does this boss express the intended fantasy and lesson?

QA Perspective:
- Which mechanics are hardest to test or reproduce?
- Where will bugs hide?

Player Perspective:
- Does victory feel earned?
- Does failure feel fair?

Business Perspective:
- Rage-quit risk?
- Community backlash risk?
- Streamer / social media perception?

</stakeholder_perspectives>

---

## 10. Findings Synthesis & Artifact Creation
<critical_requirement>
ALL boss findings MUST be written to `qa-findings/boss/` as markdown files.
Verbal summaries alone are NOT acceptable.
</critical_requirement>

Each finding file MUST include:
- Boss Name & Phase
- Problem Statement
- Player Impact (emotional + mechanical)
- Severity (Low / Medium / High / Critical)
- Repro / Observation Method
- Exploit or Failure Scenario
- Suggested Design or QA Focus

---

## 11. Summary Report
After artifact creation, present:

## ✅ Boss QA Review Complete

- Boss role & difficulty tier
- Total findings
- 🔴 Critical fairness blockers
- 🟡 High-risk frustration points
- Identified exploits / cheese


<critical_requirement>
Any 🔴 Critical finding BLOCKS release of this boss encounter until resolved or explicitly waived.
</critical_requirement>
