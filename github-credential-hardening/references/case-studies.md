# Case Studies

## 001: GitHub Credential Leakage Surfaces In Vesper (2026-02-12)

Source documentation:
- `docs/solutions/security-issues/github-credential-leakage-surfaces-vesper-20260212.md`

### Symptoms

- Team Skills repo URL accepted credential-bearing URLs and could persist/log the raw input.
- MCP stdio validation spawned subprocesses with inherited unfiltered `process.env`.
- GitHub OAuth flow included an IPC path that could return `accessToken` data to renderer.

### High-Priority Fixes

1. Sanitize GitHub URLs before persistence and logging.
2. Apply shared sensitive-env filtering to validation and runtime subprocess paths.
3. Keep token lifecycle in privileged process boundaries and return status metadata only.
4. Redact token-like strings in logs and add regression tests around redaction.

### Key Files

- `apps/electron/src/main/ipc.ts`
- `packages/shared/src/mcp/validation.ts`
- `packages/shared/src/mcp/client.ts`
- `packages/shared/src/github/oauth.ts`
- `packages/shared/src/agent/session-scoped-tools.ts`

Use this case study as the baseline checklist for future GitHub integration changes.
