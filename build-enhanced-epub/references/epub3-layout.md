# EPUB 3 layout

## ZIP invariants

- First entry: `mimetype`.
- Exact content: `application/epub+zip`.
- Store it uncompressed.
- Include `META-INF/container.xml` pointing to the OPF.

## Recommended package

```text
OEBPS/
├── content.opf
├── nav.xhtml
├── toc.ncx
├── cover.xhtml
├── images/cover.jpg
├── styles/book.css
├── guide/
│   ├── start.xhtml
│   ├── story-map.xhtml
│   ├── intents.xhtml
│   ├── characters.xhtml
│   ├── locations.xhtml
│   ├── factions-concepts.xhtml
│   └── events.xhtml
└── text/chapter-0001.xhtml
```

## Metadata

Include stable identifier, title, creator, language, source, modification timestamp,
cover, and rights statement. Derive a deterministic UUID from a stable source key if
the source has no ISBN or canonical identifier.

## Navigation

Place Start, Story Map, Intent index, and lookup pages before the full chapter list.
Nest arcs below Story Map and chapters below “All chapters.” Include NCX for older
readers. Add the guide pages to the spine before chapters; make `nav.xhtml` a legal
non-linear spine target when guide pages link to it.

## XHTML and CSS

Generate XML-safe XHTML with language metadata and no script. Escape text and remove
XML 1.0 control characters. Use relative links. Give every semantic record a stable
anchor ID. Keep styling typographic and reader-friendly; do not force colors that
break dark mode. Avoid fixed layouts for prose books.

## Atomic build

Write to a temporary file in the destination directory, validate it, then rename it
to the final path. This prevents a failed build from replacing a known-good EPUB.
