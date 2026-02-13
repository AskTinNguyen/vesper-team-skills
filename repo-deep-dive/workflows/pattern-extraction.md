---
name: workflows:pattern-extraction
description: Focused extraction of design patterns, coding conventions, and idioms from a repository
---

# Pattern Extraction Workflow

<command_purpose>Extract design patterns, coding conventions, and implementation idioms from a repository — producing a comprehensive catalog with evidence-based documentation.</command_purpose>

<role>Design Pattern Analyst specializing in identifying recurring solutions, coding idioms, and convention systems in production codebases</role>

## Prerequisites

Ensure Phase 1 (Repo Ingestion) from [full-analysis.md](./full-analysis.md) is complete:
- Repository is cloned or accessible locally
- Reconnaissance script has been run
- Tech stack is identified

If not, execute Phase 1 steps first.

## Step 1: Pattern Detection

Read [pattern-catalog.md](../references/pattern-catalog.md) for the complete list of patterns to search for.

### 1.1: Launch Pattern Detection Agents

<parallel_tasks>

Run these 2 agents in parallel:

#### Agent A: Design Pattern Detective

```
Task Explore("Search {repo-path} for design patterns.

Tech stack: {detected-stack}

For each pattern found, document:
- Pattern name (Gang of Four name or common name)
- Category (Creational / Structural / Behavioral / Architectural)
- Location: file:line
- How it's implemented in this codebase
- Why it's likely used here (what problem it solves)
- Confidence: definite / probable / possible

Search for:
CREATIONAL: Factory, Abstract Factory, Builder, Singleton, Prototype, DI/IoC
STRUCTURAL: Adapter, Bridge, Composite, Decorator, Facade, Proxy, Plugin
BEHAVIORAL: Observer/Event, Strategy, Command, State, Iterator, Mediator, Chain of Responsibility
ARCHITECTURAL: Repository, Unit of Work, CQRS, Event Sourcing, Saga, Circuit Breaker

Also search for language/framework-specific patterns:
- Ruby/Rails: Concerns, STI, Polymorphic associations, Service objects, Form objects
- JavaScript/TS: Module pattern, Middleware chain, HOCs, Hooks, Render props
- Python: Decorators, Context managers, Metaclasses, Descriptors
- Go: Functional options, Interface satisfaction, Table-driven tests
- Rust: Builder pattern, Type state, Newtype, Error handling with Result/Option
- Java: Dependency injection, Proxy/AOP, Repository pattern, DTO pattern")
```

#### Agent B: Convention Extractor

```
Task Explore("Extract coding conventions from {repo-path}.

Tech stack: {detected-stack}

For EACH convention, provide 3+ concrete examples with file:line references.

Extract:
1. NAMING CONVENTIONS
   - File naming (kebab-case, snake_case, PascalCase)
   - Directory naming
   - Class/struct/interface naming
   - Function/method naming
   - Variable naming (including constants, enums)
   - Database table/column naming

2. FILE ORGANIZATION
   - Grouping strategy (by feature, by type, by layer)
   - Index/barrel file usage
   - Co-location patterns (tests next to source, styles next to components)
   - File size tendencies (many small files vs fewer large files)

3. IMPORT/MODULE PATTERNS
   - Absolute vs relative imports
   - Import ordering convention
   - Re-export patterns
   - Circular dependency avoidance

4. ERROR HANDLING
   - Exception/error class hierarchy
   - Try/catch placement strategy
   - Error propagation pattern
   - User-facing error formatting
   - Logging conventions

5. DOCUMENTATION
   - Comment style and density
   - Docstring/JSDoc format
   - README presence per module
   - Type annotation usage and style

6. CODE FORMATTING
   - Indentation (spaces vs tabs, width)
   - Line length limit
   - Bracket/brace style
   - Trailing commas, semicolons
   - (Check linter/formatter configs for definitive rules)")
```

</parallel_tasks>

### 1.2: Merge Agent Results

After both agents return:

<task_list>
- [ ] Combine design patterns and conventions into a unified view
- [ ] Remove duplicates (patterns cited by both agents)
- [ ] Cross-reference: which conventions support which patterns?
- [ ] Identify the "signature" patterns — the ones most characteristic of this codebase
</task_list>

## Step 2: Deep Pattern Analysis

For each pattern rated "definite" or "probable":

### 2.1: Trace the Pattern

Follow the pattern across the codebase:
- How many times is this pattern used? (Search for similar structures)
- Is it applied consistently or are there variations?
- Is there a base class, utility, or helper that enables this pattern?

### 2.2: Extract the Recipe

For each pattern, write a generalized recipe:

```
## Pattern: {Name}

### When to Use
{Conditions under which this pattern is applied in this codebase}

### Implementation Steps
1. {Step one with generic placeholders}
2. {Step two}
3. {Step three}

### Example from Source
```{language}
// From {file}:{line}
{actual code snippet}
```

### Generic Template
```{language}
// Generalized version
{template code with placeholders}
```
```

### 2.3: Identify Pattern Interactions

Map how patterns work together:
- Which patterns are commonly used in combination?
- Is there a "standard stack" of patterns for new features?
- Are there patterns that replace or preclude others?

## Step 3: Convention Quantification

For key conventions, quantify adherence:

```
Convention: {name}
Adherence: {X}/{Y} files follow this convention ({percentage}%)
Exceptions: {list any files that deviate, with reasons if apparent}
Enforced by: {linter rule, CI check, or convention only}
```

This helps distinguish hard rules from soft preferences.

## Step 4: Generate Output

### 4.1: Patterns Report

Generate using [output-patterns.md](../references/output-patterns.md) template:
- Organized by category (Creational, Structural, Behavioral, Architectural)
- Each with evidence, recipe, and generic template
- Cross-references to other patterns

### 4.2: Conventions Report

Generate using [output-conventions.md](../references/output-conventions.md) template:
- Organized by category (Naming, File Org, Imports, Error Handling, etc.)
- Each with 3+ examples and adherence metrics
- Linter/formatter config references

### Completion Summary

Present to user:

```markdown
## Pattern Extraction Complete

**Patterns Found:** {N} ({definite}, {probable}, {possible})
**Conventions Extracted:** {N} across {categories} categories

### Signature Patterns (most characteristic)
1. {Pattern} — used {N} times, {description}
2. {Pattern} — used {N} times, {description}
3. {Pattern} — used {N} times, {description}

### Convention Highlights
- Files: {naming convention}
- Functions: {naming convention}
- Error handling: {strategy}
- Testing: {approach}

### Next Steps
- Run full analysis for feature extraction and architecture mapping
- Generate skill package from these findings
```
