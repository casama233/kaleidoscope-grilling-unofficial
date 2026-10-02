# A2.8.35: original Java sprites and native sapling item

The two chili-oil brush icons now use their exact released Java 1.1.1 PNGs,
rather than copies of the canola brush. The legacy generator reads each pinned
variant separately and fails if its source is missing. Item identifiers, stack
limits, oil-tool semantics and hidden creative categories are unchanged.

Pepper sapling now has an explicit same-ID generated sprite item, replacing the
implicit crossed-block inventory item. Its native block placer remains enabled;
the block, dirt placement validation, stage reset and growth script are unchanged.
The existing world texture is pixel-identical to Java and is not rewritten.

All four original item JSONs and PNGs are pinned in
`development/gameplay_core/fixtures/java-item-icons-1.1.1/source.json`, including
source commit and release JAR SHA256. Six focused regression tests protect these
routes, distinct variants, source bytes and preserved placement/growth resources.
Previous rack, skewer, storage, recipe, guide and Board API regressions remain on.
The guide payload has its own content version 0.3.9 from the concurrent A2.8.34.

## Remaining oil-brushing view gap

Java's oil pot overrides its model with the selected generated brush during use
(first and third person); its first-person renderer applies a temporary brush
stack and brush-specific poses. This port still animates the equipped oil pot.
Hidden brush items are not temporarily equipped, so changing their hand_equipped
flag alone cannot repair the active-use model. This patch fixes source sprites,
not that separate animation gap. No native-client visual acceptance is claimed.

No live deployment or complete Java parity is claimed.

## Editor reference check

Blockbench 5.2.1 opened the unmodified released premium brush item JSON from its
normal assets hierarchy and resolved the 16x16 original texture. Its Generated
Item Model notice, thin generated silhouette and GUI sprite were observed.
Display mode was inspected as an editor reference only; Blockbench's parent
preview/default lighting does not certify Minecraft inherited transforms or the
port's active oil-pot renderer. Canonical assets were not re-exported from the
editor, preserving exact upstream PNG bytes.

## Concurrent source integration

Preserves all 28 changed files from public main 1c9e0deaa2434466afec265b4ea8b931c9473e49
(PR105, A2.8.34): transactional plate transfers, strict saved-data checks,
Java placement direction, captured hand reads, native probe and guide corrections.
Their full verifier runs before the new icon checks. A2.8.33 was an unpublished
local candidate; its BDS report does not validate this combined runtime.

## Active brush implementation boundary

A resource-only attachable could target the two existing Cookery pot IDs without
rewriting their items. It would need a reliable client-visible active hand and oil
variant. The current oil_type/kc_oil_count values are ItemStack dynamic properties,
not synced entity properties, and stable playAnimation has no variable map.
Molang cross-entity variable reads require the owning entity's public declaration;
adding that for players would require a player resource override. No such override
or use of unrelated vanilla animation variables is introduced here.

The last successful use legitimately converts a filled pot into its empty ID;
any future presentation must retain the pre-consumption oil type and cover both
IDs. An isolated native-client proof is required before implementing this signal
bridge, followed by both hands, observer clients, depletion, repeated use and slot
switching tests. BDS loading alone cannot certify it.

References:
- https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/playanimationoptions?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/documents/molang/syntax-guide?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/documents/attachables?view=minecraft-bedrock-stable

## Combined runtime validation

The full registered 2.8.35 gate passed, including public 2.8.34 plate transaction
and orientation tests plus six hardened source-icon tests. All 330 relative script
imports resolve. Exact source packaging and frozen baseline checks pass.

The combined 16-pack family passed two isolated BDS 1.26.52.3 load/restart cycles,
with no content/script errors and the persistence marker restored. Existing pack
override and empty-allowlist warnings are recorded; no native guide overlay,
player simulation, client rendering acceptance or live deployment was performed.
See BDS-ITEM-ICONS-2.8.35.json for the exact archive hash and evidence.
