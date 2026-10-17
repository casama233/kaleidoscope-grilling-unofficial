# Projectile Dodge precedes Invincible damage cancellation

When an actor has both effects, a normal Java projectile impact uses Projectile Dodge: it attempts teleport and consumes the finite 200-tick fee. Invincible remains active. The projectile does not then trigger Invincible’s damage feedback.

The earlier Bedrock before-hurt subscriber checked Invincible first. With both effects it canceled damage, played shield feedback, preserved the dodge budget and queued no teleport. This is a portable ordering defect in the subscriber; the separate Bedrock impact-stage limitation does not require this order.

## Exact author sources

Projectile Dodge belongs to **Cookery 1.6.0**. Invincible belongs to **Grilling 1.1.1**, not Cookery. These reviewed sources remain distinct:

| Source | Event stage and action |
| --- | --- |
| [Cookery Forge 1.20.1 at `2f4e386`](https://github.com/KaleidoscopeMods/KaleidoscopeCookery/blob/2f4e386ce23f49a385ddf003c67fc6415c55417a/src/main/java/com/github/ysbbbbbb/kaleidoscopecookery/event/effect/ProjectileDodgeEvent.java#L29) | `ProjectileImpactEvent`; entity impacts become `SKIP_ENTITY`, followed by teleport and finite-duration charge. |
| [Cookery NeoForge 1.21.1 at `4d39e36`](https://github.com/KaleidoscopeMods/KaleidoscopeCookery/blob/4d39e36cfa749939ba5f9d6d3b715ef9a984cb9c/src/main/java/com/github/ysbbbbbb/kaleidoscopecookery/event/effect/ProjectileDodgeEvent.java#L29) | `ProjectileImpactEvent`; cancellation precedes teleport and the same finite-duration charge. |
| [Grilling Forge Invincible at `9a1acdab`](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/forge-1.20.1/src/main/java/cn/breezeth/kaleidoscope_grilling/effect/InvincibleHandler.java#L17) | `LivingAttackEvent`; cancels damage except `GENERIC_KILL`, then emits rate-limited shield/spark feedback. |
| [Grilling NeoForge Invincible at `9a1acdab`](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/effect/InvincibleHandler.java#L17) | `LivingIncomingDamageEvent`; the same damage cancellation and feedback contract. |

Grilling registers Invincible at `HIGHEST` in both [Forge](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/forge-1.20.1/src/main/java/cn/breezeth/kaleidoscope_grilling/KaleidoscopeGrilling.java#L117) and [NeoForge](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/KaleidoscopeGrilling.java#L117). That priority orders listeners of its damage event; it does not move damage ahead of an earlier projectile-impact event.

## Loader dispatch proof

The maintained Forge 1.20.1 arrow patch, inspected at immutable framework commit [`0ec923d`](https://github.com/MinecraftForge/MinecraftForge/blob/0ec923d7307eb15bef70d6916329642b733a21ed/patches/minecraft/net/minecraft/world/entity/projectile/AbstractArrow.java.patch#L29), dispatches the projectile-impact result before its hit routine. For an entity `SKIP_ENTITY`, it marks the entity ignored and does not call that routine. The [LivingEntity patch](https://github.com/MinecraftForge/MinecraftForge/blob/0ec923d7307eb15bef70d6916329642b733a21ed/patches/minecraft/net/minecraft/world/entity/LivingEntity.java.patch) dispatches living-attack cancellation from the damage method, a stage the skipped arrow hit does not reach.

The maintained NeoForge 1.21.1 arrow patch, inspected at [`a2d6402`](https://github.com/neoforged/NeoForge/blob/a2d6402a3c1eec093aef7e7d10ac5145906c199e/patches/net/minecraft/world/entity/projectile/AbstractArrow.java.patch#L18), breaks on canceled projectile impact before `hitTargetOrDeflectSelf`. Its [ProjectileImpactEvent contract](https://github.com/neoforged/NeoForge/blob/a2d6402a3c1eec093aef7e7d10ac5145906c199e/src/main/java/net/neoforged/neoforge/event/entity/ProjectileImpactEvent.java) likewise states that cancellation prevents processing the impact. Invincible’s later incoming-damage hook therefore does not supply feedback for that intercepted hit.

These are loader-stage source facts, not an assumption about arbitrary mod registration order or a claim to have run both Java clients.

## Bedrock repair and evidence boundary

The successful Projectile Dodge reservation now runs before Invincible. If no dodge claim is available, processing continues to Invincible and then the existing damage logic. Already canceled events, non-projectile damage, Invincible bypass causes, the finite ledger and unrelated effect paths retain their existing contracts.

An uncovered production-subscriber regression uses both effects with 200 dodge ticks. The old subscriber cancels with zero queued work, zero teleport calls, one Invincible feedback call and an unchanged dodge deadline. The corrected production subscriber queues the single owned dodge charge, removes the exhausted dodge field, retains Invincible and omits its damage feedback. An independent second case sends two same-tick impacts: it still owns exactly one dodge/teleport, while the second impact falls through to Invincible once the reservation budget is exhausted. Both corrected sequences pass the focused operation-adapter regression; the original counterexample is retained separately.

Production callback/storage/scheduler adapters establish this source ordering and resource ownership. They do not establish native projectile event order, Java `SKIP_ENTITY` equivalence, rendered/audible feedback, real player lifecycle or client acceptance. Those remain separately scoped. This correction must not be reported as complete Java or client parity.
