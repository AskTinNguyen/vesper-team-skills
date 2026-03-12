# Example: OAuth Authentication Feature

**User request:** "Add user authentication with OAuth"

This example starts with a universal task plan, then shows one Claude Code-flavored adapter snippet at the end.

## Universal Task Plan

| ID | Subject | Capability | Files | Evidence |
|----|---------|------------|-------|----------|
| 1 | Design authentication architecture | `planner` | `docs/auth-design.md` | architecture doc |
| 2 | Create user model and migrations | `builder` | `src/models/user.ts`, `db/migrations/*` | migration + model diff |
| 3 | Implement OAuth provider integration | `builder` | `src/auth/providers/*` | provider flows work |
| 4 | Build login and logout endpoints | `builder` | `src/api/auth.ts` | endpoint tests |
| 5 | Add session management middleware | `builder` | `src/middleware/auth.ts`, `src/utils/jwt.ts` | auth middleware tests |
| 6 | Write authentication tests | `builder` | `tests/auth/*` | passing test run |
| 7 | Update API documentation | `lightweight` | `docs/api.md`, `docs/authentication.md` | docs updated |

## Dependencies

- `2` blocked by `1`
- `3` blocked by `1`
- `4` blocked by `2`, `3`
- `5` blocked by `2`
- `6` blocked by `4`, `5`
- `7` blocked by `4`

## Execution Phases

- Phase 1: `[1]` design
- Phase 2: `[2, 3]` model and OAuth in parallel
- Phase 3: `[4, 5]` endpoints and middleware in parallel
- Phase 4: `[6, 7]` tests and docs in parallel

## Expected Coordinator Checks

- After Phase 1, the design doc exists and downstream tasks are still unclaimed.
- After Phase 2, schema and provider abstractions are ready.
- After Phase 3, endpoints and auth middleware can be tested together.
- After Phase 4, the auth test suite passes and docs match implementation.

## Claude Code Adapter Snippet

```text
TaskCreate(
  subject: "Design authentication architecture",
  description: "Choose session strategy, define user model fields, plan Google and GitHub OAuth flows, and produce docs/auth-design.md",
  activeForm: "Designing authentication architecture"
)
TaskCreate(
  subject: "Create user model and migrations",
  description: "Implement the User model, migration, and repository helpers for provider-backed login",
  activeForm: "Creating user model"
)
TaskCreate(
  subject: "Implement OAuth provider integration",
  description: "Add Google and GitHub providers, token exchange, and provider abstraction code",
  activeForm: "Implementing OAuth providers"
)

TaskUpdate(taskId: "2", addBlockedBy: ["1"])
TaskUpdate(taskId: "3", addBlockedBy: ["1"])

TaskUpdate(taskId: "1", status: "in_progress", owner: "planner")
Task(
  model: "sonnet",
  prompt: "Complete task 1 and mark it completed when the design doc is ready.",
  description: "Design auth architecture"
)
```
