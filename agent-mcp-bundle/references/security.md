# Security and human-oversight reference

## Credential separation

Keep four identities separate:

1. site-view password/session;
2. human CMS edit password/session;
3. server-side Git/database/deployment credential;
4. short-lived, scoped agent capability token.

The agent must receive only (4). Store only a hash plus non-secret metadata in the registry. Return plaintext exactly once. Bound expiry, support idempotent revocation, and record issuer identity/capability ID and last use. Reject malformed scope records instead of defaulting them to wildcard access.

## Human token administration

Require an authenticated human edit session for issue/list/revoke. Require same-origin checks for every administration request and CSRF proof for mutations. Never return `EDIT_PASSWORD`, repository tokens, or token plaintext to browser JavaScript. If a reverse proxy changes origins, configure one canonical public origin and validate `Origin`/`Referer` conservatively.

## Browser MCP

Treat browser MCP as a backend-for-frontend, not a second agent identity. A same-origin session bootstrap may issue:

- an HttpOnly, Secure-in-production, `SameSite=Lax` session cookie scoped to the MCP route;
- a separate non-HttpOnly CSRF cookie/token;
- short absolute and idle expiries.

Mutating browser calls require same-origin and CSRF proof. Native/server-to-server clients continue to use bearer tokens. Never put bearer tokens in localStorage, source bundles, URLs, or article content.

## Threat controls

- Fail closed when production flags or durable storage credentials are absent.
- Rate-limit by token/capability and bound concurrent work.
- Limit body bytes, block count, string lengths, upstream time, and response size.
- Reject unsafe external URLs if media blocks can be edited.
- Redact secrets from logs and error hints.
- Use idempotency keys for retryable writes.
- Keep source-audit holds immutable from ordinary content writes.
- Rotate any secret that appeared in chat, CI output, screenshots, or an unintended log.

## Revocation correctness

Revocation is a lifecycle event, not merely a database flag. The revoke operation
must become visible before slow socket/room cleanup and must invalidate active
connections where applicable. Wrap slow reads and writes with a `whileActive`
equivalent:

```text
authenticate → slow operation → authenticate again → return only if same active connection
```

For mutations, serialize the final commit and revoke through a per-agent commit
gate (or transactional equivalent). Test that a revoke racing a blocked mutation
prevents both the result from being returned and the commit from landing after the
revoke point.

## Scoped capabilities

For interactive or multi-tenant products, a bearer token alone is not enough. A
context or observation capability should be short-lived and bound to the project,
agent connection, target page/collection, covered record IDs or bounds, and the
document revision observed. Reject missing, expired, cross-project, cross-connection,
out-of-bounds, or stale capabilities before mutation. Bound observations with cursors,
page sizes, property truncation, and an explicit stable revision.
