# Implementation Guide — building a meta-agent-style harness optimizer

## Step 1: define one narrow harness-config contract
Use a single strategy seam like:
- `build_options(ctx) -> ClaudeAgentOptions`

This keeps experiments replaceable and easy to validate.

## Step 2: store optimizer memory as artifacts
Persist:
- config source,
- traces,
- per-task outcomes,
- scores,
- human-readable summaries.

This turns the optimizer into a system with inspectable memory.

## Step 3: separate proposer, validator, and evaluator
Do not let the proposer directly mutate live runtime state.
Make it write a staged artifact, then validate, then evaluate.

## Step 4: make the same experience store readable by both humans and agents
Expose it through a CLI or tool layer so the proposer and the operator reason over the same evidence.

## Step 5: prefer one harness mutation at a time
Small deltas make it possible to understand what helped and what regressed.

## Step 6: keep a protected holdout
Search traces are not enough. Maintain a separate holdout to catch overfitting.

## Step 7: capture four categories separately
When productizing this pattern, store and reason about these separately:
- scripts / executable entrypoints,
- tool calls and tool surfaces,
- methods and contracts,
- prompts and hook-injected guidance.

This skill is organized around exactly those four categories because collapsing them makes future maintenance weaker.
