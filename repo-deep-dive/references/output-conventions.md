# Output Template: conventions.md

Use this template when generating the `references/conventions.md` file for a repo-knowledge package. Replace all `{placeholders}` with actual findings.

---

```markdown
# Conventions: {Repo Name}

## Quick Reference

| Category | Convention | Example |
|----------|-----------|---------|
| File names | {kebab-case / snake_case / PascalCase} | `{example-file.ts}` |
| Directories | {kebab-case / snake_case / PascalCase} | `{example-dir/}` |
| Classes | {PascalCase} | `{UserService}` |
| Functions | {camelCase / snake_case} | `{getUserById}` |
| Variables | {camelCase / snake_case} | `{currentUser}` |
| Constants | {SCREAMING_SNAKE_CASE / PascalCase} | `{MAX_RETRIES}` |
| File org | {by feature / by type / by layer} | `{src/users/}` or `{src/controllers/}` |
| Error handling | {exceptions / Result type / error codes} | `{throw new AppError()}` |
| Tests | {co-located / mirror tree / separate dir} | `{src/__tests__/}` |

## Naming Conventions

### Files

**Convention:** {description of file naming convention}
**Enforced by:** {linter rule / convention only}

Examples:
- `{file1}` — {what this file contains}
- `{file2}` — {what this file contains}
- `{file3}` — {what this file contains}

### Directories

**Convention:** {description}

Examples:
- `{dir1}/` — {purpose}
- `{dir2}/` — {purpose}
- `{dir3}/` — {purpose}

### Classes / Interfaces / Types

**Convention:** {description}

Examples from source:
- `{ClassName}` at `{file}:{line}` — {purpose}
- `{InterfaceName}` at `{file}:{line}` — {purpose}
- `{TypeName}` at `{file}:{line}` — {purpose}

### Functions / Methods

**Convention:** {description}

Examples from source:
- `{functionName}` at `{file}:{line}` — {what it does}
- `{methodName}` at `{file}:{line}` — {what it does}
- `{helperName}` at `{file}:{line}` — {what it does}

### Variables

**Convention:** {description}

Examples from source:
- `{varName}` at `{file}:{line}`
- `{CONST_NAME}` at `{file}:{line}`
- `{enumValue}` at `{file}:{line}`

### Database

**Convention:** {table naming, column naming, index naming}

Examples:
- Table: `{table_name}` — {columns}
- Column: `{column_name}` — {type}
- Index: `{index_name}` — {purpose}

## File Organization

### Directory Structure Pattern

```
{Actual directory tree showing the organization pattern}

Example:
src/
├── features/           # Grouped by feature
│   ├── auth/
│   │   ├── auth.controller.ts
│   │   ├── auth.service.ts
│   │   ├── auth.model.ts
│   │   └── auth.test.ts
│   └── users/
│       ├── users.controller.ts
│       └── ...
├── shared/             # Cross-cutting utilities
│   ├── middleware/
│   ├── errors/
│   └── utils/
└── config/             # Configuration
```

**Grouping strategy:** {by feature / by type / by layer / hybrid}

**Key rules:**
1. {Rule about where new files go}
2. {Rule about file naming relative to directory}
3. {Rule about index/barrel files}

### Where New Files Go

| File Type | Location | Naming | Example |
|-----------|----------|--------|---------|
| {Controller} | `{path/}` | `{pattern}` | `{example}` |
| {Model} | `{path/}` | `{pattern}` | `{example}` |
| {Service} | `{path/}` | `{pattern}` | `{example}` |
| {Test} | `{path/}` | `{pattern}` | `{example}` |
| {Config} | `{path/}` | `{pattern}` | `{example}` |

## Import / Module Patterns

**Import style:** {absolute / relative / path aliases}
**Import ordering:** {description of ordering convention}

Example from source (`{file}:{line}`):
```{language}
// 1. Standard library / built-in
{import example}

// 2. Third-party packages
{import example}

// 3. Internal modules (absolute)
{import example}

// 4. Relative imports
{import example}
```

**Barrel files:** {Yes/No — description of re-export pattern}
**Circular dependency avoidance:** {Strategy if any}

## Error Handling

### Strategy

**Approach:** {exceptions / Result types / error codes / mixed}

**Error class hierarchy:**
```
{Text tree of error classes}

Example:
AppError (base)
├── ValidationError
├── NotFoundError
├── AuthenticationError
├── AuthorizationError
└── ExternalServiceError
```

### Error Creation Pattern
```{language}
// From {file}:{line}
{code showing how errors are created}
```

### Error Handling Pattern
```{language}
// From {file}:{line}
{code showing how errors are caught/handled}
```

### Error Propagation
{Description of how errors flow through layers}

### User-Facing Errors
{How errors are formatted for API responses or UI}

### Logging Convention
{What gets logged, at what levels, format}

## Documentation Conventions

### Code Comments

**Style:** {JSDoc / docstrings / inline / minimal}
**Density:** {Heavy / Moderate / Sparse / Functions-only}

Example:
```{language}
// From {file}:{line}
{code with representative comments/docs}
```

### Type Annotations

**Usage:** {Strict / Moderate / Minimal}
**Evidence:** {tsconfig strict mode, mypy config, etc.}

## Code Formatting

**Formatter:** {Prettier / Black / rustfmt / gofmt / etc.}
**Config file:** `{path to config}`

| Rule | Setting |
|------|---------|
| Indentation | {spaces/tabs, width} |
| Line length | {max chars} |
| Trailing commas | {always / never / multi-line only} |
| Semicolons | {always / never / ASI} |
| Quotes | {single / double} |
| Bracket style | {same line / next line} |

## Git Conventions

### Commit Messages

**Format:** {Conventional Commits / free-form / custom}

Examples from git log:
- `{commit message 1}`
- `{commit message 2}`
- `{commit message 3}`

### Branch Naming

**Pattern:** `{prefix/description}` (e.g., `feature/add-auth`, `fix/login-bug`)

### PR Conventions

{PR template, review requirements, merge strategy}

## Testing Conventions

### Test Organization

**Location:** {co-located / mirror / separate directory}
**Naming:** `{pattern}` (e.g., `*.test.ts`, `*_spec.rb`)

### Test Structure

```{language}
// From {file}:{line}
{representative test showing structure conventions}
```

### Data Setup

**Approach:** {factories / fixtures / inline / builders}

Example:
```{language}
// From {file}:{line}
{code showing how test data is created}
```

### Assertion Style

{describe or assertEqual / expect / assert / should}
```
