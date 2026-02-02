---
name: test-orchestrator
description: Orchestrate comprehensive testing for Frontend and Backend with collaborative 7-step workflow
argument-hint: "[mode] [target]" e.g., "full" or "pr <url>" or "bug <description>"
---

# Test Orchestrator

Orchestrate comprehensive testing for Frontend and Backend with a collaborative 7-step workflow. This command handles everything from clarifying requirements to reporting bugs and suggesting fixes.

## When to Use

- Test entire project: `/test-orchestrator full`
- Test new feature: `/test-orchestrator "Add shopping cart"`
- Test bug fix: `/test-orchestrator bug "Login timeout error"`
- Test PR changes: `/test-orchestrator pr https://github.com/org/repo/pull/123`
- Specific test types: `/test-orchestrator e2e ./e2e`

## 7-Step Collaborative Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                     TEST ORCHESTRATOR                       │
├─────────────────────────────────────────────────────────────┤
│ Step 0: Input Clarification                                 │
│   └── AskUserQuestion until requirements clear              │
│ Step 1: Test Type Identification                            │
│   └── Detect PR / Feature / Bug / Full Suite                │
│ Step 2: Parallel Research                                   │
│   └── repo-research + best-practices + framework-docs       │
│ Step 3: Test Planning                                       │
│   └── MINIMAL / MORE / ALOT (user approval)                 │
│ Step 4: Test Case Generation                                │
│   └── spec-flow-analyzer for comprehensive coverage         │
│ Step 5: Parallel Test Execution                             │
│   └── frontend + backend + e2e + api (simultaneous)         │
│ Step 6: Bug Reporting & User Decision                       │
│   └── Create todos → Present summary → Ask next steps       │
└─────────────────────────────────────────────────────────────┘
```

## Step 0: Input Clarification

**If user input is unclear, use AskUserQuestion to clarify.**

### Input Types

| Type | Pattern | Example |
|------|---------|---------|
| `PR` | URL containing github/gitlab + pull | `https://github.com/org/repo/pull/123` |
| `Bug` | Keywords "bug", "error", "fail", "issue" | `bug "login timeout error"` |
| `Feature` | Feature name or file path | `./src/components/Cart` |
| `Full` | "full", "all", "entire" | `full` |
| `Mode` | "e2e", "api", "frontend", "backend" | `e2e ./e2e` |

### Clarification Questions

**If input is unclear bug report:**
- "Where are you encountering this issue? (Frontend UI, API endpoint, or both?)"
- "Is there a specific error message?"
- "What are the steps to reproduce?"

**If input is unclear feature:**
- "What components does this feature include?"
- "Are there specific user flows that need testing?"
- "What is the priority of this feature? (Critical/High/Medium/Low)"

**If input is PR:**
- "What changes does this PR introduce? (New feature, bug fix, refactor?)"
- "Are there any migrations or breaking changes?"

**Do not proceed until you have clear requirements or user says "proceed".**

## Step 1: Test Type Identification

### 1.1 Parse Input

```
Input: <feature_description> #$ARGUMENTS </feature_description>

If $ARGUMENTS is empty:
  → "What would you like to test? Please describe the feature, bug, or code path."
  → Use AskUserQuestion to clarify
```

### 1.2 Determine Test Scope

| Input Pattern | Test Type | Affected Areas |
|--------------|-----------|----------------|
| `*.tsx, *.jsx, *.vue` | Frontend | Components, Hooks |
| `*.ts, *.js` (server) | Backend | Controllers, Services |
| `*test*, *spec*` | Existing Tests | Run & Report |
| `/api/*` | API | Endpoints, Auth |
| `e2e/, tests/e2e/` | E2E | User flows |
| `pr <url>` | PR Review | Changed files analysis |
| `bug <desc>` | Bug Repro | Reproduction test |

## Step 2: Parallel Research

**Spawn 3 agents in parallel to gather context:**

```typescript
// Parallel Research Phase
const [repoContext, bestPractices, frameworkDocs] = await Promise.all([
  spawnAgent('repo-research-analyst', {
    task: 'Analyze project structure and existing tests',
    context: { targetPath: args.target }
  }),
  spawnAgent('best-practices-researcher', {
    task: 'Research testing best practices for this stack',
    context: { techStack: detectedStack }
  }),
  spawnAgent('framework-docs-researcher', {
    task: 'Gather framework-specific testing documentation',
    context: { framework: detectedFramework }
  })
]);
```

### Research Outputs

| Agent | Output | Purpose |
|-------|--------|---------|
| repo-research-analyst | Project structure, existing tests, tech stack | Context awareness |
| best-practices-researcher | Testing patterns, coverage targets, anti-patterns | Quality standards |
| framework-docs-researcher | Framework-specific APIs, setup guides | Implementation details |

## Step 3: Test Planning

**Choose appropriate detail level:**

### 📄 MINIMAL
**Use for:** Simple bugs, small improvements, clear features

**Structure:**
```yaml
test_plan:
  level: MINIMAL
  target: "Bug fix: Login timeout"
  scope:
    - Reproduction test
    - Fix verification
  deliverables:
    - 1-2 test cases
    - Basic acceptance criteria
```

### 📋 MORE (Default)
**Use for:** Most features, complex bugs, team collaboration

**Structure:**
```yaml
test_plan:
  level: MORE
  target: "Feature: User cart"
  scope:
    frontend:
      - Component tests (Cart, CartItem)
      - Integration tests (add/remove items)
    backend:
      - API tests (POST/GET/DELETE /cart)
      - Service tests (business logic)
    e2e:
      - Critical flow: Add to cart → Checkout
  deliverables:
    - Test cases matrix
    - Coverage targets
    - Risk assessment
```

### 📚 A LOT
**Use for:** Major features, architectural changes, complex integrations

**Structure:**
```yaml
test_plan:
  level: A LOT
  target: "Feature: Payment system integration"
  scope:
    frontend:
      - Component tests
      - State management tests
      - Error boundary tests
      - Accessibility tests
    backend:
      - Unit tests (all layers)
      - Integration tests (payment gateway)
      - Security tests
      - Performance tests
    e2e:
      - All payment flows
      - Error scenarios
      - Edge cases
    api:
      - Contract tests
      - Load tests
  deliverables:
    - Comprehensive test plan
    - Implementation phases
    - Resource requirements
    - Risk mitigation strategies
```

### Planning Checklist

- [ ] Determine test scope (Frontend/Backend/E2E/API)
- [ ] Identify priority areas (P0/P1/P2/P3)
- [ ] Estimate effort (test cases count × complexity)
- [ ] Select detail level (MINIMAL/MORE/ALOT)
- [ ] **Ask user**: "Does this plan look good? Proceed or adjust?"

## Step 4: Test Case Generation

**Use spec-flow-analyzer to generate test cases:**

```typescript
const testCases = await spawnAgent('spec-flow-analyzer', {
  task: 'Generate comprehensive test cases from requirements',
  context: {
    requirements: userInput,
    testPlan: generatedPlan,
    scope: testScope
  }
});
```

### Test Case Format

```markdown
| TC ID | Scenario | Priority | Type | Preconditions | Steps | Test Data | Expected Result |
|-------|----------|----------|------|---------------|-------|-----------|-----------------|
| TC001 | Successful login | P0 | E2E | User exists | 1. Enter email<br>2. Enter password<br>3. Click Login | valid@creds | Redirect to dashboard |
| TC002 | Invalid password | P0 | E2E | User exists | 1. Enter email<br>2. Enter wrong password<br>3. Click Login | valid@wrong | Show error "Invalid credentials" |
```

### Coverage Categories

**For each feature, ensure coverage of:**
- [ ] Happy path (positive scenario)
- [ ] Alternative paths
- [ ] Error handling
- [ ] Edge cases (empty, null, max values)
- [ ] Security (auth, input validation)
- [ ] Accessibility (if UI)

## Step 5: Parallel Test Execution

**Spawn specialized testing agents in parallel:**

```typescript
// Parallel Test Execution
const testResults = await Promise.allSettled([
  // Frontend Tests
  testScope.includes('frontend') && spawnAgent('test-frontend', {
    task: `Test ${target}`,
    context: { coverage: true, framework: detectedFrontend }
  }),

  // Backend Tests
  testScope.includes('backend') && spawnAgent('test-backend', {
    task: `Test ${target}`,
    context: { unit: true, integration: true }
  }),

  // E2E Tests
  testScope.includes('e2e') && spawnAgent('test-e2e', {
    task: `Test critical flows for ${target}`,
    context: { browsers: ['chromium'], visual: false }
  }),

  // API Tests
  testScope.includes('api') && spawnAgent('test-api', {
    task: `Test API endpoints for ${target}`,
    context: { coverage: true, contract: true }
  })
]);
```

### Execution Order

```
┌─────────────────────────────────────────────────────────┐
│                    TEST EXECUTION                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Phase 1: Setup (Sequential)                            │
│    ├── Prepare test data                                │
│    ├── Start test services/containers                   │
│    └── Verify environment                               │
│                                                         │
│  Phase 2: Unit Tests (Parallel)                         │
│    ├── Frontend Components                              │
│    └── Backend Services                                 │
│                                                         │
│  Phase 3: Integration Tests (Parallel)                  │
│    ├── API Tests                                        │
│    └── Database Tests                                   │
│                                                         │
│  Phase 4: E2E Tests (Sequential by flow)                │
│    ├── Critical user paths                              │
│    └── Cross-browser checks                             │
│                                                         │
│  Phase 5: Cleanup                                       │
│    ├── Collect results                                  │
│    ├── Stop services                                    │
│    └── Cleanup test data                                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Step 6: Bug Reporting & User Decision

### 6.1 Bug Classification

| Severity | Criteria | Action Required |
|----------|----------|-----------------|
| 🔴 P1 - Critical | Crash, data loss, security breach | Must fix before merge |
| 🟡 P2 - Important | Feature broken, poor UX | Should fix |
| 🔵 P3 - Nice-to-have | Minor issues, code quality | Fix if time permits |

### 6.2 Create Bug Todo Files

**For each bug found, create a todo file:**

```markdown
<!-- todos/001-pending-p1-login-timeout-error.md -->
---
id: BUG-001
status: pending
priority: p1
severity: critical
type: bug
area: backend
created: 2024-01-15T10:30:00Z
---

# Login Timeout Error

## Problem Statement
Login API returns timeout after 30s when database has >1000 users.

## Findings
- Response time: 35s (Expected: <2s)
- Affected endpoint: POST /api/auth/login
- Root cause: Missing database index on users.email

## Proposed Solutions
1. **Add database index** (Recommended)
   ```sql
   CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
   ```
   - Effort: 5 minutes
   - Risk: Low
   - Impact: Response time <200ms

2. **Implement query caching**
   - Effort: 2 hours
   - Risk: Medium
   - Impact: Reduce DB load

## Acceptance Criteria
- [ ] Login response time < 2s with 10K users
- [ ] No timeout errors in logs
- [ ] Test passes with load of 100 req/s

## Technical Details
- File: `src/services/authService.ts:45`
- Query: `SELECT * FROM users WHERE email = $1`
- Environment: Production, Staging

## Work Log
- 2024-01-15 10:30: Bug reported by test-orchestrator
- 2024-01-15 10:35: Root cause identified
- 2024-01-15 __:__: Fix implemented
```

### 6.3 Present Summary Report

```
╔════════════════════════════════════════════════════════════╗
║              TEST ORCHESTRATION COMPLETE                   ║
╠════════════════════════════════════════════════════════════╣
║  Duration: 4m 12s                                          ║
╠════════════════════════════════════════════════════════════╣
║  TEST RESULTS                                              ║
║  ─────────────                                             ║
║  Total Tests:  156                                         ║
║  Passed:       148 (94.9%)  ✅                             ║
║  Failed:       5   (3.2%)   🔴                             ║
║  Skipped:      3   (1.9%)   ⏭️                             ║
╠════════════════════════════════════════════════════════════╣
║  COVERAGE                                                  ║
║  ─────────                                                 ║
║  Frontend:     87%  ✅                                     ║
║  Backend:      92%  ✅                                     ║
║  API:          89%  ✅                                     ║
║  E2E:          100% ✅ (critical flows)                    ║
╠════════════════════════════════════════════════════════════╣
║  BUGS FOUND                                                ║
║  ──────────                                                ║
║  🔴 P1 Critical: 2 bugs (require immediate fix)            ║
║     • BUG-001: Login timeout error                         ║
║     • BUG-002: Race condition in checkout                  ║
║                                                            ║
║  🟡 P2 Important: 3 bugs (should fix)                      ║
║     • BUG-003: Missing validation on email field           ║
║     • BUG-004: Flaky test in pagination                    ║
║     • BUG-005: Console warning in dev mode                 ║
║                                                            ║
║  🔵 P3 Nice-to-have: 0 bugs                                ║
╠════════════════════════════════════════════════════════════╣
║  Report: ./test-reports/report-2024-01-15.html             ║
╚════════════════════════════════════════════════════════════╝
```

### 6.4 User Decision Point

**Use AskUserQuestion to ask user:**

```
I found 5 issues (2 P1 critical, 3 P2 important).

What would you like to do next?

Options:
1. 🔴 Fix P1 bugs now (I'll create PRs)
2. 📝 Create GitHub issues for all bugs
3. 🎯 Create issues for P1 bugs only
4. ⏭️ Skip this time, continue other work
5. 📊 View details of each bug before deciding
```

**If user chooses to fix bugs:**
```
How would you like to fix the bugs?

Options:
1. I'll fix all (auto-create PR)
2. Fix one by one (confirm each)
3. Only suggest fixes, you implement
4. Group into 1 PR or separate per bug?
```

### 6.5 Post-Test Actions

| User Choice | Action |
|-------------|--------|
| "Fix now" | Spawn work agents, create PRs |
| "Create issues" | Use `report-bug` skill for each bug |
| "Skip" | Mark todos as `wontfix`, record reason |
| "View details" | Show details of each todo file |

## Example Workflows

### Example 1: Bug Fix Verification

```
User: /test-orchestrator bug "Login fails with special characters"

Step 0: Clarify
→ "Where are you seeing this? (Frontend form validation or API?)"
→ User: "Both, entering 'test@user+1.com' shows invalid"

Step 1: Identify
→ Type: Bug
→ Scope: Frontend + Backend
→ Priority: P1 (affects user registration)

Step 2: Research
→ Run 3 agents in parallel

Step 3: Plan
→ Level: MINIMAL (clear bug)
→ Scope: Repro test + Fix verification

Step 4: Generate Cases
→ TC001: Register with email containing '+' → Should succeed
→ TC002: Login with email containing '+' → Should succeed

Step 5: Execute
→ Create reproduction test
→ Test fails (confirm bug exists)
→ Show user: "Bug confirmed. Want me to fix it?"

Step 6: Decision
→ User: "Fix it"
→ Spawn work agent, create PR
→ Close todos
```

### Example 2: Feature Testing

```
User: /test-orchestrator "Add cart feature"

Step 0: Clarify
→ "What does this feature include?"
→ User: "Add to cart, view cart, remove item, checkout"

Step 1: Identify
→ Type: Feature
→ Scope: Frontend + Backend + E2E

Step 2-4: Plan & Cases
→ Level: MORE
→ 15 test cases generated

Step 5: Execute
→ Run all test types in parallel
→ 148/156 pass
→ 8 bugs found

Step 6: Report
→ "Found 8 bugs. 2 P1 need to be fixed before release."
→ AskUserQuestion for next steps
```

## Output Formats

### Test Plan File
```
test-plans/
├── test-plan-{timestamp}-{feature-name}.md
└── test-cases-{timestamp}-{feature-name}.md
```

### Bug Todo Files
```
todos/
├── {id}-pending-p1-{description}.md
├── {id}-pending-p2-{description}.md
└── {id}-ready-p1-{description}.md  (after user approves fix)
```

### Test Report
```
test-reports/
├── report-{timestamp}.html
├── report-{timestamp}.json
└── coverage/
    ├── frontend/
    ├── backend/
    └── api/
```

## Integration with Other Skills

| Skill | Usage |
|-------|-------|
| `test-frontend` | Component testing |
| `test-backend` | API & service testing |
| `test-e2e` | Browser automation |
| `test-api` | REST/GraphQL testing |
| `report-bug` | Create GitHub issues |
| `workflows:work` | Implement fixes |
| `dispatch` | Parallel agent execution |

## Best Practices

### ✅ DO
- Always clarify input before proceeding
- Run research agents in parallel
- Generate test plan before executing
- Create todo files for bugs found
- Ask user before creating PR/fix
- Cleanup test data after each run

### ❌ DON'T
- Proceed when requirements are unclear
- Skip P1 bugs without notifying user
- Auto-fix bugs without asking
- Forget to cleanup test environment
- Hard-code test data
