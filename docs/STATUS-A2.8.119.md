# G119：手持餐盤、植物適配與重金屬提交

2026-10-09（香港；UTC 2026-10-08）。本版從已合併的 G118
`f7bd2d26367c113ab8881bc67e9f5e69624917ff` 繼續修補剩餘來源差異。
包、模組及自有 BP/RP 配對版本為 **2.8.119**，指南資料為 **0.3.49**。
UUID、作者 Cookery 1.6.0、server 2.9.0／server-ui 2.2.0 沿用現行契約。
所有程式及模型均進入 canonical BP/RP，封裝不另注入玩法。

本輪重新取得作者原碼 [`9a1acdab27698457bec16c9362678e574895a28c`](https://github.com/breezeth-CN/KaleidoscopeGrilling/tree/9a1acdab27698457bec16c9362678e574895a28c)，
並核對 [CurseForge 專案](https://www.curseforge.com/minecraft/mc-mods/kaleidoscope-grilling)：
維護中的 [Forge 1.20.1](https://www.curseforge.com/minecraft/mc-mods/kaleidoscope-grilling/files/8726006)
及 [NeoForge 1.21.1](https://www.curseforge.com/minecraft/mc-mods/kaleidoscope-grilling/files/8726014)
仍為作者 1.1.1。本版主要玩法對照維持 NeoForge 1.21.1；下述甜莓副手入口的 Forge 差異另列。
家族 `java-upstream.json` 已唯讀核對；其 Grilling 敘述仍停在 G117，不能代替本倉庫 G118/G119 的交付紀錄。

## 這次實際完成的來源工作

| 工作線 | 原缺口或缺陷 | G119 的實作 |
| --- | --- | --- |
| 手持餐盤 | 現行只有放置盤顯示；歷史手持原型的 count／大整數解碼故障未入有效主線。 | 新建手持盤 attachable、geometry、animation、render controller 及保存內容讀取器；1–5 份各自投影，份數獨立傳送。 |
| 原版植物 | G118 僅有 8 個明列植物入口；通用骨粉 API 未成立。 | 新增 10 個有 Java 方法與 Bedrock 狀態依據的入口，保留兩次作用／一次扣費，包含掉落與雙高植物交易。 |
| 重金屬 | 延後結算分別 clear/set，錯誤被舊 wrapper 吞掉，仍可能改 HP／播聲；排程失敗會留下預留。 | 成功排程後才取消傷害；一次提交移除重金屬與加入中毒，驗實際前像與讀回後才改 HP／播聲，未知結果保留防重入狀態。 |
| 原生能力重查 | 任意三食材 inventory icon、剩餘吸收值及最終死亡／圖騰事件仍缺可靠入口。 | 重新核對精確穩定 bindings／schema，更新證據與指南限制；沒有把能力調查列成已修復功能。 |

三位代理使用獨立工作樹實作；主控負責 main 接線、來源保護、指南、版本與整合。
手持通道及矩陣另有獨立代理覆核。這些都是來源層工作，沒有把代數、資產生成或 CI 稱作原生／真人接受。

## 手持餐盤的完整來源鏈

`main.js` 載入 `plate_held_visual_runtime.js`，直接讀取餐盤保存的 envelope。
現在的 `captureSkewerMetadata` 已把物品資料展開到 `row.native.props`，因此顯示讀取不需要重新建造
暫存 ItemStack，也不會為每次刷新寫入新的內容位址資料。舊資料的 `row.props` 路徑保留。
固定生／熟串、普通串及秘製串使用現行模型／palette；不支援的外部模型保留原槽位及完整保存資料，畫面留空。
損壞或不完整內容不偽装成另一種食物。

玩家目前已使用全部 32 個 entity properties。每一隻手只可能持有一種類型，
所以既有秘製串、調料瓶與新餐盤共用該手原有的 12 個**顯示**欄位，權威物品不借用這些欄位保存。

| 每手既有欄位 | 手持盤用途 |
| --- | --- |
| `bottle_*_0` 至 `bottle_*_7` | 前四份食物，每份兩個整數 word。 |
| `secret_*_0`、`secret_*_1` | 第五份食物的兩個 word。 |
| `secret_*_2` | 獨立份數 0–5。 |
| `secret_*_piece` | owner／有效標記：餐盤 255、瓶子 214、更新中 254；秘製串原 helper 索引 0–213 保留。 |

`held_visual_transport.js` 是每玩家／每手的唯一 writer 與 cache。
切換餐盤→原來的同一瓶或秘製串，也必須以新 owner 重寫，不能由分散 cache 當成沒有变化。
提交先把標記設為無效，再寫內容，最後發 owner；失敗會丟棄 cache，下一次完整重送。
spawn／leave 清理衍生狀態；來源讀取錯誤只隔離該手。
這個順序不等於已證明客戶端會把多個 property 在同一幀原子呈現。

秘製串每份三個 cell 採兩個有界 word：

```
A = v0 + 8192 × (v1 % 64)
B = 1 + floor(v1 / 64) + 128 × v2
```

cell 沿用現行 0–5333 編碼；A 最大 521429，B 最大 682708。
解碼以 8192、128、256 等 2 的冪次取出欄位，沒有重建成一個超大整数，
份數也不從食物 word 中相除取得。固定模型使用 B=0，秘製串使用 B≥1。
shape／style 改用小整數比較選取；食材、palette、模型陣列索引都有邊界。
這避開歷史 radix/count 共字的來源風險，仍需同候選客戶端確認實際同步與呈現。

`held_visual_dispatch_runtime.js` 合併既有事件與五 tick 輪詢；秘製串保持二十 tick 回退週期。
相對週期不假定載入時的世界 tick 餘數為零；排程拋錯會撤銷 token，佇列仍可由下一次事件或五 tick 回退恢復。
新手持路徑不生成 helper entity、不增加 PNG，也不增加玩家 property。

### 模型與姿態

`tools/build_plate_held.py` 讀取當前 canonical grill mesh、普通串及秘製串模型，產生四個指定資產。
Java 手持與放置盤共用 1–5 份布局，但**手持 renderer 沒有放置盤額外的 Z +180°**。
其 FIXED 內層約成 `T(0,1.8,1.8) Rz(-180) S(1.2)`，因此使用獨立手持動畫。

座標轉換沿用目前已釘選的 hand basis：body／ordinary 轉換一次 +24；
grill 先撤銷既有 sourceY−1，再轉換到同一基底；秘製串使用原有 `held=True` 轉換。
沒有在動畫或每個子骨骼再加一個猜測偏移。
一個滿盤秘製串最多選中 21 個 render passes；這是路由數量，不是手機 GPU／多人效能合格證明。
第一／第三人稱、左右手、FOV、光照、遮擋和皮膚仍需原生及真人逐項對照。

## 植物從 8 個入口擴充至 18 個

原有油菜、洋蔥、番薯、魚腥草、花椒苗、小麥、胡蘿蔔、馬鈴薯保留。
新增項目及其精確方法、版本、下載來源、狀態映射見
[原版植物取證](evidence/vanilla-plant-fertilizer.md)。

| 新增植物 | 單次作用／兩次油渣的關鍵行為 |
| --- | --- |
| 可可 | 每次加一階，到 age 2；保留方向。 |
| 甜莓 | 每次加一階，到 growth 3；只在初始入口處理採果、潛行與主副手優先序，第二次不變成採果。 |
| 粉紅花簇 | 未滿增加一份；滿時每次掉一份。已滿時一次油渣規劃兩次獨立掉落。 |
| 無果洞穴藤 | 按已載入下鄰判斷 head／body，生成發光莓；不延長藤蔓。 |
| 向日葵、紫丁香、玫瑰叢、牡丹 | 完整上下半任一半可用；每次掉同種花一朵，油渣共兩朵。 |
| 短草、蕨 | 有正確土壤及上方空氣才變双高草／大蕨；上方被堵而未生長仍屬有效消耗。 |

Java 的兩次 `super.useOn` 只要任何一次 consumesAction，生存合計消耗一顆油渣；Creative 不消耗。
`doTileDrops=false` 時花卉不掉物，仍算有效作用。不能把「有效但沒長／沒掉」當成「無效」退料。

甜莓主要按 NeoForge 1.21.1：非潛行主手對初始 age 2／3 保留原生採果；
潛行或實際副手 item-use 可對 age 2 施肥。Forge 1.20.1 的非潛行副手區塊採果呼叫不同，
本版沒有把兩個分支稱成完全同義。Bedrock 的整套主副手輸入選擇仍需原生確認。

journal 同時記錄被讀取但未改動的鄰位、目標與實際寫入位置，第一次扣料前驗完整手持、潛行狀態及 permutation。
新增掉落須有有效 entity handle 與實際物品讀回；回滾須確認該 entity 已移除。
未知掉落／移除或回滾失敗會隔離整個參與集合，不能換雙高花的另一半繼續重複產出。
這是同步交易保護；未知交付、進程崩潰與已隔離資料仍須依實際世界恢復。

甜菜的 Bedrock 中間年齡、瓜梗成熟當次 randomTick／結果、竹子停止生長 stage，
以及其他樹苗／蘑菇／海帶／feature 與外部植物都仍有明確缺口。
`Dimension.placeFeature` 的存在沒有提供通用骨粉規則及完整回滾清單，未用它偽装原作施肥。

## 重金屬的單次確認提交

`heavy_metal_damage_runtime.js` 仍由 main 唯一 before-hurt 訂閱呼叫，
既有彈射閃避、無敵的優先序保持。排程成功前不取消傷害；排程入隊後拋錯的 callback 也會因 token 被撤銷而失效。

延後結算直接重讀有效效果、時鐘與存活生命；`writeEffects(...,{expectedRaw})`
要求實際欄位符合最新前像，在一次寫入中移除重金屬並加入 12000 ticks 中毒，保留其他有效效果。
提交後再直接讀原始欄位，確認沒有重金屬 key 且中毒描述精確相同，才把生命設為 1；生命讀回成立後才播既有聲音。
因此同 tick 的舊 cache 不能冒充這次寫入收據。

已取消傷害而結果不明時，保留相同 until／amp 的 quarantine；不重新播放傷害、不盲目重試寫入。
已提交後的生命或聲音失敗不恢復保命效果；損壞的非有限描述在 admission 就拒絕。
death、entityRemove、leave 和非首次 spawn 都會使舊工作失效。
預留仍只存在於當前 session，跨重新登入／腳本重載及任意崩潰的持久保護尚未閉合。

完整官方 API 核實、Java 兩分支方法及仍缺的 absorption／death／totem 時序見
[重金屬與 inventory API 記錄](evidence/heavy-metal-and-inventory-api-20261009.md)。
原生 event 35 的客戶端動畫也沒有由一個 sound 呼叫變成完全還原。

## 驗證與交付邊界

本輪使用原碼、官方資料／SDK、獨立代數審查、生成一致性、語法與 source conservation 檢查。
沒有新增或在本機執行模擬玩家互動；既有互動回歸保留其 assertions，僅按新的 production 模組路由調整依賴。
兩個純重金屬轉移規則案例分開檢查；它們不建立玩家，也不證明原生傷害時序。

main 的五個窄接線以公開提交
[`1e8011e1f71833739ea12097e80c0f69a21c844e`](https://github.com/casama233/kaleidoscope-grilling-unofficial/commit/1e8011e1f71833739ea12097e80c0f69a21c844e)
的整檔 bytes 為見證；G118 及更早 preimage、原 provenance pack 與舊回歸保持。
修改 fixture hash 不能放行該公開範圍外的 main 變更。
另外五檔 player／secret runtime／secret attachables 的共用通道變更固定在
[`b37ec0d78b75f61e441a97fe31746dab5aac7fef`](https://github.com/casama233/kaleidoscope-grilling-unofficial/commit/b37ec0d78b75f61e441a97fe31746dab5aac7fef)，
逐檔核對原 G69 前像與公開整檔；原始 witness manifest、JSON 及既有 terminal mask 保持原意。
此差異不能擴充到其他檔案，修改本機內容及 fixture hash 仍會被公開來源比對拒絕。

完整必要來源套件由整合 PR 的 canonical CI 執行，成功收據供 pinned Dash 與精確輸出比對重用；
baseline／bridge／family-candidate 關卡保持。實際結果以該候選的 GitHub Checks 與發布紀錄為準，
沒有本機重跑整條歷史驗證鏈，也沒有以同版本更換輸出內容。

### 仍未閉合與下一個所需證據

| 剩餘範圍 | 下一步需要的證據或能力 |
| --- | --- |
| 手持盤／放置盤、牆上串譜及完整進食聲畫 | 同一 G119 的原生載入與 Windows／手機真人對照，含左右手、1–5 份、切槽、重登及旁觀者。 |
| 任意秘製串 inventory icon | 真正把每 ItemStack 的三槽顏色、形狀與 variant 傳到原生 inventory renderer 的受支持通道及客戶端證據；目前仍是 static fallback。 |
| 通用施肥與外部 tags／未知 shape | 各植物的有效性、RNG、狀態／多方塊規則與完整回滾，或可驗證的原生橋接。 |
| 吸收、圖騰與死亡順序 | 可讀剩餘 absorption 或最終 death／totem 判定的原生能力；before-hurt 只能覆蓋目前可確認分支。 |
| Cookery 生產者、天然要塞及其他平台 callback | 真實宿主的 production／generation 回呼，完整依賴及來源版本一致；accepted 註冊不當作正常取得成功。 |
| 存檔／LIVE | 此候選的整套家族 static、BDS 首次／重啟、停服存檔演練、准入及逐檔部署讀回。 |

本輪環境沒有受管 BSM／luosen 入口、當前世界或家族部署收據，不能沿用 G114 的家族收據或 G118 的來源／發布紀錄接受 G119。
因此本頁不宣稱已更新 LIVE、完成 C/D 或全部一比一。
保留 `client=false`、`production_ready=false`，並等待同一候選的原生／真人證據。
現有持續部署授權不變；取得受管入口後按 canonical family update、備份、演練及准入流程續行。
