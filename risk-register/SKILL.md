---
name: risk-register
description: Create and maintain a Risk Register following PMI Risk Management standards. Use when identifying project risks, analyzing probability/impact, planning responses, or monitoring risks throughout the project lifecycle. Triggers on "risk register", "identify risks", "risk analysis", "risk management", "probability impact", "risk response", "risk assessment", "what could go wrong", "project worries", "contingency planning".
allowed-tools: [Read, Write, Bash, Grep]
preconditions:
  - Project Charter approved
  - WBS or scope defined
  - Stakeholders available for risk identification
---

# Risk Register

Systematic identification, analysis, and response planning for project risks. Following PMI standards: identify → analyze (qualitative/quantitative) → plan responses → monitor.

---

## When to Use This Skill

| Scenario | Use This Skill |
|----------|----------------|
| Starting project planning | ✅ Identify initial risks |
| WBS completed | ✅ Analyze risks per work package |
| Regular risk reviews | ✅ Update and monitor risks |
| Before major decisions | ✅ Assess risk impact |
| Issues becoming risks | ✅ Escalate to register |
| Project changes | ✅ Reassess risk exposure |

---

## Risk Management Process

### Process Groups

```
1. Plan Risk Management → Define approach, methodology, thresholds
2. Identify Risks → What could go wrong/right?
3. Perform Qualitative Analysis → Probability × Impact ranking
4. Perform Quantitative Analysis → Numerical analysis (optional)
5. Plan Risk Responses → What to do about each risk
6. Implement Risk Responses → Execute plans
7. Monitor Risks → Track, review, report
```

---

## Risk Identification Techniques

### 1. Documentation Reviews
Review project documents (charter, WBS, assumptions) for risks.

### 2. Information Gathering
- **Brainstorming:** Team session to identify risks
- **Delphi Technique:** Expert input anonymously
- **Interviews:** Stakeholder one-on-ones
- **Root Cause Analysis:** Dig into problems to find risks

### 3. Checklist Analysis
Use categories to ensure comprehensive coverage:

| Category | Prompts |
|----------|---------|
| **Technical** | New technology, complexity, integration |
| **External** | Vendors, regulations, market, weather |
| **Organizational** | Resources, funding, priorities, politics |
| **Project Management** | Planning, control, communication |
| **Human** | Skills, availability, conflict, turnover |

### 4. Assumptions Analysis
Every assumption carries risk — validate or track.

### 5. SWOT Analysis
- **S**trengths → Exploit
- **W**eaknesses → Mitigate
- **O**pportunities → Enhance
- **T**hreats → Mitigate/Transfer/Avoid

---

## Risk Register Structure

### Master Risk Register

```markdown
# Risk Register: [Project Name]

**Version:** 1.0  
**Date:** YYYY-MM-DD  
**Status:** Draft / Active / Closed  
**Next Review:** [Date]  

---

## Risk Summary

| Metric | Count |
|--------|-------|
| Total Risks | X |
| High Priority | X |
| Medium Priority | X |
| Low Priority | X |
| Active | X |
| Mitigated | X |
| Realized (Issues) | X |

---

## Risk Matrix (Heat Map)

```
              IMPACT
         1      2      3      4      5
        Low   Low    Med    High   Critical
       ┌─────┬─────┬─────┬─────┬─────┐
   5   │  5  │ 10  │ 15  │ 20  │ 25  │ ← Almost Certain
   4   │  4  │  8  │ 12  │ 16  │ 20  │ ← Likely
P  3   │  3  │  6  │  9  │ 12  │ 15  │ ← Possible
R  2   │  2  │  4  │  6  │  8  │ 10  │ ← Unlikely
O  1   │  1  │  2  │  3  │  4  │  5  │ ← Rare
B      └─────┴─────┴─────┴─────┴─────┘

Score = Probability × Impact (max 5 × 5 = 25)

Priority Levels:
┌───────────┬──────────┬─────────────────────────┐
│ Score     │ Priority │ Action                  │
├───────────┼──────────┼─────────────────────────┤
│ 20-25     │ Critical │ Immediate action,       │
│           │          │ escalate to sponsor     │
├───────────┼──────────┼─────────────────────────┤
│ 12-16     │ High     │ Active management,      │
│           │          │ dedicated owner         │
├───────────┼──────────┼─────────────────────────┤
│ 6-9       │ Medium   │ Plan response,          │
│           │          │ monitor regularly       │
├───────────┼──────────┼─────────────────────────┤
│ 1-4       │ Low      │ Accept and monitor      │
└───────────┴──────────┴─────────────────────────┘
```

---

## Detailed Risk Entries

### R001: [Risk Title]

| Field | Value |
|-------|-------|
| **Risk ID** | R001 |
| **Date Identified** | YYYY-MM-DD |
| **Category** | Technical / External / Organizational / PM |
| **Risk Statement** | [If X occurs, then Y impact on project objective] |
| **Root Cause** | [Why might this happen?] |
| **Triggers** | [Early warning signs] |

#### Qualitative Analysis

| Factor | Rating | Score |
|--------|--------|-------|
| Probability | High/Med/Low | [1-5] |
| Impact (Schedule) | High/Med/Low | [1-5] |
| Impact (Cost) | High/Med/Low | [1-5] |
| Impact (Quality) | High/Med/Low | [1-5] |
| **Risk Score** | | **[P × max(I)]** |
| **Priority** | | **High/Med/Low** |

**Urgency:** Immediate / Soon / Can wait

#### Response Strategy

| Element | Value |
|---------|-------|
| **Strategy** | Avoid / Transfer / Mitigate / Accept / Exploit / Enhance / Share |
| **Response Actions** | [Specific steps to take] |
| **Owner** | [Who is responsible] |
| **Contingency Plan** | [If risk occurs, do this] |
| **Fallback Plan** | [If contingency fails] |
| **Budget Reserve** | $X (contingency) |
| **Schedule Reserve** | X days |

#### Status Tracking

| Date | Status | Notes | Updated By |
|------|--------|-------|------------|
| YYYY-MM-DD | Active | Initial identification | [Name] |
| YYYY-MM-DD | Mitigated | [Actions taken] | [Name] |

---

### R002: [Next Risk...]
[Same structure]
```

---

## Risk Scoring Matrix

### Probability Scale

| Score | Probability | Description |
|-------|-------------|-------------|
| 5 | >80% | Almost certain |
| 4 | 60-80% | Likely |
| 3 | 40-60% | Possible |
| 2 | 20-40% | Unlikely |
| 1 | <20% | Rare |

### Impact Scale

| Score | Cost Impact | Schedule Impact | Quality Impact |
|-------|-------------|-----------------|----------------|
| 5 | >20% budget | >2 months | Unusable deliverable |
| 4 | 10-20% budget | 1-2 months | Major quality issues |
| 3 | 5-10% budget | 2-4 weeks | Moderate issues |
| 2 | 1-5% budget | 1-2 weeks | Minor issues |
| 1 | <1% budget | <1 week | Negligible impact |

### Risk Score Calculation

```
Risk Score = Probability × Impact

Where Impact = maximum of (Cost, Schedule, Quality)
```

| Score Range | Priority | Action Required |
|-------------|----------|-----------------|
| 15-25 | Critical | Immediate action, escalate to sponsor |
| 10-14 | High | Active management, dedicated owner |
| 5-9 | Medium | Plan response, monitor regularly |
| 1-4 | Low | Accept and monitor |

---

## Response Strategies

### For Threats (Negative Risks)

| Strategy | When to Use | Example |
|----------|-------------|---------|
| **Avoid** | High impact, can eliminate | Change scope to remove risky feature |
| **Transfer** | Impact too high to bear | Insurance, outsourcing, warranties |
| **Mitigate** | Reduce probability/impact | Prototyping, training, redundancy |
| **Accept** | Low impact or no viable response | Acknowledge and monitor |

### For Opportunities (Positive Risks)

| Strategy | When to Use | Example |
|----------|-------------|---------|
| **Exploit** | High value opportunity | Assign best resources |
| **Share** | Need partner to realize | Joint venture, partnership |
| **Enhance** | Increase probability | Add resources, prioritize |
| **Accept** | Can't or won't actively pursue | Monitor for changes |

### Contingency vs. Fallback

| Plan | Purpose | Trigger |
|------|---------|---------|
| **Contingency** | Primary response if risk occurs | Risk trigger event |
| **Fallback** | Backup if contingency fails | Contingency plan fails |

---

## Risk Register Example

```markdown
# Risk Register: CRM Modernization Project

## R001: Data Migration Corruption

| Field | Value |
|-------|-------|
| **Risk ID** | R001 |
| **Category** | Technical |
| **Statement** | If legacy data contains corrupted records, migration may fail causing project delay and data loss |
| **Root Cause** | 15-year-old database with no validation rules |
| **Triggers** | Migration test failures, data validation errors |

**Analysis:**
- Probability: 4 (Likely — old data is messy)
- Impact: 5 (Critical — data loss unacceptable)
- **Risk Score: 20 (Critical)**

**Response:**
- Strategy: Mitigate
- Actions: 
  1. Data profiling before migration
  2. Automated validation scripts
  3. Staged migration with verification
- Owner: Data Architect
- Contingency: Manual data correction budget ($25K)
- Fallback: Extended migration timeline (+2 weeks)

---

## R002: Key Vendor Delays

| Field | Value |
|-------|-------|
| **Risk ID** | R002 |
| **Category** | External |
| **Statement** | If implementation vendor misses deadlines, project completion delayed |
| **Triggers** | Missed milestone, communication gaps |

**Analysis:**
- Probability: 3 (Possible)
- Impact: 4 (High — 1-2 month delay)
- **Risk Score: 12 (High)**

**Response:**
- Strategy: Mitigate + Transfer
- Actions:
  1. Penalty clauses in contract
  2. Weekly checkpoint meetings
  3. Identify backup vendor
- Owner: Project Manager
- Contingency: Switch to backup vendor (2-week transition)

---

## R003: User Adoption Resistance

| Field | Value |
|-------|-------|
| **Risk ID** | R003 |
| **Category** | Organizational |
| **Statement** | If users resist new system, ROI not realized |
| **Triggers** | Low training attendance, negative feedback |

**Analysis:**
- Probability: 4 (Likely — change is hard)
- Impact: 3 (Moderate — efficiency gains delayed)
- **Risk Score: 12 (High)**

**Response:**
- Strategy: Mitigate
- Actions:
  1. Change management plan
  2. Champion network
  3. Early involvement in design
  4. Comprehensive training
- Owner: Change Manager
- Contingency: Additional training budget ($15K)
```

---

## Post-Response Risk Analysis

### Residual Risk
The risk that **remains after** implementing the planned response strategy.

| Original Risk | Response | Residual Risk |
|--------------|----------|---------------|
| Vendor bankruptcy | Select established vendor + contract penalties | Vendor acquisition causing service disruption |
| Key person departure | Cross-training + documentation | Temporary productivity loss during transition |
| Data loss | Automated backups + redundancy | Small data gap between last backup and incident |

**Action:** Document residual risks and accept or develop secondary responses.

### Secondary Risk
A **new risk created** by implementing a risk response.

| Response | Secondary Risk |
|----------|----------------|
| Adding redundant server | Increased complexity, higher maintenance cost |
| Accelerating schedule | Team burnout, quality issues |
| Outsourcing development | Communication gaps, IP concerns |
| Using new technology | Learning curve, unknown limitations |

**Action:** Identify secondary risks during response planning and include in register.

### Risk Closure Criteria

A risk can be closed when:
- [ ] Response strategy fully implemented
- [ ] Residual risk accepted or transferred
- [ ] Secondary risks identified and planned
- [ ] Risk no longer relevant (external change)
- [ ] Risk realized and converted to issue

---

## Risk Review Cadence

| Project Phase | Review Frequency | Participants |
|--------------|-------------------|--------------|
| Planning | Weekly during planning | Core team |
| Execution | Bi-weekly | Core team + stakeholders |
| Critical periods | Daily/weekly | Relevant owners |
| Near milestones | Before go/no-go | Sponsor + team |
| Closure | Final risk review | Lessons learned |

### Risk Review Agenda

1. **Status Update** — Review active risks
2. **New Risks** — Identify any new risks
3. **Trigger Monitoring** — Check early warning signs
4. **Realized Risks** — Issues requiring immediate action
5. **Mitigation Effectiveness** — Are responses working?
6. **Reserve Analysis** — Contingency fund status
7. **Close/Aggregate** — Close mitigated risks

---

## Risk-Adjusted Planning

### Reserve Analysis

| Reserve Type | Purpose | Calculation |
|--------------|---------|-------------|
| **Contingency Reserve** | Known unknowns (identified risks) | Sum of contingency amounts |
| **Management Reserve** | Unknown unknowns (unidentified) | 5-10% of total budget |

### Expected Monetary Value (EMV)

```
EMV = Probability × Impact

Example:
Risk A: 30% × $100K = $30K EMV
Risk B: 20% × $50K = $10K EMV
Risk C: 10% × $200K = $20K EMV

Total Risk Exposure = $60K
→ Contingency reserve should cover ~60-80% of this
```

---

## Output Files

Create these artifacts:

1. **Risk Register:** `docs/planning/[project]-risk-register.md`
2. **Risk Report:** Status reports to stakeholders
3. **Watch List:** Low-priority risks to monitor

---

## Tips for Great Risk Management

### DO ✅
- Identify risks early and often
- Involve the whole team — diverse perspectives catch more
- Focus on risks with high impact, not just high probability
- Assign specific owners, not "the team"
- Create specific responses, not "be careful"
- Monitor triggers, not just the risk
- Review regularly — risks change

### DON'T ❌
- Skip opportunities (positive risks)
- Confuse issues with risks (risks = future, issues = now)
- Create generic responses
- Set and forget — risk management is continuous
- Ignore low probability/high impact risks (black swans)
- Over-analyze — 80% of value comes from action

---

## Related Skills

| Skill | Relationship |
|-------|--------------|
| `project-charter` | Input — high-level risks from charter |
| `wbs-creator` | Context — risks by work package |
| `earned-value-analysis` | Input — performance risks from variances |
| `dispatch` | Execution — assign risk response tasks |

---

*"Risk management is not about avoiding risk — it's about making informed decisions with eyes wide open."* — PMI
