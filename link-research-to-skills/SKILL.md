---
name: link-research-to-skills
description: Turn links, articles, threads, repos, and research notes into reusable agent skills with grounded sources, clear triggers, and installable SKILL.md packages.
argument-hint: "URL, source bundle, or research topic to convert into a skill"
---

# Link + Research → Skill

Use when the user drops a link, research result, article, repo, thread, transcript, or rough notes and wants the useful procedure captured as an agent skill. Operate proactively: if the source contains a repeatable workflow, tool integration, playbook, or decision rubric, convert it into a durable skill rather than leaving it as a summary.

## Operating rule

Produce an installable skill, not just notes. Preserve the source's reusable method, remove one-off context, and make the resulting skill usable by a future agent without asking the user to rediscover the source.

## Workflow

1. **Collect the source.** Fetch/read the linked material or provided notes. If a link is inaccessible, record that limitation and use any supplied excerpts.
2. **Extract the durable procedure.** Identify:
   - Trigger: what user request should load this skill.
   - Outcome: what the skill helps produce or decide.
   - Inputs: URLs, files, credentials, commands, repos, or APIs required.
   - Steps: the smallest reliable sequence an agent should follow.
   - Pitfalls: source-specific gotchas, failure modes, limits, or anti-patterns.
   - Verification: how to prove the skill worked.
3. **Separate summary from skill.** Put only reusable instructions in `SKILL.md`. Move large source excerpts, schemas, examples, prompts, or command references into `references/` when needed.
4. **Write skill frontmatter.** Use a short kebab-case `name` and a specific third-person `description` that says when the skill should be used.
5. **Ground the skill.** Add a `## Sources` section with canonical URLs, titles, dates accessed when useful, and any local notes used.
6. **Install where requested.** Copy the final skill package to each target agent/app skill directory exactly, preserving resources.
7. **Verify.** Confirm `SKILL.md` exists in every target, frontmatter parses, and the installed skill appears in the relevant skill listing when the app provides one.

## Writing standards

- Prefer imperative, agent-facing instructions.
- Do not include temporary session progress, PR numbers, branch names, or stale facts unless the skill's purpose is explicitly tied to that repo state.
- Do not overfit to one source. Generalize the method while retaining necessary source constraints.
- Do not create grab-bag mega-skills. Split into multiple skills when triggers or outcomes differ.
- Include exact commands only when they are part of the reusable workflow.

## Output format

When reporting completion, include:

- Skill name(s)
- Installed locations
- Source link(s)
- Verification performed
- Backup commit or artifact path, if applicable
