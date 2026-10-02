# Java 原作與煙火移植：2026-10-03 審查

本次重新讀取 Java 1.1.1 / NeoForge 1.21.1 來源
`9a1acdab27698457bec16c9362678e574895a28c`，並對照 canonical main
`cad8651`（2.8.43）和本次候選差異。隨後以 2.8.45 main `1cf16f3` 和 2.8.46 系列標籤 `9e1bdb8` 為基底，保留兩輪差異。32 份直接讀取的 Java 檔案、連結、
SHA256 與特效參數記錄在
[`immersion-feedback-java-1.1.1.json`](../development/gameplay_core/fixtures/immersion-feedback-java-1.1.1.json)。
這份表涵蓋主要功能面，不能解讀成所有 Java 方法、所有第三方組合都已逐一執行。
來源審查、程式回歸、BDS 原生 API 和 Windows 真人畫面是不同證據。

| 功能面 | 直接比較結果 | 本次處理／仍有差異 |
| --- | --- | --- |
| 種植 | `CanolaCropBlock`、`OnionCropBlock`、`SweetPotatoCropBlock` 的 0–7 齡；`HouttuyniaCropBlock` 靈魂沙紅色、農田 30% 紅色、變體成長保留；runtime 對應 core 參數一致 | 真人需驗證自然獲取、骨粉、採收。花椒葉 Java `entityInside` 減速與條件頂面碰撞仍不是 Bedrock `onStepOn` 的完整等價。 |
| 切配／榨油 | `OilPressBlockEntity` 四餅、16 進度、鐵砧 +4、10 tick 冷卻；大缸八桶與 runtime 一致 | 落錘特效原為六個大型 crit 發射器，原作要求 14 粒。本次改自有單粒定義、14 粒高斯分布與 .82–.94 音高；交易與延遲機制不變。 |
| 組串 | `SkeweringHandler` 最多三份；runtime 19 生→熟配方加普通串、完整食材 snapshot 與變體路由 | 任意第三方食材私有模型、背包動態合成圖示仍不等價。已保留他人 2.8.45 的秘製串手持模型修復；仍須獨立驗收。 |
| 烤爐流程 | `GrillBlockEntity` 三槽、四翻、20 tick 翻面冷卻、800 tick 過熟與再 400 tick 木炭；runtime 同樣分段狀態機 | 本次移除原作不存在的 phase 切換火聲；刷油恢復 `grill_flip` 聲，不更動材料／出料交易。多人競爭、拆爐與斷線需要候選世界驗收。 |
| 火箱氣氛 | `GrillBlock.animateTick` 煙 y+.22／火 y+.18，橫向範圍與概率不同；runtime 曾合併為 y+.35 | 本次修復原作位置、1/3 和 1/8 概率與初速。仍以既有每四個 server ticks 取樣；Java 客戶端隨機 animateTick 的整體密度未聲稱等價。 |
| 油與熱源 | 三油熱時長 1200／12000／24000 ticks 已有；原作 `PremiumChiliOilBlock.animateTick` 有熔岩／火焰粒子 | 自訂油是腳本方塊流動，不是真 Java FluidType。熔岩辣椒油的原作環境粒子仍缺；沒有用任意高頻輪詢來假裝等價。 |
| 調料 | `SeasoningBottleBlockEntity` 八料、四瓶；runtime 16 次使用、基底配方及頂瓶操作已存在 | 修正加入原料五粒 end rod、搖勻 12 粒 happy、原作音量；取瓶改播 bottle-place，堆瓶仍播 bottle-stack。 |
| 熱食 | `FoodState` 熱度、調料條件、按數量加權合併，runtime 已有；25 tick 進食 checkpoint 已有 | runtime 2.8.41 保留單 tick 期限，而本次讀取的 Java source `bucket()` 仍是 100 ticks，屬既有已交付偏差，本次不暗中撤回。GUI 熱食徽標與未開啟第三方容器仍未完全還原。 |
| 進食／手持 | `MultiBiteSkewerItem` 的 25 tick checkpoint、`SkewerEatingHud` 的 102×5／16 像素圖示與 runtime 原作 HUD 來源相符 | 2.8.43 為玩家骨架座標回歸，不能證明 Windows 畫面。五類動畫、主副手、走動、FOV、秘製串多食材與第三人稱均需真人。不得以編輯器投影通過代替。 |
| 黃金串 | `GoldenSkewerItem.afterFoodCommitted` 的 18 點螺旋 spark 完全缺失，beacon 音高／音量缺省 | 本次補 18 點、半徑 .65、高度 .25+i×.06 與原作事件速度、beacon .8/1.15。只在原有食物結算成功路徑觸發。 |
| 無敵狀態 | `InvincibleHandler` 每十 tick 一粒周身 spark；受擊六 tick 節流、8 spark+4 end rod、體高 55% | 本次補齊；使用穩定 API `getAABB().extent.y*2`，並把不存在的 `random.shield_block` 改成官方 `item.shield.block`。傷害取消條件未改。 |
| 普通串挑戰 | `CursedSkewerItem` 被盾擋住時有兩聲與 28 spark，runtime 原只有錯誤盾音效和一粒 | 成功盾分支本次補齊。致死分支的 Java damage-indicator／large-smoke 及完整聲畫仍缺，沒有以不同粒子冒充完成。 |
| 其他藥效 | 原生 speed／strength、水下呼吸等與自訂效果儲存已有；麻木持續時間／調料倍率已存在 | 牛奶、死亡、重連需真人事件驗收；麻木準星偏移無穩定對等 API。已保留另一輪 2.8.45 的原生龍血與共享進食修復，不重做／覆蓋。 |
| 盤子／食譜 | `SkewerPlateBlock` 原作放取物品為 itemframe 音；`SkewerRecipeBookItem` 完成為 action-success .7，貼牆為 itemframe-place .8 | 本次取代 runtime 的 pop／levelup 聲；保留既有出入料 rollback。最多五串、選最營養串、食譜材料消耗仍由既有功能回歸覆蓋。 |
| 架子／容器 | `AdvancedRackBlockEntity` 九格；runtime 使用 native ItemStack 容器、個別所有權、metadata 與交易收據 | 選槽／篩選是 Bedrock 表單操作，並非原作 CapsLock 原生 GUI。需要真人測完整手持物品、多人與重啟；不可把 adapter 測試稱為存檔驗收。 |
| 音效資產 | 已有 Java 正式 jar 的原始 OGG 與 SHA256，循環烤爐有獨立 handle／空爐停聲 | 本次修事件路由與音量。聲音方向、衰减、多爐混音與 Windows 多玩家聽感仍待驗，原聲檔存在不代表每个場景完整。 |
| 粒子資產 | 原 vanilla `critical_hit_emitter` 是 steady 520/s、max 48；manual emitter 不能以呼叫次數當粒數；electric spark 需要 direction 參數 | 本次六個自有 `feedback_*` 一次一粒／零偏移，顯式提供三軸初速，不覆蓋 vanilla。保留 Mojang 版 sprite／motion 是 Bedrock 表現近似，並非 Java particle class 完整物理拷貝。 |
| 指南／多語 | 依既有 Guide 標準：Cookery 內唯一 Grilling 入口、六類烹飪分類、三語名稱；不新增實體指南 | 本次不改宿主或指南 payload。頁面是否可達、圖片、三語排版、觸控與 Windows 真實操作仍需候選驗收。 |
| 持久化／遷移 | Java BlockEntity save/load 對應 Bedrock 原生容器+own DP，並有來源與交易回歸 | 靜態功能存在不證明 luosen 存檔資料已遷移。本次只改聲畫；完整家族 static、BDS、saved_world_migration 通過後，依 2026-10-03 持續授權為該收據登記 deferred_client_acceptance，可先更新 live 開發測試；真人未驗證仍為 client=false、production_ready=false。 |
| 選用模組／效能 | Java Create／Maid／KubeJS／JEI 等為獨立整合；Bedrock 有已登記公開 food/oil/render API、bounded helper 調度 | 未安裝 Java 模組的整合不能宣稱完整移植。真實 TPS、FPS、大量設備、多人粒子密度與長時間运行未由來源測試證明。 |

本次粒子來源釘選 Mojang `v1.26.50.4`，原始定義及 hash 在
[`feedback-mojang-1.26.50.4.json`](../development/gameplay_core/fixtures/feedback-mojang-1.26.50.4.json)。
`tools/build_feedback_particles.py` 僅从這份經 hash 驗證的公開來源生成自有定義。
`test_immersion_feedback.mjs` 驗證 count、位置／高斯分布、速度轉換、單次發射器、
螺旋範圍、六 tick 冷卻和 API 失敗隔離；不建立模擬玩家、不宣稱渲染通過。

Windows 客戶端優先驗收：三種串第一／三人稱及吃完後、黃金串一次螺旋與無敵持續、
連續受擊節流與多人旁觀、調料五／十二粒、榨油 14 粒、點燃／熄火／空爐、
放取瓶／盤子／牆上食譜的聲音，以及酒館和名酒同時載入時的 HUD。
