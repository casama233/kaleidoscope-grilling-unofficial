# A2.7.62 — Runtime Split + Legacy Workflow Retirement

這批繼續按移植改善手冊的「唯一 canonical runtime / adapter 與規則分層 / 防止舊生成器回寫」原則收斂煙火移植。

## 1. Intent 規則離開 main.js

A2.7.61 已把 Grill / Seasoning 的延後互動收斂成同一種 hand intent，但 stack signature、descriptor、capture、recheck 仍寫在 `main.js`。

A2.7.62 拆成：

- `a2762_interaction_intent_core.js`：純規則，沒有 `@minecraft/server` 依賴；
- `a2762_interaction_intent_adapter.js`：只負責從玩家讀主手／副手／selected slot，再交給 core；
- `main.js`：只 import `primitiveStackProps`、`captureInteractionIntent`、`interactionIntentStillCurrent`。

因此 hand 判斷與延後快照現在可用 Node mock 單獨測試，不必啟動 Minecraft，也不需要在主玩法檔複製 API 細節。

新增測試覆蓋：

- dynamic property key 排序後 signature 穩定；
- amount / name / lore / durability 變更會使 intent 失效；
- 主手 intent 綁定 selected slot；
- 副手 intent 不受主手 selected slot 改變影響；
- deferred 期間 stack amount / property 改變會拒絕執行。

## 2. 65 條版本 workflow 正式退休

此前 `.github/workflows/` 同時存在 A2.0 ～ A2.7.60 共 65 條 `gameplay-core-a*.yml`。部分歷史 workflow 具有自動 push/pull_request trigger，甚至包含 commit/push 發布步驟。

這造成兩個風險：

1. 修改歷史 generator / verifier 時可能意外觸發過時建置；
2. 手動重跑早期 workflow 可能把舊生成結果寫回目前 canonical runtime。

A2.7.62 不刪除歷史 YAML，而是保持原 blob 不變移到：

`docs/legacy_workflows/`

GitHub 因而不再把它們註冊成 Actions workflow，但仍可逐字追溯過去建置方式。

唯一 gameplay-core workflow 現為：

`.github/workflows/gameplay-core.yml`

Canonical verifier 會 fail closed 檢查：

- `.github/workflows/` 不得重新出現 `gameplay-core-a*.yml`；
- legacy archive 必須保留 65 份歷史檔；
- canonical workflow 必須存在。

Canonical workflow 自身也改為監聽 `.github/workflows/gameplay-core*.yml`，所以有人重新塞回版本 workflow 時，這條 guard 會被觸發。

## 不改的玩法

本批不修改：

- Grill phase / 800 + 400 tick 時間；
- 4 次翻面；
- 油量與油種；
- 調料 8 ingredient / 16 uses；
- 穿串配方與秘制串公式；
- item / block identifier；
- BP/RP/module UUID；
- world dynamic-property key；
- Cookery 1.0.6 依賴。

## 驗證邊界

Node / Python / Dash / CI 仍只證明規則、語法、結構、編譯及打包鏈。

本批仍標記：

- `minecraft_tested=false`
- `bds_tested=false`
- `client_visuals_tested=false`

雪克杯、第一人稱手持、方塊模型與透明材質等 client visual 問題仍需要後續實機畫面 / Content Log 驗收。
