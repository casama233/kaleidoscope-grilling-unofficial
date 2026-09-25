# Cookery 指南擴充：煙火 A3.0

本目錄是實際打包的指南 BP/RP。內容來自 `projects/grilling/guide/catalog.a3.json`，不是舊的五章教學資料。

## 玩家入口

在 Cookery 原指南中選「森羅物語：煙火」。六個頂層分類沿用本體；食物百科再按八種製作方式分組。
共 76 個唯一條目，包含 19 組生熟烤串合頁、調料瓶流程合頁、77 個配方變體及實際物品圖標。
同一條目可以出現在多個適合的分類，但不是重複的操作／配方頁。

## 套件

指南 BP/RP 版本均為 0.3.0，原 UUID 保留，module ID 仍是 `kg_a1:grilling`。
指南需要既有 Cookery 本體與對應煙火 Gameplay Core；不包含這兩個本體包，不新增實體書，不修改世界存檔。
這次只更新指南；Gameplay Core 的 A2.7.64 渲染與互動修正保持不變。

Cookery 1.0.6 Guide API 的既有 locale validator 相容限制仍在；CI 沿用既有窄範圍 locale-compat host 候選，不改 host gameplay/UI，也不在 guide-only mcaddon 偷帶 host scripts。

## 建置

```sh
python tools/build_grilling_guide.py
python tools/build_grilling_guide.py --check
python tools/check_grilling_guide.py
python tools/build_grilling_guide_release.py
```

細節、未核實取得途徑、圖標來源與驗證邊界見 `docs/STATUS-GUIDE-A3.0.md`。
實際分類索引見 `docs/GUIDE-INDEX-A3.md`；包內玩家說明位於 `resource_pack/README.zh-TW.md`。
