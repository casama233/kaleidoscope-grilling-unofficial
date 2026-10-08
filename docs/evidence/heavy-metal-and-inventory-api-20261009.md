# Stable API recheck: Heavy Metal and custom inventory icons

Checked **2026-10-09 Hong Kong / 2026-10-08 UTC** against Grilling main
`f7bd2d26367c113ab8881bc67e9f5e69624917ff` and its stable dependencies
`@minecraft/server` **2.9.0**, `@minecraft/server-ui` **2.2.0**.
No beta dependency, native player probe, UI override or rendered-client claim
is introduced by this work.

## Official source boundary

The latest [Mojang sample main][sample-head] was read back as
`46ba6ea985fb5a92d79a9419198f10dda14c199d` (sample 1.26.50.4; commit dated
2026-09-16). The exact [server bindings][server-bindings] were inspected, including
`WorldBeforeEvents`, `WorldAfterEvents`, `Entity`, `Effect`, the entity/item
component maps, `ItemStack` and `ItemDyeableComponent`. This is declaration
evidence; it does not establish runtime ordering on another engine version.

| Requirement | Confirmed stable surface | Remaining boundary |
| --- | --- | --- |
| Cancel an incoming hit | [`EntityHurtBeforeEvent`][before-hurt] has writable `cancel` and `damage`, plus `hurtEntity` and `damageSource`. The event is present in the exact 2.9.0 bindings. | It does not expose a final death decision or a native totem outcome. |
| Read absorption remaining after earlier hits | [`Effect`][effect] exposes amplifier and duration. The inspected entity/component bindings have no remaining-absorption value. | An amplifier only bounds the initial shield. The existing conservative lethal predicate cannot resolve every partly spent shield. |
| Act at Java's death callback | The exact event inventory has `entityDie` only among after events; before events include hurt/heal/remove. | No stable before-death/totem event was found. `entityRemove` concerns entity removal; it is not a replacement death-cancellation API. |
| Draw three independently colored skewer ingredients in an inventory slot | [`ItemDyeableComponent`][dyeable] exposes one writable RGB. [`ItemStack`][item-stack] exposes no icon/texture/aux setter. The modern [icon schema][icon-schema] supplies named texture references. | No verified arbitrary per-stack three-color/variant compositor or dynamic-property-to-slot bridge was found. |
| Draw custom images in a form | The exact [server-ui 2.2.0 bindings][ui-bindings] include `CustomForm.image`; image options are onClick, tooltip, visible and width. | A packaged image in a form does not supply runtime pixels or replace each normal inventory slot. |

The current [Microsoft icon reference][icon-doc] and the pinned `ui_common.json`
inventory renderer were also reread. Existing atlas arrays, one custom-color
binding and historical frame fields do not establish a supported new route.
This is a bounded documented-support finding, not a claim that all future or
undocumented client techniques are impossible. The full GUI analysis remains in
[CUSTOM-SKEWER-INVENTORY-RENDER-LIMITS.md](../CUSTOM-SKEWER-INVENTORY-RENDER-LIMITS.md).

## Java Heavy Metal contract and the implemented correction

Author commit `9a1acdab27698457bec16c9362678e574895a28c` has equivalent
`AdvancedSeasoningHandler.onDeath` behavior in [NeoForge 1.21.1][java-neo]
and [Forge 1.20.1][java-forge]: an active Heavy Metal effect with no poisoning
cancels death, removes Heavy Metal, sets health to 1, adds **12000 ticks** of
poisoning and broadcasts entity event **35**. There is no amplifier-dependent
extra rescue in either handler.

G118 already used before-hurt cancellation. Its concrete storage failure was
the later pair of `fxClear` / `fxSet` calls: both passed through a wrapper that
swallowed write errors, so health/sound could proceed without consuming the
rescue and recording poisoning. A scheduler error could also leave its pending
reservation behind.

The dedicated `heavy_metal_damage_runtime.js` is called from the existing single
main subscriber after projectile dodge and invincibility. It:

1. Reserves once and cancels only after scheduling succeeds. A callback queued
   by a scheduler that then throws loses its token and cannot settle later.
2. Rechecks the actual stored effect, clock, poisoning and living health. It
   submits the complete Heavy Metal-to-poisoning transition through the actual
   effect writer in one stored-field update, preserving other active effects.
3. Supplies an exact `expectedRaw` preimage. The writer compares the actual field
   even when its same-tick cache already resembles the desired result; unrelated
   callers retain their prior cache and projectile-dodge generation behavior.
4. Directly rereads the actual stored transition before setting health or
   playing the existing sound. Health writes are acknowledged before sound.
5. Quarantines an already protected claim if its read/write outcome is unknown.
   The same raw Heavy Metal until/amplifier cannot authorize another rescue.
   It neither retries unknown writes nor replays native damage. Death, entity
   removal, logout and respawn invalidate queued work through the main owner.

The reservation is session-local. Same-byte external removal/reinsertion is not
observable; disconnect/reload and crash-atomic protection are not solved here.
Partly spent absorption, other addons' later changes, full native totem/death
ordering and Java event-35 client presentation remain unclosed. The old
`ordinary-heavy-metal-2.8.73-native.json` evidence belongs only to that historical
candidate and is not reused as native acceptance for this correction.

[sample-head]: https://github.com/Mojang/bedrock-samples/commit/46ba6ea985fb5a92d79a9419198f10dda14c199d
[server-bindings]: https://github.com/Mojang/bedrock-samples/blob/46ba6ea985fb5a92d79a9419198f10dda14c199d/metadata/script_modules/%40minecraft/server-bindings_2.9.0.json
[before-hurt]: https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entityhurtbeforeevent?view=minecraft-bedrock-stable
[effect]: https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/effect?view=minecraft-bedrock-stable
[dyeable]: https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/itemdyeablecomponent?view=minecraft-bedrock-stable
[item-stack]: https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/itemstack?view=minecraft-bedrock-stable
[icon-schema]: https://github.com/Mojang/bedrock-samples/blob/46ba6ea985fb5a92d79a9419198f10dda14c199d/metadata/json_schemas/server/item/1.26.30/minecraft_icon%20v1.21.80.json
[icon-doc]: https://learn.microsoft.com/en-us/minecraft/creator/reference/content/itemreference/examples/itemcomponents/minecraft_icon?view=minecraft-bedrock-stable
[ui-bindings]: https://github.com/Mojang/bedrock-samples/blob/46ba6ea985fb5a92d79a9419198f10dda14c199d/metadata/script_modules/%40minecraft/server-ui-bindings_2.2.0.json
[java-neo]: https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/seasoning/AdvancedSeasoningHandler.java
[java-forge]: https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/forge-1.20.1/src/main/java/cn/breezeth/kaleidoscope_grilling/seasoning/AdvancedSeasoningHandler.java
