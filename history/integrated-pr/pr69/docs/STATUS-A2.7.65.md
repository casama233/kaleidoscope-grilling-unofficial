# A2.7.65 — 指南併回煙火本體

## 問題與正確產品邊界

上一輪把 A3 指南的內容模組錯當成另一個可安裝 addon，要求玩家額外啟用指南 BP／RP。
使用者要求的是：指南属于煙火本體內容，以附屬章節出現在森羅物語（Cookery）原指南裡。
本次修正交付邊界，而不是為獨立指南包換名字。

現在安裝關係為「森羅本體＋煙火（含指南）」。完整煙火成品只有原有的一組 BP／RP，不含第三方本體，不另加指南 pack、不新增實體指南書。

## 已提交的實際修改

正式執行來源是 `projects/grilling/gameplay_core`：

- `behavior_pack/scripts/main.js` 僅新增一次 `import './guide/main.js';`，仍為唯一 Script API 入口。
- `behavior_pack/scripts/guide/{main,publisher,payload}.js` 隨本體一起載入；module ID 保持 `kg_a1:grilling`。
- RP 內含 105 張章節／分类／物品 PNG，原三語玩法文字保留，指南另放在明確的生成區段。
- 沿用 A3 內容：76 個唯一條目，六個頂層分類、八個食物子分類、77 個配方變體，生熟串與調料瓶狀態合頁。
- `catalog.a3.json` 仍是唯一可編輯指南資料；0.3.0 是內部內容版本，不再是一個獨立安裝包的版本。

煙火包與其模組版本統一為 2.7.65，UUID 不變：

- BP：`c68005c5-23ff-54e8-a3ff-da6349ad43c2`
- RP：`bbbd2d60-52e5-53a6-8b9a-c09b0f516389`

原 Cookery 1.0.6 依賴、物品／方塊 ID、持久資料鍵、配方和既有渲染內容不變。
遷移驗證確認 919 份既有非語言／非入口／非 manifest 檔案保持原位元組，三份玩法語言內容完整保留。
記錄見 `projects/grilling/guide/builtin-integration.verified.json`。

## 發布入口收斂

`tools/build_grilling_guide.py` 改為在本體內生成資料、圖標與語言區段。
`tools/build_grilling_release.py` 打包完整煙火並驗證指南在成品中；缺少指南註冊鏈、內容或圖標時會失敗。
`build_grilling_guide_release.py` 只保留棄用轉接，執行時轉交完整煙火打包，不能再生成獨立指南。

獨立指南的舊檔案與發布 workflow 保存在 `history/standalone-guide-a3`，不是有效發布來源。
原 `projects/grilling/integration/cookery106` 只留下停用說明。
正常 CI 只輸出一份完整煙火 mcaddon；不再上傳 Guide-only mcaddon 或自動製造 Cookery 替換整包。
一次性整合 workflow 完成後移除。

## 玩家更新

保留既有 Cookery 本體，只更新煙火到 A2.7.65。重新進入世界後從本體指南開啟煙火章節。
若曾安裝誤發的獨立 Grilling Guide A3.0，只在世界包清單停用那一組舊指南 BP／RP，避免重複註冊同一 module；未安裝者无需新增或處理它。
不刪除世界存檔，不重置物品或設備資料。

## 既有 host 語言限制

未修正的 Cookery 1.0.6 Guide API 對 mechanicsByLocale 的 locale token 驗證有已知限制；它會採用本資料提供的繁中 mechanics fallback。
三語標題、名稱及 per-locale 正文資料仍保留，供本體支援的欄位／修正版使用。
這次不覆蓋本體腳本，也不要求另裝一個相容 addon。這項語言限制不應被混同成額外指南包的安裝需求。

## 驗證邊界

完成的遷移檢查包括原檔保留、UUID／版本／依賴、唯一入口、來源配方／營養／圖標、208 則 Script Event 的純資料編碼與長度、JSON／JS 和渲染靜態檢查。
正式 canonical pipeline 另驗證官方 Dash 編譯、來源與編譯結果逐檔對照及成品雜湊。
成品必須恰有兩份煙火 manifest，指南三個腳本與所有圖標均在同一份 ZIP 內。
沒有執行模擬玩家互動；上述檢查不能代替客戶端章節載入、字型換行、觸控／控制器操作的實機驗收。
