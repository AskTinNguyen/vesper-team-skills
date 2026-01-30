---
name: code-quality-hook
description: PostToolUse hook that checks code quality after Edit/Write operations. Reports violations for function size, nesting depth, file size, and commented-out code blocks as non-blocking feedback.
---

# Code Quality Hook

A lightweight PostToolUse hook that checks files after Claude edits them. Reports quality violations as non-blocking feedback (exit code 2) so Claude can self-correct.

## What It Checks

| Check | Threshold | Why |
|-------|-----------|-----|
| Function size | >50 lines | Large functions are hard to reason about |
| Nesting depth | >4 levels | Deep nesting signals complex control flow |
| File size | >500 lines | Large files accumulate entropy |
| Commented-out code | >10 consecutive lines | Dead code should be deleted, not commented |

## What It Skips

- Test/spec files (`test`, `spec`, `_test.go`, `_spec.rb`)
- Vendored code (`node_modules`, `vendor`, `dist/`, `build/`)
- Minified files (`.min.js`, `.min.css`)
- Generated files (checked via first-line markers)

## Installation

Add to your `settings.json` (project or user level):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/skills/code-quality-hook/scripts/code_quality_check.py",
            "timeout": 15
          }
        ]
      }
    ]
  }
}
```

## Behavior

- **Exit 0**: No violations found (or file skipped)
- **Exit 2**: Violations found — printed to stderr as non-blocking feedback to Claude
- **Exit 1**: Script error (does not block Claude)

Violations appear as feedback in Claude's context, prompting it to reconsider the code it just wrote. This is advisory, not blocking.

## Manual Testing

```bash
echo '{"tool_name":"Edit","tool_input":{"file_path":"src/app.ts"}}' | python3 ~/.claude/skills/code-quality-hook/scripts/code_quality_check.py
echo $?
```
