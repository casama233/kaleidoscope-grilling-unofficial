# 家族兼容第二批：無實驗儲存後端候選 2.8.9-compat2

承接 PR #79 的公開 Cookery 1.0.8 身份、家族刀具標籤與私有庫存隔離。
沒有恢復錯誤的跨 BP `kc_station:*`、`kc_oilpot:*` 讀寫，也沒有修改第三方 BP。

## 新後端

烤爐三槽與高級廚具架九槽不再宣告需要實驗的 `minecraft:block_entity`。
每一站使用自己的持久原生 inventory 實體；保留真正 ItemStack、耐久、附魔、名稱、lore 與原生動態屬性，並非用顯示模型或 JSON 清單冒充容器。
站點 ledger、完整維度／座標、實體 ID、持久 owner token 一起校驗。只有無紀錄的新站點才能建立新容器；已有紀錄但 helper 不可讀、錯位或損壞時拒絕操作，不重新生成空容器，不補發物品。

RP 隱藏 helper；它不是可拋棄的視覺實體。禁止將它納入清理所有 helper／非玩家實體的指令。持久性不等於能抵抗管理員 `/kill` 或其他 addon 強制刪除。

`stationContainer` 被烤爐既有操作、tick、Advanced Rack 的原生表單槽位流程共同調用。
破壞與爆炸先準備掉落，成功移除站點、清空容器後才退役 helper。
Advanced Rack 裝箱仍沿用既有 payload schema；增加寫入讀回與既有編解碼欄位 round-trip 檢查，失敗不能先清除站內物品。輸出回收或回滾無法確認時鎖定 ledger，保留內容等待人工恢復，不猜測補發。

這不是宣稱所有可能的第三方物品 metadata 都能被舊版打包 codec 表達；站內原生儲存與打包 codec 的能力必須分開看。

## 不可直接遷移的舊世界

**只用於新測試世界，或已確認沒有舊實驗方塊容器資料的副本。**
關閉實驗／移除 block_entity 元件不會將原來引擎保存的槽位自動搬到新 helper。
有舊實驗容器存貨時先保持舊包及實驗設定，備份並走專門遷移；本版沒有啟用或停用任何世界實驗，也不宣稱可以自動讀出被停用元件的舊庫存。

Cookery 1.0.6 私有資料與 1.0.8 UUID 的遷移仍未做。本候選也不修正式服自訂 UUID 配置。
指南、配方、圖示、玩家動畫、Tipsy、油世界、既有物品 ID、owned header/module UUID 未更換。

## 驗證分層

`python tools/apply_family_profile.py` → `python tools/family_candidate.py --build` → `python tools/check_station_storage.py` → `node tools/check_family_knives.mjs`。
profile 是最後一道顯式 overlay，不會偷偷重跑歷史生成器；main.js delta 有前後完整雜湊，不匹配就停止，避免覆蓋後續修正。

原生測試另由 Tavern 的 batch2 harness 使用全新測試世界、真實方塊／實體／物品執行；測試副本才注入 probe，正式 runtime 不包含測試腳本。沒有玩家或模擬玩家、未驗客戶端 UI。
以原生日誌及 SUMMARY 的 actual pass 結果為準，不能用本文件替代尚未讀回的原生通過證據。
