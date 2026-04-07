# Architecture — canvas-org/meta-agent

## System Overview
`meta-agent` is a **Python modular monolith** for optimizing agent harnesses from execution traces rather than optimizing model weights.

The core loop is explicit in the module docstring of `meta_agent/outer_loop.py`:
1. invoke Claude Code as proposer,
2. inspect prior experience,
3. write a new config,
4. validate it,
5. evaluate it,
6. store results,
7. repeat (`meta_agent/outer_loop.py:4-11`).

That loop is supported by five main subsystems:
- benchmark loading,
- task execution,
- evaluation and artifact storage,
- CLI inspection over stored artifacts,
- proposer-driven outer-loop optimization.

## Component Catalog

### Benchmark layer
**Files:** `meta_agent/benchmark.py:8-87`, `benchmarks/example/benchmark.yaml:1-10`, `benchmarks/tau3/benchmark.yaml:1-10`

This layer turns YAML into a typed `Benchmark` model using Pydantic. It supports:
- local tasks with workspaces and verify commands,
- tau-style backend configuration,
- relative workspace resolution,
- type-specific validation.

### Config strategy layer
**Files:** `meta_agent/run_context.py:6-16`, `configs/vanilla.py:14-25`, `configs/bootstrap.py:25-39`, `configs/hooks.py:105-126`

Each harness candidate is a Python module exposing:
`build_options(ctx: RunContext) -> ClaudeAgentOptions`

This is the main strategy seam in the system.

### Task execution layer
**Files:** `meta_agent/task_runner.py:19-196`

This layer:
- imports the selected config,
- constructs runtime options,
- runs the agent via the Claude Agent SDK,
- serializes streamed messages to `trace.jsonl`,
- runs the verify command,
- returns a structured `TaskResult`.

### Evaluation layer
**Files:** `meta_agent/eval_runner.py:20-248`

This layer:
- runs many tasks in parallel,
- builds a candidate directory under `experience/<bench>/candidates/<name>/`,
- computes aggregate pass rate/cost/turns,
- stores per-task JSON, traces, and markdown summaries.

This is the **filesystem experience store**.

### CLI inspection layer
**Files:** `meta_agent/cli.py:23-260`

This exposes the experience store through commands like:
- `list`
- `show`
- `diff`
- `pareto`
- `failures`

The proposer itself is instructed to use this CLI, which means the same inspection surface works for humans and agents.

### Outer-loop proposer layer
**Files:** `meta_agent/outer_loop.py:57-186`, `meta_agent/outer_loop.py:438-606`, `SKILL.md:1-121`

This layer shells out to `claude`, stages the next config, validates it, evaluates it, records history, and optionally runs holdout or skill evolution.

### Tau adapter layer
**Files:** `benchmarks/tau3/sdk_adapter.py:29-239`

This layer wraps tau tools and the simulated customer as SDK tools so the same config/hook patterns apply to benchmarked customer-service tasks.

## Data Flow
```text
benchmark YAML
  -> load_benchmark()
  -> task set + backend info
  -> config module build_options(ctx)
  -> task_runner.run_task()
  -> trace.jsonl + result.json + verify result
  -> eval_runner.build_experience_dir()
  -> experience/<benchmark>/candidates/<candidate>/...
  -> meta_agent.cli reads this store
  -> outer_loop prompts proposer using that store
  -> new config staged and validated
  -> next evaluation run
```

## Key architectural decisions observed

### 1) Keep optimizer memory on disk
**Evidence:** `meta_agent/eval_runner.py:24-110`, `README.md:89-91`, `WRITEUP.md:29-31`

The system uses directories and JSON/Markdown/JSONL artifacts rather than a database. That makes every iteration transparent and diffable.

### 2) Optimize harness artifacts, not task outputs
**Evidence:** `meta_agent/outer_loop.py:156-166`, `SKILL.md:1-39`

The proposer is explicitly asked to improve the config module, not manually fix each task. This is how the system turns local failure analysis into reusable harness improvements.

### 3) Keep proposal and evaluation loosely coupled through artifacts
**Evidence:** `meta_agent/outer_loop.py:153-166`, `meta_agent/cli.py:54-260`

The proposer reads from the same artifact store a human can read. That reduces hidden state and improves auditability.

### 4) Make meta-optimization a first-class extension
**Evidence:** `meta_agent/outer_loop.py:189-347`, `meta_agent/outer_loop.py:577-583`

The repo includes a second-order loop that can improve the proposer skill itself.

## Why this matters for Vesper
This architecture maps naturally to Vesper if building:
- a candidate ledger for harness variants,
- trace-aware improvement loops,
- a code-mode or session-mode proposer that edits harness configuration,
- a holdout-aware evaluator,
- or a team-visible diffable memory of what harness changes worked.
