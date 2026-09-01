# MCP contract profile

Use this reference when implementing or reviewing the wire contract. Adapt names to the target app, but keep the safety semantics.

## HTTP profile

- `POST /api/mcp` (or the project’s canonical route).
- Required request headers: `Authorization: Bearer <scoped-agent-token>`, `Content-Type: application/json`, and `Accept: application/json, text/event-stream`.
- JSON-RPC 2.0 envelope with request IDs. Notifications may return an empty success response.
- Advertise a current MCP protocol version and one compatibility version. Reject unsupported versions clearly.
- If the server has no server-initiated SSE stream, `GET` should return `405`, not pretend to be a stream.
- Return `x-request-id` on transport-level errors and include the same correlation value in structured logs.

## Baseline tools

### `content_list_sections`

Optional identity filter (for example `chapter`). Return only manifest/index-backed identities and source paths or safe metadata. Do not reveal arbitrary filesystem paths or secrets.

### `content_get_section`

Required canonical identity fields (for example `chapter`, `section`). Return the complete current content payload, its `baseSha`/revision, effective status, and any source-audit hold as separate fields.

### `content_update_section`

Required: identity, complete validated payload, truthful `author`, and fresh `baseSha`/revision in durable/Git mode. Optional: `note`, idempotency key. Compare the revision immediately before persistence. Return commit/revision and branch/PR/change evidence; never auto-merge.

## Error taxonomy

Use stable application codes inside JSON-RPC errors:

`VALIDATION_ERROR`, `NOT_FOUND`, `PERMISSION_DENIED`, `CONFLICT`, `DEPENDENCY_FAILURE`, `RATE_LIMITED`, and `INTERNAL_ERROR`.

Include a bounded operator hint, never a stack trace or secret. Distinguish these cases operationally:

| Response | Meaning |
|---|---|
| `404 NOT_FOUND` with “disabled” | feature gate is off or route is intentionally dark |
| `401 PERMISSION_DENIED` | no valid agent token/session |
| `403 PERMISSION_DENIED` | identity exists but lacks required scope/CSRF/origin proof |
| `409 CONFLICT` | supplied revision is stale |
| `502 DEPENDENCY_FAILURE` | Git/database/upstream persistence unavailable |

## Optional additive capabilities

Review, evidence, authority, decision, and canon-proposal tools may be added only as explicit capability profiles with separate scopes and schemas. Keep `effectiveStatus`, `sourceAuditHold`, review records, promotion claims, and freshness distinct. Append-only evidence/review writes must bind to the reviewed content revision/hash and remain human-reviewable.
