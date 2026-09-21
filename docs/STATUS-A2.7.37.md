# A2.7.37 — Offhand Cookery Oil Pot Fill

本批只補 Java `OilFillingHandler.onRightClickItem` 的一條缺失路徑：

- 主手：Grilling 油桶
- 副手：Cookery 油壺
- 對空氣使用主手油桶

## Java 1.1.1 行為

固定 `OilFillingHandler.java` blob：

`8f9738b94ed119093f3f8552dc7e76c58fa08bc4`

原版：

1. 只處理 MAIN_HAND；
2. 主手不是三種 Grilling 油桶 → 不處理；
3. 副手不是 Cookery oil pot → 不處理；
4. 命中後取消普通 item use；
5. native Cookery fat、不同 Grilling oil、剩餘容量不足 8 → 拒絕；
6. 成功時 +8；
7. 生存主手油桶變成空桶；
8. Creative 保留油桶。

## Bedrock A2.7.36 之前的缺口

已有：

- 世界油源 → Cookery 油壺；
- Big Vat → Cookery 油壺；
- 已放置 Cookery typed oil pot → Grilling 油桶填充；
- 烤架/涼拌折耳根消耗 typed oil pot。

但沒有 Java 的「主手油桶 + 副手油壺，直接 item use」入口。

## A2.7.37

新增：

- `a2737_offhand_oil_fill_core.js`
- `a2737_offhand_oil_fill_runtime.js`

不新增第二套基建：

- 油桶 → 油種：直接讀 `a23_oil_world.js` 的 `OIL_TYPES`；
- 油壺讀寫/混油檢查：`a2734_cookery_oil_pot_adapter.js`；
- 主副手與 Creative：`a2735_player_io.js`。

runtime 不直接讀寫：

- `kc_oil_count`
- `kaleidoscope_grilling:oil_type`

也沒有重新硬編三個 Grilling 油桶 ID。

## 交易安全

在 before item-use 只先判斷是否應接管，真正修改延後到 `system.run`：

- 重新讀主手/副手；
- 再跑 adapter plan；
- 更新副手油壺；
- 生存模式將主手改為 `minecraft:bucket`；
- 寫入後重新讀回驗證 type/count 與主手桶狀態；
- 驗證失敗則嘗試回滾主手與副手。

## 驗證狀態

仍不宣稱真機測試：

- `minecraft_tested=false`
- `bds_tested=false`
