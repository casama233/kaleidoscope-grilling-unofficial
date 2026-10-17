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

## 13. A2.7.65/A2.7.66 測試版的三處回歸（2026-09-25 伺服器側已修，建議上游修正）

A2.7.65-test 與 A2.7.66-test 相對 A2.7.64 出現三處回歸，均在正式服內修復並驗證：

1. **調料瓶放置腳本崩溃（致命）**：`main.js` 使用 `world.beforeEvents.playerPlaceBlock`（穩定版 API 無此事件），`main.js:572` 拋出 `cannot read property 'subscribe' of undefined`，整個腳本未載入、全部玩法失效。修法同伺服器版既有模式：改為 `system.beforeEvents.startup` 註冊 `senluo:grilling_bottle_place` 方塊自訂元件，並在 5 個 `seasoning_bottle*.json` 補上元件聲明。
2. **`ambient_occlusion` 型別回歸**：`skewer_recipe.json`、`pepper_sapling.json`、`pepper_leaves.json`、`sweet_potato_crop.json` 等重新出現布林值 `false`（本版 schema 僅接受數值），觸發 `invalid numeric value` / `invalid string`。已全包規範化為浮點數。
3. **`tag:minecraft:crop` 回歸**：`canola_crop.json`、`onion_crop.json`、`houttuynia_crop.json`、`sweet_potato_crop.json` 重新帶上本版 schema 不支援的 `tag:minecraft:crop` 元件（A2.7.14 伺服器版已移除過一次）。

另：`All MaterialInstances must use the same render_method` 警告（26 條）**不是包缺陷**——隔離實驗證明同一組包在另一世界為 0 條，僅在生產世界（level.dat 開啟 `experimental_creator_cameras`／`voxel_shapes`／`y_2026_drop_3` 三個實驗）出現，屬實驗模式下引擎的更嚴格驗證提示，不影響載入。

## 14. A2.8.0 整合測試版（2026-09-25 部署）

`A2.8.0-test.115.1` 已部署（2.8.1）。伺服器側處理清單：

- 相依改接（同前）；8 個配方缺 unlock → 其中 2 個為熔爐配方（本就免 unlock），實際補 0；AO 布林 10 檔、`tag:minecraft:crop` 4 檔、`playerPlaceBlock` 調料瓶放置——三類回歸仍在，已按既有流程修復（§13）。
- **新回歸**：新增的 `a2770_placed_oil.json`／`a2770_placed_seasoning.json` 實體使用 `"deals_damage": false`（布林），本版 schema 僅接受字串，已改為 `"no"`。
- 上游已自行吸收：RP `capabilities:["pbr"]`（VV 聲明）、配方 unlock 主體、胡椒樹世界生成。

三包（煙火 2.8.1／酒館 0.6.44／世界名酒 0.1.7）部署後 Content Log **0 錯誤**。

## 15. 創造分類「裝備」頁分組失效（2026-09-25 晚間事件與修復）

現象：創造選單「裝備」類中，廚房系的可摺疊分組（刀具／鍋具／冰櫃等）失效成逐件散列。

根因：世界包堆疊被重排後，廚房（定義分組圖標的一方）降到位於煙火／世界名酒之下；而煙火與世界名酒的 `crafting_item_catalog.json` 向廚房既有分組**追加時只寫 `name` 不寫 `icon`**。同名合併時，較高優先級的無圖標定義覆蓋了廚房的帶圖標定義，分組失去圖標後無法以可摺疊組呈現。

修復（伺服器側）：為煙火 8 個、世界名酒 4 個 name-only 分組定義補上與廚房／酒館一致的 `icon`（煙火 BP 2.8.1→2.8.2、世界名酒 BP 0.1.7→0.1.8），使合併結果與堆疊順序無關。

**建議上游**：`crafting_item_catalog.json` 中向既有分組追加的條目請一併帶上 `icon`（值可與本體一致），避免部署環境的堆疊順序影響分組渲染。
