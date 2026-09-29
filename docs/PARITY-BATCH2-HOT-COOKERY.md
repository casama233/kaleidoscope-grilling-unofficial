# Grilling parity batch 2 — 通用熱食合併與 Cookery 權威輸出

基準為 parity batch 1（PR #81）。

## 1. 手動熱食合併不再只認煙火烤串

Java `FoodState.canMergeHot/mergeHot` 的核心條件不是「是不是烤串」，而是：

- 忽略 `HotUntil`、模型變體與作者欄位後，其餘 ItemStack 元資料一致；
- 兩邊同為熱食或同為冷食；
- 熱食合併後按數量加權剩餘熱度。

Bedrock 現在保留 OrderToCook/箱桶用的 `compactSkewerContainer`，但玩家的
「副手空＋潛行使用手中熱食」改走 `compactMatchingHotFood`：

- 原版食物、自家料理、第三方具有 `minecraft:food` 的食物都可參與；
- Secret Skewer 這種動態食物仍以 skewer fallback 參與；
- 只合併與手中樣本完整 merge signature 相同、而且同為熱食的堆；
- 不套 5 分鐘 Normal Sort 視窗，對應 Java 的手動 merge；5 分鐘規則仍只屬
  Refrigerator/目前箱桶替代的 Normal Sort。

Bedrock stable 沒有 Java inventory screen 的 CapsLock + slot-click mixin，因此手勢
仍是平台適配，不把 UI 輸入方式宣稱為 1:1。

## 2. Cookery output 不再只有玩家背包差量一條路

Java 1.1.1 直接在 Pot/Stockpot BlockEntity 的 result 上寫入 heat/seasoning，因此
hopper/automation 等非玩家取出仍保有資料。舊 Bedrock bridge 只能比較玩家互動前後
背包差量，R16 因此一直不能關閉。

本批加入：

`kaleidoscope_grilling:cookery_output_ready`

Host/Cookery 腳本在**已確定輸出目標後**送出 JSON：

```json
{
  "version": 1,
  "station": {
    "dimensionId": "minecraft:overworld",
    "x": 10, "y": 64, "z": 20
  },
  "target": {
    "kind": "block_slot",
    "dimensionId": "minecraft:overworld",
    "x": 11, "y": 64, "z": 20,
    "slot": 0,
    "expectedId": "example:meal",
    "expectedAmount": 1
  }
}
```

`target.kind` 也可為 `player_slot`，此時提供 `playerId`、`slot`、
`expectedId`、`expectedAmount`。

安全條件：

- live station 必須仍是 Cookery pot/stockpot；
- target 的 ID **和完整數量**必須完全符合；不把已存在舊堆的一部分誤標成熱食；
- 只有原生 `minecraft:food` 物品會被改寫；
- 成功後才消耗/更新該 station 的 Grilling seasoning/oil 狀態。

因此 automation 可以提供**明確的容器槽**，不再靠「附近看到掉落物就猜來源」。
沒有 host 事件的舊 Cookery 仍保留現有玩家背包差量 fallback。

### Java 數值修正

Java `PotBlockEntityMixin.takeOutProduct` 即使沒有 typed oil，也會給輸出 60 秒
煙火氣。舊 Bedrock `metadataPlan('pot', {oilType:''})` 是 0；本批改成：

- default / canola：1200 ticks
- secret chili：12000 ticks
- premium chili：24000 ticks
- stockpot：1200 ticks

## 驗證

新增兩個 regression：

- `test_hot_food_manual_merge.mjs`：非烤串 vanilla/第三方食物、熱/冷隔離、
  數量加權熱度及非食物拒絕；
- `test_cookery_output_contract_core.mjs`：player/block target schema、嚴格目標
  比對及 Java Pot/Stockpot 熱度數值。

這批仍不聲稱能在不修改 Cookery host 的情況下攔截所有非玩家輸出；stable Script
API 沒有 Java Mixin 那種跨模組 BlockEntity result 注入點。權威事件是後續 Cookery
host/自動化適配要使用的正式接口。
