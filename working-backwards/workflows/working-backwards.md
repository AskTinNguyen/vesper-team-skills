# Working Backwards Workflow

Use this workflow to define success from the future, pressure-test the bet, and reverse-engineer the present-day plan.

## Phase -1: Preflight Setup

Collect these artifacts before writing strategy output:
- Decision owner
- User segment definition or best available proxy
- Current metrics baseline source
- Constraints source (technical, legal, org, timeline)
- Output destination (doc, issue, memo, planning artifact)

### Stakes Classification (Operational)

| Stakes | Use When | Typical Shape |
|--------|----------|---------------|
| Low | Narrow scope, easily reversible | 1 team or fewer, under 2 weeks, no trust/compliance risk |
| Medium | Cross-functional but manageable | 2-3 teams, 2-6 weeks, moderate user/process impact |
| High | Hard to reverse or high consequence | 4+ teams, over 6 weeks, trust/compliance/brand risk, strategic commitment |

### Mode Selection

| Mode | Default For | Target Duration | Required Bar |
|------|-------------|-----------------|--------------|
| Lite | Low stakes | 20-30 min | Brief but complete artifacts |
| Standard | Medium stakes | 45-90 min | Full workflow |
| Deep | High stakes | 2h+ | Full workflow + `workflow-review` |

**Gate: pass all**
- Decision owner is named.
- Stakes are recorded.
- Mode is recorded.
- Output destination is recorded.

## Recovery Protocol (Blocked Inputs)

Use this when required inputs are missing.

1. Ask at most **2 clarification rounds**.
2. After 2 rounds, choose one:
   - **Proceed with assumptions** only if stakes are Low/Medium and the decision owner accepts the risk.
   - **Pause and escalate** if stakes are High, trust/compliance risk exists, or the missing input changes the bet materially.
3. Record every unresolved item in the assumption log.

### Assumption Log

| Assumption | Why Needed | Evidence Source | Confidence | Owner | Next Validation Step |
|------------|------------|-----------------|------------|-------|----------------------|
| | | | High / Medium / Low | | |

## Phase 0: Prior Learnings and Context

- If stakes are **Medium/High** and no equivalent planning artifact exists, run `workflow-research` first.
- If equivalent research exists, reuse it instead of re-researching.
- At minimum, capture:
  - prior learnings source
  - current baseline metrics source
  - constraints source

**Gate: pass all**
- Medium/High stakes have a prior learnings source.
- Current baseline source is named.
- Constraint source is named.

## Phase 1: Frame the Bet

Write the bet in one line:

```text
Bet: If we build <feature>, then <target user> will achieve <outcome>, creating <business impact>.
```

**Gate: pass all**
- Names one feature bet.
- Names one primary target user.
- States one behavior or outcome change.
- States one business impact.

<required_reading>
Before Phase 2, read `references/intake-template.md`.
</required_reading>

## Phase 2: Clarify Success Inputs

Complete `references/intake-template.md`.

Rules:
- Fill all 5 required inputs.
- For each input, add an evidence source and confidence level.
- For High stakes, unresolved Low-confidence items require explicit decision-owner sign-off before proceeding.

**Gate**
- Intake template checklist passes.

## Phase 3: Define the Future Success Snapshot

Write a concrete future-state snapshot, usually 12-24 months ahead.

Include:
- what users do differently
- what became easier, faster, safer, or more trustworthy
- what metrics improved
- what did not regress

**Gate: pass all**
- Future date is explicit.
- Before/after is concrete.
- At least one measurable improvement is stated.
- At least one preserved guardrail is stated.

<required_reading>
Before Phase 4, read `references/press-release-template.md`.
</required_reading>

## Phase 4: Draft the Future Press Release

Complete `references/press-release-template.md` and pass its checklist before advancing.

<required_reading>
Before Phase 5, read `references/ultimate-ux-template.md`.
</required_reading>

## Phase 5: Design the Ultimate UX Narrative

Complete `references/ultimate-ux-template.md` and pass its checklist before advancing.

Rules:
- Set a **time-to-value target**.
- Default target is `P50 <= 5 minutes`.
- If that is unrealistic, write a justified replacement target.

<required_reading>
Before Phase 6, read `references/faq-template.md`.
</required_reading>

## Phase 6: Write the FAQ Backward from Risk

Complete `references/faq-template.md` and pass its checklist before advancing.

Rules:
- Answer at least 12 serious questions.
- Include at least 3 kill/stop questions.
- Record what changed in scope, sequencing, or policy after the FAQ.

<required_reading>
Before Phase 7, read `references/success-scorecard-template.md`.
</required_reading>

## Phase 7: Build the Success Scorecard

Complete `references/success-scorecard-template.md` and pass its checklist before advancing.

Rules:
- Every metric needs an owner.
- Every metric needs a baseline plan and cadence.
- Trust, quality, and cost guardrails are required.

<required_reading>
Before Phase 8, read `references/reverse-roadmap-template.md`.
</required_reading>

## Phase 8: Reverse Roadmap (Future -> Now)

Complete `references/reverse-roadmap-template.md` and pass its checklist before advancing.

Rules:
- Start at launch readiness, then step backward.
- Delay irreversible commitments until evidence exists.
- Add at least one fast experiment for each major unproven assumption.

<required_reading>
Before Phase 9, read `references/execution-handoff-template.md` and `references/decision-log-template.md`.
</required_reading>

## Phase 9: Verification, Recommendation, and Handoff

### Verification Checklist

For **Standard/Deep** mode, pass all before final recommendation:
- Every major assumption is tied to evidence or an experiment.
- Every scorecard metric has an owner and cadence.
- The FAQ produced at least one real change or explicit confirmation of scope.
- The execution handoff contains 3-7 concrete next actions.
- Go / adjust / stop thresholds are explicit.
- Recommended reviewers are named.

### Recommendation

Choose one outcome:
1. **Proceed now**
2. **Proceed with conditions**
3. **Do not proceed**

### Review Rule

- `workflow-review` is recommended for Standard mode.
- `workflow-review` is required for Deep mode before commitment.

### Execution Bridge

Complete `references/execution-handoff-template.md`.
Complete `references/decision-log-template.md`.

## Output Format

```markdown
# Working Backwards Plan: [Feature Name]

## Bet Statement
## Stakes and Mode
## Preflight Summary
## Assumptions and Evidence
## Future Success Snapshot ([Date])
## Future Press Release
## Ultimate UX Narrative
## FAQ (Backward Stress Test)
## Success Scorecard
## Reverse Roadmap
## Execution Handoff
## Recommendation
## Review Plan
## Open Questions
```

## Next Steps

- If approved, hand the `Execution Handoff` to `workflow-work`.
- After the decision or launch, store reusable learnings with `workflow-compound`.
