# A2.7.17 — Onion Crop / 洋蔥取得與種植

> Java 基線：Kaleidoscope Grilling 1.1.1 @ `9a1acdab27698457bec16c9362678e574895a28c`。  
> 本批只完成 Onion item、8 階段 crop、成熟掉落、65% 堆肥與草帽打短草初始取得；Onion Powder 加工留下一小批。

## 本批完成

- `kaleidoscope_grilling:onion` 正式 item
- `kaleidoscope_grilling:onion_crop` 8 階段 crop
- farmland 種植
- Java/vanilla CropBlock 光照、生長速度、crowding、骨粉行為
- Java 8 張 16×16 crop texture
- 未成熟 / 成熟 Fortune 掉落
- Java 65% composter chance
- 戴 Cookery 草帽打短草的初始 Onion 取得

## Java source contract

CI 鎖定並重新檢查：

- `OnionCropBlock.java` `881b9e426e5108b28ad366d248cf6208be797504`
- `CropDropHandler.java` `36a58893c4788626a6b5a610b2a230fd709b4ece`
- `ModItems.java` `6f190e03dc1b7c54bbbae1d5d49d35c78c19b63a`
- `CommonSetup.java` `06e34b81779f72b35a66cedbce19418eb248786a`
- onion blockstate `3769d7a50dfc62a7a2e8bfca918c314ff3ff5a59`
- onion crop loot `b96926076396c2a70003aaca65766fcfee9e27d6`

## Onion item

Java：

`ingredient("onion", () -> new ItemNameBlockItem(ModBlocks.ONION_CROP.get(), new Item.Properties()))`

因此：

- 64 stack
- 非食物
- item 本身直接種 Onion Crop
- Java `CommonSetup` 的 composter chance = `0.65F`

Bedrock 對齊：

- `minecraft:block_placer` -> `kaleidoscope_grilling:onion_crop`
- `use_on = minecraft:farmland`
- `minecraft:compostable.composting_chance = 65`

item texture Git blob SHA-1：`103aa78661bf35aa6b3a42989a398573056faff1`。

## 初始取得：草帽打短草

Java `CropDropHandler` 在成功破壞 `Blocks.SHORT_GRASS` 後，若：

- 非 Creative
- 頭戴 `kaleidoscope_cookery:straw_hat` 或 `straw_hat_flower`

則三次獨立 `tryDrop`：Canola、Sweet Potato、Onion。

Onion 分支：

- count = `1 + random(0..Fortune)`
- chance = 12.5%

A2.7.17 直接復用 A2.7.15 已驗證的草帽集合、Fortune count 與 12.5% helper，所以 **Onion 分支自己的概率與數量分布精確對齊**，而且可以和 Canola 在同一次打草中同時成功。

目前 Sweet Potato 分支尚未落地，因此 Java 原碼完整 PRNG 呼叫順序（Canola -> Sweet Potato -> Onion）還不是 byte-for-byte 一樣；這只影響原始 RNG stream 次序，不影響 Onion/Canola 各自的概率與數量分布。等 Sweet Potato crop slice 加入後再統一收口。

## 作物

`OnionCropBlock` 是標準 `CropBlock`：

- age 0..7
- farmland
- 生存最低亮度 8
- 自然生長最低亮度 9
- Java CropBlock 3×3 farmland moisture 權重
- 同種作物 crowding penalty
- 骨粉 +2..5 age

A2.7.17 不再複製算法，而是復用 A2.7.15 -> A2.7.14 已測純函式。

所有 Onion crop texture 都是 **16×16**，可安全復用 A2.7.14 的 `geometry.kaleidoscope_grilling.houttuynia_crop` 交叉作物 geometry，不存在 Canola 的 16×28 UV 特例。

貼圖 SHA：

- stage0 `490cd255f3e94a82844e5c0dd4fbc0f39e7ed851`
- stage1 `27e70b8e92331894e46926a1a9acd19b77a7329d`
- stage2 `22f7dd1f49602fce4cce32046bc2b70140b2cb7f`
- stage3 `8963fc4f952806dc0833eb19a4fbe1b831a3eb74`
- stage4 `348515d3f3c59a5a06a4d366f831b676e71f16b4`
- stage5 `5a4631796be63179bcf796359eeba00a5986e04c`
- stage6 `e8badfe410205c7d82745124cec24c5a93802208`
- stage7 `857cddb6802c9cf63f32d4ff799fd799beb753ff`

## 掉落

Java：

- 未成熟：固定 1 Onion
- age7：固定第一個 1，再第二 stack 套 Fortune binomial
- `extra = 2`
- `probability = 0.5714286`

總數：

`2 + Binomial(Fortune + 2, 0.5714286)`

Bedrock 對 vanilla Fortune 0..3 完整分布等價；非原版 Fortune >3 不宣稱完全等價。

## 下游

repo 已有 `onion_powder` item，但 Java 還有：

`#kaleidoscope_grilling:ingredients/onions -> Cookery Millstone -> onion_powder ×1`

這條加工在本批不塞進來，所以：

- Onion 生存取得：完成
- Onion 種植/繁殖：完成
- Onion -> Onion Powder：未完成

下一小批可以直接接公開 Cookery Millstone Extension API。

仍保持：

- `minecraft_tested=false`
- `bds_tested=false`
