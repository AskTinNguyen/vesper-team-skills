---
name: code-simplifier
description: This skill should be used when simplifying and refining code for clarity, consistency, and maintainability while preserving all functionality. It focuses on recently modified code unless instructed otherwise.
model: opus
license: MIT
metadata:
  author: anthropic
  version: "1.1.0"
---

# Code Simplifier

Simplify and refine code for clarity, consistency, and maintainability without changing functionality. Prioritize readable, explicit code over compact solutions.

## Scope

Focus on recently modified code unless explicitly instructed to review a broader scope. To identify recently modified files, check `git diff --name-only` or the current session context.

## Process

1. **Identify target code** — determine which files or sections were recently modified
2. **Read project standards** — load CLAUDE.md (or equivalent) for project-specific conventions, naming rules, and patterns
3. **Analyze and edit** — apply refinements directly to each file (do not just report findings)
4. **Verify** — confirm all original functionality, outputs, and behaviors remain intact
5. **Document** — note only significant changes that affect understanding

## Refinement Priorities

Apply project standards from CLAUDE.md first, then these general principles:

### Do

- Reduce unnecessary nesting and complexity
- Consolidate related logic that is scattered across a file
- Improve variable and function names for clarity
- Remove comments that describe obvious code
- Replace nested ternary operators with if/else or switch statements
- Choose clarity over brevity — explicit code is better than dense one-liners

### Do Not

- Change what the code does — only change how it is expressed
- Create overly clever solutions that are hard to follow
- Combine too many concerns into single functions or components
- Remove helpful abstractions that improve code organization
- Prioritize "fewer lines" over readability
- Make the code harder to debug or extend
- Add features, error handling, or abstractions beyond what exists
