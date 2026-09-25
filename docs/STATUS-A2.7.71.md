# A2.7.71 — 併入森羅系列既有創造群組

## 更正 A2.7.70 的方向

使用者要求的是附屬配合本體的創造分類，不是煙火另開一套。A2.7.70 的 11 個自建群組因此撤回，並移除煙火對應的群組名稱翻譯。物品／方塊本身的 identifier、顯示名稱與玩法不變。

本版直接讀取使用者指定的 Chinese Food 公開包及其 Cookery 本體，使用其真實 catalog，不從群組中文名稱推測識別碼。

## 實際參考

- Chinese Food 1.0.2：CurseForge file 8908581，https://www.curseforge.com/minecraft-bedrock/addons/kaleidoscope-chinese-food-unoffical/files/8908581
- Cookery 1.0.6：CurseForge file 8908596，https://www.curseforge.com/minecraft-bedrock/addons/kaleidoscope-cookery-unofficial/files/8908596

兩者 catalog 都使用 `equipment`。Chinese Food 的月餅模具直接追加到本體 `kaleidoscope_cookery:itemGroup.name.tools`，泡菜罈接 `cooking_stations`，食材接 `ingredients`。Chinese Food 實際共用本體 10 個群組；其特有娃娃群組不作為煙火新增群組的理由。

參考包 SHA256、catalog 雜湊與實際 metadata 保存於 `development/gameplay_core/fixtures/a2771-series-catalogs.json`。僅保存分類定義／標籤，不發布完整第三方包或其私有腳本。

## 煙火的對接

全部使用同一個 `equipment` 大分類，下表均為 **本體既有群組**，新增群組數為 **0**。群組名稱 prefix 為 `kaleidoscope_cookery:itemGroup.name.`。

| 本體既有群組 | 識別碼尾段 | 煙火追加數 | 主要內容 |
|---|---|---:|---|
| 工具 | tools | 1 | 空調料瓶 |
| 烹飪設備 | cooking_stations | 3 | 烤架、榨油機、大缸 |
| 儲存與實用工具 | storage_utility | 1 | 高級廚具架 |
| 作物與種子 | crops | 5 | 菜籽、洋蔥、紅薯、魚腥草、花椒樹苗 |
| 材料 | ingredients | 43 | 生串、加工食材、調味料、油品與榨油產物 |
| 食物 | foods | 34 | 熟串、特殊串、菜餚、點心 |
| 方塊 | other_blocks | 2 | 花椒原木與樹葉 |
| 食譜頁 | recipe_pages | 1 | 串譜 |

這個映射是將煙火內容依用途接入上述既有分類；不是宣稱 Chinese Food 本身包含煙火物品。

catalog 的 `group_identifier` 只填本體 `name`，不填圖示。群組圖示、名稱與翻譯交由本體定義。煙火只追加自己的物品清單，並將可見物品／方塊的 `menu_category` 設成一致的分類與群組。

## 已驗證的約束

- 90 個原有可見項目沒有增加、刪除、重複或遺失。
- 88 份隱藏／內部狀態定義 SHA256 不變。
- 生熟串仍按相同 19 種品種次序排列，但分別位於本體材料／食物群組。
- 所有群組識別都存在於實際 Cookery 1.0.6 catalog；不僅是出現在語言檔。
- 不覆寫本體圖示或群組翻譯，沒有 `kaleidoscope_grilling:itemGroup.*` 新群組。
- 對 Cookery、Chinese Food 與煙火三個 catalog 的六種資料合併排序檢查，不新增群組、不丟項目、不重複 ID。
- BP/RP 非創造資料摘要與 A2.7.70 前的基線一致；配方、程式、模型、貼圖、UUID、依賴及存檔鍵未改。
- 新分類資料檢查與原有 Java 對照、材質、幾何、規則回歸仍由 canonical verifier 執行。

`release:` 提交觸發正式 canonical 建置；Dash、編譯輸出比對與打包成功後才發 Prerelease。不得將本文件當成尚未讀回的 CI 成功證明。

## 實機驗收邊界

這些是來源、分類資料與建置檢查，不是 Minecraft 客戶端實测。`minecraft_tested=false`、`bds_tested=false`、`client_visuals_tested=false`。

實機需啟用 Cookery 本體與本版煙火，清空創造欄搜尋字串，再在 Equipment／裝備分頁確認煙火物品進入既有森羅群組。Chinese Food 只是對照範例，不是煙火新增依賴；不需要為這次修改額外安裝 Chinese Food。
