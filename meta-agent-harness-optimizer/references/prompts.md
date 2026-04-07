# Prompts — canvas-org/meta-agent

This file captures the **prompts and prompt-bearing artifacts** that shape optimizer behavior.

## 1) Proposer prompt constructed by outer loop
**Implementation:** `meta_agent/outer_loop.py:156-166`

The outer loop builds this prompt structure:
- read `SKILL.md` first,
- optimize for a named benchmark,
- inspect the benchmark's experience store,
- use `meta_agent.cli` commands to rank or inspect candidates,
- diagnose failures in the current best candidate,
- write an improved `config.py` to the staging directory.

This is the bridge between artifact memory and harness mutation.

### Why it matters
This prompt makes the proposer an **artifact reader + config writer**, not a task solver.

## 2) System append for proposer
**Implementation:** `meta_agent/outer_loop.py:166-174`

The proposer run appends:
- `Read {SKILL_PATH} for your full instructions.`

This means the real behavioral logic is split between:
- a short orchestration prompt,
- and the bundled `SKILL.md` guidance.

## 3) Bundled proposer skill (`meta-agent` source repo `SKILL.md`)
**File:** source repo root `SKILL.md:1-121`

This is one of the most important prompt artifacts in the repo.

### Core prompt responsibilities
It tells the proposer to:
- optimize the harness rather than solving tasks,
- inspect scores and failed traces,
- choose one targeted change,
- prefer cheaper levers first,
- perform a generalization check,
- avoid task-specific hardcoding,
- preserve prior good ideas unless evidence says otherwise.

### Most important prompt structures captured there
- **change hierarchy** (`SKILL.md:19-39`)
- **diagnostic questions before writing** (`SKILL.md:40-52`)
- **abstraction/generalization test** (`SKILL.md:53-58`)
- **hook/tool/subagent reference patterns** (`SKILL.md:59-114`)
- **experience-store reading instructions** (`SKILL.md:115-121`)

## 4) Skill evolver prompt template
**Implementation:** `meta_agent/outer_loop.py:189-258`

This prompt tells a second-order optimizer to improve the proposer `SKILL.md` itself.

### Key sections in that prompt
- analyze proposer behavior over recent iterations,
- compare behavior against outcomes,
- identify repeated failures, missed signals, bundled changes, successful patterns, stagnation,
- make targeted edits only,
- avoid task-specific guidance,
- write both an updated `SKILL.md` and `skill_evolution_notes.md`.

### Why it matters
This is the repo's explicit **meta-prompting loop**. It optimizes the optimizer's instruction layer.

## 5) Bootstrap prompt append
**Implementation:** `configs/bootstrap.py:13-22`

`BOOTSTRAP_PROMPT` tells the runtime agent to spend its first turn understanding the environment by checking:
- files/directories,
- installed tools/languages,
- package managers,
- memory availability,
- README/instruction files.

### Why it matters
This is a good example of a cheap but reusable harness mutation: add one targeted prompt append rather than redesigning the system.

## 6) Stop-hook reason text
**Implementation:** `configs/hooks.py:90-99`

The stop hook injects a verification-oriented reason telling the agent to:
1. run tests if they exist,
2. check compile/run correctness,
3. verify output against the request,
4. only stop after confirmation.

This is not a traditional system prompt, but it is still a prompt artifact because it shapes model behavior through lifecycle interception.

## 7) Warning text injected by Bash-loop hook
**Implementation:** `configs/hooks.py:33-58`

Two warning prompts are injected via `additionalContext`:
- stop and reconsider after repeated failing Bash commands,
- avoid repeating the same command when stuck.

These are hook-time prompt fragments.

## Prompt design lessons from the repo
**Evidence:** `WRITEUP.md:84-116`

The writeup states:
- the proposer prompt matters a lot,
- overfitting is common,
- better abstraction guidance improved outcomes,
- moving business rules into a skill worked better than just inflating the root prompt.

## How to capture prompts when porting this system
Preserve prompt logic in four buckets:
1. **outer orchestration prompt**
2. **bundled skill guidance**
3. **config-level prompt appends**
4. **hook-injected context fragments**

If porting to Vesper, keep those layers separate so each can be iterated independently.
