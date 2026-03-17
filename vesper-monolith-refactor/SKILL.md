---
name: vesper-monolith-refactor
description: This skill should be used when refactoring a large Vesper file, feature, or component into smaller modules without changing behavior. Use it for breaking up monoliths such as main-process managers, React shells, or mixed-responsibility services by following Tung Nguyen's facade-first, seam-by-seam extraction method.
---

# Vesper Monolith Refactor

Refactor large Vesper files into smaller modules without losing behavioral trust.

## When To Use

Use this skill when:
- A Vesper file is too large to reason about safely.
- A service, manager, or React shell mixes several responsibilities.
- You want to split code incrementally instead of rewriting it.
- The user asks to "break up", "modularize", "extract", "slim down", or "refactor" a large file or feature.
- You want to follow Tung Nguyen's `sessions.ts` extraction style.

## Core Method

Apply Tung's method by default:

1. Keep the original owner alive as a facade.
2. Extract one stable seam at a time.
3. Move the seam into an adjacent job-named module.
4. Preserve guards, orchestration order, recursion, and boundary side effects in the facade.
5. Verify the moved seam before touching the next one.
6. Report what moved, what stayed, and how much the monolith shrank.

## Execution Workflow

1. Identify the risky contracts first.
   Add or extend focused tests for the user-visible flows most likely to regress.

2. Build a seam map.
   List 3-7 extraction candidates and choose the smallest one that:
   - already behaves like one job
   - can take explicit dependencies
   - can leave a thin wrapper behind
   - will remove a meaningful block of code

3. Extract adjacent to the owner.
   Create a nearby module named after the job, not the old line range.

4. Keep the facade thin but authoritative.
   Leave in the original file:
   - preflight guards
   - recursive fan-out
   - orchestration order
   - compatibility entrypoints
   - delicate event/persistence boundaries

5. Inject dependencies explicitly.
   Prefer a narrow parameter bag and explicit callbacks over reaching into wide shared state.

6. Verify narrowly, then widen only if needed.
   Start with the seam's direct tests plus typecheck.

7. Commit or report in Tung style.
   Always state:
   - what moved
   - what intentionally stayed
   - the new file(s)
   - verification run
   - file size reduction if meaningful

## Tung's Practical Order

When the seam order is not obvious, prefer this progression:

1. Wiring and registration groups
2. Feature or action families
3. Event-family handlers
4. Lifecycle and storage seams
5. Runtime/config/state-transition seams
6. Remaining hard orchestration

This keeps early passes lower-risk and makes later core extractions easier.

For the detailed rubric and a reconstructed commit-by-commit phase order, read:
- `references/tung-method.md`
- `references/commit-sequence.md`

## Guardrails

- Do not start with a full rewrite.
- Do not move guards, recursion, and orchestration order out in the same step unless the seam is tiny and well-tested.
- Do not create generic `utils.ts` dumping grounds; create job-named adjacent modules.
- Do not split one behavior across multiple new files in the first pass.
- Do not claim progress from file count alone; behavior and trust matter more than fragmentation.
- Do not run broad cleanup across unrelated concerns while extracting one seam.

## Vesper-Specific Guidance

- For large main-process owners, preserve IPC/session/runtime boundaries in the facade until the seam is proven.
- For renderer shells, keep navigation, route parsing, and user-visible layout boundaries stable while extracting inner state/effect logic.
- Prefer adjacent folders like `apps/electron/src/main/sessions/` over generic shared folders unless the seam is truly cross-domain.
- If a repo already has a refactor plan, update it as you go so later agents can resume without reconstructing the seam map from git history.

## Response Contract

When using this skill, report:
- the chosen seam
- why it was chosen over nearby seams
- what stayed in the facade
- what verification ran
- what the next likely seam is

## References

- `references/tung-method.md`
- `references/commit-sequence.md`
