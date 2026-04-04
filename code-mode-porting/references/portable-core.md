# Portable Core

This is the reusable architecture behind Vesper's current code mode.

Do not start with Vesper's product nouns.
Start with the portable shape.

## Problem It Solves

Agent apps accumulate too many top-level tools.

That creates:

- prompt bloat
- noisy discovery
- too many tool-call round trips
- fragile multi-step mutations spread across many turns
- policy logic duplicated across individual tool surfaces

Code mode fixes this by turning many related workspace operations into one primary execution gateway.

## Core Architecture

Use this layered model:

1. Agent-facing workspace gateway
2. Runtime tool catalog and on-demand discovery
3. Host-side dispatcher
4. Worker-side sandbox
5. Policy and permission boundary at execution time

The gateway should let the model:

1. discover a tool family
2. inspect an exact tool schema only when needed
3. call the selected tool directly through one bundled execution block

## Execution Path

Recommended flow:

1. Agent calls one gateway tool.
2. Gateway receives `{ code, _timeout? }` or an equivalent structured call shape.
3. Host builds a function map for code-eligible tools.
4. Host validates the code before execution.
5. Host spawns a sandbox worker with no ambient secrets.
6. Worker exposes an async proxy object such as `workspace.*`.
7. Worker posts tool calls back to the host.
8. Host executes the real handlers and returns results.
9. Gateway returns logs, result, and retry-safe failure context.

## Discovery Model

Use lightweight discovery helpers instead of embedding the full surface eagerly.

Recommended helper set:

- `tool_pack_list()`
- `tool_pack_get({ name })`
- `tool_catalog_list({ query, pack, category, limit })`
- `tool_catalog_get({ name })`

This lets the model:

- see common workspace capabilities first
- inspect specialized packs only when needed
- fetch exact schemas lazily

## Tool Descriptor Shape

Use a stable runtime descriptor for every bundled tool.

Suggested fields:

- `name`
- `displayName`
- `description`
- `category`
- `pack`
- `inputSchema`
- `requiredParams`
- `optionalParams`
- `surface`
- optional transport hints
- optional permission profile

The descriptor exists for discovery and routing, not just documentation.

## Direct Vs Bundled Split

Make this decision explicit.

### Keep Direct

Keep tools direct when they:

- require human-facing UI or OAuth/browser flows
- block waiting on human input
- are intentionally one-at-a-time orchestration actions
- should remain visible as first-class top-level controls

### Bundle Behind Code Mode

Bundle tools when they are:

- CRUD/data operations
- non-blocking status queries
- fire-and-forget callbacks
- machine-driven orchestration that can be bounded by timeout

This classification is one of the most important design decisions in the whole system.

## Sandbox Boundary

The worker should be able to ask for tool execution, but not perform side effects directly.

Recommended properties:

- empty or highly constrained environment
- no direct FS/network/module loading
- only the proxy object and safe utilities injected
- whole-block timeout
- console capture
- explicit syntax and escape validation before execution

Good default stance:

- host owns all privileged effects
- worker owns only planning and sequencing

## Policy Boundary

Do not treat the gateway as a policy bypass.

Inspect bundled code at the gateway boundary.

Examples:

- safe mode should allow read-only discovery helpers
- safe mode should block bundled mutating calls
- dynamic aliasing or dynamic property access may need to be blocked in stricter modes if you cannot classify them safely

Policy belongs at the execution boundary, not scattered through every leaf tool.

## Failure Semantics

Your bundled gateway must report more than "timed out" or "failed."

At minimum, track:

- completed calls
- in-flight calls
- whole-block timeout
- direct structured tool errors

The key invariant:

Do not let the agent blindly retry a whole mutation block without being told what may already have persisted.

## Prompt Strategy

Teach a discovery-first flow:

1. search common workspace tools first
2. inspect one exact tool only when needed
3. call concrete methods directly
4. isolate long waits in their own gateway call

Do not force every model family into the same wording.
Shape the guidance by runtime/provider/model if needed.

## Transport-Neutral Principle

The transport can vary.

Examples:

- MCP tool such as `vesper_execute`
- direct function gateway such as `workspace_call`
- provider-native tool surface with separate catalog helpers

The portable part is not the tool name.
The portable part is:

- one gateway
- one catalog
- one host-owned dispatcher
- one sandbox boundary

## Minimum Success Criteria

A port is on the right track when:

1. bundled workspace actions no longer dominate the prompt surface
2. the model can batch related operations in one gateway call
3. sandboxed code cannot directly reach privileged resources
4. safe/read-only policy still works through the gateway
5. timeout and retry behavior are explicit enough to avoid duplicate mutations
