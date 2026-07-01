---
name: slash-commands
description: Handle slash commands like /plan, /review, /changelog
triggers:
  - message starts with /
  - user asks about available commands
---

# Slash Commands

When a user message starts with `/`, it's a slash command.

## How to Handle

1. **Extract the command name** from the message (e.g., `/plan feature X` → command is `plan`)
2. **Call `slash_read(command)`** to get the command instructions
3. **Follow the instructions** in the returned file
4. The text after the command name is the user's input/context (treat as `$ARGUMENTS`)

## Examples

```
User: /changelog
→ slash_read("changelog") → follow the changelog instructions

User: /workflows:plan Build a login system
→ slash_read("workflows:plan") → follow plan instructions with "Build a login system" as context

User: /simplify-code file:src/utils.ts
→ slash_read("simplify-code") → follow with "file:src/utils.ts" as the argument
```

## Namespaces

Commands can be namespaced with `:` separator:
- `/workflows:plan` → reads `commands/workflows/plan.md`
- `/workflows:review` → reads `commands/workflows/review.md`

## Discovery

If unsure what commands exist, call `slash_list()` first.

## Argument Handling

The command file may reference `$ARGUMENTS`, `{{ARGS}}`, or similar placeholders.
Treat everything after the command name as the arguments:

```
/plan Build user authentication with OAuth
      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      This is $ARGUMENTS
```

Just substitute naturally when you encounter these placeholders in the instructions.
