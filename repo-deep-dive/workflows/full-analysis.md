---
name: workflows:full-analysis
description: End-to-end 5-phase repo analysis orchestration with parallel agent spawning
---

# Full Analysis Workflow

<command_purpose>Perform a comprehensive 5-phase analysis of a repository, extracting architecture, patterns, conventions, and features into a skill-creator-compatible output package.</command_purpose>

<role>Senior Software Archaeologist with expertise in reverse-engineering codebases, identifying architectural patterns, and documenting system knowledge</role>

## Phase 1: Repo Ingestion

<critical_requirement>Complete Phase 1 fully before launching Phase 2 agents. The reconnaissance data informs what each agent investigates.</critical_requirement>

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

Execute the bundled reconnaissance script to get initial structure:

```bash
bash {skill-path}/scripts/analyze-repo.sh {repo-path}
```

This produces:
- Directory tree (depth 3)
- File type distribution
- Config file inventory
- Entry point candidates

### Step 1.3: Read Priority Files

Read [analysis-checklist.md](../references/analysis-checklist.md) for the full priority list. At minimum, read these in order:

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

Read [tech-stack-detection.md](../references/tech-stack-detection.md) and identify:

- Primary language(s)
- Framework(s) and version(s)
- Build system / task runner
- Test framework(s)
- Database / data layer
- Deployment target (Docker, serverless, bare metal, etc.)

Record findings as a structured summary to pass to Phase 2 agents.

### Step 1.5: Prepare Phase 2 Context

Create a brief context document (~200 words) summarizing:
- Repo name and purpose (from README)
- Tech stack detected
- Directory structure overview
- Key entry points identified
- Estimated codebase size (file count, LOC estimate)

This context is passed to all Phase 2 agents.

---

## Phase 2: Parallel Architecture Deep Dive

<parallel_tasks>

Launch ALL 5 agents simultaneously. Each agent receives the Phase 1 context summary plus specific instructions.

### Agent 1: Architecture Mapper

```
Task Explore("Analyze the architecture of {repo-path}.

Context: {phase1-context}

Investigate:
1. Component/module boundaries — what are the top-level directories and what does each own?
2. Dependency graph — which modules import from which? Map internal dependencies.
3. Data flow — how does data enter the system, get processed, and exit?
4. Layer architecture — is it MVC, hexagonal, clean architecture, microservices, monolith?
5. External integrations — what third-party services, APIs, or databases are used?

For each finding, include file:line references.

Output a structured report with sections:
- System Overview (2-3 sentences)
- Component Catalog (name, purpose, key files, dependencies)
- Data Flow Diagram (text-based)
- Architecture Style classification
- External Integrations list")
```

### Agent 2: API Surface Analyzer

```
Task Explore("Analyze the API surface and interface layer of {repo-path}.

Context: {phase1-context}

Investigate:
1. Routes/endpoints — list all HTTP routes, gRPC services, or CLI commands
2. Middleware/interceptors — what processing happens before handlers?
3. Authentication/authorization patterns — how are users verified?
4. Request/response shapes — what DTOs, serializers, or schemas are used?
5. Error response patterns — how are errors communicated to clients?
6. API versioning strategy (if any)

For each finding, include file:line references.

Output a structured report with sections:
- Endpoint Catalog (method, path, handler, auth required)
- Middleware Stack (order and purpose)
- Auth Pattern description
- Request/Response Patterns
- Error Handling Strategy")
```

### Agent 3: Pattern Detective

```
Task Explore("Identify design patterns used in {repo-path}.

Context: {phase1-context}

Read [pattern-catalog.md] for the full list of patterns to look for.

Investigate:
1. Creational patterns — Factory, Builder, Singleton, DI containers
2. Structural patterns — Adapter, Decorator, Facade, Proxy, Plugin systems
3. Behavioral patterns — Observer/Event, Strategy, Command, State machines
4. Architectural patterns — Repository, Unit of Work, CQRS, Event Sourcing
5. Framework-specific patterns — middleware chains, hooks, mixins, concerns

For EACH pattern found:
- Name the pattern
- Cite the file:line where it's implemented
- Explain how it's used in this codebase
- Rate confidence: definite / probable / possible

Output a structured report organized by pattern category.")
```

### Agent 4: Convention Extractor

```
Task Explore("Extract coding conventions from {repo-path}.

Context: {phase1-context}

Investigate:
1. Naming conventions — files, directories, classes, functions, variables, constants
2. File organization — how are files grouped? By feature, by type, by layer?
3. Import/module patterns — absolute vs relative, barrel files, index files
4. Error handling — try/catch patterns, Result types, error classes, logging
5. Documentation style — JSDoc, docstrings, inline comments, README per module
6. Code formatting — indentation, line length, bracket style (check linter configs)
7. Git conventions — commit message format, branch naming (check CONTRIBUTING.md)

For each convention, provide 3+ examples with file:line references.

Output a structured report with sections:
- Naming Conventions (with examples)
- File Organization Pattern
- Import Style
- Error Handling Strategy
- Documentation Style
- Formatting Rules")
```

### Agent 5: Test Pattern Analyzer

```
Task Explore("Analyze testing patterns in {repo-path}.

Context: {phase1-context}

Investigate:
1. Test framework(s) — what's used? (Jest, pytest, RSpec, Go testing, etc.)
2. Test organization — mirror source? Separate tree? Co-located?
3. Test types present — unit, integration, e2e, snapshot, property-based
4. Fixture/factory patterns — how is test data created?
5. Mocking strategy — what's mocked and how?
6. Coverage configuration — is there a coverage threshold?
7. CI test pipeline — how are tests run in CI?
8. Test naming conventions — describe blocks, test descriptions

For each finding, include file:line references.

Output a structured report with sections:
- Test Stack (framework, assertion library, mock library)
- Test Organization (directory structure, naming)
- Test Types Present (with example file paths)
- Data Setup Patterns (fixtures, factories, builders)
- Mocking Strategy
- CI Pipeline description")
```

</parallel_tasks>

### Phase 2 Synthesis

After all 5 agents return:

<task_list>
- [ ] Collect all 5 agent reports
- [ ] Identify overlapping findings and consolidate
- [ ] Flag any contradictions between agents
- [ ] Create a unified "repo profile" combining all findings
- [ ] Note gaps — areas none of the agents covered sufficiently
</task_list>

---

## Phase 3: Feature Extraction

<thinking>With architecture and patterns understood, now identify the discrete features this system implements and how each is built.</thinking>

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

For each feature, distill a "recipe" — a generalized step-by-step for implementing a similar feature:

```
Recipe: {Feature Name}
1. Create {model/entity} with fields: ...
2. Add {route/endpoint} mapping to ...
3. Implement {handler/controller} with pattern: ...
4. Add {validation/auth} using: ...
5. Write tests: {unit for ..., integration for ...}
```

### Step 3.4: Document Extension Points

Identify where the system is designed to be extended:
- Plugin/hook systems
- Configuration-driven behavior
- Abstract base classes / interfaces
- Event emitters / pub-sub channels
- Middleware registration points

---

## Phase 4: Knowledge Synthesis

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

Note patterns that are conspicuously absent — things the codebase deliberately does NOT do:
- No service objects? (prefers fat models)
- No ORM? (raw SQL preferred)
- No DI container? (manual injection)
- No global state?

### Step 4.3: Consolidate Conventions

Merge the convention extractor's findings with patterns observed across all phases into a unified conventions document.

### Step 4.4: Quality Assessment

Rate the codebase on:
- **Consistency** (1-5): How consistently are patterns applied?
- **Documentation** (1-5): How well is the code documented?
- **Test Coverage** (1-5): How thorough is the test suite?
- **Separation of Concerns** (1-5): How clean are the boundaries?
- **Extensibility** (1-5): How easy is it to add new features?

---

## Phase 5: Generate Output Package

Read [generate-skill-package.md](./generate-skill-package.md) and follow its procedures to produce the final output.

The output directory is: `repo-knowledge-{repo-name}/`

<critical_requirement>All generated files must use imperative/infinitive writing style, include file:line evidence, and follow skill-creator formatting conventions (YAML frontmatter, XML body tags where applicable).</critical_requirement>

### Completion Checklist

<task_list>
- [ ] `repo-knowledge-{name}/SKILL.md` exists with valid frontmatter
- [ ] `repo-knowledge-{name}/references/architecture.md` is populated
- [ ] `repo-knowledge-{name}/references/patterns.md` is populated
- [ ] `repo-knowledge-{name}/references/conventions.md` is populated
- [ ] `repo-knowledge-{name}/references/features.md` is populated
- [ ] `repo-knowledge-{name}/references/implementation-guide.md` is populated
- [ ] At least 1 template in `assets/templates/`
- [ ] Every pattern has file:line evidence
- [ ] SKILL.md is under 500 lines
- [ ] Output validates against skill-creator expectations
</task_list>

### Final Report

Present to the user:

```markdown
## Repo Deep Dive Complete

**Repository:** {name}
**Tech Stack:** {language} + {framework}
**Architecture:** {style}

### Key Findings
- {N} design patterns identified
- {N} conventions extracted
- {N} features cataloged
- {N} ADRs created

### Output Package
Generated at: `repo-knowledge-{name}/`

### Next Steps
1. Review the generated SKILL.md and references
2. Feed into skill-creator: "Create a skill from repo-knowledge-{name}/"
3. Iterate on the generated skill with real usage
```
