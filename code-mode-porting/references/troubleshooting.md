# Troubleshooting

Load this only when rollout or validation checks fail.

| Symptom | Likely Cause | Where To Inspect | Safe Remediation | Stop Rollout When |
|---|---|---|---|---|
| Catalog search returns nothing useful | Pack assignment is wrong or descriptors are too thin | catalog builder, descriptor `pack` and `description` fields | fix descriptor grouping and descriptions before changing prompt wording | the model still cannot find core tools after an exact schema lookup |
| Results map to the wrong call ID | worker/host message correlation is unstable under concurrency | dispatcher message contract and completed/in-flight tracking | make call IDs explicit, deterministic, and round-tripped in every result | concurrent calls can still cross-wire results |
| Safe mode can mutate through the gateway | gateway policy is not reusing the existing permission seam | gateway boundary checks and mutation classification | block bundled mutations in safe mode and route through the existing approval path | any safe-mode mutation persists state |
| Safe mode blocks harmless discovery | discovery helpers are classified as mutations or the validator is too broad | permission matrix and gateway validator | downgrade discovery helpers to read-only and narrow the validator | the model cannot inspect schemas in safe mode |
| Timeout output gives no retry guidance | completed or in-flight calls are not captured before shutdown | timeout owner, worker termination path, response formatter | add completed/in-flight tracking and return explicit retry guidance | the agent cannot tell whether blind retry is safe |
| Worker can reach privileged APIs directly | sandbox is leaking environment, modules, or host objects | injected runtime surface and worker bootstrap | remove ambient globals and keep real handlers on the host side only | filesystem, network, env, or module access works from the worker |
| Direct surface and gateway surface drift apart | code-mode on/off registration rules are not centralized | tool registration split and feature-flag/profile wiring | create one shared classification table and derive both surfaces from it | the same tool behaves differently across on/off modes without design intent |
