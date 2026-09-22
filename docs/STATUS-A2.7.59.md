# A2.7.59 — Fireworks Feast Parity

本批只處理 Java `Fireworks Feast / 煙火全席`，不新增第二套進食監聽、成就儲存或輪詢器。

## Java 原版契約

固定上游：

`breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c`

Java `ModAdvancements.recordFoodFinished()` 會在成功吃完食物後：

1. 僅接受 Grilling namespace 的食物。
2. 若食物屬於固定的 `FEAST_FOODS` 集合，就寫入玩家 persistent data：
   `kaleidoscope_grilling:advancement_foods`。
3. 去重保存已吃過的食物。
4. 29 種全部吃過後，解鎖 `fireworks_feast`。

Advancement contract：

- parent: `eat_it_hot`
- frame: `challenge`
- XP: 100
- hidden: false
- show_toast: true
- announce_to_chat: true

## 29 種食物

包含：

- 19 種固定熟烤串
- Ordinary Skewer
- Cold Houttuynia
- Sugared Tomato
- Pepper Honey
- 3 種 Wok 菜
- 3 種 Stockpot 菜

與 Java 一致，`secret_skewer` **不屬於** Fireworks Feast 集合。

## Bedrock 實作

不新增 `itemCompleteUse` listener。

直接復用現有唯一成功進食收束點：

`main.js -> afterCommitted(player, id, ...)`

順序保持與 Java `recordFoodFinished()` 一致：

- Eat It Hot
- Mental Preparation Failed
- Fireworks Feast progress

新增：

- `a2759_fireworks_feast_core.js`
- `a2759_fireworks_feast_runtime.js`

進度仍存在玩家 dynamic property：

`kaleidoscope_grilling:advancement_foods`

內容使用 JSON array；讀取器同時兼容 Java-style comma string，以便資料遷移。

最終獎勵完全復用 A2.7.53：

`awardOneShotAdvancement(player, FIREWORKS_FEAST)`

所以：

- 不重複 XP 系統
- 不重複 announce
- 不重複 completion property
- 不新增 progression store

## Microsoft 官方成功案例

固定：

`microsoft/minecraft-scripting-samples@73a171fc8393a1052b4ca0669dc82231f775d8b1`

檔案：

`editor-multi/scripts/goto-mark.ts`

固定 Git blob：

`833e034c9e04dd920680f4287a66efb008a81449`

官方 sample 對 player entity 直接使用：

`player.setDynamicProperty(key, JSON.stringify(structuredState))`

並用 `getDynamicProperty()` 讀回，與本批的玩家持久化集合模式相同。

## 不重複造輪子

- 新 listener：0
- 新 interval：0
- 新 progression store：0
- 新 food-consume path：0
- Cookery Wok / Stockpot host：不變
- A2.7.57 HotFood/seasoning hardening：保留
- A2.7.58 challenge advancement runtime：保留

## 下一步剩餘 advancement

Fireworks Feast 完成後，Java advancement 剩下主要是每 20 ticks inventory/dimension check 類：

- Human Fireworks
- Better Write It Down
- A Handful of Canola
- Strength Makes Oil
- Sweet Potato
- Nether Taste

這 6 個不應直接照 Java 粗暴加一個新的 20-tick 全背包輪詢器；下一批應先找 Bedrock 官方 inventory / acquisition / dimension event 能否精確覆蓋，只有必要部分才共享掃描。

## 驗證邊界

CI 會驗證：

- pinned Java ModAdvancements / advancement / lang blobs
- pinned Microsoft player dynamic-property sample
- 29 種食物集合逐項一致
- pure progress core
- 唯一 `afterCommitted()` hook
- 新 listener / interval = 0
- A2.7.58 / A2.7.57 / loot / worldgen regression
- 全 JS syntax
- checksum-pinned Dash build
- compiled-output compare
- packaged artifact integrity

仍明確：

- `native_java_advancement_tree=false`
- `native_java_toast=false`
- `minecraft_tested=false`
- `bds_tested=false`
