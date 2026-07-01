# Findings Presentation Templates

Templates for presenting findings at Checkpoint 2. Organize findings by user interest (not by agent) and provide per-finding triage actions.

## Findings Presentation Format

### Section Header

```markdown
## {Dimension Name} Findings

{1-2 sentence summary of what was found in this dimension.}
```

### Per-Finding Format

```markdown
### {Finding Title}

**Confidence:** {Definite | Probable | Possible}
**Evidence:** {N} file references

{2-3 sentence summary of the finding. State what was found, where, and why it matters.}

**Key evidence:**
- `{file:line}` — {brief description of what this reference shows}
- `{file:line}` — {brief description}

**Action:** `[Keep]` `[Skip]` `[Dig deeper]`
```

### Triage Actions

| Action | Meaning | What Happens |
|--------|---------|-------------|
| **Keep** | Include this finding in the final output | Finding passes to output generation as-is |
| **Skip** | Exclude this finding from the final output | Finding is discarded, not mentioned in output |
| **Dig deeper** | Investigate this finding further | Triggers a deep-dive session (max 3 iterations) |

## Summary Table

Present after all individual findings:

```markdown
## Summary

| # | Finding | Dimension | Confidence | Evidence | Action |
|---|---------|-----------|------------|----------|--------|
| 1 | {title} | {dimension} | {level} | {N} refs | {Keep/Skip/Dig deeper} |
| 2 | {title} | {dimension} | {level} | {N} refs | {Keep/Skip/Dig deeper} |
| ... | ... | ... | ... | ... | ... |

**Totals:** {N} findings — {N} kept, {N} skipped, {N} dig deeper
```

## Quality Ratings Table

Present alongside the summary:

```markdown
## Quality Assessment

| Dimension | Rating (1-5) | Notes |
|-----------|-------------|-------|
| Consistency | {N} | {brief note on pattern consistency} |
| Documentation | {N} | {brief note on docs quality} |
| Test Coverage | {N} | {brief note on testing} |
| Separation of Concerns | {N} | {brief note on boundaries} |
| Extensibility | {N} | {brief note on extension points} |
```

## Overall Questions Section

Present at the end of findings:

```markdown
## Questions for You

Based on the analysis, these areas could benefit from your input:

1. {Question about an ambiguous finding — e.g., "The codebase uses both factory functions and class constructors. Is one preferred?"}
2. {Question about a gap — e.g., "No formal error handling strategy was detected. Is this intentional?"}
3. {Question about scope — e.g., "The `legacy/` directory contains older patterns. Include or exclude from output?"}
```

## Bulk Triage Prompts

Offer these shortcuts for efficiency:

```markdown
**Quick triage options:**
- "Keep all" — Keep every finding
- "Keep all {dimension}" — Keep all findings in a specific dimension
- "Skip all {dimension}" — Skip all findings in a specific dimension
- "Only keep definite" — Keep only high-confidence findings, skip the rest
- Triage individually — Review each finding one by one
```

## Deep-Dive Request Format

When the user selects "Dig deeper" on a finding:

```markdown
## Deep-Dive Request: {Finding Title}

**Original finding:** {2-3 sentence summary}
**Current evidence:** {N} references
**User's question:** {What specifically to investigate further, if stated}

**Proposed investigation:**
- {Specific files or areas to examine}
- {Specific questions to answer}
- {Expected outcome}
```

Collect all "dig deeper" requests and pass them to [deep-dive-session.md](../workflows/deep-dive-session.md) as a batch.
