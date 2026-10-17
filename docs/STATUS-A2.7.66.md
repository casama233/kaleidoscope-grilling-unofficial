# A2.7.66 — Seasoning State Completion

## 修復範圍

本批接續 `1743ee615e59939085208ac09131b569a3fe6136`，保留 A2.7.65 的 39 個烤串 attachable／150 個手持 geometry。這些模型仍未收到 Minecraft 實機驗收，本批不把它們標成已驗收。

該基線已將特製調料瓶 visual state 接入玩法，但只包含 42 種物品／attachable；runtime 可產生 8 個剩餘量分級 × 8 個變體，共 64 種。缺少 22 種會讓部分搖勻、使用或取回流程嘗試建立不存在的 ItemStack。

A2.7.66 補齊 22 種缺少的定義，讓 0–15 次已使用量 × 0–7 變體的 128 組有效輸入，都能解析至實際存在的物品、模型、貼圖與 render controller。

## Java 依據與外觀

固定參照 `breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c`。`SeasoningData` 定義 16 次使用與 8 個變體。Java `seasoning_special_states` 模型定義剩餘量與 spice_fill 的 UV 色塊。

新增狀態重用同剩餘量的既有 v0 geometry；將原有 32×32 `seasoning_bottle.png` 中 v5／v6／v7 的色塊原樣複製至 v0 填充 UV 區域，形成三張 palette 貼圖。瓶身、標籤、透明材質、手部 binding、填充高度與裁切 UV 不变，不新增猜測的偏移，不複製 Cookery 資源。

這補齊的是手持調料瓶狀態。放置後四瓶堆疊仍沿用既有靜態世界模型，不能宣稱放置外觀已與 Java 完全等價。

## 資料與交易安全

`retargetSpecialSeasoningStack` 保留配料、使用次數、變體、自訂名稱、原始多語 lore、dynamic properties、死亡保留／鎖定與冒險模式限制。任一必要資料複製失敗便不輸出半成品；來源物品不被修改。

Cookery 調味改成先建立扣次數後的瓶子，再提交手持槽位與鍋具狀態。任一提交失敗會嘗試回復兩者；回滾失敗另外記錄 Content Log，不假報成功。`system.run` 延後期間改變槽位或手持資料時取消操作，保留 Java 主手調味語義。創造模式不扣使用次數，最後一次仍回傳空瓶。

現有 UUID、world dynamic-property key、配方、烤製數值、Cookery 1.0.6 依賴保持不變。

## 驗證

新增 `verify_a2766.py` 與 `test_a2766_runtime.mjs`。測試載入實際 runtime/core 模組，以模擬 Minecraft API 進行 15 項測試，包括 128 組狀態解析、逐次使用、資料保留、最後一次、創造模式、缺物品／寫入失敗、兩方回滾、換槽和配料改變。資源檢查逐一核對 64 種物品、fill 高度與 UV、三張 palette SHA256，並保留 39／150 烤串回歸檢查。

Canonical CI 仍跑既有 input／intent／transaction 測試、固定 Java contract、JavaScript 語法、Visual Reference Gate、Dash 與 source/dist 精確比對；通過後使用 `release:` 提交發布 prerelease。

## 實機驗收與尚未修復

建議在備份的測試世界中做：加入配料並搖勻 → 取得不同變體 → 手持／放置再取回 → Cookery 主手調味直至第 16 次 → 確認空瓶、配料與剩餘量。快速切換槽位不應把新物品當成舊瓶使用。

`minecraft_tested=false`、`bds_tested=false`、`client_visuals_tested=false`。上述 Node 測試不等於真實背包／引擎驗收。Typed Oil Pot 世界外觀、MAXIM tooltip、放置瓶動態外觀與其餘 parity 差異不在本批完成範圍。
