# Implementation Playbook

Use this when building code mode in another app.

## Phase 1: Define The Goal

Write down:

1. Which tool families currently dominate prompt surface
2. Which of them are safe to bundle
3. Which tools must stay direct
4. Which runtime boundary owns privileged execution

If you cannot answer those four questions, stop and map the tool surface first.

## Phase 2: Define The Gateway Contract

Pick one gateway transport:

- MCP execution tool
- provider-native workspace call
- internal tool wrapper with equivalent semantics

Keep the gateway input minimal.

Recommended shape:

```ts
{
  code: string;
  _timeout?: number;
}
```

If your runtime does not support code execution comfortably, use a structured `workspace_call({ toolName, args })` transport and keep the catalog helpers separate.

## Phase 3: Build The Runtime Tool Catalog

Create a descriptor type and populate it from bundled tools.

You need:

- a list/search endpoint
- a get-one endpoint
- pack/category grouping
- required/optional param exposure

Do not make the model guess exact schemas from short names alone.

## Phase 4: Classify Direct Vs Bundled

Write the rules down in code and docs.

Examples of good bundled candidates:

- CRUD
- read/search
- non-blocking status
- bounded machine-driven orchestration

Examples of good direct candidates:

- OAuth
- human approval dialogs
- blocking spawn-and-wait UX
- fragile global actions

## Phase 5: Implement The Sandbox

Recommended minimum:

1. pre-validate syntax
2. reject obvious escape hatches
3. run in a dedicated worker/process/thread boundary
4. inject only:
   - proxy object
   - safe console
   - timer utilities if needed
5. enforce a whole-block timeout

The worker should never own the real privileged handlers.

## Phase 6: Implement The Host Dispatcher

Host responsibilities:

- build the function map
- execute real handlers
- map results back to worker call IDs
- track completed calls
- track in-flight calls
- terminate the worker on timeout

This is where you preserve retry safety.

## Phase 7: Integrate Policy

Add policy checks at the gateway boundary.

At minimum:

- allow read-only discovery in safe mode
- block bundled mutations in safe mode
- reject forms of code you cannot classify safely

If you already have direct-tool permission logic, do not fork it into an unrelated parallel system. Reuse the same execution-boundary model.

## Phase 8: Shape Prompt Discovery

Teach the model a short flow:

1. search common tools first
2. inspect one exact tool only when needed
3. call concrete methods directly
4. isolate long waits in their own call

If you support multiple model families, shape the wording per family.

## Phase 9: Preserve Backward Compatibility

If the app already has direct tools:

- keep them available while code mode is off
- move code-eligible tools behind the gateway only when code mode is on
- keep direct-only tools direct in both modes

This makes rollout and debugging much safer.

## Phase 10: Write The Failure Contract

Return enough context for safe retries.

Include:

- logs
- final result
- direct error text
- completed calls before failure
- in-flight calls at failure or timeout

If your gateway hides that information, agents will create duplicate side effects under pressure.

## Rollout Strategy

Use this order:

1. ship catalog helpers
2. ship gateway behind a flag
3. bundle low-risk read/write tools first
4. add policy checks
5. add long-running orchestration with explicit timeout guidance
6. add provider/model shaping
7. trim direct surface only after validation

## Final Design Snapshot

Before shipping, you should be able to state:

- gateway transport
- direct-only tool rule
- bundled-tool rule
- catalog helper set
- sandbox runtime
- host dispatcher owner
- safe-mode behavior
- timeout behavior
- retry guidance
- model-family shaping rules
