# Web Porting Guide

Use `../workflows/web.md` for sequence. This file defines web-specific constraints.

## Scope Notes

Examples in this file are framework-agnostic templates.
Keep one snapshot schema and one context builder shared across UI and backend send adapters.

## Security And Sanitizer Spec

Redact at capture-time and before send-time.

Required deny rules:
- input types: `password`, `hidden`
- attributes: `value`, `data-secret`, `data-token`, `data-api-key`
- keys matching case-insensitive patterns:
  - `token`
  - `secret`
  - `password`
  - `api[_-]?key`
  - `authorization`

Content handling:
- redact secret-like substrings in text snippets
- strip query string key/value pairs for sensitive keys
- never serialize unrelated form values outside selected subtree

## Auth Adapter Modes

Choose one explicit mode and document it in implementation output.

| Mode | Required Headers/Credentials | Common Failure Mapping |
|---|---|---|
| Cookie + CSRF | `credentials: include` and CSRF header/token | invalid/missing CSRF -> `PERMISSION_BLOCKED` |
| Bearer token | `Authorization: Bearer <token>` | expired/invalid token -> `PERMISSION_BLOCKED` |
| Server proxy | no browser secret in client; proxy adds auth server-side | upstream auth/network failures -> `SEND_FAILED` |

`AUTH_MODE` resolution rules:
1. Default from app config.
2. Override by environment variable (for dev/staging).
3. Optional runtime toggle only in dev mode.
4. Reject unknown mode values at startup with an explicit configuration error.

## Capture Strategy

- default: metadata-only capture
- optional screenshot: allowed when feature flag enabled and caps enforced
- always cap payload sizes from `contracts.md` before model handoff

## Chat Adapter Contract

Request body fields:
- `message`
- `agentContextPrefix`
- `uiInspectorAttachment` (optional summary)

Adapter must include:
- auth headers/session credentials
- timeout and abort control
- explicit error classification to typed taxonomy codes

## Rollout And Safety

Rollout stages:
1. Internal dev only (100% feature-flagged).
2. Pilot team (10-20%).
3. Broader dev rollout (50%).
4. Full dev rollout (100%).

Rollback triggers:
- >2% send failure rate over 1h
- repeated redaction misses
- regression in chat pipeline latency SLO

Required kill switches:
- `uiInspectorEnabled`
- `uiInspectorScreenshotsEnabled`
- `uiInspectorSendToChatEnabled`

## Edge Cases To Handle

- Shadow DOM targets
- portals
- iframe boundaries
- detached nodes during capture
- zero-sized nodes
- rapidly animating layout transitions
- two active windows/tabs capturing concurrently
