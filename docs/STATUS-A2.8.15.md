# A2.8.15 — Java 1.1.1 survival-chain restoration

Reference: the released NeoForge 1.21.1 **1.1.1** JAR, not only the upstream main branch or the CurseForge description. Exact JSON recipe/tag fixtures and the archive identity are in `development/gameplay_core/fixtures/java-1.1.1-recipes/`.

## Implemented

- Restore the missing Grill crafting recipe: five iron ingots, two bricks, coal/charcoal in the Java pattern.
- Restore initial Empty Seasoning Bottle crafting: six glass and one wooden button. Eleven Java 1.21.1 wood variants have explicit Bedrock recipes because the Java wooden-buttons tag is not a documented Bedrock recipe tag.
- Register Green Chili Powder, Houttuynia Powder and Totem Powder through the public Cookery millstone API. All seven released millstone recipes now have an actual registration path.
- Restore Premium Chili Oil crafting with the correct four ingredients, including Houttuynia Powder.
- Implement Dragon Egg Powder acquisition from a kitchen knife used on a dragon egg: Looting controls the 1..1+level count, durability/Unbreaking/creative mode are handled, the egg is not consumed, and vanilla egg interaction is not cancelled. Hand and output writes are a rollback-capable transaction.
- Fixed skewers accept their Java ingredient tags, including tagged ingredients from other addons; previously only exact hardcoded IDs could produce a fixed recipe. Literal-ID callers remain compatible.
- Burnout resets the cooking batch without extinguishing the grill. Java `GrillBlockEntity.resetProcess` does not change the block's lit state.
- Update the existing three-language guide to 0.3.3 with real acquisition paths and disclose remaining public-host gaps. No extra guidebook or second publisher.
- Correct release notes that still advertised obsolete Cookery 1.0.6. Canonical dependency remains public Cookery 1.0.8.

## Tests and limits

`test_java_survival_parity.mjs` checks 69 released recipe/effect rows, fixed ingredient alternatives, tag matching, a complete grill cycle and retained fire. `test_dragon_powder_transaction.mjs` fault-injects seven cases into the actual transaction function. The aggregate source gate remains required.

Native BDS probes and exact candidate receipts are recorded separately. Static checks do not certify actual crafting UI, player input or rendering. This is a test release, not a claim of complete Java parity or safe live-world migration.

## Still open

- Beef Chunks and Chicken Skin: public Cookery prioritizes built-in beef output and has no authoritative chicken-chopping completion receipt. Do not revive cross-pack private-state guesses to fake compatibility.
- Initial Skewer Recipe Book: the public host does not expose the old blank `recipe_item`. Existing recording/auto-threading code therefore does not establish a working survival acquisition path.
- Dynamic secret-skewer icons/held models, exact bespoke Java eating animations and rendering still need implementation/visual acceptance beyond the 2.8.14 anchor fixes.
- General Cookery automatic output heat/seasoning needs a cooperating host receipt; supplying a receiver contract alone is insufficient.
- Exact custom-health effects, Java optional integrations, arbitrary third-party food consumption and fluid simulation remain platform/implementation gaps.
- Private-to-public UUID and occupied-world inventory migration is a separate prerequisite before live deployment.
