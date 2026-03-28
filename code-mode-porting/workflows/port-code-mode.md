<required_reading>
Read these first:
- `../references/portable-core.md`
- `../references/vesper-specific-adaptations.md`
- `../references/implementation-playbook.md`
- `../references/validation-checklist.md`
</required_reading>

# Port Code Mode

Use this workflow when implementing a Vesper-derived code-mode architecture in another agent app.

## Start Here

Before coding:

1. Name the target app and runtime boundary.
2. Name the current overloaded tool families.
3. Separate direct-only tools from bundled candidates.
4. Pick the gateway transport.

## Workflow

1. Write the bundled-vs-direct classification rules.
2. Define the runtime tool descriptor shape.
3. Implement pack-aware catalog helpers.
4. Implement the host dispatcher.
5. Implement the worker sandbox.
6. Add whole-block timeout and partial-result tracking.
7. Add gateway-boundary permission checks.
8. Shape prompt instructions for the target model/runtime families.
9. Preserve backward compatibility when code mode is off.
10. Run the validation checklist before trimming the direct surface.

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
