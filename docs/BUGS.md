# 煙火目前缺口與待重現問題

Phase 0 原始稽核基準：2.8.114／`6fc3ab711e90ae9f23739b18b1f28ef5f31bbf8a`；當前修補來源2.8.117，2026-10-08。
本頁不把「缺證據」全部當作已證實程式 bug，也不把舊候選觀察沿用成現行驗收。
G116承接餐盤營養界限與防誤食；G117修復瓶爆炸取消及手持提前結算界限。其他功能原型仍分開保留，真人驗收待完成。
現況總表見 [PARITY-MATRIX.md](PARITY-MATRIX.md)，工具變更見 [CHANGELOG](../CHANGELOG.md)。

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

## SEASONING-EXPLOSION-CANCEL：後續取消爆炸仍清除瓶與內容

**狀態：G116來源可重現；G117已在延後結算前確認取消狀態，未沿用舊候選的原生／client驗收。**

重現：放置含自訂名稱、外來metadata與材料的調料瓶，讓原生爆炸before-event先經過瓶handler，
再由較後訂閱者設 `cancel=true`，最後執行已排程工作。
G116仍把瓶變成AIR、清除native容器與兩筆保存資料，沒有掉落。

`scheduleNativeBottleExplosion`現在與既有餐盤路徑一致：延後工作只在 `cancel===false` 時繼續，
取消或讀取event失敗均保留方塊、完整ItemStack與原有ownership；既有目標／owner快照檢查保留。
原本未取消爆炸的Java毀損與不掉落行為不變。
既有 [native-storage API回歸](../development/gameplay_core/test_seasoning_native_storage.mjs)新增一項具體故障案例，
直接執行production函式並核對完整瓶資料、容器identity與保存記錄；這是B，並非BDS或真人爆炸操作證據。
此次runtime變更使用新的G117identity；完整家族准入另行記錄，不能重用G116包證據。

## PLATE-SATURATION：餐盤營養寫入使用舊飽和度界限

**狀態：G116已承接營養窄修補；production函式回歸通過，受影響Player／client待LIVE復驗。**

重現參數：舊 native trace 中 hunger 10→13 寫入成功後，cached saturation view 的 max仍為10，
後續寫入12.353846153846154造成 `ArgumentOutOfBoundsError`，交易退回食物與營養。
在獨立当前候選重現同一飢餓／食物與原生界限條件，觀察吃餐盤是否成功或被回滾。

Java 預期：完成食用後按食物資料加飢餓與飽和度，且只結算一次；
原生寫入失敗則完整回滾，不可吞物品、虛構 attribute max 或丟失應有增益。
G116 的 `addSecretNutrition` 在 hunger 寫入後重新取得 saturation，尊重 live effectiveMax；
刷新／寫入失敗仍回滾，沒有導入舊餐盤union。[修補範圍與LIVE場景](STATUS-A2.8.116.md)；
[PR148](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/148) 保留原故障與來源。

## HANDHELD-SATURATION：手持串提前結算沿用舊飽和度界限

**狀態：G116的餐盤修補沒有覆蓋這條手持路徑；G117已修正production結算，實際Player／client仍待復驗。**

重現：hunger=10、saturation=10，手持兩份熟牛肉串，在25-tick checkpoint後停止使用。
使用餐盤G116回歸已有的native captured-cap模型，舊 `hungerSettle` 先讀取cap=10的saturation view，
再將hunger提高至15並用舊view寫saturation=15，導致整筆交易退回10／10且不消耗、不給效果。
hunger=10、saturation=2的對照則可以成功，說明不是所有提前停止都失敗。

現在hunger寫入後才重取saturation component，在其即時effectiveMax內完成原配方的營養結算。
取得或寫入失敗仍回復完整食物與原hunger／saturation；不修改份數、25-tick checkpoint、
熱食倍數、一次結算、原生完整食用或既有餐盤路徑。
[實際handler回歸](../development/gameplay_core/test_eating_native_completion.mjs)涵蓋新cap、較低有效cap、
metadata保留、重複stop／complete不再扣料，以及refresh／寫入失敗回滾。
這是production函式與API模型的B；不是新的真人飢餓值或原生食用事件觀察。

## PLATE-USE-ARBITRATION：點餐盤時意外食用手持剩餘串

**狀態：G116已承接block／item-use仲裁；原生輸入次序與client仍待LIVE復驗。**

重現：手持多份可食用串，對餐盤進行正常插入；停止操作後觀察手持剩餘數量、hunger及延遲吃的動作。
另做空氣中合法食用、其他方塊與取消操作控制組。

Java 預期：成功餐盤互動遵守 block／item use 次序，不額外啟動獨立的 air-eating 或扣另一份食物。
G116 `a25_plate_recipe_runtime.js` 已承接
[PR150](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/150) 的窄防誤食路由，並核對較近entity，
保留合法air-use與潛行副手例外。實際Player／client驗收仍獨立，見[G116場景](STATUS-A2.8.116.md)。

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
| 舊 build 入口 | 重整後預設拒絕，只有全新且位於 Git 工作樹外的明確輸出可用；不再刪除既有目錄 | 已修工具；66個augment仍是歷史入口，不能當現行release鏈 |
| 舊 workflow 直接寫主幹 | 兩個 localization workflow 已移到 `docs/legacy_workflows`，Actions不再執行 | 已退出自動執行，歷史內容保留；没有證據稱它們曾覆蓋今日main |
| 驗證鏈重複 | 四組已審查重複命令在當前一次source-receipt驗證內重用成功結果 | 已去重；保留失敗／來源漂移拒絕及historical standalone行為 |
| 效能 | 有手動 BDS profiling，尚無約定的通過預算；家族有 slowdown／記憶體警告 | 独立当前场景量測，再決定上限；不能把 logging 成功當能效已修復 |
| 真自訂流體／Numb準星／Pepper entityInside／任意 mod smoking | 有已記錄平台替代或未完成项 | 按選定API與實際場景重審，分別決定近似／等待，不永久憑舊README放棄 |

完整 PR 處置來源與范围見 [稽核表](audit/PR-TRIAGE.md)；
下一階段按具體玩家問題從current main逐項修復；本輪不將這些舊提案直接合併或刪除歷史證據。
