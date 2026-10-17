# G2.8.107 original downward ground adjustment

Projectile Dodge previously tested the sampled airborne position directly.
It now searches the original downward block column first, retains the sampled
fractional Y while subtracting exactly one per non-supporting cell, checks
the adjusted body's liquids, then uses Native collision-checked teleport with
explicit velocity retention. The fixed original RNG origin, three draws per
attempt, targeted rider exit and maximum16 attempts remain unchanged. An
unknown cell stops that column; a sample at the original minimum has no
below-cell support and does not teleport.

Motion comes from the actual publisher `blocksMotion` exports for both
maintained Minecraft branches.954 identity-qualified vanilla rows are kept
separate from75 identity holds,60 original21-only facts and431 unknown Native
identities. New/custom or unqualified terrain is a coverage gap; it never
inherits a Boolean from names, material, raycasts or Native solidity.

Native snapshots include legacy material/color/half/direction aliases absent
from the declared metadata. For461 eligible IDs,3,942 complete primary tuples
now bind their exact full Native fields.1,030 exact requests were reused in
the final collection, including495 newly observed requests; the remaining
2,912 were observed once. The resulting facts retain535 older G100R2 API
observations and3,407 G106 observations. Earlier incomplete family/producer
flags stay attached to those older observations. No independent field-domain
whitelist grants impossible color, half or direction combinations.

Six alias source cases and six movement composition source cases failed before
their repair and pass afterward. Existing source-column and movement cases
remain, with literal dry ground supplied to the earlier body-liquid fixtures.
The current source verifier retains the previous complete functional chain.

Six new actual Native cases used a real cow and real placed permutations:
stone support, snow-layer fractional descent, top-slab alias, adjusted-body
water rejection, unqualified-floor rejection and zero-read minimum rejection.
Each passed. Successes retained the actual nonzero three-axis velocity read
before and immediately after movement in the same callback. Initialization
required observing the newly spawned actor after engine ticks; the earlier
failed setup attempts are retained and did not complete movement cases.
These are explicit disposable owned-source overlays, not complete-family
release admission or simulated-player/client evidence.

The maintained original Cookery source heads were checked again: Forge main
`2f4e386ce23f49a385ddf003c67fc6415c55417a` and NeoForge1.21.1
`4d39e36cfa749939ba5f9d6d3b715ef9a984cb9c`. Their handlers retain the
ground-adjustment delegate used here. Public original sources:
[Forge](https://github.com/KaleidoscopeMods/KaleidoscopeCookery/blob/2f4e386ce23f49a385ddf003c67fc6415c55417a/src/main/java/com/github/ysbbbbbb/kaleidoscopecookery/event/effect/ProjectileDodgeEvent.java),
[NeoForge](https://github.com/KaleidoscopeMods/KaleidoscopeCookery/blob/4d39e36cfa749939ba5f9d6d3b715ef9a984cb9c/src/main/java/com/github/ysbbbbbb/kaleidoscopecookery/event/effect/ProjectileDodgeEvent.java).

Complete projectile-impact/cancellation phases, author-owned/custom floors,
Java temporary move/collision/rollback shape equivalence, navigation stop,
teleport game events/byte46, shared actor RNG and player/client acceptance
remain incomplete. G106 pending-seasoning repair and the unresolved client
mixing/sprinkling/display report remain intact. This release does not certify
complete Java parity. Canonical PR/checks/merge and complete-family static,
Native first/restart, fresh saved-world rehearsal and guard admission still
precede the live development update. `client=false; production_ready=false`.
