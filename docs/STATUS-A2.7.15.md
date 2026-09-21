# A2.7.15 — Canola Crop / 油菜取得與種植

> Java 基線：Kaleidoscope Grilling 1.1.1 @ `9a1acdab27698457bec16c9362678e574895a28c`。  
> 本批只完成 canola seeds 的初始取得、8 階段作物、成熟掉落與堆肥；種子磨成菜籽粉留下一小批。

## 本批完成

- `kaleidoscope_grilling:canola_seeds` 正式 item
- `kaleidoscope_grilling:canola_crop` 正式 8 階段 crop
- farmland 種植
- Java/vanilla CropBlock 光照、生長速度、crowding、骨粉行為
- Java 8 張 crop texture
- 未成熟 / 成熟 Fortune 掉落
- Java 30% composter chance
- 戴 Cookery 草帽打短草的初始油菜籽取得

## Java source contract

CI 鎖定並重新檢查：

- `CanolaCropBlock.java` `9b728ebc1961a8527d2b36b97b90dc2c6903b5fb`
- `CropDropHandler.java` `36a58893c4788626a6b5a610b2a230fd709b4ece`
- `ModItems.java` `6f190e03dc1b7c54bbbae1d5d49d35c78c19b63a`
- `CommonSetup.java` `06e34b81779f72b35a66cedbce19418eb248786a`
- canola blockstate `25a57e64eeb2b7635e9075578ae121d1c4719a17`
- canola crop loot `6e4643a2b44e73add93b4cb674adc2489eacfa70`

## Canola Seeds

Java `CANOLA_SEEDS` 是 `ItemNameBlockItem(ModBlocks.CANOLA_CROP, new Item.Properties())`：

- 64 stack
- 不是食物
- 本身就是 crop 的種子

Bedrock 同樣用一個 item：

- `minecraft:block_placer` -> `kaleidoscope_grilling:canola_crop`
- `use_on = minecraft:farmland`
- Java `CommonSetup` 的 0.30 composter chance 用 stable `minecraft:compostable { composting_chance: 30 }` 對齊。

item texture 使用鎖定 Java 原圖，Git blob SHA-1 `89a7008164006a16dcd194ce27b6e5c165b14987`。

## 初始取得：草帽打短草

Java `CropDropHandler`：

1. 必須成功破壞 `Blocks.SHORT_GRASS`；
2. Creative 不觸發；
3. 頭部必須是：
   - `kaleidoscope_cookery:straw_hat`
   - `kaleidoscope_cookery:straw_hat_flower`
4. Fortune 從主手工具取得；
5. 先算 count：`1 + random(0..Fortune)`；
6. 再以 12.5% chance 決定是否掉落。

Bedrock 使用 stable `world.afterEvents.playerBreakBlock`，以 `brokenBlockPermutation` 判斷原 block 確實是 `minecraft:short_grass`，並以 `itemStackBeforeBreak` 讀 Fortune。這避免 before-event 中其他 Add-On 取消破壞時仍錯誤掉種子。

Cookery 1.0.6 archive 仍 checksum-pin；A2.7.15 contract 會直接遍歷 Behavior Pack item JSON，確認兩頂草帽 identifier 真的存在。

Java 同一個 `CropDropHandler` 還會獨立嘗試掉 Sweet Potato 與 Onion；本批只移植 Canola 分支，另外兩種留給各自 crop slice。

## 作物

Java `CanolaCropBlock` 沒有自訂生長公式，而是標準 `CropBlock`：

- age 0..7
- farmland
- 生存最低亮度 8
- 自然生長最低亮度 9
- Java CropBlock 3x3 farmland moisture 權重
- 同種作物 X/Z + diagonal crowding penalty
- 骨粉 +2..5 age

A2.7.15 直接重用 A2.7.14 已測好的 CropBlock 純函式，不另寫第二套生長公式。custom component 仍用 `system.beforeEvents.startup` 註冊，不做全局 runInterval crop scan。

視覺使用 A2.7.14 已有的官方 Microsoft custom-crop-pattern 交叉幾何，只換 Java canola stage0..7 貼圖。

8 張 Java texture SHA：

- stage0 `afc9eb650ca70bece3a5f0fb08e979d64512e71c`
- stage1 `f4fa3cc14f2876aaf932dce2ebf7c4bd1a149aae`
- stage2 `18ec9e2d1e55e491c90dbeb6c20d7ed652d0474e`
- stage3 `4cb6afb9df1d62f590f7cea118f88049cbdfef0c`
- stage4 `4cb6afb9df1d62f590f7cea118f88049cbdfef0c`
- stage5 `314dcd4e949c5f610b1d07431424ec278ece5dc2`
- stage6 `314dcd4e949c5f610b1d07431424ec278ece5dc2`
- stage7 `5f7f96c41be52be77d53a2e337e7b2dbfa9f7218`

## 作物掉落

Java loot：

- 未成熟：固定 1 canola seeds
- age7：第一 pool 固定 1，再第二 pool 預設 1 並套 `binomial_with_bonus_count`
- `extra = 2`
- `probability = 0.5714286`
- enchantment = Fortune

因此成熟總數：

`2 + Binomial(Fortune + 2, 0.5714286)`

Bedrock 用兩個無條件 0.5714286 bonus pools，再加 Fortune >=1 / >=2 / >=3 各一個 bonus pool，對 vanilla Fortune 0..3 的完整分布等價。非原版 over-level Fortune >3 不宣稱完全等價。

## 下游狀態

目前 repo 已有：

- `canola_powder` item ✅
- `8 canola_powder + 1 wheat -> oil_cake` ✅
- A2.6 Oil Press / Big Vat / Canola Oil ✅

目前仍缺：

`canola_seeds -> Cookery Millstone -> canola_powder x1`

所以 A2.7.15 後：

- 第一顆 Canola Seeds 生存取得：完成
- 油菜種植/繁殖：完成
- Canola Seeds -> Powder：未完成
- 整條 Canola Oil 生存鏈：未完全閉環

下一小批應直接補 Cookery Millstone recipe，不需要再碰作物。

仍保持：

- `minecraft_tested=false`
- `bds_tested=false`
