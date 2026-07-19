# Editorial semantic indexing

## Evidence artifacts

Create these before assigning narrative meaning:

- corpus manifest with title, length, paragraph count, checksum per chapter;
- JSONL containing order, title, and plain text;
- proper-noun candidates with chapter frequency;
- concordance for known names, aliases, factions, and places;
- boundary samples containing the end of one proposed arc and start of the next.

Machine candidates are evidence locators, not canonical facts.

## Arc method

1. Read the full chapter-title sequence for orientation.
2. Propose high-level continuous ranges.
3. Inspect chapter text on both sides of every boundary.
4. Write one summary describing setup, development, and the transition to the next arc.
5. Select at least three useful entry chapters for a long arc: setup, turn, climax.
6. Ensure ranges cover chapter `1..N` exactly once with no gaps or overlaps.

Favor a small number of memorable story stages over chapter-sized pseudo-arcs.

## Entity method

Merge aliases, honorifics, translated spellings, secret identities, and renamed
personas before minting IDs. Keep separate entities separate when the text treats them
as distinct people despite shared titles. Compute textual ranges, then editorially
remove ordinary-language homonyms and prophecy-only false prominence.

Summaries should answer who/what the entity is and why a returning reader cares.

## Event method

Use an event range wide enough to include necessary setup. Mark a peak chapter, not
merely the first title containing the event name. Include participants and locations
only when the text supports them.

## Intent method

Write intents as remembered questions or desires, for example:

- “I want to reread when the protagonist first meets X.”
- “Where is the truth about Y revealed?”
- “Start the campaign at Z with enough context.”
- “Show me the final battle and immediate aftermath.”

Give one to six ranked destinations. Explain why each destination is useful and start
one chapter earlier when context materially improves the reading experience.

## Canonical merge

Only one process writes canonical JSON. Draft workers may use local IDs, but the merge
step must deduplicate names, mint final IDs, rewrite all references, validate ranges,
and reject unknown references. Preserve drafts as evidence, not as runtime indexes.
