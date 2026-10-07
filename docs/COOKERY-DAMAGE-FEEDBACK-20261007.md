# Cookery 1.6 damage and flatulence feedback

The previous Grilling handler attached Hinder to `entityHitEntity`, which the
stable Bedrock API defines as a melee event. Both maintained Java Cookery 1.6
branches instead apply 100 ticks of Slowness II when the damage source's
responsible entity is a living actor with Hinder. Projectile damage therefore
missed the Bedrock handler.

The repair subscribes once to `entityHurt`, prefers the reported responsible
`damagingEntity`, and reads the native projectile's `owner` only when that field
is absent. A health component is the Bedrock mapping for a living attacker and
victim. The existing `kaleidoscope_grilling:a21_fx` state and `hinder` key remain
unchanged, including expiry and food/secret-ingredient producers. The Java
handlers have no positive damage amount condition; the port adds none.

Author sources: [Forge HinderEvent](https://github.com/KaleidoscopeMods/KaleidoscopeCookery/blob/2f4e386ce23f49a385ddf003c67fc6415c55417a/src/main/java/com/github/ysbbbbbb/kaleidoscopecookery/event/effect/HinderEvent.java#L16-L24)
and [NeoForge HinderEvent](https://github.com/KaleidoscopeMods/KaleidoscopeCookery/blob/4d39e36cfa749939ba5f9d6d3b715ef9a984cb9c/src/main/java/com/github/ysbbbbbb/kaleidoscopecookery/event/effect/HinderEvent.java#L16-L24).
The loader phases differ: Forge uses `LivingDamageEvent`, NeoForge uses
`LivingDamageEvent.Pre`. Bedrock's after-hurt event does not prove equivalent
ordering with arbitrary damage addons, canceled damage, death or immunity.
Custom entities with differing native components also require separate review.
Zero-damage after-hurt input is preserved if the engine reports it; this is not a
claim that every engine emits that callback.

Flatulence previously played `random.fizz` and emitted one smoke particle. Both
author branches specify ten Cloud particles, center height +0.25, Gaussian
spread 0.25 on each axis, event speed 0.1 blocks/tick, and the original fart
sound at volume 1 with pitch in [0.8, 1.2). The repair restores those event
parameters through the existing Grilling delivery adapter and calls the current
Cookery resource event `kaleidoscope_cookery.fart`. The three samples in the
Cookery 1.6 original resource pack are byte-identical to the corresponding Java
author samples; no host scripts or new copies of those sounds are exported.

Author sources: [Forge flatulence feedback](https://github.com/KaleidoscopeMods/KaleidoscopeCookery/blob/2f4e386ce23f49a385ddf003c67fc6415c55417a/src/main/java/com/github/ysbbbbbb/kaleidoscopecookery/network/message/SimpleC2SModMessage.java#L48-L58)
and [NeoForge flatulence feedback](https://github.com/KaleidoscopeMods/KaleidoscopeCookery/blob/4d39e36cfa749939ba5f9d6d3b715ef9a984cb9c/src/main/java/com/github/ysbbbbbb/kaleidoscopecookery/network/message/SimpleC2SModMessage.java#L48-L57).
The existing sneak edge/impulse is retained as the Bedrock input adaptation.

The owned Cloud definition derives from the [public Tavern free-flight provider](https://github.com/casama233/kaleidoscope-tavern-unofficial/blob/a11a0eea4971373d2be71d5bcd4900e641fb015d/runtime/RP/particles/fx_cloud.json).
It uses Grilling's existing attributed Minecraft 1.21.1 `generic_7..0` sprite
atlas and native velocity variable contract, so it creates no Tavern runtime
dependency. Direct review of the official 1.21.1 `PlayerCloudParticle` confirmed
the free-flight lifetime, size, gray range and friction parameters. That Java
class also attracts particles vertically toward a nearby player; this portable
provider does not implement that behavior. Native sprite projection, frame
timing, mixing and nearby-player attraction remain unverified client behavior.

`test_cookery_damage_feedback.mjs` exercises the actual production subscribers
and flatulence statement with API-operation adapters. Its old-handler
counterexample misses an attributed projectile hurt event; the corrected
handler applies Slowness II once. The focused checks cover expiry, responsible
source priority, missing sources, nonliving mappings, reported zero damage,
removed entities, repeated sneak state, ten particle commands, sound pitch and
feedback failures. These source tests do not certify native Minecraft event
ordering or human audio/render acceptance. The owned Cloud producer has a
`--check` mode; it rebuilds from the committed source fixture.

Stable API references: [melee hit event](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entityhitentityafterevent?view=minecraft-bedrock-stable),
[hurt event](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entityhurtafterevent?view=minecraft-bedrock-stable),
[damage source](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entitydamagesource?view=minecraft-bedrock-stable)
and [projectile owner](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entityprojectilecomponent?view=minecraft-bedrock-stable).

This change keeps `client=false` and does not claim complete Java parity.
