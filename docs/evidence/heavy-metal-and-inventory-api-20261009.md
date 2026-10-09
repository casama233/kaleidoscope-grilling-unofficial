# Stable API recheck: Heavy Metal and custom inventory icons

Rechecked **2026-10-09 Hong Kong / UTC** against Grilling G119 main
`b010ec2a6709ada74ed96ead19c60da4e0bc2789` and its stable dependencies
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
| Persist a claim before cancelling that hit | The pinned bindings explicitly give both `Entity.setDynamicProperty` and `World.setDynamicProperty` the `restricted_execution` call privilege; their getters and plural setters share that privilege. The current [Entity][entity] and [World][world] references agree. | Dynamic-property writes are permitted here; native `Entity.setProperty`, health mutation and sound are separate surfaces. Actual property readback is not a disk-flush or crash-atomicity guarantee. |
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

G119 introduced `heavy_metal_damage_runtime.js`, called from the existing single
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

That G119 reservation was session-local. G120 adds the persistence barrier below
without changing the single main subscriber, effect-field schema or UUIDs.
Partly spent absorption, other addons' later changes, full native totem/death
ordering and Java event-35 client presentation remain unclosed. The old
`ordinary-heavy-metal-2.8.73-native.json` evidence belongs only to that historical
candidate and is not reused as native acceptance for this correction.

## G120: acknowledged claim before cancellation

The source recheck corrected an overly broad assumption that all writes are
forbidden in before events. In the exact Mojang server 2.9.0 bindings,
`EntityHurtBeforeEventSignal.subscribe` supplies a `restricted_execution`
callback, while entity and world dynamic-property setters explicitly accept
that privilege. `Entity.setProperty` instead requires the default privilege.
G120 uses the permitted dynamic-property surface only; health and sound stay in
the scheduled settlement callback.

The new owned entity field is
`kaleidoscope_grilling:heavy_metal_claim`. Its version-1 JSON contains exactly
`version`, `until`, `amp` and `time`, with finite numeric effect/clock values and
an integral nonnegative amplifier. The claim belongs to this behavior pack under
the existing UUID. It does not replace `kaleidoscope_grilling:a21_fx`, change any
existing effect payload, or write another addon's state. No world-wide receipt
index, polling worker or new player entity property is required.

Admission and settlement now have the following ordering:

1. Read the actual active effect, the current claim and provisional health.
   Only `undefined` is an absent claim. Unreadable, malformed or unknown-version
   claims fail closed. A valid existing claim for the same `until`/`amp` denies a
   second rescue, including after memory cleanup or script reload.
2. Reserve the in-memory callback token, compare the actual saved claim with its
   raw preimage, then write and directly reread the new claim. A setter that
   applied before throwing succeeds only when its readback is exact. Failure or
   unknown readback cannot authorize cancellation.
3. Schedule once, then set and read back `event.cancel`. If scheduling queues a
   callback and then throws, revoke that exact token before attempting cleanup.
   Only an actual `cancel === false` permits restoring the exact previous claim;
   the current raw value must still be this token's receipt, and restoration also
   needs readback. Unknown cancellation retains quarantine instead of refunding
   a hit that may already be protected.
4. The deferred callback must still own both its in-memory token and the exact
   saved claim. It then uses G119's fresh effect preimage, single acknowledged
   Heavy Metal-to-12000-tick-poisoning write, living-health check, HP=1 readback and
   sound ordering. It never resurrects a later death or replays native damage.
5. Existing leave/death/remove/respawn hooks only discard in-memory work. They
   do not erase the persistent claim or try to write through a departed entity
   handle. A completed rescue also retains its receipt. A later eligible effect
   with a different `until` or `amp` may replace that one field after a fresh
   comparison; an old claim does not permanently block all future effects.

Normal login and the existing expiry-pruning pass do not rebase Heavy Metal's
absolute `until`: they read the saved descriptor and either preserve it or prune
it. Explicit food/effect changes, including the existing hot-food increment, are
separate mutations. The claim is deliberately not expired by wall-clock or
effect-clock polling, so rolling the clock back cannot revive the same claimed
descriptor. Same-byte external removal/reinsertion remains indistinguishable
from that descriptor and stays closed; arbitrary third-party mutations are not
certified as owned effect generations.

This closes the source-level loss of an acknowledged reservation when the
in-memory map is forgotten. A reload can leave a protected but incompletely
settled effect quarantined; G120 does not replay the old callback, restore health,
or infer that poisoning was committed. There is no general crash transaction:
an interruption after claim acknowledgement but before cancellation can retain
an unused claim, and Script API readback does not prove a recent world change
has reached durable disk storage. World-save interruption, true before-hurt
ordering, normal logout/rejoin and script-reload scenarios still require native
acceptance of this exact candidate.

Local verification is limited to the pure claim codec and descriptor rules,
module syntax, source ordering and the pinned SDK privilege inventory. Existing
CI adapters receive the new pure-module dependency and a separate property slot
without changing their scenario assertions. No local simulated-player sequence,
BDS load, client rendering or LIVE acceptance is claimed.

[sample-head]: https://github.com/Mojang/bedrock-samples/commit/46ba6ea985fb5a92d79a9419198f10dda14c199d
[server-bindings]: https://github.com/Mojang/bedrock-samples/blob/46ba6ea985fb5a92d79a9419198f10dda14c199d/metadata/script_modules/%40minecraft/server-bindings_2.9.0.json
[before-hurt]: https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entityhurtbeforeevent?view=minecraft-bedrock-stable
[entity]: https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entity?view=minecraft-bedrock-stable
[world]: https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/world?view=minecraft-bedrock-stable
[effect]: https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/effect?view=minecraft-bedrock-stable
[dyeable]: https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/itemdyeablecomponent?view=minecraft-bedrock-stable
[item-stack]: https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/itemstack?view=minecraft-bedrock-stable
[icon-schema]: https://github.com/Mojang/bedrock-samples/blob/46ba6ea985fb5a92d79a9419198f10dda14c199d/metadata/json_schemas/server/item/1.26.30/minecraft_icon%20v1.21.80.json
[icon-doc]: https://learn.microsoft.com/en-us/minecraft/creator/reference/content/itemreference/examples/itemcomponents/minecraft_icon?view=minecraft-bedrock-stable
[ui-bindings]: https://github.com/Mojang/bedrock-samples/blob/46ba6ea985fb5a92d79a9419198f10dda14c199d/metadata/script_modules/%40minecraft/server-ui-bindings_2.2.0.json
[java-neo]: https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/seasoning/AdvancedSeasoningHandler.java
[java-forge]: https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/forge-1.20.1/src/main/java/cn/breezeth/kaleidoscope_grilling/seasoning/AdvancedSeasoningHandler.java
