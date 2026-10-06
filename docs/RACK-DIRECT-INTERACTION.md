# Advanced rack direct-interaction adaptation

The owner requested ordinary-Cookery-style interaction without a rack UI on
2026-10-06 and approved local repair and a Git draft while retaining the BSM
upstream-status check as a prerequisite for merge, release and deployment.
This is a local G73 source repair. No archive, world or live server was changed.

## Controls

- Ordinary main-hand use targets the exact shelf cell: a held accepted stack
  inserts into that cell; an empty hand picks up its stored stack
- Sneak-use of an occupied cell retains advanced hotbar swap and remembered
  cross-rack return behavior. A held stack can also fill an empty cell
- Empty-hand sneak-use of an empty cell clears only that cell's retained filter
- `/kaleidoscope_grilling:rack` directly returns matching inventory stacks to
  the nearest rack within eight blocks. It no longer opens a form
- Wrong-category items, unavailable capacity and stale/repeated interaction
  events make no transfer. There is no alternate-slot fallback

Advanced stack capacity and the five seasoning plus four tool slots are retained.
The ordinary rack's one-tool placement quantity is not imposed on saved advanced
racks. No new gameplay text or actionbar polling is introduced. Successful
placement/pickup uses the item-frame sounds used by the Java and Cookery racks.

## Source distinction

Grilling Java NeoForge source at
`9a1acdab27698457bec16c9362678e574895a28c` opens a menu in
`rack/AdvancedRackBlock.java`. Its `rack/AdvancedRackRenderer.java` renders only
the first three occupied tool slots onto three hooks. Its count-based shelf state
has five stored seasoning slots and levels zero through four. These source
mechanics were inspected, not silently relabeled as menu-free behavior.

Ordinary Cookery `KitchenwareRacksBlock` and `KitchenwareRacksBlockEntity` provide
main-hand rotated-hit placement/pickup without a menu. The reviewed source pins
are Forge1.20.1/main `2f4e386ce23f49a385ddf003c67fc6415c55417a` and
NeoForge1.21.1 `4d39e36cfa749939ba5f9d6d3b715ef9a984cb9c`.
The reviewed Bedrock Cookery1.6.0 archive is file9054164,
SHA256 `da12fe6d39d7514aff1de3c963d69899324d771be5ca0fc3da1ccb759c7ad458`.
Its ordinary rack also has alternate-side fallback; advanced direct targeting
deliberately acts only on the clicked cell.

The menu-free controls, four fixed hooks and five fixed shelf cells are explicit
owner adaptations. They are not a claim of unchanged advanced-Java interaction
or rendered-client parity.

## Layout and saved contents

`advanced_rack_layout.js` defines both rows across the existing14/16 rack width.
Slots0–4 are fixed seasoning cells; slots5–8 are fixed tool cells. Forward visual
and inverse-hit cardinal transforms share this layout. East/west hit selection
now agrees with the equipment renderer. Removing neighbors never compacts a tool
into another slot, and the fourth tool is always represented.

`build_direct_rack_geometry.py` reflows the existing source-textured rack parts;
it does not change textures. All five established geometry identifiers are kept.
Four hooks and five jars use the shared cell centers. Shelf bone visibility uses
the derived32-value `seasoning_occupancy` state, so sparse occupancy identifies
the correct shelf cells instead of only a count. Existing spice-level values are
kept for saved permutations. Visual discovery rebuilds occupancy from existing
native contents without creating an inventory helper for inspection.

There is no item-slot, filter, binding, ownership-key, payload or UUID migration.
Native ItemStack transfers retain the existing transaction plans and rollback/
quarantine behavior. Deferred events verify hand metadata/restrictions, selected
slot, dimension/range, facing and sneak intent, then re-read live rack contents.
Rollback remains synchronous best effort, not process-crash atomicity.

## Evidence and remaining acceptance

Focused production-body/adapter-double and resource checks cover exact normal
placement/pickup in all nine cells and four facings, sneak controls, filter/write
rollback, full-inventory rejection, stale/repeated/offhand events, queued
two-player conservation, all tool masks, all32 shelf masks and preserved saved
nine-slot data. The geometry builder is idempotent. These checks do not simulate
a Minecraft client or certify multiplayer persistence.

Before merge/release/deploy: obtain and review the required current BSM status;
integrate the completed source repair, choose/freeze the final release identity,
and perform the canonical candidate checks. Native Blockbench/client validation
must confirm four hook poses, shelf visibility and exact clicked-cell behavior
for every facing, empty/full rack and repeated/sneak operations. Saved-world
rehearsal must verify all nine stacks and metadata after upgrade, break/place and
restart. Rollback needs the standard consistent stopped-world backup; engine
behavior when downgrading the added display state has not been accepted.
