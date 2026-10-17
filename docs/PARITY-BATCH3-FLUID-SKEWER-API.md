# Grilling parity batch 3 — 世界油持久化與 SkewerCompat 擴展層

基準為 parity batch 2（PR #82）。

## 世界油：移除 64 個來源硬上限

舊 A2.3 使用單一 world dynamic property：

`kaleidoscope_grilling:a23_oil_sources`

並在保存時直接 `.slice(0, 64)`。第 65 個世界油源因此無法被正式登記，這是 Java
`FluidType/BaseFlowingFluid` 不存在的額外限制。

本批改為：

- 每個 source 使用自己的 dynamic property；
- 首次載入自動讀取舊 aggregate JSON，逐源遷移後再刪除舊欄位；
- 使用 stable `World.getDynamicPropertyIds()` 恢復所有已持久化來源；
- 不再有全局 source count 上限；
- 每 tick 最多處理 8 個到期來源，來源多時只會延後更新，不會直接拒絕第 65 個；
- 垂直流動改用 `Dimension.heightRange.min`，移除固定 16 格下降上限；
- 每個來源的單次流場工作量從 160 提升至 512 cells，仍保留性能保護。

最後一點代表它依然是 **scripted fluid simulation**，不是 Java 原生 FluidType；
R17 因此仍不能標成真正 1:1。

## SkewerCompat：第三方不必再改 Grilling 本體

Java 1.1.1 的 `SkewerCompatApi` 提供：

- `skewerable_ingredients` / `unskewerable_ingredients` item tags；
- `raw_skewers` / `grilled_skewers` tags；
- ordered ingredient rules；
- custom raw-skewer cooking rules。

Bedrock 本批加入相同語義的資料層：

### 原生 item tag

- `kaleidoscope_grilling:skewerable_ingredients`
- `kaleidoscope_grilling:unskewerable_ingredients`
- `kaleidoscope_grilling:raw_skewers`
- `kaleidoscope_grilling:grilled_skewers`

### runtime 註冊

事件：

`kaleidoscope_grilling:register_skewer_compat`

例：

```js
system.sendScriptEvent('kaleidoscope_grilling:register_skewer_compat', JSON.stringify({
  ingredientRules: [
    { tag: 'example:plant_food', decision: 'allow' },
    { input: 'example:forbidden_food', decision: 'deny' }
  ],
  cooking: [
    { input: 'example:raw_skewer', output: 'example:grilled_skewer' }
  ]
}));
```

規則順序保持註冊順序；`unskewerable_ingredients` 和 Java 一樣優先拒絕。
固定 Grilling 配方食材仍保持原配方優先，不會被第三方 deny 破壞。

custom cooking 在 Bedrock contract 中是 ID→ID 的 declarative mapping，不能執行 Java
任意 `ItemStack -> ItemStack` lambda。需要更複雜資料的第三方仍應建立專用適配。

## 驗證

- 128 個 source 產生 128 個獨立 registry key，證明資料模型不再有 64 source 截斷；
- 舊 registry key 保留作 migration；
- dimension token 防止 `a:b` / `a_b` 的簡單碰撞；
- SkewerCompat 測試 allow/deny、tag 優先級、raw tag、自訂 cooking 和 bundle 註冊；
- canonical verifier 會拒絕重新出現 `MAX_SOURCES` 或 `.slice(0,MAX_SOURCES)`。
