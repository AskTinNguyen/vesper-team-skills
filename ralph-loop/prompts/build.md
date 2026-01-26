# Build Task

Complete ONE story autonomously. Do not ask questions - make reasonable decisions.

## Story

**ID:** {{STORY_ID}}
**Title:** {{STORY_TITLE}}

### Story Content

{{STORY_BLOCK}}

## Rules

1. **Implement ONLY this story** - Do not work on other stories
2. **No questions** - Make reasonable assumptions and proceed
3. **Verify before done** - Run tests/checks relevant to your changes
4. **Use /commit** - Create conventional commits with proper type and scope
5. **One commit per story** - Group related changes together

## Workflow

1. Read and understand the story requirements
2. Identify files to create or modify
3. Implement the changes
4. Run verification (tests, lint, type-check as appropriate)
5. Create a commit using `/commit` skill
6. Mark story done (see below)

## On Complete

After committing, mark this story as done in the PRD file:

**File:** `{{PRD_PATH}}`

**Change:**
```
### [ ] {{STORY_ID}}:
```
**To:**
```
### [x] {{STORY_ID}}:
```

## Commit Format

Use conventional commits:
- `feat(scope): description` - New feature
- `fix(scope): description` - Bug fix
- `refactor(scope): description` - Code refactor
- `test(scope): description` - Add tests
- `docs(scope): description` - Documentation

**Example:** `feat({{STORY_ID}}): implement user authentication`
