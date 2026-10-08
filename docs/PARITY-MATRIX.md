# 煙火現況對照表

更新：2026-10-08；G117保存與手持營養修補基於 canonical G116／`b4bd3229f254adf58be1ee413f89daa1ab9c4df0`。
來源版本2.8.117；下列既有BDS／LIVE觀察快照為04:42 UTC的T126／G114／W103、作者Cookery1.6.0；
G117新家族部署證據另行記錄，不能沿用舊觀察為新功能驗收。
完整客戶端驗收仍是 `client=false`、`production_ready=false`。

Java 選定來源為作者 [`9a1acdab27698457bec16c9362678e574895a28c`](https://github.com/breezeth-CN/KaleidoscopeGrilling/tree/9a1acdab27698457bec16c9362678e574895a28c)。
2026-10-08 04:23 UTC 上游查核的正式維護發布為
[Forge 1.20.1／CF8726006](https://www.curseforge.com/minecraft/mc-mods/kaleidoscope-grilling/files/8726006)
及 [NeoForge 1.21.1／CF8726014](https://www.curseforge.com/minecraft/mc-mods/kaleidoscope-grilling/files/8726014)，均為1.1.1。
主要邏輯對照使用 NeoForge；共用資產不代表 Forge 的專有事件也已驗收。
原碼為 BSD-3-Clause，素材為 CC BY-NC-SA 4.0；選定 snapshot 不等於完整原作 JAR 已執行。

證據代號沿用 Phase 0：**A** 是直接執行原 Java 純邏輯所得黃金向量；**B** 是守恆、冪等、交易回滾等不變量；
**C** 是真 BDS 引擎場景；**D** 是真人客戶端視覺、音效與手感對照。
原始碼比較、Python 翻譯公式、資產預覽、static、compile、hash 和 CI 身份檢查是前置，均不算 A–D 通過。
「有實作」與「待驗證」也不分別等於「完整還原」和「新證實的 bug」。

| 項目 | Java 原邏輯／A 證據 | 當前 Bedrock runtime／B 證據 | 真 BDS／C 範圍 | 真人畫面、音效／D 範圍 | 尚未完成／來源參照 |
| --- | --- | --- | --- | --- | --- |
| 環境與完整家族 | 原作兩個 loader 分支各自追蹤；來源 pin 不證明移植完成。 | G117；最低 engine1.26.50、既有驗證 BDS1.26.51.1；server2.9.0／server-ui2.2.0；Cookery1.6.0 與 family API0.2.6。 | G114既有42包首次／重啟、最新停服存檔首次／重啟通過，0玩家；18筆玩家資料及2個自訂容器保留。**只證明載入與記錄的保存範圍。** | 沒有當前候選的完整 Java↔Bedrock 全玩法驗收。 | 不能把42包載入稱完整玩法通過。保留了存檔原有 GameTest／upcoming_creator_features 等實驗旗標；未執行 GameTest，也未證明關閉全部實驗仍可完整運作。[Phase0範圍](audit/AUDIT.md) |
| 固定牛肉串：正常取得 | 一份生牛肉加工出2份牛肉塊；固定配方依序使用牛肉塊／紅辣椒／牛肉塊。這是來源／資料契約，尚無整段 A trace。 | 完整家族 Board API0.1.0 的 replace 配方保留4刀、再一次持刀釋放、輸出2塊；B涵蓋材料、取消、出料交易與回滾。普通未擴充 Cookery 能力另列。 | 舊 Board probe 有真 ItemStack／drop／狀態及重啟資料；其代用容器並非玩家持刀事件。當前 family載入不能補成 G114砧板操作C。 | G114 正常取材、4刀耐久、釋放、取消與拾取仍待同候選完整操作。 | 舊 Cookery1.0.8 取得阻塞已被家族 API 承接，不能當今天仍未修；註冊 accepted 也不是實際取得成功。[G31契約](STATUS-A2.8.31.md)、[Cookery1.6適配](STATUS-A2.8.72.md) |
| 固定牛肉串：穿製 | 原配方的食材順序與 raw→grilled 對應已固定。 | 主副手穿製、固定配方與 snapshot 有實作；B涵蓋扣料、剩餘物與交易失敗。 | 舊 G29 核心 probe 從已提供的物品進管線；`playerUseEvents=false`、`naturalAcquisition=false`。 | 空氣／方塊／實體入口、潛行、連按、換槽、滿包仍需真操作；不能沿用舊候選為G114完整D。 | 優先限定這一配方，避免用注入生串代表生存全流程。[原流程證據](evidence/skewer-flow-native-2.8.29.json) |
| 固定牛肉串：油、四翻、撒料、取出 | 爐容量3串；4翻、20tick翻面冷卻；FINISHED800tick、BURNT400tick階段。每占用串耗1點油、1次調料。 | 當前 core 保留上述規則；一串耗1油／1調料。B有不足不前進、手部失敗回滾、成功後清槽與成品保存。 | 舊G29有19固定串＋1秘製串的真 ItemStack／容器核心烹調與重啟；沒有玩家使用／食用事件。**不是G114／Cookery1.6完整受影響流程C。** | 同一瓶與同一串的刷油→四翻→撒料→熱串取出尚未完整驗收。 | 先復驗瓶前置與此切片，不重做已有爐狀態機；800/400是階段計時，不能直接稱總烹調時間。[既有全流程B](../development/gameplay_core/test_full_skewer_flow.mjs) |
| 調料瓶前置 | EMPTY→PENDING；持續使用80tick／4秒搖勻為SPECIAL；成功撒料才消耗use。 | G114 RawMessage／材料數修補已合併部署；保留原料、搖勻與交易路由。B保護自訂lore、metadata與失敗回滾。G117新增延後爆炸取消／event不可讀時保留瓶、容器與完整保存記錄的B。 | 原生 ItemStack建構、容器資料片段及family載入各有範圍；未證明整個玩家取瓶／完成handler或本輪爆炸取消時序。 | 舊G112真取瓶失敗有記錄；G114同瓶取回→搖勻→撒料仍待復驗，瓶姿態亦未完整D。 | [SEASONING-FLOW](BUGS.md#seasoning-flow自填瓶取回搖勻撒料)、[爆炸取消](BUGS.md#seasoning-explosion-cancel後續取消爆炸仍清除瓶與內容)、[已合併PR176](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/176)。舊draft[#172](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/172)／[#174](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/174)的列明有效差異已承接，不重合併其舊身份。 |
| 熱度與營養 | **有限A**：原 `FoodState.HEAT_BUCKET_TICKS`／`bucket` 方法以Java執行，非負時間的100tick桶向量相符。牛肉串nutrition5、saturation modifier0.6、Strength10秒是原資料，尚非完整A。 | 三油熱期限1200／12000／24000tick；熱食與調味資料有保存路由。B涵蓋期限、外來metadata、回滾與一次結算。 | 當前保存／載入C不等於真人hunger、saturation、effect各分支C；舊core產物讀回只保留其原身份。 | 牛肉串实际营养、10秒Strength及热食到期效果需同候选真食用核对。 | A **没有覆盖整个FoodState、grill、营养／效果回呼或完整JAR**；本輪不扩大oracle。[ORACLE-CHECK](audit/ORACLE-CHECK.json)、[有限向量](../development/gameplay_core/fixtures/java-heat-deadlines.json) |
| 食用、取消與離線 | FOUR profile90tick／4.5秒；25tick提前結算檢查點與release的一tick grace分開；完整動畫不是1.25秒。 | G81已修有完整counter證據的nonterminal stop→leave競態，G114保留。G117讓手持提前結算重取saturation／effectiveMax；B檢查新界限、較低cap、metadata、重複事件與refresh／寫入失敗回滾。 | source／API doubles不能證明真Player stop/complete/leave順序；direct leave、缺省／0counter、shutdown/crash未閉合。新的手持營養修補尚無其原生Player證據。 | 舊G81有局部進食／relog／副手觀察；普通副手air-use未啟動是有限失敗記錄，非G114修復。 | [手持飽和度修補](BUGS.md#handheld-saturation手持串提前結算沿用舊飽和度界限)與G116餐盤修補分開追蹤。24/25/26、90tick完成、取消／換手／換槽／連吃／normal relog仍需當前完整D。[G81範圍](STATUS-A2.8.81.md)、未入基準的文件[#145](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/145) |
| 固定牛肉串 icon、模型、HUD、聲音 | fixed raw/grilled sprite、模型、FOUR曲線、25tick原HUD與音源可追蹤；這些來源不是A執行或Java截圖。 | 靜態icon註冊、原資料衍生的持物／進食投影和audio路由存在；引用鏈／資產檢查只算前置。 | BDS可確認載入與特定API呼叫，不能確認鏡頭、逐口去塊、光照或聽感。 | 第一／第三人稱、主副手、皮膚／FOV、旁觀者、模型去塊與聲音中斷尚未完整對照。 | **待完成D，不宣稱聲畫一致。** 固定串靜態icon與下一行秘製串動態icon分開。[食用契約](JAVA-FIDELITY-GOAL-20261007.md) |
| 任意食材秘製串 inventory icon | 原16×16 GUI按有序食材、數量、生熟與variant合成；Python參考合成器是來源翻譯，**不算A或D**。 | G104有兩張static fallback；任意每串三槽資料的native inventory投影尚未完成。 | 載入static圖像不能驗證任意stack顏色／形狀選擇。 | 有使用者失敗觀察；現行仍待實際inventory復驗。手持模型不能代替背包icon。 | 這是秘製串的真缺口，不能無說明當作固定牛肉串直接阻塞。[SKEWER-GUI](BUGS.md#skewer-gui任意食材秘製串-inventory-icon)、[issue166](https://github.com/casama233/kaleidoscope-grilling-unofficial/issues/166)、[渲染界線](CUSTOM-SKEWER-INVENTORY-RENDER-LIMITS.md) |
| 餐盤營養與互動 | 原食用只結算一次；成功block互動不額外啟動另一份air-eating。 | G116重取live saturation／effectiveMax，並仲裁plate與item-use、排除較近entity；既有B覆蓋具體故障、回滾及合法使用，不證明原生輸入完整相同。 | 舊診斷有saturation越界後回滾；需保留原phase，不當成當前修復C。 | 舊候選有插盤後意外食用剩餘串的觀察，當前復驗未完成。 | 已由G116窄承接[#148](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/148)／[#150](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/150)的列明差異；未導入舊視覺union。[G116](STATUS-A2.8.116.md)記錄來源与LIVE場景，受影響C/D仍待驗。 |
| 放置／手持餐盤內容 | 原作按槽、份數與FIXED transform顯示實際串。 | 放置盤仍走generic路由；獨立完整mesh／dirty更新與手持五行projector尚未入受審runtime。 | 舊placed候選只有限定份數／四朝向樣本；held stored1／4被讀成0／3的故障保留。 | 舊tiny-edge-pixels、secret-alt空顯示與count失敗是bounded觀察，非當前完成D。 | 未整合來源：placed[#146](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/146)／[#149](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/149)／[#152](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/152)；held[#153](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/153)。[#155–164診斷](audit/PR-TRIAGE.md)保留原來源；#164 count-only候選未有其原生驗收，不能以float32模型代替。 |
| 其他平台與效能 | 原作流體、準星mixin、碰撞hook及任意食品回呼有各自需求，非單一算法。 | 腳本油流與明列替代保留；任意Java callbacks／Create／Maid等不會自動取得Bedrock等價。 | 有局部native能力與profiling；沒有約定的完整效能通過預算，載入正常不代表slowdown已解決。 | 完整粒子／混音／碰撞／多人手感仍缺。 | 保留[平台與效能缺口](BUGS.md#維護風險與平台決策)，按來源和實際API逐項決策；不由舊README永久判定放棄。 |

PR欄採用 **2026-10-08 G116重新核對的固定runtime差異**；「未入基準」不以版號落後、ahead數或PR仍開啟作判據。
完整exact heads、已承接差異與診斷範圍只維護在[PR-TRIAGE](audit/PR-TRIAGE.md)，不在此複製另一份歷史清單。

後續先修一個能改變玩家結果的問題；本機只做該失敗的診斷，完整必要套件交同一候選CI一次。
沒有相關新變更或新失敗時重用有效證據，不為這張表新增測試或重新啟動BDS。
固定牛肉串下一輪以正常取得→穿製→油→四翻→同瓶撒料→取出→食用→保存為單一路徑；
所需C只補原生／保存缺口，D由使用者實際客戶端對照。來源／發版／備份／家族准入邊界仍保留，禁止模擬玩家。
