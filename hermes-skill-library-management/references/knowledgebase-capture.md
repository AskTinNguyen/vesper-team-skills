# Knowledgebase capture

Former standalone skill `knowledgebase-capture`, preserved as a reference under the skill-library management umbrella during consolidation.

Use these notes when skill-library work needs to capture, archive, distill, or publish web items/posts/articles into a durable personal knowledgebase.

## Goals

- Preserve original sources with enough metadata to cite them later.
- Convert thin source material into reusable knowledge: summary, insights, action prompts, deeper questions, and operating principles.
- Save reader-compatible markdown rather than only responding in chat.
- Verify that the saved artifact exists and, when available, that the reader/build pipeline indexes it.

## Workflow

1. **Fetch source content.**
   - For X/Twitter URLs, first try browser snapshots for visible text.
   - If X blocks replies/full content, use public mirrors/APIs such as `https://api.fxtwitter.com/<user>/status/<id>` or `https://api.vxtwitter.com/<user>/status/<id>`.
   - For X Articles, reconstruct `tweet.article.content.blocks`; for `atomic` blocks, resolve entity ranges against `entityMap`; preserve `MARKDOWN` entities verbatim and label media/embedded tweets.
   - For public Google Drive links, extract file id and try `https://drive.google.com/uc?export=download&id=<file_id>`; for PDFs verify `%PDF` and save under KB `_sources/` before extracting text.
   - Preserve the canonical source URL even if extraction used a mirror or direct-download endpoint.
2. **Locate knowledgebase conventions.**
   - Check existing project/readme scripts for root, folder naming, frontmatter, and build/publish commands.
3. **Write reader-compatible markdown.**
   - Include YAML frontmatter such as `title`, `source`, `author`, `date`, `type`, `tags`, `visibility`, and `summary` when supported.
   - Use a stable filename like `YYYY-MM-DD-topic-slug.md` and a topical folder.
4. **Structure extraction for future action.**
   - Recommended sections: Short summary, Source snippet, Valuable extraction, Thought-provoking snippets, Action prompts, Deeper questions, Practical operating principle.
5. **Verify.**
   - Read back or stat the saved file.
   - If a reader sync/generation command exists, run it when safe and verify manifest/index inclusion.
   - For Tin reader on Windows, `bun run sync` from `C:/Users/Admin/tin-research-reader-secure` regenerates `site-data/posts`; after syncing, search for the generated JSON slug under `site-data/posts`.
   - For Tin reader on Windows, `bun run sync` may hit a `C:\\C:\\...` path-normalization bug; use the `fileURLToPath(import.meta.url)` sync-script workaround documented in Tin references.

## Quality bar

- Do not merely summarize; turn the source into reusable prompts for decisions, behavior, or deeper thinking.
- Keep quotes faithful and separate quoted source from synthesis.
- Avoid inventing missing thread items.
- Make the note useful even if the original URL disappears.

## Pitfalls

- X may show only the first post when unauthenticated.
- Do not let transient local setup issues become permanent assumptions.
- On Windows hosts, verify actual path formats used by the reader.
