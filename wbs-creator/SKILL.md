---
name: wbs-creator
description: Create a Work Breakdown Structure (WBS) following PMI standards. Use when planning projects, decomposing scope into work packages, estimating effort, assigning resources, or creating project schedules. Triggers on "create WBS", "work breakdown structure", "decompose scope", "work packages", "WBS dictionary", "scope decomposition", "project plan", "task breakdown", "what needs to be done".
allowed-tools: [Read, Write, Bash, Grep]
preconditions:
  - Project Charter approved (or clear scope defined)
  - Scope statement available
  - Project team/stakeholders available for input
---

# Work Breakdown Structure (WBS) Creator

Decompose project scope into manageable work packages following PMI's "100% Rule" — the WBS includes 100% of the work defined by the project scope and captures ALL deliverables.

---

## When to Use This Skill

| Scenario | Use This Skill |
|----------|----------------|
| Planning a new project | ✅ Decompose charter scope into work packages |
| Estimating effort/cost | ✅ Break work down for accurate estimation |
| Assigning resources | ✅ Identify who does what work package |
| Tracking progress | ✅ Create basis for scheduling and earned value |
| Preventing scope creep | ✅ Clear definition of what's included |
| Agile/Scrum planning | ✅ Epic → Feature → Story decomposition |

---

## The 100% Rule

> The WBS must capture **100% of the work** defined by the project scope. Anything not in the WBS is **out of scope**. Anything in the WBS must be completed.

### Verification Checklist
- [ ] All deliverables from charter are represented
- [ ] Project management work is included (not just product work)
- [ ] No work is duplicated across branches
- [ ] Lowest level is a work package (can be estimated, scheduled, assigned)

---

## WBS Creation Process

### Step 1: Identify Major Deliverables
Start with the deliverables from your Project Charter.

### Step 2: Choose Decomposition Approach

| Approach | PMI Preference | Best For | Example |
|----------|----------------|----------|---------|
| **Deliverable-based** | ✅ **Primary** — PMI standard | Product-focused projects | Design → Build → Test → Deploy |
| **Phase-based** | Alternative | Sequential, process-heavy projects | Initiation → Planning → Execution → Closure |
| **Geographic** | Alternative | Multi-location projects | US Region → EU Region → APAC Region |
| **Organizational** | Alternative | Cross-functional handoffs | Marketing → Engineering → QA → Ops |

**PMI Recommendation:** Use deliverable-based WBS as the default. Deliverables focus on outcomes (nouns) rather than activities (verbs), making the WBS more stable and easier to verify for completeness.

### Step 3: Decompose to Work Packages
Continue breaking down until you reach the **work package** level:

**Work Package Criteria:**
- Can be realistically estimated (effort, cost, duration)
- Can be assigned to a specific person or team
- Can be scheduled with start/end dates
- Can be tracked and measured for completion

**Typical depth:** 3-6 levels depending on project complexity

### Step 4: Number and Code
Assign unique identifiers for tracking:

```
1.0 Project
  1.1 Major Deliverable
    1.1.1 Sub-deliverable
      1.1.1.1 Work Package
      1.1.1.2 Work Package
    1.1.2 Sub-deliverable
  1.2 Major Deliverable
```

### Step 5: Create WBS Dictionary
Document each work package in detail (see template below).

---

## The Scope Baseline

Per PMI standards, the **Scope Baseline** consists of three components:

```
┌─────────────────────────────────────────┐
│           SCOPE BASELINE                 │
├─────────────────────────────────────────┤
│  1. Project Scope Statement             │
│     └─ Narrative description of scope,  │
│        deliverables, assumptions,       │
│        constraints                      │
├─────────────────────────────────────────┤
│  2. WBS                                 │
│     └─ Hierarchical decomposition       │
│        of all work                      │
├─────────────────────────────────────────┤
│  3. WBS Dictionary                      │
│     └─ Detailed description of each     │
│        work package                     │
└─────────────────────────────────────────┘
              ↓
     Approved baseline for changes
```

**Baseline Change Control:**
- All three components move together
- Changes require formal Change Control Board (CCB) approval
- Version control maintains history

---

## WBS Templates

### Template 1: Software Development (Deliverable-Based)

```markdown
# WBS: [Project Name]

## 1.0 Project Management
  1.1 Project Initiation
    1.1.1 Charter Development
    1.1.2 Stakeholder Analysis
    1.1.3 Kickoff Meeting
  1.2 Project Planning
    1.2.1 Scope Planning (WBS)
    1.2.2 Schedule Development
    1.2.3 Budget Development
    1.2.4 Risk Planning
    1.2.5 Communication Planning
  1.3 Project Execution
    1.3.1 Status Reporting
    1.3.2 Change Management
    1.3.3 Quality Assurance
  1.4 Project Closure
    1.4.1 Lessons Learned
    1.4.2 Final Report
    1.4.3 Archive Documentation

## 2.0 Requirements & Design
  2.1 Requirements Gathering
    2.1.1 Stakeholder Interviews
    2.1.2 Requirements Workshops
    2.1.3 Requirements Documentation
    2.1.4 Requirements Sign-off
  2.2 System Design
    2.2.1 Architecture Design
    2.2.2 Database Design
    2.2.3 API Design
    2.2.4 UI/UX Design
    2.2.5 Design Review & Approval

## 3.0 Development
  3.1 Backend Development
    3.1.1 Database Implementation
    3.1.2 API Development
    3.1.3 Business Logic Implementation
    3.1.4 Integration Development
  3.2 Frontend Development
    3.2.1 Component Library
    3.2.2 Core Pages/Screens
    3.2.3 User Workflows
    3.2.4 Responsive/Adaptive Implementation
  3.3 Third-Party Integrations
    3.3.1 Authentication Integration
    3.3.2 Payment Integration
    3.3.3 External API Integration

## 4.0 Quality Assurance
  4.1 Test Planning
    4.1.1 Test Strategy
    4.1.2 Test Case Development
  4.2 Testing
    4.2.1 Unit Testing
    4.2.2 Integration Testing
    4.2.3 System Testing
    4.2.4 UAT (User Acceptance Testing)
    4.2.5 Performance Testing
    4.2.6 Security Testing
  4.3 Bug Fixing
    4.3.1 Bug Triage
    4.3.2 Critical Bug Fixes
    4.3.3 Bug Regression Testing

## 5.0 Deployment
  5.1 Environment Setup
    5.1.1 Production Environment
    5.1.2 Staging Environment
    5.1.3 Monitoring Setup
  5.2 Data Migration
    5.2.1 Migration Scripts
    5.2.2 Data Validation
  5.3 Release
    5.3.1 Deployment Execution
    5.3.2 Smoke Testing
    5.3.3 Rollback Plan (if needed)

## 6.0 Training & Documentation
  6.1 User Documentation
    6.1.1 User Guides
    6.1.2 FAQ Development
  6.2 Training
    6.2.1 Training Materials
    6.2.2 Training Sessions
    6.2.3 Train-the-Trainer
```

### Template 2: Creative/Video Production (Phase-Based)

```markdown
# WBS: [Campaign Name]

## 1.0 Pre-Production
  1.1 Creative Development
    1.1.1 Creative Brief
    1.1.2 Concept Development
    1.1.3 Script Writing
    1.1.4 Storyboard Creation
    1.1.5 Client Approval
  1.2 Planning
    1.2.1 Budget Finalization
    1.2.2 Schedule Development
    1.2.3 Location Scouting
    1.2.4 Talent Casting
    1.2.5 Crew Assembly
    1.2.6 Equipment Booking
  1.3 Pre-Production Meetings
    1.3.1 Production Meeting
    1.3.2 Tech Scout
    1.3.3 Final PPM

## 2.0 Production
  2.1 Shoot Day 1: [Location/Scene]
    2.1.1 Setup
    2.1.2 Blocking & Rehearsal
    2.1.3 Principal Photography
    2.1.4 Strike
  2.2 Shoot Day 2: [Location/Scene]
    [Same structure]
  2.3 B-Roll / Additional Footage
    2.3.1 Location B-Roll
    2.3.2 Product Shots
    2.3.3 Pickup Shots

## 3.0 Post-Production
  3.1 Editorial
    3.1.1 Assembly Edit
    3.1.2 Rough Cut
    3.1.3 Fine Cut
    3.1.4 Picture Lock
  3.2 Sound
    3.2.1 Dialogue Edit
    3.2.2 Sound Design
    3.2.3 Music Composition/Licensing
    3.2.4 Mix
  3.3 Visual Effects
    3.3.1 VFX Planning
    3.3.2 Graphics/Animation
    3.3.3 Color Correction
    3.3.4 Final Online
  3.4 Deliverables
    3.4.1 Master File Creation
    3.4.2 Format Conversions
    3.4.3 Quality Control

## 4.0 Delivery & Wrap
  4.1 Client Delivery
    4.1.1 Review Cuts (Round 1, 2, 3)
    4.1.2 Final Approval
    4.1.3 Asset Delivery
  4.2 Project Wrap
    4.2.1 Archive Assets
    4.2.2 Final Accounting
    4.2.3 Lessons Learned
```

### Template 3: Event Planning (Hybrid)

```markdown
# WBS: [Event Name]

## 1.0 Event Management
  1.1 Planning
  1.2 Coordination
  1.3 On-Site Management
  1.4 Post-Event

## 2.0 Venue
  2.1 Selection
  2.2 Contracting
  2.3 Setup
  2.4 Breakdown

## 3.0 Content & Programming
  3.1 Agenda Development
  3.2 Speaker Management
  3.3 Materials Production

## 4.0 Attendees
  4.1 Registration System
  4.2 Communications
  4.3 On-Site Experience

## 5.0 Vendors
  5.1 Catering
  5.2 AV/Production
  5.3 Decor/Staging
  5.4 Transportation
```

---

## WBS Dictionary Template

Create a dictionary entry for each work package:

```markdown
## WBS Dictionary: [Project Name]

### 1.1.1 Charter Development

| Field | Value |
|-------|-------|
| **WBS Code** | 1.1.1 |
| **Work Package Name** | Charter Development |
| **Description** | Create formal project charter document including business case, objectives, scope, budget, timeline, and obtaining sponsor approval. |
| **Acceptance Criteria** | Charter document completed, reviewed by sponsor, formally signed. |
| **Deliverables** | Approved Project Charter |
| **Dependencies** | Business case approval |
| **Responsible** | Project Manager |
| **Estimated Effort** | 16 hours |
| **Estimated Cost** | $1,600 |
| **Start Date** | [Date] |
| **End Date** | [Date] |

---

### 2.2.4 UI/UX Design

| Field | Value |
|-------|-------|
| **WBS Code** | 2.2.4 |
| **Work Package Name** | UI/UX Design |
| **Description** | Design all user interfaces including wireframes, high-fidelity mockups, interactive prototypes, and design system components. |
| **Acceptance Criteria** | All screens designed, prototype functional, design review approved by stakeholders. |
| **Deliverables** | Design files, clickable prototype, design system documentation |
| **Dependencies** | 2.1.4 Requirements Sign-off |
| **Responsible** | UX Designer |
| **Estimated Effort** | 80 hours |
| **Estimated Cost** | $8,000 |
| **Start Date** | [Date] |
| **End Date** | [Date] |

---

### [Continue for all work packages...]
```

---

## Work Package Sizing Guidelines

| Project Type | Work Package Duration | Work Package Effort |
|--------------|----------------------|---------------------|
| Small project (< 3 months) | 1-2 weeks | 8-40 hours |
| Medium project (3-12 months) | 2-4 weeks | 40-160 hours |
| Large project (> 12 months) | 1-3 months | 160-480 hours |

**Rules of Thumb:**
- 8/80 Rule: Work packages should be between 8 and 80 hours
- Reporting Period: Work packages should match your reporting cadence (weekly/monthly)
- Control Account: Group work packages for earned value tracking

---

## WBS Quality Checklist

Before finalizing your WBS, verify:

### Structure
- [ ] Follows 100% Rule — all scope captured, nothing extra
- [ ] Uses noun-based deliverables (not verbs/tasks)
- [ ] Mutually exclusive — no overlap between elements
- [ ] Hierarchical — each level is a full decomposition of the parent

### Work Packages
- [ ] Lowest level = work package (can be estimated, scheduled, assigned)
- [ ] Consistent level of detail across similar work
- [ ] Includes project management work (not just product)
- [ ] Includes integration/testing/deployment work

### Documentation
- [ ] Each work package has dictionary entry
- [ ] Acceptance criteria are clear and testable
- [ ] Dependencies identified
- [ ] Responsible party assigned

---

## Output Files

Create these artifacts:

1. **WBS Structure:** `docs/planning/[project]-wbs.md`
2. **WBS Dictionary:** `docs/planning/[project]-wbs-dictionary.md`
3. **WBS Visual** (optional): Create in tool like Lucidchart, Miro, or Excel

---

## Next Steps After WBS

Once WBS is complete:

1. **Estimate Work Packages** — Effort, duration, cost for each
2. **Create Schedule** — Sequence work packages, identify dependencies
3. **Assign Resources** — Match work packages to team members
4. **Establish Baseline** — Approved WBS becomes scope baseline

Related skills:
- `risk-register` — Identify risks at work package level
- `dispatch` — Distribute work packages to agents/teams
- `earned-value-analysis` — Track progress against work packages

---

## Tips for Great WBS

### DO ✅
- Decompose to the level you can manage and estimate
- Use deliverable-oriented language (nouns, not verbs)
- Include "Project Management" as a major deliverable
- Get team input — those doing the work know it best
- Review against charter scope — 100% Rule verification

### DON'T ❌
- Create a task list — this is deliverable decomposition
- Decompose everything to the same level — some need more detail
- Forget integration/testing — it's work that must be done
- Plan in isolation — involve the team
- Make it so granular it becomes unmanageable

---

## Related Skills

| Skill | Relationship |
|-------|--------------|
| `project-charter` | Input — charter scope becomes WBS |
| `risk-register` | Parallel — identify risks per work package |
| `dispatch` | Execution — assign work packages to agents |
| `earned-value-analysis` | Control — track progress by work package |

---

*"The WBS is the foundation of project management. Everything else — schedule, budget, resources — builds on this structure."* — PMI
