# 煙火內建指南內容源

`catalog.a3.json` 是玩家指南唯一可編輯內容源。A3／0.3.0 是內容資料版本，不是獨立 addon 版本。

自煙火 A2.7.65 起，指南直接隨煙火既有 BP／RP 安裝，透過 `kg_a1:grilling` 註冊為森羅本體原指南的一個附屬章節。
不需要第三個指南 addon，不新增另一件實體指南書，也不覆蓋森羅本體 UI。

## 分類與條目

沿用本體的工作站、食物百科、工具與裝備、儲存與實用功能、耕作與收成、進度與指南物品六類；食物按八種製作方式分組。
76 個唯一條目涵蓋 88 個非歷史油刷 item，生熟烤串與調料瓶狀態合頁。取得、製作、用途與效果在同頁，不另拆同名配方頁。

## 正常建置

```sh
python tools/build_grilling_guide.py
python tools/build_grilling_guide.py --check
python tools/check_grilling_guide.py
python tools/build_grilling_release.py
```

輸出位置：

- `gameplay_core/behavior_pack/scripts/guide/`：資料、publisher、內建註冊。
- `gameplay_core/behavior_pack/scripts/main.js`：唯一產品入口，載入 guide/main.js 一次。
- `gameplay_core/resource_pack/textures/ui/kg_grilling/`：指南圖標。
- `gameplay_core/resource_pack/texts/`：保留玩法文字，另加入生成的指南區段。
- `docs/GUIDE-INDEX-A3.md`：分類索引。

舊的 `build_grilling_guide_release.py` 指令只作棄用相容入口，會轉交完整煙火打包，不再產生獨立指南包。

## 歷史與驗收

舊 `content.json`／`content.a2.json` 和 `history/standalone-guide-a3` 只供追溯；一次性遷移脚本不參與預設建置。
`builtin-integration.verified.json` 記錄這次整合時的來源保留與產品身份檢查。

未修正的 Cookery 1.0.6 Guide API 可使用繁中正文 fallback；這是既有 host 語言限制，不是另裝指南包的理由。本次沒有打包或改寫 Cookery。
靜態資料、序列化、Dash 與成品一致性檢查不代表實機觸控／排版驗收。詳見 `docs/STATUS-A2.7.65.md`。
