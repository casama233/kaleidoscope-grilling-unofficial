# A2.7.52 — Cookery Stockpot Cuisine

本批補齊目前確認仍缺的三道 Java Stockpot 菜：

- `potato_beef_stew`
- `red_sweet_potato_porridge`
- `sour_spicy_noodles`

繼續復用 A2.7.50 已發布的 Cookery cuisine bridge，不新增第二套 Stockpot、不讀 Cookery 私有 `kc_station`。

## Java 1.1.1 契約

固定上游：`breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c`。

### 食物

- Potato Beef Stew：nutrition 12 / saturation 0.9 / stack 16
- Red Sweet Potato Porridge：nutrition 14 / saturation 0.071429 / stack 16
  - Flatulence 900 ticks
  - Warmth 900 ticks
- Sour Spicy Noodles：nutrition 10 / saturation 0.6 / stack 16
  - Warmth 900 ticks

### Stockpot recipes

Potato Beef Stew：

- exact：2 × beef chunks + potato + carrot dice + onion
- flex：beef chunks + potato + carrot dice + onion
- soup base：water
- carrier：bowl
- time：300

Red Sweet Potato Porridge：

- exact：3 × sweet potato + 3 × Cookery rice
- flex：sweet potato + Cookery rice
- soup base：water
- carrier：bowl
- time：300

Sour Spicy Noodles：

- Java 僅在 `kaleidoscope_tavern` 已載入時存在
- exact：vinegar + 2 × red chili + 2 × raw sweet potato sheet + leafy greens
- flex：vinegar + red chili + raw sweet potato sheet + leafy greens
- leafy greens 固定 Java tag 目前只有 `kaleidoscope_cookery:lettuce`

## 不把 Java vinegar ID 硬搬到 Bedrock

Java recipe 使用：

`kaleidoscope_tavern:vinegar`

目前 Bedrock Tavern 主幹則使用品質物品：

- `kaleidoscope_tavern:vinegar_q1`
- `...`
- `kaleidoscope_tavern:vinegar_q6`

A2.7.52 固定核對 Tavern commit：

`c9fb794eb83d7695155fba4479f8b8182dcb4687`

並把 q1～q6 作為同一 vinegar ingredient slot 的 alternatives。

同時保留 Java optional-mod 語義：

- 既有唯一 Cookery recipe publisher 使用 `ItemTypes.get()` 檢測 q1～q6；
- 六個品質 ID 全部存在才註冊兩條酸辣粉 Stockpot recipe；
- 沒有 Tavern 時 Potato Beef Stew / Porridge 仍正常註冊，酸辣粉不註冊；
- Grilling 不建立假的 `kaleidoscope_tavern:vinegar`。

## Cookery host API

固定 Cookery 1.0.6 mcaddon SHA-256：

`c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351`

驗證 public API：

- `stockpot_exact`
- `stockpot_flex`
- `normalizeStockpot(raw, flex=false)`
- `getStockpotExactRecipes()`
- `getStockpotFlexRecipes()`

A2.7.52 只擴充既有 `a2727_cookery_host_recipes_core.js`；
仍由既有唯一 `a2727_cookery_host_recipes_runtime.js` 發送 `register_recipe`。

## Cuisine bridge 復用

A2.7.50 已完成：

- Cookery Pot/Stockpot output inventory delta
- Hot Food metadata
- Special Seasoning metadata
- Stockpot Hot Food = 1200 ticks
- 不讀 host 私有 station state

本批不再修改 bridge。

Wok 與 Stockpot 的食用狀態則從：

- `WOK_EATS`
- `WOK_FOOD_SET`

收束成：

- `CUISINE_EATS`
- `CUISINE_FOOD_SET`

仍使用 main 既有同一個 `itemStartUse / itemCompleteUse / itemStopUse` 訂閱，不新增第二個完成食用 listener。

## 特殊效果

Red Sweet Potato Porridge / Sour Spicy Noodles 的效果直接追加到 A2.7.32 standalone-food effect registry：

- 不新增 effect listener
- 保留 Wedding Candy / Pepper Honey rows
- 熱食時仍能由既有 `afterCommitted` 路徑處理 Hot Food 對效果/飽和的既有邏輯

## 平台 tag 適配

Java common tags 在 Bedrock 缺乏跨 addon tag registry，因此採已存在的穩定內容 ID：

- beef chunks → `kaleidoscope_grilling:beef_chunks`
- carrot dice → `kaleidoscope_grilling:carrot_dice`
- onions → `kaleidoscope_grilling:onion`
- sweet potatoes → `kaleidoscope_grilling:sweet_potato`
- leafy greens → `kaleidoscope_cookery:lettuce`

不宣稱具備 Java common tag 的任意第三方模組廣度。

## 驗證限制

- `minecraft_tested=false`
- `bds_tested=false`
- Java recipe/tag blobs、Cookery 1.0.6 public API、Tavern q1～q6、pure core、條件 recipe 過濾、JS syntax、Dash build、compiled-output comparison 均由 CI 驗證

## 完成本批後

先前確認的 **9 個缺失 Java 獨立食品 ID** 已全部進入主幹：

- Sugared Tomato
- Pepper Honey
- Wedding Candy
- 3 × Wok dishes
- 3 × Stockpot dishes

下一步不再應以「補缺失食物 ID」為主，而應重新掃：

- Pepper Tree worldgen / village acquisition
- advancements
- remaining Java automation / optional compat
- UI/guide parity
- 實機 Minecraft/BDS gameplay 驗證

並繼續優先復用 Cookery / Tavern 已有平台能力。
