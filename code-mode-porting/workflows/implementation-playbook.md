# Implementation Playbook

Use this as the canonical execution path when building a bundled workspace gateway in another app.

## Phase 1: Define The Goal

Write down:

1. which tool families currently dominate prompt surface
2. which of them are safe to bundle
3. which tools must stay direct
4. which runtime boundary owns privileged execution

Produce:

- a tool-surface inventory with columns:
  - family
  - current top-level tools
  - direct or bundled candidate
  - reason
  - privileged owner

Verify:

- every high-volume tool family is classified
- one host boundary is named as the owner of real side effects

If blocked:

- stop here and map the current surface first
- do not choose transport or sandbox details before the inventory exists

## Phase 2: Define The Gateway Contract

Pick one gateway transport:

- MCP execution tool
- provider-native workspace call
- internal tool wrapper with equivalent semantics

Use this host matrix:

| Host shape | Recommended transport | Isolation primitive | Fallback when strong isolation is unavailable |
|---|---|---|---|
| Electron / desktop | MCP execution tool or internal gateway | worker thread or child process | keep a smaller structured wrapper and avoid arbitrary code blocks |
| Server-side app | internal gateway or MCP tool | child process, worker, or isolated container | restrict to typed workspace calls |
| Web app with trusted backend | provider-native or backend gateway | backend worker/process, not browser-only sandboxing | keep browser discovery read-only and execute on the backend |
| CLI-native app | internal gateway | subprocess or worker thread | keep direct tools for mutations that cannot be isolated |
| Mobile / constrained runtime | provider-native or backend relay | server-side worker/process | avoid local arbitrary execution entirely |

Keep the gateway input minimal.

Recommended shape:

```ts
{
  code: string;
  _timeout?: number;
}
```

If your runtime cannot support safe bundled code execution, use a structured `workspace_call({ toolName, args })` transport and keep catalog helpers separate.

Produce:

- the chosen transport
- the chosen isolation primitive
- the fallback plan when the isolation guarantee is weaker than desired

Verify:

- the chosen transport can reach the same real handlers as direct tools
- the chosen isolation primitive keeps secrets and privileged APIs on the host side

## Phase 3: Build The Runtime Tool Catalog

Create a descriptor type and populate it from bundled tools.

You need:

- a list/search endpoint
- a get-one endpoint
- pack/category grouping
- required/optional param exposure

Start with a descriptor like:

```ts
type RuntimeToolDescriptor = {
  name: string;
  displayName?: string;
  description: string;
  category: string;
  pack: string;
  inputSchema: unknown;
  requiredParams: string[];
  optionalParams: string[];
  surface: 'native' | 'source' | 'plugin';
};
```

Produce:

- one descriptor type
- one pack list
- one catalog list/search helper
- one exact-schema helper

Verify:

- the model can list likely candidates before it has exact schemas
- an exact schema fetch returns enough detail to make a concrete call without guessing

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

Produce:

- a direct-vs-bundled table with at least:
  - tool family
  - classification
  - reason
  - timeout/retry note

Verify:

- every bundled mutation is retry-safe enough to run through one gateway block
- every direct tool has a concrete reason to stay visible individually

## Phase 5: Implement The Sandbox

Recommended minimum:

1. pre-validate syntax
2. reject known escape patterns
3. run in a dedicated worker/process/thread boundary
4. inject only:
   - proxy object
   - safe console
   - timer utilities if needed
5. enforce a whole-block timeout

Reject patterns such as:

- `require`
- `process`
- `global` / `globalThis`
- `eval`
- `Function`
- dynamic `import()`

If your policy engine cannot classify dynamic property access like `workspace[toolName]`, either block it in strict modes or downgrade the gateway to discovery-only behavior there.

Produce:

- the validation rule set
- the injected runtime surface
- the timeout owner

Verify:

- worker code cannot reach filesystem, network, environment, or module loading directly
- only the host can execute real privileged handlers

## Phase 6: Implement The Host Dispatcher

Host responsibilities:

- build the function map
- execute real handlers
- map results back to worker call IDs
- track completed calls
- track in-flight calls
- terminate the worker on timeout

This is where you preserve retry safety.

Produce:

- the host function map owner
- the worker-to-host message contract
- the completed/in-flight call tracking fields

Verify:

- concurrent results map back to the correct call IDs
- timeout cleanup cannot leave the worker running after the host has given up

## Phase 7: Integrate Policy

Add policy checks at the gateway boundary.

At minimum:

- allow read-only discovery in safe mode
- block bundled mutations in safe mode
- reject or downgrade patterns you cannot classify safely

If you already have direct-tool permission logic, do not fork it into an unrelated parallel system. Reuse the same execution-boundary model.

Produce:

- a mode matrix showing discovery, read, and mutation behavior per permission mode

Verify:

- safe mode cannot mutate through the gateway
- the gateway reuses the app's existing approval or deny seams instead of bypassing them

## Phase 8: Shape Prompt Discovery

Teach the model a short flow:

1. search common tools first
2. inspect one exact tool only when needed
3. call concrete methods directly
4. isolate long waits in their own call

If you support multiple model families, shape the wording per family.

Produce:

- one default discovery snippet
- any provider- or model-specific variant you actually need

Verify:

- the default prompt starts from common packs first
- specialized packs remain reachable without eager top-level mounting

## Phase 9: Preserve Backward Compatibility

If the app already has direct tools:

- keep them available while code mode is off
- move code-eligible tools behind the gateway only when code mode is on
- keep direct-only tools direct in both modes

This makes rollout and debugging much safer.

Produce:

- an on/off registration matrix
- a rollout flag or profile gate

Verify:

- toggling code mode changes the surface exactly as designed
- direct-only tools remain direct in both states

## Phase 10: Write The Failure Contract

Return enough context for safe retries.

Include:

- logs
- final result
- direct error text
- completed calls before failure
- in-flight calls at failure or timeout

Load `../references/gateway-response-contract.md` and adopt one concrete success, failure, and timeout shape before shipping.

Produce:

- one documented response schema
- one success payload example
- one partial-failure or timeout payload example

Verify:

- the agent can tell whether blind retry is safe
- timeout output shows what may already have persisted

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

Before shipping, capture this artifact:

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
- validation evidence
