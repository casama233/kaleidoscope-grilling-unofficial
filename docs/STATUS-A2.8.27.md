# A2.8.27 — correct legacy packed-plate food ranking

Follow-up to [A2.8.26](STATUS-A2.8.26.md), retaining its native vanilla-food fallback, safe recipe-book acquisition/crafting, ingredient metadata and smoker fixes.

Existing plates could cache nutrition=1 for a secret skewer made before native vanilla-food recognition was repaired. Eating it already awarded corrected nutrition, but highest-nutrition selection could still choose a worse fixed skewer first.

Plate row normalization now re-evaluates secret food from its stored raw/cooked ingredients and updates only the derived nutrition/saturation fields. Both legacy props and new native-envelope props are supported. No ItemStack reconstruction or restricted native APIs run in beforeEvents. Original ingredient/creator/effect/foreign metadata is retained. Invalid ingredient JSON is not replaced with invented data.

The fifteen new regressions cover legacy/native ranking, raw versus cooked food, preserved arbitrary metadata, unchanged fixed-skewer values and malformed-data preservation. This addresses the specific cached-ranking limitation recorded for A2.8.26, not all old-world migrations.

Still open: personalized secret/unfinished models, exact public Cookery beef/chicken-skin acquisition, real-client input/rendering, arbitrary third-party food callbacks, general automation and full saved-world migration. No live deployment.

## Verification

141 focused regressions and full canonical source checks passed. Final frozen-source four-pack native BDS tests preserve recipe/ingredient metadata, verify 40 foods and 11 smoker mappings, and recalculate a saved legacy plate after a real server restart. Exact 16-pack family load/restart also passed. See [BDS-PLATE-CACHE-20261002.json](BDS-PLATE-CACHE-20261002.json). Client visual/input and general live-world migration remain unverified.
