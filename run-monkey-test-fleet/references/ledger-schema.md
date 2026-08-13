# Fleet Ledger Schema

## Contents

1. Run state
2. Issue state machine
3. Lane state machine
4. Evidence rules
5. Minimal example

## 1. Run state

`ledger.json` is the authoritative program record. Required top-level keys:

- `schema_version`: currently `1`.
- `run`: identity, repository, dossier, base revision, integration revision, deployment revision, status, timestamps, authority, protected paths, and live-process notes.
- `issues`: normalized findings.
- `lanes`: ownership and agent status.
- `gates`: baseline, lane, integration, final, packaging, browser, runtime, and production measurements.
- `discoveries`: requirements found after initial intake.
- `residuals`: accepted or unresolved risks.
- `events`: concise chronological decisions.

Recommended run statuses are `intake`, `planning`, `implementing`, `reviewing`, `rework`, `reconciling`, `integrating`, `final_review`, `certified`, `deployed`, and `complete_with_residuals`. Strict validation accepts only the last three and checks their supporting revision evidence.

Do not store secrets, lease tokens, raw credentials, private source paths intended for public artifacts, or unnecessary process details.

## 2. Issue state machine

Allowed issue states:

```text
identified -> normalized -> assigned -> implementing -> review_spec
          -> review_engineering -> rework -> integration_ready -> integrated
          -> final_review -> cleared
```

Terminal truth states:

- `cleared`: all required code, evidence, reviews, integration, and documentation are complete.
- `partial`: some acceptance criteria pass; missing criteria are explicit.
- `blocked`: external authority/dependency prevents completion after safe alternatives are exhausted.
- `roadmap`: explicitly out-of-scope capability, not a disguised defect closure.
- `unmeasured`: implementation may exist, but required production/runtime measurement did not occur.
- `wont_fix`: user-authorized decision with rationale and risk owner.

An issue may return from either review or integration to `rework`. Any post-clearance code change affecting its surface returns it to `final_review`.

Each issue contains:

```json
{
  "id": "AREA-001",
  "title": "Observable title",
  "source": "docs/qa/findings.md#area-001",
  "severity": "P1",
  "kind": "code",
  "state": "normalized",
  "acceptance": [
    {"id": "AREA-001-A", "criterion": "Observable outcome", "status": "pending", "evidence": []}
  ],
  "lane": "area-core",
  "implementation_commits": [],
  "reviews": {"spec": [], "engineering": []},
  "integration_commit": null,
  "residuals": [],
  "notes": []
}
```

Allowed acceptance statuses: `pending`, `pass`, `fail`, `unmeasured`, `not_applicable`.

## 3. Lane state machine

Allowed lane states:

```text
planned -> running -> committed -> reviewing -> rework -> cleared
        -> integrating -> integrated -> final_review -> complete
```

Failure states are `errored` and `blocked`; they must include a reason and next action. An errored agent does not imply an errored lane if reassigned.

Each lane records:

- ID, issue IDs, owned surfaces, forbidden surfaces.
- Worktree, branch, base, implementation agent, and reviewer agents.
- State, commits, command results, findings, rework rounds, and integration notes.
- Model requested, model actually used, and substitution reason.

## 4. Evidence rules

Every evidence item should contain:

- `kind`: test, review, browser, static-analysis, build, manual-probe, runtime, artifact, or decision.
- `revision`: exact commit where applicable.
- `command` or method.
- `result`: pass, fail, or unmeasured.
- `summary`: counts or observed behavior.
- `artifact`: optional repository-relative or run-directory path.
- `timestamp`.

Clearance requires:

- Every acceptance criterion is `pass` or justified `not_applicable`.
- At least one implementation commit.
- A clear specification review.
- A clear engineering review.
- An integration commit containing the fix.
- Relevant combined and final gates at that integration revision or a descendant proven not to alter the surface.
- No unresolved P0/P1 residual attached to the issue.

Strict run validation also requires at least one issue and lane, terminal lane states, a passing `final` matrix gate, and passing `final_spec_review` and `final_engineering_review` gates at the exact `run.integration_revision`. A run marked `deployed` must name that same revision in `run.deployment_revision`.

Do not count a review statement as test evidence or a unit test as live evidence.

## 5. Minimal example

```json
{
  "schema_version": 1,
  "run": {
    "id": "2026-08-13-monkey",
    "repo_root": "/workspace/project",
    "dossier": "docs/qa/monkey.md",
    "base_revision": "abc123",
    "integration_revision": null,
    "deployment_revision": null,
    "status": "intake",
    "created_at": "2026-08-13T00:00:00Z",
    "authority": ["code_changes"],
    "protected_paths": [],
    "live_process_notes": []
  },
  "issues": [],
  "lanes": [],
  "gates": [],
  "discoveries": [],
  "residuals": [],
  "events": []
}
```
