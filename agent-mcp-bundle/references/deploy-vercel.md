# Vercel/Next.js deployment playbook

Use this only when the target is a Vercel-hosted Next.js app. For another provider, keep the same sequence and substitute its secret manager/deploy commands.

## Preflight

Confirm the repository, production project, canonical alias, deployment branch, branch protection, and the commit intended for release. Run the app’s build, content checks, and MCP contract harness locally. Keep a clean diff or explicitly record unrelated work.

## Production variables

Configure names appropriate to the implementation:

```text
MCP_ENABLED=true
MCP_PUBLIC_ORIGIN=https://<canonical-production-host>
CMS_GITHUB_TOKEN=<server-side token>
EDIT_PASSWORD=<separate human CMS secret>
```

Do not print values while inspecting environment configuration. Prefer the Vercel dashboard or CLI secret input that does not echo plaintext. `MCP_AGENT_TOKEN` should not be a permanent broad project secret when the design has a token registry; issue per-agent tokens after deployment instead.

## Deploy and verify

Deploy the intended commit to production using the project’s normal Vercel workflow. Then verify the canonical alias:

1. `POST /api/mcp` without a token → `401` after the feature gate is enabled;
2. initialize/tools discovery with a scoped token;
3. list/read a known manifest entry;
4. invalid and stale write checks;
5. branch/PR evidence and no direct default-branch mutation;
6. token revoke/expiry replay check.

If the response remains `404` disabled, the deployment did not receive `MCP_ENABLED=true` or the request is hitting the wrong alias. If it is `401`, the route is active and the receiving harness lacks a valid token. Do not “fix” either by weakening auth or reusing `EDIT_PASSWORD`.

## Provider-neutral translation

- GitHub-backed content: use a server-side repository token, optimistic blob SHA, dedicated branch, and PR.
- Database-backed content: use a row version/ETag CAS, append an audit record, and create a review state rather than changing the published row directly.
- Static export: generate a reviewable artifact and require a human merge/release; do not write the build output as the source of truth.
