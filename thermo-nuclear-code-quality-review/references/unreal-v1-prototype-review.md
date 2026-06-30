# Unreal V1 prototype thermo-nuclear review notes

Use when reviewing a narrow Unreal prototype that adds new gameplay/system code.

## High-value blockers to check

- Reflected `UPROPERTY` types have safe includes for UHT/generated code; forward declarations may not be enough for reflected object pointers.
- Names match semantics. If a container is `RequiredTags` but code uses `HasAny`, rename it to `AcceptedTags`/`IncludeTags` or change behavior.
- Query/pure classifier layers should not depend on authoring components. Component-to-candidate conversion belongs in the component or adapter layer.
- Designer-facing fields must be consumed and tested. Remove dead knobs from V1 rather than exposing future behavior.
- Avoid overlapping source-of-truth models: tags, enum responses, and booleans should not represent the same concept differently.
- Normalize numeric request fields in code; editor metadata such as `ClampMin` is not a C++ invariant.
- Result structs should usually be Blueprint read-only; mutable request/config fields can be Blueprint writable intentionally.
- If filters are implemented (altitude, distance-to-segment, etc.), add focused tests or remove the filters from V1.

## V1 boundary reminder

For a narrow prototype, prefer fewer explicit concepts that are tested end-to-end over broad generic systems with future-facing flags. Delete complexity rather than documenting that it is “for later.”