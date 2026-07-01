---
name: graphics-reverse-engineering-research
description: "Use for authorized graphics reverse engineering: shader/effect analysis, asset-format research, GPU-capture investigation, dual-track evidence ledgers, or viewer/prototype verification with legal and safety boundaries."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [graphics, reverse-engineering, shaders, webgpu, research, multi-agent]
    related_skills: [subagent-driven-development, systematic-debugging, spike]
    source_article: "https://x.com/Grummz/status/2062921270262726955"
---

# Graphics Reverse-Engineering Research

## Overview

Use this skill to understand an unknown visual effect, rendering pipeline behavior, shader technique, asset/file format, or graphics artifact from authorized samples and tool output. The workflow is based on a durable pattern from the Grummz/Grok Build Crimson Desert case study: give agents the right specialized tools, split the investigation into independent evidence paths, keep a shared findings ledger, cross-check hypotheses, and prove the result with a minimal viewer or reproduction.

This is a research and verification workflow, not a shortcut for illicit game hacking. Stay inside authorization boundaries, preserve evidence, and report uncertainty honestly.

## Choose the mode

- **Quick investigation** — one agent can inspect available files/captures and report a bounded hypothesis.
- **Dual-track research** — split evidence into data/assets and shader/code paths, then cross-check.
- **Multi-agent investigation** — use separate agents only when the evidence streams are independent enough to reduce bias.
- **Verification build** — create a minimal viewer, reproduction, or prototype when a hypothesis can be tested.
- **Safety-only methodology** — provide high-level guidance when authorization is unclear or the request approaches restricted activity.

Completion requires: authorization recorded, evidence ledger populated, hypotheses cross-checked, verification artifact produced or explicitly skipped with a reason, and final confidence/limitations stated.

## When to Use

Use this when the user wants to:

- Understand how a visual effect or rendering artifact is implemented.
- Analyze shader code, shader disassembly, GPU captures, renderdoc-style observations, or compiled shader blobs they are authorized to inspect.
- Reverse engineer an owned or permitted asset/file format for interoperability, modding documentation, preservation, debugging, or research.
- Coordinate multiple agents across data/assets and code/shader evidence streams.
- Build a small WebGPU/WebGL/native viewer to validate a graphics hypothesis.

Do **not** use this for:

- DRM bypass, copy protection circumvention, piracy, cheating, botting, credential theft, or online exploit development.
- Extracting or redistributing proprietary assets without permission.
- Circumventing a service's anti-cheat or access controls.
- Claims of certainty without independent evidence or a reproducible verification artifact.

## Safety and Authorization Gate

Before analysis, record the user's authorization and constraints:

1. What target is being analyzed?
2. Does the user own it or have permission to inspect it?
3. Are the files/assets public, open-source, user-created, or otherwise legally inspectable?
4. Are there terms of service, anti-cheat, DRM, NDA, or redistribution limits?
5. What outputs are allowed to be shared?

If authorization is unclear, restrict work to high-level methodology, public documentation, toy examples, or user-provided non-sensitive excerpts. If the request asks for bypassing protections, cheating, or exfiltration, refuse that part and offer a safe research or toy-example alternative.

See `references/legal-and-safety-boundaries.md`.

## Core Workflow

### 1. Define the phenomenon

Write a short research brief:

- Observable effect: what is seen?
- Expected baseline: what normal rendering/format behavior would be?
- Candidate explanations already considered.
- Available evidence: screenshots, videos, captures, shaders, files, logs, docs, source snippets.
- Verification target: what artifact would prove or falsify the explanation?

### 2. Inventory tools and evidence

Collect exact versions and inputs. Typical graphics research tools include:

- Shader compilers/disassemblers such as `dxc`, `fxc`, `spirv-dis`, `spirv-cross`, `glslangValidator`, vendor tools, or platform SDK tools.
- Decompilers/disassemblers such as Ghidra only for authorized targets.
- GPU/frame capture tools such as RenderDoc, PIX, Nsight, Radeon GPU Profiler, or safe screenshot/video captures.
- Domain-specific asset/model browsers, when legal and trusted.
- A browser/WebGPU/WebGL or native viewer for reproduction.

Save raw outputs under `evidence/` and never overwrite the original capture or decompile output.

### 3. Split into dual tracks

Use two independent evidence streams whenever possible:

- **Data/asset path:** file headers, byte layouts, geometry/material metadata, textures, height/normal maps, packing, coordinate systems, compression, bounds, and runtime resources.
- **Shader/code path:** shader stages, bindings, constants, compute kernels, rasterization path, culling, displacement, sampling, synchronization, CPU setup, and render pass order.

Give each track its own brief. Use the templates:

- `templates/agent-brief-data-path.md`
- `templates/agent-brief-shader-path.md`

### 4. Maintain a shared findings ledger

The ledger is the source of truth. Use `templates/findings-ledger.md` and keep sections for:

- Facts with evidence links.
- Hypotheses and confidence.
- Cross-check matrix.
- Contradictions.
- Open questions.
- Next probes.
- Verification/prototype status.

Each agent pass must write findings with citations to files, commands, screenshots, or code lines. Avoid free-floating guesses.

### 5. Cross-check hypotheses

A hypothesis is strong only if it survives an attack from the opposite path:

- If the shader path says a height map displaces micro-geometry, the data path should locate height data, scale factors, bounds, or metadata that could feed it.
- If the data path infers a tile/grid layout, the shader path should find dispatch sizes, threadgroup dimensions, buffer indexing, or culling logic consistent with that layout.
- If visual output shows a silhouette, code/shader evidence should explain why the silhouette can move rather than only surface shading.

Promote contradictions into the next pass instead of smoothing them over.

### 6. Escalate only when needed

If shader/capture analysis explains GPU behavior but not where inputs originate, escalate to CPU-side/source/decompiler analysis only when it is authorized and necessary. Ask targeted questions:

- Where are constants or buffers populated?
- Which asset fields feed the shader?
- Which render pass or material flag enables the behavior?
- What fallback path handles missing data or edge cases?

Do not perform broad binary trawling when a narrow evidence question is enough.

### 7. Build a verification artifact

The viewer/prototype is proof, not decoration. Build the smallest artifact that can falsify or support the hypothesis:

- Load a toy sample or authorized sample.
- Reproduce the key visual behavior.
- Document known limitations versus the original engine/hardware path.
- Capture screenshots/video from both the original observation and the reproduction.
- Use mismatches as evidence for another analysis pass.

For browser graphics, WebGPU is useful for compute-heavy experiments, but note limitations such as different atomic widths, browser API constraints, missing hardware tessellation/mesh shaders, and performance differences.

### 8. Final report

End with:

- Research question and target.
- Authorization/safety scope.
- Evidence sources and tool versions.
- Final explanation with confidence level.
- Cross-check matrix summary.
- Verification artifact path and how to run it.
- Known limitations and unresolved questions.
- What would change confidence up or down.

## Multi-Agent Recipe

When the task is large enough for subagents:

1. Orchestrator creates `findings/ledger.md` from `templates/findings-ledger.md`.
2. Agent A receives `templates/agent-brief-data-path.md` and writes `findings/data-path.md`.
3. Agent B receives `templates/agent-brief-shader-path.md` and writes `findings/shader-path.md`.
4. Orchestrator extracts contradictions and open questions into the ledger.
5. Repeat bounded passes against the highest-value questions.
6. A prototype/viewer agent builds only after there is a concrete hypothesis to verify.
7. A final review pass checks evidence citations and safety boundaries.

## Common Pitfalls

1. **Skipping authorization.** Reverse-engineering context matters. Clarify whether the target and outputs are permitted.
2. **Asking the model to stare at opaque binaries.** Give agents tools and narrow questions; preserve tool output as evidence.
3. **Letting two agents drift into duplicate work.** Data and shader/code tracks should attack different evidence streams.
4. **Treating preliminary findings as truth.** Every strong hypothesis needs cross-checking.
5. **Building the viewer too early.** Prototype after there is a specific behavior to reproduce.
6. **Ignoring visual mismatches.** Mismatches are diagnostic inputs, not embarrassment.
7. **Overfitting to a vendor-specific tool.** Keep the workflow portable across Grok Build, Codex, Claude Code, local CLIs, and human-driven tooling.
8. **Publishing proprietary details carelessly.** Final reports should respect licensing, NDAs, and redistribution constraints.

## Verification Checklist

- [ ] Authorization and output boundaries recorded.
- [ ] Research question is specific and falsifiable.
- [ ] Evidence inventory includes exact files/tool versions/commands.
- [ ] Data/asset and shader/code tracks have separate briefs.
- [ ] Findings ledger exists and contains facts, hypotheses, contradictions, and open questions.
- [ ] Strong hypotheses are cross-checked from the opposite evidence stream.
- [ ] Any decompiler/binary analysis is targeted and authorized.
- [ ] Viewer/prototype, if built, documents limitations and has comparison captures.
- [ ] Final report includes confidence levels and unresolved questions.

## References and Templates

- `templates/findings-ledger.md` — shared research ledger.
- `templates/agent-brief-data-path.md` — data/asset path brief.
- `templates/agent-brief-shader-path.md` — shader/code path brief.
- `references/grok-build-crimson-desert-case-study.md` — source article summary and reusable pattern.
- `references/legal-and-safety-boundaries.md` — safety framing for reverse-engineering requests.
