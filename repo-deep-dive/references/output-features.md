# Output Template: features.md

Use this template when generating the `references/features.md` file for a repo-knowledge package. Replace all `{placeholders}` with actual findings.

---

```markdown
# Features: {Repo Name}

## Feature Catalog

| # | Feature | Entry Point | Key Files | Patterns Used |
|---|---------|-------------|-----------|---------------|
| 1 | {Feature name} | `{file}:{line}` | `{file1}`, `{file2}` | {Pattern1}, {Pattern2} |
| 2 | {Feature name} | `{file}:{line}` | `{file1}`, `{file2}` | {Pattern1}, {Pattern2} |

## Core Features

### Feature: {Feature Name}

**Purpose:** {What this feature does for the user}
**Entry point:** `{file}:{line}`

#### File Map

| Role | File | Key Lines |
|------|------|-----------|
| Route/Endpoint | `{file}` | {line range} |
| Handler/Controller | `{file}` | {line range} |
| Business Logic | `{file}` | {line range} |
| Data Access | `{file}` | {line range} |
| Validation | `{file}` | {line range} |
| Tests | `{file}` | {line range} |

#### Implementation Flow

```
1. {Entry trigger — HTTP request, CLI command, event, etc.}
2. {Validation / auth check}
3. {Business logic execution}
4. {Data persistence}
5. {Side effects — notifications, events, cache invalidation}
6. {Response formation}
```

#### Design Patterns Used

- **{Pattern}** — {how it's applied in this feature}
- **{Pattern}** — {how it's applied in this feature}

#### Database Tables Involved

| Table | Operations | Key Columns |
|-------|-----------|-------------|
| `{table}` | {READ/WRITE/BOTH} | `{col1}`, `{col2}` |

#### Error Handling

| Error Case | Handler | User Response |
|-----------|---------|---------------|
| {error condition} | `{file}:{line}` | {what user sees} |

{Repeat for each core feature}

---

## Implementation Recipes

Generalized step-by-step guides extracted from the feature implementations above.

### Recipe: {Feature Type} (e.g., "CRUD Resource", "Background Job", "Webhook Handler")

**Based on:** {Which features this recipe was extracted from}

**When to use:** {Conditions for applying this recipe}

#### Steps

1. **{Step title}**
   ```{language}
   // Template
   {generic code template}
   ```
   *Reference:* `{source_file}:{line}` for real example

2. **{Step title}**
   ```{language}
   // Template
   {generic code template}
   ```
   *Reference:* `{source_file}:{line}` for real example

3. **{Step title}**
   ```{language}
   // Template
   {generic code template}
   ```
   *Reference:* `{source_file}:{line}` for real example

#### Checklist

- [ ] {Required step 1}
- [ ] {Required step 2}
- [ ] {Required step 3}
- [ ] {Add tests for: ...}
- [ ] {Update documentation: ...}

{Repeat for each recipe}

---

## Extension Points

Places where the system is designed to be extended with new functionality.

### {Extension Point Name}

**Type:** {Plugin / Hook / Config / Interface / Event}
**Location:** `{file}:{line}`
**How to extend:**

```{language}
// Template for adding a new extension
{code showing how to add new functionality at this point}
```

**Existing extensions:**
- `{extension1}` at `{file}:{line}` — {what it does}
- `{extension2}` at `{file}:{line}` — {what it does}

{Repeat for each extension point}

---

## Feature-to-Pattern Map

Visual map showing which patterns each feature uses:

```
Feature          | Factory | Repository | Observer | Strategy | Middleware
-----------------|---------|------------|----------|----------|----------
{Feature 1}      |    X    |     X      |          |          |     X
{Feature 2}      |         |     X      |    X     |          |
{Feature 3}      |    X    |            |    X     |    X     |
```

## Background / Async Features

### {Background Feature Name}

**Trigger:** {Schedule / Event / Manual / Queue}
**Worker:** `{file}:{line}`
**Processing:**
1. {Step 1}
2. {Step 2}
3. {Step 3}

**Error handling:** {Retry strategy, dead letter, alerting}
**Monitoring:** {How to observe this feature's health}
```
