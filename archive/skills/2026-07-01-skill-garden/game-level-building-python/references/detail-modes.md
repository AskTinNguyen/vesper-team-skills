# Detail Modes

Use detail modes when the user wants more scene depth than a pure blockout.

## Recommended Modes

- `blockout`: dominant masses only, fastest iteration
- `low`: restrained secondary forms that sharpen silhouette readability
- `medium`: visible decorative support pieces for scene richness
- `high`: a clearly more expressive architectural pass with stronger roof hierarchy, ceremonial entry composition, foreground layering, and regional character

## Backward Compatibility

If an older script or request uses:

- `ornamented`, treat it as `medium`
- unknown detail strings, fall back to `blockout`

## Detail Toggle Pattern

Expose this near the top of the script:

- `DETAIL_MODE = "blockout"`, `"low"`, `"medium"`, or `"high"`
- `DETAIL_PROFILE = { ... }` or preset-driven detail toggles

Useful toggles:

- `add_eaves`
- `add_ridge_caps`
- `add_lanterns`
- `add_totems`
- `add_tree_markers`
- `add_fence_segments`
- `add_path_posts`
- `add_corner_finials`
- `add_bridge_rails`
- `add_deep_roof_tier`
- `add_front_colonnade`
- `add_gate_composition`
- `add_processional_forecourt`
- `add_axial_frontispiece`
- `add_ceremonial_stair`

Primitive-language upgrades can also be part of detail mode:

- replace single boxes with layered cylinders, cones, and spheres when they better communicate the archetype
- use segmented curves or bead chains as a spline-like fallback when full spline authoring would make the generator brittle
- use restrained color-role accents when the available primitive material supports tinting

## Calibration Rule

Treat the modes as progressive layers:

- `low` should make the silhouette feel more architectural
- `medium` should make the scene feel intentionally dressed
- `high` should feel intentionally authored, with a meaningful compositional jump over `medium` instead of just more props
- `high` can deepen the entry sequence and roof hierarchy when that reinforces the target architectural language

## Replication Procedure

When applying detail modes to a new template:

1. keep the base `blockout` pass unchanged
2. make `low` add silhouette-supporting architectural detail only
3. make `medium` add readable decorative scene elements
4. make `high` add a design-led composition layer, not just denser tertiary accents
5. for Chinese compounds, prefer stronger eave stacking, screen walls, gate frames, colonnades, paired ceremonial markers, and processional forecourts
6. let `high` strengthen the arrival experience and roof silhouette, but do not break the base traversal logic
7. keep mode names and progression meaning consistent across templates

## Chinese Architecture Heuristic

When the target is Shang, Zhou, Han-adjacent, or Three Kingdoms inspired architecture, make `high` read as a stronger axial composition:

- widen and layer roof skirts before adding random ornaments
- reinforce the front bay with columns, lintels, and entry framing
- let high-detail stairs and entry platforms become more ceremonial when the template is axial
- add paired elements symmetrically: lanterns, steles, pillars, trees, screen walls
- prefer cypress-like or layered tree silhouettes over generic round canopies when the goal is classical Chinese atmosphere
- use foreground pieces to suggest ceremonial sequence, not clutter
- prefer a few larger, legible gestures over many tiny scattered details

## Design Rule

Treat detail mode as a second pass layered on top of stable blockout masses.

Do not let decorative pieces replace core silhouette readability.

## Verification

When detail mode is enabled, confirm:

- the main blockout still reads clearly from a distance
- decorative actors are organized under the same output folder
- rerunning still replaces prior actors cleanly
- the added detail supports the intended style instead of noisy clutter
- `low`, `medium`, and `high` each read as distinct steps rather than tiny variations
- `high` reads as a stronger cultural and architectural statement from the camera's first glance
