# Evidence and temporal contract

The JSON contract binds source evidence to intended output. `vfx_contract.py` checks structural and provenance invariants; independent inspection judges fidelity. Schema version 1 is local to this skill and is not an Unreal import format.

## Admission

Each reference has `id`, `path`, `sha256`, `kind` (`original`, `derivative`, `video-frame`), and a description. Paths are relative to the contract, unless a caller deliberately uses an external path. Copy originals into the project with the user's existing authorization when portable delivery is needed. Derived AI boards may be admitted for presentation but cannot be the sole supporting source of a critical observed feature.

Each `feature` has `id`, `layer`, `priority`, `description`, `evidence_class`, `reference_ids`, `phase`, `targets`, and `disposition`. Classes are `observed`, `author-reported`, `hypothesis`, `proposed`. Dispositions are `implement` or `omitted`, with a concrete `reason` for omissions. Do not merge a shader guess into an observed fact. Layer-stack rows imported from the study catalog are proposed implementation goals; they do not suddenly become observed geometry.

Use extra feature rows for particulars such as a vertical rift that narrows, bright grains fading before dark falling grains, continuous floor contact, paired inward strands, or detached residue. A four-row generic layer mapping is a starting point, not exhaustive feature analysis. Preserve raw source notes in `source_notes` and record `coverage_note` explaining exclusions or remaining interpretation.

## Prototype contract

Fill `prototype` only when making an animation. Record:

- `fps`, `frame_start`, `frame_end`, `seed`, and `timing_basis`: `proposed` or `measured`;
- `events`: named frame anchors with basis; measured anchors require a video-frame source and timestamp evidence;
- `scale_basis`: known measurement or a declared proxy assumption; Blender units are meters by default;
- `builder_id` and `checkpoint`: nonempty identity and existing `.blend`;
- `samples`: unique `id`, `scene`, `camera`, `frame`, `role`, `variant`, `scenario`;
- temporal `before`, `event` and `clear` samples bind to same-named event anchors, ordered before < event < clear in the normal scenario; extra loop/cancellation anchors have distinct names;
- `required_roles`: minimum evidence roles actually needed for this recipe;
- `expected_clear_samples`: IDs that must contain no visible VFX objects;
- `required_feature_samples`: critical feature IDs mapped to sample IDs where they must be evaluated.

Suggested roles for a short burst: `before`, `gather`, `event`, `residue`, `clear`, `oblique`, `lite`, `no-accents`, `isolate-l1`, `isolate-l2`, `cancel-clear`. Add `hold`, `loop-seam`, `retrigger`, `bright-background`, `near`, and `far` only as applicable. At least one Standard gameplay view, one actual Lite and no-accent view, temporal event/clear samples, and an oblique view are required for a claimed animated prototype. Meaningful layer isolation is required for the implemented L1–L4 layers; the tool checks those roles against layer presence.

An original multi-panel board is not a calibrated camera reference. Use `camera_basis: proposed-gameplay` unless reference framing is actually solved. Do not call an oblique camera “orbit” when its transform equals the gameplay camera. Declare intentionally view-dependent cards and their acceptable angular range rather than requiring irrelevant rear views.

## Scene bindings

Map implemented features to exact object names in `targets`. Tag each renderable VFX object with `vfx_layer` (`L1`…`L4`) and `vfx_feature_id`. L0 belongs to the contract/proxy demonstration, not an emitter. Required feature evidence may need multiple target objects; capture audits each name. Environment, actors and ground proxies are outside those tags so their persistence does not fail an effect-clear sample.

Each scene has `vfx_variant` and `vfx_scenario`, agreeing with sample metadata. A Lite scene must actually reduce support/accent work while preserving the essential read. A cancel scene must evaluate an interrupted event, not merely relabel the normal final frame. For no-accents/isolation samples, collection visibility can remove layers; capture records actual visible tags. The verifier rejects mislabeled no-accent and isolation samples and uncleared tagged VFX at declared clear samples. It cannot prove visual meaning from tags.

The `event` role is a Standard/normal gameplay sample. Required Lite, no-accents, oblique and isolation comparisons use that same event frame and normal scenario, so a quiet tail cannot masquerade as a cheaper or cleaner variant. Temporal samples carry `anchor`; additional samples may omit it. Visibility audit lists must be present even when empty. Render eligibility is audited separately from pixel opacity and viewport visibility; authors hide completed tagged objects from rendering after their fades.

## What the manifest proves

Capture records actual Blender version, checkpoint/contract/source hashes, per-frame image hashes, engine, resolution, FPS, color settings, camera matrix, scene names, seed and visible feature/layer tags. Verification rejects stale contract/checkpoint/reference/image hashes, missing samples, absent targets and semantic label mismatches that can be checked mechanically. A source hash proves file identity, not source-game authenticity. Passing this check means **evidence integrity**, not visual approval.
