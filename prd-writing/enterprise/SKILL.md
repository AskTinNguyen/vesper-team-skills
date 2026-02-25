---
name: prd-enterprise
description: "Generate strategic PRDs for enterprise products, stakeholder alignment, and complex initiatives. Structured yet efficient—30-45 min to complete. Use for customer-facing features, AI/ML products, compliance requirements, or when cross-functional coordination needed. Triggers on: enterprise prd, strategic spec, team prd, ai product spec, stakeholder doc."
version: 2.1.0
---

# Enterprise PRD Generator

Create strategic PRDs that align teams and de-risk initiatives—in **30-45 minutes**, not hours.

---

## Philosophy: The 4-Sentence Foundation

Before writing, be able to answer:

1. **Why:** What problem are we solving, and why now?
2. **What:** What's the smallest solution that delivers value?
3. **Who:** Who are the users, and who decides if this ships?
4. **How:** What's our approach, and what could go wrong?

---

## Phase 1: Rapid Discovery (5 min)

Ask 4 targeted questions:

```
1. What's the business driver?
   A. Revenue/Growth    B. Retention/Expansion    C. Efficiency/Cost    D. Compliance/Risk

2. Who's the primary user?
   A. End users         B. Admins/Ops            C. Developers         D. Executives

3. What's the risk level?
   A. Low (well-understood)  B. Medium (some unknowns)  C. High (complex/new)

4. Any hard constraints?
   A. Compliance/Security  B. Performance/Scale  C. Integration requirements  D. Timeline pressure
```

**Response:** "1A, 2A, 3B, 4A" format

---

## Phase 2: Efficient PRD Structure (25-40 min)

### Document Header (1 min)

```markdown
# PRD: [Feature/Product Name]

| **Version** | 1.0.0 | **Status** | Draft / Review / Approved |
| **Author**  | [Name] | **Date** | YYYY-MM-DD |
| **Stakeholders** | [Key approvers] | **Classification** | Internal/Confidential |
```

---

### Section 1: Executive Summary (3 min)

```markdown
## 1. Executive Summary

**The Ask:** [One sentence: What for whom?]

**Business Case:**
- **Problem:** [Quantified pain - e.g., "40% support tickets on X"]
- **Opportunity:** [Quantified gain - e.g., "$500K ARR potential"]
- **Strategic Fit:** [Link to OKR/pillar]

**Investment:** [Timeline] • [Team size] • [Cost estimate]

**Success:** [1 metric - e.g., "Reduce churn 15% in 90 days"]
```

---

### Section 2: Context & Users (5 min)

```markdown
## 2. Context & Users

### Problem
[When [situation], [users] struggle with [problem] because [cause], 
resulting in [impact].]

**Evidence:** [Support tickets, churn data, NPS, market analysis]

### Strategic Alignment
| Company Goal | Our Contribution |
|--------------|------------------|
| [OKR] | [Specific linkage] |

### Primary Persona

| Attribute | Detail |
|-----------|--------|
| **Role** | [Title/type] |
| **Goal** | [What they want] |
| **Pain** | [Current frustration] |
| **Decision Power** | [User/Influencer/Buyer] |

### Stakeholders

| Role | Name | Approval | Criteria |
|------|------|----------|----------|
| [e.g., CPO] | [Name] | Go/No-go | Strategic fit |
| [e.g., CTO] | [Name] | Technical | Architecture |
| [e.g., Legal] | [Name] | Compliance | Regulatory |
```

---

### Section 3: Requirements (10 min)

```markdown
## 3. Requirements

### User Stories by Priority

#### 🔴 Must Have

**US-1: [Title]**
> As a [persona], I want [action], so that [outcome].

| # | Acceptance Criteria | Test |
|---|---------------------|------|
| 1 | [Specific condition] | [Unit/E2E] |
| 2 | [Specific condition] | [Unit/E2E] |
| 3 | [Edge case] | [E2E] |
| 4 | **UI:** Verified in browser | Manual |

**Notes:** [Files, APIs, dependencies]

**US-2:** [Repeat for each Must-have]

---

#### 🟡 Should Have

**US-X:** [Title and story - 2-3 items max]

---

#### 🟢 Could Have

[Deferred to next iteration]

### Non-Functional Requirements

| Category | Requirement | Target |
|----------|-------------|--------|
| Performance | [Metric] | [Target] |
| Security | [Standard] | [Target] |
| Compliance | [Requirement] | [Target] |

### Out of Scope

| Item | Reason | Future |
|------|--------|--------|
| [Feature] | [Why excluded] | [When considered] |
```

---

### Section 4: Technical Approach (5 min)

```markdown
## 4. Technical Approach

**Architecture:** [Brief description or link to diagram]

**Key Components:**
| Component | Tech | Owner |
|-----------|------|-------|
| [Name] | [Stack] | [Team] |

**Integrations:**
| System | Type | Contract |
|--------|------|----------|
| [System] | [API/Event] | [Link] |

**Risks & Mitigations:**
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| [Description] | H/M/L | [Plan] |

**Key Decisions:**
- [Decision]: [Rationale]
```

---

### Section 5: Release & Success (4 min)

```markdown
## 5. Release & Success

### Release Strategy

**Approach:** □ Big Bang  □ Phased  □ Feature Flags  □ Beta→GA

| Phase | Deliverable | Audience | Gate |
|-------|-------------|----------|------|
| Alpha | Core | Internal | [Criteria] |
| Beta | Full | Partners | [Criteria] |
| GA | Production | All | [Criteria] |

### Go/No-Go Criteria

- [ ] [Criterion 1 - e.g., "Zero P0 bugs"]
- [ ] [Criterion 2 - e.g., "Performance targets met"]
- [ ] [Criterion 3 - e.g., "Security review passed"]

### Success Metrics

| Category | Metric | Baseline | Target |
|----------|--------|----------|--------|
| Adoption | [Metric] | [Value] | [Value] |
| Engagement | [Metric] | [Value] | [Value] |
| Business | [Metric] | [Value] | [Value] |

**Counter-Metrics:** [What shouldn't degrade]
```

---

### Section 6: Risk & Operations (2 min)

```markdown
## 6. Risk & Operations

### Risk Register

| ID | Risk | Category | L | I | Score | Mitigation |
|----|------|----------|---|---|-------|------------|
| R1 | [Risk] | Tech/Product | H/M/L | H/M/L | [L×I] | [Plan] |

### Operational Readiness

- [ ] Support plan defined
- [ ] Monitoring configured
- [ ] Documentation complete
- [ ] Rollback plan ready

**Response Times:** SEV1 [X min] / SEV2 [Y min] / SEV3 [Z min]
```

---

### Section 7: Appendix (Optional)

```markdown
## 7. Appendix

**Questions & Answers:**
1. [Q] → [A]

**Assumptions:**
- [Assumption]: [Validation]

**Open Questions:**
- [Question]: [Who answers]

**Decision Log:**
| Date | Decision | Rationale |
|------|----------|-----------|
| [Date] | [What] | [Why] |
```

---

## Quick Reference: Decision Frameworks

### RICE Scoring (for prioritization)
```
RICE = (Reach × Impact × Confidence) / Effort

Reach: Users per time period
Impact: 3=Massive, 2=High, 1=Medium, 0.5=Low
Confidence: 100%=High, 80%=Medium, 50%=Low
Effort: Person-months
```

### MoSCoW (for scope)
| Priority | Definition |
|----------|------------|
| **Must** | Non-negotiable |
| **Should** | Important, can launch without |
| **Could** | Nice-to-have |
| **Won't** | Out of scope |

### Risk Scoring
```
Score = Likelihood × Impact (1-3 scale each)
7-9 = High: Executive attention required
4-6 = Medium: Monitor + contingency
1-3 = Low: Accept and monitor
```

---

## AI/ML Quick Add-On

If building AI features, add this section:

```markdown
### AI/ML Considerations

**Model:**
- Type: [Classification/Generation/etc]
- Performance: [Accuracy/latency targets]

**Data & Safety:**
- Training data: [Source, privacy]
- Bias testing: [Approach]
- Guardrails: [Safety constraints]
- Human review: [When required]

**Operations:**
- Drift detection: [Method]
- Versioning: [Approach]
- Explainability: [Requirements]
```

---

## Time Budget Summary

| Phase | Time |
|-------|------|
| Discovery (4 Qs) | 5 min |
| Header + Executive | 4 min |
| Context + Users | 5 min |
| Requirements | 10 min |
| Technical | 5 min |
| Release + Success | 4 min |
| Risk + Ops | 2 min |
| **Total** | **~35 min** |

---

## When to Use Individual PRD Instead

Consider downgrading when:
- 👤 Solo project with no stakeholders
- ⏱️ Need spec in <20 minutes
- 🛠️ Simple CRUD or UI feature
- 🔄 Rapid iteration over formal process

---

## Output

- **Naming:** `prd-[feature]-v1.0-[status].md`
- **Location:** `.ralph/PRD-N/prd.md` or `docs/prd/[feature]/prd.md`
- **Distribution:** Engineering, Design, Product, Stakeholders

---

*"A strategic PRD doesn't need to be long. It needs to be clear, aligned, and actionable."*
