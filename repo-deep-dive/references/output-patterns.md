# Output Template: patterns.md

Use this template when generating the `references/patterns.md` file for a repo-knowledge package. Replace all `{placeholders}` with actual findings.

---

```markdown
# Design Patterns: {Repo Name}

## Pattern Summary

| Pattern | Category | Confidence | Usage Count | Key Location |
|---------|----------|-----------|-------------|--------------|
| {Name} | {Creational/Structural/Behavioral/Architectural} | {Definite/Probable/Possible} | {N instances} | `{file}:{line}` |

## Signature Patterns

These patterns are most characteristic of this codebase — they define its identity and should be adopted when building similar systems.

### 1. {Pattern Name}

**Category:** {Creational / Structural / Behavioral / Architectural}
**Confidence:** Definite
**Usage:** {N} instances across the codebase

**What it does in this codebase:**
{2-3 sentences explaining how this pattern is specifically used here}

**Evidence:**
- `{file1}:{line}` — {what this code demonstrates}
- `{file2}:{line}` — {another instance}
- `{file3}:{line}` — {another instance}

**Source Example:**
```{language}
// From {file}:{line}
{actual code snippet showing the pattern}
```

**Generic Recipe:**
```{language}
// Generalized template — adapt naming and types to your domain
{generic version of the pattern with placeholder names}
```

**When to use this pattern:**
{Conditions under which this codebase applies this pattern}

**Related patterns:**
{Other patterns commonly used alongside this one}

{Repeat for each signature pattern}

---

## Creational Patterns

### {Pattern Name}

**Confidence:** {Definite / Probable / Possible}

**Evidence:**
- `{file}:{line}` — {description}

**Implementation:**
```{language}
// From {file}:{line}
{code snippet}
```

**Recipe:**
1. {Step 1}
2. {Step 2}
3. {Step 3}

{Repeat for each creational pattern found}

## Structural Patterns

### {Pattern Name}

**Confidence:** {Definite / Probable / Possible}

**Evidence:**
- `{file}:{line}` — {description}

**Implementation:**
```{language}
// From {file}:{line}
{code snippet}
```

**Recipe:**
1. {Step 1}
2. {Step 2}
3. {Step 3}

{Repeat for each structural pattern found}

## Behavioral Patterns

### {Pattern Name}

**Confidence:** {Definite / Probable / Possible}

**Evidence:**
- `{file}:{line}` — {description}

**Implementation:**
```{language}
// From {file}:{line}
{code snippet}
```

**Recipe:**
1. {Step 1}
2. {Step 2}
3. {Step 3}

{Repeat for each behavioral pattern found}

## Architectural Patterns

### {Pattern Name}

**Confidence:** {Definite / Probable / Possible}

**Evidence:**
- `{file}:{line}` — {description}

**Implementation:**
```{language}
// From {file}:{line}
{code snippet}
```

**Recipe:**
1. {Step 1}
2. {Step 2}
3. {Step 3}

{Repeat for each architectural pattern found}

## Framework-Specific Patterns

### {Pattern Name}

**Framework:** {Framework name and version}
**Confidence:** {Definite / Probable / Possible}

**Evidence:**
- `{file}:{line}` — {description}

**Implementation:**
```{language}
// From {file}:{line}
{code snippet}
```

{Repeat for each framework-specific pattern}

## Pattern Interactions

How the identified patterns work together:

```
{Text diagram showing pattern relationships}

Example:
Factory (creates) → Repository (accesses data via) → Unit of Work (manages transactions)
                         ↓
Observer (notifies on changes) → Event Handler (processes async)
```

### Common Pattern Stacks

When implementing a new feature in this codebase, the typical pattern stack is:

1. {Pattern} — for {purpose}
2. {Pattern} — for {purpose}
3. {Pattern} — for {purpose}

## Anti-Patterns Avoided

Patterns this codebase conspicuously does NOT use:

| Avoided Pattern | Evidence | Likely Reason |
|----------------|---------|---------------|
| {Pattern} | {What they do instead, with file:line} | {Why they likely avoid it} |
```
