---
name: code-mode-porting
description: Use when implementing, porting, or reviewing a bundled code-mode workspace gateway for an agent app, especially when collapsing many CRUD or orchestration tools into one discovery-first execution bus with host-side policy and sandboxed execution.
---

# Code Mode Porting

Port Vesper's current code-mode architecture as a reusable pattern, not as a literal copy.

The goal is to give another agent app:

- one primary workspace gateway
- lightweight tool discovery
- host-owned side effects
- sandboxed execution
- clear policy and retry semantics

## When To Use

Use this skill when:

- designing a "code mode" or "workspace gateway" for another agent app
- collapsing a large CRUD tool surface into one primary execution bus
- replacing eager tool dumps with catalog-driven discovery
- deciding which tools should stay direct versus move behind a bundled gateway
- reviewing an existing agent app for prompt bloat, tool round-trip overhead, or unsafe bundled execution

## When Not To Use

Do not use this skill when:

- the app only needs a few direct tools and does not have prompt-surface pressure
- the real problem is provider auth, source mounting, or UI transport rather than workspace gateway design
- you need Vesper-specific product guidance more than a portable architecture

## Read In This Order

1. Portable core:
   `references/portable-core.md`
2. Vesper-derived seams to strip or replace:
   `references/vesper-specific-adaptations.md`
3. Step-by-step implementation path:
   `references/implementation-playbook.md`
4. Ship gate:
   `references/validation-checklist.md`
5. Execute the work:
   `workflows/port-code-mode.md`

## Core Rule

Preserve the architecture, not the nouns.

Keep these ideas:

- one workspace gateway
- discovery-first catalog
- host-side tool execution
- worker-side sandbox
- policy at the execution boundary
- provider-shaped prompt exposure

Replace these with your app's own concepts:

- tool families
- packs
- session/profile names
- server names
- product-specific orchestration flows

## Deliverable

A good result should be easy to summarize as:

- gateway transport:
- direct-vs-bundled classification rule:
- discovery model:
- sandbox boundary:
- host policy boundary:
- timeout and retry semantics:
- provider/model shaping:
- validation evidence:
