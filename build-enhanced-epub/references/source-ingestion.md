# Source ingestion

## PDF with embedded text

1. Inspect metadata, encryption, page count, fonts, and extractability.
2. Use Poppler `pdftotext -layout` to preserve useful page structure.
3. Split on form-feed so source-page provenance remains available.
4. Detect chapter headings only in the content region. Exclude TOC pages.
5. Join paragraph fragments across page breaks conservatively.
6. Render the first page with `pdftoppm` for the cover when appropriate.

Use the PDF skill when visual layout or OCR quality must be inspected. Compare a
sample of extracted pages with rendered images before trusting a heading regex.

## Scanned PDF

Render pages, OCR with the appropriate language model, retain confidence or audit
samples, and never claim exact text fidelity without spot checks. Separate OCR output
from the original scan. Prefer manual correction of headings before prose cleanup.

## HTML chapter site

Inspect the viewer and network-visible page structure before writing a crawler.
Prefer stable chapter IDs or canonical URLs over visible next/previous labels. Cache
each fetched response. Use a descriptive user agent, rate limiting, retry/backoff,
and resume support. Stop if access controls, robots policy, or site terms prohibit
the intended collection.

Extract only title and chapter body. Remove navigation, ads, comments, breadcrumbs,
and repeated headers using source-specific selectors. Preserve source URL per chapter.

Use browser control only when interactive inspection or an existing authorized login
is required. Do not automate around CAPTCHAs or anti-bot controls.

## Plain text or structured files

Detect encoding, normalize line endings, and identify chapter boundaries without
destroying paragraph breaks. If filenames determine order, parse order explicitly and
reject ambiguous lexical sorting such as `1, 10, 2`.

## Download safety

- Require an explicit rights acknowledgement flag for commands that download a book.
- Download to a temporary file, verify media signature and plausible size, then rename.
- Compute SHA-256 of the source.
- Avoid downloading again when a verified cache exists.
- Store credentials outside the project and never emit them in logs.
