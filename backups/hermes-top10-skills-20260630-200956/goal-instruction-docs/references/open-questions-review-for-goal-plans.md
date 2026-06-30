# Open-question review pattern for GOAL-backed implementation plans

Use this reference when the user asks to save proposed phases, produce a concise `/goal` prompt, and resolve open questions with recommendations plus subagent critique.

## Pattern

1. Save the durable implementation phases in the existing implementation plan file, or create one under the project docs/plans area if none exists.
2. Create a standalone `*-goal.md` or `*_GOAL.md` next to the implementation plan when the `/goal` prompt would otherwise be long.
3. Keep the chat-facing `/goal` prompt short: it should point at the GOAL document and name the plan/spec files as source-of-truth references.
4. For open questions:
   - propose concrete defaults/recommendations first;
   - spawn a critique subagent with the plan/spec context and the draft recommendations;
   - ask the subagent for gaps, risks, better defaults, and an append-ready section;
   - append only the synthesized decisions, justifications, evidence, and follow-up gates to the plan.
5. Include the concise `/goal` prompt in the plan itself so future operators can copy it without searching the chat transcript.
6. Verify by reading back the updated plan and GOAL document before reporting completion.

## What to include in the appended open-question section

- The recommendation/default.
- Why it is recommended.
- Evidence from the plan/spec/current measurements.
- Acceptance additions or test gates.
- Any explicit deferrals and the criteria for revisiting them.

## Pitfalls

- Do not leave the open-question answers only in chat; append them to the durable plan.
- Do not make the `/goal` prompt carry all details; put details in the GOAL document and keep the prompt concise.
- Do not let a subagent critique replace controller synthesis; incorporate only the parts that strengthen the durable plan.
- Do not rewrite the whole plan if an append-only decision log is sufficient.
- Do not trust the current working directory when the user references a prior plan, checklist, quoted message, or project-specific feature. First identify the repo from the user's context and existing plan paths, then save/patch the plan there. If the context names S2 game systems, aerial enemy movement, Combat Movement Profiles, SipherAIScalableFramework, or `EnemyAI_AerialPseudo3DMovement_*`, the target repo is the S2 game repo (`E:/S2_`, git-bash `/e/S2_`), not whatever repo the agent session happened to start in.