# A1.12 — 使用真正 Cookery 1.0.6 的單一指南入口

## 本次可用檔案與測試方法

`Grilling_Guide_Cookery106_A1.12.mcaddon`只包含我們自己的指南BP和縮圖RP，不包含Cookery、完整煙火玩法、任何新增書本、物品或方塊。是供遊戲內驗收的開發測試包，不是已通過Minecraft測試的成品。

先複製一個測試世界並啟用原本的Cookery 1.0.6 BP/RP，再匯入指南mcaddon並啟用它自己的BP/RP。退出世界後重新進入，用原本的森羅物語指南找「煙火 · 素材預覽」；英文設定下是「Grilling · asset preview」。指南語言由Cookery設定管理。

應只多一個入口。章節內有開始／範圍、設備、油菜、20組固定串參考配方、6項調料參考、尚未實作的自訂配方記錄說明。配方不是可合成的承諾，沒有假保存按鈕。其他Cookery章節不應消失。關閉／返回交由原書處理。

沒有出現入口時，先確認兩個指南包均啟用，並提供內容日誌中`[Grilling guide]`和`Guidebook extension`附近的錯誤；不要刪世界或修改Cookery腳本。移除此測試BP/RP後重新載入世界，本次章節便不應再註冊。註冊不持久寫入世界。

## 真正查到的宿主協議

原始包SHA-256：`c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351`。

BP：`10f37ae2-9ccf-435f-b34b-0eec8191cd94`；RP：`c89dc8df-c3fc-4bc8-8bd0-527abba76681`；兩者版本[1,0,6]。
指南物品：`kaleidoscope_cookery:guidebook`。

來源位置（全部位於原包BP）：
- `documentation/KC_GUIDEBOOK_EXTENSION_API.md`
- `scripts/api/guidebookExtensionRegistry.js`
- `scripts/events/guidebook.js`
- `items/guidebook.json`及`manifest.json`

逐檔SHA及大小在`guide/host-contract.verified.json`，全包唯讀掃描在`reports/cookery106-static-scan.json`。舊pending檔已改為指向verified的索引；真正舊未綁定fixture保留在`guide/history/a111/`。

宿主公開Guidebook Extension API v1，用`kaleidoscope_cookery:guidebook_ready`、`guidebook_ping`、`guidebook_begin`、`guidebook_chunk`、`guidebook_end`協作。begin/end帶api/source/id/revision；chunk為source、id、revision、index、片段的換行分隔字串。宿主接受1–512片，未完成片段在600tick後清理。

我們以1600字ASCII片段發布，22條總訊息、最長1638bytes，每tick最多8條。非ASCII字元先JSON Unicode轉義，避免字符數／UTF-8長度歧義。重複註冊以同一`kg_a1:grilling`取代自身，不覆蓋其他ID；有限ping和錯誤重試，缺宿主時不生成替代書。沒有ACK，傳送完成只代表本端送完。

本指南API的作者文件說明無需manifest依賴宿主，因此測試BP只依賴自己的RP及`@minecraft/server`2.7.0（與實包一致）。這不是說未來完整Grilling玩法不需要Cookery前置。

## 已重現的宿主限制

1.0.6的`mechanicsByLocale`經`cleanToken`過濾，拒絕標準locale裡的大寫地區碼；UI卻用標準locale去讀。因此本章採繁中＋英文的`mechanics`欄位。`text`與`names`仍使用宿主的正確locale路徑，中文／英文名稱已測試。zh_CN目前使用繁中回退，其餘語言英語回退。

原生靜態章節沒有提供自訂回調供我們接搜尋、收藏或玩家配方存檔。A1.11原型保留作需求參考，不再把它當成宿主已支援的功能。原生子頁取消回上層，首頁取消關閉，不攔截去強迫改寫。

食材映射只確認10個直接Cookery ID在上傳檔案內存在；Java標籤／原版ID沒有亂猜。參考配方用mechanics保留位置顺序與OR選項，避免宿主食譜顯示把食材合併計數後失去穿串順序。沒有真正向加工設備註冊配方。

## 原始宿主程式測試

執行：`python tools/test_cookery106.py "Kaleidoscope Cookery v1.0.6.mcaddon"`。需要Python與Node.js，不需要網路。工具驗證原包雜湊，僅在臨時目錄提取JS，測後清理；修改過或別版本包必須重新核查，不能直接冒用相同契約。

31項測試直接載入原始註冊器、原始指南及其locale／data依賴，共36份未修改宿主JS。Node VM中只模擬Minecraft tick、ScriptEvent、玩家和表單傳輸。驗證全33條目、單一入口、原分類保留、所有頁面可達、兩玩家語言互不影響、取消／返回、重註冊、遺失／亂序／過期片段及重試，並逐檔與ZIP原始SHA對照。

第二個擴充只用合成fixture測試，沒有真正Chinese Food包，不宣稱二者已實機相容。`guide/cookery106-host-trace.html`只展示原始宿主輸出的文字／按鈕記錄，UI外框為我方離線查看器，不是Minecraft截圖。

## 仍需遊戲驗收

MC客戶端／BDS實際匯入，RP載入與縮圖、觸控及控制器，Cookery單獨＋指南、Cookery＋真正Chinese Food＋指南，斷線與重進，缺宿主提示，移除測試包後入口消失。自訂配方保存／命名／重開和完整煙火玩法尚未完成。
