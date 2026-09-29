# A2.8.8：Java parity Batch 1 — 秘製串契約與熱食合併

基準：Java Grilling 1.1.1 `9a1acdab27698457bec16c9362678e574895a28c`。
本批只處理可隔離驗證的秘製串／熱食資料機制，不碰世界油、Cookery 自動化、動態秘製串外觀或 Java-only 可選模組。

## 修正

- 秘製串烤熟食材不再由 `main.js` 私有 `VANILLA_SMOKED` 表直接判斷。新增 `a288_parity_contract.js`，內建原版 smoking fallback，並提供可註冊的 smoking resolver。
- 合作 Addon 可透過 stable `/scriptevent` / `SystemAfterEvents.scriptEventReceive` 註冊：
  - `kaleidoscope_grilling:register_smoking`：`{"input":"mod:raw","output":"mod:cooked"}`
  - `kaleidoscope_grilling:register_food_finish`：`{"item":"mod:food","effects":[...],"convertTo":"mod:container",...}`
- 秘製串食材 finish-use 等價層先保留既有 vanilla／煙火內建行為，再疊加合作 Addon 註冊資料；可用 `replaceEffects:true` 明確取代既有效果。註冊資料經 ID、效果、時長、倍率及機率邊界驗證。
- 玩家手動熱食合併不再限制煙火烤串。任何實際 `minecraft:food` 且仍帶煙火氣的相同物品／相同資料，都可用目前 Bedrock 的「潛行使用」替代手勢合併；時間按數量加權，且**沒有 5 分鐘限制**，對應 Java `FoodState.mergeHot()`。
- Chest／Trapped Chest／Barrel 的潛行空手整理仍保留「烤串 + 5 分鐘窗口」規則，因那條對應的是 Java OrderToCook `RefrigeratorSkewerSorter`，不是通用 `FoodState.mergeHot()`。

## 驗證

新增 `test_a288_parity.mjs` 與 `verify_a288.py`：

- 原版 smoking fallback；
- 第三方 smoking 註冊與非法 ID 拒絕；
- 第三方 finish-use 效果／容器返還／replaceEffects；
- registry snapshot 不可由呼叫方反向修改；
- 非烤串熱食可合併；
- 超過 5 分鐘熱度差仍可走手動 FoodState 合併；
- 不同自訂資料不會錯誤合併；
- canonical A2.8.7 全部既有 gate 繼續回歸。

## 仍然不是 Java 自動發現

Bedrock 1.26.51 stable 沒有 Java `RecipeManager.getRecipeFor(RecipeType.SMOKING,...)` 的等價公開查詢，也不能對任意另一個物品偽造其原生 `finishUsingItem()`。因此：

- vanilla smoking 由本包 fallback 保證；
- 第三方 Addon 必須主動註冊自己的 smoking／finish-use parity 資料；
- 未合作的任意第三方模組仍不能宣稱自動 1:1；
- 不偽造 `itemCompleteUse` 事件，避免重複扣物、重複事件與跨包副作用。

這一限制仍記在 R09／R11；A2.8.8 將其從「只能由煙火硬編碼」改善成公開、可擴展的 Bedrock parity contract，但沒有冒稱 Bedrock 擁有 Java RecipeManager。
