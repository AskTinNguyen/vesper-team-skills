# Blender VFX authoring and capture

## Scene conventions

Use meters and record any inferred dimensions. Keep `REFERENCE`, `PROXIES`, `VFX_L1`, `VFX_L2`, `VFX_L3`, `VFX_L4`, `CAMERAS`, and `LIGHTS` separable. Collections are useful organization; actual object tags and visibility are what the capture audit records. For complex Geometry Nodes, identify the node group and exposed sockets in the feature description and bind the evaluated output object.

Use curves/tapered strips for coherent flow, mesh surfaces for stable boundaries, instancing for sparse detail, and shader masks for subpixel variation. Do not create hundreds of separate objects for a production particle family just because a small test fixture does. Emission and intentional transparency are valid VFX materials. Dark backgrounds and bloom must not hide weak silhouettes or opaque disks masquerading as portals.

Preserve procedural source geometry and editable animation. For keyed VFX, use explicit interpolation: linear/controlled curves for measured movement, deliberate ease for buildup, and stepped visibility only when hidden transitions are intentional. Opacity should usually handle final dissolve rather than shrinking every particle to a visible point. Stable seeds make repeated captures comparable.

## Temporal truth

Separate attachment from simulation space. Charge follows the body; departure residue remains at the old world transform; arrival pre-roll belongs to the accepted destination. Shield fragments detach on the break event. A portal surface should not drag its interaction wave as the actor traverses.

For analytic/keyframed animation, arbitrary `frame_set` evaluation can be valid. For physics, Geometry Nodes simulation zones and cached systems, bake or step from the simulation start before rendering samples. The capture helper steps frames in increasing order within each scene; this is not a substitute for baking simulations whose cache is external or nondeterministic. Record bake path and seed in the delivery notes.

Cancellation is a separate evaluated scenario. If the event was not committed, stop buildup without playing the accepted-use signal. If it was committed, preserve state truth and clear residual cosmetics using the owner's policy. Retrigger must reset or layer intentionally, not inherit a half-dissolved material.

Review a post-event frame before the final clear: a shrinking intact shield can still communicate protection after a declared break. Remove/dissolve that silhouette and let detached debris carry the aftermath. For portal interaction, separate the ready loop, outward accepted-use wave and flatter residue so one generic scale curve cannot impersonate all three. Check focal accents in the composite as well as isolation; an actor proxy may fully occlude a correctly tagged glint.

Check the motion of each bound layer across the buildup. A contracting ring does not prove convergence if its supporting grains move outward. Author particle positions around an explicit focal point, and keep any post-event release distinct from the gather phase.

## Camera, light and display

Lock reference/playback camera transforms between corrections. Review an oblique view to expose paper-thin or intersecting constructions within the required viewing cone. In a third-person study include an actor proxy and world plane so scale, grounding and occlusion can be judged. Do not add a matched-camera claim when only a board is available.

Set renderer, FPS, resolution, samples, world, exposure and display transform explicitly. Use the installed Blender RNA/API to discover version-sensitive settings. Emission/alpha, compositor glare, refraction and material surface rendering changed across Blender versions; avoid copying removed properties such as legacy Eevee bloom flags. Keep glare separate and removable. Review dark and light backgrounds before declaring contrast robust.

A Standard/Lite pair changes only documented layer complexity, not semantic event timing or primary extent. No-accents disables L4 and optical post effects; it must still read. Isolated-layer renders need the actual layer alone against the same camera/ground reference, not four copies of the full composite.

Map each promised Lite reduction to actual objects, node controls or material features and verify the resulting image. Reducing dust count alone cannot satisfy a contract that also removes secondary flow.

## Capture helper

`capture_vfx.py` opens the supplied contract, validates prototype fields, and operates on the already-open `.blend`. It validates scene/camera identities and feature targets before rendering, then evaluates samples sequentially per scene. It saves PNGs and `manifest.json` into a new output directory. The input checkpoint is never saved over.

Scene variants must already exist. Use per-scene collection exclusions or separate datablocks for variant-specific animation. Beware copying a scene while linking object data: changing an Action or material can alter Standard and Lite together. Validate the final file by reopening it for capture; in-memory success is not delivery proof.

Pass `--python-exit-code 1` before `--python` in headless commands: Blender may otherwise print a Python traceback and exit zero. Check the success marker and complete manifest as well as process status. In Blender 5.2, legacy `Scene.use_nodes` is not a reliable compositor enable flag; use render compositing settings and the actual compositor node group. Audit render collection exclusions independently from viewport hiding.

## Export decision

Keep the `.blend` as the procedural authoring source. Export only the deliverable requested:

- **Mesh/curve bake:** choose scale, axes, origin, UVs, normals and supported animation deliberately; reopen the actual export in a clean scene.
- **Flipbook:** lock frame count/FPS, camera and transparent background; export color/emission and alpha with explicit straight/premultiplied convention. Document atlas rows/columns, padding, orientation, looping and color spaces. Test edge halos against light/dark backgrounds and a full loop seam.
- **Mask/normal/distortion texture:** separate data channels from display-managed color. A beauty PNG is not a calibrated refraction/normal map.
- **Volumetric sequence:** confirm target format, cache path, frame rate and renderer/engine support before authoring a heavy simulation.

None of these automatically serializes Blender nodes or simulation behavior into Niagara.
