---
name: agent-swarm
description: Run a supervised local fleet of Codex CLI or Claude CLI workers from a reviewed JSON manifest. Use for parallel research, implementation lanes, dependency-ordered work, provider-diverse analysis, or an independent review pass that needs explicit ownership, approvals, bounded concurrency, timeouts, and persisted evidence.
---

# Agent Swarm

Use `scripts/swarm.py` as the single orchestration interface. Keep the
coordinator responsible for decomposition, authority, integration, and final
verification; workers own only the prompts and paths declared in the manifest.

## Workflow

1. Copy `assets/example-manifest.json` and make every packet self-contained.
   Give each packet a unique ID, owner, provider, timeout, approval state, and
   optional `depends_on` list. Keep mutable write paths disjoint.
2. Validate and inspect the exact provider commands without launching workers:

   ```powershell
   python path/to/agent-swarm/scripts/swarm.py validate --manifest swarm.json
   python path/to/agent-swarm/scripts/swarm.py run --manifest swarm.json --dry-run
   ```

3. Set `approved: true` only after reviewing each prompt, working directory,
   provider arguments, and authority. Run into a new output directory:

   ```powershell
   python path/to/agent-swarm/scripts/swarm.py run --manifest swarm.json --output-dir results/run-001
   ```

4. Read `summary.json` and each packet result. Record accepted, rejected,
   conflicting, and unresolved findings. A dependent packet runs only after
   every prerequisite succeeds; otherwise it is persisted as `blocked` without
   launching its CLI.
5. Reserve a final read-only packet for independent verification after the
   implementation surface is frozen.

## Manifest controls

- `max_workers` bounds concurrency.
- `provider_args` supplies shared Codex or Claude arguments before packet-local
  `args`.
- `capture_max_bytes` bounds retained stdout and stderr while preserving each
  stream's original byte count, truncation flag, and SHA-256 digest.
- `executables` overrides provider commands when they are outside `PATH`.
- `depends_on` defines a validated acyclic dependency graph.

Real runs preflight every used provider before launching any packet. Dry-runs
do not require installed providers. Results are committed as a fresh directory;
the runner refuses to overwrite an existing result directory.

Treat `cleanup_unconfirmed` as an unsafe workspace state: stop new mutation
work and inspect surviving worker processes before resuming.

## Authority boundary

This skill does not grant permission to mutate Git, CI, production, external
services, credentials, or a GUI application. It does not provide shared live
memory, retries, remote workers, automatic synthesis, or sandboxing beyond the
flags passed to each provider CLI. Apply the host repository's normal rules and
approval gates to every worker.

Run the bundled self-tests after changing the runner:

```powershell
python path/to/agent-swarm/scripts/test_swarm.py
```
