<required_reading>
Read these first:
- `../references/ai-native-interaction-doctrine.md`
- `../references/option-action-depth-operating-model.md`
</required_reading>

# Apply Option-Action Depth

Use this workflow when implementing or reviewing a Vesper surface that deepens under the desktop lean-in modifier.

## Start Here

Before designing or coding:

1. Name the target surface.
2. Decide whether the work is desktop-only or must be cross-platform.
3. Inspect an existing Vesper example if one exists.
4. Write the surface contract before touching code.

## Platform Mapping

Use the semantic term `lean-in modifier` in design thinking.

Desktop mapping:
- macOS: `Option`
- Windows/Linux: `Alt`

Implementation guidance:
- implement against `event.altKey`
- render user-facing copy with platform-aware labels such as `Option` or `Alt`
- avoid making the doctrine depend on a Mac-only name

## Workflow

1. Name the base user intent in one sentence.
2. Define the default action without AI depth.
3. Define the lean-in variant of that same action.
4. Choose the first deeper reveal:
   - explanation
   - suggestion
   - delegation
   - automation
5. Write the surface contract:
   - target
   - scope boundary
   - signal source
   - freshness or evidence
   - manual fallback
   - exit path
6. Add a subtle discoverability cue if needed.
7. Verify pointer, keyboard, and focus behavior.
8. Check the result against the doctrine ship gate.

## Verification

Use this pass/fail checklist:

1. Plain hover never mutates state or opens detached windows.
2. Plain click still performs the normal manual action.
3. Lean-in hover or lean-in focus reveals the deeper layer without changing scope.
4. Lean-in click delegates or opens a scoped AI workflow, not an unrelated global action.
5. Releasing the modifier collapses or reverts the deeper state cleanly.
6. Important actions remain reachable without the modifier.
7. Keyboard focus can reach the same reveal path as pointer hover.
8. Reduced-motion mode keeps the same meaning without decorative motion.
9. Recommendation evidence is legible enough to trust.

## Done Criteria

The work is done when:

1. The base UI stands on its own.
2. The lean-in trigger deepens the same gesture.
3. The deeper action stays scoped to the touched target.
4. The first reveal improves understanding before pushing automation.
5. Manual fallback exists.
6. Exit behavior is clear.
7. Pointer, keyboard, and focus paths are verified.
8. The recommendation source is specific enough to trust.

## Use Alongside

Pair this workflow with adjacent Vesper skills when needed:
- `build-electron-features` for implementation that crosses renderer, preload, and main
- `vesper-electron-testing` for renderer and Electron verification
- `ui-design-pipeline-superdesigner` for pattern exploration and direction selection
- `polish` when the interaction is working and needs final UX refinement
