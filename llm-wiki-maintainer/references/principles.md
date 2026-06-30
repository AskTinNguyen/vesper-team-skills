# LLM Wiki Principles

This reference extracts the operating rules from Karpathy's `LLM-WIKI.md` field notes and reframes them as reusable design constraints.

## Core Thesis

Most personal knowledge systems die from maintenance overhead, not from lack of ideas.

The pattern here is:

- the human curates sources and asks questions
- the model owns summarization, cross-referencing, reconciliation, and index upkeep
- the wiki becomes a compiled artifact that improves with use

The key distinction is between **raw record** and **compiled knowledge**.

## The Nine Rules

### 1. Sources Are Immutable

Everything captured into `raw/` is source-of-truth material.

- articles
- transcripts
- PDFs
- screenshots
- exports

Do not rewrite it after capture. If a source is wrong, add a corrected source or an explicit note in `wiki/`.

Why it matters:

- preserves auditability
- prevents two conflicting systems of record
- keeps reinterpretation possible without corrupting history

### 2. Separate The Layers

Use distinct layers with explicit ownership:

- `raw/` for immutable source record
- `wiki/` for maintained pages
- one schema/config document for update rules

Blurring these layers destroys trust. If the model writes into `raw/`, or the human manually edits compiled pages to win an argument, the system quietly becomes unreliable.

### 3. The Model Owns The Wiki

Humans should rarely do the clerical work of:

- summarizing
- filing under the right topic
- updating neighboring pages
- keeping links current

That bookkeeping is exactly what the model should absorb.

### 4. Compile, Don’t Retrieve

This pattern is not classic RAG.

RAG re-derives answers from raw chunks on every query.
A wiki compiles sources into structured pages, then answers from those maintained pages.

Analogy:

- `raw/` is source code
- the model is the compiler
- `wiki/` is the executable
- questions are runtime

Why it matters:

- knowledge compounds instead of being rediscovered
- strong answers can become pages, not dead chat output

### 5. Ingest One Source At A Time

Drop in one source and trace its implications through the graph.

A good ingest does not merely add one page. It updates every page whose meaning changes because of the new source.

Batch-importing an entire life archive at once produces a dump, not a wiki.

### 6. Link Everything

Every durable page should connect to others.

- every link should become a visible edge in the graph
- clusters and hubs should emerge naturally
- orphans indicate missed integration work

The value is in the edges, not just in the node count.

### 7. Navigate By Index

The model should answer by following `index.md` and reading the relevant pages, not by loading the entire vault every time.

An honest index:

- exposes the main territories
- reveals clusters
- makes stale areas obvious
- reduces brute-force scanning

If the model must crawl the whole corpus for normal questions, the index stopped reflecting the territory.

### 8. Lint The Knowledge

Treat the wiki like code and run health checks.

Look for:

- contradictions between pages
- low-confidence claims
- orphans
- duplicate entities
- spelling drift
- stale summaries

A contradiction is not a cosmetic error. It usually means two sources disagree and now the system knows where judgment is required.

### 9. Start Small

Begin with a few sources, not a grand architecture.

The first real ingests reveal which naming conventions, page shapes, and maintenance rules actually matter.

A small working wiki beats an abandoned elaborate design.

## Deeper Product / System Lessons

### The model should maintain editorial state, not just answer questions

The real leverage is not better one-turn reasoning.
It is better upkeep at near-zero marginal cost.

### Good answers should promote into durable assets

When a query yields a strong synthesis, the system should be able to:

- create a new wiki page
- expand an existing one
- update the index
- schedule future review if the topic is still moving

### Persona/schema matters as governance

The schema file is not cosmetic. It determines what counts as durable knowledge, how pages are updated, and how the model behaves as a maintainer rather than a generic assistant.

### Memory and wiki should stay distinct

Keep short durable facts in memory systems.
Keep rich synthesis, comparisons, evolving views, and source-grounded editorial structure in the wiki.

## Practical Heuristics

- prefer updating an existing page over creating a new one
- create a new page when the concept has multiple inbound links or recurring relevance
- add explicit “open questions” sections rather than hiding uncertainty
- record source anchors for claims that may later be challenged
- run lint passes after bursts of ingest, not only after full rebuilds
