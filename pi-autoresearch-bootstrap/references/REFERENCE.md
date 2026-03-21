# Pi Autoresearch Bootstrap Reference

Use this reference when setting up `pi-autoresearch` in a brand-new repository or in a fresh worktree of an existing repository.

## Purpose

Stand up a fresh `pi-autoresearch` workflow with:

- a safe experiment workspace
- a benchmark script
- a keep gate
- a durable session brief
- a copy-paste launch prompt

## Capability Expectations

If running inside Vesper with Pi plugin support, prefer this tooling shape:

- `pi.interview`
  - plugin id: `pi.interview`
  - use for structured intake and interactive question flow
  - rollout requirements: manager + extensions + interview rollout
- `visual-explainer`
  - plugin id: `visual-explainer`
  - use for the final setup summary and walkthrough
  - rollout requirements: manager + skillpacks rollout

Important:

- `pi.interview` is an extension-style plugin.
- `visual-explainer` is a skill/prompt pack in Vesper's catalog, not an executable extension tool.
- If either capability is unavailable, continue with a text-only fallback and say what is missing.

## Workflow

### Phase 1: Intake

Use `pi.interview` if available. Otherwise ask concise plain-text questions.

Collect the minimum inputs:

1. Repository absolute path or clone URL
2. Optimization goal
3. Primary metric name and whether lower or higher is better
4. The workload or command that should represent the benchmark
5. Which files or directories are in scope
6. Which files or directories are off-limits
7. Which correctness checks should gate `keep`
8. Whether full tests are known green on baseline
9. Whether a fresh worktree should be created before changes
10. Whether to use a local `pi-autoresearch` clone or install from GitHub

Do not proceed to file creation until these are answered or responsibly inferred.

### Phase 2: Repo Validation

Before writing anything:

1. Confirm the repository exists locally and is a git repo.
2. Check whether the working tree is already dirty.
3. If the repo is dirty or the user requests isolation, create a fresh worktree from local `main` or the repo's mainline branch.
4. Determine whether the proposed benchmark and checks can run on baseline before using them as gates.

If a proposed check is already red on baseline, do not use it as the keep gate. Document that explicitly and choose a narrower baseline-green gate instead.

### Phase 3: Pi Autoresearch Bootstrapping

Set up Pi using one of these methods:

- Preferred local mount:
  - create `.pi/settings.json`
  - mount the local `pi-autoresearch` path
- Alternative global install:
  - install from GitHub using Pi package install flow

Then create these files at the worktree or repo root:

- `autoresearch.md`
- `autoresearch.sh`
- `autoresearch.checks.sh`
- `autoresearch.config.json`
- `PI_AUTORESEARCH_LAUNCH.md`

Required `autoresearch.config.json` fields:

- `workingDir`
- `maxIterations`

Make `autoresearch.sh` and `autoresearch.checks.sh` executable.

### Phase 4: Author the Session Files

Write the files with this intent:

- `autoresearch.md`
  - objective
  - metric definitions
  - files in scope
  - off-limits paths
  - constraints
  - baseline numbers
  - first likely experiment candidates
- `autoresearch.sh`
  - small, deterministic benchmark
  - outputs `METRIC name=value` lines
- `autoresearch.checks.sh`
  - scope guard
  - blocked config guard where appropriate
  - only baseline-green checks
- `PI_AUTORESEARCH_LAUNCH.md`
  - exact `cd ... && pi` launch command
  - exact copy-paste `/autoresearch ...` prompt

Do not leave placeholders unresolved.

### Phase 5: Baseline Verification

Run the baseline locally before handoff:

1. `./autoresearch.sh`
2. `./autoresearch.checks.sh`

Record the actual metric output in `autoresearch.md`.

If checks fail:

- diagnose whether the failure is baseline pre-existing
- tighten or replace the keep gate if necessary
- rerun until the session is honestly launchable

Do not claim success without a passing baseline keep gate.

### Phase 6: Explanation and Handoff

If `visual-explainer` is available, use it to produce a concise explanation of:

- what the experiment is optimizing
- what files were created
- what the benchmark measures
- what the keep gate enforces
- what command to paste into Pi

If `visual-explainer` is unavailable, provide the same explanation in plain markdown.

The final handoff must include:

1. Exact worktree or repo path
2. Exact launch command
3. Exact `/autoresearch ...` prompt
4. Baseline metric values
5. Any known caveats, especially baseline-red tests excluded from the gate

## Decision Rules

- Prefer one experiment per worktree.
- Keep the benchmark narrow and hard to game.
- Never improve a metric by adding ignore rules or config suppressions unless the experiment explicitly targets configuration cleanup.
- If the user wants deletion work, require local reference tracing in addition to detector output.
- If the repo uses dynamic loading, registries, IPC names, or side-effect entrypoints, treat detector-reported unused code as suspicious until confirmed.
- When uncertain, choose the safer smaller first experiment.

## Expected Deliverables

By the end of setup, the repo or worktree should contain:

- `autoresearch.md`
- `autoresearch.sh`
- `autoresearch.checks.sh`
- `autoresearch.config.json`
- `PI_AUTORESEARCH_LAUNCH.md`
- `.pi/settings.json` if using a local package mount

And the agent should be able to state:

- the benchmark command works
- the keep gate passes on baseline
- the experiment can now be resumed by any fresh Pi session from the written files alone

## Fallback Prompt

Use this when the user wants a single short instruction:

```text
Use $pi-autoresearch-bootstrap to set up a fresh pi-autoresearch run in this repo. Start by interviewing me for the minimum inputs needed for the benchmark, keep gate, scope, and install method. If the Interview plugin is available, use it. If Visual Explainer is available, use it at the end to summarize the setup and launch plan. Create the session files, run the baseline benchmark and keep gate yourself, record the baseline metrics, and leave me with a copy-paste /autoresearch launch prompt.
```
