# Agent Brief: Data / Asset Path

## Mission

Investigate the data, assets, files, metadata, captures, and resource layouts that could explain the target visual/rendering phenomenon. Do not duplicate shader/code-path work except where needed for cross-checking.

## Inputs

- Research question:
- Target files / captures / samples:
- Known-safe tools:
- Findings ledger path:
- Output file for this pass: `findings/data-path.md`

## Constraints

- Work only on authorized inputs.
- Do not bypass DRM, anti-cheat, access controls, or encryption.
- Do not redistribute proprietary assets.
- Preserve original files; write derived notes separately.
- Cite evidence IDs or file paths for every factual claim.

## Questions to answer

1. What file/resource types are present?
2. What headers, magic bytes, dimensions, counts, bounds, offsets, or compression markers are visible?
3. What textures, height maps, normal maps, material parameters, or metadata could feed the effect?
4. Are there tile/grid/block structures in data that match observed rendering behavior?
5. Which fields might correspond to shader constants, buffers, or dispatch sizes?
6. What contradictions or missing data should the shader/code path investigate?

## Method

1. Inventory files and metadata.
2. Inspect small samples first; avoid broad destructive scans.
3. Record exact commands/tool versions in `evidence/` or the ledger.
4. Make conservative hypotheses and rank confidence.
5. Update the cross-check matrix with what the shader/code path should verify.

## Output structure

```markdown
# Data / Asset Path Findings

## Evidence inspected

## Facts

## Hypotheses

## Cross-check requests for shader/code path

## Contradictions / anomalies

## Recommended next probes
```
