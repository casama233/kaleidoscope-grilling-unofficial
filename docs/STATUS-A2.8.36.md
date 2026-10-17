# A2.8.36: original Java sprites and native sapling item

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
The guide payload has its own content version 0.3.10 from the concurrent plate-drop fixes.

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


## Additional concurrent plate-drop integration

Also preserves PR106 packed plate drops/explosion settlement and guide 0.3.10.
The final verifier executes its plate regressions before the new icon tests.
The earlier icon-only 2.8.35 candidate was not merged or published. Its archived
BDS-ITEM-ICONS-2.8.35.json does not describe public plate-drop version 2.8.35.
Final combined 2.8.36 validation is recorded below.

## Explosion cancellation guard

Review found PR106 queued plate destruction even after another addon cancelled
the explosion. This version checks cancellation at entry and again before queued
settlement; unreadable or unknown final status leaves the plate and data intact.
Queued-callback regressions cover cancellation before/after our listener, normal
settlement and unavailable event state. Packed-row tests now use five distinct
metadata snapshots, and quarantine is checked in a newly created module instance.
Native final-event lifetime remains subject to the separate BDS probe.

## Final combined-runtime validation

The full registered 2.8.36 gate passed: 36 plate transaction/cancellation tests,
six hardened source-icon tests, prior skewer/storage/recipe/Board API regressions,
and all 330 relative script imports. Frozen baseline and exact packaging pass.

The unchanged 16-pack family passed two isolated BDS 1.26.52.3 load/restart cycles.
A separate test-only append/export overlay also passed native packed plate drops,
five distinct ordered metadata rows, cancelled-explosion preservation, accepted
real explosion settlement, repeat protection and item-metadata restart persistence.
Both runs have zero content/script errors. Existing pack override/empty-allowlist
warnings are retained. Overlay before/after hashes are recorded in
BDS-ITEM-ICONS-2.8.36.json, separate from the unchanged production source receipt.

The cancelling listener was registered after the production listener; invocation
order was not independently traced in BDS. Both cancellation orders are explicitly
covered by queued production-function tests. These tests use zero real players
and no simulated players, and do not certify client visuals or saved-world migration.
