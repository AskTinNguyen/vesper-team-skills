# Reference implementation blueprint

This is the concrete shape to reproduce in a TypeScript/Next.js app. Rename modules to match the target project; do not copy paths blindly.

## tldraw reference adaptation notes

The reviewed reference lives at `/Users/tinnguyen/tldraw`, branch `develop`. The
following source modules informed this blueprint:

- `packages/backend/src/agent/mcp/mcp.plugin.ts` — route mounting, strict project
  ID/query checks, tool registration, stable error mapping, and the `whileActive`
  pre/post-authentication wrapper.
- `packages/backend/src/agent/mcp/mcp.auth.ts` — cookie rejection, bearer format
  validation before lookup, hashing, and project-scoped active-agent resolution.
- `packages/backend/src/access/access.plugin.ts` and `access.service.ts` — human
  provisioning, hash-only secret storage, active/revoked lifecycle, and one-time
  setup response.
- `packages/backend/src/agent/mcp/agent-mcp.types.ts` — explicit active-agent,
  context-scope, and context identity types with TTLs.
- `context-handoff.service.ts` — page/shape/bounds validation and short-lived
  browser-approved capabilities.
- `observation.service.ts` — bounded page reads, cursors, property truncation,
  asset metadata summaries, and document-clock continuation checks.
- `mutation.service.ts` and `mutation.schemas.ts` — centralized capability checks,
  in-bounds/covered-target enforcement, revision checks, and schema validation
  before commit.
- `tldraw-actions.ts` — domain record construction kept outside transport code.
- `packages/backend/src/app.ts` — composition-root dependency injection.
- `packages/backend/src/agent/agent-commit-gate.ts` — serialized revoke/commit
  ordering, with tests proving release after errors.
- The adjacent `*.test.ts` files — focused tests for auth, route behavior, revoke
  races, context expiry/binding, bounded observations, typed mutations, and the
  commit gate.

Adopt these invariants, not tldraw’s shape names or Elysia-specific syntax. A Wiki
usually needs manifest-backed article tools; a board, CRM, or internal app may need
page/record context and observation capabilities in addition to the baseline tools.

## Module seams

```text
src/app/api/mcp/route.ts              JSON-RPC transport + tool dispatch
src/app/api/mcp/session/route.ts      same-origin browser session adapter
src/app/api/cms/tokens/route.ts       human issue/list/revoke API
src/lib/cms/auth.ts                   human identity + bearer principal
src/lib/cms/scopes.ts                 canonical scope parser
src/lib/cms/tokens.ts                 hashed token registry + CAS persistence
src/lib/mcp/browser-session.ts        signed cookies, origin, CSRF, expiry
src/lib/cms/schema.ts                 canonical block/record validator
src/lib/cms/store.ts                  Git/database read + CAS write + PR
src/content/manifest.ts               allow-listed section identities
src/content/source-audit.ts           immutable hold/status lookup
```

The MCP route should depend on these seams rather than importing UI components or manipulating files directly. Tests should be able to replace the store and token registry with local fakes without changing the protocol contract.

For a project/tenant-scoped interactive app, add explicit seams for context handoff,
bounded observation, and the revoke/commit gate. The bearer principal should carry
the project ID and agent connection ID; a context or observation should carry the
target page/collection, covered IDs or bounds, expiry, and observed document clock.

## Request pipeline

```text
request
  → assign requestId
  → production feature gate
  → parse JSON-RPC envelope + protocol headers
  → authenticate bearer OR validated browser session
  → authorize required tool scope
  → acquire rate/concurrency budget
  → dispatch named tool
  → validate identity and complete payload
  → read current revision
  → compare baseSha/version immediately before write
  → persist branch/PR or reviewable change
  → release budget in finally
  → redact structured log + return evidence
```

Every early return must preserve the request ID and stable error taxonomy. Do not let an upstream exception escape as an HTML error page or stack trace.

For slow tools use a `whileActive` wrapper that authenticates before and after the
operation and compares the same connection ID. For writes, route the final persistence
through an agent commit gate that serializes revoke and commit decisions.

## Token record

Persist only a record like this (never plaintext):

```ts
type AgentTokenRecord = {
  id: string;
  name: string;
  prefix: string;            // e.g. nt_<8 hex chars>
  secretHash: string;        // SHA-256 or stronger keyed digest
  scopes: Array<"content:read" | "content:write" | string>;
  createdAt: string;
  createdBy: string;
  authorizedVia: "human-edit-session";
  expiresAt: string;
  revokedAt?: string;
  lastUsedAt?: string;
  metadata?: Record<string, string>;
};
```

Issue with cryptographically random bytes, return the secret exactly once, and persist with optimistic CAS when the registry is Git-backed. Registry mutations should retry a bounded number of times only after re-reading; never overwrite another issuer’s changes.

## Tool authorization map

```ts
const requiredScope = {
  content_list_sections: "content:read",
  content_get_section: "content:read",
  content_update_section: "content:write",
} as const;
```

Do not infer scopes from tool names supplied by the caller. Resolve the server-owned descriptor first, then enforce the mapped scope and input schema.

## Git publication pattern

For a write:

1. fetch the canonical file at the protected default branch;
2. require the caller’s `baseSha` and compare it to the fetched SHA;
3. derive a deterministic, sanitized agent branch from an idempotency key and section identity;
4. create/update that branch from the default branch;
5. commit the serialized complete payload with actor and note attribution;
6. create/update a PR targeting the protected default branch;
7. return `{ sha, branch, pullRequest, path, hold }` evidence.

If the fetched SHA changes at any point, return `CONFLICT`. If the Git provider fails, return `DEPENDENCY_FAILURE`. Do not fall back to local writes in hosted production.

## Browser session shape

`POST /api/mcp/session` is allowed only with an authenticated human edit cookie and same-origin request. On success, set an HttpOnly `nt-mcp` cookie and a separate CSRF token cookie. `GET` reports status only; `DELETE` requires same-origin plus CSRF and clears both. The browser session authorizes a human-mediated BFF call; it must not return or mint an agent bearer secret.

Keep browser-approved context handoff separate from remote bearer authentication. A
human may approve a page/bounds/shape scope through the browser route; the remote MCP
agent may only retrieve or mutate within a context/observation that is explicitly
bound to its own active connection.

## Minimum test fixtures

Include fixtures for:

- valid initialize/tools/list and notification envelopes;
- missing/expired/revoked token and insufficient scope;
- unknown manifest entry and malformed complete payload;
- stale SHA with unchanged source after rejection;
- Git/provider outage mapped to dependency failure;
- token plaintext absent from GET/list/log/error output;
- cross-origin and missing-CSRF browser mutations;
- rate/concurrency release after thrown errors;
- branch/PR evidence and idempotent repeated update;
- revoke racing a slow read returns an authentication failure and no usable result;
- revoke racing a mutation prevents a post-revoke commit;
- context/observation from another project or connection is rejected;
- expired or revision-stale capabilities are rejected;
- bounded observation continuation rejects a changed document clock.
