# Acceptance and handoff checklist

## Automated checks

- typecheck/lint/build pass;
- content/schema and link checks pass;
- MCP harness covers initialize, tools/list, list/read, notifications, malformed envelopes, unsupported protocol, auth, scope, validation, limits, and request correlation;
- adversarial checks cover revocation replay, CAS conflicts, unsafe URLs, empty-section protection, and block limits;
- revoke races cover both a slow read result and a slow mutation commit;
- project/tenant and agent-connection binding is tested for every capability;
- context/observation expiry, bounds, covered-record IDs, cursor continuation, and document-clock staleness are tested;
- production mode refuses missing feature flag, missing durable storage, and missing canonical origin where required.

## Hosted smoke matrix

| Case | Expected result |
|---|---|
| no auth with gate off | structured disabled `404` |
| no auth with gate on | `401 PERMISSION_DENIED` |
| read token + list/read | success |
| read token + update | `403`/scope denial |
| read/write token + fresh revision | branch/PR or reviewable change |
| stale revision | `409 CONFLICT`, no overwrite |
| revoked/expired token | `401` |
| unknown section/path | `404`, no path disclosure |
| malformed block/body | `400`/`VALIDATION_ERROR` |
| browser cross-origin mutation | `403` |
| upstream unavailable | `502 DEPENDENCY_FAILURE` |
| revoke during slow read | authentication failure, no usable result |
| revoke during slow mutation | no post-revoke commit |
| cross-project/connection capability | capability denial |
| changed revision during continuation | stale-capability denial |

## Agent-facing handoff template

```text
You now have access to <project> MCP.

Endpoint: <canonical MCP URL>
Protocol: <version(s)> over Streamable HTTP
Secret: configure the human-issued scoped bearer token in your connector secret store; do not echo or commit it.
Scopes: <content:read[, content:write]>
Expiry: <timestamp>

Start with initialize, tools/list, content_list_sections, and content_get_section.
For changes use: discover → read → explain diff → human confirmation → update with the exact fresh baseSha/revision → report commit/PR evidence.
Writes never auto-publish to the default branch. On CONFLICT, read again and rebase; never retry stale payloads. Do not edit arbitrary paths or bypass source-audit/review holds.
Revoke the token in <human token-management URL> if exposed.
```
