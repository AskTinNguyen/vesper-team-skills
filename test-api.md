---
name: test-api
description: API testing for REST and GraphQL endpoints with pytest
argument-hint: "[target] [options]" e.g., "./tests/api" or "--openapi=./api.yaml"
---

# Test API

API testing specialist for REST and GraphQL endpoints. Uses pytest with httpx for fast, reliable API tests.

## When to Use

- Test REST API endpoints
- Test GraphQL queries/mutations
- Validate API contracts
- Performance testing
- Authentication/Authorization testing

## Usage

```bash
# Test all API endpoints
/test-api ./tests/api

# Test specific module
/test-api ./tests/api/test_users.py

# Test from OpenAPI spec
/test-api --openapi=./openapi.yaml

# Run in parallel
/test-api ./tests/api -n auto

# Test with coverage
/test-api ./tests/api --coverage

# Filter by test name
/test-api ./tests/api -k "test_create"
```

## Test Structure

### REST API Test
```python
class TestUsersCRUD:
    def test_create_user_success(self, authenticated_client):
        response = authenticated_client.post("/users", json=user_data)
        assert response.status_code == 201
        assert "id" in response.json()

    def test_get_user_not_found(self, authenticated_client):
        response = authenticated_client.get("/users/99999")
        assert response.status_code == 404
```

### GraphQL Test
```python
def test_get_users_query(self, authenticated_client):
    query = """
    query GetUsers($limit: Int!) {
        users(limit: $limit) { id email }
    }
    """
    response = authenticated_client.post("/graphql", json={
        "query": query,
        "variables": {"limit": 10}
    })
    assert response.status_code == 200
    assert "errors" not in response.json()
```

## Test Categories

### Positive Tests
- Valid requests return 200/201
- Correct response structure
- Data persistence verified

### Negative Tests
- Invalid input returns 400
- Unauthorized returns 401
- Forbidden returns 403
- Not found returns 404

### Contract Tests
```python
# Validate against OpenAPI spec
@schema.parametrize()
def test_api_contract(case):
    case.call_and_validate()
```

## Authentication

Handles multiple auth types:
- Bearer Token (JWT)
- API Key
- OAuth 2.0
- Session-based

## Fixtures

```python
@pytest.fixture
def authenticated_client():
    """Client with valid auth token"""

@pytest.fixture
def valid_user_data():
    """Valid test data for users"""

@pytest.fixture
def created_user(authenticated_client):
    """User created and cleaned up after test"""
```

## Performance Testing

```python
def test_response_time_under_threshold(self, client):
    start = time.time()
    response = client.get("/api/users")
    elapsed = time.time() - start
    assert elapsed < 2.0
```

## Output

```
test-results/
├── api-test-results.xml
├── coverage/
│   ├── api-coverage.xml
│   └── html-report/
├── contract-test-results/
└── performance-report.json
```

## Coverage Requirements

- All endpoints tested
- All HTTP methods (GET, POST, PUT, PATCH, DELETE)
- All status codes (200, 201, 400, 401, 403, 404, 500)
- Input validation for each field
- Authentication on protected endpoints

## Best Practices

1. **Test full CRUD lifecycle**
2. **Use factories for test data**
3. **Clean up resources after test**
4. **Test pagination, filtering, sorting**
5. **Verify error response formats**

## Integration

Called by `/test-orchestrator` when:
- API changes detected
- Backend services modified
- Contract validation needed
