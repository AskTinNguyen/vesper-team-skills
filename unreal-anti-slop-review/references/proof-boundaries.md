# Unreal Proof Boundaries

Record each claimed boundary as `PROVED`, `NOT_APPLICABLE`, or `GAP`. An item-disposition `GAP` means the invariant cannot be adjudicated; a proof-boundary `GAP` means the item is adjudicated but a higher validation claim remains unproved.

| Boundary ID | `PROVED` requires | Common false substitute |
| --- | --- | --- |
| `surface` | Valid frozen manifest, exact files, attribution, exclusions, and supplied provenance | Empty scanner output or inferred Git scope |
| `source-static` | Canonical owner, callers, lifecycle, terminal cleanup, configuration, and platform guards traced | Regex match or style preference |
| `compile-uht` | Matching target/configuration build, UHT, and zero-new-warning log | Live Coding or stale generated files |
| `pure-automation` | Canonical production helper/executor, deterministic trigger, meaningful observable, cleanup | Copied algorithm or unconditional success |
| `engine-integration` | Real UObjects, delegates, timers, GC, ASC, world state, and teardown | Fixture validity or direct broadcast |
| `serialization-migration` | Current round trip plus old data/defaults/redirects/custom versions as applicable | Successful compile |
| `editor-authoring` | Real tool/Details/Blueprint action, transaction, notification, dirtying, Undo/Redo, and failure atomicity | Reflected property or `Modify()` alone |
| `evaluated-asset` | Compiled/evaluated Blueprint, material, Niagara, BT/StateTree, animation, or target state | Asset presence, thumbnail, or raw metadata |
| `pie-runtime` | Real map/world, readiness predicate, bounded timeout, observable, and terminal cleanup | Editor composition or `AutomationOpenMap` alone |
| `networking` | Authority/client roles, owner connection, prediction/replication, relevancy, expected results, teardown | `ClientContext` or single-player PIE |
| `cook-server-commandlet` | Relevant non-editor path actually executes | Editor target build |
| `platform` | Target-platform compile or run | Win64 Editor build |
| `engine-fork` | Git/upstream provenance, exact delta, extension decision, regression, and merge note | Packaged source snapshot |

For every proof `GAP`, record the missing artifact and closest evidence. Lower proof never upgrades a higher boundary. A source-proven finding remains a finding when runtime, networking, editor, cook, or platform reproduction is missing.
