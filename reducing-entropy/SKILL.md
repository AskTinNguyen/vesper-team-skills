---
name: reducing-entropy
description: This skill should be used when the user explicitly requests minimizing total codebase size. It measures success by final code amount, not effort, and biases toward deletion. Manual activation only.
---

# Reducing Entropy

More code begets more code. Entropy accumulates. This skill biases toward the smallest possible codebase.

**Core question:** "What does the codebase look like *after*?"

## The Goal

The goal is **less total code in the final codebase** — not less code to write right now.

- Writing 50 lines that delete 200 lines = net win
- Keeping 14 functions to avoid writing 2 = net loss
- "No churn" is not a goal. Less code is the goal.

**Measure the end state, not the effort.**

## Three Questions

### 1. What's the smallest codebase that solves this?

Not "what's the smallest change" — what's the smallest *result*.

- Could this be 2 functions instead of 14?
- Could this be 0 functions (delete the feature)?
- What would be deleted if this were done?

### 2. Does the proposed change result in less total code?

Count lines before and after. If after > before, reject it.

- "Better organized" but more code = more entropy
- "More flexible" but more code = more entropy
- "Cleaner separation" but more code = more entropy

### 3. What can be deleted?

See `references/detection-patterns.md` for concrete grep patterns to find dead code, unused imports, shims, and inline candidates.

Every change is an opportunity to delete. Ask:

- What does this make obsolete?
- What was only needed because of what is being replaced?
- What's the maximum that could be removed?

## Red Flags

- **"Keep what exists"** — Status quo bias. The question is total code, not churn.
- **"This adds flexibility"** — Flexibility for what? YAGNI.
- **"Better separation of concerns"** — More files/functions = more code. Separation isn't free.
- **"Type safety"** — Worth how many lines? Sometimes runtime checks in less code wins.
- **"Easier to understand"** — 14 things are not easier than 2 things.

## When This Does Not Apply

- The codebase is already minimal for what it does
- The codebase is in a framework with strong conventions (do not fight it)
- Regulatory/compliance requirements mandate certain structures

---

**Bias toward deletion. Measure the end state.**
