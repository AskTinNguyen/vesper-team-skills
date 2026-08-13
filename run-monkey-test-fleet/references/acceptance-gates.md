# Acceptance Gates

## Contents

1. Gate philosophy
2. Baseline gate
3. Lane gate
4. Integration gate
5. Final code gate
6. Runtime and production gates
7. Evidence matrix

## 1. Gate philosophy

Select commands from repository instructions and manifests; do not invent a fashionable matrix that the project does not support. A skipped unavailable gate is `unmeasured`, not `pass`. Record exact commands and revisions.

## 2. Baseline gate

Before implementation, capture:

- Repository status, branch, revision, and dirty paths.
- Supported interpreter/runtime and dependency environment.
- Existing unit/integration tests relevant to the dossier.
- Existing lint, format, type, compile, and package checks.
- Read-only state of live processes and data.
- Pre-existing failures with reproduction.

## 3. Lane gate

Each implementation lane should pass:

- Targeted regression tests.
- Tests for adjacent public behavior.
- Repository lint/format on touched files.
- Type checks on touched modules when supported.
- Security/accessibility/concurrency/crash probes required by its acceptance criteria.
- Clean branch diff and committed work.
- Clear specification review.
- Clear engineering review.

## 4. Integration gate

After every semantic merge wave:

- Run targeted cross-surface tests.
- Run the full automated suite when affordable.
- Re-run lint/format/type checks affected by conflict resolution.
- Compile or syntax-check shipped languages.
- Check migrations and old-data fixtures.
- Check for conflict markers, dropped entry points, duplicate handlers, stale tests, and lost documentation.
- Verify the integrated commit contains every cleared lane commit or equivalent semantic changes.

## 5. Final code gate

Apply all supported items:

- Unit and integration test suites.
- End-to-end/composed release fixture.
- Lint and format verification.
- Static type analysis with zero unwaived errors.
- Python/module compilation or equivalent.
- JavaScript/TypeScript syntax and import resolution.
- Native builds where shipped.
- Wheel/package/container/application builds.
- Dependency/entry-point smoke checks.
- Diff hygiene, conflict-marker, generated-file, and repository-status checks.
- Security, privacy, durability, recovery, concurrency, and stale-worker adversarial tests.
- Browser responsive and accessibility checks when UI changed.
- Two fresh whole-branch reviews of the exact revision.

Record the combined matrix as gate kind `final`, the dossier/spec auditor as `final_spec_review`, and the engineering/security auditor as `final_engineering_review`. All three must pass at the exact integration revision for strict ledger validation.

If a formatter changes code after tests, rerun affected tests and reviews. If the final revision changes, the previous certification no longer names the deployed artifact.

## 6. Runtime and production gates

Keep these separate from code certification:

- Safe deployment of the exact certified revision.
- Process restart verification.
- Browser/API/MCP smoke probes.
- Sanitization and policy probes against live configuration.
- Representative data coverage.
- Performance percentiles.
- Precision/recall/ranking quality.
- Long-running recovery behavior.
- Production-scale terminal coverage.

Only run authorized probes. Report fixture-verified but undeployed work accurately.

## 7. Evidence matrix

| Claim | Minimum evidence |
|---|---|
| Implemented | Commit and source diff |
| Regression fixed | Pre-fix reproduction plus post-fix targeted test |
| Specification-clear | Independent issue-by-issue review |
| Engineering-clear | Independent adversarial review |
| Integrated | Combined commit and cross-surface tests |
| Certified | Exact revision, full supported matrix, final audits |
| Deployed | Runtime identifies exact certified revision |
| Production-validated | Representative live metrics meet declared thresholds |

Never use a weaker row to claim a stronger row.
