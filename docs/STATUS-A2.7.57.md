# A2.7.57 — P0 Official API Hardening

本批不新增玩法；在已正式發布的 A2.7.56 Event Advancement Parity 之上，對 A2.7.50/A2.7.52 的 Cookery Wok/Stockpot P0 整合做官方 API 驅動的修正。

## 已確認問題

舊版 `applyFoodMetadata()` 順序是：

1. 寫 Special Seasoning dynamic property
2. 再寫 HotFood lore / hot-until

Cookery 六道菜本身是 max-stack > 1 的普通食物。Microsoft stable Script API 對 ItemStack dynamic property 有 non-stackable/custom-item 限制，因此第一步可能在 serving 尚未 custom 化時被拒絕，而現有 catch 會讓錯誤靜默。

A2.7.57 改為：

1. `setHotFood(stack, hotTicks)`
2. HotFood 先 `setLore(...)`，把 serving 變成 custom/non-stackable
3. 再寫 hot-until dynamic property
4. 最後 `setFoodSeasonings(stack, seasoning)`

## 官方成功案例 / 契約

固定 Microsoft 官方 `minecraft-scripting-samples` commit：

`73a171fc8393a1052b4ca0669dc82231f775d8b1`

CI 會用 Git blob SHA 驗證：

- `howto-gallery/scripts/Containers.ts` — 精確 slot 使用 `Container.setItem`
- `howto-gallery/scripts/DynamicProperties.ts` — world dynamic property + JSON 結構化狀態
- `custom-components/scripts/main.ts` — item complete-use / consume custom component

另核對 Microsoft Learn stable API：

- ItemStack / ContainerSlot stackability
- WorldBeforeEvents restricted execution
- system.run 延後修改模式

## 不重造輪子

保持不變：

- Cookery 1.0.6 仍是唯一 Wok / Stockpot host
- 配方只走 Cookery public extension Script Event API
- 不讀 Cookery 私有 `kc_station:*`
- 不新增第二個 Wok/Stockpot state machine
- 仍使用 inventory before/after delta 只裝飾本次出菜
- 仍復用共享 cuisine eat path、HotFood、Special Seasoning、typed oil

## P0 regression

必須保留：

- 3 個 Wok 菜
- 3 個 Stockpot 菜
- exact + flex Stockpot recipes
- A2.7.56 的 `a2756_advancement_event_runtime.js`
- A2.7.54/55 village / fortress loot
- Pepper Tree worldgen

Java Stockpot 本身不會在每批結束後清空 `grilling$seasoning`，所以這一點不擅自改成不同語義。

Java FlexPot 目前仍無 Cookery Bedrock v1 公開 Wok-flex API，因此不以錯誤 batching 冒充 parity。

## 測試邊界

包含 source structure、固定官方 samples、全部 JS syntax、官方 Dash build / output compare、artifact checksum/integrity；仍明確保持：

- `minecraft_tested=false`
- `bds_tested=false`
