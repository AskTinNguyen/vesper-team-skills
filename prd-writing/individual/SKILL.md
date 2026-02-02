---
name: prd-individual
description: "Lightweight PRD generator for individual developers, side projects, and small teams. Fast, focused, and implementation-ready. Use for MVPs, personal projects, hackathons, and small features. Triggers on: quick prd, simple prd, personal project, mvp spec, weekend project."
version: 1.0.0
---

# PRD Generator for Individuals

Create focused, actionable PRDs that help you ship faster. No corporate overhead—just clarity for your next build.

---

## Philosophy: Ship, Don't Document

Your PRD exists to:
1. **Clarify** your thinking before coding
2. **Remember** what you decided when you come back in 2 weeks
3. **Communicate** with yourself, collaborators, or AI assistants

**Time Budget:** 15-30 minutes max. If it takes longer, your feature is too big—split it.

---

## The 5-Minute Discovery

Ask 3 essential questions. Answer in 1 sentence each:

### Q1: What problem are you solving?
*"Users struggle with X because Y, which leads to Z"*

### Q2: What's the smallest version that helps?
*List the one thing that, if it works, makes this worth building.*

### Q3: How will you know it works?
*Pick 1 metric or 1 qualitative signal.*

---

## PRD Template

Copy this structure. Fill in brackets. Delete sections you don't need.

```markdown
# PRD: [Feature Name]

**Status:** Draft | In Progress | Done  
**Created:** YYYY-MM-DD  
**Est. Effort:** [hours/days]  

---

## The Problem

[1-2 sentences describing the pain point. Include evidence if you have it: "I've noticed...", "Users said..."]

## The Solution

[1 paragraph on what you're building. Be specific about the user experience.]

**Core Flow:**
1. User [action]
2. System [response]
3. Result [outcome]

## User Stories

### US-1: [Title]

**As a** [user type], **I want** [action], **so that** [benefit].

**Acceptance Criteria:**
- [ ] [Specific, testable condition]
- [ ] [Specific, testable condition]
- [ ] [Edge case or constraint]
- [ ] **UI only:** Verified in browser

**Notes:**
- [Any technical notes, API endpoints, file names]
- [Links to designs, references, inspiration]

### US-2: [Title]
[Repeat as needed—aim for 2-4 stories total]

## Out of Scope

**Not building:**
- [Feature that sounds related but isn't essential]
- [Nice-to-have that can come later]
- [Complex variation—save for v2]

**Why:** [Brief rationale—keeps you focused when tempted to add "just one more thing"]

## Technical Notes

**Stack/Approach:**
- [Technology choice and why]
- [Key library or API]

**Files to Touch:**
- `[path/to/file]` - [what you'll change]
- `[path/to/file]` - [what you'll change]

**Open Questions:**
- [What you need to figure out before coding]
- [Decision you're postponing]

## Success Check

**I'll know this is done when:**
- [ ] [Observable outcome]
- [ ] [Metric or user feedback]

**Post-Launch:**
- [What you'll measure or watch for]
- [When you'll decide to iterate or move on]

---

## Context

**How I decided on this scope:**
- [Brief notes on trade-offs considered]
- [Why I excluded certain features]
```

---

## Quick Examples

### Example 1: Personal Task App Feature

```markdown
# PRD: Task Priorities

**Status:** Draft  
**Created:** 2024-01-15  
**Est. Effort:** 4 hours  

---

## The Problem

My task list is overwhelming. I can't quickly see what needs attention first, 
so I waste time scanning or miss important items.

## The Solution

Add priority levels (high/medium/low) to tasks with visual indicators and 
simple filtering.

**Core Flow:**
1. User creates/edits a task
2. User selects priority from dropdown
3. Task displays with colored badge (red/yellow/gray)
4. User can filter list by priority

## User Stories

### US-1: Set Task Priority

**As a** user, **I want** to assign priority to tasks, **so that** I know what to focus on.

**Acceptance Criteria:**
- [ ] Priority field in task form: high/medium/low (default: medium)
- [ ] Priority saves and persists
- [ ] Invalid value shows error
- [ ] Verified in browser

**Notes:**
- Add `priority` column to tasks table
- Enum: 'high' | 'medium' | 'low'
- Migration needed

### US-2: See Priority in List

**As a** user, **I want** to see priority badges in my task list, **so that** 
I can scan quickly.

**Acceptance Criteria:**
- [ ] Each task card shows colored badge
- [ ] High=red, Medium=yellow, Low=gray
- [ ] Badge visible without hover
- [ ] Verified in browser

**Notes:**
- Reuse existing Badge component
- Colors: red-500, yellow-500, gray-400

### US-3: Filter by Priority

**As a** user, **I want** to filter by priority, **so that** I can focus on high-priority work.

**Acceptance Criteria:**
- [ ] Filter dropdown: All/High/Medium/Low
- [ ] Filter persists in URL
- [ ] Empty state when no matches
- [ ] Verified in browser

## Out of Scope

**Not building:**
- Auto-priority based on due date (too complex for now)
- Priority notifications (can add later if needed)
- Priority sorting (filter is enough for MVP)

**Why:** Keeping to 4 hours. Auto-features need more testing.

## Technical Notes

**Stack:** React + TypeScript + Prisma + PostgreSQL

**Files to Touch:**
- `prisma/schema.prisma` - add priority enum
- `src/components/TaskForm.tsx` - add priority select
- `src/components/TaskCard.tsx` - add badge display
- `src/components/TaskFilter.tsx` - new component
- `src/pages/api/tasks.ts` - update endpoints

**Open Questions:**
- Should filter use query params or local state? → Query params (shareable)

## Success Check

**I'll know this is done when:**
- [ ] I can set priority on any task in under 2 clicks
- [ ] My high-priority tasks are visually distinct
- [ ] I use the filter at least once per day for a week

**Post-Launch:**
- Watch: Do I actually use this, or ignore it?
- Decide: If unused after 2 weeks, remove to reduce complexity.
```

---

### Example 2: Side Project MVP

```markdown
# PRD: URL Shortener MVP

**Status:** In Progress  
**Created:** 2024-01-20  
**Est. Effort:** 1 weekend  

---

## The Problem

I share long URLs in tweets and they look messy. Existing shorteners have 
ads or tracking I don't want.

## The Solution

Minimal URL shortener: paste long URL, get short code, redirect works.
No accounts, no analytics, no frills.

**Core Flow:**
1. User pastes long URL into form
2. System generates 6-character code
3. System shows short URL
4. Visiting short URL redirects to original

## User Stories

### US-1: Create Short URL

**As a** visitor, **I want** to paste a long URL, **so that** I get a short one.

**Acceptance Criteria:**
- [ ] Input field accepts URLs
- [ ] Valid URL creates short code
- [ ] Invalid URL shows error message
- [ ] Result displays short URL (copyable)
- [ ] Verified in browser

**Notes:**
- Code: 6 chars, alphanumeric, case-sensitive
- Store: original URL, code, created_at
- Validate URL format (http/https)

### US-2: Redirect to Original

**As a** visitor, **I want** to visit short URL, **so that** I reach the original site.

**Acceptance Criteria:**
- [ ] `/:code` looks up original URL
- [ ] Found → 301 redirect
- [ ] Not found → 404 page
- [ ] Response time < 100ms

**Notes:**
- Redis for caching? Not for MVP—PostgreSQL is fine.
- Index on code column

## Out of Scope

**Not building:**
- Custom short codes (can add later)
- Analytics/click tracking (privacy-focused by design)
- User accounts (keep it simple)
- URL expiration (manual cleanup if needed)

**Why:** One weekend project. Core flow is the value.

## Technical Notes

**Stack:** Next.js + Vercel + PostgreSQL (Neon)

**Files to Touch:**
- `app/page.tsx` - main form
- `app/api/shorten/route.ts` - create endpoint
- `app/[code]/route.ts` - redirect handler
- `lib/db.ts` - database setup

**Open Questions:**
- Handle collisions? → Retry with new code (rare at small scale)

## Success Check

**I'll know this is done when:**
- [ ] I can shorten a URL in under 10 seconds
- [ ] Short URLs work reliably
- [ ] I use it for my own tweets

**Post-Launch:**
- Monitor: Database size
- Decide: If >1000 URLs, add expiration. If popular, add accounts.
```

---

## Guidelines for Good PRDs

### DO ✅

- **Start with the problem.** If you can't articulate it, don't build yet.
- **Limit to 4 hours of work.** If bigger, split into multiple PRDs.
- **Write acceptance criteria you can test.** "Works correctly" is bad. "Clicking X shows Y" is good.
- **Include the "why" in Out of Scope.** Future you will thank present you.
- **Set a success check.** Know when to call it done—and when to kill it.

### DON'T ❌

- **Don't write for others unless you have to.** This is for you.
- **Don't design the perfect system.** Design the minimal useful system.
- **Don't skip Out of Scope.** Scope creep kills side projects.
- **Don't estimate in days if you can help it.** Hours keep you honest.

---

## Story Sizing Guide

Each story should be completable in **1-2 focused hours.**

| If your story has... | It's probably... | Action |
|---------------------|------------------|--------|
| >5 acceptance criteria | Too big | Split it |
| Touches >3 files | Too complex | Simplify or split |
| Needs new API + UI + database | An epic | Break into stories |
| Unclear how to test | Vague | Refine acceptance criteria |

---

## When to Upgrade to Enterprise PRD

Consider the enterprise skill when:
- 🏢 Building for paying customers or employers
- 👥 Need stakeholder approval or budget
- 🔒 Compliance, security, or legal review required
- 📊 Success measured in revenue, retention, or OKRs
- 🤖 AI/ML features with safety considerations
- 🌐 Cross-team dependencies

---

## Quick Reference: PRD Checklist

Before you start coding:

- [ ] Problem is stated in 1-2 sentences
- [ ] Solution is described with core flow
- [ ] User stories have testable acceptance criteria
- [ ] Out of Scope lists at least 2 things you're NOT building
- [ ] You can complete this in [your estimated effort]
- [ ] Success criteria is observable (not "users love it")

---

## Output

- **Format:** Markdown (`.md`)
- **Location:** `.ralph/PRD-N/prd.md` or `docs/prd/[feature].md`
- **Naming:** `prd-[feature]-brief.md`

---

*"The best PRD is the one that gets you building faster, not the one that documents everything."*
