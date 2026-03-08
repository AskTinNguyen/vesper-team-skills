# Model-Shaped Harness Patterns

Use this reference when implementing the pattern behind `docs/internals/code-mode-token-optimization.md` in Vesper or porting the same ideas into another agent application.

## Load By Subtask

| Need | Section |
|------|---------|
| Design a compact executor | `Compact Executor With Progressive Discovery` |
| Design mount profiles | `Progressive Tool Mounting` |
| Classify tools | `Tool Classification Rubric` |
| Sequence the implementation | `Integration Sequence` |
| Verify gains | `Measurement Guidance` and `Verification Checklist` |
| Recover from failures | `Troubleshooting And Recovery` |
| Wire Vesper specifically | `Vesper Implementation Map` |

## Why This Pattern Matters

The central insight is simple:

- token overhead often comes more from tool declarations than from the user's words
- large static tool surfaces penalize every turn, even when the model only needs one or two operations
- the right fix is architectural, not cosmetic

The winning pattern is to shape the harness around the model's reasoning loop:

1. give the model one obvious execution path for code-eligible work
2. expose exact schema progressively instead of eagerly
3. mount only the surfaces needed for the current turn profile

This is what "model-shaped harness building" means. Build the interface the model sees around inference economics and action patterns, not around human-oriented module boundaries.

## Architecture Decisions

### 1. Collapse code-eligible tools behind a single executor

Use a single executor tool when the underlying operations are:

- deterministic
- parameterized
- non-visual
- compatible with batching
- safe to call from code without pausing for judgment

Good candidates:
- CRUD
- search
- memory lookup
- schedule inspection or mutation
- config operations
- status polling
- orchestrator control with explicit timeout guidance

Keep these outside the executor:
- human approval prompts
- `render_ui`-style presentation tools
- OAuth or credential acquisition
- operations that intentionally pause the model loop

### 2. Make discovery dynamic

Do not embed a full declaration dump for every bundled tool in the main tool description.

Instead:
- keep category guidance in the description
- add a tiny catalog API for exact lookup
- let the model fetch schema only when needed

This preserves exactness while avoiding giant eager prompt payloads.

### 3. Make mount policy explicit

Do not scatter "minimal mode" behavior across many call sites.

Create a typed mount profile that decides:
- which session tools exist
- whether the code-mode executor mounts
- whether built-in servers mount
- whether workspace source servers mount
- whether all-sources context is injected
- whether old source state should be cleared

### 4. Deduplicate capability before optimizing descriptions

If the same family is exposed both:
- inside the executor
- and as a standalone tool or source surface

remove the duplicate first. Reducing schema verbosity does not fix duplicated capability exposure.

### 5. Optimize for retry-safe execution

When many operations move behind one executor, timeout design matters more.

Make the executor:
- support explicit `_timeout`
- explain that timeout applies to the whole block
- report completed calls before timeout when possible
- warn that side effects may already be persisted

This keeps batching useful without making retries dangerous.

## Tool Classification Rubric

| Situation | Default placement |
|-----------|-------------------|
| Deterministic CRUD, search, config, status | Executor |
| UI pause, approval, OAuth, credential collection | Standalone |
| Broad family with sparse usage | Deferred pack or catalog-first |
| Simple typed mutation with explicit retry guidance | Usually executor |
| Partial side effects or hidden external state | Standalone or escalate |
| Provider-sensitive or permission-sensitive ambiguity | Escalate before bundling |

## Reference Architecture

Use a three-layer model-facing design:

1. `session` server
   Keep interactive, human-gated, or UI-coupled tools here.
2. `execute` server
   Expose one tool such as `app_execute` or `vesper_execute`.
3. `mount profile` resolver
   Decide which surfaces exist for each turn.

The result is a harness that is:
- compact on most turns
- exact when needed
- reusable across apps

## Integration Sequence

Implement in this order:

1. Define the mount-profile resolver.
2. Define the executor and discovery surface.
3. Classify which tools stay standalone versus executor-bound.
4. Wire session-scoped or built-in server assembly from the resolver.
5. Add duplicate-source normalization.
6. Add renderer or main-process sync for effective mounted state.
7. Re-measure representative turns and record evidence.

## Example: Compact Executor With Progressive Discovery

```ts
type ToolDefinition = {
  name: string;
  category: string;
  description: string;
  inputSchema: Record<string, unknown>;
  handler: (args: unknown) => Promise<unknown>;
};

function buildCatalogEntries(tools: ToolDefinition[]) {
  return tools.map((tool) => ({
    name: tool.name,
    category: tool.category,
    description: tool.description,
  }));
}

export function createAppExecuteTool(tools: ToolDefinition[]) {
  const catalogEntries = buildCatalogEntries(tools);
  const catalogByName = new Map(tools.map((tool) => [tool.name, tool]));

  return tool(
    "app_execute",
    [
      "Use this tool for app data operations.",
      "Discover exact methods on demand first:",
      '- await app.tool_catalog_list({ query: "schedule" })',
      '- await app.tool_catalog_get({ name: "schedule_create" })',
      "- Then call the real method with await app[toolName](params)",
    ].join("\n"),
    {
      code: z.string().min(1),
      _timeout: z.number().int().min(1000).max(600000).optional(),
    },
    async ({ code, _timeout }) => {
      const fns: Record<string, (args: unknown) => Promise<unknown>> = {};

      fns.tool_catalog_list = async (args: any) => {
        const query = String(args?.query ?? "").trim().toLowerCase();
        const limit = Math.max(1, Math.min(100, Number(args?.limit ?? 25)));
        const filtered = catalogEntries.filter((entry) => {
          if (!query) return true;
          const haystack =
            `${entry.name} ${entry.category} ${entry.description}`.toLowerCase();
          return haystack.includes(query);
        });
        return {
          items: filtered.slice(0, limit),
          total: filtered.length,
          truncated: filtered.length > limit,
        };
      };

      fns.tool_catalog_get = async (args: any) => {
        const name = String(args?.name ?? "").trim();
        const tool = catalogByName.get(name);
        if (!tool) throw new Error(`Unknown tool: ${name}`);
        return {
          name: tool.name,
          category: tool.category,
          description: tool.description,
          inputSchema: tool.inputSchema,
        };
      };

      for (const toolDef of tools) {
        fns[toolDef.name] = toolDef.handler;
      }

      return runInSandboxedExecutor({
        code,
        timeoutMs: _timeout ?? 30000,
        bindings: { app: fns, console },
      });
    },
  );
}
```

Why this works:
- one mounted tool replaces a large sibling tool family
- category guidance stays cheap
- exact schema lookup moves to runtime
- the model can batch multiple operations inside one execution block

## Example: Progressive Tool Mounting

```ts
export type ToolProfile = "default" | "automation_minimal" | "research_readonly";

export interface ToolMountProfile {
  profile: ToolProfile;
  includeSessionServer: true;
  includeExecuteServer: boolean;
  includeBrowserServer: boolean;
  includeWorkspaceSources: boolean;
  includeAllSourcesContext: boolean;
  buildEnabledSourceServers: boolean;
}

const TOOL_MOUNT_PROFILES: Record<ToolProfile, ToolMountProfile> = {
  default: {
    profile: "default",
    includeSessionServer: true,
    includeExecuteServer: true,
    includeBrowserServer: true,
    includeWorkspaceSources: true,
    includeAllSourcesContext: true,
    buildEnabledSourceServers: true,
  },
  automation_minimal: {
    profile: "automation_minimal",
    includeSessionServer: true,
    includeExecuteServer: false,
    includeBrowserServer: false,
    includeWorkspaceSources: false,
    includeAllSourcesContext: false,
    buildEnabledSourceServers: false,
  },
  research_readonly: {
    profile: "research_readonly",
    includeSessionServer: true,
    includeExecuteServer: true,
    includeBrowserServer: true,
    includeWorkspaceSources: true,
    includeAllSourcesContext: true,
    buildEnabledSourceServers: true,
  },
};

export function resolveToolMountProfile(profile?: ToolProfile) {
  return TOOL_MOUNT_PROFILES[profile ?? "default"];
}
```

Then wire server construction from that resolver:

```ts
const mountProfile = resolveToolMountProfile(turnOptions?.toolProfile);

const mcpServers = {
  session: getSessionServer(sessionId, rootPath, sessionOptions),
  ...(mountProfile.includeExecuteServer ? { app: getExecuteServer(...) } : {}),
  ...(mountProfile.includeBrowserServer ? { browser: getBrowserServer(...) } : {}),
  ...(mountProfile.includeWorkspaceSources ? sourceServers : {}),
};

agent.setAllSources(mountProfile.includeAllSourcesContext ? allSources : []);

if (!mountProfile.buildEnabledSourceServers) {
  clearBuiltSourceStateForTurn();
}
```

Why this works:
- each turn gets a deterministic surface
- minimal turns stop inheriting expensive or stale mounts
- the policy becomes reusable and testable

## Example: Duplicate Source Normalization

If a source family is already mirrored into the executor, strip the duplicate source in code mode.

```ts
const CODE_MODE_DUPLICATE_SOURCE_SLUGS = new Set(["app-canvas"]);

export function normalizeEnabledSourceSlugs(
  sourceSlugs: string[] | undefined,
  options: { codeModeEnabled: boolean },
): string[] | undefined {
  const deduped: string[] = [];
  const seen = new Set<string>();

  for (const slug of sourceSlugs ?? []) {
    if (seen.has(slug)) continue;
    seen.add(slug);
    if (options.codeModeEnabled && CODE_MODE_DUPLICATE_SOURCE_SLUGS.has(slug)) {
      continue;
    }
    deduped.push(slug);
  }

  return deduped.length > 0 ? deduped : undefined;
}
```

Also emit a UI sync event when normalization changes the effective source set so the model-facing optimization does not silently desync the renderer.

## How Code Mode Helps

Code mode is useful because it changes the shape of the agent loop:

- one tool call can perform multiple operations
- the model can sequence work locally with `await`
- schema discovery becomes progressive
- timeout policy becomes centralized
- broad capability becomes cheap to mount

The key insight is not merely "run code."

The deeper value is:
- consolidate a wide action surface into one model-facing entrypoint
- let the model compose operations without extra API turns
- move from tool-count scaling to harness-quality scaling

## System Prompt And Tool Routing

If one tool is the intended primary path, state that directly in system instructions.

Bad pattern:
- tell the model to discover the right tool through ToolSearch every turn

Better pattern:
- name the executor explicitly
- say when to call it directly
- reserve ToolSearch or catalog lookup for method discovery inside the executor

This avoids spending one extra reasoning step to find the tool that the model was always supposed to use.

## Configuration Precedence

Use a deterministic override order:

1. Hard runtime/provider constraints
2. Workspace feature flags
3. Provider-harness defaults
4. Turn-level `toolProfile` or equivalent
5. Explicit manual override for the current run

If two layers disagree, document which layer won.

## Optimization Checklist

When optimizing an existing agent app, check these in order:

1. Duplicate surfaces
   Look for the same capability exposed as source tools and executor bindings.
2. Static schema mass
   Check whether the main tool description embeds giant declarations or raw schemas.
3. Mount defaults
   Check whether minimal turns still build sources, browser, or broad built-ins.
4. Inherited state
   Check whether turns reuse old mounts even when the current profile should be smaller.
5. Prompt routing
   Check whether system instructions force unnecessary ToolSearch steps.
6. Timeout ergonomics
   Check whether batched executor calls can be retried safely.

## Measurement Guidance

Measure both shape and effect:

- total tool count mounted per turn
- deferred tool tokens or equivalent schema mass estimates
- executor description size before and after compaction
- median token usage for common turns
- failure or retry behavior after batching

Use local modeled estimates for comparison if billing numbers are noisy, but keep the relative deltas visible.

## Verification Checklist

For each target path, capture:

- before/after mounted tool or server count
- before/after schema-mass estimate or telemetry
- one retained capability reached through the new harness shape
- one minimal-profile replay proving stale mounts were not inherited
- one note covering timeout/retry behavior for long executor calls

If any of these are unavailable, state the gap explicitly.

## Troubleshooting And Recovery

| Symptom | Likely cause | Inspect | Safe recovery |
|---------|--------------|---------|---------------|
| Minimal turn still sees broad tools | Old mounts still reused | mount-profile resolver and turn assembly | clear mounted source/server state for that turn |
| Capability disappeared after dedupe | duplicate surface was removed before executor parity existed | executor bindings and source normalization | restore one surface until parity is real |
| Duplicate writes after timeout | long call mixed fast CRUD with slow orchestration | executor timeout guidance and completed-call reporting | split long operations into separate executor calls |
| Model keeps searching for tools instead of using executor | routing instructions too weak | system/developer prompt and tool description | make the intended primary tool explicit |
| Provider path behaves differently than expected | provider contract guessed, not verified | provider capability detection | downgrade to conservative harness and mark assumptions |

## Porting The Pattern To Other Agent Apps

Translate the pattern, not the names.

Examples:

- project management app
  Use `project_execute` for issues, docs, schedules, and configs.
- research workspace
  Use `research_execute` for search, note CRUD, tagging, and synthesis orchestration.
- ops control plane
  Use `ops_execute` for jobs, alerts, runbooks, and service annotations.

In each case:
- keep human approval flows separate
- keep the executor compact
- use progressive schema discovery
- drive mounts from turn profiles

Framework-agnostic wiring sketch:

```ts
const contract = detectProviderContract(runtime);
const harness = resolveHarnessProfile({ contract, model, toolProfile });
const mountProfile = resolveToolMountProfile(harness, turnOptions);
const executor = mountProfile.includeExecuteServer ? createAppExecuteTool(toolSet) : null;
const mcpServers = buildServers({ mountProfile, executor, sourceServers });
```

## Vesper Implementation Map

Use these files as the concrete reference implementation. Verify current locations and tool names if the repo has recently moved:

- `docs/internals/code-mode-token-optimization.md`
  Source explanation of the three-phase optimization.
- `docs/internals/code-mode.md`
  Broader Code Mode architecture and executor behavior.
- `packages/shared/src/agent/code-mode-tool.ts`
  `vesper_execute`, compact discovery helpers, timeout guidance, executor binding map.
- `packages/shared/src/agent/tool-mount-profile.ts`
  Shared typed resolver for `default` and `schedule_minimal`.
- `packages/shared/src/agent/session-scoped-tools.ts`
  Dedicated code-mode server construction and session tool profile handling.
- `packages/shared/src/agent/vesper-agent.ts`
  Turn-time server assembly from the mount profile.
- `apps/electron/src/main/session-source-normalization.ts`
  Code-mode duplicate source stripping and canvas auto-attach behavior.
- `apps/electron/src/main/sessions.ts`
  Main-process normalization, source syncing, and `sources_changed` emission.

## Vesper-Specific Lessons Worth Reusing

These are observed in Vesper at the time of writing and should be rechecked if the implementation changes:

- Removing duplicate Canvas exposure mattered before optimizing descriptions.
- Compact discovery produced a larger gain than small wording tweaks.
- Minimal-turn determinism required clearing mounts, not only skipping some additions.
- A dedicated executor server made the intended call path clearer than burying the executor inside a crowded session server.

## Future Direction

Model-shaped harnesses are the future because agent apps will keep gaining capabilities, but models still pay per visible surface.

The scalable path is:
- fewer mounted entrypoints
- richer runtime discovery
- tighter profile control
- clearer execution contracts

Do not keep adding tools as if the model sees them for free.

Shape the harness so the model sees:
- the minimum surface needed to start
- the exact schema only when needed
- one obvious path for broad programmable work
