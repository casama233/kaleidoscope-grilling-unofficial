# A2.8.39：按 Java 原作修正提示與進食 HUD

本輪依使用者最後指示，以 Java 1.1.1 的實際行為為準；不是全面關閉原作提示。原作 JAR SHA256：`cf31071e4ba790bcd5c1d3f6005439bc512acba084e70b8ab6a767e8c8f99dd6`。核對 `GrillBlock`、`OilPressBlock/BlockEntity`、`BigVatBlock`、`SeasoningBottleBlock`、`SkewerRecipeBookItem`、`HudControl`、`SkewerEatingHud` 與 `SkewerGuiIconCache`。

| 部分 | 來源修正 |
| --- | --- |
| 烤架 | 按原作事件送出刷油成功／缺油、撒料失敗／完成、未點火、等待刷油／撒料、成功翻面次數；冷卻與任意物品提醒保持安靜 |
| 榨油器／大缸 | 互動時顯示原作容量／油餅／進度／批量與容器失敗訊息；壓擊訊息在實際撞擊提交後送出，不輪詢顯示 |
| 調料與串譜 | 原作瓶滿、無效調料、基料不足及缺少食材翻譯鍵／參數；缺料名稱由客戶端翻譯 |
| 進食 | 54 份 GUI 圖片逐檔來自同一 JAR；102×5 圖形條，25 tick 由黃轉綠，16×16 食物圖標、原作灰色與透明度；史萊姆／神秘串四 tick／五幀圖標 |
| 日常提示 | 舊自創文字出口與 ASCII 進食出口保留為無輸出的相容函式；不送停止／完成的空 actionbar |
| API 與資料故障 | 保留 A2.8.38 的操作、回復與安全拒絕；移植 API 同步提示及交易診斷改記錄於 Content Log，不新增原作沒有的玩家訊息 |

進食傳輸只含格式碼，由本包獨立 JSON UI factory 顯示原作圖片。停用後私有圖片在 75 ms 內到期，不清除其他包的共用 actionbar。保留現有酒館及 `!js.` 圖形封包過濾條件；這不是已經驗收的跨包 HUD 仲裁。

[Microsoft RawMessage](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/rawmessage?view=minecraft-bedrock-stable) 支援翻譯鍵、字串與巢狀翻譯參數；此處沒有把原作互動內容改寫成新的數字摘要。

## 尚未完全等價

- 原作 `/kg hud on` 開啟的右側機器／調料／油壺面板仍未移植；目前維持原作的預設關閉。Jade 擴充的選用資訊不能視為預設 actionbar。
- 秘製／第三方自訂烤串的動態合成 GUI 圖標尚未完整移植，目前使用原作 fallback 圖片。普通串與固定／失敗串使用原圖標。
- 真人畫面上的位置、UI 比例、F1／觸控、停止時序、網路延遲與其他包的 actionbar 競爭仍需驗收。BDS 不會渲染此 UI，載入通過不能寫成畫面已通過。
- 保留原作互動訊息不等於所有機制已等價；調料基料拒絕、跨包接口及生存互動仍按差距矩陣追蹤。

本版承接已合併 A2.8.38 的油／食物 API、內容顯示、Java 曲線及龍血修復；不覆蓋那輪工作。[差距矩陣](PARITY-REPAIR-MATRIX.md)保持未完成項目。

本輪的本地 38 候選與另一輪已合併的 A2.8.38 同時形成，已撤回本地候選並承接 main 的不可變歷史，改為新的 A2.8.39。不得以 38 的 BDS 結果替代新版載入證據。

[最終 39 候選 BDS 證據](BDS-JAVA-HUD-20261002.json)：16 包原檔逐檔比對，首次與重啟均通過，沒有腳本／HUD 錯誤。每次 25 則 warning 已核對為 19 個收據登記的物品覆蓋、5 行空測試 allowlist 提醒及 1 個酒館初始化訊息，沒有以更新 hash 消除告警。先前的 38 候選證據保留供審查，沒有套用到正式世界。
