# 煙火目前缺口與待重現問題

Phase 0 稽核基準：2.8.114／`6fc3ab711e90ae9f23739b18b1f28ef5f31bbf8a`，2026-10-08。
本頁不把「缺證據」全部當作已證實程式 bug，也不把舊候選觀察沿用成現行驗收。
本輪未修任何項目，未改變現有 issue／PR 狀態。

## SKEWER-GUI：任意食材秘製串 inventory icon

**狀態：使用者有失敗觀察；現行來源缺動態 GUI 投影，当前候選仍待 client 複驗。**

重現：用未完成串手動穿三份胡蘿蔔，分別查看未完成與完成串的背包 icon。
比較其他食材及 raw/cooked／variant，確認 inventory icon 是否仍只呈現通用空串。
不要用手持 geometry 或進食模型替代 inventory 觀察。

Java 預期：GUI 依三槽實際食材、狀態與 variant 合成原作圖像。
當前三份相同食材可以完成秘製串、未完成空串可堆疊不是這個 defect。
來源與入口：[issue #166](https://github.com/casama233/kaleidoscope-grilling-unofficial/issues/166)、
[現行 GUI 邊界](CUSTOM-SKEWER-INVENTORY-RENDER-LIMITS.md)、`tools/java_custom_skewer_gui.py`。
Python 原作參考圖像存在，但沒有證明 native inventory 路由完成。
此項與固定牛肉串的靜態 icon 分開驗收。

## SEASONING-FLOW：自填瓶取回→搖勻→撒料

**狀態：舊 LIVE 候選有失敗；G114 RawMessage／材料數修補已部署，完整實際操作尚待複驗。**

重現：在一個新瓶放入 Java 必要 base 材料（green chili powder、Sichuan pepper、onion powder），
取回同一瓶，記錄材料數與 PENDING；在空氣中持續使用 80 ticks／4 秒，
確認成為 SPECIAL，然後對有一串、可調味的烤爐撒料。
全程保留同一瓶，記錄剩餘 uses、食材資料、背包／手持／放置畫面。

Java 預期：EMPTY→PENDING→80-tick held-use→SPECIAL，成功調味才消耗該瓶的 use，
不得為了讓流程成功而改配方、即時轉換或清除原材料。
來源：[issue #168](https://github.com/casama233/kaleidoscope-grilling-unofficial/issues/168)、
[PR176](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/176)、
`main.js` 的 `refreshBottleIngredientLore`／`warnMissingSeasoningBase`／取瓶與 seasoning handlers。
失敗的舊瓶如何編碼已被保留為來源回歸案例；本輪没有再做真人操作。

## PLATE-SATURATION：餐盤營養寫入使用舊飽和度界限

**狀態：舊診斷候選有原生失敗；相關修補尚未入現行 main，当前重現未執行。**

重現參數：舊 native trace 中 hunger 10→13 寫入成功後，cached saturation view 的 max仍為10，
後續寫入12.353846153846154造成 `ArgumentOutOfBoundsError`，交易退回食物與營養。
在獨立当前候選重現同一飢餓／食物與原生界限條件，觀察吃餐盤是否成功或被回滾。

Java 預期：完成食用後按食物資料加飢餓與飽和度，且只結算一次；
原生寫入失敗則完整回滾，不可吞物品、虛構 attribute max 或丟失應有增益。
main 的 `addSecretNutrition` 仍在 hunger 寫入前取得 saturation，尚未採用
[PR148](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/148) 的重新取得 live view／effectiveMax 路徑。
應從 current main 提小修補，不能合併整套過時餐盤 union；仍需受影響 C 場景。

## PLATE-USE-ARBITRATION：點餐盤時意外食用手持剩餘串

**狀態：G86 後續真人觀察記錄有此失敗；保護路由尚未入 current main。**

重現：手持多份可食用串，對餐盤進行正常插入；停止操作後觀察手持剩餘數量、hunger及延遲吃的動作。
另做空氣中合法食用、其他方塊與取消操作控制組。

Java 預期：成功餐盤互動遵守 block／item use 次序，不額外啟動獨立的 air-eating 或扣另一份食物。
current `a25_plate_recipe_runtime.js` 沒有
[PR150](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/150) 的 `skewerUseTargetsPlate` 防誤食路由。
本輪只核對來源與舊觀察，不稱当前候選已實測。

## PLATE-PLACED-DISPLAY：已放置餐盤缺完整內容投影

**狀態：來源確認相關功能未入主幹；舊原生候選有 tiny-edge-pixel／朝向問題。**

重現：餐盤插入普通熟牛肉串與秘製串，按1–5份、四朝向放置；
立即查看、取出一份、再載入區塊，記錄是否顯示完整串及原作布局。
Java 預期：顯示真實內容、對應布局與 source FIXED transform；成功交易後更新一次，失敗不改顯示。

current renderer 仍走 generic equipment／composed 路由，沒有獨立 `plate_visual_core.js`。
有效來源分散在 [PR146](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/146)、
[PR147](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/147)、
[PR149](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/149)、
[PR152](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/152)。
重新整合時保留當前 palette、ownership 和後續修補，不用舊發版 artifact 覆蓋。

## PLATE-HELD-CONTENTS／DECODE：未入主幹的手持餐盤原型

**狀態：新功能與其診斷原型，不能稱 current main 已有或已修好。**

原型重現：滿盤／單份餐盤在雙手查看，對 secret-alt、普通牛肉及 count 1／4 記錄原生顯示和已保存資料。
舊 G95 控制組記錄 stored1／4 被讀成0／3；palette 低位仍未確定。
[PR164](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/164) 的 +0.5 count 修補候選尚未完成其原生驗收。

Java 預期：手持顯示每槽實際食物與份數，不漏串、不錯解碼、不洩露其他玩家內容。
[PR153](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/153) 的子系統尚未入 current main；
#155／156／158／161／163／164 應保留在同一問題脈絡，不能孤立把公式貼到不存在的 current decoder。
也不能把 float32 數值模型當成引擎或客戶端結果。

## EATING-ACCEPTANCE：逐口、雙手、停止與離線

**狀態：驗收缺口與舊候選有限失敗；没有本輪重現的新 bug。**

場景：固定牛肉串依次測早停、24／25／26-tick checkpoint、完整90-tick FOUR profile、
換手／換槽／連吃、stop後立即leave及重新加入；觀察份數、hunger／saturation、Strength、模型去塊和音效。
以普通副手持食物、主手工具或空手的 air-use 為單獨情境。

Java 預期：25-tick readiness、release一tick grace與完整動畫長度分開；
每次只消耗／獎勵一次，取消不吞食物；副手與攝影機場景按原作行為比較。
G81 已修有完整 counter 證據的 stop→leave 分支，未知／0 counter、direct leave等仍未全面認證。
[PR145](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/145) 有有限真人進食／relog／副手記錄，
其版本不能自動認證今日 G114，亦不含完整 Java 聲畫矩陣。

## 維護風險與平台決策

| 項目 | 已知事實 | 下一步，不是本輪修補 |
| --- | --- | --- |
| 破壞性旧 build 入口 | `build.py` 删除 current gameplay_core 并写旧版本；当前release不调用它 | 隔离输出／拒绝现行baseline重建，修正文档 |
| 舊 workflow 直接寫主幹 | 兩個 localization workflow 有寫權與舊 augment；目前會被版本gate拒絕 | 歸檔／收窄觸發和權限，不假稱已覆蓋main |
| 驗證鏈重複 | 現行同一鏈重複呼叫熱食合併、seasoning storage、bottle FP 等 | 依功能合併入口，保留一次有效證據和必要邊界 |
| 效能 | 有手動 BDS profiling，尚無約定的通過預算；家族有 slowdown／記憶體警告 | 独立当前场景量測，再決定上限；不能把 logging 成功當能效已修復 |
| 真自訂流體／Numb準星／Pepper entityInside／任意 mod smoking | 有已記錄平台替代或未完成项 | 按選定API與實際場景重審，分別決定近似／等待，不永久憑舊README放棄 |

完整 PR 處置來源與范围見 [稽核表](audit/PR-TRIAGE.md)；
需要維護者選擇下一阶段優先序，本輪不將這些提案直接合併或刪除歷史證據。
