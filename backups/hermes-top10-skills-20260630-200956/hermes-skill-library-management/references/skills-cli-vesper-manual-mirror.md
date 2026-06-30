# `skills` CLI Cross-Agent Install: Vesper Manual Mirror

## When this applies

Use this note when importing an upstream skill package with `npx skills add ...` and the user asks for Codex/Codex CLI, Hermes, and Vesper global installation.

## Observed behavior

- `npx skills add <repo> --global --agent codex hermes-agent ...` can install/register a shared global package under `~/.agents/skills/<skill-name>` and copy to Hermes under `~/.hermes/skills/<skill-name>`.
- The current `skills` CLI agent list includes `codex` and `hermes-agent` but rejects `vesper` as an invalid `--agent`.
- Depending on the target agent's own loader, Codex CLI may also need a physical copy under `~/.codex/skills/<skill-name>` even when the `skills` CLI global registry says the package is available to Codex from `~/.agents/skills/<skill-name>`.

## Durable install pattern

1. Install via the CLI for the agents it supports:
   ```bash
   npx --yes skills add <owner>/<repo> \
     --skill <skill-name> \
     --global \
     --agent codex hermes-agent \
     --copy \
     --yes
   ```
2. Use the shared installed package as the source:
   ```bash
   SRC="$HOME/.agents/skills/<skill-name>"
   ```
3. Mirror it for Codex CLI and Vesper when requested:
   ```bash
   mkdir -p "$HOME/.codex/skills" "$HOME/.vesper/skills"
   rm -rf "$HOME/.codex/skills/<skill-name>" "$HOME/.vesper/skills/<skill-name>"
   cp -R "$SRC" "$HOME/.codex/skills/<skill-name>"
   cp -R "$SRC" "$HOME/.vesper/skills/<skill-name>"
   ```
4. Verify all requested roots have the same package files and hashes:
   ```bash
   for root in \
     "$HOME/.agents/skills/<skill-name>" \
     "$HOME/.codex/skills/<skill-name>" \
     "$HOME/.hermes/skills/<skill-name>" \
     "$HOME/.vesper/skills/<skill-name>"; do
     test -f "$root/SKILL.md" || exit 1
     find "$root" -maxdepth 2 -type f -printf '%P %s bytes\n' | sort
     sha256sum "$root/SKILL.md"
   done
   ```
5. For Hermes, verify through the actual loader with `skill_view(<skill-name>)` or `hermes skills list/inspect` rather than only checking files.

## Pitfall

Do not stop after `npx skills add ... --agent codex hermes-agent` if the user explicitly asked for Vesper. Treat the CLI's `Invalid agents: vesper` as a signal to manually mirror the already-audited package into `~/.vesper/skills/<skill-name>` and then verify parity.