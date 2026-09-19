# Kaleidoscope Grilling — unofficial Bedrock port

煙火（Grilling）的非官方 Minecraft 基岩版移植工程。

## 專案狀態

本倉庫已確認為正確目的地：`casama233/kaleidoscope-grilling-unofficial`，GitHub repository ID `1377218440`。

**這是開發中工程，不是完整可遊玩的附加包。歷史素材工程尚未全量入庫。**

本批匯入範圍：先前 A1.13 Recovery 交付中的玩家筆記資料核心與測試（`notebook/`）。它支援有順序的自訂配方、收藏、搜尋、版本／容量檢查與玩家儲存適配器；測試使用模擬玩家，不能當成 Minecraft 世界持久儲存或指南 UI 驗收。

```sh
node notebook/test.mjs
```

仍待入庫的歷史內容包括 A1.12 累積素材工程、指南章節測試專案、來源快照、模型／貼圖、轉換工具與審查資料。請勿將本批少量源碼匯入解讀為全部歷史成果已上傳。

## 固定方向

- 指南整合到森羅物語原指南，維持一個煙火入口，不另新增指南書。
- 素材先做來源核對與多角度驗證；未經遊戲測試的材質、姿態、動畫不標成完成。
- 不提交使用者上傳的完整 Cookery 安裝包、第三方私有腳本、世界、憑證或機器環境資料。
- 來源素材與我方工具分開標明授權及出處；本倉庫沒有取得整個原模組的重新授權。

匯入來源與已知限制見 `docs/MIGRATION_STATUS.md`。
