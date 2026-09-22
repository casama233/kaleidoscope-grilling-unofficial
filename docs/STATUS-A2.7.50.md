# A2.7.50 — Cookery Wok Cuisine

本批補 Java 原版三道嚴格 Pot 炒菜，**不在 Grilling 重做鍋具**，而是正式使用已驗證的 Cookery 1.0.6 public Wok extension API。

## 本批食物

| 食物 | Java nutrition | saturation | stack |
|---|---:|---:|---:|
| 折耳根炒肉 | 9 | 0.7 | 16 |
| 青椒炒魷魚鬚 | 8 | 0.6 | 16 |
| 紅燒雞翅 | 10 | 0.8 | 16 |

固定 Java 1.1.1：`9a1acdab27698457bec16c9362678e574895a28c`。

### 嚴格 Pot 配方

- 折耳根炒肉：3 × 折耳根 + 3 × 生豬肉 + 碗
- 青椒炒魷魚鬚：2 × Cookery 青辣椒 + 2 × 魷魚鬚 + 洋蔥 + 碗
- 紅燒雞翅：3 × 雞翅 + 3 × 糖 + 碗

Java recipe blobs：

- `31676dd8c13331aec31560df1028f21aeb77feef`
- `4b7a16790f96ba00e112d3ce94c1492263d703a0`
- `3a07fd7c9c9252db9134043b2438e10c46089d0c`

原圖 blobs：

- 折耳根炒肉 `12c3d37ecee6b20598265e0511e391bd39330a4f`
- 青椒炒魷魚鬚 `cd66ab879f3c1818ea2f149955945ce6e6bb22ff`
- 紅燒雞翅 `849984b12af4346a276ed1db03ee0ff70a6ef62c`

## Cookery host，不造第二套 Wok

Cookery 1.0.6 真實 mcaddon 的 public extension contract 已驗證：

- `kaleidoscope_cookery:api_ready`
- `kaleidoscope_cookery:register_recipe`
- kind `wok`
- `getWokRecipes()`
- direct station：`kaleidoscope_cookery:pot`

A2.7.50 只擴充現有：

`a2727_cookery_host_recipes_core.js`

三個 Wok row 仍由既有唯一：

`a2727_cookery_host_recipes_runtime.js`

發布。因此沒有第二個 ready listener、ping 或 recipe publisher。

### FlexPot 邊界

Java 同時有 flex_pot 版本，但 Cookery 1.0.6 public v1 API **沒有 wok_flex**。

本批只註冊 Java 嚴格 Pot recipe，不把 flex semantics 偽裝成另一個普通 Wok recipe。

## 抽出共享 Hot Food / Seasoning 狀態

主幹原本把：

- hot-until dynamic property
- hot lore
- seasoning list

私有 helper 放在 `main.js`。

如果 Cookery Wok 再寫一份就會重複造輪子。

A2.7.50 抽成：

`a2750_food_state_adapter.js`

主燒烤與 Cookery cuisine bridge 都共用：

- `readFoodSeasonings()`
- `setFoodSeasonings()`
- `setHotFood()`
- `hotUntil()`
- `isHotFood()`
- `refreshHotLore()`
- `applyFoodMetadata()`

## Cookery cuisine bridge

`a2750_cookery_cuisine_runtime.js` 不讀寫 Cookery 私有 `kc_station`。

它只：

1. 在玩家和 Cookery Pot/Stockpot 互動前保存玩家 inventory snapshot；
2. 讓 Cookery 自己處理真正 recipe/station；
3. 下一 tick 比對新產出的 serving；
4. 只對新 food output 加回 Grilling metadata。

並復用現有：

- Cookery typed oil pot adapter
- Special Seasoning 16 次使用契約
- Grilling hot-food 狀態
- 既有吃熱食的飽和 ×125% / 調料效果路徑

油熱度：

- default / canola：1200 ticks
- secret chili：12000 ticks
- premium chili：24000 ticks

沒有新增第二個 `itemCompleteUse` listener；三道菜接入 main 現有完成食用邏輯。

## 驗證限制

- `minecraft_tested=false`
- `bds_tested=false`
- 結構 / pure core / JS syntax / Java contract / Cookery package contract / Dash build / compiled-output comparison 由 CI 驗證

## 下一批

完成後剩下三道 Stockpot 菜：

- `potato_beef_stew`
- `red_sweet_potato_porridge`
- `sour_spicy_noodles`

它們可直接沿用本批 cuisine bridge，再接 Cookery `stockpot_exact` / `stockpot_flex`，不再改鍋具架構。
