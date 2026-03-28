<required_reading>
Read these first:
- `../references/portable-core.md`
- `../references/gateway-response-contract.md`
- `../references/vesper-specific-adaptations.md`
- `../references/validation-checklist.md`
- `./implementation-playbook.md`

Load this only if rollout checks fail:
- `../references/troubleshooting.md`
</required_reading>

# Port Code Mode

Use this workflow when implementing a Vesper-derived code-mode architecture in another agent app.

## Start Here

Before coding:

1. Name the target app and runtime boundary.
2. Name the current overloaded tool families.
3. Separate direct-only tools from bundled candidates.
4. Pick the gateway transport.

Do not start implementation until you can show:

- one tool-surface inventory
- one direct-vs-bundled classification table
- one chosen transport and isolation primitive
- one named permission boundary that already owns real side effects

## Workflow

1. Execute the phases in `workflows/implementation-playbook.md`.
2. For each phase, capture:
   - what artifact you produced
   - how you verified it
   - what fallback you will use if the phase is blocked
3. Adopt one concrete success payload and one timeout or partial-failure payload from `../references/gateway-response-contract.md`.
4. Run `../references/validation-checklist.md` before trimming the direct surface.
5. Load `../references/troubleshooting.md` immediately if validation exposes call-ID drift, policy regressions, timeout ambiguity, or sandbox leaks.

## Evidence To Collect

Do not call the port ready until you have:

- tool-surface inventory
- direct-vs-bundled classification table
- transport and isolation decision
- one success response example
- one timeout or partial-failure response example
- permission-mode matrix
- code mode on/off registration matrix
- validation checklist results

## Decision Gates

Stop and re-evaluate if any of these happen:

1. You are copying Vesper product nouns into another app.
2. The worker can directly access privileged resources.
3. The gateway can mutate state in safe/read-only mode without inspection.
4. Failure output does not tell the agent what may already have persisted.
5. You are trimming the direct surface before catalog discovery is usable.

## Done Criteria

The port is ready when:

1. one primary workspace gateway exists
2. common discovery is lightweight and reliable
3. host-side privilege ownership is preserved
4. retry safety is explicit
5. policy still holds through the bundled path
6. model-specific prompt shaping is intentional
7. the validation checklist passes
8. response payloads show completed and in-flight call handling
9. the direct-vs-bundled split is documented in code and docs
