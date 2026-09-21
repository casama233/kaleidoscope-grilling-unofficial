# Guide A1.16 — Cookery 1.0.6 每玩家正文語言相容

本批只處理「森羅物語：煙火」附屬章節的長篇正文語言切換，不新增第二本書、不修改 Grilling gameplay。

## 已確認的 Cookery 1.0.6 宿主問題

固定來源為 Kaleidoscope Cookery (Unofficial) v1.0.6，原始 mcaddon SHA-256：

c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351

宿主對一般 locale map 已正確接受標準代碼，例如 zh_CN、zh_TW、en_US；但 Guidebook Extension API v1 在 mechanicsByLocale 上錯用了只允許小寫 token 的 cleanToken。

因此標準 locale 在註冊時被丟掉，而 guide UI 後面其實已經有正確的每玩家查找：

entry.mechanicsByLocale[guidebookLocaleCode(player)] || entry.mechanics

Cookery 的語言設定本身也是每玩家 dynamic property：kc:guidebook_language。

所以問題不在 UI 或語言儲存，而是 registry 的一行 locale 驗證。

## 最小宿主相容修復

相容包只改一個原始檔：scripts/api/guidebookExtensionRegistry.js。

只把 mechanicsByLocale 的 locale 驗證從 generic cleanToken 改為與宿主 locale map 相同的標準 xx_YY 格式。

不放寬 generic cleanToken，避免影響分類、revision、source 等其他安全驗證。

除此之外：

- Cookery gameplay 不變。
- recipes 不變。
- UUID / manifest version 不變。
- guide UI 不變。
- 每玩家語言 dynamic property 不變。
- 所有原資產不變。
- 額外加入一份相容修補說明文件。

輸出：Kaleidoscope_Cookery_v1.0.6_Grilling_Guide_Locale_Compat.mcaddon。

它應取代 stock Cookery 1.0.6 使用，不能與同 UUID 的原包同時啟用。

## Grilling Guide A1.16

A1.15 已有完整三語正文。A1.16 把 33 個 entry 全部正式送出 mechanicsByLocale：zh_CN、zh_TW、en_US。

仍保留 zh_TW mechanics 作為 stock 1.0.6 fallback。

搭配相容宿主後，Cookery 原本的 guide UI 會直接依目前玩家的 kc:guidebook_language 讀取正文，因此多人可各自使用不同語言，不需要全域切換、不會互相覆蓋。

## 驗證

CI 會驗證已發布 Guide A1.15，產生 A1.16 的 33×3 mechanicsByLocale，下載 SHA 鎖定的 Cookery 1.0.6，證明 stock registry 的錯誤，並保證只修改 registry 一個原始檔。之後驗證 Cookery UI 仍使用每玩家語言屬性，模擬 zh_CN / zh_TW / en_US 三種正文選擇，再用官方 Dash v1.2.0 編譯 Guide A1.16 並逐檔比較。

minecraft_tested 與 bds_tested 仍維持 false，直到新組合完成遊戲內多人實測。
