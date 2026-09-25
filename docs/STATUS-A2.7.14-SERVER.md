# 伺服器差異清單 — A2.7.67 修正狀態

更新：2026-09-25。此路徑原先累積 A2.7.14–A2.7.66 的部署紀錄；完整舊文已[原樣歸檔](history/STATUS-A2.7.14-SERVER-before-A2.7.67.md)，blob `6b942d166651578d8298ec033cb57b5f4d95fe5d`。原有證據與限制沒有刪除，以下只更新本次實際完成的事項。

## 目前來源與發版範圍

A2.7.67 的窄範圍修正 PR #71 已合入正在產生 A2.7.66 測試包的 `refactor/canonical-runtime-interactions-20260924`，提交 `96fd50ceefe07fed20f689520a9737fd19e83b31`；發版標記提交 `4d02ce29331968fae73dd7c32841ac962c4ffbb5`。較大的 PR #70 仍待審核，**本次沒有將它整批合進 main；main 的 runtime 不因此冒充已升級 A2.7.67**。

詳見 [PR #71](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/71) 與 [A2.7.67 server status](https://github.com/casama233/kaleidoscope-grilling-unofficial/blob/4d02ce29331968fae73dd7c32841ac962c4ffbb5/docs/STATUS-A2.7.67-SERVER.md)。

## 已修正

**原 §11／§12 的八份配方缺 unlock**：油壓機、高級置物架、花椒原木轉木板、大缸、秘製辣椒油、花椒蜂蜜、油餅、糖拌番茄，全部補上以原料為條件的 unlock。配方形狀、材料、數量及成品未改，熔爐配方不額外加 unlock。

**原 §5 的 MaterialInstances 警告已有具體來源**：A2.7.66 大缸六份宣告材質表內，外殼 alpha_test 與液體 blend 混用；本次統一為 blend，保留透明液體與原始素材。此處更正舊文「未發現同一方塊混用」的中間判斷，但不宣稱歷史 26 條警告都已逐條歸因或實機消失。

新增靜態 gate 已核對 23 個方塊、133 組材質配置、72 個 block_placer 與全部工作台配方；扣除已授權資料修正後，1,239 個非 manifest runtime 檔案與原 A2.7.66 正規化內容一致。正常 CI 已通過實際 Dash 編譯與 source/dist 核對。

## 仍需保留的部署適配與未解項目

私服 Cookery UUID 改接是該伺服器的部署需求，不是公開包應寫死的 UUID。ItemStack 中介資料、支撐判斷、before-event 延後、油流未載入保留與指南等舊 server-edition adapter 本輪未移除，也沒有宣稱已全數吸收進公開 runtime。`tools/build_server_edition.py` 的用途不變；使用新輸入仍需按實際部署驗收，不能套用歷史 BDS 通過紀錄。

三筆調料瓶 block_placer 警告的目标是存在的 `seasoning_bottle_1`，目前多個物品狀態共用該方塊，沒有刪除其放置路線。舊隔離世界中的酒館桌／吧檯重啟遺失也尚未在固定包組合重現，不改寫或清空使用者世界。

新增 `Block  couldn't be found in the registry` 日誌沒有方塊 ID／來源路徑，仍未歸因。本包靜態 block_placer 檢查沒有空值或不存在的本包目標；這不能排除跨包、引擎版本或世界載入問題。

魔法輪盤紫黑缺圖另有酒館自身 title 通道干擾：Tavern PR #87／0.6.42 已撤掉 title 資料傳輸與閒置 `ktmix:off`，改用有限生命週期的獨立 actionbar 圖形。不等於已證明所有 A Magic Way 圖片問題的原因；沒有改寫 A Magic Way、UI Queue 或 Novelty API。

## 驗證邊界

本輪沒有啟動 Minecraft 客戶端、BDS 或模擬玩家互動測試。材料／引用／資料校驗、CI、真實 Dash build 與上傳成品比對，不能代替 Android 透明排序、魔法輪盤或重啟持久化實機驗收。下一次回報請保留第一條錯誤前後的 Content Log、實際包版本與載入順序。
