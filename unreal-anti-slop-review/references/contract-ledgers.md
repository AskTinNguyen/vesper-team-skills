# Unreal Contract Ledgers

Use every branch below exactly once in the applicability ledger. A branch is `NOT_APPLICABLE` only with a surface-specific reason. Scanner signals seed review items; the ledgers establish completeness.

## Branch IDs

`uobject`, `registration`, `async`, `shared-state`, `editor-mutation`, `loading-performance`, `gameplay-networking`, `test-proof`, `engine-ownership`

## UObject, Reflection, And Serialization

Ledger fields:

`input | runtime type | canonical owner | retention/GC path | CDO/archetype phase | reflected/config/default path | serialization/duplication/replication consumer | destruction`

- Treat lifecycle owner, outer, asset, replicated object, and editor context types as external input unless every construction and reconstruction path enforces the type.
- `CastChecked` is acceptable only after a durable local invariant. Blueprint-spawnable or attachable components, loaded assets, networking, optional editor state, and teardown generally require recoverable validation.
- Prove UObject retention through a reflected hard property, complete `AddReferencedObjects` chain, strong handle, managed streamable handle, or documented root. `NewObject` and an outer alone do not prove durable retention.
- Treat native constructors as CDO, archetype, and instance construction. Config/property initialization and many world contracts occur later.
- Reflected name, type, specifier, default, enum, struct, RPC, or replication changes require compatibility, old-data, cook, and network proof as applicable.

## Registrations And Replaceable Sources

Ledger fields:

`logical owner | current source | bound source | handles/owner token | bind point | use | exact inverse | replacement path | logical terminal`

- For a source that can change, store current source separately from bound source. Unbind from the bound source before overwriting either identity.
- Apply this to delegates, Enhanced Input, mapping contexts, ASCs, worlds, subsystems, components, ToolMenus, tabs, styles, commands, extenders, compiler/details registries, tickers, debug draw, and static registries.
- Weak/UObject-aware binding is memory-safety evidence only. Remove registrations at the earliest logical terminal: replacement, feature deactivation, `EndPlay`, world teardown, panel destruction, module shutdown, supersession, or owner destruction.
- Automatic invalidation satisfies cleanup only when destruction is the sole terminal and the source cannot outlive or be replaced independently.
- `RemoveAll(this)` is acceptable only against the proven bound source and only when its removal scope is correct.

## Async, World, And Threading

Ledger fields:

`request owner | captured state | destination thread | operation identity | cancellation | stale-result rejection | re-entrant replacement check | world teardown guard | terminal state`

- Scheduling, weak capture, and cancellation requests do not prove lifetime, exclusivity, or terminal cleanup.
- Supersedable work requires a generation, token, state-object identity, or equivalent checked immediately before each mutation.
- Durable order: `invalidate prior identity -> request cancellation -> capture new identity -> execute -> revalidate identity/owner/world/thread -> mutate -> terminal`.
- Revalidate after external or re-entrant callbacks that can replace or end the operation.
- A documented non-overlap guarantee, synchronous join, or completion barrier can dismiss the identity requirement.

## Shared UObject And CDO Mutation

Ledger fields:

`shared object | mutated fields/containers | saved prior state | cache/compiled/notification effects | restoration paths | concurrent observers | scheduler/test isolation | terminal state`

- Mutation of a CDO, mutable settings singleton, global registry, or other shared UObject always creates a review item.
- RAII restoration proves one cleanup path, not isolation. Dismissal requires restoration on every exit, derived side effects accounted for, and proof that concurrent tests, callbacks, editor consumers, or runtime consumers cannot observe temporary state.
- Reachable overlap or incomplete restoration is a finding. Missing isolation or side-effect evidence is an item gap.

## Editor Mutation

Ledger fields:

`preflight | transaction owner | Modify() point | first persistent write | mutation sequence | compile/PostEdit/notification | dirtying | save policy | failure rollback | success terminal`

- Undo/Redo recording and failure atomicity are separate contracts.
- Call `Modify()` before the first persistent write. A caller-owned transaction must be traced rather than assumed.
- Returning failure does not restore objects, derived state, registries, dirty packages, or files.
- Flag irreversible mutation before validation, partial persistent state on failure, late `Modify()`, and unsolicited saving outside an explicit user action.
- `WITH_EDITOR` proves compile separation, not clean Runtime/Editor ownership.

## Loading And Performance

Ledger fields:

`activation | phase/thread | frequency | scale | load/lookup/allocation type | retention/backpressure | stop condition | measured or bounded cost`

- Distinguish resolve, synchronous load, async request, retention, cancellation, and release.
- Runtime synchronous loads in combat, input, status application, ability activation, or network response require a guaranteed preload/rare-path contract with bounded scale; otherwise they are findings.
- Review tick, polling, broad invalidation, Asset Registry discovery, reflection, object lookup, logging, allocation, and replication fan-out only when the Unreal execution path establishes frequency and consequence.
- File size, generic abstraction quality, `LogTemp`, and warning policy belong to other review skills.

## Gameplay And Networking

Ledger fields:

`input/producer | canonical state owner | authority | net owner/connection | prediction | replication/relevancy | consumer | removal/rollback | teardown`

- Do not treat authority, net ownership, owning connection, prediction, and replicated visibility as interchangeable.
- For tags or counters, identify every producer, overlap/count model, authority, replication, and removal owner.
- Reject local flags that shadow canonical GAS, replicated, gameplay-tag, BT/StateTree, or coordinator truth.
- Re-check active identity after callbacks when re-entrancy can replace or terminate the operation.

## Test Proof

Ledger fields:

`failure mode | production executor | injected dependency seam | trigger | observable | cleanup | claimed boundary | false substitute excluded`

- Production-executor proof requires the same callable path production invokes, or a canonical shared production helper called by it. Test doubles may replace dependencies below that seam.
- Separate executor sequencing, producer wiring, real engine mutation/evaluation, serialization/persistence, and teardown claims.
- Copied algorithms, test-only executors, direct delegate broadcasts, unconditional success, validity-only assertions, and placeholder helpers cannot prove the production path.
- A direct broadcast may prove consumer shape; it does not prove producer wiring.

## Engine Ownership

Ledger fields:

`supplied provenance | exact delta claim | supported extension alternative | product-neutral owner | irreversible mutation | callback/result | rollback | module/load boundary | merge surface | focused regression`

- Missing Git/base provenance limits delta, introduced attribution, extension history, ancestry, and merge claims; it does not erase source-contract findings in supplied engine files.
- Prefer project Editor plugins and supported extension points for product-shaped behavior. Engine seams must remain product-neutral.
- Trace extension hooks as preconditions, irreversible mutation, callback, rollback, and structured result.

## Scanner Signals

The scanner may emit only these lexical signals:

- `synchronous-load`
- `runtime-object-discovery`
- `reflection-dispatch`
- `hard-cast-invariant`
- `tick-definition`
- `raw-callback-registration`
- `global-registration`
- `direct-package-save`
- `config-write`
- `deferred-work`
- `mutable-default-access`
- `test-direct-broadcast`

Every signal creates adjudication work, so a signal is retained only when fixtures define positive forms, safe near-misses, comments/strings, and multiline behavior.

Manual-only relational contracts include bound-source replacement, exact teardown completeness, shared-object isolation, latest-wins identity correctness, owner-type construction reachability, producer wiring, production-executor proof, replication semantics, and rollback atomicity. Zero scanner signals proves nothing.
