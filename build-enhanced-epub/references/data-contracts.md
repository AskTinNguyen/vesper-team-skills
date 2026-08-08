# Data contracts

## Library layout

```text
library/<book-slug>/
├── metadata.json
├── cover.jpg
├── source.*
└── chapters/
    ├── 0001.json
    └── ...
```

## metadata.json

Required fields:

```json
{
  "title": "Book title",
  "author": "Author",
  "language": "vi",
  "source_url": "https://example.test/book",
  "cover_file": "cover.jpg",
  "expected_chapters": 492,
  "rights": "Personal offline copy; do not redistribute"
}
```

Add source checksum, page count, extraction count, original title, and source file
when available.

## Chapter JSON

```json
{
  "order": 1,
  "chapter_id": "source-id-or-number",
  "display_label": "Chương 1",
  "title": "Chapter title",
  "paragraphs": ["First paragraph.", "Second paragraph."],
  "checksum_sha256": "...",
  "source_url": "https://example.test/chapter/1",
  "source_page_start": 10,
  "source_page_end": 18,
  "source_credit": "Source attribution"
}
```

`order`, `chapter_id`, `display_label`, `title`, `paragraphs`, and checksum are the
portable core. Source URL and PDF page fields are optional by source type.

## Index documents

Each document has `schema_version: 1` and one top-level array.

### Arc

Required: `id`, `title`, `summary`, `start_chapter`, `end_chapter`, `themes`,
`search_terms`, `characters`, `locations`, `factions`, `key_chapters`.

Each key chapter has `chapter`, `label`, and `reason`.

### Entity

Required: `id`, `name`, `type`, `aliases`, `summary`, `first_chapter`, `arc_ids`,
`important_ranges`, `related_entities`.

Entity type is one of `character`, `location`, `faction`, `concept`. Each important
range has `start`, `end`, and `label`.

### Event

Required: `id`, `title`, `summary`, `start_chapter`, `end_chapter`, `peak_chapter`,
`arc_ids`, `participants`, `locations`, `search_terms`.

### Intent

Required: `id`, `category`, `title`, `description`, `search_terms`, `destinations`.
Each destination has `chapter`, optional `end_chapter`, `label`, `reason`, `priority`,
and `arc_id`.

Recommended categories:

- Identity and mysteries
- Characters and relationships
- Eras and history
- Places and journeys
- Battles and confrontations
- Reform, cultivation, and power
- Revelations and reversals
- Ending and extras

Localize category display strings to the book language, but keep them consistent
within the project.
