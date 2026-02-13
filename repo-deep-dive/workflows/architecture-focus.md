---
name: workflows:architecture-focus
description: Architecture-only deep dive for understanding system design, component boundaries, and data flow
---

# Architecture Focus Workflow

<command_purpose>Perform a focused deep dive into a repository's architecture — system design, component boundaries, data flow, and architectural decisions — without full pattern/convention extraction.</command_purpose>

<role>Software Architect specializing in system decomposition, dependency analysis, and architectural pattern recognition</role>

## Prerequisites

Ensure Phase 1 (Repo Ingestion) from [full-analysis.md](./full-analysis.md) is complete:
- Repository is cloned or accessible locally
- Reconnaissance script has been run
- Priority files have been read
- Tech stack is identified

If not, execute Phase 1 steps first.

## Step 1: Structural Analysis

### 1.1: Map Top-Level Boundaries

Read the top-level directory listing and classify each directory:

| Directory | Classification | Purpose |
|-----------|---------------|---------|
| src/, lib/, app/ | Source code | Core implementation |
| test/, spec/, __tests__/ | Test code | Verification |
| config/, .config/ | Configuration | Runtime/build config |
| docs/, doc/ | Documentation | Human-readable docs |
| scripts/, bin/, tools/ | Tooling | Build/deploy/dev scripts |
| public/, static/, assets/ | Static assets | Served directly |
| migrations/, db/ | Data schema | Database evolution |

### 1.2: Identify Architectural Layers

Read entry points and trace the call chain to identify layers:

<task_list>
- [ ] **Presentation layer** — routes, controllers, views, CLI handlers
- [ ] **Business logic layer** — services, models, domain objects
- [ ] **Data access layer** — repositories, ORMs, query builders, DAOs
- [ ] **Infrastructure layer** — database connections, HTTP clients, caches, queues
- [ ] **Cross-cutting concerns** — logging, auth, error handling, middleware
</task_list>

For each layer, list the key files and their responsibilities.

### 1.3: Map Internal Dependencies

Trace imports/requires across modules to build a dependency map:

```
Module A → imports from → Module B, Module C
Module B → imports from → Module D
Module C → imports from → Module D, Module E (external)
```

Identify:
- **Core modules** — imported by many, import few (high fan-in)
- **Leaf modules** — import many, imported by few (high fan-out)
- **Circular dependencies** — modules that import each other
- **Shared utilities** — modules imported by 3+ other modules

## Step 2: Data Flow Analysis

### 2.1: Request/Response Flow

Trace a typical request from entry to response:

```
1. HTTP Request arrives at {router file}:{line}
2. Middleware processes: {middleware chain}
3. Route handler at {controller}:{line}
4. Business logic in {service/model}:{line}
5. Data access via {repository/ORM}:{line}
6. Database query
7. Response serialization at {serializer}:{line}
8. HTTP Response
```

### 2.2: Data Models

<task_list>
- [ ] List all data models/entities/tables
- [ ] Map relationships (has-many, belongs-to, many-to-many)
- [ ] Identify the core domain model (most relationships, most referenced)
- [ ] Document data validation rules and where they're enforced
- [ ] Note any event/audit trails
</task_list>

### 2.3: Async / Background Flows

If present, trace background processing:
- Job queues and workers
- Event emitters and subscribers
- Scheduled tasks / cron jobs
- WebSocket / real-time channels

## Step 3: Architectural Decisions

### 3.1: Classify Architecture Style

Based on findings, classify the architecture:

| Style | Indicators |
|-------|-----------|
| **Monolith** | Single deployable, shared database, in-process calls |
| **Modular Monolith** | Single deployable but clear module boundaries, internal APIs |
| **Microservices** | Multiple deployables, service-to-service calls, separate databases |
| **Serverless** | Function handlers, event triggers, managed services |
| **MVC** | Controllers, models, views in separate directories |
| **Clean/Hexagonal** | Ports and adapters, dependency inversion, domain core isolated |
| **Event-Driven** | Event bus, pub/sub, event sourcing, CQRS |
| **Layered** | Strict layer separation with one-way dependencies |

### 3.2: Infer Architecture Decision Records

For each significant choice, create an ADR:

```
## ADR: {Title}
**Status:** Observed (inferred from code)
**Context:** {What problem was being solved}
**Decision:** {What was chosen}
**Evidence:** {file:line references showing the pattern}
**Alternatives not chosen:** {What they didn't do, if detectable}
**Consequences:** {Trade-offs — what this enables vs constrains}
```

Common ADRs to look for:
- Database choice and access pattern
- Authentication/authorization approach
- API style (REST, GraphQL, gRPC, tRPC)
- State management approach
- Caching strategy
- Error handling philosophy
- Deployment strategy

### 3.3: Scalability and Performance Patterns

Note any evidence of:
- Connection pooling
- Caching layers (Redis, in-memory, CDN)
- Query optimization (indexes, eager loading, N+1 prevention)
- Rate limiting
- Load balancing configuration
- Horizontal scaling support (stateless services, session stores)

## Step 4: Generate Architecture Report

Produce the architecture report using the template from [output-architecture.md](../references/output-architecture.md).

The report should include:
1. System overview (2-3 paragraphs)
2. Architecture style classification with evidence
3. Component catalog with dependencies
4. Data flow diagrams (text-based)
5. Data model summary
6. ADRs (at least 3)
7. Quality assessment

Present the completed report to the user and ask if they want to proceed to full analysis or generate a skill package.
