# G123：Cookery 指南正文的標準語言鍵

Cookery 1.6.0 的原 Guidebook Extension registry 接收分類、條目和三語名稱，但將 `mechanicsByLocale` 的 `zh_CN`、`zh_TW`、`en_US` 交給僅允許小寫 token 的 `cleanToken`，三語正文因此被丟棄。完整家族的實際接收檢查首先在酒館木桶頁發現此缺陷；227 條目／31 分類的接收數不代表正文完整。

核對原作者 [Cookery 發布頁](https://www.curseforge.com/minecraft-bedrock/addons/kaleidoscope-cookery-unofficial) 的 1.6.0 原包（file 9054164，archive SHA256 `da12fe6d39d7514aff1de3c963d69899324d771be5ca0fc3da1ccb759c7ad458`），未套用歷史料理替換。`scripts/api/guidebookExtensionRegistry.js` 原檔 SHA256 為 `664964a32be1038d3bc9be3d9e0fb460d77b65aa20f2c78d5efb9d12099dbf07`。原檔第 109 行以 `cleanToken(locale)` 驗證正文語言；同檔 `normalizeLocaleMap` 已使用 `xx_YY` 格式處理 names／text。

G123 在現有 `host_api/guide_labels_core.js` 自主編寫 `publicGuideLocale`，修剪空白後只接受 `/^[a-z]{2}_[A-Z]{2}$/`。既有 `board-api.json` 增列這一原檔的原 hash、import、單一插入及套用後 hash；只在正文 locale 迴圈內將 `cleanToken` 指向該 helper。原通用函式、分類、source、revision、身份與其他 author scripts 均保留。公開來源不包含原作者完整 registry／原包；assembler 仍按已審查的原檔及最終 hash 准入。

包／模組及自有相依為 2.8.123，指南資料版本 0.3.53，登記 family API 0.2.10。G122 的炒鍋、品質、施肥所有權及既有指南橋接不變；原 Cookery 1.6.0 UUID 和 API 相依不變。

`tools/check_cookery160_host.py` 從上述乾淨原包讀取實際 registry，以 begin／chunk／end 註冊同一最小三語條目：原檔保留 names、丟棄全部標準正文語言，套用後逐語保留正文並拒絕格式錯誤的語言鍵。大小寫不合法的分類、source、revision 仍拒絕。此為資料接收與故障重現，不使用模擬玩家，不宣稱客戶端呈現。

此段即原作者問題回報草稿：重現輸入、來源版本／hash、原因與最小介面修法均已備齊，尚未透過外部留言送達作者。已核對作者 [Loyallay](https://www.curseforge.com/members/loyallay/projects) 與官方說明連結的 [Discord](https://discord.gg/ay5mqVuXdN)；[Cookery 留言頁](https://www.curseforge.com/minecraft-bedrock/addons/kaleidoscope-cookery-unofficial/comments) 需要登入。本機沒有已登入的發送渠道，不宣稱已回報、作者已同意或作者已有修正。

作者修正標準正文語言鍵後，移除此局部掛鉤並以乾淨新版重做同一回歸；每次作者更新重新審查，現行介面審查到期日為 2026-11-02。

PR 必要檢查及完整家族 static／BDS／實際 Cookery 接收／存檔演練另記於當前家族收據。真人 client 驗收與 Java 一比一仍未由本回歸證明。
