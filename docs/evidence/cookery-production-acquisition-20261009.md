# Cookery 生產、取消清理與剩餘取得鏈：2026-10-09

本頁對照 Grilling G119 canonical `b010ec2a6709ada74ed96ead19c60da4e0bc2789`、
Java 作者 `9a1acdab27698457bec16c9362678e574895a28c` 與 Cookery Bedrock 1.6.0。
本輪修改是來源層修補，不是實際宿主／玩家／自然生成已通過。

## 精確來源與版本

- Grilling Java [Forge 1.20.1](https://www.curseforge.com/minecraft/mc-mods/kaleidoscope-grilling/files/8726006)
  與 [NeoForge 1.21.1](https://www.curseforge.com/minecraft/mc-mods/kaleidoscope-grilling/files/8726014)
  均維持作者 1.1.1。主要機制比較採 NeoForge，沒有把 loader 專有 hook 當成共用事件。
- Cookery 1.6.0 的 CF9054164 原包 SHA256 為
  `da12fe6d39d7514aff1de3c963d69899324d771be5ca0fc3da1ccb759c7ad458`。
  本輪重新取回原包並核對 `extensionRegistry.js` 的
  `4f02f0705fe6cd1578485490a404bff7887ceb8ace9fec9c9f61863e3cdd1723`，
  以及 `directStation.js` 的
  `19207a023a04da532ff9e34cd95413f09cf000fc672255c03633a7bcb2744ad4`。
  只保留本倉庫原有的 hash、短 hook 宣告及自有模組；完整作者檔和原包未加入 Git。
- 本候選繼續使用 `@minecraft/server` 2.9.0。重新核對官方
  [WorldAfterEvents](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/worldafterevents?view=minecraft-bedrock-stable)、
  [Dimension](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/dimension?view=minecraft-bedrock-stable)
  及 [LootTableManager](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/loottablemanager?view=minecraft-bedrock-stable)。
  可產生 loot 的 API 不等於正常爐具出料或新區塊／要塞生成事件。

## 取消拆鍋／爆炸仍清除調味資料

G119 `a2750_cookery_cuisine_runtime.js` 的兩個 before-event subscriber 直接排程
`clearCuisineAt`；其他 subscriber 後續取消時仍會清除本站點的油／調味資料。
這與 Java 僅在實際 reset／移除時改變方塊實體保存內容的生命周期不符。
原 Java 對照為兩分支的 `mixin/PotBlockEntityMixin.java`，包括 `grilling$reset`、
`saveAdditional`／`loadAdditional`，以及 `StockpotBlockEntityMixin.java` 的保存欄位。

修補在 before-event 捕獲維度、位置、原方塊 ID、原 Grilling property key 與未正規化的原始 bytes。
初始和延後判定均要求 `cancel === false`；事件已無法讀取時保留資料。
延後再確認該位置已載入、原站點確實離開、沒有新炒鍋／湯鍋，而且原始保存 bytes 未改變，
才刪除本次捕獲的資料。刪除讀回確認後才送原有空狀態通知。
沒有把區塊未載入當成空氣，沒有取消作者的正常破壞，也沒有新增玩家提示。

本修補沒有聲稱跨包 script-event 通知具有原子提交；實際作者端收到通知的時序仍需同候選原生驗證。

## 菜餚出料與持久確認

自有 [`host_api/cuisine_api_host.js`](../../projects/grilling/gameplay_core/behavior_pack/scripts/host_api/cuisine_api_host.js)
仍由現有 Cookery host extension 複製、由作者實際取菜／拆鍋 hook 呼叫。
它不因模組檔案存在便自動成為普通未擴充 Cookery 的生產回呼。

G119 的來源風險有三個：prepared receipt 和批次序號寫入後未讀回；撤回物品未確認實際移除就標成
`rolled_back`；prepared 重試可能把另一位領料者同編號的 slot 當成原收貨證據。
現在 prepared receipt 與 batch 序號先確認保存，才准許 output 寫入／spawn。
原收貨者或原方塊容器身份必須相符，才能用該 caller 的 container 重讀 prepared output。
slot 撤回會保留已換成其他內容的位置；掉落撤回則先有確實存在的 entity handle，之後確認該 entity 已移除。
撤回不明保留 `quarantined`，不把下一次呼叫當成可再發一份。

已確認物品交付後，terminal receipt 保存失敗仍回傳成功並標 `recoveryPending`；
持久 prepared guard 保留，不能把此狀態當作「沒給物品」。新交付結果不明時，不退回該次已扣 carrier。
新版成本入口在已有 committed／prepared／quarantined output 時不先扣另一個 carrier；
沿用舊 capture 呼叫的相容路徑，則只在確認該次扣除仍由自己持有時補償。

### 保存格式與兩條路徑

公開 `cookery_output_ready` 通知仍為 version 2，metadata／target 格式保持。
現有 `senluo:cuisine_output:<station>:<operationId>` key 與 `api:2` 保存格式保留，
新寫入額外標記 `settlementVersion:1` 與 `kind`。
只有帶此標記的 `rolled_back` 才代表新版本已確認撤回，可以重試同一操作。
既有 committed 收據继续承認其已交付數量；舊版未經 readback 的 rolled_back 不被升格為已證實撤回。
損壞或無法確認的保存資料維持隔離，未清除重發。

| 保存層 | 身份與用途 |
| --- | --- |
| 取出某一份 | `pot:<epoch>:<當時剩餘數>`；重播只承認原已交付份數。 |
| 拆鍋輸出 | 沿用 `break:pot:<epoch>:<當時剩餘數>`；先扣除同份數取出收據已確認的 credit，只交付未給出的餘量。 |
| 整批拆鍋 fence | 新 `senluo:cuisine_recovery:<station>:pot:<epoch>`，version 1；保存原份數、確定餘量、原 break operationId 與當次 metadata。先讀回確認此 fence，才准許拆鍋出料。 |
| 木炭交付 | `burnt:pot:<epoch>`；空手取出與拆鍋共用同一筆 plain receipt，包含 `kind:burnt`，沒有食物 metadata 或食物完成通知。 |
| 容器成本 | 新 `senluo:cuisine_carrier:<playerId>`，version 1；連到確定的 output receipt key，保存扣除前／後的公開 fingerprint 與準備、已扣、已付或撤回階段。 |

拆鍋開始後，普通取出會拒絕**整個同 epoch**，不只拒絕原本那個份數 key。
因此作者 `save` 沒有存妥而遺留舊資料，或舊資料在同座標的新鍋被讀到，不能改用另一個份數再領。
餘量為零仍保存整批已關閉的 fence；真正由 `nextCuisineBatch` 產生的新 epoch 可正常使用。
已存在的 G119 break 收據按 1–64 個有界份數 key 檢查並採納：有效 committed 關閉該 epoch，
其他未確認結果隔離。舊收據本身不重寫，也不掃描整個世界的方塊。

拆鍋重試使用 fence 原本的 operationId／餘量，不重新計算成另一筆 credit。
若 exact break receipt 已 committed，僅補 terminal fence，不再 spawn。
若已確認 rolled_back，允許同一次拆鍋操作重投；prepared／quarantined 未確認的交付仍保留。
相同 epoch 不會退回普通取出以繞過這個 guard。
既存 fence 為 `null`、`false`、數字、陣列或不明形狀時均拒絕；只有 property 不存在才代表未開始。

例如原保存 3 份、其中 1 份已取出而作者 count 還是 3，拆鍋只再交付 2 份。
若原保存 1 份且已全部取出，拆鍋交付 0 份並仍關閉該 epoch。
沒有把舊世界資料換成新的隨機 operationId，也沒有刪除未知份數。

### 容器扣除與重試

原始 `beginCuisineCarrier → 作者 consume → give` 只捕獲成本前像，作者的扣除可能未生效或在 give 前拋錯。
新的 `consumeCuisineCarrier` 取代炒鍋、湯鍋各一個精確 consume 錨點，仍使用作者已判斷的 carrier ID；
Creative 保持不扣容器。原 `beginCuisineCarrier` 函式保留 capture 回傳；沒有 operation identity 的舊 capture 不會被其他 give 當作可退款的 pending 成本。
所有成本結算必須同時符合 owner 和 exact output receipt key；不需 carrier 的另一批菜不能領走前一批已支付／未知成本。

新的 survival 成本順序為：取得真實主手 clone 和預期 after → prepared journal 讀回 → setItem →
實際主手 readback → debited journal 讀回。原生 setter 在實際扣除後拋錯時，after 讀回相符即承認該扣除，
不再扣第二次。任一步未確認均不進入 give；helper 自己處理補償，不把 orphan capture 留給下一次無關互動。
補償僅接受槽位仍等於這次 before，或確實等於這次 after；槽位已換成其他內容便保留，不能無條件覆寫。

確認輸出交付後成本標 committed。新交付結果不明時成本標 quarantined，不能把可能已存在的食物視為零交付而退碗。
已確認的成本撤回標 rolled_back，下一次可重做同一份數。已知成功或撤回但 terminal journal 存不妥时，
同一執行階段保留實際確認結果，下一次可只補存此結果；不需要再扣或再退一次。
重啟後若只剩 prepared／debited／quarantined，則拒絕該 owner 的新成本，保留原 source receipt 與數量供實際保存層核查。
沒有把未知當作零成本，也沒有猜測或序列化重建帶任意 NBT 的原容器來自動退款。
這是保留待恢復狀態，仍需要同候選原生保存演練及遇到不明終局時的核查。

### 木炭轉換與交付

`prepareCuisineBurn` 在作者 `burnWok` 清除 result 前執行。它檢查相同 epoch 的拆鍋 fence、木炭 receipt、
以及當前剩餘數的 takeout receipt。當前份數已有 credit 或未知交付，拒絕把未扣妥的旧 result 轉成木炭；
不按成品份數猜測木炭數量或替作者隨機規則換算法。
正常已保存的部分取菜則會留下較小 count，仍可按作者規則燒焦其真正剩餘狀態。

對尚未完成就燒焦、原本沒有 output epoch 的 active batch，先保留一個讀回確認的 batch 序號，
再透過窄 `{save,raw}` host callback 保存 epoch 和 `grillingBurnOrigin`。
新 active 必須在實際保存中也無 result／burnt／origin、且 started、recipe result 和非空材料清單相符，
才先取得新 epoch；同位置較早的 legacy fence 不會永久封鎖新材料。已有成品或 burnt 的 legacy 資料仍先核對舊收據，不能換身份繞過。後者 version 1 記錄原 result ID／count；
active ingredients 記錄空 ID／0。只有原作者 property 的精確 JSON 讀回相符，才讓原 burnWok 繼續清 result，
作者的 `burntCharcoalCount`、隨機抽樣、聲效和顯示邏輯保持。
此處只固定 origin：若原作者最後保存 burnt／charcoalCount 被吞掉，下一 tick 仍可能對同 epoch 重抽，
當時尚未交付木炭；本輪沒有宣稱 RNG 結果單次持久提交或任意 crash 原子性。
身份寫入失敗時不交付，已寫入但回傳失敗時用 actual readback 辨識，避免重新建立可領取的身份。

空手取木炭與拆鍋改用相同 `burnt:pot:<epoch>` 收據。木炭走 plain output：
沒有 public food、熱度 lore、nativeVariant 裝飾或 `cookery_output_ready` 食物通知。
一條路已交付，另一條只承認其收據，不再次 spawn；相同 epoch 的舊食物 result 也不能繞過已存在的木炭 receipt 再領菜。

舊 burnt 存檔沒有 origin 時，不能重建早已清除的 result 或推算木炭 RNG。
若該 epoch 的 1–64 個份數 key 有已付／未知的食物收據，保留舊 burnt 資料而不猜發木炭；
沒有這類衝突才用 actual save/readback 採納新 origin。原始無收據的歷史交付沒有可驗證證據，
不聲稱能事後證明過去是否曾領取。新版本不刪除這些原始資料。

### 精確 hook 與仍保留的範圍

自有 host extension 升為 `family-api-0.2.7`。保留原作者 UUID／1.6.0 版本、原 archive 與八個原檔 hashes；
只更新短 import／consume、burn、charcoal／recover 錨點及相應 patched hash，自有 copies 仍為八個。
新增 GameMode import 補既有 heat CI loader 的 binding，既有 storage Item double 補 stackability 方法以保留原撤回斷言；三個既有 version verifier 加入 G120 條件，保留歷史斷言。
沒有將完整作者腳本或完整包放進本倉庫。後续其他独立 host adapter 整合須重新計算同一份規格的 patched hash。

持久收據及正常 output readback 的 fingerprint 明確只涵蓋 **ID、數量、名稱、raw lore**，不是任意 NBT 的完整證明。
具破壞性的 slot／entity 撤回與 carrier 寫回另用 native `isStackableWith` 檢查 custom data／properties；
先確認 expected 自身可堆疊再比較實際 stack，非堆疊項目或 API 不可讀屬 unknown，保留而不刪／覆寫。
正常成本／output ACK 若 native 明確證實不同也拒絕；只有 native 比較未知但公開欄位一致時保留有限 fallback。
這個三態保護不被誤用成所有正常食物、尤其 native stew 的全域可堆疊要求；持久 prepared replay 仍只用保存的公開 fingerprint。
API 仍 clone 真正 output，public `nativeVariant` 保持；不以同名新建物品覆蓋 caller 提供的 nativeStack。
上述修補覆蓋已確認的正常 food 出料、容器成本、燒焦轉換與木炭交付入口；
不能推成所有原料加入／取回、所有機器、所有不明舊保存、所有任意 NBT 的全局守恆已驗收。

## 仍未實作的宿主與自然取得能力

| 項目 | 精確現況與可行下一個入口 |
| --- | --- |
| 砧板牛肉／雞皮 | 目前自有 Board API 的 replace／supplement 配方與 4 刀後取出契約存在；兩個維護分支的來源一致。仍需實際 Cookery 1.6.0 host 回呼正常運作的原生取得證據。accepted 註冊不代表已由玩家取得。 |
| Java `flex_pot` 三菜 | 來源 `common/.../recipe/flex_pot` 與 Forge `recipes/flex_pot` 各有雞翅、青椒魷魚、魚腥草炒肉，`stir_fry_count:3`、`time:200`。現有 Grilling 只發送 exact `wok` 資料。Cookery 1.6.0 `normalizeWok` 把 stirs 固定為 1，`wokRecipe` 走 exact／整份 batching，沒有 `wok_flex` 能力。不能把較短 ingredients 陣列當成 Java flex-set matcher。本輪追加審查已核對 Java Cookery matcher、兩種serializer預設、全部料理階段與品質：[完整來源及六步規格](cookery-flex-pot-lifecycle-20261009.md)。既有6／5／6 exact配方有原作依據；兩條路都需完整備料／三翻／品質及保存接線，不能只加註冊或改stirs。World.seed已可讀，這是尚未實作的自有adapter與遷移缺口，不是平台永久限制。 |
| 下界要塞箱子 | 兩分支 `world/FortressHouttuyniaHandler.java` 的 65% pool、1–2 rolls、每 roll 1–3 魚腥草，已有現行 loot wrapper 對照；未另加猜測掉落。自然箱子／真世界取得未由 source 檢查認證。 |
| 自然要塞疣 25% 替換 | 兩分支 `world/FortressWartReplacementHandler.java` 依 `ChunkEvent.Load.isNewChunk` 及真正 fortress bounds 排程。現行 fresh_fortress 接口的 signed-long hash／年齡規則存在，但沒有安裝作者的權威新區塊回呼。官方 loot generator 和結構查詢都不能證明是新生成區塊；不掃描舊農場猜測或替換。 |
| 原生熔爐／煙燻爐與其他 producer | 現有 prepare/decorate 契約仍須真正製作／取料回呼提供 output。容器關閉、背包增加或查詢 loot 不是等價生產收據。 |

## 驗證範圍

本機只做相關 Java／作者原檔來源核對、JSON/short-hook 檢查和 JavaScript 語法檢查。
在既有 `test_family_oil_food_api.mjs` 加入具體 receipt 故障／份數、plain 木炭及 burn origin 保存回歸，沿用 storage-only adapter，
沒有建立 Player 或新增玩家互動模擬；這些回歸留給候選必要 CI，未在本機執行整條歷史套件。
語法、source 檢查和 required CI 都不能接受正常真人取菜、自然要塞、完整 C/D 或 LIVE。

完整家族必須安裝本候選自有 host modules，通過該候選的 static／BDS／停服存檔演練與准入，
才可把本輪來源修補列成部署。保留 `client=false`、`production_ready=false`。
