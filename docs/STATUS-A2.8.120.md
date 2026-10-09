# G120：持久保命記錄、瓜梗與料理出料守恆

2026-10-09（香港）。本版繼續已合併 G119
`b010ec2a6709ada74ed96ead19c60da4e0bc2789` 的剩餘缺口。
包、模組和自有 BP/RP 配對版本為 **2.8.120**，指南為 **0.3.50**。
維持 UUID、作者 Cookery **1.6.0**、server **2.9.0**／server-ui **2.2.0**，
自有 family API 升至 **0.2.7**。來源直接進入 canonical BP/RP，封裝不注入另一份玩法。

## 本版修補與證據範圍

| 工作線 | 已確認的問題 | 本版來源修補 | 尚須的原生證據 |
| --- | --- | --- | --- |
| 重金屬 | G119 的防重複結算 map 在 logout／script reload 後消失，未完成或未知效果提交可能再次取消致命傷害。 | 在取消之前保存具名效果 claim 並確認讀回；同一 until／amp 跨 session 保持隔離，舊 callback 不能重入。 | 實際 before-hurt、正常重登／重载、存檔重啟、吸收與圖騰／死亡順序。 |
| 植物 | 西瓜梗、南瓜梗、纏根土及兩種下界藤沒有自己的油渣 handler。 | 支援總數 18→23；補成熟當次結瓜條件、RNG、土地／鄰株和根下空間，以及下界藤沿相連末端兩次延長的規劃與回滾。 | 日夜／天氣光照、附著梗與果實的鄰居更新、失敗回滾後世界狀態。 |
| 料理工作站 | 後續取消破壞／爆炸仍可清除油及調味資料；出料確認與取出／拆鍋之間的記錄不完整。 | 補最終取消判定、原站點和 metadata 前像；prepared／terminal 寫入及交付撤回均需實際確認，份數交付與拆鍋共用防重發邊界。 | 作者宿主的真正操作／保存回呼、交付後重啟和取消事件時序。 |

三條工作線使用独立工作樹；重金屬和料理交易另有跨代理唯讀覆核。
程式審查、API declarations、純資料檢查、CI 與資產生成均不代替原生／真人接受。

## 重金屬：先保存，再取消

新增 `heavy_metal_claim_core.js`，使用實體自己持有的
`kaleidoscope_grilling:heavy_metal_claim`。保存格式固定為
`{version:1, until, amp, time}`；原 FX 欄位與 main 的唯一 before-hurt 接線不變。
只有實際 `undefined` 表示無記錄，讀失敗、未知版本、損壞或非有限資料都不能授權救援。

流程先讀實際 FX 和 claim，比較 claim 原始值，保存新記錄並直接讀回，
再排程、設置與確認 `event.cancel`。排程入隊後拋錯會撤銷 exact token；
只有取消明確為 false，才可以恢復本次記錄的精確前像。取消未知時保留隔離。
延後回呼還須持有同一 map token、pending 階段和完全相同的 raw claim，
才進入 G119 的 fresh FX 比較、一次效果寫入、HP=1 讀回與聲音路徑。

logout、death、entityRemove 和 respawn 只撤銷記憶體 callback，
不删除持久記錄，不透過已失效 entity handle 清理保存。
同一 until／amp 不能因重新登入或時間回退再得到救援；新不同描述可重新比較並替換。
正常登入與既有 expiry pruning 不會重寫 until。

此次精讀[固定 Mojang 2.9.0 bindings][sdk]，發現 Entity／World 的
`setDynamicProperty`、`setDynamicProperties` 明列 `restricted_execution`，
與只允許 `default` 的 Entity `setProperty` 不同。
因此不能沿用「before-event 一概不能寫 dynamic property」的概括判斷。
主控独立取得原始固定檔並確認宣告；health／sound 仍延後執行。

API 讀回不是磁碟 flush 收據。本版不承諾斷電／world-save crash 原子性；
claim 已保存而操作中斷時，可能保守保留尚未使用或尚未完成結算的記錄。
不自動重播傷害、补血或猜測中毒已提交。外來同字移除再授予效果仍無法辨識成新 generation。
完整細節見[效果與 API 證據](evidence/heavy-metal-and-inventory-api-20261009.md)。

## 瓜梗、纏根土與下界藤

西瓜／南瓜梗只接受未附著的 growth 0–6。每次增長 2–5，最多到 7；
**只有該次剛成熟才執行 randomTick 的結瓜路徑**。
已成熟梗不能反覆施肥抽果。光照門檻為 9，3×3 乾濕耕地、中心與周邊權重、
同類未附著鄰株懲罰和抽樣順序都對照原作。命中後只抽一次北／東／南／西；
被擋不重抽，空位下方須符合原版 dirt 集合或 farmland。

實際 SDK 提供 total brightness 和 sky brightness；本版以 `max(total, sky)`
適配 Java `getRawBrightness(pos,0)` 保留原始天空光的語義。
這是來源推導的有限適配，尚未證明所有日夜／天氣／維度下逐值等價。
兩個讀值各自保存、各自重驗，缺失、未載入或超界時停止規劃，不猜光照、不扣料。

成功結瓜先寫果實，再寫附著梗；其他 handler 的寫入順序不變。
纏根土只在正下方明確是空氣時長一格懸根，第二次作用看見已有根便無效。
所有讀過的鄰位和寫入位置納入原 journal，保留兩次作用／一次油渣、Creative 免費、
完整手持資料、寫入確認、逆序回滾與未知結果隔離。

[植物增量證據](evidence/stem-and-rooted-dirt-fertilizer-20261009.md)列出
兩版 Java 原始方法、Bedrock ID／狀態映射、光照推論及引擎鄰居更新的剩餘範圍。
兩種下界藤沿相連同 ID 尋找末端：扭曲藤向上、垂淚藤向下，只向空氣生長。
每次先按 Java 的 1、逐次乘 0.826 抽完整長度，再依序放置；不以自然生長的 age25 停止条件限制骨粉。
第二次油渣仍從原點出發，沿 journal 第一次生長後的虛擬鏈尋新末端。所有鏈節與障礙都重驗，
未知 chunk／超界拒絕整筆，沒有猜空氣或提交半套結果。
[下界藤增量及海帶邊界](evidence/nether-vine-fertilizer-20261009.md)列明兩版 head／body 原始方法和完整 age 映射。

甜菜中間年齡、竹子停止階段、其他 feature 植物及外部 tags 沒有猜測補齊。
海帶骨粉每次延長一格的來源已確定，但現有 journal 尚無原水位／流態／液體層的完整回復契約，因此未註冊。

## 料理：取消、交付與同批次防重複

工作站破壞與爆炸不再直接排程刪除調味／油資料。回呼先確認最終取消值，
再確認位置可讀、原工作站確實消失、沒有替換成另一工作站、原 metadata 尚未變更。
任何一項無法確認就保留，刪除後也需讀回確認，才送原有的空狀態通知。
這個檢查不宣稱跨包 script-event 與原宿主保存具有原子性。

菜餚出料先保存 prepared 收據和批次序號並讀回，才放入容器或產生掉落物。
重試只能以原領料者或原方塊容器確認交付，不能借用另一玩家同編號的格子。
撤回亦需確認實際移除；位置已換成其他物品或掉落結果未知時保留隔離。
物品已確認交付、最終收據保存失敗時，保留 prepared 記錄並標記待恢復，不能退回並重發。

取出和拆鍋共用同一料理批次的交付邊界。如果原保存仍寫 3 份，但其中 1 份已確認交付，
拆鍋最多只交付剩餘 2 份。拆鍋前還須保存整批關閉記錄；原宿主清空保存失敗後，
普通取出不能改用另一個份數 key 再領一次，零剩餘也會關閉批次。
真正的新批次使用新的 epoch。G119 舊收據保留，其已確認交付可採納；
旧版未讀回的 rolled_back 不升格成確定撤回，損壞或未知保存不視為不存在。

炒鍋與湯鍋扣容器改用自有 acknowledged helper：先保存成本記錄，再扣主手並讀回，
確認後才出料。Creative 免扣。每次成本同時綁定玩家與完整 output receipt key；
另一筆操作不能退還前次已付容器。補償只改回仍屬於本次的格子，未知交付保留成本。
重啟後若只剩未結案成本，拒絕該 owner 的新扣除，保留原收據供核查。

燒焦前先保存原菜品／批次身份，拒絕把已領但尚未扣妥份數的舊成品再換成木炭。
空手取炭和拆鍋共用 `burnt:pot:<epoch>`，一條已給出，另一條只承認收據。
木炭維持普通物品，不附帶熱食資料或食物完成通知。真正的新 active 材料可建立新 epoch，
但必須與作者實際保存的 recipe／材料相符；完成或已燒焦的 legacy 資料不能改身份繞過。
本次固定的是 burn origin；作者最後 burnt／charcoalCount 保存失敗而尚未交付時仍可能重抽 RNG。

現有持久交付指紋涵蓋 ID、數量、名稱和 raw lore；它不是任意 ItemStack NBT 的完整證明。
撤回／退款等破壞性操作另要求實際可自我堆疊的 native clone 比較為相同；
不同或未知均不刪除／覆寫。正常 ACK 亦拒絕 native 明確不同，無法比較的非堆疊物品則保留有限公開欄位確認。
來源守恆修補亦不等於 world-save crash 原子性或作者生產回呼已通過原生驗收。
逐路徑證據及正常取得缺口見[料理生產與取得記錄](evidence/cookery-production-acquisition-20261009.md)。

## 炒鍋原作對照：已查清但尚未接入的完整流程

本輪另追到 Java Cookery 的實際 recipe serializer、PotBlockEntity、品質評估與食物讀取。
現行三道料理的 6／5／6 格固定食材不是憑空配方：原作也有對應 exact pot 配方，
它們與 flex 配方並存，exact 優先。問題是两者原作預設都要三次翻炒，
並由第一下鍋鏟啟動 200 tick 烹調；現在作者宿主的計時／翻炒流程沒有還原這段生命週期。

Flex 匹配還須依 Item 身分去重，再做 padded exact matching；不能依重複整組食材放大產量。
品質另依原世界 seed、recipe ID 和比例向量，沿保存資料影響實際營養。
**World.seed 已存在於精確 server 2.9.0，不能再把讀不到種子列成平台限制。**
目前真正缺少的是備料起時計時、輸入鎖定、烹調階段與翻炒餘量、保存／出料所有權，
以及品質從成品到實際食用的完整接線。這是尚待實作的來源缺口，不能改稱只缺真人驗收。

本版沒有註冊未接好生命週期的 `wok_flex`，沒有把 `stirs` 單改成 3，
也沒有以任意 seed／中性品質填補。後續須把完整炒鍋狀態與品質作同一份可遷移候選，
連同 exact recipe 優先、未結案料理守恆和既有食用單次結算一起核對。
完整原作方法、六個實作階段與舊批次遷移限制見[炒鍋來源與後續規格](evidence/cookery-flex-pot-lifecycle-20261009.md)。

## 版本、指南與來源檢查

指南維持 Cookery 原書內的一個煙火入口、6 個根類和 8 個子類。
僅油渣頁的第 3 段及新增第 8 段改變；三語皆同步，其他名稱、alias 和指南正文保持。
76 個條目、95 個配方、69 個圖示；payload 為 235 個傳輸 chunks。
遊戲指南說明操作，不加入儲存協定或偽裝成已驗收的提示。
三語第 3／8 段的精確前後像鎖定在[已公開來源提交](https://github.com/casama233/kaleidoscope-grilling-unofficial/commit/187e179d58f48fbc9b4d57b5f01cff90b7489ee6)，
歷史 source refs 增至 24 個；G118／G119 指南前像與原名稱／alias 護欄保留。

既有完整案例仍由必要 CI 執行。本機沒有新增／執行模擬玩家互動，沒有跑整條歷史 verifier。
本機針對純 claim 資料、Java／SDK／state、語法、指南序列化及來源保護做檢查。
兩個 Heavy Metal 相關既有測試只接入新 codec／独立 claim 儲存；原情境、FX 故障注入和 assertions 保留。

另修正 current verifier 的來源 session 選擇：G117 以後的 wrapper 已支援原有四組成功命令重用，
但 current 入口仍只列 G114–G116。本版將 G117–G120 接入同一份收據包圍的 session，
不跨候選快取、不重用失敗、不刪除必要案例；歷史 standalone 驗證保持原行為。
既有兩項純 session 檢查通過。PR 的完整必要 CI、Dash 編譯、精確輸出及 main 發布結果各自記錄。

## 原作與宿主版本

本輪再讀作者 main，仍為 [1.1.1／9a1acdab][java]；
[Forge 1.20.1／8726006][forge] 與 [NeoForge 1.21.1／8726014][neo] 未發現較新維護版。
Cookery 作者頁仍以[Bedrock 1.6.0][cookery]為目前正式版。
家族 `family/java-upstream.json` 已唯讀核對，其中 Grilling 描述仍停在 G117，
不能作本版交付或實測收據；本輪沒有改寫其他倉庫。

## 尚未閉合，以及下一個所需條件

| 範圍 | 下一個具體條件 |
| --- | --- |
| 手持／放置餐盤、牆上串譜、食用聲畫 | 本版原生載入，以及 Windows／手機左右手、第一／第三人稱、切槽、重登、旁觀者與 FOV 對照。 |
| 任意秘製串背包圖示 | 真正受支持的每 ItemStack 三槽顏色／形狀／variant 到 inventory renderer 通道；目前仍是 static fallback。 |
| 食用取消與離線 | direct leave、缺省／0 counter、shutdown/crash 和真實原生事件順序；不以世界 tick 猜測玩家實際 use counter。 |
| 通用植物 | 甜菜年齡、竹子 stop stage、海帶液體層回復、其他 feature 與外部植物的個別規則或可驗證原生橋接。 |
| 重金屬完整等價 | 剩餘 absorption、最終死亡／圖騰判定、event 35 畫面，以及持久 claim 的實機保存證據。 |
| 完整炒鍋／料理品質 | 完整備料和烹調時鐘、三次翻炒、輸入鎖定、flex／exact 優先、品質保存與實際食用；目前仍為未實作來源缺口。 |
| 正常生產／天然取得 | 真實 Cookery 生產回呼、全新要塞／區塊的 generation 入口；accepted 註冊不是正常取得成功。 |
| 家族與 LIVE | 本候選的整套 static、BDS 首次／重啟、fresh 停服存檔演練、備份、准入與逐檔部署讀回。 |

本輪工具没有受管 BSM／luosen 能力，手冊所列伺服器路徑不存在，也沒有當前世界、
`senluo-java-upstream-status.json` 或本候選家族收據可用。
不能沿用 G114 的世界觀察、G119 的發布或他版收據作 G120 的原生／LIVE 接受。
持續部署授權仍有效；入口恢復後沿 canonical family 更新、備份、演練和准入續行。
維持 **client=false、production_ready=false**；本頁不宣稱已更新 LIVE 或全部一比一。

[sdk]: https://github.com/Mojang/bedrock-samples/blob/46ba6ea985fb5a92d79a9419198f10dda14c199d/metadata/script_modules/%40minecraft/server-bindings_2.9.0.json
[java]: https://github.com/breezeth-CN/KaleidoscopeGrilling/tree/9a1acdab27698457bec16c9362678e574895a28c
[forge]: https://www.curseforge.com/minecraft/mc-mods/kaleidoscope-grilling/files/8726006
[neo]: https://www.curseforge.com/minecraft/mc-mods/kaleidoscope-grilling/files/8726014
[cookery]: https://www.curseforge.com/minecraft-bedrock/addons/kaleidoscope-cookery-unofficial
