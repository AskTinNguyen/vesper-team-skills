---
name: code-optimization-agent-skills
description: "Use for an end-to-end evidence loop for performance optimization: read project context, profile realistic workloads, optimize measured hotspots, verify correctness/performance, and repeat bounded passes."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [optimization, profiling, performance, codex, agents, workflow]
    related_skills: [profiling-software-performance, extreme-software-optimization, repeatedly-apply-skill]
    source: "https://x.com/doodlestein/status/2059715849196564726"
    source_site: "https://jeffreys-skills.md/"
    note: "Clean-room Hermes-compatible workflow extracted from public post and public landing/docs pages; not a copy of paid skill content."
---

# Code Optimization Agent Skills

## Overview

This is the global entrypoint for the code-optimization setup described in Jeffrey Emanuel's X post: combine project-context reading, performance profiling, extreme optimization, and repeated skill application.

The public post names three cooperating skills:

- `profiling-software-performance` — establish real-world performance baselines and identify hotspots.
- `extreme-software-optimization` — optimize only measured bottlenecks while proving behavior is preserved.
- `repeatedly-apply-skill` — run the optimization skill in repeated, bounded passes against the critical items uncovered by profiling.

This Hermes skill installs that setup as a callable workflow. It is a clean-room implementation based on public descriptions, not a mirror of proprietary/premium skill text.

The leading word is **evidence loop**: profile realistic work, optimize only measured hotspots, verify correctness and speed, then repeat within a bounded budget. This skill is the router/orchestrator; detailed profiling, optimization, and repetition rules belong to the component skills.

## Evidence loop gates

1. **Context gate** — applicable project instructions, README, build/test commands, and benchmark entry points are identified.
2. **Baseline gate** — realistic workload, command, environment, metric, and raw baseline numbers are recorded.
3. **Pass gate** — each optimization maps to one hotspot, preserves correctness, and reports before/after delta with noise/confidence.
4. **Stop gate** — stop when gains flatten, risk rises, verification is unavailable, the backlog is empty, or the pass budget is exhausted.

## When to Use

Use when the user says things like:

- "Optimize this codebase using the Jeffrey / doodlestein setup"
- "Apply the Code Optimization agent skills"
- "Find performance hotspots and optimize them scientifically"
- "Use profiling + extreme optimization repeatedly"
- "Make this faster without changing behavior"

Don't use for:

- Cosmetic refactors with no performance goal.
- Guesswork optimization without a benchmarkable workload.
- Security audits, unless performance is the primary question.

## Invocation Prompt

When invoked in a repository, follow this exact shape unless the user provides a narrower target:

```text
First read ALL of the AGENTS.md file and README.md file super carefully and understand ALL of both. Then investigate the codebase to understand the code, technical architecture, and purpose of the project. Now apply profiling-software-performance so we can understand the performance hotspots under realistic usage. Then start optimizing the highest-impact proven hotspots using extreme-software-optimization. Keep repeatedly applying, using repeatedly-apply-skill, the extreme-software-optimization skill systematically to focus on the critical items uncovered in the profiling.
```

After any optimization changes, apply this adversarial review goal before finalizing:

```text
/goal Perform an adversarial review of the changes in this branch. Look for opportunities to reduce layers, remove complexity, and increase reliability. Ensure repo-wide policies are maintained, changes are verified, and maintain the original intent.
```

Treat this as a review lens, not permission to make broad rewrites. It should challenge unnecessary abstraction, layering, special cases, fragile cleverness, and policy drift introduced during optimization while preserving the measured performance goal.

## Workflow

1. **Load the component skills**
   - Load `profiling-software-performance`.
   - Load `extreme-software-optimization`.
   - Load `repeatedly-apply-skill`.

2. **Read project contract and context first**
   - Read every `AGENTS.md` or similar agent instruction file that applies to the repo/subtree.
   - Read `README.md` and any quickstart/developer docs it points to.
   - Inspect package/build/test config before running commands.
   - Identify the runtime, benchmark, and test commands already present.

3. **Build a codebase model**
   - Determine the product purpose and main user-facing flows.
   - Map the architecture: entrypoints, hot request paths, storage, IO, concurrency, caches, serialization, and external services.
   - Identify what "real-world usage" means for this project.

4. **Profile before optimizing**
   - Establish correctness tests and baseline performance.
   - Use realistic workloads.
   - Record latency/throughput/resource metrics.
   - Find measured hotspots, not suspected hotspots.

5. **Optimize scientifically**
   - Choose the top measured bottleneck.
   - Preserve behavior with tests/golden outputs/invariants.
   - Make one focused change at a time.
   - Re-run correctness checks and benchmarks.
   - Keep only changes with demonstrated improvement and no regression.

6. **Repeat bounded passes**
   - Apply the optimization loop repeatedly to remaining high-value hotspots.
   - Stop when improvements flatten, risk exceeds reward, tests fail, or budget/time is exhausted.

## Output Standard

At completion, report:

- Context read: files/instructions consulted.
- Baseline: workload, command, environment, and measured numbers.
- Hotspots: ranked list with evidence.
- Changes made: each change mapped to a hotspot and rationale.
- Verification: tests/golden comparisons/invariants run.
- Performance delta: before/after numbers and percent change.
- Remaining opportunities: next hotspots and risk notes.

## Safety Rules

- Never optimize before a baseline exists.
- Never accept an optimization without correctness verification.
- Never bundle unrelated changes into the same pass.
- Never claim a speedup without measured before/after evidence.
- If benchmarking is impossible in the environment, say so and create a profiling/benchmark harness first.

## Common Pitfalls

1. **Reading only a slice of instructions.** The public setup explicitly begins by reading all applicable `AGENTS.md` and `README.md` content.
2. **Benchmarking toy paths.** Real-world usage must resemble how the project is actually used.
3. **Optimizing guessed slow code.** Use profiler data to rank work.
4. **Skipping isomorphism checks.** Behavior preservation matters as much as speed.
5. **Stopping after one pass when more hotspots remain.** Use `repeatedly-apply-skill` with a clear stop condition.

## Verification Checklist

- [ ] Applicable project instructions and README were read.
- [ ] Architecture and purpose were summarized before changes.
- [ ] A realistic profiling workload was defined.
- [ ] Baseline metrics were recorded.
- [ ] Hotspots were evidence-ranked.
- [ ] Each optimization had correctness tests before/after.
- [ ] Each optimization had before/after performance data.
- [ ] Repeated passes stopped for an explicit reason.
