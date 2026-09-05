# Independent temporal and visual review

Keep the builder and critic separate. A fresh critic subagent is appropriate for a Blender prototype; a study-only task needs an evidence/semantic review rather than a forced render loop. Each critic owns only its report. Do not send desired scores, a suggested fix or private builder reasoning.

Supply the admitted originals, contract, current manifest/images and previous equivalent samples if present. Review chronological samples before the peak beauty view. A sampled sequence proves sampled frames; it cannot establish absence of flicker between samples. Add consecutive frames or playback when rapid fades, loop seams, motion blur or particle stepping are under review.

## Review priorities

1. **Evidence:** references and checkpoint match; images can be judged; hypothetical behavior is labeled.
2. **Meaning and primary shape:** visible action/state is unambiguous; actor/opening/boundary reads at the declared camera distance.
3. **Temporal structure:** gather, event, hold, aftermath and clear have distinct jobs; arrival/departure and break/expiry are not conflated.
4. **Layer hierarchy:** L1 survives Lite/no-accents; L2 explains direction; L3 supports scale/contact; L4 stays subordinate.
5. **Spatial behavior:** attachment, oblique view, floor contact and detached residue are consistent.
6. **Lifecycle:** evaluated cancellation, end/reset and relevant retrigger/loop seam leave no stray state or VFX.
7. **Delivery:** actual scene/dependencies reopen and requested exports are tested; no Blender-to-engine performance claim.

Hard failures include wrong state semantics, missing critical feature, unsupported source measurement, a covered primary read, mislabeled isolation/variant, stale evidence, orphaned effects after clear, and claiming engine proof from Blender. Use `unassessed` for a requested check that lacks evidence; do not score it as pass.

## Report shape

Return JSON with `critic_id`, `builder_id`, `contract_sha256`, `checkpoint_sha256`, `decision` (`accept`, `refine`, `conditional`), `checks` (rows with `id`, `status`, `sample_ids`, `finding`), `critical_features` (feature ID, status and sample IDs), `highest_impact` (one root cause or null), and `limitations`. Include a one-sentence verdict. The builder cannot author this report on the critic's behalf.

Use `accept` only for the declared fidelity/coverage level and when required checks pass. A simple workflow fixture can pass as a fixture while remaining unassessed as AAA visual reconstruction. If only stills were supplied, “source timing match” remains unassessed but a **proposed timing prototype** can pass on its own declared contract.

## Bounded task prompt

> Use the img2vfxblender review reference. Independently inspect the attached originals, contract and current captured frames/manifest. Do not edit the skill or scene. Review the full temporal/layer evidence, including clear, Lite and no-accents, and cite sample IDs. Judge against the contract's declared fidelity rather than a label in a filename. Return the report shape above, one highest-impact root cause if refinement is needed, and explicit unassessed areas. You are not the builder and have not authored this checkpoint.

After correction, a fresh critic receives the new evidence plus previous equivalent samples. Keep camera, resolution, timing and seed fixed unless the identified root cause is itself a contract/camera/timing error; record such an intentional comparison change. Default cap is three rounds. A second independent acceptance after the final correction is useful for complex production work, but do not create pointless required defects for already-passing simple fixtures.
