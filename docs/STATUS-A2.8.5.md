# A2.8.5：生存資料與操作修復

完整追蹤見 [修復總表](REPAIR-TRACKER.md)。本批不宣稱整個 Java 移植已完成。

## 變更

- 提前吃串結算先核對原槽位、數量、名稱及食材資料，再扣物品並加營養；写入失敗回滾。熱度倒數文字變化不視為換了另一串。
- 原生方塊 tick 更新烤架，移除 256 登記上限；既有位置狀態鍵及容器保留。舊登記資料不刪除但不再參與更新。
- 調料放置快照按方塊位置及玩家配對；擷取失敗直接取消原生放置。67 個單瓶清空配方涵蓋全部調料變體。
- 秘製串繼承已列舉的原版食物、煙火獨立食品及固定串效果，保留機率與容器回收。蜂蜜清除中毒、紫頌果嘗試安全傳送。任意第三方消費腳本不會被偽造為已觸發。
- 熱秘製串完成食用的飽和加成只計算一次；重複食材係數按原材料判斷。食材效果先結算，再由熱食完成事件延長新增效果，對應 Java `HotFoodHandler.onFinish` 的順序。
- 副手留空、潛行使用熱串：合併背包內同類串並按數量平均熱度。潛行點擊廚具架上排五格／下排四格可快速取物；正常互動保留管理表單。
- 花椒葉按生物碰撞範圍檢查側面與內部接觸，傷害共用冷卻。冷卻採存檔時間，避免程序重啟重設 tick 造成異常。
- 新操作寫入既有指南的中／繁／英條目，不新增實體指南或常駐提示。

## 驗證

- `verify_current.py`：既有玩法回歸、資源引用、指南、語法；新增交易故障、換槽／替換資料、原版食物機率、碰撞範圍與四向快速槽位邏輯檢查。
- 真正 BDS 1.26.51.1 獨立世界：300 個烤架放入實際 ItemStack 並檢查持久化狀態；300/300 更新、300/300 物品保留。
- 停止並重新啟動 BDS 後：300/300 繼續更新、300/300 物品保留。
- 原生豬從花椒葉側面接觸：生命由 10 降至 9。這驗證接觸程式可在引擎執行，不等於所有玩家皮膚／碰撞體型均驗收。
- 初次 BDS 檢查發現新增配方缺少 unlock，已補正；隨後載入沒有 Grilling 配方錯誤。
- 引擎探針 `development/gameplay_core/a285_engine_probe.js` 只供獨立世界，需複製到測試 BP scripts 並由該測試副本匯入；正式 BP 沒有探針或測試世界操作。

## 驗證界線

尚未實際操作玩家背包、調料合成、廚具架或多人場景。第三人稱、第一人稱、透明排序與手機操作仍需客戶端畫面。
秘製串任意模組食材事件、巢狀秘製串、可疑燉湯資料變體、個人化外觀與跨包自動化產出仍未完成。
本次原版食材效果以目前 Bedrock 原生食品定義為依據，並非宣稱所有數字與 Java 完全一致。

## 主要依據

- Java `SecretSkewerItem`、`ClearSeasoningCraftingRecipe`、`PepperLeavesBlock`，基準 commit `9a1acdab27698457bec16c9362678e574895a28c`。
- [原生方塊 tick](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/blockcomponents/minecraftblock_tick?view=minecraft-bedrock-stable)。
- [物品食物 API 的可讀欄位](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/itemfoodcomponent?view=minecraft-bedrock-stable)。
- [Mojang 原版食品資料](https://github.com/Mojang/bedrock-samples/tree/main/behavior_pack/items)，所用效果事實及逐檔來源收於 `fixtures/a285/vanilla-food-behavior.json`。
