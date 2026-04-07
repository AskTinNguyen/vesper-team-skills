# qa-performance-analyzer

## Overview

Perform exhaustive performance analysis using metric-driven reasoning, risk scoring, and QA verdict synthesis.

| name | description | argument-hint |
|------|-------------|---------------|
| workflows:performance-analyzer | Perform exhaustive performance analysis using metric-driven reasoning, risk scoring, and QA verdict synthesis | [Performance report image(s), CSV/JSON metrics, markdown table, or latest run] |

## Review Command

```xml
<command_purpose>
Perform exhaustive performance analysis on game builds using FPS metrics (Avg / 1% Low / Min / Max),
identify regressions, stability risks, and release readiness with QA-grade verdicts.
</command_purpose>
```

## Introduction

Senior Performance & QA Architect with deep expertise in:
- Frame-time analysis
- FPS stability diagnostics
- Game performance regression detection
- Release risk assessment (Go / No-Go)

This workflow is designed to:
- Replace subjective performance comments
- Enforce metric-driven judgments
- Produce consistent, explainable QA verdicts

## Prerequisites

- Performance input in ONE of the following forms:
  - Screenshot(s) of FPS report (CapFrameX, PresentMon, in-game HUD)
  - Structured table (Markdown / CSV / JSON)
  - Text dump of metrics (Avg FPS, 1% Low, Min, Max)
- At least ONE comparison baseline (Previous build)
- Same test condition (map, camera path, duration, hardware)

## Main Tasks

### 1. Determine Analysis Target & Data Validity (ALWAYS FIRST)

```xml
<analysis_target> #$ARGUMENTS </analysis_target>
```

**Immediate Actions:**

```xml
<task_list>

1. Identify input type:
   - Image-based report
   - Structured table
   - Raw text metrics

2. Validate metric completeness:
   - Avg FPS
   - 1% Low FPS
   - Min FPS
   - Max FPS

3. Detect comparison scope:
   - Latest vs Previous 1
   - Latest vs Previous N
   - Latest only (baseline missing)

4. Verify test parity:
   - Same location/map
   - Same camera path / duration
   - Same hardware & settings

5. If any validation fails:
   - Mark analysis as ⚠️ PARTIAL
   - Downgrade confidence level

⚠️ DO NOT proceed to verdict until data is validated.

</task_list>
```

### 2. Metric Normalization & Delta Calculation

```xml
<analysis_rules>

For EACH metric, compute:
Δ = Latest − Previous

Attach direction:
- ↑ Increase (positive delta)
- ↓ Decrease (negative delta)

Format standard:
↑ +X.X
↓ −X.X

Metrics:
- Avg FPS      → Overall throughput
- 1% Low FPS   → Frame-time stability (HIGHEST PRIORITY)
- Min FPS      → Spike / hitch severity
- Max FPS      → Peak rendering capacity (LOW PRIORITY)

</analysis_rules>
```

### 3. Weighted Importance Model (CRITICAL)

```xml
<weight_model>

Metric Weights:
- 1% Low FPS : 40% (Primary stability indicator)
- Avg FPS   : 30% (Overall smoothness)
- Min FPS   : 20% (Spike risk / hitch detection)
- Max FPS   : 10% (Non-blocking, cosmetic)

Interpretation Rules:
- Any drop in 1% Low > 10% → AUTOMATIC STABILITY WARNING
- Min FPS ≤ 1–2 → Spike risk exists even if Avg FPS improves
- Max FPS improvement NEVER offsets 1% Low degradation

</weight_model>
```

### 4. Risk Classification Logic

```xml
<risk_rules>

🔴 HIGH RISK (P1)
- 1% Low ↓ ≥ 15%
- Avg FPS ↓ ≥ 20%
- Min FPS ≤ 1 AND worse than previous
→ Release Blocker

🟡 MEDIUM RISK (P2)
- Avg FPS ↓ 5–15%
- 1% Low ↓ 5–15%
- Conflicting signals (Avg ↑ but 1% Low ↓)
→ Needs investigation / optimization

🟢 LOW RISK (P3)
- Avg FPS ↑
- 1% Low ↑ or stable
- Min FPS stable or improved
→ Safe / Improved

</risk_rules>
```

### 5. Automated QA Verdict Synthesis

```xml
<verdict_logic>

Verdict MUST be derived, not opinionated.

Verdict Mapping:
- 🟢 IMPROVED
  Stability ↑, gameplay smoother than previous

- 🟡 UNSTABLE / MIXED
  Performance signals conflict, risk exists

- 🔴 REGRESSION
  Clear degradation in stability or smoothness

Each verdict MUST include:
- 1 short reason tied to metrics
- Comparison explicitly stated (vs which build)

</verdict_logic>
```

### 6. Output Contract (MANDATORY FORMAT)

```xml
<output_format>

Table columns (STRICT):

| Date | Location | Build | Avg FPS | 1% Low FPS | Min FPS | Max FPS | Mức thay đổi | Nhận xét |

Rules:
- "Mức thay đổi" MUST list deltas for:
  Avg / 1% Low / Min / Max
- Use arrows ↑ ↓ with signed numbers
- "Nhận xét" MUST be 1 concise QA sentence
- Latest row contains verdict
- Previous row contains raw reference only

</output_format>
```

### 7. Scenario & Edge Case Reasoning

```xml
<thinking_prompt>
ULTRA-THINK: What could go wrong even if Avg FPS looks fine?
</thinking_prompt>

<scenario_checklist>

- Avg ↑ but 1% Low ↓ → Micro-stutter risk
- Min FPS extremely low → Streaming / GC / shader hitch
- Max FPS ↑ only → GPU unlocked but gameplay unchanged
- Large variance between runs → Non-deterministic performance

</scenario_checklist>
```

### 8. Release Gate Recommendation

```xml
<release_gate>

Based on risk level:
- 🔴 P1 → ❌ NO-GO (block release)
- 🟡 P2 → ⚠️ CONDITIONAL GO (fix or monitor)
- 🟢 P3 → ✅ GO

Always state:
"Release recommendation based on Latest vs Previous build."

</release_gate>
```

### 9. Confidence Scoring (Optional but Recommended)

```xml
<confidence_model>

Confidence Level:
- High: clean data, same conditions, clear deltas
- Medium: minor inconsistencies
- Low: partial data / missing baseline

</confidence_model>
```

## Workflow Pipeline

```
workflows:plan → workflows:performance-analyzer → workflows:compound
```

| Command | Purpose | Artifacts |
|---------|---------|-----------|
| `/workflows:performance-analyzer` | FPS & stability analysis | tables, verdicts |
| `/workflows:compound` | Long-term perf documentation | reports/*.md |

## XML Tag Reference

| Tag | Purpose |
|-----|---------|
| `<analysis_target>` | Capture input metrics |
| `<task_list>` | Mandatory preprocessing |
| `<weight_model>` | Prevent wrong conclusions |
| `<risk_rules>` | Objective risk grading |
| `<verdict_logic>` | Enforced QA judgment |
| `<output_format>` | UI / report contract |
