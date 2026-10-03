# Java eating piece and native clock repair

This is an unfrozen source candidate for integration. BDS, compiled-pack and real-client acceptance remain separate. No live deployment, release or merge is part of this change.

The starting candidate is the verified source-only handoff `a9e6a4ae7262e18b7e8cc68d9cb9e2b926cd40b1`, reconstructed over public `.60` commit `4ee97f04e81dcdc2d00653e2bb907f6c1b1f0d6a` / tree `d3e963b588245d4556d3da273722a9cd7d529808`. Its gzip SHA256 is `46644b459bb9af7a5a3c250522364dd3d7bc1b67b46603ef381280ed1f124f90`, decompressed patch SHA256 `2a3b8d900da6f3271841515caf414dc6fcb7a334b2603f12ab83478b16003c4b`. All 266 manifest paths were verified before repair. Windows CRLF conversion was corrected only where the normalized bytes matched the required hash exactly.

## Resulting behavior

`THREE_RANDOM` previously chose a 90-tick THREE_ALT curve even after a native 100-tick item use had begun. Java selects the branch before querying use duration. This candidate selects THREE for a captured native 100-tick session, and THREE_ALT for a captured 90-tick session. It retains explicit profiles and the two-argument pure random selector. It does not write equipment, replace ItemStacks, or change metadata, recipes, plate contents or food-effect identities.

This is a deliberate fixed-duration compromise: current 100-tick items always use THREE. Java's per-use random 90/100-tick duration is not reproduced, and the THREE branch retains its existing presentation. The THREE_ALT first-person projection will not be selected for a 100-tick session. Implementing full randomness through item-type substitution is a different change with identity and metadata admission requirements.

The handed-off `.61` completion helper remains unchanged: duration 90 accepts start+89 only with terminal remaining=0; item/session identity and complete/stop dedup remain required. The first-person-only attachable changes, server-synced observer elapsed ticks, exact item/profile/hand gates and render-controller scope repair are retained.

## Source-backed ONE / THREE preparation

The missing resolver was recovered from [the pinned Forge source](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/forge-1.20.1/src/main/java/cn/breezeth/kaleidoscope_grilling/skewer/SkewerEatingPiece.java). Git blob: `447b3174972704be702233de60a41d38748515e1`; SHA256: `f89f3eb1dd742fa5ba79407ce11d5388c889599f4f211e0f0f9bec889b5676af`. The NeoForge resolver was also checked and uses the same mapping rules.

- Fixed models strip the first `raw_` / `grilled_` prefix, strip trailing `_skewer` from the folder, use `_raw` for raw food and piece group 1 for ONE / 3 otherwise.
- Secret, mysterious and dark food use an ingredient snapshot instead of a fixed model. ONE chooses the first ingredient; the other branch chooses the last; empty ingredients produce no piece. The ordinary `_piece_3` asset exists.
- All 47 piece assets are checked against the pinned source manifest; no food-model mapping is guessed.

`java_eating_piece_resolver.py` and `java_dual_eating_frames.py` provide the resolver, both authored arm matrices and active/detached child matrices for ONE and THREE. They retain source helper-arm Z handling, item rotation order, slim item offsets and ONE's step visibility. They factor the piece into a separate mesh under the active socket; no second ItemStack or offhand carrier is introduced.

These modules are authoring tools only. They are not imported into the gameplay runtime or activated in the resource pack. The matrix tests check algebraic factorization and decomposition, not an executing Java/Bedrock renderer. Native arm/skin/socket admission and detached-piece rendering still require implementation and real-client review. In particular, an arbitrary foreign ingredient requires a client model renderer or an explicitly supported resource catalog; a server API snapshot alone cannot reproduce Java's arbitrary `renderStatic(ItemStack)` call.

The stable [ItemStack API](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/itemstack?view=minecraft-bedrock-stable) exposes a read-only type ID and an exact clone of an existing type. It does not expose a setter for per-stack native food duration. Rebuilding a different type with a metadata serializer is not an exact clone of inaccessible native/foreign data. This is the reason for the conservative duration selection; it is not a claim that fixed owned helper meshes are impossible in Bedrock.

## Regression coverage and remaining acceptance

The original 14 completion tests remain, extended to 20 production-subscriber/API-double tests covering captured 90/100-tick random selection, cancellation, repeat start, changed item/slot/metadata, duplicate stop and metadata/opposite-equipment preservation for main/offhand release. Observer tests evaluate generated Molang and first-person/third-person gates statically. Dual/source tests cover 6,432 factorization conditions across two profiles, hands, slim/wide item transforms, two meshes, eye heights and 201 time samples.

`verify_a2861.py` includes the new dual/source tests and keeps the bottle worker's existing checks. The observer test sends its Node source through stdin to avoid Windows command-line length limits. Whole-suite Windows launches may additionally require `python3` to resolve to the active Python interpreter and long `node -e` input to use stdin; assertions and production logic must not be weakened.

No native/BDS acceptance is asserted by these tests. A real second observer, ONE/THREE main and detached food, both hands, skins and offhand equipment, per-use randomized duration, cancellation/item-swap persistence and compiled assets remain acceptance work. The integrating owner must assign a new release identity/freeze after combining repairs; this branch intentionally keeps the supplied unfrozen identity.

## PR124 overlap at the requested public head

[PR124](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/124) was reviewed at `6c71ac78fe6631033664b342e2e2c8860f174fdb`. Its label 2.8.52 does not imply it is included in .60/.61. Its branch advanced during review; these findings do not assert the state of a newer head.

It introduces 22 alternate 90-tick native items, 20 copied alternate attachables, canonical food-lookup aliases and a metadata-readback pre-use replacement. Its generator check passes. It does not contain the inclusive start+89 completion check or the .61 server-synced observer clock. Do not replace current handlers wholesale.

Read-only pure-module probes at that head reproduced four alias gaps:

1. Ordinary food used as a secret ingredient loses its `ordinary` flag when the ingredient is an alternate item. Direct standalone completion is a separate canonicalized path.
2. `secretVisualIndex` returns 141 for ordinary canonical food and 0 for its alternate, hiding that supported ingredient mesh.
3. Identical canonical/alternate food rows do not trigger `secretFood(...).duplicate`, while two canonical rows do.
4. A custom recipe-book literal canonical selector rejects alternate stock, although `makeBookRecord` canonicalizes its result ID.

Canonicalize logical comparisons while retaining actual snapshot `id` and `native.id` for exact restoration. Another pack's exact native recipe IDs also do not automatically recognize the alternate type. Both-hand preparation and inaccessible metadata require actual native admission before replacing the conservative duration solution.

At that head, five unchanged source test files produced 116 tests / 106 passes / 10 failures. All ten failures are plate VM fixture omissions of `canonicalFoodId`, not proof of runtime plate item loss. The failed [canonical CI run](https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/37139605901) stops at `verify_a286.py:76`: the assertion expects 107 attachables while the head contains 127 (20 new alternates). Dash compilation was skipped. No code from PR124 is merged into this repair.
