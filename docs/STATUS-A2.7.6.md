# A2.7.6 — 延遲互動意圖快照 + 烤架主／副手一致性

> 本批繼續做核心實機風險收斂，不新增食材、菜品、作物或 processing recipe。  
> Java 基線：Kaleidoscope Grilling 1.1.1 @ `9a1acdab27698457bec16c9362678e574895a28c`。

## 1. 真正的競態不是「多執行緒」

Bedrock Script API 的 JS 回調本身按序執行，所以 A2.7.6 沒有添加一個沒有實際意義的 mutex。

真正問題出在：

1. `PlayerInteractWithBlockBeforeEvent` 需要在 before-event 取消原互動；
2. 真正世界／背包修改延遲到 `system.run()`；
3. A2.7.5 以前 deferred callback 重新讀 `heldMain(player)`。

因此事件發生與 callback 執行之間，玩家若切換 hotbar 或改變手中堆疊，舊版會把「原本的操作」變成另一種操作。

例：

- 空手右鍵準備翻面 → 下一 tick 前切到生串 → 可能變成插串。
- 生串右鍵 → callback 前切到油壺 → 可能走刷油。
- 打火石右鍵 → callback 前換手 → 舊版可能不再對最初互動工具處理。

## 2. A2.7.6 意圖快照

首次 block-use 事件發生時，對 Grill 記錄：

- 實際推斷的互動手：main / off
- 該手 ItemStack 的 type / amount / name / lore / primitive dynamic properties
- durability damage
- 主手操作時的 selected slot

callback 執行前再次比對。

若 stack / slot 已變：

- 不扣材料；
- 不改 grill state；
- 不把舊操作解釋成新操作；
- 顯示「互動後手持物品已改變，操作取消」。

副手 intent 不因玩家切換主手 hotbar slot 而失效，只要求副手 stack 本身仍一致。

## 3. Java InteractionHand parity

Java `GrillBlock.use(... InteractionHand hand)` 會直接取：

`player.getItemInHand(hand)`

並在同一隻手執行：

- Flint & Steel 點火／耐久；
- shovel 熄火；
- Oil Pot 刷油與扣油；
- 相容刷具；
- Special Seasoning 撒料與扣次數；
- 生串放入；
- 空手翻面動作。

A2.7.5 以前 Grill runtime 幾乎全部硬編碼 main hand。

A2.7.6 改成 hand-aware：

- `heldByHand`
- `setHand`
- `decrementHand`
- `damageHandTool`
- hand-aware Cookery oil
- hand-aware seasoning
- hand-aware insertion
- brush / season / reach 動畫選擇 `.main` / `.off`

## 4. Bedrock 沒有明確 hand 欄位的限制

stable `PlayerInteractWithBlockBeforeEvent` 有 `itemStack`，但沒有 Java 那種明確的 `InteractionHand` enum。

所以 A2.7.6 透過 event stack 與當下：

- main hand signature
- offhand signature

比對來推斷。

規則：

1. exact signature 只匹配其中一手 → 選該手；
2. exact 不成立時，用唯一 typeId 匹配兜底；
3. 空手事件：main 空則 main；否則 off 空則 off；
4. 若兩手放的是**完全等價 stack**，Bedrock 事件資料不足以可靠分辨，固定 fallback 到 main。

最後一項明確保留為平台 ambiguity，不宣稱不存在。

## 5. 插串額外 rollback

放生串流程仍是同步操作，但 A2.7.6 多加一層防禦：

- 先把 copy 放入空 slot；
- 再從已驗證的 used hand 扣 1；
- 若扣減竟然失敗，立即清掉剛插入的 slot。

因此不會因 hand 狀態異常造成「免費複製一根串」。

## 6. 不屬於本批

- Seasoning Bottle 世界方塊的副手 parity；
- entity interaction 的 hand / hold-repeat；
- 真正跨 Add-On transaction API；
- 新食材／菜品／配方；
- Minecraft / BDS 實機 PASS。

## 7. CI

A2.7.6 會完整重建 A2.0 → A2.7.5，再驗證：

- 11 個 hand/intent 純邏輯案例；
- stale main slot / stale stack 拒絕；
- offhand 不受主手 slot 切換影響；
- 所有 Grill material/tool consumption 已改為 hand-aware；
- insertion rollback 存在；
- A2.7.5 hold-repeat / 熄火 / 油順序修正保留；
- A2.7.4 Java 原 GUI icon 保留；
- A2.7.3 suspended grill helper 保留；
- 全 JS 語法；
- Dash v1.2.0；
- source / dist 逐檔一致；
- mcaddon / brproject 打包。

仍保持：

- `minecraft_tested=false`
- `bds_tested=false`
