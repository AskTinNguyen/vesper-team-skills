# Agent Brief: Shader / Code Path

## Mission

Investigate shader code, disassembly, GPU captures, render pass behavior, compute kernels, binding layouts, and authorized implementation snippets that could explain the target visual/rendering phenomenon. Do not duplicate data/asset-path work except where needed for cross-checking.

## Inputs

- Research question:
- Shader files / disassembly / captures / snippets:
- Known-safe tools:
- Findings ledger path:
- Output file for this pass: `findings/shader-path.md`

## Constraints

- Work only on authorized inputs.
- Use decompiler/disassembly tools only where permitted.
- Do not bypass DRM, anti-cheat, access controls, or encryption.
- Preserve raw tool outputs; write interpretations separately.
- Cite evidence IDs, command outputs, file paths, or line numbers for every factual claim.

## Questions to answer

1. Which shader stages or compute passes are involved?
2. What buffers, textures, samplers, constants, and dispatch dimensions are referenced?
3. Is there evidence for displacement, parallax, ray marching, tessellation, mesh/task shaders, screen-space grids, software rasterization, culling, or hole filling?
4. What coordinate spaces and transforms are used?
5. Where could data/asset-path fields feed this shader/code path?
6. What runtime visuals should a verification viewer reproduce?

## Method

1. Inventory shader/code artifacts and tool versions.
2. Preserve raw disassembly/decompile output under `evidence/`.
3. Identify resources, constants, loops, atomics, barriers, texture samples, and write targets.
4. Form hypotheses with exact evidence citations.
5. Ask the data/asset path to verify required input data and metadata.
6. Propose a minimal prototype/viewer behavior that would verify the hypothesis.

## Output structure

```markdown
# Shader / Code Path Findings

## Evidence inspected

## Facts

## Hypotheses

## Cross-check requests for data/asset path

## Verification viewer requirements

## Contradictions / anomalies

## Recommended next probes
```
