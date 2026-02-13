---
name: repo-deep-dive-interactive
description: This skill should be used when users want to collaboratively analyze a GitHub repository or local codebase through an interview-driven process. It interviews the user at 3 checkpoints to understand what matters before reaching conclusions — selecting analysis dimensions, triaging findings, and shaping output. Produces structured output compatible with the skill-creator skill. Triggers on requests like "interactively analyze this repo", "guided deep dive", "analyze this repo with me", or "interview me about this codebase".
---

<objective>
Perform collaborative, interview-driven analysis of a GitHub repository or local codebase. Interview the user at 3 checkpoints — after reconnaissance, after analysis, and before output generation — to focus investigation on what matters most. Produce structured reference files reflecting user-selected emphasis, formatted for consumption by the skill-creator skill.
</objective>

<essential_principles>
## Core Philosophy

**Ask before assuming:** Never decide what matters without consulting the user. Present findings and let the user direct depth, focus, and emphasis through structured interviews at each checkpoint.

**Selective investigation:** Launch only the agents the user's selections require. If the user cares about architecture and conventions but not testing, skip the test pattern analyzer.

**User-directed depth:** The user controls how deep to go. "Dig deeper" at Checkpoint 2 launches targeted follow-up investigation. "Skip" discards low-value findings.

**Fast-exit to autonomous mode:** If the user says "analyze everything" or "skip" at Checkpoint 1, degrade gracefully — launch all 5 agents, skip remaining checkpoints, generate the full output package autonomously.

**Evidence-based extraction:** Every pattern, convention, and architectural decision documented must include `file:line` references back to the source code. No speculation — only what the code demonstrates.

**Progressive depth:** Start with broad reconnaissance (directory structure, config files, README), then drill into user-selected dimensions in parallel.

**Skill-creator compatibility:** All output follows the skill-creator spec — YAML frontmatter with `name` and `description`, XML body tags, progressive disclosure via references, imperative writing style.

**Shallow clone first:** Use `--depth 1` for initial analysis. Only fetch full history when git log analysis or blame is specifically needed.

**Bounded iteration:** Deep-dive sessions are capped at 3 iterations to prevent unbounded loops. On the third iteration, present findings as final.
</essential_principles>

<intake>
What repo do you want to analyze?

Provide one of:
- **GitHub URL** — `https://github.com/owner/repo` or `owner/repo`
- **Local path** — `/path/to/repo` or `.` for current directory
- **PR/branch** — analyze a specific branch or PR's changes

No need to select a workflow — the guided interview will help determine what to focus on.
</intake>

<routing>

| Response | Workflow to Load |
|----------|-----------------|
| Any repo URL, path, or identifier | [guided-analysis.md](./workflows/guided-analysis.md) |

**Always route to guided-analysis.md.** The interview process handles all routing decisions.

After selecting the workflow, read it and follow its procedures.

</routing>

<reference_index>
## Reference Files

Load these as needed during analysis:

| File | Purpose |
|------|---------|
| [interview-questions.md](./references/interview-questions.md) | Question bank for 3 checkpoints |
| [analysis-dimensions.md](./references/analysis-dimensions.md) | User-facing menu of 6 analysis areas |
| [findings-presentation.md](./references/findings-presentation.md) | Templates for presenting findings with triage format |
| [agent-prompts.md](./references/agent-prompts.md) | 5 agent prompt templates with placeholders |

## Workflows

| Workflow | Purpose |
|----------|---------|
| [guided-analysis.md](./workflows/guided-analysis.md) | Main flow: recon + Checkpoint 1 + agent launch + synthesis |
| [guided-synthesis.md](./workflows/guided-synthesis.md) | Checkpoint 2 findings review + Checkpoint 3 output shaping + generation |
| [deep-dive-session.md](./workflows/deep-dive-session.md) | Iterative refinement loop for "dig deeper" requests (max 3 iterations) |

## Scripts

| Script | Purpose |
|--------|---------|
| [analyze-repo.sh](./scripts/analyze-repo.sh) | Initial reconnaissance — directory tree, file counts, config detection |

## External References (Read by Skill Name)

These files live in the `repo-deep-dive` skill. Read them by skill name when needed:

| File | Purpose |
|------|---------|
| `repo-deep-dive` → `references/pattern-catalog.md` | Catalog of design patterns to identify |
| `repo-deep-dive` → `references/tech-stack-detection.md` | Framework and language detection matrix |
| `repo-deep-dive` → `references/output-architecture.md` | Template for generated architecture.md |
| `repo-deep-dive` → `references/output-patterns.md` | Template for generated patterns.md |
| `repo-deep-dive` → `references/output-conventions.md` | Template for generated conventions.md |
| `repo-deep-dive` → `references/output-features.md` | Template for generated features.md |
| `repo-deep-dive` → `references/output-skill-template.md` | Template for generated SKILL.md |

</reference_index>

<output_format>
## Generated Output Structure

The final output is a complete skill directory, filtered by user selections:

```
repo-knowledge-{repo-name}/
├── SKILL.md                    # Pre-populated with extracted principles, routing, conventions
├── references/
│   ├── architecture.md         # System overview, component catalog, data flow, ADRs
│   ├── patterns.md             # Design patterns with generic + source-specific examples
│   ├── features.md             # Feature catalog, implementation recipes, extension points
│   ├── conventions.md          # Naming, file org, error handling, testing conventions
│   └── implementation-guide.md # "How to build a similar system" step-by-step
└── assets/templates/           # Component/module/test templates in repo's style
```

Files are only generated for dimensions the user selected. Output emphasis, naming, and exclusions reflect Checkpoint 3 preferences.

This output can be fed directly into skill-creator: "Create a skill from repo-knowledge-{repo-name}/"
</output_format>

<success_criteria>
Analysis is complete when:
- Tech stack is identified with evidence (config files, imports, dependencies)
- User confirmed analysis dimensions at Checkpoint 1
- Selected agents completed their investigation
- User triaged findings at Checkpoint 2 (keep/skip/dig deeper)
- User shaped output preferences at Checkpoint 3
- Output package reflects user-selected emphasis and exclusions
- Output package passes skill-creator validation (valid YAML frontmatter, XML tags, imperative style)
- Every extracted pattern has source code evidence
- All "dig deeper" requests were investigated (within 3-iteration bound)
</success_criteria>
