# Example: OAuth Authentication Feature

**User request:** "Add user authentication with OAuth"

## Task Decomposition

```
TaskCreate(
  subject: "Design authentication architecture",
  description: "Design the auth system architecture:
- Choose session vs JWT approach (recommend JWT)
- Define user model schema
- Plan OAuth flow (Google, GitHub)
- Document API endpoints

Deliverable: Architecture document in docs/auth-design.md",
  activeForm: "Designing authentication architecture"
)

TaskCreate(
  subject: "Create user model and migrations",
  description: "Implement user data model:
- Create User model with: id, email, name, avatar, provider, providerId
- Add database migration
- Add model validations
- Create user repository with CRUD operations

Files: src/models/user.ts, db/migrations/xxx_create_users.ts",
  activeForm: "Creating user model"
)

TaskCreate(
  subject: "Implement OAuth provider integration",
  description: "Integrate OAuth providers:
- Implement Google OAuth flow
- Implement GitHub OAuth flow
- Create provider abstraction layer
- Handle token exchange and user info retrieval

Files: src/auth/providers/google.ts, src/auth/providers/github.ts",
  activeForm: "Implementing OAuth providers"
)

TaskCreate(
  subject: "Build login and logout endpoints",
  description: "Create auth API endpoints:
- POST /api/auth/login - initiate OAuth flow
- GET /api/auth/callback - handle OAuth callback
- POST /api/auth/logout - invalidate session
- GET /api/auth/me - get current user

Files: src/api/auth.ts",
  activeForm: "Building auth endpoints"
)

TaskCreate(
  subject: "Add session management middleware",
  description: "Implement JWT session handling:
- Create JWT signing/verification utilities
- Build auth middleware for protected routes
- Add token refresh mechanism
- Handle expired token gracefully

Files: src/middleware/auth.ts, src/utils/jwt.ts",
  activeForm: "Adding session middleware"
)

TaskCreate(
  subject: "Write authentication tests",
  description: "Comprehensive test coverage:
- Unit tests for user model
- Unit tests for OAuth providers
- Integration tests for auth endpoints
- Test token refresh flow

Files: tests/auth/*.test.ts",
  activeForm: "Writing auth tests"
)

TaskCreate(
  subject: "Update API documentation",
  description: "Document the auth system:
- Add auth endpoints to API docs
- Document OAuth setup requirements
- Add authentication guide for developers

Files: docs/api.md, docs/authentication.md",
  activeForm: "Updating documentation"
)
```

## Dependencies

```
TaskUpdate(taskId: "2", addBlockedBy: ["1"])
TaskUpdate(taskId: "3", addBlockedBy: ["1"])
TaskUpdate(taskId: "4", addBlockedBy: ["2", "3"])
TaskUpdate(taskId: "5", addBlockedBy: ["2"])
TaskUpdate(taskId: "6", addBlockedBy: ["4", "5"])
TaskUpdate(taskId: "7", addBlockedBy: ["4"])
```

## Execution Phases

```
Phase 1: [1] Design (opus)
Phase 2: [2, 3] Model + OAuth (sonnet, parallel)
Phase 3: [4, 5] Endpoints + Middleware (sonnet, parallel)
Phase 4: [6, 7] Tests + Docs (sonnet + haiku, parallel)
```

## Spawning

```
# Phase 1
TaskUpdate(taskId: "1", status: "in_progress", owner: "coordinator")
Task(model: "opus", prompt: "Complete task 1...", ...)

# Phase 2 (parallel)
TaskUpdate(taskId: "2", status: "in_progress", owner: "coordinator")
TaskUpdate(taskId: "3", status: "in_progress", owner: "coordinator")
Task(model: "sonnet", prompt: "Complete task 2...", ...)
Task(model: "sonnet", prompt: "Complete task 3...", ...)
```
