# G118 horizontal support shapes: official Java evidence

Reviewed on 2026-10-08 for Minecraft Java 1.20.1 and 1.21.1. This is a narrow source review of the side-support primitive used by `SkewerRecipeBlock.canSurvive`, covering leaves, glass, ice, soul sand, trapdoors, cauldrons, composters, and the already implemented stair cases. Both Java versions give the results below.

Evidence level: official Mojang client bytecode, decoded with official Mojang mappings and CFR 0.152. Bedrock client placement, rendering, and native state-to-orientation behavior remain separate acceptance work. No Bedrock runtime or test suite was executed for this review.

## Exact inputs and reproduction

Every downloaded artifact was checked against its SHA-1 before inspection. These are the exact objects named by Mojang's version metadata, not a third-party source mirror.

| Version | Artifact | SHA-1 | Official download |
|---|---|---|---|
| 1.20.1 | Client JAR | `0c3ec587af28e5a785c0b4a7b8a30f9a8f78f838` | [client.jar](https://piston-data.mojang.com/v1/objects/0c3ec587af28e5a785c0b4a7b8a30f9a8f78f838/client.jar) |
| 1.20.1 | Client mappings | `6c48521eed01fe2e8ecdadbd5ae348415f3c47da` | [client.txt](https://piston-data.mojang.com/v1/objects/6c48521eed01fe2e8ecdadbd5ae348415f3c47da/client.txt) |
| 1.21.1 | Client JAR | `30c73b1c5da787909b2f73340419fdf13b9def88` | [client.jar](https://piston-data.mojang.com/v1/objects/30c73b1c5da787909b2f73340419fdf13b9def88/client.jar) |
| 1.21.1 | Client mappings | `2244b6f072256667bcd9a73df124d6c58de77992` | [client.txt](https://piston-data.mojang.com/v1/objects/2244b6f072256667bcd9a73df124d6c58de77992/client.txt) |

Reproduce by downloading these four URLs, checking `sha1sum`, and locating the classes below through each official mapping. Extract the corresponding `.class` entries and inspect their bodies and superclass chain. For example, with the 1.20.1 files in the current directory:

```sh
unzip -p client.jar ctu.class > ctu.class
java -jar cfr-0.152.jar ctu.class --extraclasspath client.jar --outputdir decoded
```

CFR was obtained from [its author's distribution](https://www.benf.org/other/cfr/cfr-0.152.jar). Method line numbers below are **original Java source ranges encoded in Mojang's mapping**, not line numbers assigned by the decompiler. The symbol names in the last two columns make each method independently locatable in its exact JAR.

## Primitive being matched

The mod's reviewed source calls `supportState.isFaceSturdy(level, support, facing)` from [Forge `SkewerRecipeBlock.canSurvive`](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/forge-1.20.1/src/main/java/cn/breezeth/kaleidoscope_grilling/skewer/SkewerRecipeBlock.java#L67-L70) and [NeoForge `SkewerRecipeBlock.canSurvive`](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/skewer/SkewerRecipeBlock.java#L75-L78).

The three-argument Java predicate selects `SupportType.FULL`. That type tests `Block.isFaceFull(state.getBlockSupportShape(...), direction)`. Its cached path records the same predicate for every direction and support type. Default support shape delegates to collision shape, but subclasses can replace it. `VoxelShape.getFaceShape` slices at the requested outside boundary; a complete collision cube is therefore neither required nor sufficient for this support test.

| Class / method | 1.20.1 mapped lines; obfuscated symbol | 1.21.1 mapped lines; obfuscated symbol |
|---|---|---|
| `BlockBehaviour.BlockStateBase.isFaceSturdy` | 1234, 1238–1241; `dca$a.d`, `dca$a.a` | 1282, 1286–1289; `dtb$a.d`, `dtb$a.a` |
| `SupportType.FULL.isSupporting` | 15; `cxp$1.a` | 15; `doa$1.a` |
| `Block.isFaceFull` | 300–301; `cpn.a` | 312–313; `dfy.a` |
| `BlockBehaviour.getBlockSupportShape` | 295; `dca.b_` | 317; `dtb.b_` |
| `BlockBehaviour.getCollisionShape` | 349; `dca.c` | 355; `dtb.b` |
| `VoxelShape.getFaceShape` / `calculateFace` | 179–194 / 198–206; `efb.a` / `efb.b` | 186–201 / 205–213; `exv.a` / `exv.b` |

## Confirmed horizontal faces

| Family / state | Full collision cube | Sturdy horizontal faces | Consequence for separate classifiers |
|---|---|---|---|
| Vanilla leaves | Yes | None | `_leaves` must not inherit a positive side-support result from full collision. |
| Plain glass | Yes | All four | Keep the positive full-collision and side-support results. |
| Ice | Yes | All four | Keep the positive full-collision and side-support results. |
| Soul sand | No; collision height is 14/16 | All four | Side support needs a positive exception; full-cube collision remains false. |
| Trapdoor, closed | No | None | No horizontal support. |
| Trapdoor, open | No | Only the face opposite Java `FACING` | Side support depends on the open state and orientation. |
| Empty, water, or lava cauldron | No | None | Keep false: the lower wall has gaps between the feet. |
| Composter, every level | No | All four | Side support needs a positive exception; full-cube collision remains false. |

The geometry and overrides responsible for these results are:

| Evidence | 1.20.1 | 1.21.1 | Observed behavior |
|---|---|---|---|
| `LeavesBlock.getBlockSupportShape` | line 42; `ctu.b_` | line 50; `dki.b_` | Returns `Shapes.empty()` unconditionally. |
| `SoulSandBlock.getCollisionShape` / `getBlockSupportShape` | lines 26 / 31; `cwz.c` / `cwz.b_` | lines 34 / 39; `dnl.b` / `dnl.b_` | Collision uses `(0,0,0)-(16,14,16)`; support returns `Shapes.block()`. |
| `TrapDoorBlock.getShape` | lines 54–67; `cya.a` | lines 68–81; `dom.a` | Open shape is a 3/16-thick vertical panel on one outside boundary; closed shape is a horizontal panel. No collision/support override occurs in its superclass chain. |
| `AbstractCauldronBlock.getShape` and `SHAPE` initializer | line 72; `cof.a`, field `cof.b` | line 71; `der.a`, field `der.b` | Subtracts the inner cavity and bottom slots from a full cube. The slots `(0,0,4)-(16,3,12)` and `(4,0,0)-(12,3,16)` interrupt all four side faces. Empty, layered/water, and lava subclasses add no shape/support override. |
| `ComposterBlock.getCollisionShape` and `SHAPES` initializer | line 224; `cqw.c`, field `cqw.h` | line 233; `dhj.b`, field `dhj.i` | Collision always uses `SHAPES[0]`: full cube minus inner box `(2,2,2)-(14,16,14)`. All four outside walls remain complete at every compost level. |

Glass was also checked through its registered block type: 1.20.1 uses `GlassBlock` (`css`) → `AbstractGlassBlock` (`coi`) → `HalfTransparentBlock` (`ctb`); 1.21.1 uses `TransparentBlock` (`dol`) → `HalfTransparentBlock` (`djo`). The empty glass shape override is **visual shape**, not collision or support. Ice (`cti` / `djw`) also inherits collision/support behavior. Their `Blocks` registrations use `noOcclusion()`, without `noCollission()`; collision remains enabled. Official mappings distinguish these two property methods as `c()` and `b()` respectively in both versions.

For Java trapdoors, the exact open-state mapping is:

| Java `FACING` | Sturdy side |
|---|---|
| north | south |
| south | north |
| west | east |
| east | west |

This table establishes Java source semantics only. Bedrock `direction` / `minecraft:cardinal_direction` values and the rendered hinge orientation require their own native evidence; this review does not certify that mapping or a Bedrock client run.

## Existing stair logic cross-check

The two official `StairBlock` classes (`cxh` / `dnt`) have identical shape-index masks. For both halves, straight stairs support their Java-facing side; `inner_left` additionally supports the counterclockwise side, `inner_right` the clockwise side, and either outer corner has no complete horizontal side face. `getStairsShape` (1.20.1 lines 201–224; 1.21.1 lines 142–165; method `i` in both) checks the front neighbor for an outer corner, then the rear neighbor for an inner corner, requiring equal half, differing facing axis, and `canTakeShape`. This confirms the reviewed Java-facing logic. Native Bedrock stair state and visible orientation acceptance remain pending separately.
