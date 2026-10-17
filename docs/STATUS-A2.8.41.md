# A2.8.41：Java 1.1.1 審查後修復

本版以 Java 1.1.1 / NeoForge 1.21.1 的作者來源 `9a1acdab27698457bec16c9362678e574895a28c` 為功能基準，承接 main A2.8.40。保留既有油壺交易保護、作者 UUID、原作圖形進食條、音效與唯一指南入口。指南內容未改，payload 仍為 0.3.14；Cookery 的已登記 additive family API 升為 0.2.3。第三方原包、私人脚本與存檔不提交到本倉庫。

## 已實現的修復

- 喝完原生牛奶清除可治癒的煙火自訂效果，保留原作明訂不可治癒的重金屬中毒。死亡後重生清除全部自訂效果與龍血附加池；首次登入保持有效期限，不能把重新連線當作死亡。
- 熱度權威期限保留到一 tick，取消向下捨入 100 ticks。堆疊合併仍依數量加權；原生變體不同不能合併。
- 背包非手持熱食與已開啟容器以有期限的槽位工作更新 lore，保留实际 ItemStack、名稱及其他 RawMessage。每 tick 最多 64 個熱槽、兩個容器掃描；冷背包不逐 tick 全掃。卸載容器重新互動時再登記。沒有宣稱能即時刷新所有未開啟的第三方容器。
- 高級廚具架第一層選槽直接執行原交易交換，管理／篩選移至獨立入口；物理槽位潛行點擊保留。這是基岩互動改善，沒有宣稱 CapsLock 鍵位等價。
- 展示物以空間索引選取玩家 48 格內設備，每 tick 預設處理八個目標；剛互動目標優先，也保留公平輪轉與離場清理。內容 helper 預設容量由 512 升至 2048，三種 helper 上限均可設定且到限有診斷。這些仍是有界預算，不承諾無限設備。
- 效果三個 canonical 寫入者共享單 tick 快取，不重複解析同一份效果，也不逐 tick 寫回空值／相同值。油源改為 deadline heap、cell claim 索引及 BFS 游標；未確認持久寫入保留重試排程。烤爐權威逐 tick 寫入未擅自取消，以保留回復語義。
- 調料瓶、架管理與秘製串製作者／食材順序改為三語 RawMessage。交換／複製維持 RawMessage，避免 flatten 丟失翻譯。食材明細改善辨識，但不是動態合成圖示。
- 公開 food v1 增加選填 `nativeVariant`，作者可疑燉湯出料與展示命令保留／驗證 native aux；不同 aux 不混疊。登記式 render provider 只使用作者公開資料。此接口不等同任意第三方私人模型資料的完整副本。

## 管理設定

`/kaleidoscope_grilling:config <key> <value>` 需要 GameDirectors 權限。設定保存於煙火自己的世界 dynamic property，重新啟動載入；無效／未知值拒絕，不改其他包。

| key | 預設 | 可用值 |
| --- | --- | --- |
| saturationMultiplier | 1.25 | 0–16 |
| fullHungerEating | true | true / false |
| graphicalEatingHud | true | true / false |
| contentsHelpers | 2048 | 32–8192 整數 |
| fixedGrillHelpers | 1024 | 32–8192 整數 |
| placedHelpers | 1024 | 32–8192 整數 |
| contentsTargetsPerTick | 8 | 1–32 整數 |

滿飽食開關作用於煙火食物的使用入口；它不改第三方食品 JSON。提高 helper／工作上限前需以實際客戶端與多人負載驗證。Java 熔爐自動加熱、全部動畫設定與選用整合尚未提供同等選項。

## 審查項目的交付界線

| 審查 ID | 本版結果 | 未完成／仍需驗收 |
| --- | --- | --- |
| R01 效果生命週期 | 牛奶／死亡事件與共享效果儲存已修復 | 真人牛奶、死亡、重連事件驗收 |
| R02 熱食提示 | 非手持、已開啟容器、到期更新 | GUI 動態熱食框／徽標；未開啟第三方容器與客戶端首次開啟刷新時序 |
| R03 秘製串合成視覺 | 三語食材順序與來源名稱 | 任意組合背包圖示／雙手實體合成 |
| R04 展示資料 | 公開 aux／durability、明確 provider、完整可讀快照簽名 | 私人資料模型無完整 equip clone；腳本 inventory clone 不等於可見手部 |
| R05 進食曲線 | 保留原作五種曲線 | THREE／ALT 共享随机參數、手臂與第二截物件未等價 |
| R06 架操作 | 一次選槽交換、独立管理、交易不變 | 原作 CapsLock 不可直接映射；真人觸控／鍵鼠 |
| R07 展示規模 | 附近索引、互動優先、公平排程、可設定且可診斷上限 | helper 仍消耗實體；盤／其他舊輪詢與超量負載需後續量測 |
| R08 效能 | 效果去重寫入、油源排程與索引 | 真實 TPS／FPS／多人；烤爐持久化仍需交易安全設計 |
| R09 共用 HUD | 沒有捏造客戶端衝突結論 | 酒館／名酒／UI Queue 渲染與傳輸驗收 |
| R10 龍血 | 保留已修正有限 2 點附加池 | 原生 4／8 health boost 加池近似，心形與 max health 6／10 未等價 |
| R11 熱期限 | 精確 tick 與加權合併已修復 | 物品移轉／重啟真人驗收 |
| R12 多語動態資訊 | 三語本地化已修復 | 三語實際字型／表單／物品提示 |
| R13 選項／進度 | 提供可持久設定的原作適用選項與展示預算 | 全部原作 config、成就 UI、選用 Java mod integrations |
| R14 沉浸驗收 | native 載入、原生函式與存檔副本證據分開記錄 | 真實生存路徑、主副手、多人、跨平台、聲畫感受 |

來源／故障注入回歸使用儲存 adapter，沒有引擎模擬玩家。隔離 BDS 可以驗證原生 ItemStack／Container／dynamic properties 与重啟；不能證明玩家喝奶事件、死亡事件、表單畫面、聲音或 FPS。本版未完成的 Java 等價與真人項目不列為已修復。

新候選必須經完整家族逐檔收據和四項驗收。既有版本的 `deferred_client_acceptance` 僅綁定舊收據，不是本版部署授權。本次不改正式世界／實驗旗標、不重啟正式 BDS。

## 已執行驗證

完整 `verify_current.py` 與 384 個 relative imports 通過；新增 11 個效果／排程／設定／變體回歸，並保留油源交易與熱疊加測試。隔離 working candidate 的 41 包實際 BDS 函式探針已通過：原生非玩家實體效果儲存／清除、47 tick 容器熱食到期且保留名稱與 foreign lore、1197 tick 期限不取整、可疑燉湯 aux 7 裝備命令、設定持久寫入。完整 clean release 的載入／重啟與一致存檔副本收據另行記錄，不由 working candidate 推定。探針來源為 `development/native/parity-repair-probe.js`，測試匯入只存在隔離副本，不輸出進正式包。
