# Coordination Extension Tests

Comprehensive test suite for the OpenClaw Coordination extension.

## Test Files

### 1. `reservations.test.ts` (COORD-010)
Tests for file reservation system:
- ✅ Adding/removing reservations
- ✅ Conflict detection with other agents
- ✅ Pattern matching (folder `src/api/` vs file `src/api/auth.ts`)
- ✅ Agent registration and lifecycle

**19 tests, all passing**

### 2. `claims.test.ts` (COORD-011)
Tests for task claiming system:
- ✅ Successful task claiming
- ✅ Failure cases (already claimed, agent has claim)
- ✅ Task unclaiming
- ✅ Task completion and recording
- ✅ Query functions

**22 tests, all passing**

### 3. `race.test.ts` (COORD-013)
Tests for race condition handling:
- ✅ 5 concurrent claims → exactly 1 succeeds
- ✅ 10 concurrent claims → no data corruption
- ✅ 50 concurrent claims → stress test
- ✅ Concurrent claims on different tasks
- ✅ Mixed race scenarios
- ✅ Stability across multiple rounds

**6 tests, all passing**

## Running Tests

```bash
# Build and run all tests
npm run build
node --test 'dist/tests/*.test.js'

# Or use the npm script
npm run test:unit
```

## Test Results

```
✅ Total: 55 tests
✅ Pass: 55
❌ Fail: 0
⏱️  Duration: ~2 seconds
```

## Key Features Tested

### File Reservations
- Pattern-based reservations (exact files and folder prefixes)
- Conflict detection across multiple agents
- Mock agent TTL and session validation bypass

### Task Claims
- Atomic task claiming with file-based mutex
- One-claim-per-agent enforcement
- Stale claim cleanup
- Completion tracking

### Race Condition Safety
- Swarm-locked operations prevent double-claims
- No data corruption under high concurrency
- Deterministic behavior (no flaky tests)

## Implementation Notes

### Testing Environment
- Uses `process.env.OPENCLAW_COORD_NO_GATEWAY_CHECK = "1"` to bypass gateway session validation
- Creates isolated temporary directories for each test
- Invalidates agent cache between tests for isolation

### Race Testing Methodology
- Uses `Promise.all()` to spawn truly concurrent operations
- Verifies exactly one winner in N-way races
- Checks for JSON corruption after concurrent writes
- Tests various concurrency levels (5, 10, 50 agents)

## Success Criteria Met

✅ **COORD-010**: All reservation tests pass  
✅ **COORD-011**: All claims tests pass  
✅ **COORD-013**: Race conditions handled correctly  
✅ No flaky tests (all deterministic)  
✅ Clean test output with meaningful assertions
