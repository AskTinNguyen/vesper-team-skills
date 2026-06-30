# LLM Wiki Templates

Use these templates when creating or normalizing a compiled markdown wiki.

## Minimal Directory Layout

```text
knowledge-base/
├── raw/
│   ├── 2026-06-29-source-a.md
│   └── 2026-06-29-source-b.pdf
├── wiki/
│   ├── topic-a.md
│   ├── person-b.md
│   └── concept-c.md
├── index.md
└── AGENTS.md
```

Optional additions:

```text
knowledge-base/
├── raw/
├── wiki/
├── index.md
├── review-queue.md
└── AGENTS.md
```

## Schema Snippet For AGENTS.md / CLAUDE.md

```markdown
## Compiled Wiki Rules

- `raw/` is immutable source material; never rewrite captured sources.
- `wiki/` is the maintained editorial layer; update pages there.
- `index.md` is the navigation surface; keep it honest and current.
- Ingest one source at a time.
- Prefer updating existing pages before creating new ones.
- Every durable page should link outward and inward where appropriate.
- Run periodic lint passes for contradictions, orphans, duplicate entities, and stale summaries.
- Promote strong recurring answers into `wiki/` instead of leaving them trapped in chat.
```

## Page Template

```markdown
# {{Page Title}}

## Summary

One paragraph explaining what this page is and why it matters.

## Key Points

- Point one
- Point two
- Point three

## Linked Pages

- [[related-page-a]]
- [[related-page-b]]

## Source Notes

- Source: `raw/2026-06-29-source-a.md`
- Source: `raw/2026-06-29-source-b.pdf`

## Open Questions

- Question one
- Question two
```

## Source Summary Page Template

Use when a source deserves its own compiled page in `wiki/`.

```markdown
# {{Source Topic}}

## Why This Source Matters

One paragraph on the source’s relevance.

## Claims / Learnings

- Claim or learning one
- Claim or learning two

## Implications For Existing Pages

- Update [[page-a]] because...
- Update [[page-b]] because...

## Source Record

- Raw file: `raw/2026-06-29-source-a.md`

## Open Questions

- What remains uncertain?
```

## Index Template

```markdown
# Index

## Main Territories

- [[topic-a]]
- [[topic-b]]
- [[concept-c]]

## People / Entities

- [[person-a]]
- [[company-b]]

## Current Focus

- [[active-theme-a]]
- [[active-theme-b]]

## Review Queue

- Page needing lint or rewrite
- Topic awaiting more sources

## Newly Added / Recently Changed

- [[page-updated-this-week]]
- [[new-page]]
```

## Lint Checklist

Run this pass after a few ingests or before calling the system healthy.

### Structural

- Does every important page appear in `index.md` or through a reachable hub?
- Are there orphan pages?
- Are there pages that should be merged?

### Consistency

- Do two pages make incompatible claims?
- Did the same entity drift into multiple spellings or duplicate pages?
- Did a new source invalidate an old summary?

### Link Density

- Does each durable page link to relevant neighbors?
- Are there repeated unlinked concepts that deserve their own page?

### Source Trust

- Are major claims anchored to raw sources?
- Did any interpretation leak into `raw/`?

### Uncertainty

- Are unresolved questions surfaced explicitly?
- Are contradictions being hidden instead of marked?
```

## Ingest Checklist

For each new source:

1. Save it to `raw/`
2. Read it for implications, not only summary
3. Update affected pages
4. Add or repair links
5. Update index only if the map changed
6. Add open questions where the source creates ambiguity

## Heuristic For New Page Creation

Create a new page when at least one of these is true:

- the concept recurs across multiple sources
- several pages would naturally link to it
- the source changes enough context that a summary deserves its own durable home
- the user is likely to revisit the concept directly

Otherwise, prefer expanding an existing page.
