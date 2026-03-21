---
name: pi-autoresearch-bootstrap
description: Set up pi-autoresearch in a new repository or fresh worktree, including intake, package install or local mount, creation of `autoresearch.md`, `autoresearch.sh`, `autoresearch.checks.sh`, `autoresearch.config.json`, and `PI_AUTORESEARCH_LAUNCH.md`, baseline verification, and a copy-paste `/autoresearch` launch prompt. Use when the user asks to start pi-autoresearch from scratch, bootstrap an autoresearch run in a repo, create a new autoresearch starter pack, or use Interview and Visual Explainer to guide setup.
---

# Pi Autoresearch Bootstrap

Use this skill to bootstrap a fresh `pi-autoresearch` run that another Pi session can resume from files alone.

## Quick Start

1. Open [REFERENCE.md](./references/REFERENCE.md) and follow the phases in order.
2. Use `pi.interview` for intake when available. Otherwise ask only the minimum plain-text setup questions.
3. Prefer a fresh worktree when the repo is dirty or the user wants isolation.
4. Create the session files, make the scripts executable, and run the baseline locally before handoff.
5. Use `visual-explainer` for the final walkthrough when available. Otherwise provide the same explanation in markdown.

## Deliverables

Leave the repo or worktree with:

- `autoresearch.md`
- `autoresearch.sh`
- `autoresearch.checks.sh`
- `autoresearch.config.json`
- `PI_AUTORESEARCH_LAUNCH.md`
- `.pi/settings.json` when using a local package mount

## Guardrails

- Use only baseline-green checks as the keep gate.
- Do not leave placeholders unresolved.
- Do not claim the setup is ready until both `./autoresearch.sh` and `./autoresearch.checks.sh` have been run successfully.
- Document any caveats, especially baseline-red tests that were intentionally excluded from the gate.
- For deletion-oriented experiments, require local reference tracing in addition to detector output.

## Reference

Open [REFERENCE.md](./references/REFERENCE.md) for the full step-by-step setup procedure, capability expectations, decision rules, and fallback prompt.
