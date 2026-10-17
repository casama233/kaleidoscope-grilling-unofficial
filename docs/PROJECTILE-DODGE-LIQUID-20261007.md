# ProjectileDodge liquid cell precheck

Original Cookery delegates a sampled destination to Java
`LivingEntity.randomTeleport`. Its liquid rejection checks the entity's entire
collision box for any cell with a nonempty `FluidState`. The portable movement
helper previously delegated only native block collision, allowing destinations
that this Java liquid predicate would reject. G86 now calls the read-only liquid
precheck after an acknowledged targeted rider exit and before each native
teleport. A liquid or unsupported candidate cannot reach native teleport;
later candidates retain the existing16-attempt limit.

The two author callers are independently pinned at Cookery1.6.0
[Forge1.20.1](https://github.com/KaleidoscopeMods/KaleidoscopeCookery/blob/2f4e386ce23f49a385ddf003c67fc6415c55417a/src/main/java/com/github/ysbbbbbb/kaleidoscopecookery/event/effect/ProjectileDodgeEvent.java#L90)
and
[NeoForge1.21.1](https://github.com/KaleidoscopeMods/KaleidoscopeCookery/blob/4d39e36cfa749939ba5f9d6d3b715ef9a984cb9c/src/main/java/com/github/ysbbbbbb/kaleidoscopecookery/event/effect/ProjectileDodgeEvent.java#L90).
The official1.20.1 and1.21.1 delegates and `LevelReader.containsAnyLiquid` were
inspected independently with each publisher's mappings. The latter enumerates each axis from
`floor(min)` to `ceil(max)`, excluding the upper limit, and tests whole-cell
fluid-state presence. It does not shrink the tested region to a fluid surface
or fluid voxel shape. The new fixture records the independent loader proof
statuses in `java-projectile-dodge-liquid-forge-proof.json`; a shared author call
alone does not establish a shared native body. The1.20.1 source lookup used
bounded mapping/ZIP ranges and22 selected classes rather than a full JAR.

Java performs its downward support search before this liquid test, preserving
the sampled fractional Y as it descends. This module checks the initially
requested native candidate. It therefore does not establish Java landing or
liquid-rejection equivalence when a request is above water or unsupported
space. Adding the liquid predicate does not resolve that existing ground-stage
gap.

`projectileDodgeLiquidPrecheck(entity,candidate)` returns `allow`, `supported`,
`reason`, `checkedCells` and `plannedCells`, plus the first blocked/unsupported
cell when readable. A successful dry read is the only result with `allow=true`.
A known liquid returns a supported rejection. Unknown context or coverage
returns an unsupported rejection. The module does not move an actor, remove a
rider, spend an effect, choose a candidate, change attempt counts, or emit audio
or feedback.

The movement caller invokes it in the mutable stage after a single-rider exit
was acknowledged and before native teleport. It reads the
actual actor location and `getAABB()` there, translates the actual box center
by `candidate - actor.location` on all three axes, and preserves its actual
half-size extents and center offset. A hard-coded player body, feet-only test
or guessed head height cannot substitute for that box. This is a native-box
adaptation, not a claim that every Java and Bedrock actor shape or pose is
identical. [Entity.getAABB](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entity?view=minecraft-bedrock-stable)
and [AABB](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/aabb?view=minecraft-bedrock-stable)
document those collision bounds and half-size extents.

All input/derived coordinates must be finite, every extent positive, integer
cell bounds and volume safe, and the complete box at most4096 cells. This is an
explicit portable script work contract, **not an original Java cap**. An
oversized box is unsupported before any block is read; the scan is never
truncated and reported dry. Missing bounds, unloaded/exceptional block reads,
missing fluid-presence properties and a changed actor location/dimension or
collision box cannot produce dry permission. Before allowing a dry destination,
the module rereads the actual center/extents and compares all six values with
its copied snapshot. A smaller earlier box cannot grant permission to a later
larger pose at the same feet. This is an operation-context guard, not a claim
that a native pose race was observed.

For cell classification, a positive native `isLiquid` or `isWaterlogged` flag
rejects immediately. False flags may establish dry only for an exact identity
in the selected official vanilla registry and outside the original-source
fluid-carrier mapping. The registry comes from one selected
[Mojang block metadata file](https://github.com/Mojang/bedrock-samples/blob/46ba6ea985fb5a92d79a9419198f10dda14c199d/metadata/vanilladata_modules/mojang-blocks.json),
with1463 exact `data_items.name` identities. No arbitrary `minecraft:` name,
custom script-fluid block, or name pattern is accepted as dry. The catalog is
generated offline from that selected fixture; no complete sample pack or host
behavior source is imported.

`isLiquid` alone explicitly excludes waterlogged cells. `canContainLiquid` and
`isLiquidBlocking` describe capacity/flow rather than current liquid presence,
so this guard does not use them as fluid-state substitutes. Native water/lava
identities and the kelp, seagrass and bubble-column carrier mapping require
explicit original-source proof; the catalog producer refuses an unverified
carrier row. Both original versions' LiquidBlock cache returns nonempty water
or lava for every level0..15, including shallow flowing and falling levels.
BubbleColumn/Kelp/KelpPlant/Seagrass/TallSeagrass each unconditionally return
source water. These facts justify seven exact native carrier IDs; they do not
guess any custom identity. Ordinary dry cells such as wet sponge, cauldron and powder snow
are not declared fluids from their names or contents. The native presence
contracts are documented in [Block](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/block?view=minecraft-bedrock-stable).

Unknown custom blocks remain a conservative unsupported case even when both
native flags are false. A future custom/script-fluid resolver needs its own
source-backed presence contract. Unknown API reads are not converted to air,
dry cells or a shorter body. The manifest's exact `@minecraft/server`2.9.0
[published declarations](https://registry.npmjs.org/@minecraft%2Fserver/2.9.0)
were reviewed, including `getAABB`, `isChunkLoaded`, `isLiquid` and
`isWaterlogged`. The earlier2.7 declaration review is historical evidence,
not the current versioned API input. Declaration availability, the following
native capability observations and integrated gameplay acceptance are distinct.

On native engine1.26.51.1, an actual cow's AABB was observed in absolute world
coordinates, with its center tracking location immediately after each of two
same-tick native teleports while extents stayed unchanged. This establishes
the tested cow's coordinate frame and immediate refresh; it does not establish
every actor's shape/pose or Java geometry equality.

The unchanged liquid module also established15 native dry/fluid/unsupported
cell cases: air and stone; water/lava at source, shallow flowing and falling
levels0,7,8,15; dry/waterlogged slab; kelp and seagrass; and an owned dry custom
block conservatively rejected as unsupported. A further actual-body observation
rejected a water cell outside the feet cell. Kelp and seagrass reported
`isLiquid=false,isWaterlogged=true`; the wet slab reported the same flags.
The sampled water/lava cells reported their base native IDs with
`isLiquid=true,isWaterlogged=false`; separate `flowing_water`/`flowing_lava`
identity getters were not established by those depth-state observations.

The initial capability run failed its attempted bubble-column setup, so that
scoped failed result remains retained. A focused fresh follow-up established
natural soul-sand upward and magma downward columns in the actual body cells;
both native bubble-column states reported both presence flags true and were
rejected by the unchanged liquid module. The earlier15 established cell cases
were reused, not rerun. This composite establishes read-only API/cell capability,
not integrated ProjectileDodge movement, Hinder damage routing, family admission
or client acceptance. Later sparse integrated movement and Hinder observations are described separately below; complete gameplay/client acceptance remains pending.

The new `test_projectile_dodge_liquid.mjs` cases exercise the actual module:
translated center offsets, negative fractional/integer boundaries, the
exclusive upper cell, head-height liquid missed by a feet check, waterlogged
non-liquid blocks, explicit carriers, dry liquid-looking names/containers,
unknown custom and future identities, exceptional reads, invalid/unsafe boxes,
whole-volume work rejection, changed position/dimension/box and read-only behavior.
The module's14 source cases were reused. The affected movement file was run
once after integration, with20 passing cases including7 new dry/fluid,
waterlogged-body, unavailable-read, later-success, post-exit dimension/box and
remount operations. No simulated Minecraft players were used. API-operation
dimension/pose/remount sequences do not claim observed native races.

The movement integration checks the original dimension after rider exit and
after dry permission, and rejects a remount before native teleport. It does
not perform a second eject and reuse earlier box permission. A later native
success clears an earlier candidate failure reason; observed movement success
is retained if its destination disappears afterward. Fee reservation and
two-site feedback remain owned by their existing caller and run under their
separate source/native evidence.

This module does not add Java downward support search, `blocksMotion`, generic
Java collision geometry, navigation stop, TELEPORT game events or entity-event
rendering. The original16 attempts, targeted rider handling, fee reservation
and two-site audio remain in the integrated source. Custom
logical dimensions, RNG sequence, impact phase, arbitrary actor shape and
human client behavior stay separate limitations. Registry identity is the
declared vanilla-ID mapping, not proof for arbitrary addon overrides or Java
custom classes; `client=false` and
`production_ready=false` remain authoritative.

The separately observed integrated native helper rejected all16 repeated wet candidates without movement and succeeded on the second, independently dry candidate with an empty success reason. A paired dry top-slab geometry permitted native movement before the identical waterlogged body-cell candidate was rejected. These sparse observations reuse unchanged module/frame evidence and do not establish Java downward-ground or physical player parity.
