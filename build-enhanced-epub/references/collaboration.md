# Collaboration for large books

Use parallel agents only when the user requests delegation or the active environment
permits it. Keep tasks bounded and evidence-backed.

Recommended split:

1. Source engineer: inspect and normalize source.
2. Corpus auditor: independently check completeness and extraction defects.
3. Story workers: analyze non-overlapping chapter ranges with small boundary overlap.
4. Canonical editor: merge arcs, aliases, entities, events, and intents.
5. EPUB engineer: build package and navigation.
6. QA worker: validate without seeing expected conclusions.

The orchestrator owns the plan, shared schema, chapter-count contract, canonical ID
namespace, merge, final validation, and delivery. Workers write drafts only. Never let
two workers mutate the same canonical index or EPUB output concurrently.

Give story workers local corpus artifacts, exact chapter ranges, required output
schema, and a rule to cite chapter evidence. Include one or two boundary chapters from
adjacent shards so transitions can be reconciled. Do not pass expected findings to an
independent QA worker.
