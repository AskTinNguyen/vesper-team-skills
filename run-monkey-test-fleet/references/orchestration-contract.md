# Orchestration Contract

## Contents

1. Root responsibilities
2. Fleet sizing
3. Agent role contracts
4. Prompt templates
5. Review independence
6. Status protocol

## 1. Root responsibilities

The root orchestrator owns decisions that cannot be safely delegated:

- Scope and authority.
- Source-of-truth specifications.
- Issue normalization and acceptance criteria.
- Lane partitioning and file ownership.
- Protected branch, dirty-worktree, and live-process safety.
- Integration order and semantic conflict resolution.
- Ledger truth.
- Final revision freeze, quality matrix, and release claim.

Agents may discover facts and propose decisions. They do not independently broaden scope, deploy, overwrite user work, or declare the program complete.

## 2. Fleet sizing

Choose the smallest fleet that exposes real parallelism:

- 1–5 issues in one subsystem: one implementation owner plus two reviewers.
- 6–20 issues across several subsystems: 3–8 owners plus reviewers launched as commits land.
- 20+ cross-cutting findings: 6–15 ownership lanes, staged review waves, dedicated integration owners, and fresh final auditors.

Reserve at least 25% of available concurrency for rework, integration, and final audit. Prefer cohesive ownership over maximal agent count. Do not create two owners for the same writable file unless they use isolated worktrees and a named integration owner.

## 3. Agent role contracts

### Implementation owner

Must receive:

- Exact issue IDs and source documents.
- Explicit owned modules/files and forbidden surfaces.
- Worktree, branch, and base revision.
- Baseline and required verification commands.
- Acceptance criteria and expected evidence.
- Instruction that other agents are editing the repository and their work must not be reverted.
- Instruction to avoid live data and unrelated cleanup.

Must return:

- Commit hash.
- Issues addressed and acceptance mapping.
- Changed files.
- Tests added and commands/results.
- Known gaps and residuals.
- Integration dependencies/conflicts.

### Specification reviewer

Must not be the implementation owner. Verify exact behavior against the dossier and authoritative specifications. Read source and execute targeted reproductions. Treat missing product behavior, UX contracts, migrations, and public API semantics as findings even when tests pass.

### Engineering reviewer

Must not be the implementation owner or specification reviewer for the same lane when capacity permits. Review failure atomicity, concurrency, stale ownership, validation, privacy, path safety, schema evolution, type contracts, accessibility, maintainability, and test adequacy.

### Integration owner

Own only the named semantic merge in the isolated integration worktree. Preserve both parent contracts, remove obsolete branches deliberately, update tests to the surviving specification, and run combined gates. Do not change unrelated code.

### Final whole-branch auditor

Review an immutable revision with the complete raw dossier/specification set. Do not rely on lane summaries. Seek cross-track defects and verify claims from artifacts or commands.

## 4. Prompt templates

### Implementation prompt

```text
You own <lane> in worktree <path>, branch <branch>, based on <revision>.
Issues: <IDs>. Authoritative sources: <paths>.
Owned surfaces: <files/modules>. Do not edit <forbidden surfaces> without reporting the need.

You are not alone in the codebase. Other agents are editing other branches/worktrees. Do not revert or overwrite their work; adapt to shared contracts and report integration dependencies.

Read all repository instructions. Reproduce the issue, add regressions where practical, implement the smallest complete contract, and run: <commands>. Do not mutate live data/processes or perform unrelated cleanup. Commit your work.

Return: commit, changed files, issue-by-issue acceptance evidence, commands/results, residuals, and expected merge conflicts. A design memo without implementation is not completion.
```

### Specification-review prompt

```text
Independently review exact revision <commit> for issues <IDs> against <raw source paths>.
Do not assume the implementation owner's claims are correct. Inspect code, tests, and public behavior; run targeted reproductions. Return one verdict per issue: clear, partial, fail, or unmeasured. For every finding give severity, location, observable contradiction, and required correction. Do not modify code.
```

### Engineering-review prompt

```text
Independently review exact revision <commit> and diff <base>..<commit>.
Inspect correctness, security, privacy, durability, atomicity, recovery, concurrency, stale-worker fencing, input/path safety, schema compatibility, type safety, accessibility, maintainability, and test quality. Run focused checks. Return prioritized findings with file/function, reproduction or reasoning, and required correction. State whether the lane is safe to integrate. Do not modify code.
```

### Rework prompt

```text
Your prior lane at <commit> received the attached independent findings: <findings>.
Reproduce each finding, patch only the owned surface, add regression evidence, rerun the required gates, and commit a focused follow-up. Return a finding-to-fix map. Do not treat unrelated reviewer suggestions as authorized scope.
```

### Semantic-integration prompt

```text
In integration worktree <path>, semantically integrate <commits/branches> onto <base>.
Preserve contract A: <A>. Preserve contract B: <B>. Retire only these obsolete behaviors: <list>.
You are not alone in the repository; do not touch the root checkout or unrelated changes. Resolve conflicts, run <combined gates>, commit the merge, and return conflict decisions plus evidence.
```

### Final audit prompt

```text
Audit immutable revision <commit> in <worktree> against the complete dossier/spec set <paths>.
Reconstruct truth from source artifacts, not prior summaries. Verify issue closure, cross-track behavior, quality artifacts, and residual claims. Do not modify code. Return blockers, non-blocking residuals, unmeasured gates, and a release verdict.
```

## 5. Review independence

Preserve independence by:

- Using separate agents and fresh prompts.
- Passing raw artifacts and exact revisions.
- Omitting the intended verdict.
- Avoiding prior reviewer conclusions unless asking for a focused delta review.
- Requiring executable or source-based evidence.
- Re-reviewing after any material fix.

Two agents repeating the implementer's summary are not two reviews.

## 6. Status protocol

Maintain one ledger entry per issue and one lane record per owner. Agent conversational status is advisory until reconciled with commits, diffs, and commands.

Send user updates when:

- Baseline and fleet shape are known.
- A lane commits and enters review.
- Review finds a material blocker.
- A merge wave clears.
- Final gates start or fail.
- Live-system safety changes the deployment plan.

State counts and exact blockers. Avoid narrating every tool call.
