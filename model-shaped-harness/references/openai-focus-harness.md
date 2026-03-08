# OpenAI Focus Harness

Optional provider appendix for OpenAI-family and Responses-compatible runtimes.

Freshness status:

- Last verified against official OpenAI docs: March 8, 2026
- Verified from docs: Responses is recommended for new projects, hosted tools exist in Responses, tool search and `defer_loading` exist, prompt caching rewards stable prefixes, `previous_response_id` still bills prior input tokens, and `/responses/compact` exists in current Codex guidance.
- Inference layered on top: how Vesper should map those capabilities into harness profiles, and how hypothetical gateways such as Gateway or Veer should be classified.
- Treat model-name lists below as examples as of March 8, 2026, not a durable taxonomy.

For OpenAI-family models, make the harness Responses-native, Codex-shaped, cache-stable, and deferred-by-default.

This recommendation combines verified OpenAI platform guidance with architectural inference. Official docs currently recommend the Responses API for new projects and document hosted tools, tool search, prompt caching, conversation state, and compaction behavior. The Codex materials reinforce additional harness patterns such as stateless requests when needed, model-specific instructions, stable tool lists, and compaction for long threads.

Sources:
- Responses API migration guide
  https://developers.openai.com/api/docs/guides/migrate-to-responses
- Using tools
  https://developers.openai.com/api/docs/guides/tools
- Prompt caching
  https://developers.openai.com/api/docs/guides/prompt-caching
- Conversation state
  https://developers.openai.com/api/docs/guides/conversation-state
- Unrolling the Codex agent loop
  https://openai.com/index/unrolling-the-codex-agent-loop/
- OpenAI Agents JS tools guide
  https://openai.github.io/openai-agents-js/guides/tools/

## What The OpenAI-Shaped Harness Should Be

If Gateway or Veer expose a real Responses-compatible contract, map them to one of these harnesses. Treat this mapping as design scaffolding until the actual provider contract is verified end to end:

1. `openai_codex_workspace`
   Target: `gpt-5-codex`, `gpt-5.1-codex`, `gpt-5.2-codex`, `gpt-5.3-codex`
   Use for: coding, workspace mutation, long-horizon agentic work
2. `openai_responses_general`
   Target: `gpt-5.1`, `gpt-5.2`, `gpt-4.1`, `gpt-4o`
   Use for: general agent work, mixed reasoning, search, retrieval, structured tasks
3. `openai_responses_mini`
   Target: `gpt-5 mini`, `gpt-5 nano`, `gpt-4o mini`
   Use for: routing, classification, extraction, lightweight read flows
4. `openai_compat_legacy`
   Target: OpenAI-compatible gateways that do not support the full Responses tool contract
   Use for: degraded fallback only

## 1. `openai_codex_workspace`

Use this as the main harness for OpenAI coding models.

Top-level mounted surface:

- `vesper_execute`
- `ask_user`
- `render_ui`
- approval/auth tools
- delegation/session lifecycle tools only if the workspace feature flags allow them
- OpenAI built-in tools when useful: `web_search`, `file_search`, maybe `code_interpreter`

What should not be eagerly mounted:

- giant standalone Canvas families
- broad schedule/messaging/memory/source tool catalogs
- all workspace MCP sources by default

Instead, use deferred packs:

- canvas
- schedule
- memory
- messaging
- sources
- teams

For OpenAI endpoints, strongly consider using native tool search and `namespace` + `defer_loading` patterns instead of only a custom catalog. OpenAI's tools guide currently supports loading deferred tools at runtime and says tool search optimizes token usage and latency. Verify exact tool names and hosted-tool availability for the target model before implementation.

Source:
- Using tools
  https://developers.openai.com/api/docs/guides/tools

So the OpenAI Codex harness should look like:

- Stable prefix:
  - model-specific developer instructions
  - sandbox/permission block
  - workspace/project instructions
  - stable tool manifest
- Stable top-level tools:
  - `vesper_execute`
  - a few essential interaction tools
  - OpenAI hosted tools
- Deferred capability packs:
  - load only when the model reaches for them

Why this fits OpenAI:

- Codex uses model-specific instructions and a stable tool list
- OpenAI recommends strict function schemas
- OpenAI supports hosted tools, MCP, and tool search
- Prompt caching improves when tools and instructions stay identical across requests

## 2. `openai_responses_general`

Use this for GPT-5.x general models and GPT-4.1 / GPT-4o.

This harness should be narrower than Codex.

Mounted by default:

- `ask_user`
- `render_ui`
- `web_search`
- `file_search`
- maybe a thin `vesper_execute`, but only when task classification says the user wants workspace actions

Not mounted by default:

- deep coding harness
- large MCP source sets
- broad Canvas/runtime/editing packs
- browser/computer-use unless task explicitly requires it

This is the "smart generalist" harness:

- use OpenAI built-in tools first where they replace custom weight
- use strict structured outputs
- mount `vesper_execute` only for actual action-heavy turns
- prefer read-first, action-later shaping

Inference:

GPT-4o / GPT-5 general models should not automatically pay the full Codex-style workspace tax unless the turn is actually agentic enough to justify it.

## 3. `openai_responses_mini`

Use this as a deliberately small harness.

Mounted by default:

- no `vesper_execute`
- no broad source mounting
- structured output schemas
- maybe `web_search` for narrow factual tasks
- maybe one router/handoff tool

Best use:

- classify
- route
- summarize
- extract
- select the next harness

This follows current OpenAI guidance to baseline with the best model and then replace with smaller models where acceptable. Treat that as a heuristic, not a permanent rule, because price/performance tradeoffs can change.

Source:
- A practical guide to building agents
  https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf

In practice, let mini models decide:

- is this a read/query task?
- is this a coding/workspace task?
- should I hand off to `openai_codex_workspace`?

So the mini harness becomes a front controller, not a full agent shell.

## 4. `openai_compat_legacy`

If Gateway or Veer claim "OpenAI compatible" but do not actually support:

- Responses API
- tool search
- MCP tools
- strict function behavior
- compaction
- prompt caching semantics

then they should not get the full OpenAI-shaped harness.

They should get:

- a small curated function-tool set
- no deferred pack assumptions
- no Responses-specific compaction/state logic
- no Codex-style long-horizon coding harness

Key rule:

The harness should be keyed by provider contract, not just provider name.

## What Vesper Should Do Technically

Add a provider resolver above the current turn profile system:

`provider/model/runtime + toolProfile -> providerHarnessProfile`

Example:

```ts
type ProviderHarnessProfile =
  | 'openai_codex_workspace'
  | 'openai_responses_general'
  | 'openai_responses_mini'
  | 'openai_compat_legacy';
```

First detect capabilities:

```ts
interface ProviderContract {
  responsesApi: boolean;
  toolSearch: boolean;
  remoteMcp: boolean;
  hostedWebSearch: boolean;
  hostedFileSearch: boolean;
  hostedCodeInterpreter: boolean;
  strictFunctions: boolean;
  promptCaching: boolean;
  responsesCompact: boolean;
  previousResponseId: boolean;
}
```

Then map:

- Codex model + strong Responses contract -> `openai_codex_workspace`
- GPT general + strong Responses contract -> `openai_responses_general`
- Mini model + strong Responses contract -> `openai_responses_mini`
- anything weaker -> `openai_compat_legacy`

## The Best OpenAI-Specific Gems To Borrow

From OpenAI docs and Codex materials, these are the most important patterns to copy. Recheck these references before implementation if the provider surface may have changed:

- Use Responses, not legacy chat completions, for agentic flows.
  Source: Migrate to the Responses API
  https://developers.openai.com/api/docs/guides/migrate-to-responses
- Use strict tool schemas with `additionalProperties: false`.
  Source: Using tools
  https://developers.openai.com/api/docs/guides/tools
- Keep tool descriptions short and explicit; one responsibility per tool.
  Source: Agents JS tools best practices
  https://openai.github.io/openai-agents-js/guides/tools/
- Prefer tool search / deferred loading for large tool surfaces.
  Source: Using tools
  https://developers.openai.com/api/docs/guides/tools
- Keep prompt prefixes stable for prompt caching; tool order stability matters.
  Sources: Prompt caching, Codex agent loop
  https://developers.openai.com/api/docs/guides/prompt-caching
  https://openai.com/index/unrolling-the-codex-agent-loop/
- Use model-specific instructions for different OpenAI model families.
  Source: Codex agent loop
  https://openai.com/index/unrolling-the-codex-agent-loop/
- Use `/responses/compact` for long-running threads.
  Source: Codex agent loop
  https://openai.com/index/unrolling-the-codex-agent-loop/
- Treat `previous_response_id` as optional statefulness, not a free token reduction trick; prior tokens are still billed.
  Source: Conversation state
  https://developers.openai.com/api/docs/guides/conversation-state

## Concrete Recommendation For Vesper

Use a Responses-native OpenAI harness where Codex-style coding models get `vesper_execute` + deferred capability packs + hosted OpenAI tools, general GPT models get a narrower curated harness, mini models become routers, and OpenAI-compatible gateways only get that shape if they prove they support the actual Responses contract.
