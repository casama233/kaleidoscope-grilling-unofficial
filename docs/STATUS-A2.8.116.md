# G2.8.116：餐盤營養與插串誤食修補

基於 canonical G114 與工具重整 `fb0dc3c3753bcef8d323e4a20421e636db48eadf`。
保留 Cookery1.6.0、既有 UUID、配方／份數／時間、G114瓶子資料修補及所有交易保護。
新版包／模組／配對依賴為2.8.116，guide catalog／payload為0.3.46；未引入舊餐盤視覺或QA產物。

115保留原frozen身份與所有失敗CI紀錄，未合併或部署。116新增以下來源命中相容修補，
並同步根／nested bridge的dot version與underscore輸出名；不在LIVE改檔試錯。

## 實際修補

**餐盤食用營養。** 舊路徑在增加hunger之前取得saturation，保留的G84故障記錄顯示
舊view的cap10拒絕target12.353846，導致獎勵失敗並回滾。現在在hunger寫入後重新取得
原生saturation，限制在新hunger與`effectiveMax`之內。刷新或写入失敗仍由原交易還原食物與營養，
不把未完成獎勵當成功。有效差異來源為[PR148](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/148)
`07208cd8b8a047ed3e5be9a38596054b1818dcdc`，只承接這個窄修補。

**插串不再同時啟動另一份食用。** 盤子block callback與native item-use callback各自觸發，
先後順序可能使插串後又吃掉手中剩餘串。現在於item-use拒絕原本由盤子承接的skewer使用，
包含滿盤的CONSUME路徑；保留原Java潛行副手PASS例外。來源為
[PR150](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/150)
`39e6dd145a84`及選定Java1.1.1的SkewerPlateBlock互動。

原生視線查詢只在這次item-use發生時執行，明確設定`includePassableBlocks:true`，
保留前方花／藤的輪廓命中；Java1.21.1 `Entity.pick`使用OUTLINE／Fluid.NONE，
所以未新增液體阻擋。比較plate的實際face hit與較近entity，
不會因NPC／動物後面有盘子就把其互動當成插串。查詢失敗或結果無法判定時不虛構plate命中。
沒有polling、新HUD、跨包依賴、metadata改寫或安裝時玩法覆蓋。

## 已有證據與界線

- 使用既有三個受影響檢查檔，實際production營養函式／回呼在修補前能重現故障，修補後通過。
  涵蓋新view／fixed cap、刷新與寫入故障、原交易回滾、一次結算、兩種callback次序、滿盤、
  合法air／其他block使用、潛行副手及entity遮擋。沒有新增測試套件或模擬玩家。
- 故障來源與SDK/API-double回歸不是新版本的Player原生營養或客戶端證據。
  PR148原觀察保留其版本與範圍，未重新執行其旧diagnostic overlay。
- 完整canonical CI、官方Dash與新家族static／BDS首次及重啟、fresh存檔演練、准入與部署
  由各候選實際收據記錄；不能用G114載入成功認證G115，也不會把載入成功當成完整食用聲畫。
- 必須維持`client=false`、`production_ready=false`、`pending_client_acceptance`，直到真人在同一候選操作。

原生介面參考：[EntityAttributeComponent](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entityattributecomponent?view=minecraft-bedrock-stable)、
[BlockRaycastOptions](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/blockraycastoptions?view=minecraft-bedrock-stable)、
[BlockRaycastHit](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/blockraycasthit?view=minecraft-bedrock-stable)、
[EntityRaycastHit](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entityraycasthit?view=minecraft-bedrock-stable)。
型別已對照本機釘選的`@minecraft/server2.9.0`；未因rolling docs升級API或開啟實驗。

## LIVE 對照場景

1. 主手拿3串，對空盤正常插入一次：盤內1串、手上2串；不應額外增加hunger／效果或起吃動畫。
   滿盤後再用串點它：份數維持、不額外食用。再用帶自訂lore／metadata的串重複一次，資料应保留。
2. 面向天空及普通石頭正常吃串，確認原25-tick checkpoint與完整動畫仍可用；換槽取消。
   副手普通插入與潛行例外分開觀察。把NPC／動物移到盘子前面與後面，確認實際目標不串台；再用盤前的花／藤作控制，
   對花／藤的合法使用不應被後方盤子攔截。
3. 在飢餓值低於上限時食用有熟牛肉串的餐盤，觀察盤內只少1份、飢餓與增益只結算一次；
   不應停在扣料後又還原。重新登入／正常保存重啟後確認剩餘內容與手部資料。

未承接的放置／手持餐盤完整內容投影、任意食材inventory icon、完整雙手進食聲畫與
其他Java平台差距仍在[現況表](PARITY-MATRIX.md)。本版不宣稱全部問題或一比一移植完成。
