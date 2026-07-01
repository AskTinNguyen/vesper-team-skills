# Agent Prompt Templates

5 agent prompt templates for Phase 2 parallel analysis. Each prompt is a self-contained `Task Explore` instruction with placeholders:

- `{repo-path}` — Absolute path to the repository
- `{phase1-context}` — Phase 1 reconnaissance summary (~200 words)
- `{user-specific-questions}` — Questions from Checkpoint 1 Q1.5 (may be empty)
- `{scope-constraints}` — Region focus from Checkpoint 1 Q1.4 (may be "no constraints")
- `{depth-level}` — One of: surface, standard, exhaustive

---

## Agent 1: Architecture Mapper

```
Task Explore("Analyze the architecture of {repo-path}.

Context: {phase1-context}

Scope constraints: {scope-constraints}
Depth level: {depth-level}

Investigate:
1. Component/module boundaries — what are the top-level directories and what does each own?
2. Dependency graph — which modules import from which? Map internal dependencies.
3. Data flow — how does data enter the system, get processed, and exit?
4. Layer architecture — is it MVC, hexagonal, clean architecture, microservices, monolith?
5. External integrations — what third-party services, APIs, or databases are used?

User-specific questions to address:
{user-specific-questions}

For each finding, include file:line references.

Output a structured report with sections:
- System Overview (2-3 sentences)
- Component Catalog (name, purpose, key files, dependencies)
- Data Flow Diagram (text-based)
- Architecture Style classification
- External Integrations list
- Answers to user-specific questions (if any)")
```

**Required for dimensions:** Architecture, Features

---

## Agent 2: API Surface Analyzer

```
Task Explore("Analyze the API surface and interface layer of {repo-path}.

Context: {phase1-context}

Scope constraints: {scope-constraints}
Depth level: {depth-level}

Investigate:
1. Routes/endpoints — list all HTTP routes, gRPC services, or CLI commands
2. Middleware/interceptors — what processing happens before handlers?
3. Authentication/authorization patterns — how are users verified?
4. Request/response shapes — what DTOs, serializers, or schemas are used?
5. Error response patterns — how are errors communicated to clients?
6. API versioning strategy (if any)

User-specific questions to address:
{user-specific-questions}

For each finding, include file:line references.

Output a structured report with sections:
- Endpoint Catalog (method, path, handler, auth required)
- Middleware Stack (order and purpose)
- Auth Pattern description
- Request/Response Patterns
- Error Handling Strategy
- Answers to user-specific questions (if any)")
```

**Required for dimensions:** Features, Operations

---

## Agent 3: Pattern Detective

```
Task Explore("Identify design patterns used in {repo-path}.

Context: {phase1-context}

Scope constraints: {scope-constraints}
Depth level: {depth-level}

Read the pattern-catalog.md reference from the repo-deep-dive skill for the full list of patterns to look for.

Investigate:
1. Creational patterns — Factory, Builder, Singleton, DI containers
2. Structural patterns — Adapter, Decorator, Facade, Proxy, Plugin systems
3. Behavioral patterns — Observer/Event, Strategy, Command, State machines
4. Architectural patterns — Repository, Unit of Work, CQRS, Event Sourcing
5. Framework-specific patterns — middleware chains, hooks, mixins, concerns

User-specific questions to address:
{user-specific-questions}

For EACH pattern found:
- Name the pattern
- Cite the file:line where it's implemented
- Explain how it's used in this codebase
- Rate confidence: definite / probable / possible

Output a structured report organized by pattern category.")
```

**Required for dimensions:** Design Patterns

---

## Agent 4: Convention Extractor

```
Task Explore("Extract coding conventions from {repo-path}.

Context: {phase1-context}

Scope constraints: {scope-constraints}
Depth level: {depth-level}

Investigate:
1. Naming conventions — files, directories, classes, functions, variables, constants
2. File organization — how are files grouped? By feature, by type, by layer?
3. Import/module patterns — absolute vs relative, barrel files, index files
4. Error handling — try/catch patterns, Result types, error classes, logging
5. Documentation style — JSDoc, docstrings, inline comments, README per module
6. Code formatting — indentation, line length, bracket style (check linter configs)
7. Git conventions — commit message format, branch naming (check CONTRIBUTING.md)

User-specific questions to address:
{user-specific-questions}

For each convention, provide 3+ examples with file:line references.

Output a structured report with sections:
- Naming Conventions (with examples)
- File Organization Pattern
- Import Style
- Error Handling Strategy
- Documentation Style
- Formatting Rules
- Answers to user-specific questions (if any)")
```

**Required for dimensions:** Coding Conventions, Operations

---

## Agent 5: Test Pattern Analyzer

```
Task Explore("Analyze testing patterns in {repo-path}.

Context: {phase1-context}

Scope constraints: {scope-constraints}
Depth level: {depth-level}

Investigate:
1. Test framework(s) — what's used? (Jest, pytest, RSpec, Go testing, etc.)
2. Test organization — mirror source? Separate tree? Co-located?
3. Test types present — unit, integration, e2e, snapshot, property-based
4. Fixture/factory patterns — how is test data created?
5. Mocking strategy — what's mocked and how?
6. Coverage configuration — is there a coverage threshold?
7. CI test pipeline — how are tests run in CI?
8. Test naming conventions — describe blocks, test descriptions

User-specific questions to address:
{user-specific-questions}

For each finding, include file:line references.

Output a structured report with sections:
- Test Stack (framework, assertion library, mock library)
- Test Organization (directory structure, naming)
- Test Types Present (with example file paths)
- Data Setup Patterns (fixtures, factories, builders)
- Mocking Strategy
- CI Pipeline description
- Answers to user-specific questions (if any)")
```

**Required for dimensions:** Testing

---

## Agent Selection Logic

Map user-selected dimensions to agents:

```
dimensions_to_agents = {
  "Architecture":       [Agent 1],
  "Design Patterns":    [Agent 3],
  "Coding Conventions": [Agent 4],
  "Features":           [Agent 1, Agent 2],
  "Testing":            [Agent 5],
  "Operations":         [Agent 2, Agent 4]
}

# De-duplicate: if user selects Architecture + Features,
# Agent 1 appears twice — launch only once.
selected_agents = unique(flatten(dimensions_to_agents[d] for d in user_selections))
```

## Prompt Customization by Depth Level

Adjust agent instructions based on depth level:

| Depth | Instruction Modifier |
|-------|---------------------|
| **Surface** | "Focus on the top 3-5 most prominent findings. Read only Tier 1-2 files. Prioritize breadth over depth." |
| **Standard** | "Investigate comprehensively. Read Tiers 1-3 files. Provide thorough evidence for each finding." |
| **Exhaustive** | "Investigate exhaustively including edge cases, anti-patterns, and subtle conventions. Read Tiers 1-4 files. Document architecture decision records for significant choices." |
