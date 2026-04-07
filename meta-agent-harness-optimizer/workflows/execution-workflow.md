# Execution Workflow — meta-agent harness optimizer

Use this workflow when the goal is to **execute with the skill**, not just read references.

This workflow is the default operating path for agents that need to:
- analyze the `canvas-org/meta-agent` repo,
- refresh captured references from a local clone,
- extract scripts, tool calls, methods, and prompts,
- or port the pattern into another system such as Vesper.

## Success Criteria

The workflow is complete when:
- the task goal is clearly classified,
- the right reference files have been read,
- any requested extraction includes the relevant category files,
- claims about the source repo are grounded in current files or refreshed snapshots,
- and the final output clearly distinguishes **scripts**, **tool calls**, **methods**, and **prompts** when those categories are relevant.

## Default Workflow

### 1) Classify the task
First decide which of these jobs is being requested:

1. **Architecture understanding**
   - goal: explain how `meta-agent` works
2. **Reference extraction**
   - goal: capture scripts, tool calls, methods, prompts, or conventions
3. **Source refresh**
   - goal: update this skill from a newer local clone
4. **Porting / implementation**
   - goal: adapt the pattern into Vesper or another runtime
5. **Repo extension**
   - goal: change the source repo itself or propose changes to it

If the request spans multiple jobs, handle them in that order:
**understand → extract → port / extend**.

### 2) Read only the files needed for the task

#### If the task is architecture understanding
Read:
- `references/architecture.md`
- `references/methods.md`

#### If the task is reference extraction
Read:
- `references/scripts.md`
- `references/toolcalls-and-tools.md`
- `references/methods.md`
- `references/prompts.md`

Only read the categories the task actually asks for.

#### If the task is source refresh
Read:
- `references/scripts.md`
- then run `scripts/refresh-from-local-clone.sh`
- then verify refreshed files exist in `references/source-snapshots/`

#### If the task is porting / implementation
Read:
- `references/architecture.md`
- `references/prompts.md`
- `references/toolcalls-and-tools.md`
- `references/implementation-guide.md`

#### If the task is repo extension
Read:
- `references/conventions.md`
- `references/methods.md`
- `references/architecture.md`

### 3) Refresh from local clone when freshness matters
If the task depends on exact source state and a local clone is available, run:

```bash
scripts/refresh-from-local-clone.sh /path/to/meta-agent
```

Default local path on Tin's machine:
```bash
scripts/refresh-from-local-clone.sh /Users/tinnguyen/meta-agent
```

Then confirm refreshed snapshots exist under:
- `references/source-snapshots/README.md`
- `references/source-snapshots/source-SKILL.md`
- `references/source-snapshots/outer_loop.py`
- `references/source-snapshots/eval_runner.py`
- `references/source-snapshots/task_runner.py`

## 4) Use the method inventory when verifying implementation anchors
If the task needs exact functions or current line-number inspection, run:

```bash
scripts/method-inventory.sh /path/to/meta-agent
```

Use it to verify:
- function names,
- file locations,
- approximate line anchors,
- config/hook/adapter surfaces.

## 5) Preserve category boundaries in outputs
When writing results, keep these categories separate:

### Scripts
Include:
- executable commands,
- module entrypoints,
- operational CLI surfaces,
- environment variables when execution depends on them.

### Tool calls
Include:
- Claude CLI flags,
- Claude Agent SDK tool surfaces,
- hook event names,
- adapter-generated tools,
- verification command surfaces when relevant.

### Methods
Include:
- key functions,
- purpose,
- file:line evidence,
- extension seams.

### Prompts
Include:
- outer-loop proposer prompt,
- bundled skill prompt logic,
- skill-evolver prompt template,
- prompt appends,
- hook-injected prompt fragments.

Do not collapse these into one mixed summary unless the user explicitly asks for a shorter synthesis.

## 6) Add drift caveats when needed
If the task depends on exact line references or live source fidelity, say explicitly that:
- file:line anchors may drift as the source repo changes,
- helper scripts should be rerun after upstream updates,
- refreshed local snapshots are more authoritative than older extracted notes.

## 7) Final verification checklist
Before finishing, verify:
- Did the response include the requested category or categories?
- Did the response stay grounded in the current repo or refreshed snapshots?
- Did the response preserve category separation where useful?
- Did the response avoid inventing APIs, scripts, or prompts not present in the source?
- If porting to Vesper, did the response clearly separate **what exists in source** vs **what is a proposed adaptation**?

## Troubleshooting

### Local clone not found
If `/Users/tinnguyen/meta-agent` or the supplied path does not exist:
- skip refresh,
- use the already captured references,
- state that the answer is based on the existing extracted snapshot rather than a fresh refresh.

### Line numbers no longer match
If method inventory and references disagree:
- trust the current local clone,
- update the references later,
- state that anchors drifted due to upstream edits.

### Source repo structure changed
If expected files like `meta_agent/outer_loop.py` moved:
- inspect the new structure first,
- map the new equivalent files,
- update this skill's references before making strong architectural claims.

## Related skills
After using this workflow, the best follow-on skills are often:
- `repo-deep-dive`
- `skill-creator`
- `skill-enricher`
- `workflow-compound`
