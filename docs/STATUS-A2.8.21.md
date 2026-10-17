# A2.8.21 — 原生調料瓶儲存與生命週期

## 實際改進
- 放置及最多四瓶堆疊採用原生 ItemStack clone/容器，完整物品是權威資料。原 kind/ingredients/uses/variant 列只供模型與介面讀取，兩者不一致就停止操作。
- 取瓶、加料及玩家破壞保留原有名稱、說明及自訂資料。依 Java，只有 EMPTY 補齊基礎三料或取出具備基礎三料的 EMPTY 時建立新的 PENDING；原本 PENDING 不被降級。
- Java 的玩家破壞包含創造模式掉出所有瓶；支撐消失回傳 AIR，爆炸沒有調料瓶 loot。後兩者不套用玩家破壞掉落，並清理原生容器及索引。爆炸掉落結論來自 Java 類別與資源審查，未跑 Java 客戶端驗收。
- 調料瓶不可被活塞移動；穩定版逐方塊 tick 檢查支撐，避免容器與方塊分離。
- 原生容器清理先記錄「已驗證為空」的持久化退休標記，刪除失敗可重試，絕不把遺失的非空容器重建為空。
- 掉落生成結果不明、回復失敗時隔離原索引，需人工復原；不宣稱跨程序崩潰的原子性。

## Java 依據
Grilling 1.1.1 的 SeasoningBottleBlock／SeasoningBottleBlockEntity：完整堆疊複製、四瓶上限、EMPTY→PENDING、playerWillDestroy 與 updateShape。參考 JAR SHA-256：cf31071e4ba790bcd5c1d3f6005439bc512acba084e70b8ab6a767e8c8f99dd6。

穩定基岩元件依據：https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/blockcomponents/minecraftblock_movable?view=minecraft-bedrock-stable

## 驗證與限制
32 項實際函式＋儲存 API double 測試涵蓋完整資料、重新載入、每步寫入故障、舊資料導入、掉落結果不明及清理重試；不是模擬玩家或原生客戶端驗收。完整歷史回歸已通過；BDS 1.26.52.3 的 16 包原樣載入及另一個測試 overlay 的四瓶原生資料保存／真正程序重啟均通過，未啟用實驗功能。詳見 [BDS-SEASONING-20261001.json](BDS-SEASONING-20261001.json)。Dash 另由 GitHub CI 執行。

hasSolidTop 仍是穩定 API 的近似支撐判斷；延後手動放置／破壞尚未驗證所有第三方領地保護的事件順序。setblock/fill 的 replace 模式或其他 addon 直接替換方塊不會自動刪除原容器：保留原資料並拒絕覆蓋，需人工復原。舊版已丟失的自訂資料無法還原。沒有宣稱完整 Java 一比一或 live 遷移成功。

使用者已取消 live 工作；本版僅進行來源修復與公開驗證／發布。
