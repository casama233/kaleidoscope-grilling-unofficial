# Portable ProjectileDodge height and rider handling

The original Cookery1.6 helper attempts at most16 teleports, samples each axis
within a range3 around one captured origin, clamps sampled Y to its level's
minimum plus logical height minus1, and stops riding before each attempt if
the actor is still a passenger. Grilling's prior direct loop omitted the Y
clamp and rider exit.

Author sources: [Forge1.20.1](https://github.com/KaleidoscopeMods/KaleidoscopeCookery/blob/2f4e386ce23f49a385ddf003c67fc6415c55417a/src/main/java/com/github/ysbbbbbb/kaleidoscopecookery/event/effect/ProjectileDodgeEvent.java#L73-L90)
and [NeoForge1.21.1](https://github.com/KaleidoscopeMods/KaleidoscopeCookery/blob/4d39e36cfa749939ba5f9d6d3b715ef9a984cb9c/src/main/java/com/github/ysbbbbbb/kaleidoscopecookery/event/effect/ProjectileDodgeEvent.java#L73-L90).
Both original Minecraft versions' three vanilla dimension definitions were
read independently from official publisher content. Their min/build/logical
height values agree. Exact source JSON, entry records and publisher archive
identities are in `fixtures/java-projectile-dodge-movement-160.json`.

| Supported Bedrock dimension ID | Original vanilla min Y | Original logical upper Y |
| --- | --- | --- |
| `minecraft:overworld` | -64 | 319 |
| `minecraft:nether` | 0 | 127 |
| `minecraft:the_end` | 0 | 255 |

Nether's original build height is256 but its **logical** height is128; using
build height as the clamp would be wrong. Forge1.20.1's official archive was
read through bounded HTTP ranges for its ZIP directory and only the three
dimension JSON entries. Selected entry sizes/CRCs were checked; the complete
23MB archive was not downloaded or fully hashed by that lookup. Neo1.21.1
reuses the existing reviewed official client reference and reads only those
entries. No game JAR is exported with the port.

`tryProjectileDodgeMovement(entity)` runs only in a mutable callback after the
caller has acknowledged its effect fee and claimed the action. It returns
`success`, the immutable helper-stage `origin`, actual `destination` when
readable, `attempts`, dimension ID and a bounded failure reason. It changes no
effect, inventory, sound or ledger state. The caller plays the existing audio
helper only after an observed successful teleport.

The core uses the reviewed vanilla bounds above. Native `heightRange` is only
a coverage guard; it is never converted into a Java logical height or blindly
reduced by1. Unknown/custom dimensions, incomplete native coverage, invalid
coordinates and unavailable context/APIs do not cause a guessed teleport.
The selected engine still needs its real boundary observation; this coverage
check does not establish every SDK's endpoint convention.

For each attempt, stable `minecraft:riding` identifies the actor's current
mount. That mount's `minecraft:rideable.ejectRider(entity)` ejects only the
target; the helper never calls `ejectRiders` or moves other passengers. It
observes that the actor stopped riding before attempting teleport. If a native
ejection committed and a later callback threw, the observed removed rider
state acknowledges the single ejection. Missing/unobserved rider APIs return
a bounded failure instead of teleporting a guessed mounted actor.

Ordinary false teleport results retry up to16 times from the same captured
origin. Success ends the loop. Unavailable context or a teleport API exception
ends further attempts. An observed true native teleport remains a success even
if the actor disappears before the destination can be read; the caller must
not repeat an already moved action. Random sampling keeps the original uniform
distribution/range but uses `Math.random`; Java's actor RNG sequence is not
exposed by stable Bedrock.

This helper intentionally does not implement Java's downward ground search,
`blocksMotion`/no-collision equivalence, liquid exclusion for the entity AABB,
navigation stop or TELEPORT game event. `checkForBlocks:true` does not imply
those mechanisms. The existing before-hurt protection remains a platform
adaptation to the author's Forge SKIP_ENTITY/Neo canceled impact stage. Custom
logical dimension overrides, native rider timing, player input, collision,
rendering and full Java movement parity remain separate acceptance work.

`test_projectile_dodge_movement.mjs` exercises the actual helper with bounded
API-operation adapters: both original loader bounds, Nether logical height,
native coverage scope, endpoint clamping, immutable sampling, 16-attempt limit,
single-rider ordering, re-mount handling, rejected/committed ejections,
unavailable context, dimension changes, API failures and observed-success
ownership. It creates no Minecraft players and does not certify native BDS
rider state or human client behavior. Client/production-ready status stays
false until actual acceptance.

The selected native rider diagnostic found a readback timing distinction.
With two real cow passengers on a boat, the target's `minecraft:riding`
component was present through the spawn wrapper, a fresh entity lookup and
the mount-returned wrapper at attachment ticks0/1/3. Direct
`ejectRider(target)` immediately removed the target's riding component while
the other passenger retained its own. Both old and fresh mount wrappers still
reported both passengers through `getRiders()` in that same callback; the
mount's list contained only the other passenger at the next tick. The helper's
immediate acknowledgement uses the target component, rather than that delayed
mount list, so this observation requires no runtime fallback or mount scan.

The earlier G85 r2 helper measurement reported failure from the immediate
mount list; that original failed report remains intact. The separate direct
API diagnostic explains why that measurement could not establish a missing
riding component or failed ejection. A focused actual-helper observation now confirms immediate target removal,
preservation of the other rider and the next-tick mount list, with the same
unchanged owned runtime as the finite-fee and audio observations. A destination remaining inside a boat's native
automatic passenger-pickup area can permit a later new attachment; that later
behavior must be distinguished from the immediate targeted exit. These are
native mob observations, not player/client acceptance or full Java movement
parity.

Stable references: [riding component](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entityridingcomponent?view=minecraft-bedrock-stable),
[rideable ejectRider](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entityrideablecomponent?view=minecraft-bedrock-stable),
[Dimension.heightRange](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/dimension?view=minecraft-bedrock-stable)
and [Entity.tryTeleport](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entity?view=minecraft-bedrock-stable).
