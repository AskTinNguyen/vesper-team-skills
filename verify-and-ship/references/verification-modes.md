# Verification Modes — Detailed Reference

## Mode 1: Auto-Ship — Decision Tree

```
Start
  │
  ├─ Run check-agent-output.sh
  │   ├─ No changes → Report clean, check next task
  │   └─ Changes found → Continue
  │
  ├─ Review diff
  │   ├─ Looks correct → Continue to verify
  │   ├─ Obvious errors → Fix first, then verify
  │   └─ Unclear intent → Create [REVIEW NEEDED] task, skip
  │
  ├─ Run verify-and-push.sh --dry-run
  │   ├─ All checks pass → Continue to commit
  │   ├─ Lint errors only → Run auto-fix, re-verify
  │   ├─ Type errors → Attempt fix, re-verify (max 2 attempts)
  │   ├─ Test failures → Analyze failure
  │   │   ├─ Trivial fix → Fix, re-verify
  │   │   └─ Non-trivial → Create [NEEDS FIX] task, skip
  │   └─ No checks available → Proceed with caution
  │
  ├─ Run verify-and-push.sh --message "..." --branch "..."
  │   ├─ Success → Update task status
  │   └─ Failure → Log error, create task
  │
  └─ Loop to next set of changes
```

## Mode 2: Review-Gate — Workflow

### Step-by-Step

1. **Populate review queue:**
   ```bash
   bash ~/.claude/skills/github-sync/scripts/sync-prs-to-tasks.sh
   ```

2. **For each PR task (in order):**
   - Check out the PR branch locally
   - Dispatch review:
     ```
     Skill(workflows:review, args: "PR #N")
     ```
   - Process review results

3. **Batch mode (>3 PRs):**
   ```
   Skill(workflows:bulk-review)
   ```

### Review Result Triage

| Review Outcome | Action |
|---------------|--------|
| No issues found | Add "Approved" note to task |
| Style/formatting issues | Auto-fix, push, re-request review |
| Logic bugs (clear fix) | Fix, push, re-request review |
| Logic bugs (unclear) | Create `[HUMAN]` task with details |
| Security concerns | Create `[HUMAN][SECURITY]` task, do NOT fix |
| Architecture concerns | Create `[HUMAN][DESIGN]` task |
| Missing tests | Add tests, push, re-request review |
| Merge conflicts | Create `[CONFLICT]` task |

### Fix Attempt Limits

- **Maximum 2 fix attempts per PR** — after that, escalate to human
- **Never fix security issues** — always escalate
- **Track fix attempts** in task description

## Mode 3: Status-Update — What to Track

### Task Status Mapping

The status-update mode observes these task fields and keeps them current:

| Observation | Task Update |
|-------------|-------------|
| Review agent completed, no issues | Mark review task completed |
| Review agent completed, issues found | Keep in_progress, add findings note |
| Fix agent completed successfully | Mark fix task completed |
| Fix agent failed | Flag for human escalation |
| PR merged externally | Mark all related tasks completed |
| PR closed externally | Mark related tasks completed with note |

### Monitoring Checklist

Each cycle:

- [ ] Check all review tasks for completion
- [ ] Check all fix tasks for completion
- [ ] Cross-reference with `github-sync/pr-status-check.sh`
- [ ] Identify orphaned tasks (no agent, no progress)
- [ ] Create summary report

## Common Verification Checks by Project Type

### Node.js / TypeScript
```bash
npm run lint          # ESLint
npm run typecheck     # tsc --noEmit
npm test              # Jest/Vitest/Mocha
```

### Python
```bash
ruff check .          # Linting
mypy .                # Type checking
pytest --tb=short -q  # Tests
```

### Go
```bash
go vet ./...          # Static analysis
go test ./...         # Tests
golangci-lint run     # Extended linting (if available)
```

### Rust
```bash
cargo check           # Compilation check
cargo clippy          # Linting
cargo test            # Tests
```

## PR Creation Conventions

When creating PRs via auto-ship:

- **Title:** Use the commit message (conventional commit format)
- **Body:** Include summary of changes and list of files
- **Labels:** Add automatically if detectable (bug fix -> "bug", new feature -> "enhancement")
- **Reviewers:** Do not auto-assign (let the repo's CODEOWNERS handle it)
- **Draft:** Create as draft if checks had warnings (not errors)
