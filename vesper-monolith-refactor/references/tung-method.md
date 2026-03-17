# Tung's Monolith Refactor Method

Use this reference when you need the detailed reasoning behind the skill's workflow.

## Summary

Tung Nguyen's refactor of `apps/electron/src/main/sessions.ts` suggests a repeatable method for large-file reduction in Vesper:

- keep the original owner as a facade
- select seams that already behave like one job
- move one seam at a time into an adjacent job-named file
- preserve boundary-sensitive behavior in the facade
- run targeted verification after each seam
- record measurable progress in every commit

## Seam Selection Rubric

Prefer seams with all or most of these properties:

1. One cohesive responsibility
   Examples:
   - callback registration group
   - state transition
   - feature/action family
   - lifecycle segment
   - event-family handler

2. Narrow dependency shape
   The new module should be able to take a parameter bag or explicit callbacks rather than reading broad manager state directly.

3. Stable facade boundary
   The existing owner should still be able to keep:
   - early returns
   - orchestration order
   - recursive fan-out
   - compatibility entrypoints
   - event/persistence boundaries

4. Meaningful shrinkage
   The extraction should remove a real reasoning burden, not just shuffle tiny helpers.

5. Clear file name
   The target file should be named after the job:
   - `processing-cancel.ts`
   - `session-model.ts`
   - `agent-runtime-creation.ts`

## Facade Boundary Rules

Keep these in the original owner when possible:

- preflight guards
- recursive or cascading control flow
- orchestration order
- cross-feature coordination
- boundary-side effects with delicate ordering
- stable external entrypoints

Move these to the helper:

- cohesive mutation logic
- one lifecycle implementation
- one config assembly routine
- one action or event family
- bounded algorithms with explicit inputs

## Likely Step-By-Step Workflow

Based on the commit history, Tung appears to work from outer to inner:

1. wiring and registration groups
2. feature/action families
3. event-family handlers
4. lifecycle and storage seams
5. runtime/config/state-transition helpers
6. remaining hard orchestration

This order lowers risk because it removes obvious separable code first and postpones the most stateful core until the surrounding noise is reduced.

## Commit Pattern

Tung's refactor commits repeatedly communicate:

- what moved out
- what intentionally stayed in the facade
- the new helper file
- the updated line count
- that checks remained green

Use this reporting shape when continuing the method:

```text
Extracted [responsibility] into [new file], kept [owner].[method] as a thin wrapper around [remaining boundary concern], and reduced [monolith] to [line count] with checks still green.
```

## Examples From `sessions.ts`

- `updateSessionModel()` stayed as the entrypoint while `session-model.ts` took over model normalization, metadata updates, agent sync, and event payload work.
- `cancelProcessing()` kept early return and delegation-child cascade while `processing-cancel.ts` took the single-session cancellation lifecycle.
- `getOrCreateAgent()` still coordinated bootstrap ordering while `agent-runtime-creation.ts` took runtime/config assembly.

## Use On Other Surfaces

Apply the same method to:

- large main-process managers
- renderer route shells
- mixed-responsibility settings pages
- feature coordinators with tangled state/effect/event logic

The key question is:

Can this block become one adjacent job-named module while the current owner remains the safe facade?
