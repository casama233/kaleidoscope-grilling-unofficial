# Private A2.8.33 candidate (never published): original Java sprites and native sapling item

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
The guide payload has its own unchanged content version 0.3.8.

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

## Validation

The registered aggregate gameplay gate passes, including the six new icon tests
and existing Board API, skewer, transaction and storage tests. All 328 relative
script imports resolve. The deterministic archive matches the frozen canonical
runtime; local Dash compilation was not performed.

The exact 16-pack family (Tavern 0.6.84, Liquor 0.1.48, Grilling 2.8.33 plus
pinned upstream packs and the declared Cookery host extension) passed two isolated
BDS 1.26.52.3 load/restart cycles, with the persistence marker restored and no
content/script errors. Expected existing higher-pack overrides and empty allowlist
warnings remain recorded. No player or interaction was simulated. The native guide
probe was not enabled in this load-only run. See BDS-ITEM-ICONS-2.8.33.json.

Superseded by A2.8.35 after preserving the concurrent public A2.8.34 plate fixes.
