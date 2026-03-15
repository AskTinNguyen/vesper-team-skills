# Unreal Python Compatibility

## Tested Framing

- Treat this skill as editor-only Unreal Python guidance.
- Prefer UE 5.7 editor Python patterns for new or updated scripts.
- Do not assume the scripts are valid for PIE or runtime execution.

## Preferred Editor APIs

For new work, prefer subsystem access patterns such as:

- `unreal.get_editor_subsystem(unreal.EditorActorSubsystem)`
- `unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)`
- `unreal.EditorAssetLibrary.load_asset(...)`

For viewport camera access in UE 5.7, prefer:

- `unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_level_viewport_camera_info()`

The older `unreal.EditorLevelLibrary.get_level_viewport_camera_info()` path is deprecated in Epic's UE 5.7 Python docs. Keep legacy scripts runnable when practical, but prefer subsystem-based access when editing or creating scripts.

## Asset Safety

Engine-guaranteed fallback:

- `/Engine/BasicShapes/Cube.Cube`

Project-optional example from this repo:

- `/Game/S2/Core_Env/Prototype/S_Placeholder_Char.S_Placeholder_Char`

If a project-specific asset is missing, the script should still run with primitive geometry and no hard failure for the scale reference.

## Grouping Caveat

Actor grouping is best effort:

- group when `ActorGroupingUtils` is exposed and grouping is active
- otherwise select the generated actors and continue

Do not document grouping as guaranteed behavior.
