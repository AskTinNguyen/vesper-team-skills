# Scripts and Executable Entry Points — canvas-org/meta-agent

This file captures the **operational command surface** of the source repo.

## Top-level commands from README
**Evidence:** `README.md:13-29`, `README.md:61-102`

### Install and baseline
```bash
git clone https://github.com/canvas-org/meta-agent
cd meta-agent
pip install -e .
cp .env.example .env
source .env
```

### Run a baseline evaluation
```bash
python -m meta_agent.eval_runner \
    --benchmark benchmarks/example/benchmark.yaml \
    --config configs/vanilla.py \
    --name baseline \
    --model claude-haiku-4-5
```

### Run the optimization loop
```bash
python -m meta_agent.outer_loop \
    --benchmark benchmarks/example/benchmark.yaml \
    --iterations 5 \
    --model claude-haiku-4-5
```

### Reproduce tau-bench results
```bash
pip install "tau2 @ git+https://github.com/sierra-research/tau2-bench.git"

python -m meta_agent.outer_loop \
    --benchmark benchmarks/tau3/benchmark.yaml \
    --holdout-benchmark benchmarks/tau3/benchmark_holdout.yaml \
    --iterations 10 \
    --model claude-haiku-4-5 \
    --proposer-model claude-opus-4-6
```

## Python module entrypoints

### 1) `python -m meta_agent.outer_loop`
**Implementation:** `meta_agent/outer_loop.py:438-606`

Purpose:
- orchestrate proposer → validate → evaluate → record history
- optionally run holdout evaluation
- optionally evolve `SKILL.md`

Important CLI flags:
- `--benchmark`
- `--iterations`
- `--model`
- `--proposer-model`
- `--baseline`
- `--holdout-benchmark`
- `--evolve-skill`
- `--skill-evolve-every`
- `--concurrency`

### 2) `python -m meta_agent.eval_runner`
**Implementation:** `meta_agent/eval_runner.py:181-248`

Purpose:
- run a config against local or tau benchmarks,
- persist the candidate directory,
- print pass/fail and cost summary.

Important CLI flags:
- `--benchmark`
- `--config`
- `--name`
- `--model`
- `--fast`
- `--tasks`
- `--concurrency`
- `--keep-workspaces`
- `--keep-failed`
- `--dry-run`

### 3) `python -m meta_agent.cli`
**Implementation:** `meta_agent/cli.py:54-260`

Purpose:
- query the experience store.

Observed subcommands:
- `list`
- `show <name>`
- `diff <name1> <name2>`
- `pareto`
- `failures <name>`

## Claude CLI invocation as an internal script surface
Although not a shell script file, `_run_claude_cli(...)` is effectively a generated execution script.

**Implementation:** `meta_agent/outer_loop.py:57-136`

It runs:
```text
claude --print --verbose --output-format stream-json \
  --append-system-prompt <...> \
  --allowedTools Read,Write,Edit,Bash,Glob,Grep \
  --max-turns <N> \
  -p <prompt>
```

Optional additions:
- `--model <model>`
- `--permission-mode <mode>`

## Source repo files that function like scripts
Even if not in `scripts/`, these files are operational entrypoints:
- `meta_agent/outer_loop.py`
- `meta_agent/eval_runner.py`
- `meta_agent/cli.py`
- `meta_agent/task_runner.py` (runtime worker path)
- `benchmarks/tau3/sdk_adapter.py` (tau execution adapter)

## Environment variables that affect execution
**Evidence:** `configs/vanilla.py:15-21`, `meta_agent/task_runner.py:130-133`, `meta_agent/outer_loop.py:69-77`, `README.md:8-11`

Captured vars:
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- `CLAUDE_PERMISSION_MODE`
- `CLAUDE_CODE_USE_BEDROCK`
- `BEDROCK_BEARER_TOKEN`
- `AWS_BEARER_TOKEN_BEDROCK`
- `BEDROCK_REGION`
- `AWS_REGION`

## Local helper scripts bundled with this skill
These are not from the source repo; they help maintain this skill's extracted capture:
- `scripts/refresh-from-local-clone.sh`
- `scripts/method-inventory.sh`
