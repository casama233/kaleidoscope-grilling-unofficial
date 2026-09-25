# Guide A3.0 — 按森羅物語基岩本體重做圖鑑

## 這次重做的是什麼

遊戲內煙火指南從 A2.0 的 5 個教學章節、52 個主題，改成按物品查找的百科。
仍註冊在 Cookery 既有指南的 `kg_a1:grilling` 入口；不新增實體指南書，不覆蓋本體 UI。
指南包版本是 0.3.0；Gameplay Core 仍是 A2.7.64，本次不改其玩法或渲染。

## 本體依據

實際讀取 Cookery 1.0.6 的 `scripts/events/guidebook.js`、指南語言模組及 `scripts/api/guidebookExtensionRegistry.js`，不是照 Java 百科猜分類。
本體指南 UI 檔 SHA-256：`acff33eec87add1c149aff3789b1b9ec62dd1ef642a5bc7d2b2f1b70dd6332ff`。
原始 host archive SHA-256：`c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351`。

沿用本體六個有內容的頂層分類及其繁中、簡中、英文名稱：

| 頂層分類 | 煙火內容 |
| --- | --- |
| 工作站 | 燒烤架、榨油器 |
| 食物百科 | 按製作方式分組的食物與材料 |
| 工具與裝備 | 調料瓶與特製調料、Cookery 油壺的煙火用法 |
| 儲存與實用功能 | 高級廚具架、烤串盤、大缸、油桶與油壺 |
| 耕作與收成 | 油菜、折耳根、洋蔥、番薯、花椒、油渣與花椒樹 |
| 進度與指南物品 | 串譜、首次燒烤流程、煙火氣與活動喜糖 |

本體另有家具分類；煙火本批沒有對應家具條目，因此不製造空分類。
食物百科依本體「按製作方式」的做法，設燒烤架、手工穿串、炒鍋、湯鍋、合成與加熱、砧板加工、磨石加工、食材與其他食物，共 8 個子分類。
完整清單由 `docs/GUIDE-INDEX-A3.md` 自動生成。

## 同物品合頁，而不是再堆一層選單

- 76 個唯一條目，涵蓋目前 88 個非歷史油刷的 canonical item，以及相關公開設備與兩個流程頁。
- 19 組生串／熟串合成同一食物頁。頁內有生熟營養比較、穿串材料與順序、燒烤操作、熟食效果及必要警告。
- 空調料瓶、半成品調料、特製調料合成一個工具流程頁。
- 同一串可從「手工穿串」和「燒烤架」找到，但指向同一 entry ID；不是兩份同名的操作頁／配方頁。
- 配方不是只有散文：向本體提交 77 個 recipe variant，讓本體展示材料、產物、產量、製作方法與已有時間。
- 四個工作台有序配方保留文字九宮格和材料代號說明，不錯寫成任意擺放的材料清單。
- 程式化取得的烤串盤與串譜直接說明操作，不憑空新增工作台配方。
- 隱藏三個歷史油刷；油的正常使用以目前 Cookery 油壺適配為準。

## 圖標及語言

69 張條目／分類用物品或植物圖標按實際 BP icon → RP atlas → PNG 解析與複製，來源與 SHA-256 記在 `catalog.a3.json`。
公開設備使用既有設備預覽圖；不把 UV 展開圖冒充物品圖標，也不把整類材料都畫成烤架。
繁中、簡中、英文條目資料齊全。少數自訂製作方法採短雙語標籤，因 host v1 不提供任意 method 的逐語言欄位。
本體 UI 中既有的英文數量後綴等文字仍由本體控制；本批沒有宣稱改寫所有 host UI 字串。

## 不用指南掩蓋取得途徑缺口

目前核對資料仍無法確認燒烤架、龍蛋粉、青辣椒粉、折耳根粉、不死圖騰粉、熔岩辣椒油桶的生存首份取得路徑，六项在圖鑑中明示「未核實」，不把原作配方寫成已實裝。
調料瓶合頁另外明示初始空瓶取得仍未核實。
酸辣粉的醋需要酒館對應物品；缺少依賴時配方不註冊。喜糖保留程式中限定的活動日期，不包裝成全年合成食品。
這些是目前被檢查來源能支持的邊界，不宣稱已找遍所有第三方整合包。

## 內容與發布路徑

唯一可編輯內容源：`projects/grilling/guide/catalog.a3.json`。
正常建置：`python tools/build_grilling_guide.py`。
驗證：`python tools/build_grilling_guide.py --check` 和 `python tools/check_grilling_guide.py`。
打包：`python tools/build_grilling_guide_release.py`。

A2 的 `content.a2.json` 留作來源追溯；`development/guide/rebuild_catalog_a3.py` 是一次性遷移證據，不是預設建置入口。
遷移實際讀取 checksum-pinned host，產生 readable catalog、payload、三語文字和圖標後提交；一次性自動提交 workflow 已移除。

指南 BP UUID `f8c367c2-84d6-5bf6-b5a8-1bbe6cdb93ab`、RP UUID `32baef08-6b04-5115-9d5b-2d4ba2d3a7b4` 均保留。
本次交付是指南 BP/RP 升級，不是只重新導入 Gameplay Core 就會改變的內容。

## 已做的檢查與尚未驗收

來源／資料檢查確認唯一 ID、可達父子分類、88 個 item 覆蓋、20 組固定串資料、15 組 Cookery 精確加工註冊、37 個靜態食物營養、真實圖標來源及關鍵容量／時間常數。
資料本身保留替代材料組合與順序；營養不把互動用的 nutrition=0 或秘製串動態營養錯當成固定值。

每條 mechanics 不超過 host 的 512 UTF-16 單位、每頁不超過 8 條，配方與分類均在 host 上限內。
Script Event 純序列化檢查輸出 208 則訊息，最長 1638 字元，沒有超過 2048 長度限制。
這是對純資料函式的讀取與編碼檢查，不包含模擬玩家互動。

最終 CI 另做官方 Dash 編譯、來源／編譯結果逐檔比較與 deterministic mcaddon 校验。
這些不能代替 Minecraft 客戶端的觸控排版、字型換行、控制器導航或實際表單觀感；仍需遊戲內驗收。

原版 Cookery 1.0.6 的 Guide API locale validator 相容問題沒有被本次分類重做改寫：沿用已有的窄範圍 locale-compat host 流程。Guide-only mcaddon 不包含或偷偷覆蓋整份 Cookery。
