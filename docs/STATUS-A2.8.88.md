# G88 hardened plate interaction and count-transition candidate

The exact G88 runtime now has a [bounded native result](NATIVE-PLATE-G88-BOUNDED-20261007.md): short/long upright insertion retained the remainder in delayed server queries, subsequent air eating worked, and the tested count transitions plus same-camera save/reload retained the intended pose. Canonical source/Dash/export CI also passed for that runtime. The report documents the precise inputs and remaining global gates; it is not full Java/client acceptance.

G88 preserves frozen G87 commit `81d08da044c52ba5e06bb2de1bd803ea6977b041` and all fixes from frozen G86 `6e714853d029f93f0186efa2e96e192e87735a74`. G87 was frozen before independent review found the removal-fault case below; its identity and exact source remain in Git history, without an installed-package or native-pass claim. A fresh 2.8.88 identity is used for the hardened candidate. It retains the independently merged G82 Cookery palettes, all G83–G85 plate visibility/nutrition repairs, and the paired host 1.6.0 dependencies. G86's complete canonical source and Windows Dash/export CI passed in [run 37574094943](https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/37574094943); this does not accept the two later native issues described below.

## Independently observed G86 results

Actual Bedrock 1.26.52.3 used exact G86 archive SHA256 `17ee94b1d79cea64000c4cb5313697ef716f8714727585bcb31f2c1718bad4ec`. These observations were made on G86, rather than inherited from G85:

- The preserved custom occupied plate that previously rolled back completed an ordinary 1800 ms main-hand use. The selected slot became a bowl, hunger increased from 10 to 13, regeneration/absorption icons and two golden hearts were visible. No diagnostic tag was enabled
- A fresh ordinary beef-skewer plate was straight immediately in the bounded west-facing case
- Sneaking fresh placement from a canonical stack of two left one held item, confirmed by a server query. Sneaking insertion retained the remainder for at least 28 seconds
- Ordinary beef counts 1 through 5 displayed food and shafts. All five persisted through save/reload

The count-4 image shows three lower parallel skewers plus one raised crossing; count 5 shows three lower skewers plus two raised diagonals. This qualitatively corresponds to the retained [original Java layouts](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/skewer/SkewerPlateRenderer.java). Matched Java in-game images were not available. Visibility is not exact rendered parity, and the pose-stability issue below remains distinct.

## Native issues and narrow source changes

### Upright insertion also starts later food consumption

A 100 ms upright use on an occupied plate correctly inserted one skewer and immediately retained the other. About 12 seconds later the held remainder was absent and hunger had increased from 13 to 18. Sneaking controls retained the remainder. There was no initial transaction loss; no native event-order trace was captured.

Source inspection found that cancellation of the plate-block interaction did not cancel the separate native item-use callback for skewers. G87 adds a seven-line, target-specific guard in `a25_plate_recipe_runtime.js`: a recognized skewer whose first nearby view-ray block is a plate cancels item use as well. The ray is bounded to six blocks. Air, other targets, non-skewers and ordinary air eating retain their existing paths. No timer, inventory substitution, storage write or unsupported stop-use API is added. Production callback tests cover both event orders, aliases, repeated/full plates, bounded targets and immediate subsequent air use. G88 subsequently passed the bounded short/long upright delayed-remainder controls documented in the native report. Broader inputs remain unverified.

### Reused plate helpers keep a different rendered yaw from fresh helpers

At the same explicit camera, the count-5 lower-right shaft slanted before save and was straight after reload; raised overlaps changed too. Food and storage remained present. The source exposes two yaw-changing reuse cases: slot 2 changes from the raised −22.5° count-3 pose to a straight lower count-4/5 pose, and slot 3 changes from −45° at count 4 to −22.5° at count 5. Reverse transitions change the same slots. Existing helpers were teleported, while `initialRotation` was applied only at creation.

G87 records each plate helper's effective authored spawn yaw, including facing. Only a yaw change replaces that transient helper using the existing discard/spawn path. Unchanged-yaw position/metadata updates retain reuse. This removes the reuse-versus-fresh-spawn difference by construction, without changing the original layouts, food state, ownership, helper budget, observer queue or other stations. All four facings and forward/reverse 1–5 transitions are covered in source tests. Which internal native head/body value was stale is not established by screenshots; G88 subsequently passed the bounded forward/reverse count transitions and same-camera reload check documented in the native report. All-facing and exact Java image comparison remain open.

### Fail closed when native helper removal is rejected

Independent review reproduced a failure using the actual production `discard` and `renderPlate` functions: if `remove()` threw during a yaw change, the old live helper and counter were retained, but a new helper could overwrite the map entry. Two actors then existed with only one tracked. G88 adds one plate-only check: if the old map entry remains after discard, return without spawning. The existing helper remains tracked until a later successful retry. The regression uses production discard with a throwing native remover, spare capacity, and recovery; unchanged-yaw reuse and the original authored transitions remain covered. Storage and other stations are untouched.

## Source conservation and gates

Only the two named BP scripts change, apart from the fresh paired 2.8.88 manifests. All other BP/RP bytes, including `main.js`, source layouts, animations, seven corrected Cookery atlases and all ingredient metadata, remain identical to G86. Exact reviewed preimage/postimage deltas admit only those two scripts: the two G87 deltas plus the single-line G88 cleanup hardening on its frozen renderer. Historical G86 union assertions remain intact, G86 and G87 release histories are pinned, and current runtime bytes are compared against the immutable source plus complete reviewed deltas. Delta release/base metadata is also verified.

Local focused checks do not certify native event delivery or rendering. G88 now has verified exact public Git/package identity, complete canonical/compiled CI and the linked bounded native tests. Their scope does not close the broader gates. Keep `client=false`, `production_ready=false`, `pending_client_acceptance`. No merge, release or live deployment is authorized in this task. BSM freshness, full-family/saved-world admission and broader Java/client acceptance remain open.

## Evidence integrity

Private screenshots, worlds, player records, native logs and machine paths are not published. Relevant screenshot SHA256 values:

- G86 custom consumption: `dfc6f5d99062cfdbea6d073bb8e73f6dc594fa55e4647f097de05003e975e4c3`
- G86 upright insertion: `dfca5a86cc991d9f76d4bd6fea233c41765206b2116abf8dba7355502b21e395`
- G86 delayed consumption: `d3fd036724c6824c55a0e9f3b14429228ff207bc82098c9916defde5a339e0f5`
- G86 count 4: `222980faa024d42fbfc237b1999e951b47e5c5686649f3a004302c61bafa2956`
- G86 count 5: `97168685be695b4242ba041cdb9e77de072dc82379675cb5215fb0eb8fec85ac`
- G86 count 5 after reload: `45d1682453385a71a3ffbc45ffe96aac5b05d2c57b50ddfe2b68fe07c7069138`
