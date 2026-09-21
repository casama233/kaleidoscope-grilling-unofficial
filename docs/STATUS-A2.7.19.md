# A2.7.19 — Sweet Potato Crop / 紅薯作物與完整 CropDropHandler

> Java 基線：Kaleidoscope Grilling 1.1.1 @ `9a1acdab27698457bec16c9362678e574895a28c`。  
> 本批補 Sweet Potato 作物、草帽短草來源，並把 Canola → Sweet Potato → Onion 三分支整合為一個 Java 順序 handler。

## Sweet Potato item

Java `SWEET_POTATO` 是 `ItemNameBlockItem(ModBlocks.SWEET_POTATO_CROP, ...)`，同時帶食物屬性：

- nutrition = 3
- saturationModifier = 0.1
- 非 always edible
- 64 stack
- 同一個 item 直接種 crop
- composter chance = 65%

Bedrock 既有 A2.7.2 Sweet Potato food item 保留原食物數值，A2.7.19 新增：

- `minecraft:block_placer -> kaleidoscope_grilling:sweet_potato_crop`
- `use_on = minecraft:farmland`
- `minecraft:compostable.composting_chance = 65`
- `minecraft:use_modifiers.start_using = if_first`

`if_first` 沿用 A2.7.14 Houttuynia 已驗證做法：有效種植交互優先，其他場合仍可正常食用。

Sweet Potato item texture 仍是 Java 原圖，Git blob SHA-1：`6761c2d89d46df2e536dd6df3fe9fdb7c2262259`。

## Crop

`SweetPotatoCropBlock` 是 `CropBlock`，age 0..7，base seed item 就是 Sweet Potato。

Java Block Properties 複製 `Blocks.BEETROOTS`，再設：

- no collision
- random ticks
- instant break
- no occlusion

作物生長本身仍是標準 CropBlock：

- farmland
- 生存最低亮度 8
- 自然生長最低亮度 9
- 3×3 farmland moisture weighting
- 同種作物 crowding penalty
- bonemeal +2..5

A2.7.19 復用 A2.7.14/15 已測純函式，不重寫第三套生長算法。

八張 crop texture 全部是 16×16，所以直接復用已驗證的 `geometry.kaleidoscope_grilling.houttuynia_crop`。

貼圖 SHA：

- stage0 `608a3eefe99930634897aee339356fd4d87a3829`
- stage1 `22f4433daf385c206e6da0e4860c5877c3ddbb66`
- stage2 `22f4433daf385c206e6da0e4860c5877c3ddbb66`
- stage3 `7b8349e033f88b4f5e79a55e258da8e38a1ccee7`
- stage4 `7b8349e033f88b4f5e79a55e258da8e38a1ccee7`
- stage5 `bec26da1ffb404891263206e4918de9e80fa19a8`
- stage6 `bec26da1ffb404891263206e4918de9e80fa19a8`
- stage7 `1c4f02073284ed2efb738bd69d090750a38ff75e`

## 掉落公式不同於 Canola / Onion

Java loot：

- pool 1：固定 Sweet Potato ×1
- age7 pool 2：先 `set_count = 2`
- 再 `apply_bonus`
- `extra = 3`
- `probability = 0.5714286`

因此成熟總數：

`3 + Binomial(Fortune + 3, 0.5714286)`

Bedrock 對 vanilla Fortune 0..3 完整分布等價；非原版 over-level Fortune >3 不宣稱完全等價。

## CropDropHandler 收口

Java 在一個 handler 中按固定順序做三個獨立分支：

1. Canola Seeds：先 count draw，再 12.5% chance draw
2. Sweet Potato：先 count draw，再 12.5% chance draw
3. Onion：先 count draw，再 12.5% chance draw

每個 count 都是：

`1 + random(0..Fortune)`

A2.7.15 和 A2.7.17 為了小批移植各自有獨立 `playerBreakBlock` subscriber；如果直接再加第三個，註冊順序會成為 Canola → Onion → Sweet Potato。

A2.7.19 因此在**最終生成包**中移除 A2.7.15 / A2.7.17 的兩個舊 acquisition subscriber，並由一個新的 subscriber 統一處理：

`Canola → Sweet Potato → Onion`

這個生成期 patch 不修改歷史 development source，因此 A2.7.15 / A2.7.17 仍可各自重建與驗證。

現在可以標記：

- 三分支順序完整 ✅
- count/chance 呼叫順序完整 ✅
- 各分支概率與數量分布精確 ✅
- Java RandomSource 與 JS `Math.random` PRNG 算法本身相同 ❌

也就是我們對齊的是 gameplay 隨機語義與 draw order，不虛報底層 RNG bitstream 一致。

## 下游

既有：

- A2.7.2：Sweet Potato → Cookery Millstone → Sweet Potato Powder ×1
- A2.7.1：Powder 揉製
- A2.7.2：Powder Chopping Board 加工

因此 A2.7.19 後：

`草帽打短草 → Sweet Potato → 種植/繁殖 → Powder → Sheet`

這條主要生存取得與加工鏈閉環。

## Java contract pin

- `SweetPotatoCropBlock.java` `1c40e7e39e6940825414564190c96e92a43cc1b2`
- `CropDropHandler.java` `36a58893c4788626a6b5a610b2a230fd709b4ece`
- `ModItems.java` `6f190e03dc1b7c54bbbae1d5d49d35c78c19b63a`
- `ModBlocks.java` `69f91d7c18ecfa14c206b910d2d4e1d92ce9f6d0`
- `CommonSetup.java` `06e34b81779f72b35a66cedbce19418eb248786a`
- blockstate `046feabc10ff69d45d52472a19ecc827e57375eb`
- loot `d56a547eb8ccd3c12cffe51bed647b6204f2dbd0`

## CI

沿用 A2.7.18 驗證過的增量模式：

1. 驗證已發布 A2.7.18 baseline。
2. 套 A2.7.19。
3. 驗證 Sweet Potato crop + 統一 CropDrop handler。
4. checksum-pin Cookery 草帽與 Millstone contract。
5. 官方 Dash v1.2.0 全包編譯。
6. source/dist 逐檔比對。
7. main 才正式 publish。

仍保持：

- `minecraft_tested=false`
- `bds_tested=false`
