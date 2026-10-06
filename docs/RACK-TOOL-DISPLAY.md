# Rack tool projection candidate

This rack-only correction replaces the unknown native held-item basis for the
six canonical rack tools with deterministic, one-pixel-thick generated sprites.
It does not change the player's held items, their definitions, plate/composed
rendering, grill rendering, rack inventory, storage helpers, occupancy or four
fixed X/Z slot anchors. Known sprites are centered in the clicked lower row as
described below. Generic tagged extensions keep the existing native equipment
fallback and have not acquired an invented transform.

## Source and coordinate contract

- Grilling NeoForge1.21.1 source
  `9a1acdab27698457bec16c9362678e574895a28c`,
  `rack/AdvancedRackRenderer.java`: scale `.75`, negative-axis rotations X180,
  Y−25, Z45, then `ItemDisplayContext.FIXED`
- Cookery NeoForge1.21.1 source
  `4d39e36cfa749939ba5f9d6d3b715ef9a984cb9c`: the four kitchen-knife generated
  item models inherit `minecraft:item/handheld`. Both shovel override children
  (`kitchen_shovel_no_oil` and `kitchen_shovel_has_oil`) also inherit handheld,
  without a FIXED override. The Bedrock no-oil shovel is a distinct ID; only that
  canonical accepted shovel ID takes this projection
- Official Mojang Java1.21.1 client SHA1
  `30c73b1c5da787909b2f73340419fdf13b9def88`: handheld inherits generated, whose
  FIXED display is rotation `[0,180,0]`, scale `[1,1,1]`. Flint/steel inherits
  generated directly

The complete Java rotation is `Rx(-180) Ry(25) Rz(-45) Ry(180)`, converted as a
matrix to Bedrock's ZYX/sign convention. The existing audited sprite mesh's U
axis is separately converted with a 180-degree Y basis bone. These are two
explicit transforms, not a blanket rotation on the native `rightitem` bone.
Tests compare actual mesh texel positions and both plane depths with the full
Java transform and reject missing FIXED or reordered rotations.

The source facts, hashes and exact model URLs are in the checked fixture
`development/gameplay_core/fixtures/rack-tool-display.json`. No native held-item
inverse is assumed or calibrated by this implementation.

## Four-cell fit adaptation

The original Java renderer uses three hooks. Its literal `.75` scale gives the
reviewed Bedrock sprites widths of about `.320` blocks (knives), `.260` (shovel)
and `.741` (flint/steel), exceeding the owner's four-cell width `.21875`.
The new display preserves source orientation and aspect ratio, then uniformly
fits each actual opaque silhouette into the shared clicked cell, with `.03125`
block total clearance on both axes. It recenters the fitted bounds in the cell.
No item is stretched independently by axis.

The cell Y range remains `5/16..9/16`. Known sprite helpers move from the old
native anchor `.35` to the click-row center `7/16 = .4375`, a `+.0875` block
translation. Fixed X slot centers and Z `-.27` remain unchanged. Native tagged
fallback retains `.35`. The half-pixel clearance keeps opaque corners strictly
below the upper-row hit boundary, avoiding a seasoning-cell click on a tool.

The generated `RACK-TOOL-DISPLAY-FIT.json` records exact bounds and fitting data.
Uniform factors relative to source `.75` are `.2639865316` for all four knives,
`.2538332035` for the shovel and `.2531137511` for flint/steel. Final uniform
scales are approximately `.1979898987`, `.1903749026` and `.1898353133`.
This fit and recentering are explicit owner-layout adaptations, not unchanged
Java size/placement or accepted client aesthetics.

## Original texture references

The four knives and shovel reference `textures/items/kc_*` paths verified from
the original Cookery1.6.0 archive SHA256
`da12fe6d39d7514aff1de3c963d69899324d771be5ca0fc3da1ccb759c7ad458` and its item
texture aliases. Flint/steel references vanilla `textures/items/flint_and_steel`;
its outline was inspected from Mojang Bedrock samples tag `v1.26.50.4`, commit
`46ba6ea985fb5a92d79a9419198f10dda14c199d`, PNG SHA256
`f675c6e488c15b6e777823298b1bf087446667d49240f9f916a786c4f73a4c3b`.

Only derived alpha-mask facts and generated geometry are added. No external PNG,
host item definition, complete author script or original mcaddon is copied into
the public project. Alpha contour sides use the existing audited span generator,
not a rectangular opaque wall or a zero-thickness plane.

## Runtime safety and limits

The dedicated helper has no inventory, equipment, loot or armor-stand runtime.
Its client-synced `ready` property defaults to false. It receives only a known
model index after placement, then becomes visible. Switching between a known
item and a generic extension replaces only that slot's transient helper. Empty
slots remove the helper; startup removes both old and new transient render types.
The existing budget, observer checks, single work queue and invalid-entity
cleanup remain in use.

The original native ItemStack remains authoritative, including name, damage,
enchantments, lore and custom metadata. This projection does not display custom
names, enchantment glint, private model overrides or other per-stack visual data.
Those are not certified by storage conservation tests. Color-only resource-pack
texture changes remain visible through the external texture reference; changed
alpha silhouettes/resolution, animated textures or new host art require a new
outline review. Generic tagged items still have native orientation limitations.

## Verification and release boundary

Authoring: `python tools/build_rack_tool_display.py`

Idempotent source check: `python tools/build_rack_tool_display.py --check`

Focused gates:

- `python development/gameplay_core/test_rack_tool_display.py`
- `node --test development/gameplay_core/test_rack_tool_runtime.mjs development/gameplay_core/test_rack_visual_selection.mjs development/gameplay_core/test_rack_geometry.mjs`

These checks cover source inheritance, matrix order, sprite UV/contour alignment,
read-only known/fallback routing, helper replacement/cleanup, unchanged non-rack
poses, all slot masks and all cardinal facings. They are not BDS, native
Blockbench, saved-world, or rendered-client acceptance. The source-derived fit proves non-overlap and click-row coherence for the
reviewed silhouettes, not native legibility, appearance or hook contact.

No version, lock or history identity is assigned by this bounded implementation.
The integrated candidate still requires current BSM status before merge, release
or deployment, canonical gates and separate native/client acceptance.
