---
name: workflows:generate-skill-package
description: Produce a skill-creator-compatible output package from repo analysis findings
---

# Generate Skill Package Workflow

<command_purpose>Transform repo analysis findings into a complete skill directory formatted for consumption by the skill-creator skill.</command_purpose>

<role>Skill Architect specializing in packaging domain knowledge into modular, reusable skill definitions</role>

## Prerequisites

This workflow requires analysis data from at least one of:
- Full analysis (Phase 1-4 of [full-analysis.md](./full-analysis.md))
- Architecture focus ([architecture-focus.md](./architecture-focus.md))
- Pattern extraction ([pattern-extraction.md](./pattern-extraction.md))

If no analysis has been performed, redirect to full-analysis workflow first.

## Step 1: Prepare Output Directory

```bash
# Determine output location
REPO_NAME={repo-name}  # Sanitized: lowercase, hyphens, no special chars
OUTPUT_DIR="./repo-knowledge-${REPO_NAME}"

mkdir -p "${OUTPUT_DIR}/references"
mkdir -p "${OUTPUT_DIR}/assets/templates"
```

## Step 2: Generate Reference Files

<parallel_tasks>

Generate all reference files in parallel. Read each output template before writing.

### 2.1: Generate architecture.md

Read template: [output-architecture.md](../references/output-architecture.md)

Populate with:
- System overview from architecture analysis
- Component catalog with dependencies
- Data flow description
- Architecture style classification
- ADRs from synthesis phase
- External integration inventory

Write to: `{OUTPUT_DIR}/references/architecture.md`

### 2.2: Generate patterns.md

Read template: [output-patterns.md](../references/output-patterns.md)

Populate with:
- All identified design patterns organized by category
- Each pattern includes: name, evidence (file:line), recipe, generic template
- Pattern interaction map
- Signature patterns highlighted

Write to: `{OUTPUT_DIR}/references/patterns.md`

### 2.3: Generate conventions.md

Read template: [output-conventions.md](../references/output-conventions.md)

Populate with:
- Naming conventions with examples
- File organization pattern
- Import/module style
- Error handling strategy
- Documentation conventions
- Formatting rules
- Git conventions (if detected)

Write to: `{OUTPUT_DIR}/references/conventions.md`

### 2.4: Generate features.md

Read template: [output-features.md](../references/output-features.md)

Populate with:
- Feature catalog with entry points
- Implementation recipes per feature
- Extension points inventory
- Feature-to-pattern mapping

Write to: `{OUTPUT_DIR}/references/features.md`

### 2.5: Generate implementation-guide.md

Create a "How to build a similar system" guide:

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

## Step 3: Generate Templates

Based on analysis, create code templates that capture the repo's style:

### Template Selection

Identify the most commonly created file types and create templates:

<task_list>
- [ ] **Component/Module template** — the standard unit of code in this repo
- [ ] **Test template** — standard test file structure
- [ ] **Config template** — if the repo has repeating config patterns
- [ ] **Route/Endpoint template** — if it's a web service
- [ ] **Model/Entity template** — if it has a data layer
</task_list>

Each template should:
- Follow the repo's naming conventions
- Include standard imports for that file type
- Have placeholder comments where custom code goes
- Match the formatting conventions exactly

Write templates to: `{OUTPUT_DIR}/assets/templates/`

## Step 4: Generate SKILL.md

Read template: [output-skill-template.md](../references/output-skill-template.md)

<critical_requirement>The generated SKILL.md must:
- Have valid YAML frontmatter with `name` and `description` (third-person)
- Use XML body tags per skill-creator spec
- Be under 500 lines
- Use imperative/infinitive writing style
- Route to reference files, not contain all knowledge inline
</critical_requirement>

### SKILL.md Structure

```yaml
---
name: {repo-name}-patterns
description: This skill should be used when building systems similar to {repo-name}. It provides architecture patterns, design conventions, and implementation recipes extracted from the {repo-name} codebase ({tech-stack}). Triggers on requests involving {key-domains}.
---
```

```xml
<objective>
Apply {repo-name} architecture patterns and conventions when building
similar {system-type} systems using {tech-stack}.
</objective>

<essential_principles>
{Top 5-7 most important conventions and patterns — the ones that define
this codebase's character. Keep concise, link to references for details.}
</essential_principles>

<intake>
{Routing menu for the skill — what aspects can the user ask about?}
</intake>

<routing>
{Table mapping user intents to reference files}
</routing>

<quick_reference>
{Most frequently needed conventions — naming, file structure, key patterns}
</quick_reference>

<reference_index>
{Table of all reference files with descriptions}
</reference_index>

<success_criteria>
{How to know if the pattern is being applied correctly}
</success_criteria>
```

Write to: `{OUTPUT_DIR}/SKILL.md`

## Step 5: Validate Output

<task_list>
- [ ] SKILL.md has valid YAML frontmatter (parse with `grep -A2 '---'`)
- [ ] `name` field is present and kebab-case
- [ ] `description` field uses third-person ("This skill should be used when...")
- [ ] SKILL.md body uses XML tags
- [ ] SKILL.md is under 500 lines (`wc -l`)
- [ ] All reference files exist and are non-empty
- [ ] At least 1 template exists in assets/templates/
- [ ] All file:line references in patterns.md point to real files
- [ ] No TODO or placeholder text remains
- [ ] Writing style is imperative throughout
</task_list>

## Step 6: Present Output

```markdown
## Skill Package Generated

**Output:** `repo-knowledge-{name}/`

### Contents
- `SKILL.md` — {line_count} lines, {pattern_count} patterns referenced
- `references/architecture.md` — System design and ADRs
- `references/patterns.md` — {N} design patterns with recipes
- `references/conventions.md` — {N} conventions with examples
- `references/features.md` — {N} features with implementation guides
- `references/implementation-guide.md` — Step-by-step build guide
- `assets/templates/` — {N} code templates

### To Create a Skill From This
Feed this output into skill-creator:
> "Create a skill from repo-knowledge-{name}/"

### To Use Directly
Copy to your skills directory:
> cp -r repo-knowledge-{name} ~/.claude/skills/{name}-patterns

### Manual Review Recommended
- Verify architecture.md accurately represents the system
- Check that pattern recipes are generalizable
- Confirm conventions match your understanding
- Remove any sensitive information (API keys, internal URLs)
```
