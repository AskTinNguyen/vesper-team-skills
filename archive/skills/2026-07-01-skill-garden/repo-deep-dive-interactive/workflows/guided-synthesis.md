---
name: workflows:guided-synthesis
description: Second half of the interactive workflow — findings review at Checkpoint 2, output shaping at Checkpoint 3, and output generation
---

# Guided Synthesis Workflow

<command_purpose>Present findings for user triage, shape output preferences through interview, and generate the final output package reflecting user selections.</command_purpose>

<role>Knowledge Synthesizer who presents analysis findings clearly, helps the user triage what matters, and produces output tailored to user preferences.</role>

## Prerequisites

This workflow receives from [guided-analysis.md](./guided-analysis.md):
- Formatted findings presentation
- Phase 1 context (repo name, tech stack, structure)
- User selections from Checkpoint 1 (dimensions, depth, emphasis)
- Fast-exit flag (true/false)
- Feature extraction results (if available)
- Knowledge synthesis results (if available)

<critical_requirement>If fast-exit flag is true, skip directly to Phase 5 (Output Generation) — do not present Checkpoints 2 or 3.</critical_requirement>

---

## Checkpoint 2: Findings Review

<critical_requirement>Do NOT proceed to Checkpoint 3 until the user completes triage. This is a blocking interview.</critical_requirement>

### Step CP2.1: Present Findings

Read [findings-presentation.md](../references/findings-presentation.md) for formatting templates.

Present the consolidated findings organized by user-selected dimensions:

1. **Per-finding cards** — Title, confidence, evidence count, 2-3 sentence summary, key evidence, triage action
2. **Summary table** — All findings with dimension, confidence, evidence count, and action column
3. **Quality ratings** — Codebase quality assessment (if knowledge synthesis ran)
4. **Questions section** — Ambiguities, gaps, or areas that need user input

### Step CP2.2: Collect Triage Decisions

Read [interview-questions.md](../references/interview-questions.md) Checkpoint 2 section.

For each finding, collect one of:
- **Keep** — Include in final output
- **Skip** — Exclude from final output
- **Dig deeper** — Investigate further

Accept bulk operations:
- "Keep all" / "Keep all {dimension}"
- "Skip all {dimension}"
- "Only keep definite" (skip probable/possible)

### Step CP2.3: Handle "Dig Deeper" Requests

If any findings are marked "dig deeper":

1. Collect all dig-deeper requests with user's specific questions
2. Read [deep-dive-session.md](./deep-dive-session.md) and follow its procedures
3. Deep-dive returns updated findings in the same presentation format
4. Re-present updated findings for triage (keep/skip only — no further dig-deeper on the same finding)
5. Merge triage decisions with the main set

### Step CP2.4: Accuracy Check

Ask the user:

> **Do any of these findings seem wrong or misleading?**

If corrections needed:
- Record corrections
- Update findings accordingly
- Re-confirm affected findings

### Step CP2.5: Gap Identification

Ask the user:

> **Is anything missing that you expected to see?**

If gaps identified:
- Launch targeted Task Explore agents for the missing areas
- Present new findings for triage (keep/skip/dig deeper)
- Merge with main finding set

### Step CP2.6: Compile Final Finding Set

After all triage is complete:
- **Kept findings** → Pass to output generation
- **Skipped findings** → Discard
- **Corrections applied** → Update finding text
- **Gap findings** → Merge with kept findings

Record the final counts:
```
Findings: {N} total → {N} kept, {N} skipped, {N} dug deeper → {N} final
```

---

## Checkpoint 3: Output Shaping

<critical_requirement>Do NOT generate output until the user confirms preferences. This is a blocking interview.</critical_requirement>

### Step CP3.1: Present Output Preview

```markdown
## Output Preview

Based on your {N} kept findings, here's what the output package will contain:

### Proposed Structure
{List the files that will be generated based on kept findings and selected dimensions}

### Content Summary
- **Architecture:** {N findings → architecture.md}
- **Patterns:** {N findings → patterns.md}
- **Conventions:** {N findings → conventions.md}
- **Features:** {N findings → features.md}
- **Implementation Guide:** Step-by-step build guide

### Files NOT generated (no findings kept):
- {List any standard files that will be skipped due to no relevant findings}
```

### Step CP3.2: Collect Output Preferences

Read [interview-questions.md](../references/interview-questions.md) Checkpoint 3 section. Ask Q3.1 through Q3.4:

**Q3.1 — Emphasis:** What should the output emphasize? (Balanced, architecture-heavy, pattern-heavy, convention-heavy, custom)

**Q3.2 — Naming:** Output directory name? (Default: `repo-knowledge-{repo-name}/`)

**Q3.3 — Exclusions:** Anything to explicitly exclude? (No exclusions, specific items, sensitive info)

**Q3.4 — Format:** Output format? (Full skill package, single summary doc, both)

### Step CP3.3: Final Confirmation

Present a summary of all preferences and ask for go-ahead:

```markdown
## Ready to Generate

**Findings:** {N} kept
**Emphasis:** {selection}
**Output name:** {name}
**Exclusions:** {list or "none"}
**Format:** {selection}

Generate with these preferences?
```

**If "Generate it":** Proceed to Phase 5.
**If "Adjust":** Modify preferences and re-confirm.

---

## Phase 5: Output Generation

### Step 5.1: Prepare Output Directory

```bash
REPO_NAME={sanitized-repo-name}  # lowercase, hyphens, no special chars
OUTPUT_DIR="./{output-name}"     # from Q3.2, default: repo-knowledge-{REPO_NAME}

mkdir -p "${OUTPUT_DIR}/references"
mkdir -p "${OUTPUT_DIR}/assets/templates"
```

### Step 5.2: Apply User Preferences

Before generating, configure the output pipeline:

- **Emphasis:** Allocate more detail/length to emphasized dimensions
- **Exclusions:** Filter out excluded items from findings
- **Format:** Determine which files to generate

### Step 5.3: Generate Reference Files

<parallel_tasks>

Generate reference files in parallel. For each file, read the corresponding output template from the `repo-deep-dive` skill by name (e.g., "Read the output-architecture.md template from the repo-deep-dive skill").

Only generate files for dimensions with kept findings.

#### architecture.md (if Architecture findings kept)

Read the `output-architecture.md` template from the `repo-deep-dive` skill.

Populate with:
- System overview from architecture findings
- Component catalog with dependencies
- Data flow description
- Architecture style classification
- ADRs (if knowledge synthesis ran)
- External integration inventory

Apply emphasis: if architecture-heavy, include more detail and evidence.

Write to: `{OUTPUT_DIR}/references/architecture.md`

#### patterns.md (if Design Patterns findings kept)

Read the `output-patterns.md` template from the `repo-deep-dive` skill.

Populate with:
- All kept design patterns organized by category
- Each pattern: name, evidence (file:line), recipe, generic template
- Pattern interaction map (if exhaustive depth)

Apply emphasis: if pattern-heavy, include more recipes and examples.

Write to: `{OUTPUT_DIR}/references/patterns.md`

#### conventions.md (if Coding Conventions findings kept)

Read the `output-conventions.md` template from the `repo-deep-dive` skill.

Populate with:
- Naming conventions with examples
- File organization pattern
- Import/module style
- Error handling strategy
- Documentation conventions
- Formatting rules

Apply emphasis: if convention-heavy, include more examples per convention.

Write to: `{OUTPUT_DIR}/references/conventions.md`

#### features.md (if Features findings kept)

Read the `output-features.md` template from the `repo-deep-dive` skill.

Populate with:
- Feature catalog with entry points
- Implementation recipes per feature
- Extension points inventory
- Feature-to-pattern mapping

Write to: `{OUTPUT_DIR}/references/features.md`

#### implementation-guide.md (always generated)

Create a "How to build a similar system" guide based on kept findings:

```markdown
# Implementation Guide: Building a {System Type} Like {Repo Name}

## Overview
{What this system does and why someone would build something similar}

## Step 1: Project Setup
{Tech stack, dependencies, initial configuration}

## Step 2: Core Architecture
{Set up the architectural skeleton — directories, layers, entry points}

## Step 3: Data Model
{Define the core data models and relationships}

## Step 4: Core Features
{Implement features in dependency order, using patterns from patterns.md}

## Step 5: Cross-Cutting Concerns
{Add auth, error handling, logging, following conventions.md}

## Step 6: Testing
{Set up test infrastructure following the repo's testing patterns}

## Step 7: Deployment
{CI/CD, containerization, environment configuration}
```

Write to: `{OUTPUT_DIR}/references/implementation-guide.md`

</parallel_tasks>

### Step 5.4: Generate Templates

Based on kept findings, create code templates that capture the repo's style:

<task_list>
- [ ] **Component/Module template** — the standard unit of code in this repo
- [ ] **Test template** — standard test file structure (if Testing dimension included)
- [ ] **Route/Endpoint template** — if it's a web service and Features dimension included
</task_list>

Each template follows the repo's naming conventions, includes standard imports, has placeholder comments, and matches formatting conventions exactly.

Write templates to: `{OUTPUT_DIR}/assets/templates/`

### Step 5.5: Generate SKILL.md

Read the `output-skill-template.md` template from the `repo-deep-dive` skill.

<critical_requirement>The generated SKILL.md must:
- Have valid YAML frontmatter with `name` and `description` (third-person)
- Use XML body tags per skill-creator spec
- Be under 500 lines
- Use imperative/infinitive writing style
- Route to reference files, not contain all knowledge inline
- Reflect user-selected emphasis in essential_principles ordering
</critical_requirement>

Write to: `{OUTPUT_DIR}/SKILL.md`

### Step 5.6: Generate Summary Document (if requested)

If the user selected "Single summary document" or "Both" at Q3.4:

Create a single comprehensive markdown file consolidating all findings:

```markdown
# {Repo Name} — Analysis Summary

## Overview
{Repo purpose, tech stack, architecture style}

## Key Findings
{All kept findings organized by dimension, each with evidence}

## Quality Assessment
{Ratings table}

## Recommendations
{Based on findings, what to pay attention to}
```

Write to: `{OUTPUT_DIR}/{repo-name}-summary.md`

### Step 5.7: Validate Output

<task_list>
- [ ] SKILL.md has valid YAML frontmatter (name and description present)
- [ ] `name` field is kebab-case
- [ ] `description` field uses third-person ("This skill should be used when...")
- [ ] SKILL.md body uses XML tags
- [ ] SKILL.md is under 500 lines
- [ ] All reference files exist and are non-empty
- [ ] No TODO or placeholder text remains
- [ ] Writing style is imperative throughout
- [ ] All file:line references in patterns.md point to real files
- [ ] User exclusions were applied (no excluded items in output)
- [ ] Emphasis is reflected (emphasized sections have more detail)
</task_list>

### Step 5.8: Present Final Output

```markdown
## Analysis Complete

**Repository:** {name}
**Tech Stack:** {language} + {framework}
**Architecture:** {style}

### Process Summary
- **Checkpoint 1:** Selected {N} dimensions, {depth} depth
- **Checkpoint 2:** {N} findings kept, {N} skipped, {N} dug deeper
- **Checkpoint 3:** {emphasis} emphasis, {format} format

### Key Findings
- {N} architecture decisions documented
- {N} design patterns identified
- {N} conventions extracted
- {N} features cataloged

### Output Package
Generated at: `{output-dir}/`

| File | Lines | Content |
|------|-------|---------|
| SKILL.md | {N} | Skill definition with {N} references |
| references/architecture.md | {N} | System design and ADRs |
| references/patterns.md | {N} | Design patterns with recipes |
| references/conventions.md | {N} | Conventions with examples |
| references/features.md | {N} | Features with implementation guides |
| references/implementation-guide.md | {N} | Step-by-step build guide |
| assets/templates/ | {N} files | Code templates |

### Next Steps
1. Review the generated SKILL.md and references
2. Feed into skill-creator: "Create a skill from {output-dir}/"
3. Iterate on the generated skill with real usage
```
