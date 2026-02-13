---
name: workflows:guided-analysis
description: Main interactive workflow — recon through Checkpoint 1 interview and parallel agent execution
---

# Guided Analysis Workflow

<command_purpose>Perform collaborative repo analysis: reconnaissance, user interview at Checkpoint 1 to select focus areas, then launch targeted agents based on user preferences.</command_purpose>

<role>Senior Software Archaeologist who collaborates with the user to understand what matters before investigating — asking questions, presenting options, and adapting the investigation plan to user priorities.</role>

## Phase 1: Repo Ingestion

<critical_requirement>Complete Phase 1 fully before presenting Checkpoint 1. The reconnaissance data forms the basis of the user interview.</critical_requirement>

### Step 1.1: Obtain the Repository

```
If GitHub URL or owner/repo format:
  gh repo clone {repo} /tmp/repo-deep-dive/{repo-name} -- --depth 1
  cd /tmp/repo-deep-dive/{repo-name}

If local path:
  cd {path}
  Verify it's a git repo: git rev-parse --is-inside-work-tree

If current directory:
  Use . as the path
```

### Step 1.2: Run Reconnaissance Script

Execute the bundled reconnaissance script:

```bash
bash {skill-path}/scripts/analyze-repo.sh {repo-path}
```

This produces:
- Directory tree (depth 3)
- File type distribution
- Config file inventory
- Entry point candidates
- LOC estimate

### Step 1.3: Read Priority Files

Read the analysis-checklist.md reference from the `repo-deep-dive` skill for the full priority list. At minimum, read these in order:

<task_list>
- [ ] README.md / README.rst / README
- [ ] Package manifest (package.json, Gemfile, Cargo.toml, go.mod, pyproject.toml, etc.)
- [ ] Lock file sample (first 50 lines for version info)
- [ ] Main config files (tsconfig.json, .eslintrc, rubocop.yml, Makefile, docker-compose.yml)
- [ ] Entry points (src/index.ts, main.go, app.rb, manage.py, etc.)
- [ ] CI/CD config (.github/workflows/, .circleci/, Jenkinsfile)
- [ ] CONTRIBUTING.md, ARCHITECTURE.md, docs/ directory listing
</task_list>

### Step 1.4: Detect Tech Stack

Read the tech-stack-detection.md reference from the `repo-deep-dive` skill and identify:

- Primary language(s)
- Framework(s) and version(s)
- Build system / task runner
- Test framework(s)
- Database / data layer
- Deployment target (Docker, serverless, bare metal, etc.)

### Step 1.5: Prepare User-Facing Summary

<critical_requirement>This summary is for the USER, not just for agents. Make it clear, concise, and useful for decision-making at Checkpoint 1.</critical_requirement>

Present to the user:

```markdown
## Repo Reconnaissance Complete

**Repository:** {name}
**Purpose:** {1-2 sentence description from README}

### Tech Stack
- **Language:** {primary language(s)}
- **Framework:** {framework(s) + version(s)}
- **Build:** {build system}
- **Test:** {test framework(s)}
- **Database:** {data layer}
- **Deploy:** {deployment target}

### Structure
{Top-level directory tree with brief annotations}

### Size
- **Files:** {total count} (excluding deps/build)
- **LOC estimate:** {total} ({breakdown by language})

### Notable
- {Any interesting findings — monorepo structure, unusual patterns, key config}
```

Also prepare the Phase 1 context document (~200 words) for agent consumption (same data, condensed format).

---

## Checkpoint 1: Post-Recon Interview + Plan Confirmation

<critical_requirement>Do NOT proceed to Phase 2 until the user responds. This is a blocking interview.</critical_requirement>

### Step CP1.1: Present Recon Findings

Display the user-facing summary from Step 1.5.

### Step CP1.2: Conduct Interview

Read [interview-questions.md](../references/interview-questions.md) Checkpoint 1 section. Ask questions Q1.1 through Q1.5 in a natural conversational flow. Adapt based on context:

- If the repo is a library, emphasize API surface questions
- If it's a web app, emphasize architecture and features
- If the user mentioned a specific goal in intake, tailor questions to that goal
- Combine questions where natural — don't ask 5 separate messages if 2-3 will do

Read [analysis-dimensions.md](../references/analysis-dimensions.md) and present the dimension menu when asking Q1.2.

### Step CP1.3: Build Agent Plan

Based on user responses, determine:

1. **Which agents to launch** — Map dimensions → agents using the agent selection logic in [agent-prompts.md](../references/agent-prompts.md)
2. **Scope constraints** — From Q1.4 region focus
3. **Depth level** — From Q1.3
4. **User-specific questions** — From Q1.5, assigned to the most relevant agent(s)

Present the plan to the user:

```markdown
## Proposed Investigation Plan

Based on your selections, here's what I'll investigate:

| Agent | Focus | Scope | Depth |
|-------|-------|-------|-------|
| {Agent Name} | {What it will investigate} | {Scope constraints or "full repo"} | {depth} |
| ... | ... | ... | ... |

**Estimated agents:** {N} of 5
**Dimensions covered:** {list}

Proceed with this plan, adjust it, or switch to autonomous mode (analyze everything)?
```

### Step CP1.4: Handle Response

**If "Looks good / Proceed":** Continue to Phase 2 with the planned agents.

**If "Adjust":** Modify the plan per user feedback and re-present.

**If "Analyze everything" / "Skip" / autonomous mode:**
<critical_requirement>
FAST-EXIT PATH: Launch all 5 agents with standard depth, no scope constraints, no user-specific questions. Skip Checkpoints 2 and 3. After agents return, synthesize and generate the full output package autonomously using the output generation logic from guided-synthesis.md Phase 5 — but without user checkpoints.
</critical_requirement>

---

## Phase 2: Targeted Agent Launch

### Step 2.1: Prepare Agent Prompts

Read [agent-prompts.md](../references/agent-prompts.md). For each selected agent:

1. Start with the agent's template
2. Replace `{repo-path}` with the actual repo path
3. Replace `{phase1-context}` with the condensed Phase 1 context
4. Replace `{user-specific-questions}` with relevant questions from Q1.5 (or "None specified")
5. Replace `{scope-constraints}` with region focus from Q1.4 (or "No constraints — investigate the full repository")
6. Append the depth-level modifier from the agent-prompts.md customization table

### Step 2.2: Launch Agents

<parallel_tasks>
Launch all selected agents simultaneously using Task Explore. Each agent runs independently.

If only 1-2 agents are needed, launch them. Do not pad with unnecessary agents.

If all 5 agents are needed (user selected all dimensions or fast-exit), launch all 5.
</parallel_tasks>

### Step 2.3: Collect Agent Reports

Wait for all agents to return. Collect their structured reports.

---

## Phase 2 Synthesis

### Step 2.4: Consolidate Findings

<task_list>
- [ ] Collect all agent reports
- [ ] Reorganize findings by user-selected dimensions (not by agent)
- [ ] Identify overlapping findings and consolidate (de-duplicate)
- [ ] Flag any contradictions between agents
- [ ] Note gaps — areas the user asked about that weren't fully covered
- [ ] Assign confidence levels: definite / probable / possible
- [ ] Count evidence references per finding
</task_list>

### Step 2.5: Prepare Findings Presentation

Read [findings-presentation.md](../references/findings-presentation.md) and format the consolidated findings for Checkpoint 2 review. Organize by user interest, not by agent source.

---

## Phase 3: Feature Extraction (Conditional)

<critical_requirement>Only execute Phase 3 if the user selected the "Features" dimension at Checkpoint 1.</critical_requirement>

### Step 3.1: Identify Core Features

Using the Phase 2 reports, list every user-facing feature:
- What can users DO with this system?
- What are the main workflows/journeys?
- What CRUD operations exist?
- What background/async operations run?

### Step 3.2: Map Features to Implementation

For each core feature:
<task_list>
- [ ] Entry point (route, command, event handler)
- [ ] Key files involved (controller, service, model, view)
- [ ] Design patterns used
- [ ] Database tables/collections touched
- [ ] External services called
- [ ] Error handling approach
- [ ] Test coverage (which test files cover this feature)
</task_list>

### Step 3.3: Extract Generalizable Recipes

For each feature, distill a "recipe" — a generalized step-by-step for implementing a similar feature.

### Step 3.4: Document Extension Points

Identify where the system is designed to be extended:
- Plugin/hook systems
- Configuration-driven behavior
- Abstract base classes / interfaces
- Event emitters / pub-sub channels
- Middleware registration points

---

## Phase 4: Knowledge Synthesis (Conditional)

<critical_requirement>Only execute Phase 4 if the user selected depth level "Exhaustive" or selected 3+ dimensions.</critical_requirement>

### Step 4.1: Architecture Decision Records

For each significant architectural choice detected, create an ADR:

```
## ADR: {Title}
**Status:** Observed (inferred from code)
**Context:** {Why this decision was likely made}
**Decision:** {What was chosen}
**Evidence:** {file:line references}
**Consequences:** {Trade-offs observed}
```

### Step 4.2: Anti-Patterns Avoided

Note patterns that are conspicuously absent — things the codebase deliberately does NOT do.

### Step 4.3: Consolidate Conventions

Merge the convention extractor's findings with patterns observed across all phases.

### Step 4.4: Quality Assessment

Rate the codebase on:
- **Consistency** (1-5): How consistently are patterns applied?
- **Documentation** (1-5): How well is the code documented?
- **Test Coverage** (1-5): How thorough is the test suite?
- **Separation of Concerns** (1-5): How clean are the boundaries?
- **Extensibility** (1-5): How easy is it to add new features?

---

## Hand Off to Guided Synthesis

<critical_requirement>If in fast-exit mode (autonomous), skip directly to Phase 5 output generation in guided-synthesis.md without Checkpoints 2 and 3.</critical_requirement>

Pass to [guided-synthesis.md](./guided-synthesis.md):
- Formatted findings presentation (from Step 2.5)
- Phase 1 context
- User selections from Checkpoint 1 (dimensions, depth, emphasis)
- Fast-exit flag (true/false)
- Feature extraction results (if Phase 3 ran)
- Knowledge synthesis results (if Phase 4 ran)
