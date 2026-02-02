---
name: test-backend
description: Backend unit and integration testing for Node.js, Python, Ruby, and Go APIs
argument-hint: "[target] [options]" e.g., "./src/api" or "./services --integration"
---

# Test Backend

Backend testing specialist for Node.js, Python, Ruby, and Go. Handles unit tests, integration tests, and database testing.

## When to Use

- Test API endpoints
- Test business logic/services
- Test database integrations
- Setup backend testing infrastructure

## Usage

```bash
# Test all backend code
/test-backend ./src

# Test specific module
/test-backend ./src/services/user

# Only unit tests
/test-backend ./src --unit

# Only integration tests
/test-backend ./src --integration

# Test with coverage
/test-backend ./src --coverage

# Test with database
/test-backend ./src --db (uses testcontainers)
```

## Auto-Detection

This command automatically detects:
- **Language**: Node.js, Python, Ruby, Go (from project files)
- **Framework**: Express, Fastify, FastAPI, Rails, etc.
- **Test Framework**: Jest, Vitest, pytest, RSpec

## Test Structure

### Controller Test
```typescript
// Unit test with mocked dependencies
describe('UserController', () => {
  describe('getUserById', () => {
    it('returns user when found')
    it('returns 404 when not found')
    it('handles service errors')
  })
})
```

### Integration Test
```typescript
// Test with real database (testcontainers)
describe('User API Integration', () => {
  it('creates and retrieves user')
  it('enforces unique email constraint')
  it('cascades delete to related data')
})
```

## Database Testing

### Testcontainers (Recommended)
- Spins up real database in Docker
- Isolated per test run
- Production-like environment

### In-Memory (SQLite)
- Fast for unit tests
- Good for simple CRUD
- Not for complex queries

## Coverage Targets

| Layer | Target | Focus |
|-------|--------|-------|
| Controllers/Handlers | 90% | Input validation, error handling |
| Services | 95% | Business logic, edge cases |
| Repositories | 80% | CRUD, queries, relationships |
| Utils/Helpers | 90% | Pure functions |

## Output

```
test-results/
├── unit-test-results.xml
├── integration-test-results.xml
├── coverage/
│   ├── lcov.info
│   └── html-report/
└── failing-tests.log (if any)
```

## Best Practices

1. **Mock external services** (APIs, emails, etc.)
2. **Use factories for test data**
3. **Clean up after each test**
4. **Test transaction boundaries**
5. **Verify error paths**

## Integration

Called by `/test-orchestrator` when:
- Backend files detected in changes
- API endpoints need testing
- Database migrations present
