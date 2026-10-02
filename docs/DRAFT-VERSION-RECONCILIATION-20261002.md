# Draft version reconciliation — 2026-10-02

This repair was first proposed as 2.8.46 in unpublished draft commit `c6f10476103dccc8899194a382af1ceb131b3482`. While it was being checked, an independent repair using the same version was merged into main. No release or deployment of our colliding draft was performed.

The final repair is 2.8.47, based on canonical main `49159e9d4dc9a88ad59dfda618146c0d7a3b9fc0`. Its release-history file preserves every entry from that main commit exactly, including the independently merged 2.8.46. The old draft's conflicting, unpublished 2.8.46 entry is superseded rather than misrepresented as the official release.

The reconciliation push's append-only comparison against the previous draft branch correctly flagged the replacement of that draft entry. The pull-request comparison against canonical main passed. Neither guard was disabled or relaxed. Subsequent checks must use the reconciled source and the current canonical base; the earlier failed run remains part of the audit trail.

Final locally built canonical MCAddon SHA256: `672bc5674b0a0166ba99e483cb7e206fab4edf37b3a33cb09021852d750e4c9f`. This records package identity only. Blockbench/editor, static tests, native server loading and human client acceptance are separate; the latter two were not performed for this repair.

## Subsequent main reconciliation, 18:29 UTC

The draft now incorporates canonical main `22e75cc74bd27242858654adfb799f311546a622`, preserving its published identities and incoming repairs. Current candidate: 2.8.49. Fresh remote-tracking branch histories were fetched before the latest immutable local claim gate. The gate and full current verifier passed. Local claims do not coordinate separate clones or computers; publication still requires serialized maintainer coordination. Earlier candidate-tree CI is not reused as proof for this new tree. No full-family admission, release or deployment is performed by this draft update.
