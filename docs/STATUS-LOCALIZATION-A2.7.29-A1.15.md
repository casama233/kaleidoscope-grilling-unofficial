# A2.7.29 + Guide A1.15 — 語言完整性修復

本批是在 A2.7.28 / Guide A1.14 的語言整理後再做一次嚴格檢查，專門處理殘留混字與語言檔是否完整。

## Gameplay Core A2.7.29

A2.7.28 的 zh_TW 已經清除了大部分簡體字，但發布後重新掃描仍找到 3 處「头」：

- 烤饅头片串
- 生饅头片串
- 生饅头片

A2.7.29 統一修成：

- 烤饅頭片串
- 生饅頭片串
- 生饅頭片

三份正式語言檔仍維持完全相同的 96 個 key：zh_CN、zh_TW、en_US。

CI 會掃描已知簡體殘留字，防止再次混入繁中檔。

## Guide A1.15

A1.14 已能讓 Cookery 指南的語言選單切換煙火章節的標題、分類與 33 個條目名稱，但當時標準 RP 語言檔只有 42 個 UI／名稱 key，詳細正文翻譯另外存放在 JSON catalog。

A1.15 改成正常完整語言來源。

每一份 guide 語言檔現在都有 108 個相同 key：

- 9 個 UI / 分類文字
- 33 個條目名稱
- 66 個正文行

也就是 zh_CN / zh_TW / en_US 三份 lang 都包含完整的 33 條指南正文，不再只有標題與按鈕名稱。

同時修正 A1.14 正文中幾個簡中／繁中字形混用：

- 鱈鱼 → 鳕鱼
- 鮭鱼 → 鲑鱼
- 熱帶鱼 → 热带鱼
- 馒頭片 → 馒头片
- 骨頭 → 骨头
- 面團 → 面团
- 饅头片串 → 饅頭片串

## 在原 Cookery 書中切換語言

可以確認的部分：

- 章節標題：跟隨 Cookery 語言
- 簡介：跟隨 Cookery 語言
- 分類名稱：跟隨 Cookery 語言
- 33 個條目名稱：跟隨 Cookery 語言
- 返回／選擇等 UI：跟隨 Cookery 語言
- 三語正文資料：全部存在正常 lang 語言檔，key 集完全一致

### Stock Cookery 1.0.6 仍有一個宿主 API 缺陷

Guidebook Extension API v1 的 mechanicsByLocale 驗證會拒絕標準 locale key（zh_CN / zh_TW / en_US），但 UI 讀取正文時又使用標準 locale key。

Cookery 的語言是每個玩家獨立設定，所以附屬 addon 不能用全域重新註冊另一種語言 payload 繞過，否則多人會互相覆蓋語言。

因此 A1.15 不假裝這個宿主問題不存在：

- 標題、分類、條目名稱與 UI 已能正常隨書本語言切換。
- 三種語言的正文檔案也已完整準備好。
- stock Cookery 1.0.6 仍只能讓附屬章節正文使用安全的繁中 fallback。
- 要讓長篇正文真正按每位玩家切換，需要 Cookery 本體修正 Guidebook Extension API 的 locale 驗證。

本附屬不覆寫 Cookery 私有腳本，不使用會破壞多人語言隔離的全域 hack。

## CI

CI 驗證 A2.7.28 + Guide A1.14 發布基線、Gameplay 3×96 key、Guide 3×108 key、66 個正文 key 三語完整、33×3 正文 catalog 與 lang 逐行相符，然後使用官方 Dash v1.2.0 編譯並逐檔比較。

仍保持 minecraft_tested=false、bds_tested=false，直到新構件完成遊戲內回測。
