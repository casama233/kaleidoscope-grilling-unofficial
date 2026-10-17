# A2.8.3 — immersion and rendering repair

User report: persistent actionbar status, UV atlases in the inventory, 3D held
models near the player's feet, and overlapping/flickering model surfaces.

## Changes

- Retire passive crosshair polling and remove 28 routine success/progress
  messages. Necessary interaction failures share a three-second per-player
  throttle; oil-press failures go to the operator rather than every bystander.
- Audit all 155 item definitions and 91 inventory atlas entries. Restore the
  upstream rack inventory sprite, bake a plate sprite, retain the A2.8.1 bottle
  sprites, and give five Java animation strips separate square item sprites.
  Those five inventory icons are currently static; Java color animation is not
  claimed. Original strips and world/hand material textures remain available.
- Rebuild 194 active hand geometries used by 107 attachables with the Bedrock
  item origin at Y=24. Preserve all 150 fixed-skewer bite meshes and seasoning
  fill/variant meshes. Add the missing rack first-person left-hand pose.
- Keep the native vat item renderer; add dedicated native grill/oil-press item
  meshes using their upstream item display transforms. Native block-item
  transforms and entity attachable animations use separate paths.
- Use single-sided cutout materials for solid station surfaces and opaque
  skewer/rack attachables. Preserve opposite-facing interior/exterior faces.
  Remove 88 exact same-facing duplicate faces in rack meshes, plus 20 unnecessary
  tank-fluid side/bottom faces; fluid now renders its exposed top surface.
- Carry stable-server compatibility into source: numeric block AO, current
  damage-sensor enum, removal of invalid crop components, and stable custom-block
  bottle placement capture including all 64 materialized seasoning variants.

## Evidence and limits

`python development/gameplay_core/verify_current.py` passes the complete current
source gate, visual reference checks, guide checks, syntax checks, the previous
gameplay/transaction/data regression suites, and new geometry/feedback tests.
The former A2.8.0/A2.8.1 byte/pose locks are historical and are superseded by the
A2.8.3 gate; reverting to their broken geometry is not a regression requirement.

An isolated BDS 1.26.51.1 instance loaded the server edition with the existing
host dependencies and experiment flags. All 23 Grilling block IDs accepted
`setblock` after the test chunk loaded. No Grilling content/script errors were
found in the final isolated run. The initial no-experiments run exposed invalid
crop components and confirmed the existing container feature requirement; the
crop declarations were corrected and the final run used the host settings.
Unrelated host-pack warnings are not treated as Grilling test failures.

**Client visual acceptance remains pending.** BDS startup, reference checks and
image contact sheets cannot establish first-/third-person alignment, eating
motion, transparency sorting, Vibrant Visuals behavior or GPU-dependent flicker.
The secret skewer's ingredient-dependent dynamic appearance is an older parity
gap and is not implemented by this patch.

## Client acceptance

1. Join with the A2.8.3 resource pack. Look at every station without interacting:
   no Grilling actionbar status should appear. Normal cooking/press progress
   should use existing motion, particles and sounds.
2. Inspect the rack, empty/full seasoning, plate, four animated powders and
   wedding candy in inventory, hotbar, dropped form and item frames.
3. Inspect first person and another player's third person with standard and slim
   skins: rack, bottle variants and every fixed skewer. Check bites and shaking,
   and the native grill, press and vat. Check both supported hand contexts.
4. Walk around every rack fill state, empty/full vats, grill with/without legs,
   every press stage, and one-to-four stacked bottles at near/far distances.
   Repeat with the client's normal graphics and Vibrant Visuals if enabled.

## Sources

- [Mojang bound trident geometry](https://github.com/Mojang/bedrock-samples/blob/main/resource_pack/models/entity/trident.geo.json)
- [Microsoft attachables](https://learn.microsoft.com/en-us/minecraft/creator/documents/attachables)
- [Block material culling modes](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/blockcomponents/minecraftblock_material_instances)
- [Native block item transforms](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/itemdisplaytransforms)
- [Upstream Java source at the audited commit](https://github.com/breezeth-CN/KaleidoscopeGrilling/tree/9a1acdab27698457bec16c9362678e574895a28c)

Fixture hashes and upstream origin are recorded in
`development/gameplay_core/fixtures/a283/provenance.json`. No private host scripts,
world databases, credentials or machine logs are included in this repository.
