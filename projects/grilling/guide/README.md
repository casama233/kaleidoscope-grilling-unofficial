# Grilling Guide A3.0 — 物品百科

目前唯一可編輯的玩家指南內容源是 `catalog.a3.json`。

指南沿用 Cookery 基岩本體的工作站、食物百科、工具與裝備、儲存與實用功能、耕作與收成、進度與指南物品六個頂層分類；食物按製作方式分成八組。
76 個唯一條目涵蓋 88 個非歷史油刷 item，生熟烤串與調料瓶狀態合頁。同一物品的取得、製作、操作與效果留在同頁。

## 修改與驗證

```sh
python tools/build_grilling_guide.py
python tools/build_grilling_guide.py --check
python tools/check_grilling_guide.py
python tools/build_grilling_guide_release.py
```

`build_grilling_guide.py` 只讀 A3 catalog，輸出正式 guide payload、三語文字、可追溯物品圖標與 `docs/GUIDE-INDEX-A3.md`。
`check_grilling_guide.py` 核對本體可達分類、item 覆蓋、來源配方／營養、關鍵容量與時間、圖標及傳輸上限；不以固定 5 章／52 篇的舊數字限制內容。

正式交付目錄仍是 `projects/grilling/integration/cookery106/{behavior_pack,resource_pack}`。
Module ID 保持 `kg_a1:grilling`，只出現在 Cookery 原指南的一個附屬入口；不新增實體指南書、不覆蓋本體 UI。

## 歷史與相容性

`content.json` 與 `content.a2.json` 是歷史快照，不參與正常建置。
`development/guide/rebuild_catalog_a3.py` 是來源取證／一次性遷移腳本，不能拿來覆寫日後直接編輯的 A3 catalog。
Cookery 1.0.6 的既有 locale validator 相容處理仍由窄範圍 locale-compat 候選負責；本次不改本體玩法或 UI。

詳情見 `docs/STATUS-GUIDE-A3.0.md`；分類索引見 `docs/GUIDE-INDEX-A3.md`。
靜態資料檢查、Dash 與編譯輸出比較不代表客戶端排版和觸控导航已驗收。
