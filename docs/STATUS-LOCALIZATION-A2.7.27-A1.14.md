# A2.7.27 + Guide A1.14 — 語言檔與指南語言整理

這一批只處理語言，不改玩法邏輯。

## Gameplay Core

三份正式 Bedrock 語言檔維持完全相同的 96 個 key：

- `zh_CN.lang`
- `zh_TW.lang`
- `en_US.lang`

簡中重新對齊 Java 1.1.1 的原作詞彙，例如：

- 綠辣椒粉：`绿辣椒粉`
- 折耳根粉：`折耳根粉`
- 不死圖騰粉：`不死图腾粉`
- 折耳根作物名稱：`折耳根`

繁中不再直接混用簡體字，並做語意本地化：

- 烤雞皮串
- 生／烤魷魚鬚串
- 生／烤馬鈴薯片串
- 番薯／番薯粉／烤番薯
- 不死圖騰粉
- 森羅物語：煙火

CI 會阻止一批已知簡體字重新混進 `zh_TW.lang`。

## Guide A1.14

指南 RP 現在也有正常的 Bedrock 語言目錄：

- `texts/languages.json`
- `texts/zh_CN.lang`
- `texts/zh_TW.lang`
- `texts/en_US.lang`

共 42 個 guide key（9 個 UI／分類文字 + 33 個條目名稱），三種語言 key 集完全一致。

Cookery 原指南切換語言時，煙火章節的：

- 章節標題
- 簡介
- 分類名稱
- 33 個條目名稱
- 返回／選擇等 UI 文字

都跟隨宿主語言選擇，不再從 Gameplay Core 的錯誤繁中值回退。

## 詳細正文的宿主限制

這一點不能假裝已修好。

固定的 Cookery 1.0.6 Guidebook Extension API v1 在 `mechanicsByLocale` 上有已驗證缺陷：

1. registry 的 token 清理會拒絕標準 locale key（`zh_CN` / `zh_TW` / `en_US`）；
2. UI 讀取時卻使用標準 locale key；
3. 而語言選擇是每個玩家獨立的，所以附屬 addon 不能靠「全域重新註冊一份不同語言 payload」安全繞過，否則多人會互相覆蓋。

因此 A1.14 做兩件事：

- 正式建立三語完整正文 catalog（33/33 條目都有 zh_CN / zh_TW / en_US），作為正常語言來源與之後宿主修復的資料；
- stock Cookery 1.0.6 runtime 仍保留繁中正文 fallback，避免註冊失敗。

換句話說：**目前宿主語言選單可以正確切換煙火章節的標題、分類與條目名稱；要讓條目內的長篇正文也按每位玩家切換，必須修 Cookery 本體的 Guidebook Extension API locale bug。這不是子 addon 能安全繞過的限制。**

本倉庫不會偷偷覆蓋 Cookery 私有腳本，也不會為了看起來「全語言成功」而做會破壞多人語言隔離的全域 hack。

## 驗證

同一條 CI 依序：

1. 驗證 A2.7.26 與 Guide A1.13 基線。
2. 套用 A2.7.27，驗證 3×96 語言 key。
3. 套用 Guide A1.14，驗證 3×42 guide key 與 33×3 正文 catalog。
4. 分別用官方 Dash v1.2.0 編譯 Gameplay Core 和 Guide。
5. 逐檔比對 source / dist。
6. 同時打包新的 Gameplay Core 與 Guide mcaddon / brproject。

仍保持 `minecraft_tested=false`、`bds_tested=false`。
