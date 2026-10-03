# A2.8.56 — Secret ingredient snapshot at the fourth flip (draft)

Preserves 2.8.55 rack selection and the full earlier repair chain. Java Grilling 1.1.1 reference commit: `9a1acdab27698457bec16c9362678e574895a28c`.

## Repairs

- The successful transition from phase1/flips3 to phase2/flips4 now stores cooked ingredient snapshots on cloned secret skewers in all occupied grill slots. It does not set Cooked, heat or seasoning early.
- Snapshot preparation completes before any inventory/state mutation. Slot writes and the final phase write use the existing synchronous rollback/quarantine mechanism. Success sound, feedback and animation follow a successful commit only.
- Existing valid three-ingredient caches remain immutable. Malformed or partial caches fail closed rather than silently changing a previously stored result.
- Renderer selection uses stored cooked rows at visual stage4 and later, falling back to raw rows if no cache exists. It no longer reruns the smoking registry while rendering.
- This removes the prior premature cooked appearance at the third flip: the Java visual stage already becomes4 there, but a normal item has no cooked cache until the fourth flip.
- Plate and held-item readers keep their default Cooked-flag behavior. Grill display can explicitly request raw/cached context without changing item metadata.
- Extraction retains the legacy fallback for phase2 saves that do not yet contain a cache, and still owns Cooked, heat and seasoning application.

## Pinned source

- [GrillBlockEntity fourth-flip snapshot](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/grill/GrillBlockEntity.java#L128-L133)
- [SkeweringHandler snapshot/display rules](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/skewer/SkeweringHandler.java#L138-L176)
- [Extraction finalization](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/grill/GrillBlockEntity.java#L210-L217)

## Regression scope

Twenty-three deterministic tests execute production flip, snapshot, extraction and composition functions with storage/event doubles. They cover early flips, unlit fourth flip, mixed slot types, raw/cached display contexts, registry changes after cooking, existing caches, tag/item priority, unavailable/non-food outputs, metadata preservation, each slot failure, state failure, preparation failure, rollback quarantine, legacy extraction and JSON restoration. The initial seventeen-test set reproduced fourteen failures against the preceding implementation. Six additional corruption/identity cases were added during review; all twenty-three pass after repair.

These are not simulated players, native chunk persistence or actual animation acceptance. Synchronous rollback is not crash atomicity. Immutable content-addressed metadata produced during preparation is retained on rollback because deleting shared records could harm other items. Native save/restart between the fourth flip and extraction, populated rendering and remaining Java display-context differences need separate evidence.

## Isolated native persistence result

The real Bedrock Dedicated Server 1.26.52.3 loaded a disposable world with all family dependencies and the current canonical .56 source, plus an explicitly declared test-only script overlay. No simulated players or production database were used.

- All three native grill slots received the fourth-flip cooked snapshot while remaining uncooked stored items
- Normal server stop and restart preserved the exact raw and cooked snapshot strings and the phase/flips state
- Replacing the smoking registration after restart did not alter cached display selection or native output preparation
- Outer item metadata remained intact

See [machine-readable result](NATIVE-FOURTH-FLIP-2.8.56.json). Every copied BP/RP file matched the canonical source except the declared probe import and probe script. This is native storage/restart and output-preparation evidence, not actual player extraction, rendered appearance or production-world migration.

Reproduction helper: development/gameplay_core/native_fourth_flip_check.py requires explicit --bds-root, --family-candidate, --level-metadata and a new --output directory. It replaces only Grilling in a disposable copied family, runs the source probe, normally stops the server, restarts that same test world and verifies persisted data. The resulting directory contains a test-only overlay and must never be deployed. Requires the existing nbtlib 2.0.4 test dependency.
