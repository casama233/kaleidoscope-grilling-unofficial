# Hinder damage recipients and native class boundary

Cookery Hinder gives the **hurt living entity** Slowness II for 100 ticks when
the responsible living attacker has Hinder. The previous portable subscriber
identified both participants by a health component alone. A native vehicle can
have damage/health operations without being a Java `LivingEntity`, so that
predicate allowed effect calls outside the original event's recipient class.

The independent source-operation counterexample supplied a health-bearing boat
and minecart to the actual after-hurt subscriber. Each received one
`addEffect('slowness',100,{amplifier:1,showParticles:true})` call where the Java
class contract admits none. Living cow, armor-stand class and zero-health living
class controls remained admitted. These are actual-subscriber operation
adapters, not Minecraft players or native observations. They do not establish
whether a selected engine delivers those vehicle callbacks or accepts, ignores
or rejects the effect call.

## Original sources and phases

The independent Cookery1.6.0 pins are
[Forge1.20.1 revision2f4e386](https://github.com/KaleidoscopeMods/KaleidoscopeCookery/blob/2f4e386ce23f49a385ddf003c67fc6415c55417a/src/main/java/com/github/ysbbbbbb/kaleidoscopecookery/event/effect/HinderEvent.java#L16)
and
[NeoForge1.21.1 revision4d39e36](https://github.com/KaleidoscopeMods/KaleidoscopeCookery/blob/4d39e36cfa749939ba5f9d6d3b715ef9a984cb9c/src/main/java/com/github/ysbbbbbb/kaleidoscopecookery/event/effect/HinderEvent.java#L16).
Forge subscribes to `LivingDamageEvent`; NeoForge subscribes to
`LivingDamageEvent.Pre`, not Post. Both receive a `LivingEntity` target and
require the responsible source entity to be a `LivingEntity` with Hinder.
Neither adds a positive-damage or positive-current-health guard.

The selected official Forge branch
[`LivingDamageEvent`](https://github.com/MinecraftForge/MinecraftForge/blob/0ec923d7307eb15bef70d6916329642b733a21ed/src/main/java/net/minecraftforge/event/entity/living/LivingDamageEvent.java#L37)
and
[`LivingEvent.getEntity`](https://github.com/MinecraftForge/MinecraftForge/blob/0ec923d7307eb15bef70d6916329642b733a21ed/src/main/java/net/minecraftforge/event/entity/living/LivingEvent.java#L35)
retain that class in both construction and access. This event runs after final
damage reductions and resource consumption, before health subtraction.
The corresponding official NeoForge
[`Pre` constructor](https://github.com/neoforged/NeoForge/blob/a2d6402a3c1eec093aef7e7d10ac5145906c199e/src/main/java/net/neoforged/neoforge/event/entity/living/LivingDamageEvent.java#L51)
and
[`LivingEvent.getEntity`](https://github.com/neoforged/NeoForge/blob/a2d6402a3c1eec093aef7e7d10ac5145906c199e/src/main/java/net/neoforged/neoforge/event/entity/living/LivingEvent.java#L33)
also retain `LivingEntity`; Pre runs before health and absorption changes.
Bedrock after-hurt remains a different phase. Class filtering does not certify
arbitrary addon cancellation, zero-hit delivery or damage ordering.

Forge's immutable [Boat patch](https://github.com/MinecraftForge/MinecraftForge/blob/0ec923d7307eb15bef70d6916329642b733a21ed/patches/minecraft/net/minecraft/world/entity/vehicle/Boat.java.patch#L7)
explicitly retains an `Entity` superclass. Selected Mojang1.21.1 mapped class
declarations independently show Boat and AbstractMinecart extending
VehicleEntity, VehicleEntity extending Entity, and ChestBoat extending Boat;
this inheritance does not pass through LivingEntity. The official
[Bedrock boat definition](https://github.com/Mojang/bedrock-samples/blob/46ba6ea985fb5a92d79a9419198f10dda14c199d/behavior_pack/entities/boat.json)
has boat/inanimate families. Its lack of an explicit health component does not
prove a particular engine's implicit health getter behavior.

## Bounded portable classification

The correction uses the existing public [World Liquor native damage adapter](https://github.com/casama233/kaleidoscope-world-liquor-unofficial/blob/ba6c031ec2da6a71688551c59388ab868824b6d0/runtime/BP/scripts/kill-credit.js#L5)
class contract: a health-bearing player, armor stand or native mob-family
entity. Health alone is insufficient. This distinguishes known living classes
from vehicles and storage/render helpers without trying to infer Java classes
from arbitrary custom identifiers.

The actual Hinder subscriber uses the owned `isCookeryLivingEntity` predicate
both when selecting a responsible source and when admitting attacker/victim.
An independent after check imported that production predicate and repeated only
the five earlier class operations. The two vehicle calls changed from one to
zero; the three living-class controls stayed at one. This checks the relevant
source correction without rerunning unrelated suites or claiming native
vehicle effect behavior.

Do not import an effect-recipient filter's additional `health > 0` requirement
into this damage rule. Native after-hurt health may already reflect the hit,
while the original handler runs before that change and does not ask for a
positive current value. The existing zero-amount behavior must also remain.

Projectile attribution remains separate: a reported responsible living actor
has priority; a native arrow reported as the source may resolve its recognized
projectile owner; an unrelated reported nonliving actor must not inherit a
different projectile's owner. Tightening the class check must preserve that
source ownership rule.

Unknown custom native-to-Java classes, subclasses that override damage routing,
native vehicle callback/effect behavior and human client acceptance remain
unverified. This source contract does not claim every living-class hit invokes
the Java event, identical engine phases or complete gameplay parity.
# Selected native observations

The selected native engine1.26.51.1 reports cow and armor stand as living under
the reviewed helper. Its ordinary boat, minecart and chest boat have no health
component; the earlier health-only gate already excluded those particular
vanilla vehicles. The new health-bearing vehicle rejection is demonstrated by
source/API compatibility counterexamples, rather than an observed ordinary
native-boat regression.

Actual native cow-attributed damage to a cow produced amplifier1 slowness with
98 ticks remaining after two ticks. Boat- and minecart-attributed native damage
to separate cows produced real hurt callbacks without slowness. Cow-attributed
damage to the vehicle victims did not produce the selected native hurt callback;
those victim cases remain unobserved, not passed negative-event tests. No player,
physical combat, zero-health native lifecycle or Java event-phase claim follows.
