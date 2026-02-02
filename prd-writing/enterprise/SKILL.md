---
name: prd-enterprise
description: "Generate enterprise-grade Product Requirements Documents (PRD) using strategic product management frameworks, risk analysis, and stakeholder alignment methodologies. Use when planning complex features, enterprise products, AI/ML features, or when executive-level documentation is required. Triggers on: enterprise prd, strategic product doc, comprehensive requirements, big-four style prd, AI product spec."
version: 2.0.0
---

# Enterprise PRD Generator

Create strategic, investment-grade Product Requirements Documents that align cross-functional teams, satisfy stakeholder governance, and de-risk complex product initiatives.

---

## Philosophy: The Logical Thinking Framework

Every PRD answers five fundamental questions in sequence:

```
1. WHY (Existence)    → Strategic alignment, business case, problem validation
2. WHAT (Definition)  → Scope, capabilities, user value proposition  
3. WHO (Actors)       → Personas, stakeholders, decision-makers
4. HOW (Execution)    → Technical approach, integration, delivery
5. WHEN (Timeline)    → Phases, milestones, dependencies, gates
```

**Constraint:** No section N can be written until section N-1 is logically sound.

---

## Phase 1: Strategic Discovery

Before writing, establish the **Problem-Solution-Fit** through structured inquiry.

### 1.1 Strategic Clarification Questions

Ask 5-7 questions covering these dimensions:

| Dimension | Question Purpose | Example |
|-----------|------------------|---------|
| **Business Objective** | Link to OKR/strategic pillar | "Which quarterly OKR does this advance?" |
| **Problem Severity** | Validate need exists | "What's the cost of NOT solving this?" |
| **Target Segment** | Define ICP (Ideal Customer Profile) | "Enterprise, SMB, or specific vertical?" |
| **Competitive Context** | Market positioning | "How do competitors solve this today?" |
| **Success Metrics** | Quantifiable outcomes | "What metric movement defines success?" |
| **Constraints** | Guardrails and risks | "Any regulatory, security, or compliance requirements?" |
| **Dependencies** | External blockers | "What teams/systems must coordinate?" |

**Question Format:**

```
1. [Question text] (Select primary driver)
   A. [Option with business rationale]
   B. [Option with business rationale]
   C. [Option with business rationale]
   D. Other: [specify with quantified impact if possible]
```

### 1.2 The Strategic Assessment Matrix

After receiving answers, validate alignment:

```
┌─────────────────────────────────────────────────────────────┐
│ STRATEGIC ASSESSMENT                                         │
├─────────────────────────────────────────────────────────────┤
│ Business Alignment:     □ High    □ Medium    □ Low         │
│ Technical Feasibility:  □ High    □ Medium    □ Low         │
│ Market Urgency:         □ High    □ Medium    □ Low         │
│ Risk Level:             □ High    □ Medium    □ Low         │
│ Investment Required:    □ High    □ Medium    □ Low         │
└─────────────────────────────────────────────────────────────┘
```

**Decision Gate:** If 2+ dimensions are "Low" or "High Risk", recommend PRD scope reduction or spike investigation before proceeding.

---

## Phase 2: PRD Structure

### Document Header

```markdown
# PRD: [Feature/Product Name]

| Attribute        | Value                          |
|------------------|--------------------------------|
| **Version**      | 1.0.0                          |
| **Status**       | Draft / Review / Approved      |
| **Author**       | [Name, Title]                  |
| **Date**         | YYYY-MM-DD                     |
| **Review Cycle** | Q[1-4]-20XX                    |
| **Stakeholders** | [List key approvers]           |

**Classification:** □ Internal  □ Confidential  □ Restricted
```

---

### Section 1: Executive Summary

**Purpose:** Enable executive decision-making in 2 minutes.

```markdown
## 1. Executive Summary

### The Ask
[One sentence: What are we building and for whom?]

### Business Case
- **Problem:** [Quantified pain point - e.g., "Support tickets up 40% QoQ"]
- **Opportunity:** [Quantified benefit - e.g., "$2M ARR expansion potential"]
- **Strategic Fit:** [Link to company objective - e.g., "Supports Platform pillar"]

### Investment
- **Timeline:** [Duration]
- **Team Size:** [FTE count]
- **Estimated Cost:** [Range with confidence level]

### Success Criteria
[1-2 metrics that prove ROI - be specific: "Reduce churn by 15% within 90 days of launch"]

### Recommendation
□ Proceed as specified  □ Proceed with modifications  □ Spike required  □ Defer
```

---

### Section 2: Strategic Context

**Purpose:** Document the "WHY" with evidence.

```markdown
## 2. Strategic Context

### 2.1 Problem Statement
[Use this formula: When [situation], [user type] struggles with [problem] 
because [root cause], resulting in [quantified impact].]

**Evidence:**
- Customer data: [support tickets, churn reasons, NPS feedback]
- Market data: [competitor analysis, industry trends]
- Internal data: [usage analytics, funnel drop-offs]

### 2.2 Strategic Alignment

| Company Objective | This PRD's Contribution | Measurement |
|-------------------|------------------------|-------------|
| [OKR/Pillar]      | [Specific linkage]      | [Metric]    |

### 2.3 Market Context
- **Competitive Landscape:** [Who else solves this? How? Gaps?]
- **Differentiation:** [Our unique approach/advantage]
- **Timing Rationale:** [Why now? Market window?]

### 2.4 Risk-Adjusted Value

| Scenario   | Probability | Value Impact | Expected Value |
|------------|-------------|--------------|----------------|
| Best Case  | X%          | $X           | $X             |
| Base Case  | X%          | $X           | $X             |
| Worst Case | X%          | $X           | $X             |
| **Weighted EV** |         |              | **$X**         |
```

---

### Section 3: User & Stakeholder Analysis

**Purpose:** Define the "WHO" with precision.

```markdown
## 3. User & Stakeholder Analysis

### 3.1 Primary Personas

#### Persona A: [Name] - [Role]

| Attribute | Detail |
|-----------|--------|
| **Demographics** | [Age, seniority, industry] |
| **Goals** | [What they want to achieve] |
| **Pain Points** | [Current frustrations] |
| **Tech Savvy** | [Low / Medium / High] |
| **Decision Authority** | [User / Influencer / Buyer] |
| **Success Looks Like** | [Their desired outcome] |

**Quote:** "[Representative statement in their voice]"

### 3.2 Stakeholder Map

```
                    HIGH INTEREST
                          │
            ┌─────────────┼─────────────┐
            │   MANAGE    │   ENGAGE    │
            │  (Keep      │  (Satisfy   │
            │   informed) │   closely)  │
LOW POWER   ├─────────────┼─────────────┤   HIGH POWER
            │   MONITOR   │   COLLAB    │
            │  (Minimal   │  (Key       │
            │   effort)   │   partners) │
            └─────────────┼─────────────┘
                          │
                    LOW INTEREST
```

| Stakeholder | Role | Interest | Power | Engagement Strategy |
|-------------|------|----------|-------|---------------------|
| [Name]      | [Title] | High/Low | High/Low | [Approach] |

### 3.3 Decision Makers & Approvers

| Role | Name | Approval Needed | Decision Criteria |
|------|------|-----------------|-------------------|
| [e.g., CPO] | [Name] | Go/No-go | Strategic fit, resource allocation |
| [e.g., CTO] | [Name] | Technical approach | Architecture alignment, tech debt |
| [e.g., Legal] | [Name] | Compliance | Regulatory adherence |
```

---

### Section 4: Product Requirements

**Purpose:** Define the "WHAT" with completeness.

```markdown
## 4. Product Requirements

### 4.1 User Stories (The "Jobs-to-be-Done")

**Story Mapping Principle:**
- Group by user journey phase (Discover → Evaluate → Adopt → Use → Retain)
- Order by priority within each phase (MoSCoW: Must, Should, Could, Won't)

#### Epic: [Journey Phase Name]

**Epic Goal:** [One-sentence outcome for this phase]

##### Story US-[XXX]: [Story Title]

**Priority:** 🔴 Must / 🟡 Should / 🟢 Could  
**Complexity:** [S / M / L / XL]  
**Dependencies:** [Blockers or prerequisites]

**User Story:**
> As a [persona], I want [action], so that [outcome].

**Acceptance Criteria:**

| # | Criteria | Test Method | Definition of Done |
|---|----------|-------------|-------------------|
| 1 | [Specific, verifiable condition] | [Unit/Integration/E2E] | □ |
| 2 | [Specific, verifiable condition] | [Unit/Integration/E2E] | □ |
| 3 | [Edge case handling] | [Test type] | □ |
| 4 | [Performance/scale requirement] | [Benchmark] | □ |
| 5 | [UX/Accessibility standard] | [Review/Testing] | □ |

**Open Questions:**
- [Any unresolved decisions blocking this story]

**Notes:**
- [Design references, API contracts, relevant docs]
- [UI stories: Include "Verify in browser using dev-browser skill" as final AC]

---

### 4.2 Functional Requirements (System Behaviors)

**Use when:** Requirements span multiple stories or define system contracts.

| ID | Requirement | Priority | Acceptance Criteria | Owner |
|----|-------------|----------|---------------------|-------|
| FR-001 | [System behavior] | P0/P1/P2 | [Measurable condition] | [Team] |
| FR-002 | [System behavior] | P0/P1/P2 | [Measurable condition] | [Team] |

### 4.3 Non-Functional Requirements

| Category | Requirement | Target | Measurement |
|----------|-------------|--------|-------------|
| **Performance** | Page load time | < 2s | Lighthouse, RUM |
| **Performance** | API response | < 200ms | p95 latency |
| **Availability** | Uptime | 99.9% | Monitoring |
| **Security** | Auth standard | OAuth 2.0 + MFA | Security review |
| **Scalability** | Concurrent users | 10,000 | Load testing |
| **Compliance** | Data residency | [Region-specific] | Legal review |
| **Accessibility** | WCAG level | AA | Automated + manual audit |

### 4.4 Out of Scope (Non-Goals)

Explicitly excluded to manage expectations and prevent scope creep:

| Item | Reason for Exclusion | Future Consideration |
|------|---------------------|---------------------|
| [Feature] | [Why not in this iteration] | [When it might be considered] |

**Scope Change Protocol:**
- Minor changes: Product Lead approval
- Major changes: Stakeholder re-review required
```

---

### Section 5: Technical & Implementation Approach

**Purpose:** Define the "HOW" with architectural rigor.

```markdown
## 5. Technical & Implementation Approach

### 5.1 Solution Architecture

```
[Insert architecture diagram or component diagram]
```

**Components:**
| Component | Technology | Responsibility | Owner |
|-----------|------------|----------------|-------|
| [Name] | [Stack] | [Function] | [Team] |

### 5.2 Integration Points

| System | Integration Type | Data Flow | Contract |
|--------|-----------------|-----------|----------|
| [System A] | [API/Event/DB] | [Direction] | [Link to spec] |

### 5.3 Data Model (If Applicable)

**Key Entities:**
- [Entity]: [Attributes, relationships]

### 5.4 API Contracts (If Applicable)

| Endpoint | Method | Purpose | Request | Response |
|----------|--------|---------|---------|----------|
| /api/v1/... | GET/POST | [Function] | [Schema] | [Schema] |

### 5.5 Technical Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation Strategy | Owner |
|------|------------|--------|---------------------|-------|
| [Technical risk] | H/M/L | H/M/L | [Contingency plan] | [Name] |

### 5.6 Technical Debt & Trade-offs

| Decision | Trade-off | Rationale | Pay-down Plan |
|----------|-----------|-----------|---------------|
| [Choice made] | [What we sacrificed] | [Why] | [When/how we fix] |
```

---

### Section 6: Release Strategy

**Purpose:** Define the "WHEN" with milestones.

```markdown
## 6. Release Strategy

### 6.1 Phasing Approach

**Selected Strategy:** □ Big Bang  □ Phased Rollout  □ Feature Flags  □ Beta → GA

**Rationale:** [Why this approach fits the risk profile]

### 6.2 Release Phases

| Phase | Deliverables | Audience | Success Gate | Timeline |
|-------|--------------|----------|--------------|----------|
| **Alpha** | Core functionality | Internal team | [Criteria] | Week X |
| **Beta** | Full feature set | Design partners (n=5) | [Criteria] | Week Y |
| **GA** | Production ready | All users | [Criteria] | Week Z |

### 6.3 Milestone Timeline

```
Week 1-2: [Milestone] ──→ Week 3-4: [Milestone] ──→ Week 5-6: [Milestone]
    │                        │                        │
    ▼                        ▼                        ▼
[Deliverable]            [Deliverable]            [Deliverable]
```

### 6.4 Go/No-Go Criteria

**Launch is approved when ALL are true:**
- [ ] [Criterion 1 - e.g., "Zero P0 bugs"]
- [ ] [Criterion 2 - e.g., "Performance benchmarks met"]
- [ ] [Criterion 3 - e.g., "Security review passed"]
- [ ] [Criterion 4 - e.g., "Documentation complete"]
- [ ] [Criterion 5 - e.g., "Support team trained"]

### 6.5 Rollback Plan

**Trigger Conditions:**
- [Specific metric thresholds that trigger rollback]

**Rollback Procedure:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Estimated Recovery Time:** [Duration]
```

---

### Section 7: Success Metrics & Measurement

**Purpose:** Define how we prove value was delivered.

```markdown
## 7. Success Metrics & Measurement

### 7.1 North Star Metric
[The single metric that best captures product success]

### 7.2 KPI Framework

| Category | Metric | Baseline | Target | Measurement Method | Owner |
|----------|--------|----------|--------|-------------------|-------|
| **Adoption** | [Metric] | [Value] | [Value] | [Tool/method] | [Name] |
| **Engagement** | [Metric] | [Value] | [Value] | [Tool/method] | [Name] |
| **Retention** | [Metric] | [Value] | [Value] | [Tool/method] | [Name] |
| **Revenue** | [Metric] | [Value] | [Value] | [Tool/method] | [Name] |
| **Efficiency** | [Metric] | [Value] | [Value] | [Tool/method] | [Name] |

### 7.3 Counter-Metrics (Guardrails)

[Metrics that should NOT degrade:]
- [Metric]: [Why it matters, acceptable range]

### 7.4 Measurement Plan

| Timeframe | Analysis | Deliverable |
|-----------|----------|-------------|
| Week 1 post-launch | Initial adoption | [Report type] |
| Month 1 post-launch | Usage patterns | [Report type] |
| Quarter 1 post-launch | ROI assessment | [Report type] |
```

---

### Section 8: Risk Assessment

**Purpose:** Identify and mitigate threats to success.

```markdown
## 8. Risk Assessment

### 8.1 Risk Register

| ID | Risk | Category | Likelihood | Impact | Risk Score | Mitigation | Contingency | Owner |
|----|------|----------|------------|--------|------------|------------|-------------|-------|
| R01 | [Description] | Tech/Product/Market/Legal | H/M/L | H/M/L | [L×I] | [Prevention] | [If it happens] | [Name] |

**Risk Score Matrix:**
- High (7-9): Requires executive attention, mitigation plan mandatory
- Medium (4-6): Monitor closely, have contingency ready
- Low (1-3): Accept and monitor

### 8.2 Dependency Risks

| Dependency | Risk if Delayed | Mitigation |
|------------|-----------------|------------|
| [Team/System] | [Impact] | [Alternative plan] |

### 8.3 Assumptions

[Assumptions that, if proven false, invalidate this PRD:]
1. [Assumption]: [Validation method]
2. [Assumption]: [Validation method]

### 8.4 Compliance & Regulatory

| Requirement | Standard | Verification | Sign-off |
|-------------|----------|--------------|----------|
| [e.g., GDPR] | [Article/section] | [Process] | [Role] |
| [e.g., SOC2] | [Control] | [Process] | [Role] |
```

---

### Section 9: Operational Readiness

**Purpose:** Ensure post-launch success.

```markdown
## 9. Operational Readiness

### 9.1 Support Plan

| Tier | Issue Types | Response Time | Resolution Time | Escalation Path |
|------|-------------|---------------|-----------------|-----------------|
| L1 | [Types] | [Time] | [Time] | [Path] |
| L2 | [Types] | [Time] | [Time] | [Path] |

### 9.2 Documentation Requirements

- [ ] User documentation
- [ ] Admin documentation
- [ ] API documentation
- [ ] Runbooks
- [ ] Training materials

### 9.3 Monitoring & Alerting

| Metric | Threshold | Alert Channel | Runbook |
|--------|-----------|---------------|---------|
| [Metric] | [Threshold] | [Channel] | [Link] |

### 9.4 Incident Response

**Severity Definitions:**
- SEV1: [Definition, e.g., "Complete outage"]
- SEV2: [Definition, e.g., "Major feature degraded"]
- SEV3: [Definition, e.g., "Minor issue, workaround exists"]

**Response Times:**
- SEV1: [Time to acknowledge] / [Time to resolve]
- SEV2: [Time to acknowledge] / [Time to resolve]
- SEV3: [Time to acknowledge] / [Time to resolve]
```

---

### Section 10: Appendix

```markdown
## 10. Appendix

### 10.1 Glossary

| Term | Definition |
|------|------------|
| [Term] | [Definition] |

### 10.2 Reference Documents

| Document | Link | Description |
|----------|------|-------------|
| [Name] | [URL] | [Purpose] |

### 10.3 Decision Log

| Date | Decision | Rationale | Decision Maker |
|------|----------|-----------|----------------|
| [Date] | [What was decided] | [Why] | [Name] |

### 10.4 Context & Discovery Notes

#### Clarifying Questions & Answers

1. **[Question]** → **[Answer]**
2. **[Question]** → **[Answer]**

#### Assumptions Made

- [Assumption]: [Rationale]

#### Open Questions (Post-PRD)

- [Question]: [Why it couldn't be resolved, who needs to answer]
```

---

## Phase 3: Quality Assurance

### PRD Review Checklist

Before marking complete, verify:

#### Strategic Soundness
- [ ] Business case quantified (not just "improve" but "reduce by X%")
- [ ] Strategic alignment explicitly stated
- [ ] Risk-adjusted value calculated
- [ ] Competitive context documented

#### Completeness
- [ ] All 5 W's answered (Why, What, Who, How, When)
- [ ] User stories follow INVEST principles
- [ ] Each story has verifiable acceptance criteria
- [ ] Non-goals explicitly listed
- [ ] Dependencies mapped

#### Feasibility
- [ ] Technical approach reviewed by engineering
- [ ] Resource requirements realistic
- [ ] Timeline accounts for dependencies
- [ ] Risks have mitigation plans

#### Measurability
- [ ] Success metrics are SMART
- [ ] Baseline measurements documented
- [ ] Counter-metrics identified
- [ ] Measurement plan defined

#### Operational Readiness
- [ ] Support plan defined
- [ ] Monitoring strategy documented
- [ ] Rollback plan specified
- [ ] Documentation requirements listed

#### Stakeholder Alignment
- [ ] Decision makers identified
- [ ] Approval process documented
- [ ] Communication plan established

---

## Logical Decision Frameworks

### 1. Feature Prioritization: RICE Score

```
RICE = (Reach × Impact × Confidence) / Effort

Reach:     How many users in a given period? (e.g., 1000 users/quarter)
Impact:    3 = Massive, 2 = High, 1 = Medium, 0.5 = Low, 0.25 = Minimal
Confidence: 100% = High, 80% = Medium, 50% = Low
Effort:    Person-months required
```

### 2. Scope Decisions: MoSCoW

| Priority | Definition | Escalation |
|----------|------------|------------|
| **Must** | Non-negotiable for launch | Executive approval to remove |
| **Should** | Important but launch possible without | Product Lead decides |
| **Could** | Desirable if time permits | Engineering Lead decides |
| **Won't** | Explicitly out of scope | Future PRD |

### 3. Risk Assessment: Probability × Impact

```
Impact
  H │  Medium   │   High    │  Critical
    │   Risk    │   Risk    │    Risk
  M │   Low     │  Medium   │   High
    │   Risk    │   Risk    │    Risk
  L │   Low     │   Low     │  Medium
    │   Risk    │   Risk    │    Risk
    └───────────┴───────────┴──────────
          L           M           H    Probability
```

---

## Special Considerations for AI/ML Products

When the PRD involves AI/ML capabilities, add:

```markdown
### AI/ML Specific Requirements

#### Model Requirements
- **Model Type:** [Classification, Generation, Embedding, etc.]
- **Performance Criteria:**
  - Accuracy/Precision/Recall targets
  - Latency requirements (inference time)
  - Throughput (requests/second)

#### Data Requirements
- **Training Data:** [Source, size, quality criteria]
- **Privacy:** [PII handling, consent requirements]
- **Bias Assessment:** [Fairness metrics, testing approach]

#### Operational ML
- **Model Versioning:** [How models are versioned and deployed]
- **Monitoring:** [Drift detection, performance degradation alerts]
- **Human-in-the-Loop:** [When human review is required]

#### Safety & Ethics
- **Failure Modes:** [How the model can fail, harm assessment]
- **Guardrails:** [Safety constraints, output filtering]
- **Explainability:** [Requirements for model interpretability]
```

---

## Output & Distribution

### File Naming Convention
```
prd-[product-name]-[version]-[status].md

Examples:
- prd-ai-assistant-v1.0-draft.md
- prd-enterprise-sso-v2.1-approved.md
```

### Storage Location
- **Primary:** `.ralph/PRD-N/prd.md` (when using ralph workflow)
- **Alternative:** `docs/prd/[feature-name]/prd.md`
- **Archive:** `docs/prd/archive/[feature-name]-[date].md`

### Distribution List
After approval, distribute to:
- Engineering Lead
- Design Lead  
- QA Lead
- Support Lead
- Product Marketing
- Executive Sponsor

---

## When to Use Individual PRD Instead

Consider the individual skill when:
- 👤 Solo developer or side project
- ⏱️ Need PRD done in 15-30 minutes
- 🛠️ Building an MVP or internal tool
- 🔄 Rapid iteration over formal process
- 📝 Feature is straightforward (CRUD, UI improvements)

---

## Summary: The Enterprise PRD Difference

| Aspect | Individual PRD | Enterprise PRD |
|--------|----------------|----------------|
| **Focus** | Feature description | Strategic investment case |
| **Audience** | Implementation team | Cross-functional stakeholders |
| **Rigor** | Functional completeness | Business case + risk analysis |
| **Metrics** | Output-focused | Outcome-focused |
| **Governance** | Informal | Structured approval gates |
| **Scope** | Single feature | Initiative with dependencies |
| **Risk** | Acknowledged | Quantified and mitigated |
| **Post-launch** | Ship and move on | Measure, learn, iterate |

---

*"A PRD is not a specification document. It is a shared understanding of the problem, the proposed solution, and the evidence that binds them together."*
