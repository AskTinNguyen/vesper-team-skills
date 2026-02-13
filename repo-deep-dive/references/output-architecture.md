# Output Template: architecture.md

Use this template when generating the `references/architecture.md` file for a repo-knowledge package. Replace all `{placeholders}` with actual findings. Remove sections that don't apply.

---

```markdown
# Architecture: {Repo Name}

## System Overview

{2-3 paragraphs describing what the system does, its primary purpose, and how it's structured at a high level. Include the tech stack and deployment model.}

**Tech Stack:** {Language} + {Framework} | {Database} | {Key Libraries}
**Architecture Style:** {Monolith / Modular Monolith / Microservices / Serverless / etc.}
**Deployment:** {Docker / K8s / PaaS / Serverless / etc.}

## Component Catalog

### {Component Name}

| Attribute | Value |
|-----------|-------|
| **Purpose** | {What this component is responsible for} |
| **Key Files** | `{path/to/main/file}`, `{path/to/other}` |
| **Dependencies** | {Other components this depends on} |
| **Dependents** | {Components that depend on this} |
| **Patterns Used** | {Factory, Repository, Observer, etc.} |

{Repeat for each major component}

## Data Flow

### Request Lifecycle

```
{Text-based data flow diagram}

Example:
HTTP Request
  → Router (routes.rb:15)
  → Middleware Stack [Auth, Logging, CORS]
  → Controller (app/controllers/posts_controller.rb:23)
  → Service/Model (app/models/post.rb:45)
  → Database (PostgreSQL)
  → Serializer (app/serializers/post_serializer.rb:10)
  → HTTP Response
```

### Background Processing Flow

```
{If applicable — job queues, event processing, etc.}

Example:
Event Published (app/models/order.rb:67)
  → Event Bus (app/events/bus.rb:12)
  → Handler (app/handlers/send_confirmation.rb:8)
  → External Service (SendGrid API)
  → Result logged
```

## Data Model

### Core Entities

| Entity | Table/Collection | Key Fields | Relationships |
|--------|-----------------|------------|---------------|
| {Entity} | {table_name} | {id, name, ...} | has_many {Other}, belongs_to {Parent} |

### Entity Relationship Summary

```
{Text-based ER summary}

Example:
User ──has_many──→ Posts ──has_many──→ Comments
  │                  │                    │
  └──has_many──→ Subscriptions      belongs_to User
```

## Architecture Decision Records

### ADR-1: {Title}

| Attribute | Detail |
|-----------|--------|
| **Status** | Observed (inferred from code) |
| **Context** | {Why this decision was likely made} |
| **Decision** | {What was chosen} |
| **Evidence** | `{file}:{line}` — {what the code shows} |
| **Alternatives Not Chosen** | {What they didn't do, if detectable} |
| **Consequences** | {Trade-offs — what this enables vs constrains} |

{Repeat for each ADR — aim for 3-7}

## External Integrations

| Service | Purpose | Client Location | Auth Method |
|---------|---------|-----------------|-------------|
| {Service} | {What it's used for} | `{file}:{line}` | {API key / OAuth / etc.} |

## Scalability Patterns

{Document any scalability-related patterns observed:}

- **Caching:** {What's cached, where, TTL strategy}
- **Connection Pooling:** {Database pool config}
- **Async Processing:** {Job queues, event-driven processing}
- **Rate Limiting:** {If present}
- **Horizontal Scaling:** {Stateless services, session stores}

## Quality Assessment

| Dimension | Rating (1-5) | Evidence |
|-----------|-------------|---------|
| Consistency | {N} | {Brief justification} |
| Documentation | {N} | {Brief justification} |
| Test Coverage | {N} | {Brief justification} |
| Separation of Concerns | {N} | {Brief justification} |
| Extensibility | {N} | {Brief justification} |
```
