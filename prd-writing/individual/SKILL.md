---
name: prd-individual
description: "Lightweight PRD generator for individual developers, side projects, and small teams. Fast, focused, and implementation-ready. Use for MVPs, personal projects, hackathons, and small features. Triggers on: quick prd, simple prd, personal project, mvp spec, weekend project."
version: 1.1.0
---

# PRD Generator for Individuals

Create focused, actionable PRDs in **10-20 minutes**. Ship faster with clarity.

---

## The 5-Minute Discovery

Answer these 3 questions (1-2 sentences each):

1. **What problem are you solving?**  
   *"Users struggle with X because Y, which leads to Z"*

2. **What's the smallest version that helps?**  
   *The ONE thing that, if it works, makes this worth building.*

3. **How will you know it works?**  
   *Pick 1 metric or 1 qualitative signal.*

---

## PRD Template (Fill in 10-15 min)

```markdown
# PRD: [Feature Name]

**Status:** Draft | In Progress | Done  
**Created:** YYYY-MM-DD  
**Est. Effort:** [hours/days]  

---

## The Problem

[1-2 sentences. Include evidence if you have it: "I've noticed...", "Users said..."]

## The Solution

[What you're building. Be specific about the user experience.]

**Core Flow:**
1. User [action]
2. System [response]
3. Result [outcome]

## User Stories

### Story 1: [Title]

**As a** [user], **I want** [action], **so that** [benefit].

**Acceptance Criteria:**
- [ ] [Specific, testable condition]
- [ ] [Specific, testable condition]
- [ ] [Edge case]
- [ ] **UI:** Verified in browser

**Notes:** [Files, APIs, links]

### Story 2: [Title]
[Repeat as needed—2-3 stories max]

## Out of Scope

- [ ] [Feature you're NOT building now]
- [ ] [Nice-to-have for later]
- [ ] [Complex variation—v2]

**Why:** [Keep focus]

## Technical Notes

**Stack:** [Your tech]

**Files:**
- `[path]` - [change]
- `[path]` - [change]

## Success Check

**Done when:**
- [ ] [Observable outcome]
- [ ] [User feedback/signal]
```

---

## Complete Example

```markdown
# PRD: Task Priorities

**Status:** Draft  
**Created:** 2024-01-15  
**Est. Effort:** 4 hours  

---

## The Problem

My task list is overwhelming. I can't quickly see what needs attention first.

## The Solution

Add priority levels (high/medium/low) with visual badges and filtering.

**Core Flow:**
1. User edits a task → selects priority from dropdown
2. Task displays colored badge (red/yellow/gray)
3. User filters list by priority

## User Stories

### Story 1: Set Priority

**As a** user, **I want** to set task priority, **so that** I know what to focus on.

**Acceptance Criteria:**
- [ ] Priority dropdown: high/medium/low (default: medium)
- [ ] Saves to database
- [ ] Invalid value shows error
- [ ] **UI:** Verified in browser

**Notes:**
- Add `priority` enum to tasks table
- Migration needed

### Story 2: See Priority Badge

**As a** user, **I want** to see priority in my task list.

**Acceptance Criteria:**
- [ ] Each card shows colored badge
- [ ] High=red, Medium=yellow, Low=gray
- [ ] Visible without hover
- [ ] **UI:** Verified in browser

### Story 3: Filter by Priority

**As a** user, **I want** to filter by priority.

**Acceptance Criteria:**
- [ ] Filter dropdown: All/High/Medium/Low
- [ ] Filter persists in URL
- [ ] Empty state when no matches
- [ ] **UI:** Verified in browser

## Out of Scope

- Auto-priority based on due date
- Priority notifications
- Priority sorting (filter is enough)

**Why:** Keeping to 4 hours.

## Technical Notes

**Stack:** React + TypeScript + Prisma

**Files:**
- `prisma/schema.prisma` - add priority enum
- `src/components/TaskForm.tsx` - add priority select
- `src/components/TaskCard.tsx` - add badge display
- `src/components/TaskFilter.tsx` - new component

## Success Check

**Done when:**
- [ ] I can set priority in under 2 clicks
- [ ] High-priority tasks are visually distinct
- [ ] I use the filter daily for a week
```

---

## Quick Guidelines

### ✅ DO

- **Start with the problem.** If unclear, don't build yet.
- **Limit to 4 hours of work.** If bigger, split the PRD.
- **Write testable criteria.** "Clicking X shows Y" not "works correctly".
- **Include Out of Scope.** Future you will thank present you.
- **Set a success check.** Know when to call it done.

### ❌ DON'T

- Don't write for others unless required.
- Don't design the perfect system. Design the minimal useful one.
- Don't skip Out of Scope. Scope creep kills projects.
- Don't estimate in days. Hours keep you honest.

---

## Story Sizing

Each story = **1-2 hours** of focused work.

| Red Flag | Fix |
|----------|-----|
| >3 acceptance criteria | Split it |
| Touches >4 files | Simplify or split |
| Unclear how to test | Refine criteria |

---

## When to Use Enterprise PRD

Consider upgrading when:
- 🏢 Building for paying customers
- 👥 Need stakeholder approval
- 🔒 Compliance required
- 📊 Success measured in revenue/OKRs
- 🌐 Cross-team dependencies

---

## Output

- **Location:** `.ralph/PRD-N/prd.md` or `docs/prd/[feature].md`
- **Naming:** `prd-[feature]-brief.md`

---

*"The best PRD is the one that gets you building faster."*
