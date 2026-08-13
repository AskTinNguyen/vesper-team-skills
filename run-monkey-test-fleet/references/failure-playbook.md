# Failure Playbook

## Contents

1. Unsupported model or tool
2. Agent failure and weak delivery
3. Worktree and branch mistakes
4. Semantic merge collisions
5. Dirty root or concurrent `main`
6. Late specifications and expanding scope
7. Live processes and data
8. False-green tests
9. Review disagreement
10. Exhaustion and blockers

## 1. Unsupported model or tool

If a requested model fails before work begins:

1. Record the exact unsupported response.
2. Confirm no filesystem changes occurred.
3. Reassign with the strongest available suitable model.
4. Preserve independent implementation/review agents.
5. Disclose the substitution; never use the requested model's name as a nickname for another model.

If repository-required discovery tooling is unavailable, document that condition and use the permitted fallback.

## 2. Agent failure and weak delivery

Treat these as incomplete:

- Memo without code when implementation was assigned.
- Green tests from an unsupported interpreter.
- Uncommitted changes without a stable revision.
- “Done” without issue-to-evidence mapping.
- Work outside the owned surface without justification.

Inspect the worktree, preserve useful work, tighten the task with exact commands and acceptance criteria, then reassign or follow up. Record agent error separately from lane status.

## 3. Worktree and branch mistakes

If an agent edits the wrong checkout:

1. Stop the lane.
2. Inspect status and commits in both intended and actual worktrees.
3. Do not reset or delete changes.
4. Classify changes as user-owned, concurrent-owner, useful lane work, or off-scope.
5. Move only committed, attributable work through merge/cherry-pick into the isolated branch.
6. Reassign with an explicit workspace guard.

## 4. Semantic merge collisions

Do not settle complex conflicts by choosing “ours” or “theirs” globally. State both contracts, assign an integration owner, ask advisers about independent backend/frontend/test dimensions when useful, remove obsolete behavior deliberately, and run combined tests. A syntactically resolved merge is not a semantically correct merge.

## 5. Dirty root or concurrent `main`

Preserve all uncommitted and untracked work. Do not stash, stage, commit, reset, or overwrite it unless the user explicitly authorizes ownership.

- Continue in an isolated integration worktree.
- Merge newly committed protected-branch work into integration.
- Re-run affected gates and reviews.
- Hand off the clean integration branch if the root remains dirty.
- Explain why root deployment/fast-forward was withheld.

## 6. Late specifications and expanding scope

When a more authoritative approved brief appears:

1. Read it fully.
2. Compare it with the implemented contract.
3. Create new findings for material gaps.
4. Do not retroactively claim earlier agents ignored a document they could not access.
5. Implement and review the authoritative contract.
6. Preserve compatible prior hardening.

When concurrent committed features arrive, treat their integration defects as real release findings if they fall within the claimed release artifact. Keep unrelated uncommitted work out.

## 7. Live processes and data

Before any restart or live probe:

- Identify the exact process, command, owner, port, revision, active job, and dependent services.
- Wait for or preserve active work unless interruption was authorized.
- Restart only the intended component.
- Do not infer that a process belongs to this run from its port alone.
- Keep read-only status probes separate from mutations.

If safe deployment is blocked, code certification may still complete; report deployment as not performed.

## 8. False-green tests

Investigate when tests pass but reviewers find contradictions. Common causes:

- Tests encode retired behavior.
- Isolated branch lacks another lane's security contract.
- Fixture does not drive the public path.
- Evidence generator reports configured rather than measured results.
- Read paths mutate state unnoticed.
- Crash windows, lease loss, or ambiguous retry are untested.
- Accessibility assertions do not reflect real browser focus/layout.
- Static mocks hide descriptor, path, process, or network behavior.

Add the smallest realistic reproduction and keep the reviewer finding open until it passes on integration.

## 9. Review disagreement

Do not vote. Compare each claim to the authoritative specification and executable evidence. A specification reviewer may clear product behavior while an engineering reviewer finds a security edge; both findings remain valid. Ask a focused third reviewer only when the evidence or governing contract is genuinely ambiguous.

## 10. Exhaustion and blockers

Do not call work blocked because it is large or because one agent failed. Reassign, reduce lanes, integrate sequentially, or use focused advisers. Mark blocked only when required authority, external state, unavailable infrastructure, or a user decision prevents meaningful progress after safe alternatives are exhausted. Record the precise unblock condition.
