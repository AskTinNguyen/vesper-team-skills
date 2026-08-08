# QA checklist

## Source and corpus

- Verify source signature, checksum, page/response count, and extraction encoding.
- Verify chapter orders are unique and exactly continuous.
- Compare detected count with expected count.
- Flag empty or unusually short chapters.
- Detect duplicate content checksums.
- Search for TOC, site chrome, header/footer, OCR, and encoding leakage.
- Inspect first, middle, repaired, and final chapters manually.
- Record every source repair.

## Semantic index

- Validate JSON syntax and schema version.
- Validate unique ASCII slug IDs.
- Validate chapter and range bounds.
- Cover all chapters by arcs without gaps or overlaps.
- Resolve every cross-reference.
- Keep destination priorities unique per intent.
- Ensure every intent has search terms, a reason, and a valid arc.
- Spot-check arc boundaries against chapter prose.
- Spot-check aliases and false-positive homonyms.

## EPUB package

- Check uncompressed first `mimetype` entry.
- Parse all XML, OPF, NCX, and XHTML.
- Verify every manifest, spine, href, src, and fragment target.
- Verify one EPUB 3 nav document and a non-empty NCX.
- Verify cover declaration and media type.
- Verify chapter and guide counts.
- Reject duplicate ZIP entries.
- Reject network URLs, scripts, and event handlers from offline guide pages.
- Run EPUBCheck when available.
- Open on the target reader and test navigation, font resizing, dark mode, search,
  bookmarks, and at least five deep links.

## Regression tests

Test heading parsing, malformed known headings, TOC exclusion, cross-page paragraph
joining, index coverage, category coverage, EPUB ZIP invariants, and link validation.

## Handoff report

Report chapter/page/paragraph/character counts, number of arcs/entities/events/intents,
test totals, validator results, file size, SHA-256, repairs, tool limitations, and
personal-use restriction.
