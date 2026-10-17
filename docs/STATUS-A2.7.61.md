# A2.7.61 — Interaction Safety + Canonical Build Gate

這批依照《森羅物語移植改善手冊：酒館經驗 → 煙火適用》的方法，先處理兩個會讓後續修復反覆失效的基礎問題：**自訂方塊互動的 hand/intent 一致性**，以及**真正會監聽 canonical BP/RP 的建置驗證入口**。不改烤製時間、配方、油量、調料容量、物品／方塊 ID 或持久化 key。

## Java 規格依據

固定 Java 參考：`breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c`。

- `SeasoningBottleBlock.use(..., InteractionHand hand, ...)` 直接以 `player.getItemInHand(hand)` 讀取操作手；空手取回也用 `player.setItemInHand(hand, result)`。
- `GrillBlock.use(..., InteractionHand hand, ...)` 同樣把點火、油壺、調味和 replacement 綁到實際操作 hand。
- `SkeweringHandler` 的 Java 主流程是單一 `RightClickItem` handler；Bedrock stable 缺少完全等價的 generic use-button callback，因此對不可原生 use 的食材仍保留 block/entity fallback，但這些 callback 只負責導入同一個穿串 executor。

CI 以 Git blob 固定上述三份 Java 檔案，避免日後上游變更悄悄改掉本批依據。

## 互動修正

A2.7.60 只有 Grill 在 `system.run` 延後執行前保存 hand intent；Seasoning Bottle 仍：

- 硬編碼讀主手；
- 硬編碼扣主手；
- 空手取瓶固定寫回主手；
- 延後執行後不重新確認玩家是否已切槽／換物品。

A2.7.61 收斂為同一條 custom-block dispatch：

1. block before-event 只判斷目標與是否應攔截；
2. Grill／Seasoning 都捕獲同一種 hand + stack signature intent；
3. `system.run` 後先重新核對 intent；
4. 再由 `handleCustomBlockInteraction` 唯一分派到 Grill 或 Seasoning；
5. Seasoning 的讀取、扣料、取回都使用實際 `hand`。

這不新增玩法，只修正 Java 已有的主／副手語義與延後執行安全性。

## Canonical build / CI

新增非版本號綁死的入口：

- `development/gameplay_core/verify_current.py`
- `development/gameplay_core/package_current.py`
- `.github/workflows/gameplay-core.yml`

新的 workflow 直接監聽 `projects/grilling/gameplay_core/**`。因此之後直接修改 `main.js`、BP/RP JSON、模型或 manifest，不會再出現「真正 source 變了但最新版本 workflow 沒被觸發」的盲區。

`verify_current.py` 會：

- 驗證 BP/RP UUID 與 module UUID 沒被重編；
- 驗證 BP/RP 版本與依賴一致；
- 驗證 script entry 和所有相對 JS import 都存在；
- 按 manifest 版本分派到該版本的 release verifier；
- 未註冊的新版本直接 fail closed；
- Dash 編譯後要求來源與 dist **檔案集合完全一致**，除了逐檔內容相同，也不允許多出舊檔。

`package_current.py` 從 Dash 真實編譯輸出製作 review `.mcaddon`，固定 ZIP timestamp、排序並輸出 SHA256，讓相同來源可重現打包。

歷史 `gameplay-core-aXX.yml` 保留作追溯，不再作新改動的 canonical 入口。

## 驗證邊界

本批 CI 能支持：JSON 可解析、JavaScript 語法、純規則測試、Java pinned contract、Dash 編譯結果逐檔等價、review artifact ZIP 完整性與雜湊。

它**不能**證明 Android／Windows 客戶端的手持模型、HUD、透明材質或動畫，也不能把 mock/static 測試當成真實 Minecraft 操作。因此報告仍標記：

- `minecraft_tested=false`
- `bds_tested=false`
- `client_visuals_tested=false`
