# Analysis Dimensions

User-facing menu of 6 analysis areas. Present this at Checkpoint 1 to help the user select which dimensions to investigate.

## Dimension Overview

| # | Dimension | What It Covers | Why You Might Care | Agents Required |
|---|-----------|---------------|-------------------|-----------------|
| 1 | Architecture | System structure, components, data flow, layers | Understand how pieces fit together | Architecture Mapper |
| 2 | Design Patterns | Creational, structural, behavioral, framework-specific | Extract reusable patterns for similar systems | Pattern Detective |
| 3 | Coding Conventions | Naming, file org, imports, error handling, docs | Match the codebase's style when contributing | Convention Extractor |
| 4 | Features | User-facing capabilities, implementation recipes, extension points | Understand what the system does and how to extend it | Architecture Mapper + API Surface Analyzer |
| 5 | Testing | Framework, organization, coverage, mocking, CI pipeline | Understand test strategy before writing tests | Test Pattern Analyzer |
| 6 | Operations | Deployment, CI/CD, logging, monitoring, environments | Understand how the system runs in production | API Surface Analyzer + Convention Extractor |

---

## 1. Architecture

**What it covers:**
- System type (monolith, microservices, serverless, library)
- Layer architecture (MVC, hexagonal, clean, etc.)
- Component boundaries and ownership
- Dependency direction between layers
- Data flow from request to response
- External integrations (databases, APIs, services)

**Output produced:** `references/architecture.md` — system overview, component catalog, data flow diagram, architecture style classification, ADRs, external integration inventory.

**Primary agent:** Architecture Mapper

---

## 2. Design Patterns

**What it covers:**
- Creational patterns (Factory, Builder, Singleton, DI)
- Structural patterns (Adapter, Decorator, Facade, Proxy, Plugin)
- Behavioral patterns (Observer, Strategy, Command, State machine)
- Architectural patterns (Repository, CQRS, Event Sourcing)
- Framework-specific patterns (middleware, hooks, mixins, concerns)
- Custom domain-specific patterns

**Output produced:** `references/patterns.md` — pattern catalog organized by category, each with name, evidence, recipe, and generic template.

**Primary agent:** Pattern Detective

---

## 3. Coding Conventions

**What it covers:**
- Naming conventions (files, directories, classes, functions, variables, constants)
- File organization (by feature, by type, by layer)
- Import/module patterns (absolute vs relative, barrel files)
- Error handling (try/catch, Result types, error classes, logging)
- Documentation style (JSDoc, docstrings, inline comments)
- Code formatting (indentation, line length, bracket style)
- Git conventions (commit messages, branch naming)

**Output produced:** `references/conventions.md` — naming conventions with examples, file organization pattern, import style, error handling strategy, documentation style, formatting rules.

**Primary agent:** Convention Extractor

---

## 4. Features

**What it covers:**
- User-facing capabilities and workflows
- CRUD operations and background/async operations
- Feature-to-implementation mapping (entry point, key files, patterns used)
- Extension points (plugin systems, config-driven behavior, abstract types)
- Implementation recipes for each feature

**Output produced:** `references/features.md` — feature catalog with entry points, implementation recipes, extension points, feature-to-pattern mapping.

**Primary agents:** Architecture Mapper + API Surface Analyzer

---

## 5. Testing

**What it covers:**
- Test framework(s) and assertion libraries
- Test organization (mirror source, separate tree, co-located)
- Test types present (unit, integration, e2e, snapshot, property-based)
- Fixture/factory patterns for test data
- Mocking strategy
- Coverage configuration and thresholds
- CI test pipeline configuration
- Test naming conventions

**Output produced:** Testing sections in `references/conventions.md` and `references/architecture.md`.

**Primary agent:** Test Pattern Analyzer

---

## 6. Operations

**What it covers:**
- Deployment strategy (Docker, serverless, bare metal, PaaS)
- CI/CD pipeline configuration and stages
- Environment management (dev, staging, production)
- Logging and monitoring setup
- Database migration approach
- Secret management
- Infrastructure as code

**Output produced:** Operations sections in `references/architecture.md` and `references/conventions.md`.

**Primary agents:** API Surface Analyzer + Convention Extractor

---

## Agent Mapping Quick Reference

Use this to determine which agents to launch based on user-selected dimensions:

| Agent | Required For Dimensions |
|-------|------------------------|
| Architecture Mapper | Architecture, Features |
| API Surface Analyzer | Features, Operations |
| Pattern Detective | Design Patterns |
| Convention Extractor | Coding Conventions, Operations |
| Test Pattern Analyzer | Testing |

**Minimum agents for common selections:**
- "Architecture + Patterns" → 2 agents (Architecture Mapper, Pattern Detective)
- "Everything except Testing" → 4 agents (all except Test Pattern Analyzer)
- "All dimensions" → 5 agents (all)
- "Just Conventions" → 1 agent (Convention Extractor)
