# Cookery 家族 API 0.2.3：可供維護者採納的修復

2026-10-02。使用者要求擴充作者 API；此回饋稿尚未傳送給作者。原作者身份及 1.0.8 版本不變，收據明列 `upstream_extended`。原包 SHA256：`9e5b617cc4c7a08ecd429fb9e42ec10e8d40a1ed5fc1f6f6687c3aff8a45a5d5`。

## 乾淨原包的問題

砧板 built-in 選擇、雞皮多輸出與未確認交付已在 [砧板回饋](COOKERY-BOARD-API-PROPOSAL.md) 重現。另以原包產生的油壺在独立 BDS 的原生箱子交換重現：作者 32 點油壺原先被煙火讀成 0；煙火 61 點 typed 油壺被作者讀成 0、放置成 256。原包兩個油壺 item 未允許副手；宿主指南優先顯示自身英文材料／製程名稱；普通出料沒有攜帶跨包的權威熱度與調味資料。這些均不能以翻譯替換整份宿主腳本處理。

## 本輪提供的介面

| 能力 | 權威／資料界線 |
| --- | --- |
| `chopping_board_v2` | 延續 0.1.0 的配方 replace/supplement、四刀後額外取料、持久結果收據 |
| portable oil v1 | 型別、點數、修訂與校驗；普通油容量 256、typed 64，8 點／桶；拒絕混油與損壞 payload |
| oil snapshots | 作者發布旧物品／放置狀態；跨包不得讀作者私有 dynamic properties，不從可見 lore 猜容量 |
| placed oil recovery | typed 放置／補充／回收保持油種與點數；不把 typed 油取成普通油脂；未確認投放隔離 |
| cuisine output v2 | 作者在實際領料、原生容器或掉落上直接寫公開熱度／調味資料；持久 operation receipt 防重領 |
| native aux projection | public food v1 選填 nativeVariant，出料及展示保留可公開驗證的資料變體；不讀作者私人模型資料 |
| ingredient behaviors v1 | 作者主動登記食物效果、原生 `usingConvertsTo`、額外容器及辣椒傷害；不偽造 itemCompleteUse |
| localized guide labels v1 | 原 renderer 與導航不變；附屬 names 及已登記製程使用當前語言 |

普通油的熱度是 1200 ticks，秘製辣椒油 12000，高級辣椒油 24000。炒鍋存檔與扣油共同讀回確認，失敗還原原壺及設備；已確認出料後通知失敗不會觸發再次獎勵。

`host-extensions/board-api.json` 登記九份原作者文件的原 hash、微型插入位置與最終 hash，以及十二個自主模組。兩個 item JSON 只新增 `minecraft:allow_off_hand: true`；assembler 拒絕其他 item 改寫、manifest 改写、漂移或身份替換。不把原作者完整腳本或 mcaddon 放入 Git。

G123 family API 0.2.10 增列 Guidebook Extension registry 的正文 locale 掛鉤。乾淨 Cookery 1.6.0 原檔錯用小寫 token 驗證，丟棄標準三語正文；自有 helper 僅在正文 locale 迴圈接受 `xx_YY`，保留通用 token 驗證。來源、重現及尚未送出的作者回報草稿見 [G123](STATUS-A2.8.123.md)。原作者提供等效修正後移除此 hook。

暫時介面審查到期日為 2026-11-02。作者提供等效且驗證過的能力時移除相應 hook；每次作者升級重新審查，不自動安裝或修改家族鎖。未知交付收據需核對原世界實際物品，不能清空隔離標記盲重試。油壺只對已確認移除且投放已確認撤回的 pending operation 提供 `retrySharedOilRecovery`；quarantined 不准自動補發。

## 驗證界線

儲存替身只驗證交易與故障回復。獨立 BDS 原生容器交換、物品資料及重啟是另一組證據；真人刷油、指南 UI、聲音、主副手／視角與生存取得不能從零玩家測試推定。任意第三方自訂食用回呼必須由該作者公開登記；本介面沒有宣稱重播所有 Java mod callbacks。原生可疑燉湯透過原生 inventory 指令建立資料變體，不用自訂同名食物偽装。

`usingConvertsTo` 在無轉換容器的原生物品上可能拋出錯誤，因此讀取此選填欄位時獨立處理缺值，不能丟棄整筆食品效果。參照 [官方 ItemFoodComponent 文件](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/itemfoodcomponent?view=minecraft-bedrock-stable)。

## A2.8.41 的變體契約

`nativeVariant` 是 0–32767 的整數，缺值保留 v1 原行為；損壞值拒絕，不推斷私人資料。實際作者可疑燉湯建立時發布該值，交付熱度／調味時保留。煙火 station projection 以 `replaceitem ... <amount> <data>` 設定並用 `hasitem` 驗證。公開自訂模型可用 `registerStationProjection(itemId, stack => ({data}))` 登記；callback 收到實際物品的 clone，helper 不擁有／交付它。這是伺服器模組接口，跨包作者需在自己公開 API 提供可共享 metadata，沒有假稱能跨命名空間讀取私人 properties。
