# Common Dependency Patterns

This reference shows common task dependency patterns for different project types.

## Pattern Types

### Linear Chain

```
A → B → C → D
```

Use when each step must complete before the next begins.

**Example: Database Migration**
```
1. Design schema changes        (no deps)
2. Write migration files        (blockedBy: 1)
3. Update model code            (blockedBy: 2)
4. Update affected services     (blockedBy: 3)
5. Write migration tests        (blockedBy: 4)
```

### Fork Pattern

```
    ┌→ B
A ──┼→ C
    └→ D
```

One foundational task enables multiple parallel tasks.

**Example: API Feature**
```
1. Design API contracts         (no deps)
2. Implement endpoints          (blockedBy: 1)
3. Write client SDK             (blockedBy: 1)
4. Create documentation         (blockedBy: 1)
```

Execution: Task 1 first, then 2, 3, 4 in parallel.

### Diamond Pattern

```
    ┌→ B ─┐
A ──┤     ├→ D
    └→ C ─┘
```

Parallel tasks converge on a final task.

**Example: Full-Stack Feature**
```
1. Design data model            (no deps)
2. Build backend API            (blockedBy: 1)
3. Build frontend components    (blockedBy: 1)
4. Integration testing          (blockedBy: 2, 3)
```

Execution: 1 → [2, 3 parallel] → 4

### Fork-Join Pattern

```
    ┌→ B ─┐
A ──┼→ C ─┼→ E → F
    └→ D ─┘
```

Multiple parallel phases with synchronization points.

**Example: Microservice Deployment**
```
1. Update shared contracts      (no deps)
2. Update Service A             (blockedBy: 1)
3. Update Service B             (blockedBy: 1)
4. Update Service C             (blockedBy: 1)
5. Integration tests            (blockedBy: 2, 3, 4)
6. Deploy to staging            (blockedBy: 5)
```

### Independent Parallel

```
A
B    (no dependencies between any)
C
D
```

Completely independent tasks that can all run simultaneously.

**Example: Documentation Sprint**
```
1. Write API reference          (no deps)
2. Write getting started guide  (no deps)
3. Write deployment guide       (no deps)
4. Add code examples            (no deps)
```

All 4 can spawn in parallel.

---

## Project-Specific Patterns

### New Feature (Full Stack)

```
1. Design architecture          opus, no deps
2. Create database schema       sonnet, blockedBy: 1
3. Build API endpoints          sonnet, blockedBy: 2
4. Build UI components          sonnet, blockedBy: 1
5. Connect UI to API            sonnet, blockedBy: 3, 4
6. Write unit tests             sonnet, blockedBy: 3, 4
7. Write E2E tests              sonnet, blockedBy: 5
8. Documentation                haiku, blockedBy: 5
```

**Execution phases:**
- Phase 1: [1] Design
- Phase 2: [2, 4] Schema + UI (parallel)
- Phase 3: [3] API
- Phase 4: [5, 6] Integration + Unit tests (parallel)
- Phase 5: [7, 8] E2E + Docs (parallel)

### Bug Fix

```
1. Reproduce and document bug   sonnet, no deps
2. Write failing test           sonnet, blockedBy: 1
3. Implement fix                sonnet, blockedBy: 2
4. Verify fix and tests pass    sonnet, blockedBy: 3
5. Update related documentation haiku, blockedBy: 4
```

**Execution:** Linear chain (each step validates the previous)

### Refactoring

```
1. Analyze current structure    opus, no deps
2. Design target architecture   opus, blockedBy: 1
3. Add adapter/facade layer     sonnet, blockedBy: 2
4. Migrate component A          sonnet, blockedBy: 3
5. Migrate component B          sonnet, blockedBy: 3
6. Migrate component C          sonnet, blockedBy: 3
7. Remove adapter layer         sonnet, blockedBy: 4, 5, 6
8. Update tests                 sonnet, blockedBy: 7
```

**Execution:**
- Phase 1-3: Sequential (planning + scaffolding)
- Phase 4-6: Parallel migrations
- Phase 7-8: Sequential cleanup

### API Integration

```
1. Research external API        sonnet, no deps
2. Design integration interface opus, blockedBy: 1
3. Implement API client         sonnet, blockedBy: 2
4. Add error handling           sonnet, blockedBy: 3
5. Add retry logic              sonnet, blockedBy: 3
6. Write integration tests      sonnet, blockedBy: 4, 5
7. Add monitoring/logging       haiku, blockedBy: 3
```

**Execution:**
- Phase 1-3: Sequential foundation
- Phase 4-5, 7: Parallel enhancements
- Phase 6: Final validation

### Testing Suite

```
1. Set up test infrastructure   sonnet, no deps
2. Write unit tests - models    sonnet, blockedBy: 1
3. Write unit tests - services  sonnet, blockedBy: 1
4. Write unit tests - utils     haiku, blockedBy: 1
5. Write integration tests      sonnet, blockedBy: 2, 3, 4
6. Write E2E tests              sonnet, blockedBy: 5
7. Configure CI pipeline        haiku, blockedBy: 6
```

---

## Anti-Patterns

### Over-Serialization ❌

```
A → B → C → D → E → F
(Everything depends on everything)
```

**Problem:** No parallelization possible, slow execution.

**Fix:** Identify truly independent work and remove unnecessary dependencies.

### Missing Dependencies ❌

```
A    B    C    D
(No dependencies declared but they exist)
```

**Problem:** Agents will conflict when editing same files.

**Fix:** Analyze file ownership and add appropriate blockedBy relationships.

### Circular Dependencies ❌

```
A → B → C → A
```

**Problem:** Deadlock - nothing can ever complete.

**Fix:** Run `validate-dependency-graph.ts` before execution. Restructure tasks to break cycles.

### Over-Decomposition ❌

```
20+ tiny tasks for a simple feature
```

**Problem:** Coordination overhead exceeds benefit.

**Fix:** Aim for 3-10 tasks per feature. Each task should be ~30-60 min of focused work.

---

## Dependency Declaration Examples

### Setting Up Dependencies

After creating tasks, establish dependencies:

```
// Task 4 depends on tasks 2 and 3
TaskUpdate(taskId: "4", addBlockedBy: ["2", "3"])

// Task 5 depends on task 4
TaskUpdate(taskId: "5", addBlockedBy: ["4"])

// Tasks 2 and 3 depend on task 1
TaskUpdate(taskId: "2", addBlockedBy: ["1"])
TaskUpdate(taskId: "3", addBlockedBy: ["1"])
```

### Verifying Dependencies

Before spawning, check the graph:

```bash
bun run scripts/validate-dependency-graph.ts
```

Output shows:
- Execution phases (what can run in parallel)
- Critical path (longest dependency chain)
- Any cycles or errors
