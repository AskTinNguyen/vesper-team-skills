# Tool Calls and Tool Surfaces — canvas-org/meta-agent

This file captures the repo's **tool-facing behavior**: Claude CLI flags, Claude Agent SDK hooks, benchmark tool adapters, and the main tool call surfaces agents operate through.

## 1) Claude CLI invocation surface
**Implementation:** `meta_agent/outer_loop.py:57-136`

The outer loop shells out to Claude Code with:
- `--print`
- `--verbose`
- `--output-format stream-json`
- `--append-system-prompt <system_append>`
- `--allowedTools Read,Write,Edit,Bash,Glob,Grep`
- `--max-turns <N>`
- `-p <prompt>`
- optional `--model`
- optional `--permission-mode`

This is the proposer's raw tool surface.

## 2) Claude Agent SDK tool surface in configs
**Evidence:** `configs/vanilla.py:16-24`, `configs/bootstrap.py:26-38`, `configs/hooks.py:106-126`

The baseline configs rely on Claude Agent SDK presets:
- `system_prompt={"type": "preset", "preset": "claude_code"}`
- `tools={"type": "preset", "preset": "claude_code"}`

This means the runtime largely inherits the standard Claude Code tool surface and then shapes behavior through prompts or hooks.

## 3) Hook event surface
**Evidence:** `configs/hooks.py:18-126`, `SKILL.md:59-84`

Observed hook event names:
- `PreToolUse`
- `PostToolUse`
- `Stop`
- `UserPromptSubmit` (documented in the bundled prompt skill)
- `PostToolUseFailure` (documented in the bundled prompt skill)

Observed repo implementation:
- `detect_bash_loops(...)` on `PreToolUse` for `Bash` (`configs/hooks.py:18-60`)
- `track_bash_result(...)` on `PostToolUse` for `Bash` (`configs/hooks.py:63-81`)
- `force_verification_on_stop(...)` on `Stop` (`configs/hooks.py:84-126`)

## 4) Tool-use patterns encouraged by proposer prompt
**Evidence:** `SKILL.md:19-39`, `SKILL.md:59-114`

The bundled proposer prompt explicitly ranks levers by cost:
1. prompt improvements,
2. light hooks,
3. tool restrictions / permission rewrites,
4. custom MCP tools,
5. subagents.

This is effectively the repo's **tool intervention hierarchy**.

## 5) Custom tool pattern documented in proposer prompt
**Evidence:** `SKILL.md:84-98`

The skill includes a canonical pattern for defining SDK tools:
- `@tool(...)`
- `create_sdk_mcp_server(...)`
- allowing `mcp__harness__<tool_name>` entries in tool permissions.

This is guidance rather than code in the current repo, but it is still part of the captured tool surface because the proposer is expected to use it.

## 6) Tau adapter tools
**Implementation:** `benchmarks/tau3/sdk_adapter.py:38-125`

### `talk_to_customer`
Defined with:
- `@tool("talk_to_customer", ...)`
- schema `{"message": str}`

Purpose:
- send agent text to the simulated customer,
- get the next customer response,
- record the exchange into tau trajectory state.

**Evidence:** `benchmarks/tau3/sdk_adapter.py:42-73`

### Wrapped tau environment tools
The adapter iterates `env.get_tools()` and wraps each environment tool with a generated `@tool(...)` handler.

What each wrapper does:
- executes `env.make_tool_call(name, **args)`
- converts result to JSON string
- appends both tool-call and tool-message entries into tau trajectory
- logs tool usage in `state.tool_call_log`

**Evidence:** `benchmarks/tau3/sdk_adapter.py:75-125`

## 7) Message and block serialization surface
**Implementation:** `meta_agent/task_runner.py:40-100`

Captured block types:
- `TextBlock`
- `ThinkingBlock`
- `ToolUseBlock`
- `ToolResultBlock`

Captured message types:
- `AssistantMessage`
- `ResultMessage`
- `UserMessage`
- `SystemMessage`

This is the schema of what enters `trace.jsonl` and therefore what the proposer later inspects.

## 8) Verify commands as post-agent tool calls
**Implementation:** `meta_agent/task_runner.py:179-196`

After agent execution, a verify command is run via `run_command(...)`.
This is not an agent tool call itself, but it is part of the execution surface because pass/fail is determined here.

## 9) Why this matters when porting to Vesper
To port this architecture, preserve four distinct tool layers:
- **proposer shell tool surface**
- **runtime agent tool surface**
- **benchmark/environment adapter tools**
- **verification command surface**

Collapsing them together loses a major part of what makes the system inspectable and optimizable.
