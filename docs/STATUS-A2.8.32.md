# A2.8.32: correct the advanced-rack item reference

The pinned Java item model is `minecraft:item/generated`, layer0
`kaleidoscope_grilling:item/advanced_rack`. Its placed block model is NOT the
held-item reference. The previous advanced-rack 3D attachment was therefore wrong,
even though its mathematical transform matched that incorrect block reference.

Remove that one held override and retain the already pixel-matched source icon,
max-stack size1, native block_placer target, original world model and every rack
transaction. Existing unused historical hand geometry/animation is retained as
reference, not registered as an item override. The audit now rejects reintroducing
that override. Mutation tests continue against an actual skewer held rig.

106 actual attachables remain:39 skewer items plus67 bottle items. Full existing
transaction/storage/recipe/tag/audio and all150 skewer-stage resource regressions
remain enabled. No client visual acceptance or live deployment is claimed.

Source:
https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/common/src/main/resources/assets/kaleidoscope_grilling/models/item/advanced_rack.json

Audited released Java1.1.1 JAR SHA256:
cf31071e4ba790bcd5c1d3f6005439bc512acba084e70b8ab6a767e8c8f99dd6

Remaining view gaps include dropped/frame 3D skewer/bottle rendering, custom item
composition, per-context lighting and actual native client eating/holding behavior.
Fixed-skewer GUI sprites can be correct because Java's runtime GUI cache intentionally
replaces base-model GUI rendering. Do not infer all GUI items should be3D.

Includes the concurrently published A2.8.31 Board API extension unchanged.
