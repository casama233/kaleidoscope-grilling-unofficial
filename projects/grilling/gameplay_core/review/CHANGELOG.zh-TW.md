# 森羅煙火 A2.8.8 Local Review：經驗回饋優化

狀態：本地原始碼與候選包；未推送 GitHub，未發布 Release，未部署正式服。
基線：`casama233/kaleidoscope-grilling-unofficial`（ID `1377218440`），commit `707d28edab4ea9af76878e0e29d8244848971db3`。
來源是該提交成功 workflow `36373807017` 的真實 artifact `10950386970`，不是重新執行歷史生成器。
原 `.mcaddon` SHA-256：`95e0ad3530d01c8b0afa39dc27bd19c42e210094df23b71f6054a9d93fd2bc9c`。

## 1. 本輪依據與邊界

上傳的《煙火指南 A3：分類索引》要求保留 Cookery 指南入口、唯一條目及生熟／瓶狀態合頁。
《森羅物語移植改善手冊：酒館經驗 → 煙火適用》提出先找真正執行來源、分離玩法與顯示、保留資料、唯一操作入口、交易失敗回滾及如實驗收。
經驗手冊本身不是煙火故障證據：下表的問題來自本次解開 A2.8.7 後實際讀到的程式。

沒有把酒館的座標常數套進煙火，也沒有把「煙火」解讀成 fireworks。
沒有更改料理條件、配方選擇、營養、熱度算法／Full Sort 分組規則、翻面次數或熟成時間。

## 2. 根因、改動、證據、剩餘驗收

| 範圍 | 原碼中的問題 | 候選版實際改動 | 檢查與未證明部分 |
|---|---|---|---|
| 手持寫入 | 副手 setter 吞掉例外；缺少元件時返回 undefined；上層交易無法區分成功與失敗 | 主手容器不可用、缺少裝備元件、副手 setEquipment 返回 false 時明確拋錯；交易使用固定原槽位 writer | 官方 API 返回型別已核對；JS／引用檢查通過。仍需玩家主副手及其他共用 setter 使用者驗收 |
| 交易執行器 | 原 helper 只認例外、不認 false；第一步失敗也會執行未嘗試過的第二步回滾 | 新 commitSteps 支援 false、只回滾實際嘗試的步驟、逆序回滾，單一步驟回滾失敗不阻止其他回滾 | 純 callback 順序與故障分支檢查；不等於 Minecraft 的扣料／掉落已驗收 |
| 烤架操作 | 放串先寫入烤架；扣手持拋錯時不能走原先只處理 false 的撤回分支 | 放串改為容器與手持聯合提交；刷油、撒料、打火石路徑固定原槽位回滾，記錄回滾失敗 | 烤架邏輯 core、配方與時間常數未改；需要生存主副手與滿背包檢查 |
| 穿串／拆串 | system.run 延後執行時重新讀當時雙手，沒有保存原手勢的雙手狀態；扣料和副手替換分離 | 沿用原唯一 scheduleSkewerAction，增加雙手完整既有 signature、槽位、維度、潛行狀態快照；切換則取消。原料、成品、副手與餘料交付使用同一組回滾步驟 | 純字串快照比較及取消分支通過；未以 mock 玩家假裝實機。仍需同 tick 事件、長按、切槽、離線與多人檢查 |
| 餘料與拆串輸出 | 輸出途中失敗可能留下部分背包變更；未知原料還原失敗被跳過 | 預先建立全部輸出；任一原料不能建立便停止扣串；保存背包快照及本次新增掉落实体，失敗時嘗試移除本次掉落並回復背包。餘下木棍沿用原 stack metadata | 保留既有「合併背包→剩餘掉地」策略；引擎回滾仍可能失敗，會列出失敗數；沒有保證斷電／崩潰原子性 |
| 調料瓶 | push／加料／取瓶忽略 boolean 持久化結果；資料、方塊外观、手持分開提交 | 世界原始存儲值、原 permutation、原手持一同快照；讀到不支援／損壞內容時拒絕破壞性寫入，保留舊合法 string[] 遷移；取回前驗證物品內配料、次數、變體 | 保存 key 未改；容器回滾原始字串，不用正規化後資料替代。仍需 0／1／15／16 使用量、重啟與實際堆瓶驗收 |
| 熱串整理 | 先清空原槽再建立結果；結果建構或中途寫入失敗沒有回滾 | 全部結果先建立並核對熱度；確認可放回原槽後逐槽提交；寫入失败逆序回復，不觸碰其他物品槽 | 原 Full Sort／Normal Sort 語義保留；需要實際熱／冷、不同剩餘時間及特殊 metadata 檢查 |
| 烤架更新 | 即使 lit／legged／腳架方向不變，每個 tick 仍 setPermutation；未變狀態仍做 JSON.stringify | 只在目標狀態不同時寫 permutation；狀態有變才序列化；支撐方塊仍每 tick 檢查 | 源碼分支及差異核對，未量測 TPS／FPS，不能聲稱提升百分比 |
| 顯示排程 | 目標不足 12 個時游標在同輪重繞；dirty 與常規佇列可重複處理同一 row | 每輪 seen 集合＋有上限的 round-robin；保留每輪 12 個額度、6 個 dirty 保留策略及跨輪游標；單一玩家狀態讀取失敗不阻止其餘玩家 | 純 Map 排程的去重、刪除、大小與輪轉檢查；不表示實際渲染已驗收 |
| 離線暫存 | 數個 player-id Map／Set 未在 playerLeave 清理 | 清除本輪操作、吃串、潛行、提示抑制及玩家放瓶快照；不刪世界／物品／效果持久資料 | 訂閱與字段靜態核對；未測網路斷線／重連 |

## 3. 實際驗證

`review/validate_candidate.py` 可重跑，不會下載工具或啟動遊戲。
本輪檢查 128 個 JavaScript、1301 個 JSON、252 條相對 import；沒有缺失引用。
三個純演算法模組共有 22 項檢查通過；沒有匯入 Minecraft API、沒有 mock 玩家或模擬玩家互動。
基線 1905 個 BP/RP 檔案中，1896 個位元組完全不變；修改 9 個、增加 2 個，沒有刪除。
9 個修改包含兩個 manifest，因此美術、方塊／物品定義、配方、指南與創造欄仍保持原內容。
包 UUID、模組 UUID、已有內容 ID、原存檔 key、Cookery 1.0.6 UUID、Script API 版本未改。

最終 ZIP 另做排序／固定時間戳、重建雜湊相等，以及解包後逐檔雜湊核對。
這次沒有跑完整 repo 的舊 gates、官方 Dash、BDS、Minecraft 客戶端、Android 或多人實測。
基線成功的 CI 不能算作新候選版成功的 CI；舊 reports 只作歷史資料。

## 4. 尚未完成／特別風險

回滾只是同步 API 的最佳努力，並非跨存檔、跨 tick 或程序崩潰的 ACID 交易。
若玩家／容器已失效、方塊已卸載或原地面輸出無法移除，恢復可能不完整，必須查看 Content Log。
共用 hand setter 現在會顯露先前吞掉的錯誤；大缸、餐盤、油流體、廚具架等共用呼叫者未在本輪全部重寫為交易，亦需回歸驗收。
自然破壞調料瓶、首次放瓶的引擎事件交接、其他模組變更背包／方塊、以及所有非玩家自動化來源未因此全部解決。
對不支援的調料持久資料採拒絕寫入，不會自動刪除或「修成空瓶」；需另行無損遷移。

原追蹤表 R09／R11／R16 的跨包權威效果／煙燻配方／料理產出事件沒有新增；
R12 秘製串個人化外觀、R05／R06／R07 客戶端視覺、R15 多人生存等也不能列為完成。
指南依 A3 原則保留現有實作，未聲稱本輪重新生成或實機驗收指南 UI。

## 5. 安装與回退

先保留現有 `.mcaddon` 與世界備份，只在測試世界安裝。
本包依賴官方 Cookery 1.0.6；沒有內含本體、私人伺服器相容補丁或世界。
同 UUID 的 A2.8.8 可能覆蓋本地 A2.8.7 pack；不能把匯入低版本當作可靠的自動降版。
完整回退使用原包與世界備份，不要為測試而刪除正式世界資料。

## 6. 原始碼整合

交付的 SourcePatch ZIP 提供原檔雜湊檢查、預設 dry-run 的套用工具、純檢查與 CI 登記補丁。
只允許指定煙火倉庫；遇到修改過的目標檔案會中止，避免覆寫使用者未提交成果。
整合後应保留原 `verify_current.py` 通用 gate、`verify_a287.py` 既有 gate 與真實 Dash 編譯／輸出比對；新 wrapper 不取代它們。
完整 CI 尚未於本候選上執行，因此 CI 相容性仍需在整合分支確認；不能因本地檢查通過而直接推 main。
当前 main workflow 會自動建立 prerelease，源碼補丁工具不會 commit、push、開 PR、建 Release 或部署。

技術依据：Microsoft Learn 的 EntityEquippableComponent.setEquipment 返回 boolean 且可拋錯；Container.setItem 成功為 void 且可拋錯；PlayerLeaveAfterEvent 提供 playerId。
參考：
- https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entityequippablecomponent?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/container?view=minecraft-bedrock-stable
- https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/playerleaveafterevent?view=minecraft-bedrock-stable
