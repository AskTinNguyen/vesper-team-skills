# Testing Suite for Claude Code

A comprehensive testing suite for Claude Code that orchestrates Frontend, Backend, E2E, and API testing with a collaborative 7-step workflow.

## Overview

This testing suite provides intelligent test orchestration that:
- Clarifies requirements before testing
- Runs parallel research and test execution
- Classifies and tracks bugs (P1/P2/P3)
- Asks before creating PRs or fixes

## Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/test-orchestrator` | Main orchestrator with collaborative workflow | Entry point for all testing |
| `/test-frontend` | Component testing (React/Vue/Svelte/Angular) | UI component validation |
| `/test-backend` | Unit & integration testing | API services, business logic |
| `/test-e2e` | Browser automation testing | Critical user flows |
| `/test-api` | REST & GraphQL API testing | Endpoint validation |

## Installation

### For Users

Add to your `.claude/commands/` directory:

```bash
# Clone the repository
git clone https://github.com/AskTinNguyen/vesper-team-skills.git

# Copy commands to your Claude Code setup
cp -r vesper-team-skills/commands/workflows/*.md ~/.claude/commands/
```

### For Teams

Add as a git submodule to your project:

```bash
git submodule add https://github.com/AskTinNguyen/vesper-team-skills.git .claude/skills
```

## Quick Start

### Test Entire Project
```bash
/test-orchestrator full
```

### Test New Feature
```bash
/test-orchestrator "Add shopping cart functionality"
```

### Test Bug Fix
```bash
/test-orchestrator bug "Login timeout after 30 seconds"
```

### Test Pull Request
```bash
/test-orchestrator pr https://github.com/org/repo/pull/123
```

## 7-Step Collaborative Workflow

The `/test-orchestrator` command follows a structured workflow:

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

## Bug Classification

| Severity | Criteria | Action Required |
|----------|----------|-----------------|
| 🔴 **P1 - Critical** | Crash, data loss, security breach | Must fix before merge |
| 🟡 **P2 - Important** | Feature broken, poor UX | Should fix |
| 🔵 **P3 - Nice-to-have** | Minor issues, code quality | Fix if time permits |

## Output Structure

### Test Plans
```
test-plans/
├── test-plan-{timestamp}-{feature}.md
└── test-cases-{timestamp}-{feature}.md
```

### Bug Tracking (Todos)
```
todos/
├── {id}-pending-p1-{description}.md   # Critical bugs
├── {id}-pending-p2-{description}.md   # Important bugs
├── {id}-ready-p1-{description}.md     # Approved for fix
└── {id}-complete-p3-{description}.md  # Fixed bugs
```

### Test Reports
```
test-reports/
├── report-{timestamp}.html
├── report-{timestamp}.json
└── coverage/
    ├── frontend/
    ├── backend/
    └── api/
```

## Supported Technologies

### Frontend
- **Frameworks**: React, Vue, Svelte, Angular
- **Test Runners**: Vitest, Jest
- **Libraries**: React Testing Library, Vue Test Utils

### Backend
- **Languages**: Node.js, Python, Ruby, Go
- **Frameworks**: Express, Fastify, FastAPI, Rails
- **Test Frameworks**: Jest, Vitest, pytest, RSpec

### E2E
- **Tool**: Playwright
- **Browsers**: Chromium, Firefox, WebKit
- **Features**: Visual regression, mobile emulation

### API
- **Protocols**: REST, GraphQL
- **Tools**: pytest, httpx, schemathesis (contract testing)

## Example Workflows

### Feature Development
```bash
# 1. Start testing
/test-orchestrator "Add payment integration"

# 2. Answer clarification questions
→ "What payment methods?"
→ User: "Stripe and PayPal"

# 3. Review and approve test plan
→ "Plan: MORE level, 15 test cases"
→ User: "OK, proceed"

# 4. Automated test execution
→ Runs frontend + backend + e2e + api tests

# 5. Review results
→ "Found 3 bugs (1 P1, 2 P2)"
→ User selects: "🔴 Fix P1 bugs now"

# 6. Automatic fix and PR creation
→ Creates branch → implements fix → creates PR
```

### Bug Reproduction
```bash
# Report bug
/test-orchestrator bug "Checkout fails with discount code"

# Answer questions
→ "Frontend or backend?"
→ User: "Backend API returns 500"

# Creates reproduction test
→ Test confirms bug exists

# User decision
→ "Bug confirmed. Want me to fix?"
→ User: "Yes"

# Automatic fix
→ Analyzes root cause → implements fix → verifies
```

## Integration with Sub-Skills

```
                    /test-orchestrator
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   /test-frontend    /test-backend      /test-e2e
   (Components)      (Services/API)    (Browser)
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                      /test-api
                    (REST/GraphQL)
```

## Best Practices

### Do's ✅
- Always clarify requirements first
- Get user approval for test plans
- Run tests in parallel for efficiency
- Create todo files immediately for bugs
- Ask before fixing or creating PRs
- Clean up test data after runs

### Don'ts ❌
- Don't proceed with unclear requirements
- Don't skip P1 bugs without user approval
- Don't auto-fix bugs without asking
- Don't forget cleanup
- Don't hard-code test data

## Configuration

### Environment Variables
```bash
# Test Orchestrator
TEST_PARALLEL=true
TEST_COVERAGE_THRESHOLD=80
TEST_FAIL_FAST=false

# E2E Tests
BASE_URL=http://localhost:3000
PLAYWRIGHT_BROWSERS=chromium,firefox,webkit

# API Tests
API_BASE_URL=http://localhost:8000/api/v1
TEST_USER_EMAIL=test@example.com
```

## Troubleshooting

### Common Issues

**Tests pass locally but fail in CI**
- Check timing issues (add waitFor)
- Verify environment variables
- Check for race conditions

**Flaky tests**
- Use auto-waiting instead of fixed delays
- Isolate test data
- Check for async issues

**Slow tests**
- Enable parallel execution
- Use testcontainers for DB
- Optimize test data setup

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Support

- Issues: [GitHub Issues](https://github.com/AskTinNguyen/vesper-team-skills/issues)
- Discussions: [GitHub Discussions](https://github.com/AskTinNguyen/vesper-team-skills/discussions)

---

**Built for Claude Code** | **Parallel Testing** | **Collaborative Workflow**
