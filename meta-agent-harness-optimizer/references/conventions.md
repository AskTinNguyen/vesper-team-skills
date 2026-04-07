# Conventions — canvas-org/meta-agent

## Naming
- Snake_case for modules and functions (`meta_agent/task_runner.py:19-37`, `meta_agent/eval_runner.py:20-27`)
- Verb-first operational functions like `run_task`, `run_evaluation`, `invoke_proposer`, `validate_config`

## File organization
- `meta_agent/` for core runtime/orchestration
- `configs/` for strategy variants
- `benchmarks/` for declarative task definitions and adapters
- `images/` for writeup assets

**Evidence:** `README.md:111-118`

## Config contract
All config modules are expected to expose:
- `build_options(ctx: RunContext) -> ClaudeAgentOptions`

**Evidence:** `configs/vanilla.py:14-25`, `meta_agent/task_runner.py:27-37`

## Import style
Prefer absolute package imports like:
- `from meta_agent.run_context import RunContext`
- `from meta_agent.task_runner import TaskResult, run_task, run_command`

**Evidence:** `configs/vanilla.py:11`, `meta_agent/eval_runner.py:14-15`

## Persistence style
Prefer machine-readable JSON/JSONL and human-readable Markdown side-by-side.

**Evidence:** `meta_agent/eval_runner.py:73-110`

## Error handling style
- validate early,
- fail loudly at boundaries,
- degrade external tool/env failures into structured error outputs where useful.

**Evidence:** `meta_agent/benchmark.py:62-85`, `meta_agent/task_runner.py:27-37`, `benchmarks/tau3/sdk_adapter.py:47-71`, `benchmarks/tau3/sdk_adapter.py:77-117`
