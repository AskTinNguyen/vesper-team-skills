# Interview Questions

Question bank for the 3 interactive checkpoints. Each checkpoint includes structured options, an open-ended escape, and notes on what each answer drives downstream.

## Checkpoint 1: Post-Recon + Plan Confirmation

Present after Phase 1 reconnaissance completes. The user has seen the tech stack summary, directory structure, file distribution, and inferred purpose. This checkpoint combines "what do you want to focus on?" with "here's the agent plan — approve or adjust."

### Q1.1: Motivation

> **What's your goal for this analysis?**
>
> 1. **Learn the codebase** — Understand how it works before contributing
> 2. **Extract patterns** — Capture reusable architecture and design patterns
> 3. **Create a skill** — Produce a skill-creator-compatible output package
> 4. **Evaluate quality** — Assess code quality, test coverage, and maintainability
> 5. **Something else** — *(open-ended)*
>
> **Drives:** Output format, level of detail, which dimensions get priority.

### Q1.2: Analysis Dimensions

> **Which areas do you want to investigate?** *(Select all that apply, or "all")*
>
> Read [analysis-dimensions.md](./analysis-dimensions.md) for detailed descriptions.
>
> 1. **Architecture** — System structure, component boundaries, data flow
> 2. **Design Patterns** — Creational, structural, behavioral, framework-specific
> 3. **Coding Conventions** — Naming, file org, imports, error handling, docs
> 4. **Features** — User-facing capabilities, implementation recipes, extension points
> 5. **Testing** — Test framework, organization, coverage, mocking strategy
> 6. **Operations** — Deployment, CI/CD, logging, monitoring, environment management
> 7. **All of the above**
>
> **Drives:** Which agents to launch. See mapping in analysis-dimensions.md.

### Q1.3: Depth Level

> **How deep should the analysis go?**
>
> 1. **Surface scan** — High-level overview, key patterns only (faster)
> 2. **Standard depth** — Comprehensive investigation of selected dimensions
> 3. **Exhaustive** — Deep investigation including edge cases, anti-patterns, ADRs
>
> **Drives:** Agent prompt specificity, number of files read, level of evidence required.

### Q1.4: Region Focus

> **Any specific areas of the codebase you want to prioritize?**
>
> 1. **No preference** — Investigate broadly across the entire repo
> 2. **Specific directories** — *(user provides paths like `src/api/`, `lib/core/`)*
> 3. **Specific features** — *(user describes features to focus on)*
> 4. **Recent changes** — Focus on what's been modified recently
>
> **Drives:** Agent scope constraints, file reading priority.

### Q1.5: Specific Questions

> **Do you have specific questions about this codebase?**
>
> Examples:
> - "How does authentication work?"
> - "What's the data model for X?"
> - "Why is Y structured this way?"
>
> *(Open-ended. Answers are injected as user-specific questions into agent prompts.)*
>
> **Drives:** Custom investigation targets for relevant agents.

### Q1.6: Agent Plan Confirmation

> **Based on your selections, here's the investigation plan:**
>
> *[Present which agents will be launched, what each will investigate, and estimated scope]*
>
> 1. **Looks good — proceed** — Launch the planned agents
> 2. **Adjust the plan** — *(user modifies agent selection or scope)*
> 3. **Analyze everything (autonomous mode)** — Launch all 5 agents, skip remaining checkpoints, generate full output package
> 4. **Skip interviews going forward** — Same as autonomous mode
>
> **Drives:** Agent launch configuration. Options 3/4 trigger fast-exit path.

### Fast-Exit Detection

If the user responds with any of these at Q1.6 (or at any point during Checkpoint 1):
- "analyze everything"
- "skip"
- "autonomous"
- "just do it"
- "all of it"

**Trigger fast-exit:** Launch all 5 agents, skip Checkpoints 2 and 3, generate full output package using the autonomous `repo-deep-dive` workflow logic.

---

## Checkpoint 2: Findings Review

Present after Phase 2 agents return and findings are synthesized. The user sees consolidated findings organized by their stated interests.

### Q2.1: Per-Finding Triage

> For each finding presented (using [findings-presentation.md](./findings-presentation.md) format):
>
> - **Keep** — Include in final output as-is
> - **Skip** — Exclude from final output
> - **Dig deeper** — Investigate further (triggers [deep-dive-session.md](../workflows/deep-dive-session.md))
>
> *(User can triage individually or in bulk: "keep all architecture findings, skip testing")*
>
> **Drives:** Which findings appear in output, which trigger deep-dive sessions.

### Q2.2: Accuracy Check

> **Do any of these findings seem wrong or misleading?**
>
> 1. **Everything looks accurate** — Proceed with kept findings
> 2. **Some corrections needed** — *(user identifies specific issues)*
>
> **Drives:** Finding corrections before output generation.

### Q2.3: Gap Identification

> **Is anything missing that you expected to see?**
>
> 1. **No gaps** — Coverage is sufficient
> 2. **Missing areas** — *(user describes what's missing)*
>
> **Drives:** Additional targeted investigation if gaps are identified. New findings go through triage.

### Q2.4: Depth Requests

> **Any findings you want explored at a different depth than originally requested?**
>
> 1. **Current depth is fine** — Proceed
> 2. **Go deeper on specific findings** — *(treated as "dig deeper" triage)*
> 3. **Simplify some findings** — *(user identifies over-detailed areas)*
>
> **Drives:** Deep-dive sessions or simplification in output generation.

---

## Checkpoint 3: Output Shaping

Present after all findings are finalized (triage complete, deep-dives done). The user shapes the final output before generation.

### Q3.1: Output Emphasis

> **What should the output emphasize?**
>
> 1. **Balanced** — Equal weight across all kept findings
> 2. **Architecture-heavy** — Prioritize system design and component boundaries
> 3. **Pattern-heavy** — Prioritize design patterns and implementation recipes
> 4. **Convention-heavy** — Prioritize naming, style, and coding standards
> 5. **Custom emphasis** — *(user specifies)*
>
> **Drives:** Relative length and detail of output sections.

### Q3.2: Naming Preferences

> **Any naming preferences for the output?**
>
> 1. **Default** — `repo-knowledge-{repo-name}/`
> 2. **Custom name** — *(user provides preferred name)*
>
> **Drives:** Output directory and SKILL.md naming.

### Q3.3: Exclusions

> **Anything to explicitly exclude from the output?**
>
> 1. **No exclusions** — Include all kept findings
> 2. **Exclude specific items** — *(user lists items, sections, or topics to omit)*
> 3. **Exclude sensitive information** — Remove internal URLs, API keys, team names, etc.
>
> **Drives:** Output filtering and redaction.

### Q3.4: Output Format

> **What output format do you want?**
>
> 1. **Full skill package** — Complete directory with SKILL.md, references, templates
> 2. **Single summary document** — One comprehensive markdown file
> 3. **Both** — Skill package + summary document
>
> **Drives:** Output generation workflow (skill package, single doc, or both).

### Q3.5: Final Confirmation

> **Ready to generate the output with these preferences?**
>
> *[Present summary of: kept findings count, emphasis, naming, exclusions, format]*
>
> 1. **Generate it** — Proceed to output generation
> 2. **Adjust something** — *(user modifies preferences)*
>
> **Drives:** Final go/no-go for output generation.
