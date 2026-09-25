# A2.7.65：煙火本體內建指南

本目錄是完整煙火的唯一正式 BP／RP。玩法、模型、音效、文字與指南一起打包，不再另行安裝指南 addon。

## 玩家安裝與入口

保留森羅物語（Cookery）本體，更新煙火這一個 `.mcaddon` 即可。
煙火仍只有原來的一組 BP／RP，版本皆為 2.7.65，原 UUID 不變。
在森羅本體原有指南中開啟「森羅物語：煙火」附屬章節；不會新增另一件指南書。

上一輪誤發的 `Grilling Guide A3.0` 獨立包已停用。未安裝者不用安裝；已安裝者在世界中停用那一組獨立指南 BP／RP，避免兩個 publisher 同時註冊相同章節。不要刪除世界存檔或原煙火物品。

## 正式內容

- `behavior_pack/`：完整煙火 BP；唯一 Script API 入口是 `scripts/main.js`。
- `behavior_pack/scripts/guide/`：內建指南註冊及資料，由上述入口載入一次。
- `resource_pack/`：完整煙火 RP，含指南圖標與合併後的三語文字。
- `config.json`：完整產品的 bridge Dash 設定。

指南保留重做後的 76 個唯一條目、六個頂層分類及八個食物子分類；A3.0／0.3.0 只是內部內容版本，不代表另一個可安裝 addon。
A2.7.64 的互動、持久資料與渲染修正保留；本次改動是把原本錯拆的交付併回本體。

## 建置與檢查

```sh
python tools/build_grilling_guide.py
python tools/check_grilling_guide.py
python tools/check_grilling_release.py
python tools/build_grilling_release.py
```

指南編輯源是 `projects/grilling/guide/catalog.a3.json`；產物寫入本目錄，不寫入舊的 integration/cookery106 交付目錄。
歷史 standalone guide 及 workflow 已封存在 `history/standalone-guide-a3`，不參與正常編譯或打包。

Cookery 1.0.6 未修正的 Guide API 對 mechanicsByLocale 有既有驗證限制，正文可回退為繁中；本次不要求另裝相容 addon，也不打包或覆蓋 Cookery。本體支援的多語資料仍保留。

成品檢查要求恰好兩份 manifest、指南載入鏈與圖標全在同一產品內。靜態、Dash 及雜湊檢查不代表客戶端表單排版已驗收。
詳見 `docs/STATUS-A2.7.65.md`。
