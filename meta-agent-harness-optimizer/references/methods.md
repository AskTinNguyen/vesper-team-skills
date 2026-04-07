# Methods and Key Functions — canvas-org/meta-agent

This file captures the repo's most important methods, what they do, and where they live.

## Benchmark loading

### `load_benchmark(path: str) -> Benchmark`
**File:** `meta_agent/benchmark.py:47-87`

Loads YAML, validates it through Pydantic, resolves local workspace paths, and materializes backend config for tau benchmarks.

### Data models
**File:** `meta_agent/benchmark.py:8-45`
- `Task`
- `HarborBackend`
- `TauBackend`
- `Benchmark`

These are the main schema boundary objects.

## Task runtime

### `run_command(cmd, cwd, timeout=300)`
**File:** `meta_agent/task_runner.py:19-25`

Runs shell or argv-based commands. Used for setup and verification.

### `load_config_module(config_path: str)`
**File:** `meta_agent/task_runner.py:27-37`

Dynamic-import seam for harness configs. Enforces the `build_options` contract.

### `serialize_block(block)`
**File:** `meta_agent/task_runner.py:40-64`

Normalizes Claude Agent SDK block types into JSON-friendly records.

### `serialize_message(message)`
**File:** `meta_agent/task_runner.py:67-100`

Normalizes SDK message types into JSONL trace entries.

### `run_task(task, config_path, model, work_dir) -> TaskResult`
**File:** `meta_agent/task_runner.py:121-196`

This is the core runtime method.
It:
- imports the config,
- builds options with `RunContext`,
- streams query output,
- writes `trace.jsonl`,
- stores `result.json`,
- runs verification,
- returns `TaskResult`.

## Evaluation

### `get_experience_dir(bench_name: str) -> Path`
**File:** `meta_agent/eval_runner.py:20-21`

Converts a benchmark name into the canonical candidate storage directory.

### `build_experience_dir(name, config_path, model, results, experience_dir=None) -> Path`
**File:** `meta_agent/eval_runner.py:24-110`

Materializes the filesystem memory for a candidate:
- copied `config.py`
- `per_task/*.json`
- `per_task/*_trace.jsonl`
- `scores.json`
- `summary.md`

### `run_local_tasks(...)`
**File:** `meta_agent/eval_runner.py:113-138`

Executes local tasks concurrently using a semaphore and temporary workspaces.

### `run_tau_tasks(...)`
**File:** `meta_agent/eval_runner.py:141-248`

Runs tau tasks concurrently with retries, timeout handling, and pass-rate logging.

## CLI inspection

### `load_scores(candidate_dir)`
**File:** `meta_agent/cli.py:26-33`

### `load_per_task(candidate_dir)`
**File:** `meta_agent/cli.py:36-51`

### `cmd_list(args)`
**File:** `meta_agent/cli.py:54-87`

### `cmd_show(args)`
**File:** `meta_agent/cli.py:90-104`

### `cmd_diff(args)`
**File:** `meta_agent/cli.py:107-166`

### `cmd_pareto(args)`
**File:** `meta_agent/cli.py:169-225`

### `cmd_failures(args)`
**File:** `meta_agent/cli.py:228-260`

These methods are the query API over the experience store.

## Outer loop

### `_run_claude_cli(prompt, system_append, label, trace_path=None, max_turns=50, model=None) -> int`
**File:** `meta_agent/outer_loop.py:57-136`

Shells out to Claude CLI, streams JSON events, records proposer traces, and prints summarized progress.

### `invoke_proposer(staging_dir, experience_dir, bench_name, trace_path=None, model=None) -> bool`
**File:** `meta_agent/outer_loop.py:139-186`

Stages the next iteration, prompts the proposer, and checks whether it wrote `config.py`.

### `_load_skill_history()` / `_save_skill_history(...)`
**File:** `meta_agent/outer_loop.py:260-275`

Manage version history for the evolving proposer skill.

### `_backup_skill(version: int) -> Path`
**File:** `meta_agent/outer_loop.py:278-284`

Archives the current `SKILL.md` into the experience skill history.

### `validate_skill(skill_path: Path) -> bool`
**File:** `meta_agent/outer_loop.py:287-309`

Applies sanity checks before accepting an evolved skill.

### `invoke_skill_evolver(iterations_analyzed, staging_dir, experience_dir, model=None) -> bool`
**File:** `meta_agent/outer_loop.py:312-347`

Runs the meta-proposer that rewrites `SKILL.md` based on proposer behavior.

### `validate_config(config_path: Path, bench_type: str = "local") -> bool`
**File:** `meta_agent/outer_loop.py:349-399`

Validates importability and return type of a proposed config before evaluating it.

### `run_evaluation(...) -> Optional[dict[str, Any]]`
**File:** `meta_agent/outer_loop.py:402-435`

Calls `eval_runner` as a subprocess and loads `scores.json`.

### `main()`
**File:** `meta_agent/outer_loop.py:438-606`

Top-level orchestration for the whole optimization loop.

## Config strategy methods

### `build_options(ctx: RunContext) -> ClaudeAgentOptions`
**Files:**
- `configs/vanilla.py:14-25`
- `configs/bootstrap.py:25-39`
- `configs/hooks.py:105-126`
- `benchmarks/tau3/tau_vanilla.py:6-16`

This is the main extension seam in the entire repo.

## Hook methods

### `detect_bash_loops(...)`
**File:** `configs/hooks.py:18-60`

Injects context when repeated Bash failures or repeated commands indicate a loop.

### `track_bash_result(...)`
**File:** `configs/hooks.py:63-81`

Stores recent Bash command outcomes for loop detection.

### `force_verification_on_stop(...)`
**File:** `configs/hooks.py:84-102`

Rejects the first stop attempt and forces verification guidance.

## Tau adapter methods

### `build_mcp_tools(env, user, state)`
**File:** `benchmarks/tau3/sdk_adapter.py:38-125`

Creates the benchmark tool surface used by the runtime.

### `_make_tool_handler(name, desc, schema)`
**File:** `benchmarks/tau3/sdk_adapter.py:75-117`

Generates wrapped tau tools that preserve trajectory ordering and structured logging.

### `_parse_verdict(text: str) -> bool`
**File:** `benchmarks/tau3/sdk_adapter.py:160-163`

Parses judge output into correctness.

### `_judge_tau_task(...) -> TauJudgeResult`
**File:** `benchmarks/tau3/sdk_adapter.py:171-219`

Runs the external judge against policy, conversation, and tool-call summaries.

### `_judge_tau_self(user_content: str, model: str) -> TauJudgeResult`
**File:** `benchmarks/tau3/sdk_adapter.py:222-239`

Runs a same-family Claude-via-Bedrock judge.

## Practical extension guidance
If modifying the source system, start with these methods first:
1. `build_options(...)`
2. `run_task(...)`
3. `build_experience_dir(...)`
4. `invoke_proposer(...)`
5. `validate_config(...)`
6. `build_mcp_tools(...)`
