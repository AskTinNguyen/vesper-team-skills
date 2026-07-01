# Facade-First Seam Extraction Pattern

Use this reference when choosing a seam, deciding what stays in the facade, or checking the provenance behind this skill.

## Contents

- [Provenance](#provenance)
- [Summary](#summary)
- [Seam Selection Rubric](#seam-selection-rubric)
- [Tie-Breaker Worksheet](#tie-breaker-worksheet)
- [Facade Boundary Rules](#facade-boundary-rules)
- [Worked Pattern: Main-Process Manager](#worked-pattern-main-process-manager)
- [Worked Pattern: Renderer Shell](#worked-pattern-renderer-shell)
- [Examples From `sessions.ts`](#examples-from-sessionsts)
- [Use On Other Surfaces](#use-on-other-surfaces)

## Provenance

This reference captures the facade-first seam extraction pattern observed in Tung Nguyen's `apps/electron/src/main/sessions.ts` refactor across commits from 2026-03-13 through 2026-03-17.

Representative provenance points:

- `9efcda96c` collaboration callbacks
- `7a7908042` session storage lifecycle
- `3b6f91e15` agent runtime creation
- `24bdab0a9` session model extraction
- `0c498bb86` processing cancel extraction

Treat this as an observed Vesper pattern, not a timeless repo contract. If an active refactor plan says otherwise, follow the plan.

## Summary

The pattern is:

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

## Tie-Breaker Worksheet

When several seams look viable, score each candidate from 1-5 on:

| Criterion | 1 | 5 |
|-----------|---|---|
| Cohesion | tangled with unrelated behavior | clearly one job |
| Dependency width | needs most of the owner | narrow parameter bag |
| Facade safety | forces ordering-sensitive logic out | wrapper can safely stay thin |
| Code removed | tiny helper only | meaningfully reduces reasoning burden |
| Testability | hard to verify directly | easy to verify with focused checks |

Choose the highest total.

Tie-break rules:

1. prefer lower-risk seams
2. prefer seams with clearer verification
3. prefer seams that leave the owner easier to read even before the next extraction

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

## Worked Pattern: Main-Process Manager

Use this shape for owners like `sessions.ts`:

```ts
// owner facade
async cancelProcessing(sessionId: string, silent = false) {
  const managed = this.sessions.get(sessionId)
  if (!managed?.isProcessing) return

  for (const childId of this.delegationChildren.get(sessionId) ?? []) {
    await this.cancelProcessing(childId, true)
  }

  return cancelManagedProcessing({
    managed,
    sessionId,
    silent,
    sendEvent: (event, workspaceId) => this.sendEvent(event, workspaceId),
    persistSession: (targetManaged) => this.persistSession(targetManaged),
  })
}
```

Why this works:

- the facade still owns guards and recursive fan-out
- the helper owns the single-session lifecycle
- dependency flow is explicit

## Worked Pattern: Renderer Shell

Use this shape for route or settings shells:

```tsx
export function WorkspaceSettingsShell() {
  const route = useWorkspaceRoute()
  const viewState = getWorkspaceSettingsViewState(route)

  return (
    <SettingsLayout viewState={viewState}>
      <WorkspaceSettingsContent viewState={viewState} />
    </SettingsLayout>
  )
}
```

Extract to a sibling like `workspace-settings-view-state.ts` when:

- route parsing can stay in the shell
- view-state derivation is one cohesive job
- layout boundaries stay stable while state logic moves out

## Examples From `sessions.ts`

- `updateSessionModel()` stayed as the entrypoint while `session-model.ts` took over model normalization, metadata updates, agent sync, and event payload work.
- `cancelProcessing()` kept early return and delegation-child cascade while `processing-cancel.ts` took the single-session cancellation lifecycle.
- `getOrCreateAgent()` still coordinated bootstrap ordering while `agent-runtime-creation.ts` took runtime/config assembly.

## Use On Other Surfaces

Apply the same pattern to:

- large main-process managers
- renderer route shells
- mixed-responsibility settings pages
- feature coordinators with tangled state/effect/event logic

The key question is:

Can this block become one adjacent job-named module while the current owner remains the safe facade?
