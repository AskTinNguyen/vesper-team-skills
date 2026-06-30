# 2026-06-01 Hermes skill cleanup example

Context: the user asked to review the current Hermes skill list and disable skills not related to day-to-day work, explicitly naming `polymarket` as an example.

Observed state:

- `hermes skills list` reported 102 enabled, 0 disabled.
- `~/.hermes/config.yaml` had `skills.disabled` absent/empty.

Safe disable set chosen:

- `polymarket` — prediction market queries.
- `pokemon-player` — gaming/emulator automation.
- `openhue` — Philips Hue smart-home control.
- `godmode` — red-team/jailbreak prompts.

Implementation pattern:

1. Create a timestamped backup of `~/.hermes/config.yaml`.
2. YAML-load config, set or merge `skills.disabled` with the selected skill names.
3. Write config back with Unicode-safe YAML.
4. Verify with `hermes skills list | grep -E 'polymarket|pokemon-player|openhue|godmode'`.

Result:

- After cleanup: 98 enabled, 4 disabled.
- The final response listed the exact disabled skills, backup path, candidates for future review, and `/reset`/restart note.

Good next-review buckets from that session:

- Creative/media niche: `ascii-video`, `comfyui`, `manim-video`, `pixel-art`, `songwriting-and-ai-music`, `touchdesigner-mcp`, `heartmula`, `songsee`, `gif-search`.
- ML/MLOps niche: `weights-and-biases`, `llama-cpp`, `segment-anything-model`, `dspy`.
- Productivity integrations to keep only if actively used: `airtable`, `himalaya`, `obsidian`, `spotify`, `teams-meeting-pipeline`.
- Specialized upstream Codex workflows: `codex-upstream-*`, unless the user regularly works on upstream OpenAI Codex PRs/issues.
