---
name: ian-xiaohei-illustrations
description: "Generate Ian Xiaohei-style in-article illustrations, especially for Chinese articles, posts, blogs, Notion docs, workflow docs, methodology notes, processes, structures, states, metaphors, or opinions. Use when the user asks for weird, Xiaohei, hand-drawn, body illustration, article illustration, illustration suggestions, shot lists, title removal, or image cleanup. Default visual language: Xiaohei IP character, pure white hand-drawn sketch, sparse red/orange/blue handwritten Chinese annotations, clean airy composition, imaginative but readable."
version: 1.0.0-english-adapted
author: Ian / helloianneo; English adaptation by Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [illustration, image-generation, chinese, hand-drawn, xiaohei, article-illustrations]
    homepage: https://github.com/helloianneo/ian-xiaohei-illustrations
    source: https://github.com/helloianneo/ian-xiaohei-illustrations/tree/main/ian-xiaohei-illustrations
---

# Ian Xiaohei Weird In-Article Illustrations

## Core purpose

Design and generate 16:9 horizontal in-article illustrations for Chinese writing. The goal is not commercial illustration, PPT infographics, or cute cartoons. The goal is to turn a key judgment, process, structure, state, or metaphor from the article into a clean, strange, memorable, readable hand-drawn explanatory sketch.

The default visual IP is **Xiaohei**: a small solid-black creature with white dot eyes, thin legs, and a blank serious expression, doing something absurd but conceptually valid. Xiaohei must participate in the core action of the image, not stand aside as decoration.

This English-adapted version is written for English-language users. It still intentionally produces **short Chinese handwritten labels** by default because that is part of the visual identity. If the user wants English labels, bilingual labels, or no text, follow that request while preserving the rest of the style.

## Safety and rights note

This skill is adapted from the MIT-licensed public repository `helloianneo/ian-xiaohei-illustrations`. Keep attribution when redistributing. Do not present generated images as official Ian artwork unless Ian made them. Use the examples only for style calibration, not for direct copying.

## Read references as needed

Do not load everything by default. Read only what the task needs:

- `references/style-dna.md`: style DNA, colors, text rules, and hard bans.
- `references/xiaohei-ip.md`: Xiaohei's appearance, personality, action library, and bans.
- `references/composition-patterns.md`: structure types, original-metaphor method, and anti-copy rules.
- `references/prompt-template.md`: image-generation prompt template for one image.
- `references/qa-checklist.md`: post-generation QA and iteration rules.
- `assets/examples/`: low-frequency visual calibration only. Do not copy the compositions, objects, or annotations.

## Workflow

### 1. Digest the source text

First read the user-provided article, link content, Notion page, Markdown file, screenshot, or topic. Extract:

- the central claim
- paragraphs that create a cognitive turn
- parts that benefit from visual explanation
- parts that are better left as text

Do not illustrate evenly. Prioritize **cognitive anchors**, such as a core judgment, two breakpoints, input-output loop, branching, before/after contrast, one asset used many ways, handoff path, common pitfalls, or role-state change.

### 2. Produce an illustration strategy first when requested

If the user asks to “analyze how to illustrate this”, “think about where images are needed”, “make a shot list”, or similar, do not generate images yet. Provide a short shot list. For each image, include:

- placement after which paragraph or section
- image theme
- core idea
- structure type
- what Xiaohei is doing
- suggested elements
- suggested short Chinese annotation words

Default to 4-8 images. For a short article, 1-3 images. Even for long articles, avoid exceeding 9 unless clearly needed. Good enough is better than turning the article into an art book.

### 3. Generate single images

If the user explicitly asks to “generate”, “output”, “make images”, or “create illustrations”, do not stop for confirmation. Use the available image-generation tool and generate each image separately. Do not combine multiple illustrations into one collage.

Each image should express one core structure only. The prompt must include:

- 16:9 horizontal Chinese in-article illustration
- pure white background
- black hand-drawn line art
- sparse red/orange/blue handwritten Chinese annotations
- lots of empty space
- Xiaohei as the core action subject
- bans: no PPT, no commercial illustration, no childish cuteness, no complex architecture diagram, no top-left type title

Do not replicate previous examples. Examples provide only style density and Xiaohei participation guidance. Do not directly reuse existing compositions such as “conveyor belt breakpoints”, “Xiaohei pulling a lever inside a content machine”, “material fish”, “stamping toolbox”, or “common-pit path” unless the user explicitly asks to recreate a specific image. Re-invent a fresh strange-but-valid metaphor from the current article every time.

### 4. Check and iterate

After generation, check `references/qa-checklist.md`. Regenerate or edit first if any of these occur:

- Xiaohei is only decorative
- the canvas is too crowded
- it looks like a PPT slide or formal flowchart
- there is too much Chinese text or severe typo noise
- the top-left contains a title such as “common pitfalls”, “workflow”, or “system architecture”
- the style is too cute, childish, rigid, or over-polished
- the background is not clean white

### 5. Save and deliver

If the user is working inside a workspace, copy final images to:

```text
assets/<article-slug>-illustrations/
```

Name them in order:

```text
01-topic-name.png
02-topic-name.png
```

Keep original generated files. Do not overwrite existing assets unless the user explicitly asks to replace them.

## Output style

Before generation, strategy output should be short and precise. After generation, delivery should include:

- how many images were generated
- the purpose of each image
- save path
- which images are strongest and which are optional

Do not give a long lecture about the style theory. Let the images speak.
