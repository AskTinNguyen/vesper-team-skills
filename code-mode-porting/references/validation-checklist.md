# Validation Checklist

Use this as the ship gate for a code-mode port.

## Core Runtime

Pass all of these:

1. Invalid syntax fails before execution.
2. Obvious sandbox escapes are rejected before execution.
3. Worker code cannot directly access privileged resources.
4. Whole-block timeout terminates execution reliably.
5. Console output is captured and returned safely.

## Dispatcher Behavior

Pass all of these:

1. Known bundled tools route correctly through the host.
2. Unknown bundled tools fail clearly.
3. Results map back to the correct call ID under concurrency.
4. Completed calls are tracked before failure/timeout.
5. In-flight calls are reported when failure or timeout happens.

## Failure Semantics

Pass all of these:

1. Structured tool failures fail the bundled block.
2. Explicit `try/catch` recovery still works.
3. Sequential failures stop later mutations.
4. Concurrent failures are reported as non-transactional.
5. Gateway output tells the agent not to blindly retry persisted mutations.

## Discovery

Pass all of these:

1. `tool_pack_list` returns meaningful packs.
2. `tool_catalog_list` returns usable previews.
3. `tool_catalog_get` returns exact schema details.
4. Default discovery starts in the intended common pack for shaped harnesses.
5. Specialized packs remain explicitly searchable.

## Policy

Pass all of these:

1. Safe/read-only mode allows discovery helpers.
2. Safe/read-only mode blocks bundled mutating calls.
3. Dynamic patterns you cannot classify safely are rejected or downgraded appropriately.
4. The gateway does not bypass the app's normal permission model.

## Surface Composition

Pass all of these:

1. Bundled tools disappear from the direct surface when code mode is on.
2. Direct-only tools remain direct.
3. Code mode can be disabled cleanly.
4. Minimal or automation profiles can skip the broad gateway if intended.
5. Compact profiles can still expose trimmed capabilities progressively if designed that way.

## Prompt And Model Shaping

Pass all of these:

1. Prompt teaches a discovery-first flow.
2. Prompt encourages direct concrete calls after discovery.
3. Prompt includes timeout guidance for long waits.
4. Different model families get the intended gateway wording.
5. Narrowed discovery does not remove real capability by accident.

## Regression Questions

Ask these before shipping:

1. Did we preserve host-side privilege ownership?
2. Did we accidentally create a policy bypass?
3. Did we hide too much surface for weaker models to recover?
4. Did we leave so much direct surface that code mode no longer matters?
5. Can the agent recover safely after a partial mutation failure?

## Minimum Test Set

If you only have time for a small suite, cover these:

1. gateway on/off registration split
2. syntax failure
3. unknown tool
4. structured tool failure
5. safe-mode read-only inspection
6. safe-mode mutation block
7. default-pack discovery
8. explicit specialized-pack discovery
9. timeout with completed/in-flight reporting
10. concurrent failure with partial side-effect warning
