---
name: jeff-review
description: Review progress against plan
argument-hint: "[filter] [--full]"
---

# /jeff-review — Review Progress Against Plan

Assess execution progress and quality.

## Usage
```
/jeff-review
/jeff-review AUTH-*
/jeff-review --full
```

## What This Does

1. **Compare** completed beads vs plan
2. **Check** acceptance criteria were met
3. **Identify** drift from original plan
4. **Suggest** course corrections

## Process

### Step 1: Get Completed Beads
```bash
~/.local/bin/bv --robot-diff --diff-since "24 hours ago"
# Or for full review:
grep '"status":"closed"' .beads/beads.jsonl
```

### Step 2: For Each Completed Bead

Check:
- [ ] All acceptance criteria satisfied?
- [ ] Tests added/passing?
- [ ] Docs updated?
- [ ] Code committed with proper message format?

### Step 3: Assess Plan Alignment

Compare original plan against implementation:
- Any scope creep?
- Any shortcuts taken?
- Any discovered work not in plan?

### Step 4: Check Graph Health
```bash
~/.local/bin/bv --robot-insights | jq '{
  cycles: .Cycles,
  blocked_count: .blocked_count,
  velocity: .velocity
}'
```

## Output

```
📋 PROGRESS REVIEW

**Completed:** 12/47 beads (25%)
**In Progress:** 3
**Blocked:** 5

**Last 24h:**
- ✅ AUTH-001: Set up auth module structure
- ✅ AUTH-002: Implement JWT generation
- ✅ DB-001: Create database schema
- 🔄 AUTH-003: In progress (Coder working)

**Quality Check:**
- AUTH-001: ✅ All acceptance criteria met
- AUTH-002: ⚠️ Missing edge case test for expired tokens
- DB-001: ✅ All criteria met

**Plan Alignment:**
- On track: Core auth flow
- Scope creep: None detected
- Discovered work: +2 beads added (rate limiting, input validation)

**Blockers:**
- AUTH-005 waiting on external API docs
- DB-003 blocked by AUTH-002 (now unblocked)

**Recommendations:**
1. Add missing test for AUTH-002 token expiration
2. Resolve AUTH-005 blocker — need external input
3. Next priority: AUTH-003 (unblocks 4 tasks)

**Velocity:** 4 beads/day → ETA completion: ~9 days
```

## Deep Review (--full)

With `--full` flag, also:
- Read git log for commit quality
- Check code against acceptance criteria
- Verify test coverage
- Assess documentation completeness

## Reference
- Quality standards: `~/.openclaw/workspace/agents/jeff-agent/knowledge/TIPS_AND_BEST_PRACTICES.md`
