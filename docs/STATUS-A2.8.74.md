# 2.8.74 — portable Java bottle and heat repairs

The owner accepted explicitly listed platform differences and assigned client acceptance to dot. This release continues the practical Java migration; it is not a claim of complete visual parity or absence of unknown defects. `client=false`, `production_ready=false`, `pending_client_acceptance`.

## Resulting behavior

- Finished bottles select the original Java remaining/variant sprites for all 64 states. Empty and pending bottles have eight fill proxies each; placement, retrieval, rack storage and clear recipes recognize their canonical mechanic kind. Ordered ingredient layers use the Java-to-Bedrock X reflection, preserving ingredient order and geometry. Arbitrary inventory ingredient colors remain a documented platform adaptation; held/placed layers retain the actual ordered colors.
- Newly heated food and weighted heat merges round the **absolute deadline down to 100 ticks**, as the current author's `FoodState.setHot` does. This includes ordinary Grilling food, the public producer SDK and the author-owned Cookery output extension 0.2.6. Saved precise deadlines and foreign raw v1 food data are retained on reads; only a normal new heating/merge writes a bucketed deadline.
- Cosmetic heat lore reserves room for the real stackable metadata carrier. Nineteen user lines retain their content and heat while omitting the badge; twenty-line stackable items without a carrier remain unchanged instead of displaying false heat. Native property write failures restore the prior raw lore and heat. Host outputs omit the optional badge when the public metadata fills the native twenty-line limit.
- Guide 0.3.32 describes the bottle inventory adaptation and heat timing in the existing single Cookery entry. Cookery 1.6.0 UUID/API/dependencies, G73 Heavy Metal/native health/original audio/particles, and earlier survival/transaction repairs are retained.

## Source reconciliation

The selected functional bottle changes come from [PR135](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/135), head `0c33806e570219a60c5d063a7d4fef536f49c5fc`, against public G69 `8ac0dd7625ff304b79c33fa42f41e785f39ae4d2`. Its later branch called a different bottle pickup refresh G72; canonical G72 is already Cookery 1.6.0. That identity collision is preserved as provenance, not adopted. No source branch manifests, baseline, release history or dependency identity are imported. Reviewed functional source is integrated into the new G74 identity on canonical G73. Existing PR135 and its historical bounded native reports remain intact.

The immutable G69 public source witness remains unchanged; a new exact reviewed main delta records the combined G73 damage/feedback and PR135 bottle edits. Code outside that registered delta remains subject to the existing conservation checks.

## Evidence and limits

The new heat fixture executes the unchanged extracted Java bucket method from author commit `9a1acdab27698457bec16c9362678e574895a28c`, producing 24 boundary/oil vectors. Actual production metadata modules are checked with storage-operation adapters for legacy expiry, lore capacity, public data, and post-write rollback. Bottle assets are checked against pinned Java geometry/palette and source-backed generator output. These are functional checks, not rendered client acceptance.

[Current isolated native evidence](evidence/portable-fidelity-2.8.74-native.json) confirms 25 real ItemStack/container cases and all 25 records/counts after normal restart, with zero native errors. All final owned runtime bytes match apart from the precisely recorded probe module/import, and all eight copied host API modules match; historical G71/G72 bottle reports and G73 mob damage results keep their original scope. Full-family static/BDS/fresh stopped-world migration and exact live installation remain separate canonical workflow gates.

[The fidelity scope](JAVA-FIDELITY-GOAL-20261007.md) lists inaccessible remaining absorption, CapsLock/numb crosshair, new-fortress generation hooks, dynamic inventory rendering, native fluid/Java-only callbacks, and engine sound/particle differences. Existing source survival/recipes, quantities, cooking phases, effect/settings and rollback checks run once through the canonical CI chain for this candidate. Real input/observer/FOV/skin, listening and multiplayer performance acceptance belong to dot; they are not inferred from hashes or zero-player BDS.
