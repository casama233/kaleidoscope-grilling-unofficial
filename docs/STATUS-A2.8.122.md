# G122：保存炒鍋階段、彈性料理品質與施肥所有權

2026-10-09。這一版接續已合併的 [G121 酒館指南橋接](STATUS-A2.8.121.md)
`2dde8f71d46c9787e2e41b5dd2dc20bc87d6918b`，包與模組版本為 **2.8.122**，
指南 **0.3.52**，自有 family API **0.2.9**。
維持原 UUID、作者 Cookery **1.6.0**、server **2.9.0**／server-ui **2.2.0**。
所有玩法與指南輸出都進 canonical BP/RP，不在封裝時注入另一份實作。

## 版本沿革與 G121 指南橋接

[PR #186](https://github.com/casama233/kaleidoscope-grilling-unofficial/pull/186) 已將 G121 酒館指南共用入口合併主線。
本輪先前公開的機制來源
[`f27d40a7c1bab951398e3fc3d3906bcc416c5c3f`](https://github.com/casama233/kaleidoscope-grilling-unofficial/commit/f27d40a7c1bab951398e3fc3d3906bcc416c5c3f)
是當時尚未合併的機制候選，保留作為來源審查見證；其炒鍋、品質、植物與交易修補現在納入 G122。
正式 G121 的狀態頁與 `release-history.json` 紀錄保持原內容；本版的最終來源身份以 `baseline.json` 及 G122 發版紀錄為準。

G122 保留 G121 的 Cookery 酒館章節交接，由 Tavern 顯示自己的共用指南，其他章節仍走作者介面。
交接按真玩家來源、章節、nonce、語系及期限匹配，先請求、確認再開始；40 tick 未確認便續走原入口。
返回才回到 Cookery 主頁，關閉不重新開窗；離開、過期與重複事件不能重新啟動舊視窗。
這項既有橋接的來源／協定證據保留，G122 的原生 UI、完整家族與真人驗收仍須按本候選取得。

## 本版解決什麼

| 工作線 | G120／G121 沿用的未完成點 | G122 來源實作 | 尚未取得的證據 |
| --- | --- | --- | --- |
| 炒鍋 | 三道 exact 配方存在，但原作備料、第一鏟起算、三翻與完整變質階段未接通。 | 保存 phase／剩餘 tick／剩餘翻炒／epoch；新鍋有 1200 tick 備料、200 tick 烹調、800 tick 成品、400 tick 黑暗料理，再產出一次 1–3 木炭。 | 真宿主操作、保存重啟、熱源與事件順序。 |
| 彈性配方 | 種子可讀，實際 flex producer、品質保存與營養仍缺。 | 三道原作 flex 與 exact 共存，exact 優先；真正作者 registry 接受後才啟用；品質同時進入保存、輸出身份與原生食物值。 | 原生飢餓／飽和、實際食用取消與跨包完成事件。 |
| 成本守恆 | 失敗的 station 回復仍可能退款；未寫入的巧合後像可能被誤認為本次操作。 | 保存與手部寫入記錄實際進入點，先確認站點復原才退本次手部成本；未知所有權保留隔離。 | 世界儲存中斷及其他 pack 同時改寫的原生場景。 |
| 油渣 | 23 類植物，缺紅樹葉／懸掛苗；回滾失敗仍可能退料。 | 增至 25 類；乾燥葉下生苗、乾燥懸掛苗成熟；所有已執行寫入須確認復原才允許退款。 | 原生鄰居更新、水層、實際掉落／拾取與重載。 |

三個代理分工實作，植物代理另唯讀覆核炒鍋回復與出料，品質代理覆核跨模組成品身份。
獨立 Java oracle 是有限原邏輯執行；純資料／儲存檢查與 CI 不代表 BDS 操作或真人接受。
**`client=false`、`production_ready=false`，沒有宣稱全部機制已一比一還原。**

## 炒鍋：新批次的完整有界流程

實作位於 `host_api/pot_api_core.js` 與 `host_api/pot_api_host.js`。
自有 adapter 加在 SHA-256 核對過的 Cookery 1.6.0 原包短掛鉤上；保留八個原檔邊界，
自有模組複製數從 8 增為 12，沒有發布原作者完整宿主檔或改寫其 manifest。
掛鉤、實際 tick、交接和收據的逐項來源見[炒鍋證據](evidence/java-pot-lifecycle-20261009.md)。
公開能力為 `grilling_pot_exact_flex_v1`；三道原配方仍由實際宿主 registry 接受，
不能在註冊未完成時拿本地常數當 accepted。

| 階段 | 來源行為 | 保存／操作限制 |
| --- | --- | --- |
| 備料 | 在有熱源的空鍋加油，開始 1200 tick。加料或取回材料不重新起算。 | 每次讀寫核對原始 station 資料；普通材料最多九份。 |
| 開始烹調 | 有材料時第一鏟啟動 200 tick 並算第一次翻炒；備料歸零也會自動開始。 | exact／flex 原配方需三次翻炒；開始後鎖定普通材料加入與取回，調味沿用原入口。 |
| 完成 | 三翻不足變成作者的可疑炒菜；否則保存選定成品及 flex 品質。 | 一個碗領取一份；品質、熱食、調味隨实际成品保存。 |
| 留鍋 | 完成品再受熱 800 tick 變成黑暗料理，再受熱 400 tick 變木炭。 | 木炭數量先選定並保存，只交付一次，再清鍋；無熱源／未載入不補計經過時間。 |
| 取回／破壞 | 備料可取回最後一份；拆鍋保留未投入烹調的普通材料，完成品走出料收據。 | 原料返還不經「新料理」的延遲背包掃描裝飾；已交付的 operation 不重發。 |

既有 active／result／burnt 鍋保持原宿主流程，直到取完／清空，才開始新的 G122 批次。
不為舊保存捏造已經過多少備料時間，也不把舊鍋正在持有的材料當新投入。
遇到其他作者配方或未審查材料，使用明確 legacy 交接，保留作者 count／time／stirs；
這不是全部 Cookery 菜品的 Java 生命週期適配。

本版普通原料只接收能與同 ID 的普通 `ItemStack` 原生堆疊的物品。
自訂名稱、lore、特殊資料或無法確認的材料不消耗、不轉成只有 ID 的假快照。
油鍋鏟 ID 轉換保留穩定 API 公開的耐久、附魔、名稱和限制；不可見任意 NBT 仍非本版承諾。
鍋鏟先做原作 25% 耐久抽樣，再使用原生 Unbreaking 損耗機率；動畫、聲音和熱鍋傷害仍需實機對照。

## 配方、品质与真正原生營養

| 菜品 | 原作固定配方 | 彈性配方必需種類 | 每批成品 |
| --- | --- | --- | --- |
| 折耳根炒肉 | 折耳根 3＋豬肉 3 | 折耳根、豬肉 | 1 |
| 青椒炒魷魚鬚 | 青椒 2＋魷魚鬚 2＋洋蔥 1 | 青椒、魷魚鬚、洋蔥 | 1 |
| 紅燒雞翅 | 雞翅 3＋糖 3 | 雞翅、糖 | 1 |

exact 優先於 flex。Flex 按不同 Item 身分去重後做一對一匹配，空槽補至九槽；
相同 tag 的兩個不同 Item 不任意合成一類。品質計算仍使用原來九個輸入槽及原宣告順序，
不是用去重後的兩／三份計算份量折扣。品質不放大成品份數。

`World.seed` 直接解析 signed-long 十進位字串；`ResourceLocation.hashCode`、
long 溢位、48-bit Java Random、`nextInt` 拒絕抽樣和洗牌順序分別保留。
不把種子經過 Number 四捨五入、不猜 seed=0、不在失敗時發預設高品質。
品質為 0／1／2／3，倍率 1.2／0.9／0.6／0.3；exact 缺少 quality 時保持原基礎食物值，
不是暗中補 STANDARD。

十二個隱藏原生 food 變體沿用三道原菜的名稱、icon、動作、食用時間與堆疊上限，
以 native `minecraft:food` 提供品質營養，不在 after-complete 手動補發 hunger 或重扣食物。
本維護線依 NeoForge 1.21.1 原 `QualityUtils` 的飽和恢復值適配；Forge 的 modifier 縮放差異明列，
沒有把兩版合稱逐值等價。原作三道 dish 沒有吃完返碗，故不增加免費碗。

公開 food v1 的可選 quality 嚴格限制為整數 0–3；native alias 與 public payload 必須一致。
損壞、被剝除或 ID／quality 錯配的變體在目前 item-use 入口被拒絕。
冷卻、熱度合併、自訂 lore 和食材快照保存品質；菜品進秘製串後仍保留完整可公開的成品資料。
Java 串盤只接受串，故沒有新增普通菜品直接放串盤的玩法。

舊料理完成回呼的無起始記錄 fallback 被移除。熱食／調味附加效果須與開始時的手、槽、
完整公開快照及原生使用時長相符，提交前先撤銷會話，重複完成不再追加。
兩手相同且事件沒有 hand 證據時不猜附加效果所有者；品質食物本身仍由原生引擎結算。
詳細分支、數值與入口範圍見[品質證據](evidence/cuisine-quality-native-food-20261009.md)。

## 有限 Java A 證據：1,248＋12

[`tools/java_cuisine_quality_oracle.py`](../tools/java_cuisine_quality_oracle.py) 核對原作者五個檔案的 SHA-256，
分別編譯並直接執行 Forge／NeoForge 的未修改 `QualityEvaluator`／`Quality`，
另執行 NeoForge `QualityUtils`。真 JDK 負責 Random、Collections.shuffle、String hash、
整數溢位與浮點運算；Minecraft 食材／清單和未使用 codec 由明列最小資料依賴連接。
原作者完整來源不隨工具發布。

兩分支各自產生相同的 **1,248** 個品質觀察，涵蓋三道配方、九槽內所有正數二／三食材數量組合、
八個種子，包括 signed-long 上下限和超出 Number 精確範圍的正負值。四種品質都有實際觀察。
另外 **12** 組 NeoForge 原食物營養／float 飽和恢復值與自有純 core 相符。
[`java-cuisine-quality-160.json`](../development/gameplay_core/fixtures/java-cuisine-quality-160.json)
保存版本、檔案雜湊、依賴界線及觀察值；直接 JS 比對不把另一份翻譯公式當 oracle。

這項 A 只涵蓋上述 evaluator／quality／food value 純邏輯；
不代表完整原作 JAR、Minecraft recipe manager、PotBlockEntity 事件、native Bedrock 食用或 client 已執行。
新測項限定純資料／儲存：植物所有權七個回歸、炒鍋純配方與階段，及既有熱度儲存檢查中的一個品質案例。
先前機制候選整合時，另以既有 storage harness 各執行一次零交付原菜→黑暗料理和站點回復失敗保留油成本，兩個具體回歸均通過。
既有必要 CI 保留，沒有新增或本地執行模擬玩家互動套件。

## 紅樹與退款所有權

紅樹葉只在下方明確為乾燥空氣時生出 `hanging=true, propagule_stage=0` 的胎生苗。
第二次油渣仍點同一片葉，不會改點剛長出的苗。已存在的乾燥懸掛苗每次成熟一階，最多 stage 4；
一個油渣最多作用兩次。地面苗、水浸、未知水狀態或未知區塊不扣料。
目前固定 Geyser 原始映射使用 Java AGE→Bedrock propagule_stage；舊 STAGE 投影沒有被沿用。

每次寫入記錄是否真正進入 setter。前置條件失敗，不會拿巧合相同的後像退款或覆写別人的資料。
回復 block／drop 必須確認仍屬於本操作且已回到前像；任何一次失敗／未知都禁止退回肥料成本。
槽位用原生堆疊身份判斷；掉落物以原生 entity ID、完整可比較的 stack 和移除讀回確認，
已拾取／合併／改變或未知的掉落不假裝撤回成功。

詳見[紅樹與所有權證據](evidence/mangrove-and-fertilizer-ownership-20261009.md)。
甜菜中間 growth、竹子停止 stage、海帶完整液體層回復與其他 feature 植物仍是具體未完成項。
相同資料的外來 ABA 更換、隱式鄰居更新及斷電／儲存 crash 原子性亦未被這份 journal 證明。

## 指南、版本與交付邊界

指南保留一個既有 Cookery 煙火入口、76 個條目、6 根類及 8 子類。
三道菜各保留原 exact 卡，再加一張最小 flex 卡，總配方卡 95→98；
三語說明包含新鍋／舊鍋、備料、三翻、品質、變質和普通材料範圍。
12 個內部品質變體沒有重複頁面或創造模式條目；四個品質翻譯鍵位於自有 runtime 語言區，
指南 generated 區仍由唯一 catalog 產生。先前機制候選的頁面數、三語、食物值、配方和事件分片靜態檢查已通過；
G122 的指南與宿主交接仍由本版必要 CI 核對。
catalog 的 `acquisition_gaps=0` 只描述列明資料分類，不是自然取得與生存全流程證據。

原 G69／G115／G117／G118／G119／G120 公開來源見證及已合併 G121 指南歷史維持原意；
機制修補保留精確的 main.js、指南與四個品質文字差異，以及 12 個嚴格原生變體例外。
先前候選的來源比對不能代替 G122 的最終 runtime freeze；公開 PR 的必要檢查、merge commit、main CI 與測試資產逐一核對，
其實際結果以 GitHub PR／run／release 為準，不能用本地恢復檔案代替公開交付。

已重新讀取家族 `family/java-upstream.json`：Grilling 的 Forge 1.20.1／NeoForge 1.21.1
仍分別選 CF8726006／CF8726014；本次亦重新開啟原 CurseForge 兩版頁面確認 1.1.1。
家族紀錄的 Grilling 文字仍是 G119 歷史範圍，本輪不越權改寫 Tavern 遠端。
目前環境沒有可用 BSM／luosen 入口、當前 upstream-status、完整家族 receipt 或停服存檔；
所以尚未進行本候選完整家族 static／BDS／保存演練或 LIVE 更新。
既有部署授權保留，並未改成等待再次許可；native admission 證據不能捏造或借用 G114 舊 receipt。
