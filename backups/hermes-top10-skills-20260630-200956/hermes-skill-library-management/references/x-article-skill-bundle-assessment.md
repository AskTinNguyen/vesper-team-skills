# X/Twitter article-to-skill-bundle assessment

Use this when a user shares an X/Twitter post or X Article and asks to save it and decide whether it should become one or more Hermes skills.

## Capture pattern

1. Resolve public metadata before browser scraping:
   - `https://publish.twitter.com/oembed?url=https://twitter.com/<user>/status/<id>` for basic author/post metadata and shortened link hints.
   - `https://api.fxtwitter.com/<user>/status/<id>` for richer tweet JSON, including `tweet.article.content.blocks`, `entityMap`, media URLs, captions, and article metadata.
   - `https://api.vxtwitter.com/<user>/status/<id>` as a fallback/quick metadata source.
2. Save a local archive under a stable, descriptive folder, for example:
   - `~/.hermes/saved-articles/YYYY-MM-DD-<author>-<slug>/article.md`
   - `source-fxtwitter.json`
   - `interesting-strings.txt`
   - `skill-bundle-assessment.md`
3. Convert article blocks to Markdown while preserving:
   - source tweet URL
   - article ID / article URL
   - author and creation timestamp
   - cover image URL
   - embedded media captions / media IDs or URLs when available
4. Recursively scan the raw JSON for strings containing likely leads such as `github`, `skill`, `agent`, `prompt`, `build`, CLI install snippets, tool names, or domain-specific terms.

## Assessment pattern

Judge the article at the class level, not as a one-session micro-skill.

Ask:

- What reusable workflow or decision procedure does this article teach?
- Is it a maintained upstream skill/package, or just a case study that should become a reference?
- Which parts are durable versus vendor-, date-, or account-specific?
- Does the topic need safety/legal boundaries before becoming an always-available skill?
- Should this be one umbrella skill with `references/` and `templates/`, or several standalone skills?

Prefer one umbrella skill plus support files when the post is a single case study. Split into multiple skills only after repeated use proves the sub-workflows recur independently.

## Recommended output file: `skill-bundle-assessment.md`

Include:

- Short verdict: yes/no/partial.
- Reusable workflow extracted from the article.
- Candidate class-level skill names and categories.
- Recommended bundle structure.
- Safety/legal constraints if relevant.
- Why not to create narrow skills immediately, if applicable.
- Suggested next action.

## Pitfalls

- Do not treat an article's title, product name, or one-off example as the skill name unless it is truly the class of work.
- Do not install a bundle immediately when the source is only a case study and not a maintained upstream skill package.
- Do not preserve only a social-post summary; archive the raw article JSON and converted Markdown so future agents can re-check the extraction.
- Do not hard-code vendor-specific beta access or install commands as durable procedure unless the skill is explicitly about that vendor.
- For reverse-engineering/security-adjacent topics, frame skills around authorized research and verification workflows, not bypass, exploitation, or asset extraction.
