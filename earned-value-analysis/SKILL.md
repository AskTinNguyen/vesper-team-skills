---
name: earned-value-analysis
description: Perform Earned Value Management (EVM) following PMI standards. Use when measuring project performance, forecasting completion, analyzing variances, or reporting project health. Triggers on "earned value", "EVM", "SPI", "CPI", "variance analysis", "project forecast", "EAC", "ETC", "schedule performance", "cost performance", "are we on track", "project status", "budget forecast", "will we finish on time".
allowed-tools: [Read, Write, Bash, Grep]
preconditions:
  - WBS and work packages defined
  - Budget baseline established
  - Schedule baseline established
  - Progress data available (actual costs, % complete)
---

# Earned Value Analysis (EVM)

Measure project performance objectively using Earned Value Management. Compare planned vs. actual vs. earned to calculate variances, indices, and forecasts.

---

## When to Use This Skill

| Scenario | Use This Skill |
|----------|----------------|
| Monthly status reporting | ✅ Objective performance metrics |
| Sponsor steering committee | ✅ Variance analysis and forecasts |
| Project health check | ✅ SPI, CPI trend analysis |
| Forecasting completion | ✅ EAC, ETC calculations |
| Recovery planning | ✅ Identify where project is off track |
| Multi-project portfolio | ✅ Compare project performance |

---

## Core EVM Concepts

### The Three Key Values

| Term | Abbreviation | Definition | How to Calculate |
|------|--------------|------------|------------------|
| **Planned Value** | PV | Budgeted cost of work scheduled | Sum of budgets for work planned to be done |
| **Earned Value** | EV | Budgeted cost of work performed | Sum of budgets for work actually completed |
| **Actual Cost** | AC | Actual cost of work performed | Sum of actual costs incurred |

### Example

```
Work Package: "Database Design"
- Budget (PV): $10,000
- Planned: Complete by end of Month 2

End of Month 2 status:
- Planned (PV): $10,000 (should be done)
- Actual: 80% complete
- Earned (EV): $10,000 × 80% = $8,000
- Actual Cost (AC): $9,500 (spent so far)
```

---

## Earned Value Measurement Methods

EVM requires objective measurement of work completion. Select the appropriate method for each work package:

### 1. Fixed Formula Methods

**0/100 (Binary)**
- EV = 0% until work package is 100% complete
- Best for: Short work packages (< 2 weeks), discrete deliverables
- Conservative approach — no partial credit

**50/50**
- EV = 50% when work starts, 50% when complete
- Best for: Work packages of known duration
- Simple but can overstate early progress

**25/75**
- EV = 25% when work starts, 75% when complete
- Best for: Work with significant startup effort

**0/100 vs 50/50 Example:**
```
Work Package: "Database Schema Design" (BAC = $10,000)
Status: In progress, 3 of 5 days completed

0/100 Method:   EV = $0 (no credit until done)
50/50 Method:   EV = $5,000 (50% credit at start)
Actual %:       EV = $6,000 (if truly 60% complete)
```

### 2. Weighted Milestone Method

Break work package into milestones with predetermined EV weights.

```
Work Package: "API Development" (BAC = $20,000)

| Milestone | Weight | EV When Complete |
|-----------|--------|------------------|
| Design complete | 20% | $4,000 |
| Core endpoints | 40% | $8,000 |
| Authentication | 20% | $4,000 |
| Documentation | 10% | $2,000 |
| Testing complete | 10% | $2,000 |
| **Total** | 100% | $20,000 |

Current status: Design + Core complete
EV = $4,000 + $8,000 = $12,000 (60% of BAC)
```

### 3. Percent Complete (Objective)

Measure completion by countable units.

| Work Type | Measurement Method |
|-----------|-------------------|
| Code development | Function points completed / total |
| Document writing | Pages written / total pages |
| Construction | Units installed / total units |
| Testing | Test cases passed / total |
| Training | Modules delivered / total |

**Example:**
```
Work Package: "User Documentation" (BAC = $5,000)
Total pages: 50
Pages written: 35

EV = $5,000 × (35/50) = $5,000 × 70% = $3,500
```

### 4. Apportioned Effort

EV calculated based on parent activity completion.

| Activity | Relationship | Calculation |
|----------|--------------|-------------|
| Project Management | 10% of labor | EV = 10% of sum of all other work packages' EV |
| Quality Assurance | 15% of development | EV = 15% of development work package EV |
| Configuration Management | 5% of engineering | EV = 5% of engineering EV |

### 5. Level of Effort (LOE)

For ongoing support activities with no definable deliverables.

**Characteristics:**
- EV always equals PV (no variance)
- No schedule variance possible by definition
- AC still tracked for cost variance

**Best for:**
- Project management
- Ongoing support
- Maintenance activities
- Administrative work

### Measurement Method Selection Guide

| Work Package Type | Recommended Method | Rationale |
|-------------------|-------------------|-----------|
| Short tasks (< 2 weeks) | 0/100 | Avoids false progress |
| Design/development | Weighted milestones | Objective gates |
| Content creation | % complete (units) | Countable output |
| Testing | % complete (test cases) | Pass/fail criteria |
| Support/management | LOE or apportioned | No discrete deliverable |

### Critical Rule: Objectivity

**Never use:**
- Time elapsed (% of duration)
- Effort expended (% of hours worked)
- Subjective "gut feel"

**Always use:**
- Completed deliverables
- Passed inspections
- Approved milestones
- Countable units

---

## Performance Measurement Baseline (PMB)

The PMB is the integrated scope, schedule, and cost baseline against which performance is measured.

### PMB Components

```
┌─────────────────────────────────────────┐
│      PERFORMANCE MEASUREMENT BASELINE    │
├─────────────────────────────────────────┤
│  Scope Baseline                          │
│  ├── Project Scope Statement            │
│  ├── WBS                                │
│  └── WBS Dictionary                     │
├─────────────────────────────────────────┤
│  Schedule Baseline                       │
│  └── Approved project schedule          │
├─────────────────────────────────────────┤
│  Cost Baseline                           │
│  └── Time-phased budget (S-curve)       │
└─────────────────────────────────────────┘
            ↓
   Integrated baseline for EVM
```

### Baseline Changes

**Formal change control required for:**
- Scope baseline changes (CCB approval)
- Schedule baseline changes (sponsor approval)
- Cost baseline changes (finance + sponsor approval)

**Rebaselining triggers:**
- Authorized scope changes
- Approved recovery plans
- Major external changes (regulatory, market)

**Never rebaseline to hide variances.**

---

## Variance Analysis

### Schedule Variance (SV)

```
SV = EV - PV

Interpretation:
- SV > 0: Ahead of schedule
- SV = 0: On schedule
- SV < 0: Behind schedule

In example: $8,000 - $10,000 = -$2,000 (behind schedule)
```

### Cost Variance (CV)

```
CV = EV - AC

Interpretation:
- CV > 0: Under budget
- CV = 0: On budget
- CV < 0: Over budget

In example: $8,000 - $9,500 = -$1,500 (over budget)
```

### Variance Percentages

```
SV% = (SV / PV) × 100
CV% = (CV / EV) × 100

In example:
SV% = (-$2,000 / $10,000) × 100 = -20%
CV% = (-$1,500 / $8,000) × 100 = -18.75%
```

---

## Performance Indices

### Schedule Performance Index (SPI)

```
SPI = EV / PV

Interpretation:
- SPI > 1.0: Ahead of schedule (>100% efficiency)
- SPI = 1.0: On schedule
- SPI < 1.0: Behind schedule (<100% efficiency)

In example: $8,000 / $10,000 = 0.80
→ 80% schedule efficiency, 20% behind
```

### Cost Performance Index (CPI)

```
CPI = EV / AC

Interpretation:
- CPI > 1.0: Under budget (>100% efficiency)
- CPI = 1.0: On budget
- CPI < 1.0: Over budget (<100% efficiency)

In example: $8,000 / $9,500 = 0.84
→ 84% cost efficiency, spending $1.19 for every $1 of value
```

### To-Complete Performance Index (TCPI)

```
TCPI = (BAC - EV) / (BAC - AC)  [using original budget]
TCPI = (BAC - EV) / (EAC - AC)  [using revised forecast]

Interpretation:
- TCPI > 1.0: Must perform better than historical CPI
- TCPI = 1.0: Must maintain current CPI
- TCPI < 1.0: Can perform worse and still hit target

In example (BAC = $50,000, using EAC = $55,000):
($50,000 - $8,000) / ($55,000 - $9,500) = $42,000 / $45,500 = 0.92
→ Can perform at 92% efficiency and still hit revised target
```

---

## Forecasting

### Estimate at Completion (EAC)

Multiple formulas depending on situation:

| Formula | When to Use |
|---------|-------------|
| **EAC = BAC / CPI** | Current variances will continue (typical) |
| **EAC = AC + (BAC - EV)** | Original estimate was wrong, but future will be on plan |
| **EAC = AC + [(BAC - EV) / (CPI × SPI)]** | Both cost and schedule impact future work |
| **EAC = AC + New Estimate** | Bottom-up re-estimate of remaining work |

```
In example (BAC = $50,000, CPI = 0.84):
EAC = $50,000 / 0.84 = $59,524

If original budget wrong, future on track:
EAC = $9,500 + ($50,000 - $8,000) = $51,500
```

### Estimate to Complete (ETC)

```
ETC = EAC - AC

In example:
ETC = $59,524 - $9,500 = $50,024 (typical)
ETC = $51,500 - $9,500 = $42,000 (atypical)
```

### Variance at Completion (VAC)

```
VAC = BAC - EAC

Interpretation:
- VAC > 0: Project will be under budget
- VAC = 0: Project will be on budget
- VAC < 0: Project will be over budget

In example:
VAC = $50,000 - $59,524 = -$9,524 (over budget)
```

---

## EVM Analysis Report Template

```markdown
# Earned Value Analysis: [Project Name]

**Reporting Period:** [Start Date] - [End Date]  
**Data Date:** [Cutoff date]  
**Report Date:** YYYY-MM-DD  

---

## Executive Summary

| Metric | Value | Status |
|--------|-------|--------|
| Budget at Completion (BAC) | $XXX | — |
| Earned Value (EV) | $XXX | — |
| Planned Value (PV) | $XXX | — |
| Actual Cost (AC) | $XXX | — |
| **Schedule Performance** | **SPI = X.XX** | 🟢/🟡/🔴 |
| **Cost Performance** | **CPI = X.XX** | 🟢/🟡/🔴 |
| **Forecast (EAC)** | **$XXX** | vs. $XXX BAC |

**Status Legend:**
- 🟢 Healthy (≥ 0.95)
- 🟡 Watch (0.85 - 0.94)
- 🔴 At Risk (< 0.85)

---

## Project Health Dashboard

```
Schedule Performance
====================
PV: $XXX | EV: $XXX | AC: $XXX

Progress: [████████░░░░░░░░░░░░] XX%
          EV/BAC

SPI: 0.XX  [████░░░░░░░░░░░░░░] (Target: 1.0)

🟢 On Track  /  🟡 5-15% Behind  /  🔴 >15% Behind

Cost Performance
================
CPI: 0.XX  [████░░░░░░░░░░░░░░] (Target: 1.0)

Spending $X.XX for every $1.00 of value

🟢 Under Budget  /  🟡 5-15% Over  /  🔴 >15% Over

Forecast
========
BAC:   $XXX (Original Budget)
EAC:   $XXX (Forecast)
VAC:   $XXX (Variance at Completion)

Projected: 🟢 Under / 🟡 On / 🔴 Over Budget
```

---

## Detailed Analysis

### Schedule Variance Analysis

| Work Package | PV | EV | SV | SV% | Status |
|--------------|-----|-----|-----|------|--------|
| [WP-001] | $X | $X | $X | X% | 🟢/🟡/🔴 |
| [WP-002] | $X | $X | $X | X% | 🟢/🟡/🔴 |
| [WP-003] | $X | $X | $X | X% | 🟢/🟡/🔴 |

**Root Causes for Schedule Variance:**
1. [Reason 1]
2. [Reason 2]

**Corrective Actions:**
1. [Action 1]
2. [Action 2]

### Cost Variance Analysis

| Work Package | EV | AC | CV | CV% | CPI | Status |
|--------------|-----|-----|-----|------|-----|--------|
| [WP-001] | $X | $X | $X | X% | X.XX | 🟢/🟡/🔴 |
| [WP-002] | $X | $X | $X | X% | X.XX | 🟢/🟡/🔴 |
| [WP-003] | $X | $X | $X | X% | X.XX | 🟢/🟡/🔴 |

**Root Causes for Cost Variance:**
1. [Reason 1]
2. [Reason 2]

**Corrective Actions:**
1. [Action 1]
2. [Action 2]

---

## Forecasting

### Current Trajectory

| Scenario | Formula | EAC | VAC |
|----------|---------|-----|-----|
| Typical (variances continue) | BAC / CPI | $XXX | $XXX |
| Atypical (future on plan) | AC + (BAC - EV) | $XXX | $XXX |
| Combined impact | AC + [(BAC - EV) / (CPI × SPI)] | $XXX | $XXX |

### Required Performance

| Target | TCPI | Assessment |
|--------|------|------------|
| Finish at BAC | X.XX | [Achievable/Challenging/Impossible] |
| Finish at EAC | X.XX | [Achievable/Challenging/Impossible] |

**TCPI Interpretation:**
- Must perform at X% efficiency to hit target
- Historical CPI: X.XX
- Gap: [achievable or not]

---

## Trend Analysis

### SPI Trend

| Period | SPI | Trend |
|--------|-----|-------|
| Month 1 | 1.05 | 🟢 |
| Month 2 | 0.98 | 🟢 |
| Month 3 | 0.92 | 🟡 |
| Month 4 | 0.85 | 🔴 |
| **Current** | **0.80** | 🔴 ↓ |

**Trend:** Declining schedule performance

### CPI Trend

| Period | CPI | Trend |
|--------|-----|-------|
| Month 1 | 1.02 | 🟢 |
| Month 2 | 0.95 | 🟡 |
| Month 3 | 0.90 | 🟡 |
| Month 4 | 0.88 | 🔴 |
| **Current** | **0.84** | 🔴 ↓ |

**Trend:** Declining cost performance

### Conclusion
Both SPI and CPI declining — project requires intervention.

---

## Work Package Detail

### Control Account: [Name]

| WP | Description | BAC | PV | EV | AC | SPI | CPI | Status |
|----|-------------|-----|-----|-----|-----|-----|-----|--------|
| 1.1 | [Desc] | $X | $X | $X | $X | X.XX | X.XX | 🟢/🟡/🔴 |
| 1.2 | [Desc] | $X | $X | $X | $X | X.XX | X.XX | 🟢/🟡/🔴 |

---

## Recommendations

### Immediate Actions (This Week)
1. [Action 1]
2. [Action 2]

### Short-Term Actions (This Month)
1. [Action 1]
2. [Action 2]

### Strategic Decisions
1. [Decision 1 with options]
2. [Decision 2 with options]

---

## Appendix

### Data Sources
- Cost data from: [Source]
- Schedule data from: [Source]
- % complete reported by: [Source]

### Assumptions
- [Assumption 1]
- [Assumption 2]

### Changes from Last Report
- [Change 1]
- [Change 2]
```

---

## Worked Example

```markdown
# EVM Analysis: Website Redesign Project

## Data

| Work Package | BAC | Planned % | Actual % | Actual Cost |
|--------------|-----|-----------|----------|-------------|
| Requirements | $10,000 | 100% | 100% | $10,500 |
| Design | $20,000 | 100% | 90% | $18,000 |
| Development | $50,000 | 60% | 40% | $22,000 |
| Testing | $15,000 | 0% | 0% | $0 |
| Deployment | $5,000 | 0% | 0% | $0 |
| **Total** | **$100,000** | — | — | **$50,500** |

## Calculations

### Planned Value (PV)
= ($10,000 × 100%) + ($20,000 × 100%) + ($50,000 × 60%) + ($15,000 × 0%) + ($5,000 × 0%)
= $10,000 + $20,000 + $30,000 + $0 + $0
= $60,000

### Earned Value (EV)
= ($10,000 × 100%) + ($20,000 × 90%) + ($50,000 × 40%) + ($15,000 × 0%) + ($5,000 × 0%)
= $10,000 + $18,000 + $20,000 + $0 + $0
= $48,000

### Actual Cost (AC)
= $10,500 + $18,000 + $22,000 + $0 + $0
= $50,500

## Variances

| Metric | Calculation | Result | Status |
|--------|-------------|--------|--------|
| SV | $48K - $60K | -$12,000 | 🔴 Behind |
| CV | $48K - $50.5K | -$2,500 | 🔴 Over |
| SPI | $48K / $60K | 0.80 | 🔴 |
| CPI | $48K / $50.5K | 0.95 | 🟡 |

## Forecasts

| Method | Calculation | EAC | VAC |
|--------|-------------|-----|-----|
| Typical | $100K / 0.95 | $105,263 | -$5,263 |
| Atypical | $50.5K + ($100K - $48K) | $102,500 | -$2,500 |

TCPI to hit BAC: ($100K - $48K) / ($100K - $50.5K) = 1.05
→ Must improve to 105% efficiency (challenging but possible)

## Analysis

**Problem Areas:**
1. Development: Only 40% complete vs 60% planned (SPI = 0.67)
2. Design: 90% complete but cost overrun (CPI = 0.90)

**Root Causes:**
1. Development delayed by requirements changes
2. Design iterations exceeded budget

**Actions:**
1. Freeze requirements for development phase
2. Implement change control for future changes
3. Daily standups for development to accelerate
```

---

## EVM Calculation Worksheet

Use this worksheet to collect data before analysis:

```markdown
## Data Collection

### Project Info
- Project Name: _______________
- Reporting Date: _______________
- Budget at Completion (BAC): $_______________

### Work Package Status

| WP # | Description | BAC | Planned % | Actual % | Actual Cost |
|------|-------------|-----|-----------|----------|-------------|
| | | | | | |
| | | | | | |
| | | | | | |

### Calculations

**Planned Value (PV)** =
**Earned Value (EV)** =
**Actual Cost (AC)** =

**Schedule Variance (SV)** = EV - PV = ________
**Cost Variance (CV)** = EV - AC = ________

**SPI** = EV / PV = ________
**CPI** = EV / AC = ________

**EAC (Typical)** = BAC / CPI = ________
**EAC (Atypical)** = AC + (BAC - EV) = ________
**ETC** = EAC - AC = ________
**VAC** = BAC - EAC = ________

**TCPI (to BAC)** = (BAC - EV) / (BAC - AC) = ________
**TCPI (to EAC)** = (BAC - EV) / (EAC - AC) = ________
```

---

## Tips for EVM Success

### DO ✅
- Establish baselines before measuring (PV needs a plan)
- Measure % complete objectively using defined measurement methods
- Report trends, not just point-in-time
- Investigate variances (thresholds are organizational — typically ±10%)
- Update forecasts regularly
- Tie EVM to WBS work packages
- Use formal change control for rebaselining

### Avoid ❌
- Using EVM without a Performance Measurement Baseline
- Estimating % complete subjectively — use weighted milestones or units completed
- Ignoring small variances early — they compound over time
- Restricting reports to management only — share with the team
- Calculating EVM manually for large projects — use tools
- Rebaselining to hide variances — use only for approved changes

---

## Related Skills

| Skill | Relationship |
|-------|--------------|
| `project-charter` | Provides BAC, success criteria |
| `wbs-creator` | Provides work package structure for measurement |
| `risk-register` | Performance variances generate new risks |
| `dispatch` | Assign corrective actions as tasks |

---

*"What gets measured gets managed. EVM gives you the objective data to manage with confidence."* — PMI
