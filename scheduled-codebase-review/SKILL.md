---
name: scheduled-codebase-review
description: Comprehensive scheduled codebase review using multi-agent analysis. This skill should be used for periodic deep reviews of the entire codebase (every few days), not just recent changes. Creates GitHub issues for findings with ralph-ready label for automated fixing.
---

# Scheduled Codebase Review

Deep, comprehensive codebase analysis designed to run on a schedule (every few days). Unlike PR reviews that focus on diffs, this skill analyzes the entire codebase for security vulnerabilities, architectural issues, technical debt, and opportunities for improvement.

## When to Use This Skill

- Scheduled periodic reviews (every 2-3 days via cron)
- Comprehensive codebase health checks
- Pre-release security and quality audits
- Technical debt assessment
- Onboarding new team members with codebase overview
- Post-incident review to find similar issues

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  1. DISCOVERY - Map codebase structure and recent activity      │
├─────────────────────────────────────────────────────────────────┤
│  2. PARALLEL ANALYSIS - Launch specialized review agents        │
├─────────────────────────────────────────────────────────────────┤
│  3. SYNTHESIS - Deduplicate and prioritize findings             │
├─────────────────────────────────────────────────────────────────┤
│  4. ISSUE CREATION - Post to GitHub with ralph-ready label      │
├─────────────────────────────────────────────────────────────────┤
│  5. REPORT - Generate comprehensive review summary              │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Git repository with GitHub CLI (`gh`) installed and authenticated
- Project has a `.auto-claude/` directory for storing review state
- GitHub issues enabled on the repository

## Execution Instructions

### Phase 1: Discovery and Preparation

<task_list>

- [ ] Create review tracking directory if not exists: `.auto-claude/reviews/`
- [ ] Load previous review state from `.auto-claude/reviews/last-review.json`
- [ ] Get list of existing `ralph-ready` issues to avoid duplicates
- [ ] Analyze project structure to determine relevant review agents
- [ ] Identify high-priority areas:
  - Files changed most frequently (git log --name-only)
  - Files with most authors (potential complexity)
  - Files not reviewed in last 30 days
  - Security-sensitive paths (auth, payments, API, config)

</task_list>

**Project Type Detection:**

```bash
# Detect project stack
ls -la | head -20
cat package.json 2>/dev/null | jq '.dependencies | keys' | head -10
cat Gemfile 2>/dev/null | head -20
cat requirements.txt 2>/dev/null | head -10
```

| Indicator | Review Focus |
|-----------|--------------|
| `Gemfile`, `app/` | Rails: ActiveRecord, controllers, views, Turbo |
| `package.json`, `src/` | Node/React: Components, hooks, state management |
| `requirements.txt`, `*.py` | Python: Type hints, async patterns, security |
| `Cargo.toml` | Rust: Unsafe blocks, error handling |
| `go.mod` | Go: Goroutines, error handling, interfaces |

### Phase 2: Parallel Multi-Agent Analysis

<critical_instruction>
Launch ALL applicable agents in parallel using the Task tool. Each agent analyzes the ENTIRE codebase, not just recent changes.
</critical_instruction>

**Core Review Agents (Always Run):**

```
Launch these agents in PARALLEL:

1. Task security-sentinel("Perform comprehensive security audit of the entire codebase. Check for:
   - Hardcoded secrets, API keys, credentials
   - SQL injection, XSS, CSRF vulnerabilities
   - Insecure deserialization
   - Path traversal vulnerabilities
   - Authentication/authorization bypasses
   - Insecure cryptography
   - OWASP Top 10 issues
   Focus on: auth/, api/, controllers/, config/, .env files")

2. Task performance-oracle("Analyze codebase for performance issues:
   - N+1 queries in database operations
   - Missing database indexes
   - Unbounded queries without pagination
   - Memory leaks and resource exhaustion
   - Inefficient algorithms (O(n²) or worse)
   - Missing caching opportunities
   - Large synchronous operations that should be async")

3. Task architecture-strategist("Review overall architecture:
   - Circular dependencies
   - God classes/modules over 500 lines
   - Violation of single responsibility principle
   - Missing abstraction layers
   - Tight coupling between modules
   - Dead code and unused exports
   - Inconsistent patterns across similar components")

4. Task pattern-recognition-specialist("Identify code patterns and anti-patterns:
   - Duplicated code blocks (DRY violations)
   - Inconsistent naming conventions
   - Missing error handling
   - Magic numbers and strings
   - Overly complex conditionals
   - Functions with too many parameters
   - Deeply nested callbacks/promises")

5. Task code-simplicity-reviewer("Find opportunities for simplification:
   - Over-engineered solutions
   - Unnecessary abstractions
   - YAGNI violations (features not needed)
   - Complex code that could be simpler
   - Redundant null checks
   - Excessive defensive programming")

6. Task agent-native-reviewer("Verify agent accessibility:
   - Features only accessible via UI without API equivalent
   - Missing tool definitions for agent operations
   - Hardcoded workflows that agents can't invoke
   - Missing documentation for agent integration")
```

**Conditional Agents (Based on Project Type):**

```
If Rails project:
7. Task dhh-rails-reviewer("Review Rails code for DHH/37signals conventions:
   - Fat models, skinny controllers
   - Proper use of concerns
   - REST purity and resourceful routes
   - Hotwire patterns (Turbo, Stimulus)
   - Current attributes usage
   - Convention over configuration violations")

8. Task data-integrity-guardian("Check database and data handling:
   - Missing foreign key constraints
   - Orphaned records potential
   - Missing validations
   - Transaction boundaries
   - Data migration safety")

If JavaScript/TypeScript project:
9. Task kieran-typescript-reviewer("Review TypeScript/JS code quality:
   - Type safety and proper typing
   - React hook dependencies
   - State management patterns
   - Bundle size concerns
   - Tree-shaking blockers")

If Python project:
10. Task kieran-python-reviewer("Review Python code quality:
    - Type hints coverage
    - Async/await patterns
    - Import organization
    - Exception handling")
```

### Phase 3: Findings Synthesis

<task_list>

- [ ] Collect all findings from parallel agents
- [ ] Deduplicate findings (same file:line across agents)
- [ ] Cross-reference with existing GitHub issues to avoid duplicates
- [ ] Categorize by severity and type
- [ ] Estimate fix effort for each finding

</task_list>

**Severity Classification:**

| Severity | Criteria | Action |
|----------|----------|--------|
| 🔴 P1 CRITICAL | Security vulnerabilities, data loss risk, production blockers | Create issue immediately, notify team |
| 🟡 P2 IMPORTANT | Performance issues, architectural problems, significant tech debt | Create issue for next sprint |
| 🔵 P3 NICE-TO-HAVE | Code style, minor improvements, optimization opportunities | Create issue, low priority |

**Deduplication Rules:**

1. Same file + same line number = duplicate (keep highest severity)
2. Same issue pattern in multiple files = group into single issue
3. Existing open GitHub issue on same topic = skip
4. Fixed in last 7 days = skip

### Phase 4: GitHub Issue Creation

<critical_instruction>
Create GitHub issues for ALL findings using `gh issue create`. Each issue must have the `ralph-ready` label so Ralph can auto-fix them.
</critical_instruction>

**Issue Template:**

```bash
gh issue create \
  --title "[Review] [SEVERITY] Title - file:line" \
  --label "auto-review" \
  --label "ralph-ready" \
  --label "[severity-label]" \
  --body "$(cat <<'EOF'
## Problem

[Clear description of the issue]

## Location

- **File:** `path/to/file.ext`
- **Line:** [line number or range]
- **Component:** [affected component/module]

## Evidence

[Code snippet or explanation showing the issue]

## Suggested Fix

[Plain text description of how to fix - NO code blocks]

## Impact

- **Severity:** [P1/P2/P3]
- **Type:** [security/performance/architecture/quality]
- **Effort:** [Small/Medium/Large]

## Review Agent

Found by: [agent-name]
Review date: [date]

---
*Auto-generated by scheduled-codebase-review*
EOF
)"
```

**Severity Labels:**

- P1 CRITICAL → `priority:critical`
- P2 IMPORTANT → `priority:high`
- P3 NICE-TO-HAVE → `priority:low`

**Rate Limiting:**

To avoid overwhelming the issue tracker:
- Maximum 10 issues per review session
- Prioritize P1 > P2 > P3
- Group related issues when possible

### Phase 5: Review Report

Generate a comprehensive report saved to `.auto-claude/reviews/`:

```markdown
# Codebase Review Report

**Date:** [ISO date]
**Duration:** [minutes]
**Files Analyzed:** [count]
**Lines of Code:** [count]

## Executive Summary

- **Total Findings:** [count]
- **🔴 Critical:** [count]
- **🟡 Important:** [count]
- **🔵 Nice-to-Have:** [count]
- **Issues Created:** [count]
- **Skipped (duplicates):** [count]

## Findings by Category

### Security
[List of security findings with issue links]

### Performance
[List of performance findings with issue links]

### Architecture
[List of architecture findings with issue links]

### Code Quality
[List of quality findings with issue links]

## Agents Used

| Agent | Findings | Duration |
|-------|----------|----------|
| security-sentinel | [count] | [time] |
| performance-oracle | [count] | [time] |
| ... | ... | ... |

## Areas Needing Attention

1. **[Area 1]** - [summary of issues]
2. **[Area 2]** - [summary of issues]
3. **[Area 3]** - [summary of issues]

## Recommendations

1. [Recommendation based on findings]
2. [Recommendation based on findings]
3. [Recommendation based on findings]

## Next Review

Scheduled: [date + 3 days]
Focus areas: [based on current findings]

---
*Generated by scheduled-codebase-review skill*
```

**Save Report:**

```bash
mkdir -p .auto-claude/reviews
cat > .auto-claude/reviews/review-$(date +%Y%m%d).md << 'EOF'
[report content]
EOF
```

**Update Review State:**

```bash
cat > .auto-claude/reviews/last-review.json << EOF
{
  "date": "$(date -Iseconds)",
  "findings_count": [count],
  "issues_created": [count],
  "files_analyzed": [count],
  "focus_areas": ["area1", "area2"],
  "next_review": "$(date -d '+3 days' -Iseconds 2>/dev/null || date -v+3d -Iseconds)"
}
EOF
```

## Cron Setup

To schedule this review every 3 days:

```bash
# Edit crontab
crontab -e

# Add entry (runs at 3 AM every 3 days)
0 3 */3 * * cd /path/to/project && claude -p "/scheduled-codebase-review" >> ~/.auto-claude/scheduled-review.log 2>&1
```

**Alternative: Wrapper Script**

Create `scripts/scheduled-review.sh`:

```bash
#!/bin/bash
set -e
cd "$(dirname "$0")/.."
echo "[$(date)] Starting scheduled codebase review..."
claude -p "Run the scheduled-codebase-review skill. Analyze the entire codebase, create GitHub issues for findings with ralph-ready label, and generate a comprehensive report."
echo "[$(date)] Review complete."
```

Then in crontab:
```bash
0 3 */3 * * /path/to/project/scripts/scheduled-review.sh >> ~/.auto-claude/scheduled-review.log 2>&1
```

## Integration with Ralph

After review completes, Ralph can automatically fix issues:

```bash
# Fix oldest ralph-ready issue
./ralph --from-issues --pure

# Or fix a specific issue
./ralph --issue 123 --pure
```

**Full automation pipeline:**

```bash
# Review → Create Issues → Fix Issues
./scripts/scheduled-review.sh && ./ralph --from-issues --pure
```

## Customization

### Focus Areas

To focus review on specific areas, modify the agent prompts:

```
Task security-sentinel("Focus security review on: auth/, payments/, api/v2/")
```

### Severity Thresholds

Adjust what gets reported by modifying severity classification in Phase 3.

### Issue Limits

Change the maximum issues per session (default: 10) based on team capacity.

## Troubleshooting

### Too Many Issues Created

- Increase severity threshold (only report P1+P2)
- Reduce agent count
- Add more deduplication rules

### Missing Findings

- Add more specialized agents
- Extend file coverage patterns
- Reduce deduplication aggressiveness

### Review Takes Too Long

- Limit to specific directories
- Run fewer agents
- Use faster models for initial pass

### Duplicate Issues

- Check `.auto-claude/reviews/last-review.json` for state
- Manually close duplicate issues
- Improve deduplication in Phase 3

## Reference

- [OWASP Top 10](https://owasp.org/Top10/)
- [Rails Security Guide](https://guides.rubyonrails.org/security.html)
- [Node.js Security Best Practices](https://nodejs.org/en/docs/guides/security/)
