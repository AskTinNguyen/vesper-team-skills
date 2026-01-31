# Multi-Agent Orchestration — Instruction Manual

How to use the orchestration skills and commands together in real scenarios.

## Quick Reference

| Skill / Command | Invocation | Purpose |
|-----------------|------------|---------|
| `github-sync` | `/github-sync` | Sync PRs/issues between GitHub and task list |
| `agent-supervisor` | `/agent-supervisor` | Monitor agents, track status, flag issues |
| `verify-and-ship` | `/verify-and-ship` | Verify work, commit, push, create PRs |
| `skill-enricher` | `/skill-enricher` | Cross-reference skill with source repo |
| `/dispatch-tests` | `/dispatch-tests [zones]` | Partition and run tests in parallel |
| `/dispatch-issues` | `/dispatch-issues [label:X]` | Pull issues from GitHub, dispatch agents |

All orchestration skills build on top of `/dispatch` for task management and `cc` for session coordination.

---

## Scenario 1: Ship a Multi-Agent Feature Sprint

**Situation:** Multiple agents are working on a feature in parallel. You need to verify their work, ship it, and track PRs through review.

**Agents involved:** Worker agents (via `/dispatch`), verifier, supervisor

### Step-by-Step

```bash
# Terminal 1: Start a coordinated session
cc feature-sprint

# Create and dispatch work tasks
# (use /dispatch as usual to decompose and spawn worker agents)
```

```bash
# Terminal 2: Start the verifier
cc feature-sprint
# Then tell Claude:
# "Act as verify-and-ship in auto-ship mode. Check for uncommitted agent work,
#  verify it, commit, push, and create PRs."
```

```bash
# Terminal 3: Start the supervisor
cc feature-sprint
# Then tell Claude:
# "Act as agent-supervisor in pure supervisor mode. Monitor the task list,
#  flag stalled tasks, create follow-up tasks as needed."
```

### What Happens

1. **Worker agents** (Terminal 1) implement tasks and leave changes uncommitted or on branches
2. **Verifier** (Terminal 2) detects uncommitted work, runs checks, commits, pushes, creates PRs
3. **Supervisor** (Terminal 3) monitors progress, flags stalled workers, creates missing tasks

### Transition to PR Review

Once PRs are created, switch the supervisor to PR tracker mode and the verifier to review-gate mode:

```
# Terminal 2 (verifier):
# "Switch to review-gate mode. Pull open PRs, review each one,
#  fix what you can, flag what needs human attention."

# Terminal 3 (supervisor):
# "Switch to PR status tracker mode. Monitor PR review/merge status
#  and update the task list."
```

---

## Scenario 2: Triage and Fix All Open Issues

**Situation:** A repo has accumulated open GitHub issues. You want to pull them all in, dispatch agents to fix them, and ship the results.

### Step-by-Step

```bash
# Start a coordinated session
cc issue-triage

# Step 1: Dispatch agents for all open issues
# Tell Claude: "/dispatch-issues"
# Or filter: "/dispatch-issues label:bug"
```

This runs `github-sync` to pull issues into the task list, analyzes dependencies, and spawns parallel agents for independent issues.

```bash
# Step 2: Monitor progress (in same or separate terminal)
cc issue-triage
# Tell Claude: "Act as agent-supervisor in pure supervisor mode."
```

```bash
# Step 3: Ship completed work
cc issue-triage
# Tell Claude: "Act as verify-and-ship in auto-ship mode.
#  Verify completed issue fixes, commit, push, create PRs."
```

```bash
# Step 4: Review the PRs
cc issue-triage
# Tell Claude: "Act as verify-and-ship in review-gate mode.
#  Review each PR, fix trivial issues, flag complex ones for human review."
```

### Skill Composition Chain

```
/dispatch-issues
  └─ github-sync (sync-issues-to-tasks.sh)
      └─ TaskCreate per issue
          └─ /dispatch (agent spawning)

agent-supervisor (monitoring)
  └─ poll-tasklist.sh (detect stalls)

verify-and-ship (auto-ship)
  └─ check-agent-output.sh (detect changes)
  └─ verify-and-push.sh (check, commit, push, PR)

verify-and-ship (review-gate)
  └─ github-sync (sync-prs-to-tasks.sh)
  └─ /workflows:review (per PR)
```

---

## Scenario 3: Run Full Test Suite in Parallel

**Situation:** A large project has tests across multiple zones (unit, integration, e2e, etc.). You want to run them all in parallel and get a consolidated report.

### Step-by-Step

```bash
cc test-run

# Auto-detect zones and dispatch:
# Tell Claude: "/dispatch-tests"

# Or specify zones manually:
# Tell Claude: "/dispatch-tests frontend,api,e2e"
```

### What Happens

1. Project structure is scanned for test directories and patterns
2. Tests are grouped into zones (unit, integration, e2e, etc.)
3. A task is created per zone, plus a follow-up documentation task per zone
4. Parallel agents run each zone's tests
5. Results are synthesized into a summary report

### Follow-Up: Fix Failing Tests

If tests fail, combine with issue dispatch:

```
# After test report shows failures:
# Tell Claude: "Create GitHub issues for the test failures,
#  then /dispatch-issues label:test-failure"
```

---

## Scenario 4: PR Review Pipeline

**Situation:** Multiple PRs are open and need review before merging. You want automated review with human oversight for complex issues.

### Step-by-Step

```bash
cc pr-review

# Step 1: Pull PRs into task list
# Tell Claude: "Use github-sync to pull all open PRs into the task list."
```

```bash
# Step 2: Dispatch reviews
# Tell Claude: "Act as verify-and-ship in review-gate mode.
#  Review each PR. Fix trivial issues. Flag complex ones for human review."
```

```bash
# Step 3: Track review status (separate terminal)
cc pr-review
# Tell Claude: "Act as agent-supervisor in PR status tracker mode.
#  Monitor review progress and update task list."
```

### Human Handoff Points

The pipeline creates `[HUMAN]` prefixed tasks for items requiring human judgment:

| Task Prefix | Meaning |
|-------------|---------|
| `[HUMAN]` | General human review needed |
| `[HUMAN][SECURITY]` | Security concern — do not auto-fix |
| `[HUMAN][DESIGN]` | Architecture/design decision needed |
| `[CONFLICT]` | Merge conflict — needs manual resolution |
| `[NEEDS FIX]` | Automated fix failed — manual fix needed |

---

## Scenario 5: Enrich a Skill from Its Source

**Situation:** You created a skill from documentation but it's missing real implementation details.

### Step-by-Step

```
# Tell Claude: "/skill-enricher qmd-search"
# Or: "Enrich the skill at ~/.claude/skills/my-skill from the repo at ~/projects/source-repo"
```

### What Happens

1. Skill contents are read (SKILL.md, scripts/, references/)
2. Source repo is explored (README, configs, entry points, tests, CI)
3. Gap analysis is produced (missing scripts, outdated commands, missing config)
4. A diff report shows what needs updating
5. Skill is updated with real details from the source

### When to Enrich

- After initial skill creation with `/skill-creator`
- When the source project releases a new version
- When agents using the skill report errors or missing steps
- When you notice the skill uses hypothetical commands instead of real ones

---

## Scenario 6: Continuous Integration Loop

**Situation:** You want a long-running orchestration that continuously monitors, verifies, and ships work as agents complete tasks.

### Three-Terminal Setup

```bash
# Terminal 1: Workers (dispatch and implement)
cc continuous

# Terminal 2: Verifier (auto-ship loop)
cc continuous
# "Act as verify-and-ship in auto-ship mode.
#  Continuously check for uncommitted work. After shipping,
#  loop back and check again. Run until all tasks are completed."

# Terminal 3: Supervisor (monitoring loop)
cc continuous
# "Act as agent-supervisor in pure supervisor mode.
#  Poll every 3 minutes. Flag stalls. Create follow-up tasks.
#  When all tasks complete, switch to PR tracker mode and
#  monitor until all PRs are merged."
```

### Lifecycle

```
[Workers implement] ──> [Verifier ships] ──> [PRs created]
        ↑                                          │
        │                                          ↓
[Supervisor creates    <── [Supervisor tracks  <── [Reviews]
 follow-up tasks]           PR status]
```

---

## Scenario 7: Bug Bash

**Situation:** Focus on fixing all bugs in a repo during a bug bash session.

```bash
cc bug-bash

# Pull in all bug issues
# Tell Claude: "/dispatch-issues label:bug"

# In a second terminal, verify and ship fixes
cc bug-bash
# Tell Claude: "Act as verify-and-ship in auto-ship mode."

# In a third terminal, supervise
cc bug-bash
# Tell Claude: "Act as agent-supervisor. Focus on stall detection.
#  If an agent is stuck on a bug for 2 cycles, create a
#  [HUMAN] task and move to the next bug."
```

---

## Composition Rules

### Which skills work together

| Combination | When |
|-------------|------|
| `github-sync` + `agent-supervisor` | Track GitHub state alongside task progress |
| `github-sync` + `verify-and-ship` | Ship work and manage PRs |
| `agent-supervisor` + `verify-and-ship` | Full CI/CD pipeline in the task list |
| `/dispatch-issues` + `verify-and-ship` | Issue-to-PR pipeline |
| `/dispatch-tests` + `verify-and-ship` | Test, fix, and ship |
| `skill-enricher` (standalone) | Improve skills independently |

### Shared requirements

All orchestration skills require:

1. **`CLAUDE_CODE_TASK_LIST_ID`** — set before starting Claude (use `cc <name>`)
2. **`gh` CLI** — authenticated, for any GitHub operations
3. **Same task list** — all terminals must use the same list ID for coordination

### Task list conventions

All skills follow `/dispatch` task conventions:

- Tasks have `subject`, `description`, `activeForm`
- GitHub metadata in descriptions: `pr_number=N` or `issue_number=N`
- Dependencies via `blockedBy` / `blocks`
- Status flow: `pending` -> `in_progress` -> `completed`
- Claiming protocol for multi-terminal: check -> claim with owner -> verify

### Model recommendations

| Role | Model | Reason |
|------|-------|--------|
| Supervisor | sonnet | Light work — monitoring and task creation |
| Verifier | sonnet | Reads diffs, runs checks, creates PRs |
| Worker | sonnet or opus | Implementation work — opus for complex logic |
| Review | sonnet | Code review and triage |

---

## Troubleshooting

### "Tasks not visible across terminals"

All terminals must share the same `CLAUDE_CODE_TASK_LIST_ID`. Use `cc <name>` consistently.

### "github-sync scripts fail"

Check `gh auth status`. The `gh` CLI must be authenticated and have access to the repo.

### "Supervisor creates too many tasks"

Increase the poll interval or stall threshold. The supervisor should observe and flag, not micromanage.

### "Verifier ships broken code"

The `verify-and-push.sh` script auto-detects and runs project checks. If checks are missing from `package.json` or equivalent, add them. The verifier will not ship if checks fail.

### "Agents can't find skills"

Skills must be installed in `~/.claude/skills/` or `~/.vesper/team-skills/`. Check the skill path and ensure SKILL.md exists.
