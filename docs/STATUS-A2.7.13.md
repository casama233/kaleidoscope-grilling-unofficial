# A2.7.13 — 折耳根基礎物品 + 砧板加工

> Java 基線：Kaleidoscope Grilling 1.1.1 @ `9a1acdab27698457bec16c9362678e574895a28c`。  
> Cookery Bedrock：1.0.6，公開包 SHA-256 `c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351`。

## 本批完成

- `kaleidoscope_grilling:houttuynia` 正式 Bedrock item
- `kaleidoscope_grilling:minced_houttuynia` 正式 Bedrock item
- Cookery Chopping Board：`houttuynia -> minced_houttuynia ×1 / 4 cuts`
- A2.7.10 → A2.7.12 回歸與 Cookery extension contract

本批不做 crop/worldgen，也不覆寫 Nether Fortress 原版箱子 loot table。

## Java 配方

Java recipe：

`kaleidoscope_grilling:chopping_board/minced_houttuynia`

- ingredient tag: `#kaleidoscope_grilling:ingredients/houttuynia`
- cut_count: **4**
- model_id: `kaleidoscope_grilling:houttuynia`
- result: `kaleidoscope_grilling:minced_houttuynia ×1`

鎖定 Java 1.1.1 中，該 tag 實際只有一個值：

`kaleidoscope_grilling:houttuynia`

因此 Bedrock Extension Recipe API 使用單一 item input，對這個鎖定基線是精確集合等價，不是縮窄一個多值 tag。

## Houttuynia item

Java 是 `ItemNameBlockItem`：

- stack 64
- nutrition = 2
- saturation modifier = 0.2
- 同時可作為 `houttuynia_crop` 的種植 item

A2.7.13 先對齊食物/ingredient 部分：

- stack 64
- nutrition 2
- saturation_modifier 0.2
- 普通 1.6 秒 eat use
- 可副手使用

目前 **沒有** `minecraft:block_placer`，因為正式 crop block 尚未進 gameplay pack。等作物批次加入 crop 時再把同一 item 接上種植，不用新增第二個種子物品。

Java 原 texture Git blob SHA-1：`40afc94ae7826ddb7cb5a8cd106434a6745dfe25`。

## Minced Houttuynia

Java 是普通 ingredient item：

- stack 64
- 非食物
- 無 callback / effect

Java 原 texture Git blob SHA-1：`c6653c730bb5d1fefab02db05388b0f2e6aefc30`。

## Cookery API

A2.7.13 繼續重用 A2.7.8 的單次 startup `api_ping`，自己只訂閱 `api_ready`。

只有 `api=1` 且 capability 包含 `chopping_board` 時才註冊 recipe。CI 也會對 checksum-pinned Cookery 1.0.6 確認它沒有內建 `kaleidoscope_grilling:houttuynia` board recipe；如果未來 built-in 出現，contract gate 會失敗。

## 為什麼本批不做 Nether Fortress 箱子

Java `FortressHouttuyniaHandler` 是在 `chests/nether_bridge` 載入時**增量 addPool**：

- rolls = 1..2
- pool chance = 65%
- 每次成功 roll 給 houttuynia 1..3

Bedrock stable 2.9.0 現有 LootTable/LootPool script 介面可以讀取/生成 loot，但 pools / entries 是 read-only；沒有 Java `LootTableLoadEvent.addPool(...)` 那種安全增量 mutation。

直接提供同路徑 `loot_tables/chests/nether_bridge.json` 會變成整張 vanilla table override，對其他 Add-On 與未來 Minecraft 更新都太侵入，所以本批明確不採用。

## Java 生存取得仍未完整

Java 還有另一條世界取得：新生成 Nether Fortress chunk 裡，fortress bounds 內約 **25% Nether Wart** 依座標 hash 被替換為紅色變體 Houttuynia Crop；wart age 0/1/2 對應 crop age 0/3/7。

這個和 `houttuynia_crop` 本身一起留給下一個 crop/worldgen slice。

所以 A2.7.13：

- 物品本體：完成
- 砧板加工：完成
- 生存世界取得：**未完成**
- staged chopping-board Java model：**未 1:1**

## 下游

A2.4 已有：

- `slime_ball + houttuynia + slime_ball -> raw_slime_skewer`
- `raw_sweet_potato_sheet + minced_houttuynia + minced_houttuynia -> raw_sweet_potato_sheet_skewer`

這批先讓兩種 ingredient 與加工關係落地；等 Houttuynia crop/world acquisition 完成後，這兩條固定串才真正恢復生存可達。

仍保持：

- `minecraft_tested=false`
- `bds_tested=false`
- `survival_houttuynia_acquisition_complete=false`
