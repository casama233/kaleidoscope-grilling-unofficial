# Guide A2.0 — 森羅物語：煙火完整玩家手冊

本工程只把「煙火」作為 **一個章節** 接入 Cookery 1.0.6 原有指南。

不新增第二本指南書、不新增指南物品，也不把 Cookery 原包打進本工程。

## A2.0 重做內容

舊 A1.16 是 3 分類 / 33 條靜態目錄，很多固定串頁面只重複「穿串 → 刷油 → 翻面 → 調味」，而榨油、大缸、Advanced Rack、煙火氣、作物加工與排錯都缺乏完整說明。

A2.0 改為 5 章 / 52 個主題：

- **快速上手 4**：六步烤制、烤架操作、過熟／燒焦、手工穿串。
- **設備與加工 12**：烤串盤、串譜、榨油器、大缸、高級廚具架、作物與原料加工。
- **烤串配方 20**：材料順序 + 熟串實際效果／基礎時長。
- **調料與煙火氣 9**：特製調料、三種油、Hot Food、強化材料與消耗。
- **進階與排錯 7**：烤架拒絕原因、中途拆爐、熱串整理、秘製串、普通串挑戰、涼拌折耳根、世界油。

因條目數增加到 52，`showAll=false`，避免 Cookery ActionForm 一次顯示巨大平面列表；玩家先進章節，再選主題。

## Canonical content

唯一目前內容源：

`projects/grilling/guide/content.a2.json`

生成正式 payload / 三語文字：

```sh
python tools/build_grilling_guide.py
```

檢查：

```sh
python tools/build_grilling_guide.py --check
python tools/check_grilling_guide.py
```

正式生成輸出：

- `behavior_pack/scripts/payload.js`
- `resource_pack/texts/zh_CN.lang`
- `resource_pack/texts/zh_TW.lang`
- `resource_pack/texts/en_US.lang`

A1.x 的 `projects/grilling/guide/content.json`、`development/guide/augment_a*.py` 與版本化驗證器保留作歷史重放／取證，不再是當前建置來源。

## Cookery host

仍使用 Cookery 1.0.6 已驗證的 **KC Guidebook Extension API v1**。

固定契約：

- entry id：`kg_a1:grilling`
- Cookery 指南物品：`kaleidoscope_cookery:guidebook`
- publisher revision：`a2_0_0`
- 玩家語言仍由宿主的 `kc:guidebook_language` 管理
- publisher 只發 Script Events，不直接讀玩家 inventory、world storage 或宿主私有檔案

Cookery 1.0.6 原始 Guide API 對 `mechanicsByLocale` 的 locale key 有已確認 validator 問題。Canonical Guide CI 仍會從 checksum-pinned Cookery 1.0.6 原包建立原有的窄範圍 locale-compat review artifact，只修該 validator，不改 Cookery gameplay、UUID、配方或 UI 流程。

Guide API v1 是靜態目錄；搜尋、收藏、自訂配方持久化並不是這個 API 提供的能力，A2.0 不偽造這些功能。

## 驗證

`.github/workflows/guide-canonical.yml` 會：

1. 驗證 `content.a2.json` 與生成輸出一致。
2. 驗證 5 分類 / 52 條 / 三 locale / 圖標存在。
3. 對照目前 Gameplay Core 的烤架、榨油、大缸、Hot Food、調料、Rack、固定串與熟串效果常數。
4. 檢查 Guide API v1 Script Event transfer 容量。
5. 用 checksum-pinned bridge. Dash v1.2.0 編譯。
6. source vs compiled 逐檔比較。
7. 產出 deterministic Guide A2 mcaddon 與 Cookery locale-compat review artifact。

這些檢查不等於 Minecraft/BDS 實機指南 UI 驗收。觸控排版、控制器導航、字體換行、圖標大小與真實多人環境仍需客戶端確認。

完整變更見 `docs/STATUS-GUIDE-A2.0.md`。
