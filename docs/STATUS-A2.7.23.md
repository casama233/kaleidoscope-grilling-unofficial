# A2.7.23 — 創造欄整理與內部狀態物品隱藏

本批只處理使用者截圖中最明確、可由 Java 1.1.1 原始碼直接核對的創造欄問題，不混入手持模型與指南 UI 修復。

## Java 來源核對

基準仍是 `breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c`。
Java `ModCreativeTabs` 建立獨立的「森罗物语：烟火 / Kaleidoscope Grilling」創造分頁，並明確排除：

- `unfinished_skewer`
- `secret_skewer`
- `pending_seasoning`
- `skewer_plate`
- 三種 oil brush
- 尚有 Tavern 條件內容／未移植內容（本批不虛構）

因此截圖裡直接看到「未完成烤串」「待搖調料」並不是 Java 原作的創造欄行為。

## Bedrock 對應

Bedrock 不能新增 Java 式頂層 CreativeModeTab，所以採官方 `item_catalog/crafting_item_catalog.json`：

- 在「物品」分類末尾建立一個可折疊自訂群組。
- 群組名稱沿用 Java：簡中「森罗物语：烟火」、繁中「森羅物語：煙火」、英文「Kaleidoscope Grilling」。
- 群組圖標使用燒烤架。
- 依 Java `ModCreativeTabs` 的順序排列目前 Bedrock 已存在且可用靜態內容：設備 → 串譜／調料／油 → 生串 → 熟串 → 特殊串 → 其餘材料與食物。
- 目前缺失的 `advanced_rack` 等 Java 內容不放假物品佔位。

內部過渡物品改成 `menu_category.category = "none"`，仍保留註冊 ID 給腳本建立與除錯指令使用，不從創造欄直接暴露。

## 語言修正

把過渡狀態名稱與 Java 1.1.1 對齊：

- `pending_seasoning`：簡中「待摇晃的调料」、繁中「待搖晃的調料」、英文「Seasoning to Be Shaken」。
- `secret_skewer`：簡中「秘制烤串」、繁中「秘製烤串」、英文「Secret Mix Skewer」。

## 驗收邊界

CI 會驗證 JSON、隱藏清單、76 個 catalog 條目、語言鍵及 Dash 編譯輸出一致性。
本環境沒有 Minecraft 客戶端/BDS，因此「創造欄折疊群組實際顯示、觸控展開、與 Cookery 疊包時排序」仍必須實機驗收，不能把靜態驗證當成畫面已通過。

下一小批應處理所有烤串 attachable 的第一／第三人稱手持基準與位置。
