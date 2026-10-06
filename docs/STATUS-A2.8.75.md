# 2.8.75 — ordered seasoning and output ownership repairs

Current Java `FoodState.sameForManualMerge` removes only heat/model/creator fields before comparing components. `SeasoningData` stores the ordered `SeasoningIngredients` list, so kind, repeats and order must survive every transfer.

The prior Bedrock merge comparator passed the JSON string written by `setFoodSeasonings` directly to an array normalizer. It became `[]`, making different legacy seasoning lists indistinguishable. A reproduced hot-beef speed/strength pair incorrectly became one stack and lost the source seasoning. The same comparison feeds manual hot-food merging, skewer sorting and inventory output delivery.

This release decodes the actual legacy JSON representation and preserves the full ordered string list. Unparseable/foreign data remains opaque in the comparison rather than becoming plain food. Equal lists still merge using the original quantity-weighted 100-tick heat bucket; public/legacy storage shares the same ordered-list boundary. Stored data is not rewritten by comparison.

Inventory delivery also restores the complete pre-operation inventory when a slot write or native `addItem` fails after crediting output. Returning only the uncredited fragment after a post-credit exception could authorize duplicate drops. A restored operation returns the original full output; strict callers receive the error after restoration so their outer transaction can roll back all outputs. Unresolved rollback throws and does not authorize an ambiguous remainder.

## Evidence

Source regressions exercise actual production modules with storage-operation adapters, not actors: kind/strength/order/plain boundaries, equal-list bucketed merge, legacy/public compatibility, malformed payload retention, sorting/output, late slot faults, post-credit addItem faults, strict restoration and unresolved rollback. The same tests reproduce failures on unchanged G74 and pass after this repair. This is behavior evidence, not a client-rendering or unlimited fault-tolerance claim.

G74 bottle/icon/heat/lore fixes, G73 damage/original feedback, Cookery 1.6.0 and existing family functionality remain. Guide 0.3.32 and host extension 0.2.6 are unchanged because their exported content is unchanged. BP/RP/modules/dependencies advance together under the new release identity; historical claims are preserved.

[Bounded native evidence](evidence/legacy-seasoning-2.8.75-native.json) passes ten cases with real ItemStacks/chests and all twenty resulting records/counts after normal restart. Both phases have zero errors; all final owned runtime bytes match after removing only the explicit probe overlay. The initial invalid test item ID is preserved as a failed setup, not treated as a gameplay failure. Source CI, full-family load/restart, fresh stopped-world rehearsal and live readback are separate evidence. Client acceptance remains assigned to dot and unverified: `client=false`, `production_ready=false`, `pending_client_acceptance`. Accepted platform limitations remain listed in the current fidelity document; successful tests are not a claim of no unknown bugs or complete Java presentation.
