# Vesper-Specific Adaptations

This file is the anti-cargo-cult guide.

Use Vesper as the source pattern, but replace these seams in other apps.

## Product-Specific Tool Families

These are Vesper product concepts, not part of the portable core:

- checklists
- artifacts
- teams and councils
- mission control
- TillDone
- messaging bootstrap flows
- Vesper UI inspector tools
- Fresh Supervisor Loop

In another app, replace them with your own real workspace domains.

## Server Names And Tool Names

These names are Vesper-specific:

- `vesper`
- `session`
- `mcp__vesper__vesper_execute`
- `vesper_workspace_call`

Keep the role, not the literal names.

What matters:

- one dedicated gateway surface
- one or more direct/runtime-specific surfaces for always-individual tools and runtime-native capabilities

## Turn Profiles

Vesper has profile-specific mount behavior such as:

- `default`
- `interactive_compact`
- `schedule_minimal`

Those exact profile names are not portable.

Portable takeaway:

- some turns should get the full gateway
- some turns should get a compact shaped surface
- some automation turns should deliberately skip broad workspace tooling

## Source And MCP Model

In the Claude code-mode path, Vesper blends:

- built-in MCP servers
- active source servers
- provider-shaped prompt context

Vesper also has other runtime-specific surfaces, including the PI workspace harness and Pi plugin tools. Do not collapse those into a fake "one direct surface" model when porting the architecture.

If your app does not have MCP or source activation, keep the same concept at a higher level:

- built-in tools
- dynamically mounted external capability sources
- active-only exposure when context pressure matters

## Prompt Shaping By Provider

Vesper resolves harness profiles such as:

- `claude_workspace`
- `openai_codex_workspace`
- `openai_responses_general`
- `openai_responses_mini`

Do not copy these profile names unless your app already uses the same runtime split.

Portable takeaway:

- different model families may need different discovery wording
- some models benefit from `core`-first discovery
- some runtimes may need a different transport even with the same underlying capability graph

## Compact Progressive Exposure

In Vesper, some capabilities trimmed from the direct surface are still reachable progressively through the gateway, such as:

- GitHub
- `render_ui`

Portable takeaway:

- trimming direct surface does not require deleting capability
- progressive gateway exposure can replace eager top-level mounting

## Electron And Main-Process Wiring

Vesper-specific implementation seams include:

- Electron main/preload/renderer boundaries
- BrowserPaneManager and native browser tooling
- session manager lifecycle and workspace persistence

If your app is web-only, server-side, mobile, or CLI-native, replace those with your actual privileged execution boundary.

The portable rule is:

- the host side owns privilege
- the bundled code runner does not

## Existing Vesper References To Study

Use these when deriving the pattern:

- `docs/internals/code-mode.md`
- `docs/internals/openai-provider-harness.md`
- `docs/internals/platform-tools.md`
- `packages/shared/src/agent/code-mode-tool.ts`
- `packages/shared/src/agent/code-executor.ts`
- `packages/shared/src/agent/code-executor-worker.ts`
- `packages/shared/src/agent/runtime/shared/runtime-tools/runtime-tool-catalog.ts`
- `packages/shared/src/agent/provider-harness-profile.ts`
- `packages/shared/src/agent/session-scoped-tools.ts`
- `packages/shared/src/agent/runtime/pi/pi-runtime-adapter.ts`

## What To Strip First In A Port

If you are moving fast, strip these first:

1. Vesper product nouns
2. Vesper server/tool names
3. Vesper turn-profile names
4. Electron-specific lifecycle wiring
5. Vesper-only orchestration flows

Keep these longest:

1. gateway architecture
2. host-side dispatcher
3. catalog-driven discovery
4. sandbox boundary
5. policy-at-gateway enforcement
6. retry-safe failure reporting
