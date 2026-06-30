# Implementation GOAL document pattern

Use this when a user wants a short `/goal` prompt for a long coding task.

## Pattern

1. Create a standalone `*_GOAL.md` next to the plan/spec.
2. Keep the chat prompt short: `/goal Read and execute <path/to/GOAL.md>`.
3. The GOAL document should point to the longer implementation plan but not duplicate every design detail.
4. Include hard scope boundaries near the top so autonomous execution does not overbuild.
5. Include required pre-code inventory/contract work when the implementation could duplicate existing systems or cross architectural boundaries.
6. Include finalization gates, especially focused tests/build checks and a named strict review skill when the user requests one.

## Useful structure

- Objective
- Critical context
- Required starting point / source docs
- Hard scope boundaries: in scope and out of scope
- Required pre-code deliverables
- Implementation guidance
- Exit criteria
- Measurement and evidence
- Code quality guardrails
- Progress tracking
- Finalization

## Review-gate example

If the user asks for a harsh maintainability gate, explicitly include:

```markdown
After code implementation is done, invoke:

`$thermo-nuclear-code-quality-review`

Use it as a hard review gate before declaring completion. Fix blockers where reasonable, then re-run focused checks.
```

## Pitfall

Do not let a GOAL document turn a narrow V1 prototype into a broad framework build. Put anti-scope-creep rules in the GOAL itself, not only in the parent plan.