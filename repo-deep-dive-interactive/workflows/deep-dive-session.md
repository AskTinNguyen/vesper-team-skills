---
name: workflows:deep-dive-session
description: Iterative refinement sub-workflow for investigating findings marked "dig deeper" at Checkpoint 2
---

# Deep-Dive Session

<command_purpose>Perform targeted follow-up investigation on findings the user wants to explore further. Run up to 3 iterations of investigate → present → triage until the user approves all findings.</command_purpose>

<role>Focused Investigator who drills into specific areas of the codebase based on user direction, returning refined findings with stronger evidence.</role>

## Input

This workflow receives from [guided-synthesis.md](./guided-synthesis.md):

- **Dig-deeper findings** — List of findings marked "dig deeper" at Checkpoint 2
- **User questions** — Specific questions the user wants answered about each finding
- **Repo path** — Path to the repository
- **Phase 1 context** — Reconnaissance summary for agent context

## Iteration Loop

<critical_requirement>Maximum 3 iterations. On the third iteration, present findings as final — no further "dig deeper" option. Inform the user that additional investigation can be done manually.</critical_requirement>

### Iteration Counter

```
current_iteration = 0
max_iterations = 3
pending_findings = [all dig-deeper findings from input]
resolved_findings = []
```

---

### Step 1: Prepare Investigation Targets

For each finding in `pending_findings`:

```markdown
## Investigation Target: {Finding Title}

**Original finding:** {2-3 sentence summary}
**Current evidence:** {N} references
**User's question:** {What specifically to investigate, if stated}

**Investigation plan:**
- Specific files to examine: {list based on original evidence + adjacent files}
- Questions to answer: {user's question + logical follow-ups}
- Expected output: {What a resolved finding would look like}
```

### Step 2: Launch Targeted Agents

<parallel_tasks>
For each investigation target (or group of related targets), launch a targeted Task Explore agent:

```
Task Explore("Investigate {finding-title} in {repo-path}.

Context: {phase1-context}

Original finding: {original-summary}
Current evidence: {list of file:line references}

Specific questions to answer:
{user-questions}

Investigation scope:
- Start with these files: {specific files from investigation plan}
- Expand to adjacent files if needed
- Focus depth: look for implementation details, edge cases, and patterns

Output:
- Updated finding summary (2-3 sentences, more specific than original)
- All evidence found (file:line references)
- Answers to user's specific questions
- Confidence level: definite / probable / possible
- Any related findings discovered during investigation")
```

Group related findings (same area of codebase) into a single agent to avoid redundant file reads.
</parallel_tasks>

### Step 3: Collect and Format Results

For each agent response:

<task_list>
- [ ] Extract updated finding summary
- [ ] Collect all new evidence references
- [ ] Record answers to user questions
- [ ] Update confidence level
- [ ] Note any new related findings discovered
</task_list>

Format using the per-finding template from [findings-presentation.md](../references/findings-presentation.md).

### Step 4: Present Updated Findings

```
current_iteration += 1
```

**If `current_iteration < max_iterations`:**

Present updated findings with triage options:

```markdown
## Deep-Dive Results (Iteration {current_iteration}/{max_iterations})

{For each updated finding:}

### {Finding Title} (Updated)

**Confidence:** {level} (was: {previous level})
**Evidence:** {N} file references (was: {previous N})

{Updated 2-3 sentence summary}

**New evidence:**
- `{file:line}` — {description}
- `{file:line}` — {description}

**Answers to your questions:**
- {Q}: {A}

**Action:** `[Keep]` `[Skip]` `[Dig deeper]`

---

{Any newly discovered related findings, also with triage options}
```

**If `current_iteration == max_iterations`:**

Present as final — no "dig deeper" option:

```markdown
## Deep-Dive Results (Final — Iteration {current_iteration}/{max_iterations})

**Note:** This is the final deep-dive iteration. Further investigation on these findings can be done manually.

{For each updated finding:}

### {Finding Title} (Final)

**Confidence:** {level}
**Evidence:** {N} file references

{Updated summary}

**Action:** `[Keep]` `[Skip]`
```

### Step 5: Collect Triage Decisions

For each finding:
- **Keep** → Move to `resolved_findings`
- **Skip** → Discard
- **Dig deeper** (only if `current_iteration < max_iterations`) → Keep in `pending_findings` with updated context

### Step 6: Loop or Exit

**If `pending_findings` is empty OR `current_iteration == max_iterations`:**

Exit the loop. Return `resolved_findings` to [guided-synthesis.md](./guided-synthesis.md).

**If `pending_findings` is not empty AND `current_iteration < max_iterations`:**

Return to Step 1 with updated `pending_findings`.

---

## Output

Return to guided-synthesis.md:

- **Resolved findings** — All findings that were kept after deep-dive investigation
- **Iteration count** — How many iterations were used
- **Unanswered questions** — Any user questions that couldn't be fully answered within 3 iterations

```markdown
## Deep-Dive Session Complete

**Iterations used:** {N} of {max_iterations}
**Findings resolved:** {N} kept, {N} skipped
**Unanswered questions:** {list or "none"}
```
