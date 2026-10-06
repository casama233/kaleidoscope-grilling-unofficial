# 煙火 Java 對齊檢查表（2026-10-06）

這份檢查表以 **G73／Cookery 1.6.0 本地草稿**為範圍，優先追蹤穿串、烹飪、進食、畫面／圖示與保存。核心流程已有實作及來源測試，但 **G73 尚無本輪原生客戶端、完整家族或舊存檔遷移驗收**。不提供完成百分比，也不把有模型、有接口或測試通過視為完整 Java 體驗。

[2026-10-05 審查](JAVA-PARITY-AUDIT-20261005.md)固定於舊 `2.8.61／81df62d`，保留為歷史。本表更新其後已整合的修復，不再把熱食倍率、關閉動畫的 25 tick 路徑或 owning-player 讀取誤列為完全未實作。

## 1. 來源與准入界線

| 對象 | 本次來源 | 可以／不可以推論 |
| --- | --- | --- |
| 已發布 Bedrock main | `3e83eb492ad99a725296d5cd4027643eba84c845`，2.8.72／Cookery 1.6.0 | 是本次整合起點；不是 PR135 的瓶子版 2.8.72 |
| 瓶子修復來源 | PR135 `0c33806e570219a60c5d063a7d4fef536f49c5fc` | 保留有效瓶子修復；歷史 Cookery 1.0.8 原生證據不能轉成 1.6.0 驗收 |
| 本地整合 | `c8fa441ce1a62d93434d8de3f13f6e49558334aa`，父提交為上述兩支 | G73 尚未凍結；不是已發布或已部署的成品 |
| GUI 來源工具 | `a03c951210414178feac8f510735f9e5ed1a9cd6` | 新增 Java 16px GUI 參考合成器和來源 fixture；沒有接入 Bedrock 原生背包圖示 |
| 本文件同提交的修復 | `main.js:completePlateUse` 與 `test_a2810_use.mjs` | 修正盤中秘製串原生食用別名漏掉食材 finish 行為；來源測試通過，尚無原生驗收 |
| Java 作者來源 | [`9a1acdab27698457bec16c9362678e574895a28c`](https://github.com/breezeth-CN/KaleidoscopeGrilling/tree/9a1acdab27698457bec16c9362678e574895a28c) | 本次重新取得並讀取的來源；主要比較 NeoForge 1.21.1，不宣稱兩 loader 全方法驗證 |
| Java 分支版本 | `forge-1.20.1/gradle.properties`：1.20.1／1.1.1；`neoforge-1.21.1/gradle.properties`：1.21.1／1.1.1 | README 的 1.1.1a 不代表已取得另一個發布包；本輪未啟動或重新編譯 Java |
| Cookery 主機 | manifests／baseline 指向 1.6.0；BP UUID `5df753c9-3436-4fba-87f1-a2da3651cfcf`，RP UUID `f1d333ca-2d6b-4566-8005-e6c309816324` | 主機來源見 `tools/fixtures/cookery-160-reference.json`：作者 file 9054164；八個 host target 的來源檢查不等於原生 API 或遷移通過 |

本輪沿用 [G73 狀態頁](STATUS-A2.8.73.md)的准入決定：使用者允許本地修復及 Git draft；**當前 BSM Java upstream 狀態仍未取得，merge／release／deploy 前必須補齊**。不推測其新鮮度或通過結果。本檢查沒有用另一份公開搜尋結果代替 BSM 狀態，也沒有在此重複抓取或覆寫歷史收據。

有限公開新鮮度檢查：2026-10-06 12:35 UTC 作者 HEAD 仍為 `9a1acdab`；12:43 UTC 重新讀取[家族公開 Java 追蹤](https://github.com/casama233/kaleidoscope-tavern-unofficial/blob/main/family/java-upstream.json)（其更新時間 11:17 UTC），仍分列 Forge 1.20.1 file 8726006 與 NeoForge 1.21.1 file 8726014，branch adaptation scope 明示 partial／未完整重驗。這是公開來源的有界確認，不替代缺少的 BSM prerequisite。

Runtime 修改後須重新核對 G73 最終 source tree、唯一 release identity 與受影響的驗證；尚未凍結不能被當成可略過最終 gate。舊 2.8.72 發布記錄、G71／G72 native hashes 與 UUID 不重寫。

## 2. 如何讀取狀態

- **S：有實作／來源檢查**。可定位程式或資料；不代表此輪執行過每項測試
- **T：本次來源測試通過**。Node／Python 或儲存 adapter 的結果；不是 Minecraft、真人輸入或 GPU 證據
- **H：有限歷史原生證據**。只對原記錄的 source、包、依賴、設備與操作成立
- **U：待驗證**。尚無足夠證據；不得寫成已知故障或通過
- **P：明示平台替代／未實作能力**。與 Java 行為不同，不以測試數量掩蓋

下面的勾選只表示該行明確寫出的來源工作已完成。未勾選項保留到列出的退出條件成立；沒有任何一個勾選代表全項客戶端對齊。

## 3. 穿串與材料身份

| 檢查 | 當前證據 | 剩餘條件 |
| --- | --- | --- |
| [x] 固定配方與資料輸出（T） | 直接比較此輪 Java `common/.../grilling/skewers.json` 與 fixture，結構一致；Bedrock 20 筆組串含 19 組 raw→cooked 加 ordinary；19 筆效果資料含 18 筆非空效果 ID／時長一致 | 這是資料與來源流程，不是 20 筆正常生存採集／製作驗收 |
| [x] 主手原料、副手空棒／未完成串、最多三份、固定／秘製分流（S/T） | `a24_skewering_core.js`、`main.js:threadOutcome/threadCurrent`；固定 tag selector、食材可食判斷、兩手捕捉與重複事件去重已有 | 鍵鼠／觸控／手把，點空氣／方塊／實體，空棒起步、連按及蹲下 precedence 須在同一 G73 客戶端驗證 |
| [x] 真實食材 metadata 與拆串回復（S/T） | `skewer_item_snapshot.js`、`ingredientSnapshot/restoreIngredient/disassembleOff`；保留原始 ID、名稱、lore、動態資料及支援的 native 欄位，先驗證可重建才扣料 | 不保證任意其他包所有未知 component 都能重建；失敗必須保留食材，不轉成只剩 ID 的贗品 |
| [ ] 滿背包的 Java 等價結果（P） | Java `SkeweringHandler.disassemble` 把食材／棒交給原生庫存回填；Bedrock `prepareOutputDelivery` 明確在無法完整交付時拒絕並 rollback，不冒險用未確認的 world drop | 目前是保守交易替代，不能宣稱滿背包與 Java 相同；若改善，需有可確認的 overflow 所有權／掉落回復設計 |
| [ ] 正常取得到組串（U） | 刀、砧板、磨粉、植物、樹及 host 配方已有來源 | 全鏈需在 Cookery 1.6.0 自然取得，不用 give 代替採集；要塞自然折耳根另列平台缺口 |

主要 Java 依據：`SkeweringHandler`、`SkewerRecipes`、`SecretSkewerItem`；Bedrock 路徑均在 `projects/grilling/gameplay_core/behavior_pack/scripts/`。

## 4. 烹飪、熱度與調料

| 檢查 | 當前證據 | 剩餘條件 |
| --- | --- | --- |
| [x] 烤爐三槽狀態機（S/T） | `core_logic.js` 對應 `GrillBlockEntity`：四翻、20 tick 冷卻、800 tick 過熟、再 400 tick 燒成炭；未點火暫停，油與調料按佔用槽扣量 | 同槽多人輸入、三槽不同身份、拆除／爆炸、容器滿、區塊卸載與重啟需原生測試 |
| [x] 第四翻凍結秘製熟食 snapshot（S/T） | `commitGrillFlip`／`setCookedIngredientRows`；`test_fourth_flip_snapshot.mjs` 與整串流程涵蓋後續 registry 變更不追溯改掉已凍結食材 | G67 曾有三槽 normal-stop/restart 探針，僅屬 [歷史 receipt](evidence/parity-repairs-2.8.67-native.json)；不是 G73／Cookery 1.6 遷移 |
| [x] 秘製營養與熱食倍率（S/T） | `secretFood` 使用有效食材，重複食材按原始身份判定；生食折扣存在；手持／盤子營養已使用 `grillingConfig().saturationMultiplier`，不再固定 1.25 | 非預設 1.0／2.0 下，原生完整吃完、提早放開與盤子、飢餓上限須同場對照 |
| [x] 三油熱期限與容量交易（S） | canola／secret_chili／premium_chili 分別 1200／12000／24000 tick；Cookery 舊壺與 typed oil 路由分開，容量由契約定義 | author 1.6 filled Oil Can 與其他 registered oil container 不得互搶；舊所有權／空壺／耗盡身份待遷移 |
| [x] 瓶子配方／狀態資料（S） | 八份、三種基底、16 使用次數、四秒搖勻、ordered layers、堆疊取頂瓶、EMPTY／PENDING aliases 及交易已有 | 同一身份完成放置→插入→拾回→搖勻→撒料→耗盡；G71/G72 有限證據見第 7 節，G73 原生仍 U |
| [ ] 熱度完全等價（P） | Java `FoodState.setHot` 把 expiry 向下歸入 100 tick bucket；Bedrock 保留逐 tick expiry／加權合併 | 例如傳入 1234：Java 存 1200，Bedrock 精確期限可保留 1234。這是既有可識別差異；本輪不任意撤回精確期限修復 |
| [ ] 任意 smoking recipe 與食材 finish 回呼（P） | `secret_compat_core.js` 有內建及註冊 food／tag 映射；Java 查詢實際 recipe manager 並呼叫食材 `finishUsingItem` | 未註冊其他模組不能宣稱自動完整繼承；註冊、效果、容器 remainder 和未知回呼需逐能力驗證 |

## 5. 進食與效果結算

| 檢查 | 當前證據 | 剩餘條件 |
| --- | --- | --- |
| [x] Java checkpoint 與事件防重（S/T） | readiness 25 tick；release-only grace 1 tick，因此 23 拒絕、24 可結算、25 ready。90／100 tick profile 原生完成另檢查 terminal duration 與身份；stop／complete 任一順序不重複扣料 | 不能把 24 tick release 說成無條件 bug，也不能從 VM event schedule 推論實際網路／引擎順序 |
| [x] 關動畫的原生 25 tick 路徑（S/T） | `enableEatingAnimations=false` 選 `_native_plain` alias；由原生 food 完成，不走手動提早放開 debit；設定已有持久化 | 設定切換、拿回舊別名、Cookery 熱／調料開關、指南顯示與重登入同候選验收 |
| [x] 盤中秘製串別名 finish 漏算已修（T；本文件同提交） | 原先 `completePlateUse` 只用 `eaten.typeId===SECRET_ID`。現只把派發 ID canonicalize，保留實際 eaten stack 給 `secretRemainders`；canonical、THREE_ALT 和 plain 都結算一次 | 本地 source repair；不是已合併／已發布，也沒有新增原生盤子進食證據 |
| [ ] 登出 checkpoint 結算（已重現的來源缺口 D02） | Java `MultiBiteSkewerItem.onPlayerLoggedOut` 明確結算符合門檻的餐點；Bedrock leave handler 清除 session，沒有等價登出結算路徑 | 見第 8 節：需安全 persistence 設計和原生事件順序證據；不能在 after-leave 假造可寫 Player |
| [ ] 全部真人吃法（U） | 既有 code 覆蓋兩手身份、切槽、native completion、remaining stack 與 presentation reset | G73 需測 <24／24／25 tick、完整吃完、兩串連吃、500ms 取消、替換物品、斷線、重生、飢餓／滿飢餓；一項通過不推廣至其他項 |
| [ ] Heavy Metal 與龍血跨包等價（P/U） | 重金屬同步預約防重、效果身份與 life-state 驗證已有；仍以 before-hurt damage 對目前 health 判斷，Java 使用死亡事件 | 護甲、吸收、同 tick 多次受傷和其他包改傷不保證等價；龍血 20／26／30 max health、奶／死亡／重登入與共享玩家定義另驗 |

有限效果表及兼容 API 的成功，不代表可執行 Java 任意第三方 callback。咀嚼聲、粒子、圖形 checkpoint 與效果 settlement 分開驗證；不得新增任意 actionbar 成功提示代替原作安靜體驗。

## 6. 模型、手持、動畫與背包圖示

| 檢查 | 當前證據 | 剩餘條件 |
| --- | --- | --- |
| [x] 秘製串既有視覺修復保留（S） | owning-player context、食材順序／partial state、G69 idle／active calibration、exact hand/item completion ownership、terminal visibility 和 helper alpha side geometry 已整合 | source conservation 不是每個食材、皮膚、FOV 或完整 session 的 GPU 驗收；[G69 記錄](STATUS-A2.8.69.md)明確保留歷史原生範圍 |
| [x] 成品瓶 64 sprites、空／pending 16 fill proxies（S） | 維持 PR135 瓶子 model／texture bytes；成品由 remaining／variant 選圖，pending ingredient X reflection 與 ordered tint halves 已修 | 不得寫成所有 64 款已原生測過；fill proxy 是通用 fill palette，不能表示任意八份食材色彩组合 |
| [x] Java 16px 秘製串 GUI 參考合成器（S） | `tools/java_custom_skewer_gui.py` 以 `9a1acdab` 的原始 stick／六 food mask 和色彩規則產出 reference；有專用來源／數值測試 | 此工具不是 Java screenshot，也沒有原生 Bedrock inventory routing。背包任意食材圖示仍 P |
| [ ] 原生第一／第三人稱對照（U） | Java 原曲線／音檔、profile 與分手資料已有 | G73 各 profile，raw／cooked、THREE／ALT、兩手、旁觀者、走動／蹲下、不同皮膚與 FOV 的畫面／聲音／停止點均待驗 |
| [ ] Java GUI 與輸入能力（P） | `arbitraryRuntimeTextures:false`；rack 使用 Bedrock 操作替代；麻木以玩家動畫代理 | 動態 inventory composition、热徽標、麻木準星位移與 CapsLock 按住／放開快捷介面均不得標記等價。參考圖、表單或持有副手物品不是能力證明 |

**Palette 來源仍有獨立邊界**：`development/gameplay_core/fixtures/secret-food-palettes.json` 共 213 筆，不是 213 個 current-Java／Cookery 1.6 food 的完整原生對照。部分 Cookery 食材仍使用 `reviewed_cookery_1.0.8_bedrock_public_sprite`，且 `source.java_particle_parity=false`；stateful tint／外部 resource override 也沒有動態取樣。`minecraft:carrot` 明確來自 official Java 1.20.1 particle sprite，因此三胡蘿蔔 reference 的來源有效；不能推廣到其他食材或當前主機全目錄。這是 adaptation／evidence scope，單憑 host 升版不能斷言已產生 runtime 視覺退步。

## 7. 可採用的有限原生瓶子證據

本輪沒有重新操作 Minecraft。下列是 repository 已保存的歷史記錄，保持原 source／archive／client 身份；兩份都寫明 `complete_client_acceptance:false`、`production_ready:false`。

| 記錄 | 綁定 | 已觀察 | 不涵蓋 |
| --- | --- | --- | --- |
| [G71](NATIVE-BOTTLE-G71-20261006.json) | source `1b93e8f0d63eda6ff504be12828ffe03c22dc46b`；pack `0b1cdeb0083de21d5b41185797a0b30040b9c868c80f7539a053a70c88c79c3d`；Bedrock 1.26.52.3 Linux／Kai／Survival；Cookery 1.0.8／Tavern 0.6.110／WorldLiquor 0.1.71 | 普通互動放空瓶、三基底插入與消耗、拾回／重放保留三層；名義 3.6 秒中斷保留 pending，4.6 秒完成搖勻；三個 finished variant spot checks | 一次立即拾回 sample 曾有舊位置殘層，後來 settled sample 清除；G71 不能當成 pickup cleanup 全過。未測全部 64、offhand、音訊設備或 Java 逐幀 |
| [G72](NATIVE-BOTTLE-G72-20261006.json) | source `5b0ea0730c3c643d8456d4adb59c51c44bce0883`；archive `5e5e1828fb633db8aeab8827c7aa9768aa55e59aff633348a788c8379022766c`；1.26.52.3 Linux／Ari／FOV60／Survival；PR135 舊依賴來源 | 兩次拾回的第一張返回截图都無舊位置殘層；保留三層及重放內容；名義 4.6 秒 shake 得到棕色 fill 與相符 icon | 只兩次觀察，沒有零幀／零網路延遲主張；不涵蓋其他皮膚、offhand、FOV 範圍、64 款、音訊或完整 Java 動畫 |

**以上不是 published main 的 2.8.72，也不是 G73 的原生通過。** 即使瓶子資產相同，Cookery 依賴、整合 source、食用修復與最後包身份已不同。G71 的 Blockbench roundtrip 只驗證 combined held geometry 的有限轉換，不能替代 Bedrock per-bone material／visibility 驗收。

## 8. 已定位來源問題與未測項分開記錄

### D01：盤中原生食用別名漏掉秘製食材 finish（本地已修，native 待測）

- **重現來源**：`a25_plate_recipe_runtime.js:stackRow/restoreStack` 保留 exact native ID，`isSkewer` 允許 canonical aliases；`main.js:completePlateUse` 原本在已扣盤子和補營養後，以未 canonicalize 的 ID 判定秘製 finish
- **修復前實際 production function 結果**：canonical `secret_skewer` 的 ingredient-finish dispatch 1 次；`secret_skewer_java_three_alt`、`secret_skewer_native_plain` 各 0 次；三者 nutrition／debit／afterCommitted 都 1 次。這不是未測畫面的猜測
- **修復**：只將派發 ID 換成 `canonicalFoodId(eaten.typeId)`；不改盤子 payload、不替換原始 eaten stack，不移動交易或效果順序
- **回歸**：`node development/gameplay_core/test_a2810_use.mjs` 共 65 個 completion／rollback scenarios 通過。新增兩手、Survival／Creative、canonical／兩種 alias 的 finish exactly once／metadata 保留／順序；五種失敗不觸發 finish；還原舊行的 counterfactual 仍能重現漏算
- **退出条件**：最終候選 gate、Git review 與 G73 原生盤子食用；source repair 不代表已部署

### D02：停止後、deferred settlement 前登出可丟失 checkpoint 結算（來源仍開放）

- **Java 對照**：`MultiBiteSkewerItem.onPlayerLoggedOut` 呼叫 `settleIfEligible`
- **Bedrock 定位**：`itemStopUse` 排入 `system.run`；callback 開頭檢查 `ACTIVE_EATS.get(id)===a`；兩個 `afterEvents.playerLeave` subscriber 清除該 session
- **本次有界重現**：直接擷取現行 production stop／leave subscribers，用 scheduler adapters：`stop@25 → deferred callback` settlement=1；`stop@25 → leave → deferred callback` settlement=0。這證明該 source event order 有缺口，**沒有證明 Bedrock 每次登出都會產生這個順序**
- **安全限制**：官方 stable 文件提供 before-leave 的 Player，但 before-event gameplay writes 受限制。不能把該 Player 存起來並假設登出後仍可寫；也不能僅刪除清理程式就宣稱修復。[WorldBeforeEvents](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/worldbeforeevents?view=minecraft-bedrock-stable)、[PlayerLeaveBeforeEvent](https://github.com/MicrosoftDocs/minecraft-creator/blob/main/creator/ScriptAPI/minecraft/server/PlayerLeaveBeforeEvent.md)
- **下一步**：先取得精確 client／server leave event order；評估可恢復的只讀 snapshot／journal／重新登入結算。若只能延後處理，明示這是 timing adaptation，需防 crash、重登、重複獎勵及 item identity 更換；本輪未擴大實作。D02 保持公開缺口，不把尚無安全等價 hook 的研究變成 G73 的無期限阻擋

### 仍存在的明示缺口，不能只標「待測」

- `integration_api_runtime.js` 的 discover 明確為 `vanillaFortressCallbackInstalled:false`。fresh-fortress producer API 存在，不代表原生新要塞會自然替換；不得用附近掃描假冒可靠生成來源
- 秘製 inventory 任意 runtime texture、麻木準星及 Java 專有快捷鍵沒有等價 runtime。GUI 參考合成器不關閉此項
- Java 任意 food callback／Create 動力／Maid AI／KubeJS／JEI／Jade 是各自能力，已公開 API 不等於對應整合已安裝
- Heavy Metal death hook、script 油流、full-inventory fail-closed 及 100 tick heat bucket 差異是已知平台／設計邊界，需逐項決策；不能以本輪數值測試宣稱消失

## 9. 保存、Cookery 1.6 與完整家族退出条件

- [x] **S**：秘製 raw／cooked ingredient snapshot、creator、heat、seasoning 和 native aliases 有儲存路徑；plate／rack／bottle 使用交易、readback、rollback 與有界所有權資料
- [x] **S**：`family_station_storage.js` 的 ledger／owner token、retired-empty tombstone 和 quarantine 機制明確拒絕模糊回復。顯示 helper 不能成為另一份可領取物品
- [ ] **U**：G73＋Cookery 1.6 正常停服存檔／重啟、區塊卸載、玩家離線／登入、死亡、奶、爆炸與滿背包；逐物品檢查份數、原始 ID、raw/cooked snapshot、creator、期限、調料和所有權，不只看新世界能載入
- [ ] **U**：從已安裝版本／Cookery 舊 UUID 的 stopped-world copy 遷移，八個主機 hook、producer／consumer、guide 和 saved ownership 一起驗證；不得用舊 `compat/family/candidate.json`（2.8.9）作為目前安裝鎖
- [ ] **U**：最終 source／包／receipt 一致的完整家族 static、BDS、存檔演練、備份、部署與回讀各自通過。缺 BSM 狀態仍阻擋 merge／release／deploy
- [ ] **U**：最小依賴／完整家族同場景效能、實際玩家操作延遲與 FPS。既有 G67 isolated server／G69 helper 記錄不推廣為 G73、多玩家或長時效能保證

## 10. 本輪檢查及下一批順序

本輪以變更依賴範圍做 source review／focused tests，沒有重跑所有 historical suites，也沒有新增 BDS／native／migration 結果：

1. 重新取得上述 Java source；直接確認 `skewers.json` fixture 與 current pin 結構相同，20 組串／19 raw→cooked／19 效果列（18 非空）對照一致；`test_java_survival_parity.mjs` 通過其 69 筆 recipe／effect assertions 及附加 tag／grill／knife checks。不是完整生存遊玩
2. 在 `c8fa441` runtime 上，六個 focused files（`test_full_skewer_flow`、`test_java_release_grace`、`test_fourth_flip_snapshot`、`test_plate_food_cache`、`test_food_snapshot`、`test_eating_native_completion`）合計 397 source tests 通過；其後只做本節 D01 runtime 改動
3. D01 改動後 `node --check main.js` 通過，既有 `test_a2810_use.mjs` 的 65 scenarios 通過；`test_plate_food_cache`、`test_native_variant_ingredient_effects`、`test_eating_native_completion` 合計 382 tests 通過。與上批重疊，不把數字相加當覆蓋率
4. 新增 `tools/fixtures/g73-plate-alias-main-delta.json`，只准許一行已審查的改動；完整鏈為 immutable G69→G71 bottles→G72 pickup→G73 plate alias，沒有放寬其他 source 排除。`test_historical_source_refs.py` 的 8 項（含 checkpoint／額外 byte／撤銷 alias 的 mutation rejection）、`test_secret_completion_scope.py` 的 2 項及 `test_secret_idle_calibration.py` 的 4 項通過
5. 已有 203 bottle／storage／held 及 Cookery 1.6 host-target 的結果由 [G73 狀態頁](STATUS-A2.8.73.md)追蹤；本輪不再重跑相同瓶子資產檢查。最終 main.js／baseline 受影響 gate 仍由最後整合重新驗證，不宣稱本文件完成完整 source gate

建議依序：**收斂 D01 與最終來源 → 補 BSM／主機准入 → isolated G73 的穿串・烤熟・盤中 alias 食用・瓶子回歸 → stopped-world／完整家族 → 同收據真人兩手／聲畫與效能**。D02 先研究安全事件／保存邊界；新 native 結果只追加其實際 source、依賴及範圍，不改寫舊 G71／G72 結論。

### G73 後的短佇列

1. **已確認、可直接修的 source 問題**：D01 已完成本地修復，先收斂到最終候選。任何新盤／架／爐問題只按可重現失敗、exact source 和最小修補追蹤，不用「全部未測」代替 bug 清單
2. **下一個核心檢查範圍，尚不是已知 bug**：正常取得→空棒→穿串／拆串→烤熟→手持／盤子吃完的同候選流程。若產生扣料、份數、snapshot 或 finish 不一致，先固定最小 source reproduction，再安排小批修復
3. **需設計或平台能力的獨立工作**：D02 登出結算、滿背包 overflow、任意動態 inventory icon、自然要塞 callback 與 death-hook 等價。分別列出替代與未實作範圍；不因它們尚未閉合而把已驗證的小修復永遠擱置，也不將它們冒充已完成

本輪沒有再找到另一項可在無新設計前提下直接宣稱應修的來源故障；未執行的 native cases 仍按 U 管理。

## 11. 主要來源入口

- Java：[SkeweringHandler](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/skewer/SkeweringHandler.java)、[GrillBlockEntity](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/grill/GrillBlockEntity.java)、[MultiBiteSkewerItem](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/skewer/MultiBiteSkewerItem.java)、[SecretSkewerItem](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/skewer/SecretSkewerItem.java)、[FoodState](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/food/FoodState.java)
- Bedrock：[main.js](../projects/grilling/gameplay_core/behavior_pack/scripts/main.js)、[core_logic.js](../projects/grilling/gameplay_core/behavior_pack/scripts/core_logic.js)、[plate storage／reconstruction](../projects/grilling/gameplay_core/behavior_pack/scripts/a25_plate_recipe_runtime.js)、[configuration](../projects/grilling/gameplay_core/behavior_pack/scripts/server_config_core.js)、[integration capability disclosure](../projects/grilling/gameplay_core/behavior_pack/scripts/integration_api_runtime.js)
- 修復與證據：[G67](STATUS-A2.8.67.md)、[G69](STATUS-A2.8.69.md)、[PR135 舊 G72](PR135-G72-BOTTLE-CANDIDATE.md)、[G73](STATUS-A2.8.73.md)、[source conservation](G69-PUBLIC-SOURCE-CONSERVATION.md)、[current family guidance](../compat/family/README.md)
