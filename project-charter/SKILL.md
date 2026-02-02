---
name: project-charter
description: Create a formal Project Charter following PMI standards. Use when initiating new projects, seeking stakeholder alignment, defining high-level scope, budget, and timeline, or establishing project authority. Triggers on "create project charter", "write charter", "initiate project", "project authorization", "business case", "project kickoff", "project proposal", "get approval", "scope document".
allowed-tools: [Read, Write, Bash, Grep]
preconditions:
  - Project concept or business need identified
  - Sponsor or decision-maker available for approval
  - Initial stakeholder list available
---

# Project Charter

Create a formal Project Charter that authorizes the project, establishes the project manager's authority, and documents high-level requirements, boundaries, and success criteria.

---

## When to Use This Skill

| Scenario | Use This Skill |
|----------|----------------|
| Starting a new project | ✅ Formal authorization and alignment |
| Kicking off a major initiative | ✅ Establish scope, budget, timeline boundaries |
| Seeking funding/approval | ✅ Business case + ROI documentation |
| Aligning stakeholders | ✅ Clear authority, roles, success criteria |
| Handing off to project manager | ✅ Formal PM appointment with authority |

---

## Prerequisites

Collect the following required inputs. Request missing information from stakeholders before proceeding:

| Input | Why It Matters | Source |
|-------|----------------|--------|
| Business need/problem | Justifies the project | Sponsor, business case |
| Measurable objectives | Defines success | SMART goals from sponsor |
| High-level requirements | Boundaries the scope | Stakeholder interviews |
| Pre-approved budget range | Sets financial constraints | Finance/sponsor |
| Target completion date | Sets temporal boundaries | Sponsor, market needs |
| Key stakeholders | Identifies who must be involved | Org chart, sponsor input |
| Known risks (high-level) | Flags early concerns | Expert judgment |
| Project manager assignment | Authorizes leadership | Sponsor decision |

---

## Quick Start: Charter Lite

For small projects or internal initiatives, use this **1-page charter** instead of the full template:

```markdown
# Project Charter Lite: [Project Name]

**Date:** YYYY-MM-DD  
**Sponsor:** [Name]  
**Project Manager:** [Name]

## What & Why
[One paragraph: What is this project and why does it matter?]

## Success Criteria
- [Specific, measurable outcome 1]
- [Specific, measurable outcome 2]

## In Scope
- [Deliverable 1]
- [Deliverable 2]

## Out of Scope
- [What's not included]

## Timeline & Budget
- **Duration:** [X weeks/months]
- **Budget:** $[X] (or "Internal resources only")
- **Key Milestones:** [Date 1], [Date 2]

## PM Authority
Can adjust schedule up to [X] days and budget up to $[Y] without approval.
Escalate larger changes to [Sponsor].

## Signatures
| Role | Name | Date |
|------|------|------|
| Sponsor | | |
| PM | | |
```

**Use Charter Lite when:**
- Project duration < 4 weeks
- Budget < $25K
- Internal team only (no external vendors)
- Low organizational risk
- No regulatory/compliance requirements

**Use Full Charter when:**
- External stakeholders or funding
- Multiple departments involved
- Significant budget or timeline
- Regulatory/compliance requirements
- High organizational visibility

---

## Project Charter Structure

Use this template to create a complete charter:

```markdown
# Project Charter: [Project Name]

**Version:** 1.0  
**Date:** YYYY-MM-DD  
**Author:** [Project Manager Name]  
**Status:** Draft → Approved  

---

## 1. Project Purpose and Justification

### 1.1 Business Need
**The problem or opportunity:**
[Clear statement of why this project exists]

**Consequences of not doing this project:**
- [Business impact 1]
- [Business impact 2]
- [Business impact 3]

### 1.2 Project Purpose Statement
**In one sentence:**
[This project will deliver X to achieve Y, resulting in Z]

### 1.3 Alignment with Strategic Goals

| Strategic Goal | How This Project Supports It |
|----------------|------------------------------|
| [Goal 1] | [Contribution] |
| [Goal 2] | [Contribution] |

---

## 2. Measurable Project Objectives

Objectives must be **SMART**: Specific, Measurable, Achievable, Relevant, Time-bound

| Objective | Success Criteria | Measurement Method | Target Date |
|-----------|------------------|-------------------|-------------|
| [Objective 1] | [What "done" looks like] | [How to measure] | [Date] |
| [Objective 2] | [What "done" looks like] | [How to measure] | [Date] |
| [Objective 3] | [What "done" looks like] | [How to measure] | [Date] |

### High-Level Success Criteria

**Must Achieve (Critical):**
- [ ] [Criterion 1]
- [ ] [Criterion 2]

**Should Achieve (Important):**
- [ ] [Criterion 3]
- [ ] [Criterion 4]

**Nice to Achieve (Desirable):**
- [ ] [Criterion 5]

---

## 3. High-Level Requirements

### 3.1 In Scope (Will Deliver)

| Requirement | Priority | Acceptance Criteria |
|-------------|----------|---------------------|
| [Requirement 1] | Must Have | [How to verify] |
| [Requirement 2] | Must Have | [How to verify] |
| [Requirement 3] | Should Have | [How to verify] |
| [Requirement 4] | Could Have | [How to verify] |

### 3.2 Out of Scope (Will NOT Deliver)

| Item | Reason for Exclusion |
|------|---------------------|
| [Out of scope 1] | [Why excluded] |
| [Out of scope 2] | [Why excluded] |
| [Out of scope 3] | [Why excluded] |

### 3.3 Constraints

| Constraint Type | Description | Impact |
|-----------------|-------------|--------|
| Budget | [Limit] | [What this restricts] |
| Schedule | [Deadline] | [What this requires] |
| Resources | [Availability] | [What this limits] |
| Technical | [Limitation] | [What this affects] |
| Legal/Regulatory | [Requirement] | [What this mandates] |

### 3.4 Assumptions

| Assumption | If Proven Wrong... |
|------------|-------------------|
| [Assumption 1] | [Impact and contingency] |
| [Assumption 2] | [Impact and contingency] |
| [Assumption 3] | [Impact and contingency] |

---

## 4. High-Level Risks

| Risk | Likelihood | Impact | Mitigation Approach |
|------|------------|--------|---------------------|
| [Risk 1] | High/Med/Low | High/Med/Low | [Strategy] |
| [Risk 2] | High/Med/Low | High/Med/Low | [Strategy] |
| [Risk 3] | High/Med/Low | High/Med/Low | [Strategy] |

> **Note:** Detailed risk analysis will be developed in the Risk Register during project planning.

---

## 5. Summary Milestone Schedule

| Milestone | Target Date | Deliverable | Dependencies |
|-----------|-------------|-------------|--------------|
| Project Kickoff | [Date] | Team assembled, charter signed | Charter approval |
| Requirements Complete | [Date] | Approved requirements document | Kickoff complete |
| Design Complete | [Date] | Approved design specifications | Requirements |
| [Key Milestone] | [Date] | [Deliverable] | [Dependencies] |
| Project Complete | [Date] | Final deliverables accepted | All milestones |

### Rough Order of Magnitude (ROM) Timeline

```
Phase 1: Initiation & Planning  [Weeks X-Y]
Phase 2: Design & Development   [Weeks Y-Z]
Phase 3: Testing & Deployment   [Weeks Z-A]
Phase 4: Closure & Handover     [Week A]

Total Estimated Duration: [X weeks/months]
```

---

## 6. Summary Budget

### ROM Budget Estimate

| Category | Low Estimate | High Estimate | Notes |
|----------|-------------|---------------|-------|
| Personnel | $X | $Y | [Team composition] |
| Equipment/Tools | $X | $Y | [What's needed] |
| External Services | $X | $Y | [Vendors/consultants] |
| Materials/Supplies | $X | $Y | [Consumables] |
| Contingency (10-15%) | $X | $Y | [Risk buffer] |
| **Total** | **$X** | **$Y** | ROM range: ±25-50% |

### Funding Source
[Where the budget comes from]

### Budget Constraints
[Any budget limitations or approval requirements]

---

## 7. Stakeholder Summary

### 7.1 Project Sponsor

| Field | Information |
|-------|-------------|
| Name | [Sponsor name] |
| Title | [Title] |
| Role | [Authority level, decision rights] |
| Accountability | [What they're accountable for] |

### 7.2 Project Manager

| Field | Information |
|-------|-------------|
| Name | [PM name] |
| Authority Level | [What decisions PM can make] |
| Reporting To | [Sponsor/management chain] |
| Accountability | [What PM is accountable for] |

### 7.3 Key Stakeholders

| Name/Role | Interest | Influence | Communication Needs |
|-----------|----------|-----------|---------------------|
| [Stakeholder 1] | [What they care about] | High/Med/Low | [Frequency/format] |
| [Stakeholder 2] | [What they care about] | High/Med/Low | [Frequency/format] |
| [Stakeholder 3] | [What they care about] | High/Med/Low | [Frequency/format] |

---

## 8. Project Authority and Governance

### 8.1 Project Manager Authority

**PM Name:** [Name]  
**Authority Level:** [Full/Shared/Limited — define clearly]

| Authority Area | PM Can Decide | Escalation Threshold | Escalate To |
|----------------|---------------|---------------------|-------------|
| Schedule changes | Up to [X] days | Beyond [X] days | [Sponsor] |
| Budget allocation | Up to $[Y] | Beyond $[Y] | [Sponsor] |
| Scope modifications | Minor per change process | Major changes | [CCB/Sponsor] |
| Resource assignment | Internal team members | External hires | [HR/Sponsor] |
| Vendor selection | Up to $[Z] | Beyond $[Z] | [Procurement] |
| Technical decisions | Within approved architecture | Architecture changes | [Tech Lead/Sponsor] |

**Emergency Authority:**
- PM may make decisions exceeding authority in emergencies
- Post-hoc approval required within [24] hours
- Document rationale and obtain retrospective approval

### 8.2 Decision-Making Matrix

| Decision Type | Authority | Escalation Path |
|--------------|-----------|-----------------|
| Scope changes > [X]% | [Who decides] | [How to escalate] |
| Budget changes > $[Y] | [Who decides] | [How to escalate] |
| Schedule changes > [Z] days | [Who decides] | [How to escalate] |
| Vendor selection > $[A] | [Who decides] | [How to escalate] |
| Quality acceptance | [Who decides] | [How to escalate] |

### 8.3 Approval Requirements

| Deliverable | Approver | Approval Criteria |
|-------------|----------|-------------------|
| Charter | [Sponsor] | Business need validated |
| Requirements | [Stakeholders] | Meets business need |
| Final deliverables | [Sponsor + Users] | Meets success criteria |

### 8.3 Governance Structure

**Change Control Board (CCB):**
- Members: [List key decision makers]
- Meeting frequency: [How often CCB meets]
- Trigger: [What requires CCB review]

---

## 9. Acceptance Criteria

### 9.1 Project Completion Criteria

The project will be considered complete when:

1. [ ] [Deliverable 1] is delivered and accepted
2. [ ] [Deliverable 2] is delivered and accepted
3. [ ] All success criteria in Section 2 are met
4. [ ] Sponsor sign-off obtained
5. [ ] Lessons learned documented
6. [ ] Final report delivered

### 9.2 Formal Acceptance Process

1. [PM submits deliverables for review]
2. [Sponsor/stakeholders review against criteria]
3. [Feedback incorporated or formally rejected]
4. [Formal sign-off obtained]
5. [Project moved to closure]

---

## 10. Signatures

### Approval

By signing below, the undersigned acknowledge they have reviewed this Project Charter, agree with its contents, and authorize the project to proceed.

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Project Sponsor | | | |
| Project Manager | | | |
| Key Stakeholder 1 | | | |
| Key Stakeholder 2 | | | |

---

## Appendix

### A. Glossary

| Term | Definition |
|------|------------|
| [Term] | [Definition] |

### B. References

- [Link to business case]
- [Link to strategic plan]
- [Link to related projects]

### C. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | [Date] | [Name] | Initial draft |
| 1.0 | [Date] | [Name] | Approved version |
```

---

## Examples

### Example 1: Software Development Project

```markdown
# Project Charter: CRM Modernization

## 1. Project Purpose and Justification

### Business Need
Current CRM system is end-of-life, unsupported, and cannot scale with projected growth. Customer data fragmentation across 3 systems causes reporting delays and compliance risks.

**Consequences of delay:**
- Security vulnerabilities in unsupported system
- Inability to meet Q4 reporting requirements
- Manual workarounds costing 40 hours/week

### Project Purpose
This project will replace the legacy CRM with Salesforce, migrating 50,000 customer records and integrating with ERP, resulting in unified customer view and automated reporting.

## 2. Measurable Objectives

| Objective | Success Criteria | Measurement | Target |
|-----------|-----------------|-------------|--------|
| Data migration | 100% of active records migrated | Migration validation report | Aug 30 |
| User adoption | 90% of users trained and active | Login tracking | Sep 15 |
| Reporting efficiency | Reporting time reduced 75% | Time-tracking survey | Oct 1 |

## 3. High-Level Requirements

**In Scope:**
- Salesforce implementation and configuration
- Migration of customer, contact, and opportunity data
- Integration with existing ERP system
- User training for 200 staff

**Out of Scope:**
- Marketing automation module (Phase 2)
- Mobile app development (separate project)
- Data cleanup prior to migration (prerequisite)

## 4. High-Level Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Data migration errors | Medium | High | Multiple test migrations, validation scripts |
| User resistance | Medium | Medium | Change management, early champions |
| Integration complexity | High | Medium | Experienced vendor, phased approach |

## 5. Summary Milestone Schedule

| Milestone | Date |
|-----------|------|
| Charter Approved | Jan 15 |
| Requirements Signed | Feb 15 |
| System Config Complete | Apr 30 |
| Data Migration Complete | Jun 30 |
| Go-Live | Aug 15 |
| Project Closure | Sep 30 |

## 6. Summary Budget

| Category | Estimate |
|----------|----------|
| Salesforce licenses | $180,000/year |
| Implementation services | $250,000 |
| Internal resources | $120,000 |
| Training & change mgmt | $50,000 |
| Contingency (15%) | $90,000 |
| **Total Year 1** | **$690,000** |
```

### Example 2: Creative Production Project

```markdown
# Project Charter: Brand Refresh Video Campaign

## 1. Project Purpose

Produce a 3-video campaign announcing the company's rebrand, targeting B2B decision-makers, for launch at the annual industry conference.

## 2. Objectives

- 3 videos completed, approved, and delivered by March 1
- Videos achieve 85%+ stakeholder approval rating
- Campaign launch at conference drives 500+ qualified leads

## 3. Scope

**In Scope:**
- 3 videos: 60s flagship, 30s cutdown, 15s social
- Script development, filming, post-production
- Music licensing (stock)
- Two rounds of revisions per video

**Out of Scope:**
- Paid media placement (marketing team)
- Original music composition (budget constraint)
- Photography stills (separate project)

## 4. Budget

Total approved budget: $150,000
- Production company: $95,000
- Talent & locations: $35,000
- Music & stock footage: $12,000
- Contingency: $8,000

## 5. Key Stakeholders

| Role | Person | Authority |
|------|--------|-----------|
| Project Sponsor | CMO | Final approval on all creative |
| Project Manager | [Name] | Day-to-day management |
| Creative Director | [Name] | Creative direction approval |
| Legal/Compliance | [Name] | Brand and legal review |
```

---

## Output

Save to: `docs/charters/[project-name]-charter.md`

Share with: Project Sponsor, Key Stakeholders, Project Manager

---

## Next Steps After Charter Approval

Once this charter is signed:

1. **Create Project Management Plan** — Detailed planning using:
   - `wbs-creator` — Decompose scope into work packages
   - `risk-register` — Detailed risk analysis
   - Schedule tools — Critical path and timeline

2. **Kickoff Project** — Assemble team, begin execution

3. **Establish Baselines** — Scope, schedule, cost baselines for control

---

## Tips for Great Charters

### DO ✅
- Get sponsor input early and often
- Be specific about what's IN and OUT of scope
- Quantify objectives wherever possible
- Document assumptions — they'll be challenged
- Get formal signatures — this is your authority

### Avoid ❌
- Omitting the "out of scope" section — scope creep prevention depends on this
- Including detailed task lists — reserve those for the WBS
- Using vague success criteria — specificity enables verification
- Leaving the PM authority undefined — authority prevents decision paralysis
- Treating the charter as optional — it serves as the PM's protection

---

## Related Skills

| Skill | When to Use |
|-------|-------------|
| `wbs-creator` | After charter approval — decompose scope into work packages |
| `risk-register` | During/after planning — detailed risk analysis |
| `dispatch` | For multi-agent project coordination |
| `feature-specification` | For detailed feature requirements within the project |

---

*"The charter is the contract between the project manager and the sponsor. Without it, you're just guessing."* — PMI
