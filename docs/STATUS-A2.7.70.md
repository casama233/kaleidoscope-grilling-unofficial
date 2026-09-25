# A2.7.70 — 已撤回的獨立創造群組方案

**此版本對使用者需求的理解有誤，已由 A2.7.71 取代。不要以此版本的分類方案繼續開發。**

A2.7.70 曾將 90 個煙火可見項目拆成 11 個 `kaleidoscope_grilling:itemGroup.*` 自建群組，全部放在 Items 分頁。雖然引用、翻譯、隱藏狀態與建置檢查通過，但這不符合使用者要求的「附屬併入森羅系列本體既有群組」。測試通過並不代表需求做對。

## 正確方案

A2.7.71 直接檢查使用者指定的 Chinese Food 1.0.2 與 Cookery 1.0.6 公開包，以实际 catalog 為準：煙火物品使用 Equipment 分頁與本體 `kaleidoscope_cookery:itemGroup.name.*` 群組識別。

不新增煙火群組，不覆寫本體群組圖示或翻譯。詳見 `docs/STATUS-A2.7.71.md` 和 `projects/grilling/gameplay_core/reports/a2771-shared-creative-groups.json`。

本版本的 `a2770-creative-catalog.json` 留作 90 個可見項目、88 份隱藏定義及非創造資料的基線證據；不是現行分組規格。A2.7.71 仍以該基線證明沒有更改玩法、配方、貼圖、模型、UUID 或存檔鍵。
