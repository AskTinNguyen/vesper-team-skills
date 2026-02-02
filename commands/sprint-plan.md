---
name: sprint-plan
description: Review recent commits and product roadmap, then create an AI-agent-optimized sprint plan with automation-first task decomposition
argument-hint: "[roadmap source: file path (plans/roadmap.md), GitHub project URL, or feature list]"
---

# Sprint Plan

<command_purpose> Analyze recent codebase activity and product roadmap to produce a sprint plan where every feature is decomposed for maximum AI agent automation via Claude Code. Output: structured sprint document with automation feasibility scores and dispatch strategies. </command_purpose>

<role>Engineering Manager and Sprint Architect who decomposes work for parallel automated execution and optimizes sprint scope for maximum throughput with Claude Code agents</role>

## Input

<sprint_input> #$ARGUMENTS </sprint_input>

If the sprint input above is empty, ask the user: "Where is your product roadmap or feature list? Provide a file path (e.g., `plans/roadmap.md`), GitHub project URL, or describe the features for this sprint."

Do not proceed until you have a clear input source.

## Phase 0: Parse Input and Configure Sprint Scope

<thinking>
Determine input type, validate the source exists, and configure the time range before launching any agents.
</thinking>

**Detect input type:**

- **File path** (`/` or `.md`): Verify file exists with Read tool. Extract features/priorities.
- **GitHub Project URL** (`github.com`): Parse URL for owner and project number (`https://github.com/(orgs|users)/OWNER/projects/NUMBER`). Run `gh project item-list NUMBER --owner OWNER --format json --limit 100`.
- **GitHub Issues** (`label:` or `milestone:`): Run `gh issue list --label LABEL` or `--milestone MILESTONE --json title,body,labels,state`.
- **Inline feature list**: Parse directly as the feature set.

If the source is invalid (file not found, URL 404, empty result), re-prompt the user immediately. Do not launch agents with invalid input.

**Configure sprint scope** — ask the user:

"What time range should this sprint cover?"
1. **Last 2 weeks + Next 2 weeks** (Recommended)
2. **Last 1 week + Next 1 week**
3. **Last month + Next 2 weeks**
4. **Custom**

Store the selected start date as a relative git date string (e.g., `"2 weeks ago"`, `"1 month ago"`). This value is injected into agent prompts below as `{SINCE_DATE}`.

**Pre-flight checks:**

- [ ] Verify git repo: `git rev-parse --is-inside-work-tree`
- [ ] Check for existing sprint plans: `ls plans/sprint-*.md 2>/dev/null` — if found, ask: update existing or create new?
- [ ] If GitHub input: verify `gh auth status` succeeds

## Phase 1: Research

<critical_requirement> Agent 2 (Roadmap Parser) must complete BEFORE Agent 4 (Automation Assessor) can run. Agents 1, 2, 3 run in parallel first. Agent 4 runs after Agent 2 completes. </critical_requirement>

### Step 1a: Parse Roadmap + Analyze Codebase (parallel)

<parallel_tasks>

Spawn these three agents simultaneously:

**Agent 1: Commit Analyst**

```
Task(
  subagent_type: "Explore",
  model: "sonnet",
  description: "Analyzing commit history",
  prompt: "Analyze git history since {SINCE_DATE}.

Commands to run:
- `git log --oneline --since=\"{SINCE_DATE}\" --max-count=500`
- `git shortlog -sn --since=\"{SINCE_DATE}\"`
- `git branch -r --no-merged`

Output as structured markdown with these sections:
## Completed Features
(feature name, commit SHAs, files changed)
## In-Progress Work
(branch name, last commit, status)
## Hot Zones
(directory/file path, commit count)
## Velocity
(commits/day, PRs merged via `gh pr list --state merged --search \"merged:>{SINCE_DATE}\"`)
## Carry-Over Items
(incomplete branches, WIP commits)"
)
```

**Agent 2: Roadmap Parser**

```
Task(
  subagent_type: "general-purpose",
  model: "sonnet",
  description: "Parsing roadmap source",
  prompt: "Parse this roadmap source: {ROADMAP_SOURCE}

Steps:
1. Read the source (file/GitHub project/inline list)
2. Cross-reference with open issues: `gh issue list --state open --json number,title,labels,body --limit 100`
3. Check for existing plan files: `ls plans/*.md`
4. For each feature extract: title, description, priority (P0-P3), status (Not Started/In Progress/Blocked/Done)

Output as a markdown table:
| Feature | Priority | Status | Existing Issues/Plans | Dependencies |
Plus a summary list of greenfield features (no codebase footprint yet)."
)
```

**Agent 3: Codebase Mapper**

```
Task(
  subagent_type: "Explore",
  model: "sonnet",
  description: "Mapping codebase architecture",
  prompt: "Map the codebase architecture.

Research:
1. Read all CLAUDE.md files for conventions
2. Map directory structure and module boundaries
3. Find test infrastructure (frameworks, patterns, coverage gaps)
4. Detect tech debt: TODO/FIXME comments, deprecated code, skipped tests
5. Identify CI/CD setup

Output as structured markdown:
## Architecture Overview
## Test Infrastructure
## Technical Debt Inventory
(file path, description, severity)
## CI/CD Pipeline
## Conventions from CLAUDE.md"
)
```

</parallel_tasks>

### Step 1b: Assess Automation Feasibility (after Agent 2 completes)

Wait for Agent 2's feature list, then spawn:

**Agent 4: Automation Assessor**

```
Task(
  subagent_type: "general-purpose",
  model: "opus",
  description: "Assessing automation feasibility",
  prompt: "Score each feature for Claude Code automation feasibility.

Feature list from roadmap:
{AGENT_2_FEATURE_LIST}

Score each feature on 5 criteria (1-5 scale):
1. Specification clarity — well-defined enough for an agent?
2. Pattern availability — similar features exist in codebase?
3. Test verifiability — agent can verify its own work?
4. Isolation — no heavy human-in-the-loop decisions?
5. Conflict risk — low chance of merge conflicts with parallel agents?

Automation score = average. Thresholds:
- 4.0-5.0: Full automation (dispatch directly)
- 3.0-3.9: Assisted (agent works, human reviews)
- 2.0-2.9: Guided (human designs, agent implements)
- 1.0-1.9: Human-led (agent assists)

Output as markdown table:
| Feature | Clarity | Patterns | Tests | Isolation | Conflict | Score | Strategy |

Plus: parallelization graph and blockers requiring human input."
)
```

### Step 1c: Validate Research

<thinking>
Before synthesis, check that all agents returned usable data. If any agent failed or returned incomplete output, decide whether to retry or proceed with partial data.
</thinking>

- [ ] Agent 1 returned velocity metrics and commit data
- [ ] Agent 2 returned a feature list with priorities
- [ ] Agent 3 returned architecture overview
- [ ] Agent 4 returned automation scores for all features

If any agent failed: retry once with simplified prompt. If retry fails, proceed with partial data and flag gaps in the sprint plan's Risk section as "[INCOMPLETE — {agent_name} data unavailable]".

## Phase 2: Synthesis

<ultrathink_instruction>
Synthesize all research into a unified sprint context:
- Match features to commit history (done vs. planned vs. in-progress)
- Cross-reference automation scores with codebase readiness
- Build dependency graph (serialization vs. parallelization)
- Flag risks: high-priority features with low automation scores
- Calculate sprint capacity: `historical_velocity * sprint_days * agent_multiplier`
- Recommend scope: features that maximize value AND are highly automatable
</ultrathink_instruction>

Output: **Sprint Context Brief** — accomplishments, planned features, automation scores, constraints, recommended scope.

## Phase 3: Write Sprint Plan

Determine today's date with `date +%Y-%m-%d`. Write to `plans/sprint-{DATE}.md`:

```markdown
# Sprint Plan: {DATE}

## Sprint Goal
[1-2 sentence objective]

## Context
- **Sprint period:** {start} to {end}
- **Roadmap source:** {source}
- **Previous velocity:** {commits/day}, {PRs merged}
- **Automation target:** 100% code written by Claude Code agents
- **Sprint capacity:** {calculated from velocity * days * agent multiplier}

## Carry-Over
| Feature | Status | Remaining Work |

## Sprint Backlog

### P0 - Must Ship
| # | Feature | Score | Dispatch Strategy | Depends On |

### P1 - Should Ship
| # | Feature | Score | Dispatch Strategy | Depends On |

### P2 - Nice to Have
| # | Feature | Score | Dispatch Strategy | Depends On |

## Feature Details
(Per feature: priority, automation score, dispatch strategy, relevant files, similar patterns, suggested task breakdown, acceptance criteria, agent constraints)

## Automation Strategy
- Parallelization waves (which features run simultaneously)
- Human checkpoints (design/security/UX reviews needed before dispatch)
- Risk mitigation table (Risk | Impact | Mitigation)

## Technical Debt Budget
(Items from codebase mapper to address this sprint)

## Definition of Done
- All features pass automated tests
- Agent self-review via /workflows:review
- No new lint warnings
- PRs created and passing CI
```

**NEVER CODE during sprint planning.** This command produces a plan document only. Implementation happens via `/start-new-feature` or `/workflows:work`.

## Phase 4: Next Steps

<thinking>
Sprint plan is written. Present options to the user for what to do next. Keep planning separate from execution.
</thinking>

Ask the user: "Sprint plan ready at `plans/sprint-{DATE}.md`. Next?"

1. **Create GitHub issues** (Recommended) — `gh issue create` per feature with priority labels and `sprint:{DATE}` label
2. **Run `/deepen-plan`** — Enhance feature details with parallel research agents
3. **Refine plan** — Adjust priorities, scope, or automation strategies
4. **Start executing** — Dispatch P0 features (score >= 4.0) via `/start-new-feature`

## Anti-Patterns

- Don't skip commit/codebase research before planning
- Don't assume features are equally automatable — score each individually
- Don't serialize independent features — build parallelization waves
- Don't ignore carry-over work or exceed historical velocity
- Don't start coding — this command is planning only

## Workflow Pipeline

Flow: `sprint-plan` -> `start-new-feature` (per feature) -> `workflows:review` -> `verify-and-ship` -> `agent-changelog`

- `/sprint-plan`: Sprint scoping -> `plans/sprint-*.md`
- `/start-new-feature`: Parallel feature dispatch -> Task list + agents
- `/workflows:review`: Multi-agent code review -> `todos/*.md`
- `/verify-and-ship`: Quality gate -> PRs
- `/agent-changelog`: Capture learnings -> `AGENT_CHANGELOG.md`
