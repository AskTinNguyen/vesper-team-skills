# Unreal Adjudication Schema

The frozen manifest and final packet are the deterministic handoff between the caller, adjudicator, scanner, and packet validator. Runtime roots may be absolute; committed examples use symbolic roots.

## Frozen Surface Manifest

```json
{
  "schema_version": "unreal-review-surface/v2",
  "root": "<REVIEW_ROOT>",
  "review_mode": "named",
  "files": [
    {
      "path": "Source/Module/Private/Example.cpp",
      "attribution": "unknown",
      "scan": true
    },
    {
      "path": "Source/Module/Module.Build.cs",
      "attribution": "context",
      "scan": false
    }
  ],
  "exclusions": [
    {
      "path": "Source/Module/Private/Generated",
      "reason": "Generated output is reviewed through its source."
    }
  ],
  "engine_provenance": {}
}
```

Allowed attribution values: `introduced`, `modified`, `pre-existing`, `context`, `untracked`, `generated`, `unknown`.

The manifest fails closed on an empty file list, missing file, duplicate normalized path, path outside the root, invalid attribution, unsupported schema, empty exclusion reason, or a scanner-eligible file with an unsupported source type. Non-C++ Unreal files remain in the review surface with `scan: false` and must appear in the scanner receipt as intentionally unscanned.

The scanner never computes Git bases or changed files. Direct named-path invocation constructs this manifest explicitly.

## Final Packet

```json
{
  "schema_version": "unreal-adjudication/v2",
  "surface": {},
  "scanner": {
    "status": "OK",
    "scanned_files": [],
    "unscanned_files": [],
    "signals": [
      {
        "signal_id": "SIG-0001",
        "path": "Source/Module/Private/Example.cpp",
        "line": 10,
        "signal": "hard-cast-invariant",
        "attribution": "unknown",
        "review_item_id": "ITEM-0001"
      }
    ]
  },
  "applicability": [
    {
      "branch": "uobject",
      "status": "APPLICABLE",
      "reason": "The surface contains a lifecycle owner cast.",
      "ledger_ids": ["LED-0001"],
      "zero_owner_reason": null
    }
  ],
  "ledgers": [
    {
      "ledger_id": "LED-0001",
      "branch": "uobject",
      "owner": "UExampleComponent",
      "fields": {},
      "review_item_ids": ["ITEM-0001"]
    }
  ],
  "items": [
    {
      "item_id": "ITEM-0001",
      "origin": {"kind": "SIGNAL", "signal_ids": ["SIG-0001"]},
      "attribution": "unknown",
      "disposition": "FINDING",
      "invariant": "Lifecycle owner type must be validated or enforced.",
      "evidence": ["Source/Module/Private/Example.cpp:10"],
      "mechanism": "Authored attachment can supply a different owner type.",
      "consequence": "The lifecycle callback can assert or crash.",
      "owner": "UExampleComponent",
      "remedy": "Validate recoverably or enforce every creation path.",
      "item_gap": null,
      "proof": {
        "surface": "PROVED",
        "source-static": "PROVED",
        "pie-runtime": "GAP"
      }
    }
  ],
  "residual_gaps": [
    {
      "scope": "PROOF",
      "item_id": "ITEM-0001",
      "boundary": "pie-runtime",
      "missing_artifact": "PIE reproduction with a nonconforming owner.",
      "closest_evidence": "Blueprint-spawnable source path and lifecycle call graph."
    }
  ],
  "process_status": "ADJUDICATION COMPLETE",
  "outcome": "FINDINGS PRESENT"
}
```

## Item Semantics

- `FINDING`: source evidence establishes the violated Unreal invariant, reachable mechanism, consequence, and owning remedy. Missing higher validation remains in `proof`.
- `GAP`: a required source/context edge is unavailable, so the invariant cannot be adjudicated. Set `item_gap` and add an `ITEM` residual gap.
- `DISMISSED`: counter-evidence establishes that the invariant is preserved or inapplicable.

Attribution never changes disposition. Pre-existing or contextual findings remain findings; the caller decides changed-hunk actionability.

## Completion And Outcome

`ADJUDICATION COMPLETE` requires:

- every manifest file accounted for by the scanner receipt;
- every scanner signal mapped to exactly one review item;
- all nine applicability branches present;
- every applicable branch linked to ledger rows or an explicit zero-owner reason;
- unique, resolving IDs;
- every item terminated;
- every item/proof gap represented in `residual_gaps`;
- the packet validator passes.

Outcome rules:

- any `FINDING` -> `FINDINGS PRESENT`;
- otherwise any item/proof gap -> `GAPS ONLY`;
- otherwise -> `NO FINDINGS OR GAPS`.

Validator success proves structural closure, not semantic discovery or finding correctness. The calling review skill owns approval, changed-hunk policy, and closeout.
