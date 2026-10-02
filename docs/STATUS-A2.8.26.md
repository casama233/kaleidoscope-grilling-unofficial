# A2.8.26 — ingredient fidelity and usable skewer recipes

Based on public A2.8.25, preserving UUIDs and unmodified public Cookery 1.0.8.

- Four paper in a 2×2 square now creates the existing empty Skewer Recipe Book. Recording preserves the source skewer; a single-book crafting recipe clears the record. This is a Bedrock bridge for Java's unavailable blank Cookery recipe page, not a second guidebook or identical crafting UI.
- Recorded books accept an empty Unfinished Skewer in the offhand; wall recipes also accept ordinary main-hand sticks. Full-inventory delivery and input/stick writes use rollback. Java's recorded-secret metadata copy semantics are retained.
- Deferred ingredient snapshots preserve stable-API raw translated lore, name, exposed primitive/vector properties, damage, enchantments, keep-on-death, lock mode and adventure lists. Readback must succeed before debit. Existing legacy rows remain readable; already lost fields cannot be recovered. This is not arbitrary NBT or cross-pack private-data serialization.
- Native vanilla foods now use 40 pinned Mojang definitions when ItemFoodComponent is unavailable (the API only exposes data-driven foods). Canonical IDs are resolved from the same Mojang metadata; explicit live components retain precedence. Old zero-nutrition vanilla snapshots are repaired during secret-food nutrition/effect evaluation, including container remainders. Existing packed plates may retain stale highest-nutrition selection caches; their eaten-food reward is recalculated, but cache migration remains open.
- Smoking accepts only valid edible outputs, preserves unmapped/invalid/nonfood inputs, and verifies cooked-row storage. Successful ID-only conversion uses fresh result metadata, as Java recipe assembly does; arbitrary recipe output components still require a richer contract.
- Plates calculate cooked secret nutrition from effective cooked ingredients. Nested secret ingredient nutrition uses its recorded food values. Unknown third-party finish-use side effects remain outside this change.
- Mixed legacy/new snapshots retain duplicate-food penalties. Secret skewers with malformed JSON, invalid item IDs/envelope identities, or incomplete ingredient counts cannot begin native eating.

## Still open

Beef Chunks and Chicken Skin need public Cookery cooperation: its built-in board recipes take precedence over extensions, and there is no authoritative multi-output completion hook. No guessing of nearby drops or private host state is introduced.

Secret/unfinished skewers still have static icons and no personalized attachables. Java samples ingredient textures and persists three shape variants; the earlier 107-attachable audit does not cover these items. Native client rendering/eating, automation host integration, saved-world migration and broader Java parity remain open.

Source/static and real native server evidence are separate; no simulated Minecraft players and no live deployment.

## Primary references

- Java 1.1.1: https://github.com/breezeth-CN/KaleidoscopeGrilling/tree/9a1acdab27698457bec16c9362678e574895a28c
- Blank-page paper cost: https://github.com/KaleidoscopeMods/KaleidoscopeCookery/blob/4d39e36cfa749939ba5f9d6d3b715ef9a984cb9c/src/generated/resources/data/kaleidoscope_cookery/recipe/recipe_item.json
- Stable ItemStack projection: https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/itemstack?view=minecraft-bedrock-stable

Native fallback provenance: Mojang/bedrock-samples 46ba6ea985fb5a92d79a9419198f10dda14c199d (sample 1.26.50.4), verified against isolated BDS 1.26.52.3 separately. Legacy sample item names are not valid current ItemStack identifiers; canonical aliases come from Mojang mojang-items.json.

## Verification

126 focused function/data/storage-double regressions and the complete canonical source gate passed. Native BDS 1.26.52.3 verified all 40 canonical vanilla foods, all 11 smoking mappings, nonfood rejection, metadata/book preservation and the prior full skewer-state restart probe. Exact 16-pack family loading/restart also passed. See [BDS-PARITY-20261002.json](BDS-PARITY-20261002.json); no native player UI or saved-world migration acceptance is implied.
