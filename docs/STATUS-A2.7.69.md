# A2.7.69 — Food Tooltip + Oil Pot Transaction Safety

基於 `09d6b6d596e021326b2cb20299c23f3d3c950d0b`（A2.7.68）接續修復，保留剛合入的靈動視效 PBR 宣告與匯出防回退檢查。39 個烤串／150 個手持 geometry 已在 A2.7.65 全量接入，64 種手持調料狀態已在 A2.7.66 補齊；本批保留它們，不將這些既有成果重算為新增工作，也不宣稱已收到實機驗收。

## 料理格言（MAXIM）

補上八個已有翻譯鍵、但尚未在物品提示中接入的食品：白糖番茄、花椒蜂蜜、魚腥草炒肉、青椒魷魚須、紅燒雞翅、土豆燉牛肉、紅薯粥與酸辣粉。實際物品名稱隨既有語言資源顯示。

沿用固定 Java `FoodTooltip.appendMaxim` 的 DARK_GRAY／ITALIC 樣式，使用 RawMessage 翻譯鍵而不是把中文／英文寫死進背包。Java 參照為 `breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c`。本批不改原有翻譯文案。

Cookery 產出經既有 `applyFoodMetadata` 路徑寫入格言；背包變動、玩家加入及腳本載入會合併進同一個更新佇列，每次最多處理四位玩家。沒有每 tick 掃描所有背包。更新讀取即時槽位並操作 clone；寫入失敗保留原物品。重複更新不疊加格言；已有 20 行自訂 lore 時不刪除使用者內容來騰空間。箱子內的舊物品在進入玩家背包後才更新。

熱食 metadata adapter 改讀 `getRawLore()`，避免熱度刷新／冷卻時把多語格言及其他 addon 的 RawMessage 攤平成字串。原有熱度時間、配料與營養規則不變。

## 油壺資料與提交安全

修復三條實際程式路徑：

1. `buildCookeryOilPot` 原本忽略資料寫入失敗，仍回傳可能缺少油種／數量的物品。現在保留既有 raw lore，先建立自訂 lore 再寫入油量，讀回核對；失敗不回傳半成品。
2. 放置油壺的灌油原本延後執行卻沒有重驗輸入。現在保存 hand intent、槽位、物品 signature、油種／數量及方塊 permutation 快照。期間換槽、換手持、換維度或容器變動便取消；寫入／扣桶失敗則嘗試回復兩方。
3. 破壞／爆炸原本先清除油量，後續失敗可能丟失內容。現在先準備完整掉落物，再清理／移除／產生掉落物；失敗回復方塊與儲存鍵。回復失敗會記錄 Content Log，不假報成功。讀取失敗不當成空油壺。

沿用 Cookery 方塊／物品、64 點類型油容量、8 點桶量、256 原生油脂容量與所有既有 dynamic-property key。沒有新增替代油壺方塊或覆寫 Cookery 私有資源。原有原生放置後的延後 metadata bridge 仍保留，不能由本批推論其所有跨 addon 競態均已解決。

## 驗證與範圍

`verify_a2769.py` 檢查八種食品的三語翻譯鍵、實際 runtime 入口、快照／回復接線、A2.7.67 材質及配方修復、A2.7.65/A2.7.66 資源回歸，以及對固定基線的逐檔 Git blob 比對。除明列的四支 runtime、兩份 manifest 與兩個新模組，其餘 BP/RP 位元組必須不變。

另有 10 項純 lore 資料測試，包含八種映射、冪等、RawMessage 保存、使用者內容、重複格言、20 行限制及熱度行辨識。保留八項 PBR／匯出資料測試，以及既有純 input／intent／transaction 測試、固定 Java 契約、JS 語法、Visual Reference Gate、Dash 與 source/dist 精確比對。沒有執行模擬玩家互動測試。

## 仍未完成／需實機驗收

`minecraft_tested=false`、`bds_tested=false`、`client_visuals_tested=false`。

本批不是 Typed Oil Pot 放置色彩或放置調料瓶動態模型修復；這兩項仍未完成。格言使用 Bedrock lore 呈現，不是原生 Java hover 方法。油壺回復路徑、不同玩家語言、堆疊／熱食刷新與裝有其他 addon 的效果，需要在備份測試世界驗收。核心確認流程：取得上述食品 → 查看提示／變更客戶端語言 → 烹調加熱並等冷卻 → 油桶灌入 → 快速換槽 → 破壞並重新放置核對油種／數量。
