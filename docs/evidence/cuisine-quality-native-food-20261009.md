# G121：flex 品質、原生營養與成品資料保存

日期：2026-10-09。這份證據對應 G121 的自有品質模組、12 個內部食物變體、公開 food metadata、
冷卻／合併／食材快照與料理進食入口。完整炒鍋配方和階段交接由本版的 pot adapter 負責；
本頁不把純 Java 結果、Script API 宣告或 JSON 食物值當成實機食用、保存世界或客戶端驗收。

## 已讀來源與分支選擇

| 來源 | 固定 revision／方法 | 本次用法 |
| --- | --- | --- |
| Grilling 1.1.1 | [`9a1acdab27698457bec16c9362678e574895a28c`](https://github.com/breezeth-CN/KaleidoscopeGrilling/tree/9a1acdab27698457bec16c9362678e574895a28c)；兩分支 `ModItems.dish`、`FlavorFoodItem`、`CuisineQualitySupport` | 三菜基礎營養 9／8／10、modifier 0.7／0.6／0.8；只有持有品質的成品才縮放 |
| Java Cookery Forge 1.6.0 | [`2f4e386ce23f49a385ddf003c67fc6415c55417a`](https://github.com/KaleidoscopeMods/KaleidoscopeCookery/tree/2f4e386ce23f49a385ddf003c67fc6415c55417a)；`QualityEvaluator`、`Quality`、`QualityUtils` | 核對演算法與 Forge 的 modifier 縮放語義 |
| Java Cookery NeoForge 1.6.0 | [`4d39e36cfa749939ba5f9d6d3b715ef9a984cb9c`](https://github.com/KaleidoscopeMods/KaleidoscopeCookery/tree/4d39e36cfa749939ba5f9d6d3b715ef9a984cb9c)；同組品質類別 | **G121 的實際品質營養目標採用維護中的 NeoForge 1.21.1**；縮放的是 `FoodProperties.saturation()` 恢復值 |
| Java 標準庫 | [Java Random](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Random.html) 與實際 JDK `Collections.shuffle` | 48-bit LCG、`nextInt` 的高區間拒絕、同一 RNG 的比例洗牌 |
| Bedrock | [`minecraft:food`](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/itemreference/examples/itemcomponents/minecraft_food?view=minecraft-bedrock-stable)、[`World.seed`](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/world?view=minecraft-bedrock-stable#seed) | 原生營養與 modifier；世界種子直接讀十進位字串 |
| 原生食用事件 | [`ItemUseBeforeEvent`](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/itemusebeforeevent?view=minecraft-bedrock-stable)、[`ItemCompleteUseAfterEvent`](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/itemcompleteuseafterevent?view=minecraft-bedrock-stable)、[`ItemStack`](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/itemstack?view=minecraft-bedrock-stable) | 開始前可取消；完成事件提供實際使用物品；完整公開快照只在 after-event 讀取 |

配方／種類一對一匹配、exact 優先、固定九槽、原始 `flex_pot/` recipe ID 等來源細節，見
[G120 的完整來源審查](cookery-flex-pot-lifecycle-20261009.md)。G120 的「尚未實作」是當時的歷史狀態，
本版是否可註冊 flex 仍須由已接通的 producer／consumer／pot lifecycle／metadata 共同決定。

## 演算法契約

自有純模組是 `behavior_pack/scripts/host_api/cuisine_quality_core.js`：

```js
evaluateCuisineQuality({
  worldSeed,   // 精確 signed-long 十進位字串
  recipeId,    // 原作 kaleidoscope_grilling:flex_pot/<菜名>
  ingredients,// 原宣告順序的 alternatives 陣列；[] 是空 ingredient
  inputs      // 必須正好九個 item ID 字串，空槽為 ''
});            // 0..3；資料不可讀／不合法時是 undefined
```

種子先以 `BigInt` 解析，拒絕超過 Java signed-long 範圍的值；從未經過 JavaScript `Number`。
`ResourceLocation.hashCode` 是 int32 的 `31 * namespace.hashCode() + path.hashCode()`，
再符號延伸參與 Java long 的 `worldSeed * 31 + hash`；64-bit 溢位與 Random 的 48-bit 初始混合分開處理。
無法讀種子不替換成 0、時間或 `Math.random()`，也不默認領取 POOR。

二種類按 2–4、1–2 抽比例；三種類按 2–4、1–3、1–2 抽比例，之後用同一 Random 洗牌。
每個 ingredient 計算九槽中匹配的物品槽數；quantity factor 使用 list 的大小 9，故為 1，
不按非空槽數折扣。cosine 相似度的四次方依 0.95／0.82／0.55／0 的順序選品質。
固定世界與 recipe ID 的目標比例不會因為多煮一次而漂移。

| 保存值 | 原作品質 | 倍率 |
| --- | --- | --- |
| 0 | SUPERB／極佳 | 1.2 |
| 1 | EXCELLENT／優秀 | 0.9 |
| 2 | STANDARD／普通 | 0.6 |
| 3 | POOR／生疏 | 0.3 |

## 成品身份與真正營養

public food v1 增加可選整數 `quality`。**缺少欄位保持 exact 成品的原基礎值**；
`0` 必須保留，不能被 falsy 預設覆蓋。非整數、null、boolean 或範圍外值使整份 public record 無效。
新變體 ID 為 `<三菜原 ID>_cuisine_q0` 至 `_cuisine_q3`，共有 12 個，沒有獨立創造模式條目。
它們沿用原名稱、icon、16 堆疊上限、主副手能力、1.6 秒食用時間與動作，只有原生 food 值依品質改變。
原作 `dish` 沒有設定吃完返碗，`FlavorFoodItem` 也不覆寫返還，所以沒有額外加入免費碗。

原作兩分支都把 nutrition 乘品質倍率後 `Math.round`。NeoForge 把原 float 飽和恢復值直接乘 float 倍率；
Forge 則把原 modifier 乘倍率，再交由該版原生食物計算。本版沒有把這兩條公式混成一份。
Bedrock 以 `nutrition * saturation_modifier * 2` 計恢復值，因此內部 JSON modifier 由 NeoForge 目標恢復值反推，
以原生 float 可表示值保存；`cuisineQualityFoodSpec` 同時明列目標 `saturationGain`。

下表的飽和值取十進位近似便於閱讀；純 oracle 保留實際 Java float 值。

| 菜品 | 極佳：營養／飽和恢復 | 優秀 | 普通 | 生疏 |
| --- | --- | --- | --- | --- |
| 魚腥草炒肉 | 11／15.12 | 8／11.34 | 5／7.56 | 3／3.78 |
| 青椒魷魚 | 10／11.52 | 7／8.64 | 5／5.76 | 2／2.88 |
| 紅燒雞翅 | 12／19.20 | 9／14.40 | 6／9.60 | 3／4.80 |

鍋的已確認交付直接建立相應原生變體，再把相同品質寫到 actual output 的 public payload。
料理的結果與配方仍保存原 ID；交易的請求身份與實際輸出 fingerprint 分開，原生變體不覆寫已完成交易的配方身份。
領取、拆除回收與 replay 必須共同使用同一品質與 actual output ID。
JSON 讓原生引擎在消耗實際那份成品時給營養，沒有新增 after-complete 的品質加減 hunger／saturation、
定時扣食物、換手補發或品質退款路徑。

在 `beforeEvents.itemUse`，`canUseCuisineFood` 要求內部 q 變體具有有效且一致的 public 品質；
原 ID 若意外持有 quality 也拒絕食用。用指令製造但沒有 payload 的隱藏變體、被外部程式剝掉 payload 的成品、
q0 ID 配 q1 metadata，以及 malformed public lore 都不被這個入口接受，不會自行修成較高品質。
這是目前啟用的 Script API 食用入口保護；它不承諾在腳本停用、另一個 pack 越過／撤銷取消，
或外部程式於原生提交之後改寫物品時仍能覆寫引擎的已完成行為。不同 pack 也不能僅改品質欄位來改變既有成品。

## 跨保存、冷卻、合併與串盤

`normalizePublicFood`、`readPublicFoodLore` 與 `writePublicFood` 全程保留 quality。
`publicFoodLoreRows` 是唯一公開 lore 排列器；冷卻清理用它算預期前後像，避免新增品質行後和實際寫入排序不一致。
熱度截止時間與調味更新使用既有 record 的展開值，保留 quality 與 `nativeVariant`；
冷卻失敗仍走原先獨立回復／回讀，不把不確定寫入當成資料已刪除。

品質 tooltip 使用 Grilling 自有的四個 translation keys，顏色對應原作 GOLD／GREEN／WHITE／DARK_GRAY。
英語與簡體文本來自固定 Cookery 來源；其繁體來源當時沒有這四個 key，故提供明確繁體翻譯。
保留 19 行自訂 lore 時優先保存 public payload，略過可選品質展示行；不刪掉玩家的自訂行來騰位置。
原有 maxim 查詢以 canonical ID 查找，內部變體仍使用同一條原作風味文字。

熱食合併簽名包含 native type ID 和 quality，所以不同品質不被手動熱度合併抹平。
完整 `captureSkewerMetadata`／`restoreSkewerMetadata` 保存 native ID、raw lore、公開動態属性與原有附加資料；
本版沒有在回復時把 q 變體轉回沒有品質的基本食物。
`foodFacts` 拒絕不一致的料理；`ingredientFoodFacts` 要求 q 食材的完整 version 1 native envelope，
從已保存品質身份重新取得營養，不能只信舊的 cached nutrition。

Java `SkewerPlateItem.isSkewer` 排除普通菜品，故沒有新加「直接把菜放上串盤」的入口。
菜品仍可依既有 food ingredient 規則串成秘製串；其完整 q 成品快照隨秘製串進串盤、取回或保存。
現有 `refreshPlateFood` → `secretFood` → `ingredientFoodFacts` 在讀取時重新計入品質營養；
既有串盤扣一份／營養提交／回復和秘製串食材效果處理均保留。
這一資料投影仍只覆蓋 stable API 公開的 metadata，不是任意 Java NBT 或外部私有組件的序列化器。

## 原有熱食／調味只結算一次

G120 的 cuisine completion 允許缺少 start snapshot 的 fallback，且重複完成回呼可再次追加熱食／調味。
本版的 `cuisine_eating_core.js` 使用完整公開 native snapshot、實際唯一匹配的手、選中槽、開始 tick 與原生 duration。
倒數熱 lore 的展示變動可忽略，已到期的 heat 欄位可轉為冷值；品質、調味、名稱、自訂行、限制和其他公開資料仍須一致。
兩手完全相同而事件沒有 hand 欄位時，不猜測哪一手擁有可選附加效果。

完成事件必須匹配開始記錄、原生完成時間與目前手中相同的前像／原生減一後像；單份已消耗可以是空手。
匹配後先移除會話才追加既有效果，重複完成沒有 fallback 可領取。
stop 採 deferred 精確會話清理，讓同 tick 的完成有機會提交，也不會移除後來開始的新會話。
缺少起始記錄、換到不相同的手持物或無法確認公開資料時，只放棄附加效果；不退款、不額外扣份，也不改寫原生品質營養。
三道菜沒有自己的保證藥水效果，故未把油熱度／調味倍率替換成品質倍率。

## 驗證與仍需驗收的邊界

- 獨立 JVM oracle 直接執行固定的原作者 `QualityEvaluator`／`Quality`，以最小非玩家資料依賴連接真實 JDK Random／shuffle。
  兩分支的 1,248 個品質觀察值涵蓋正數二／三食材配置、九槽容量與 8 個邊界種子；完整 fixture 和直接 JS 對照由本版來源檢查保存。
  原 NeoForge `QualityUtils` 的 12 組營養／飽和恢復值與純 core 相符。工作區重建後已重新核對 `8c37f6c` 恢復的純 core bytes，全部一致。
- 唯一新增 metadata regression 是既有 `test_java_heat_deadlines.mjs` 中的 quality envelope 測項：
  驗證 0 品質穿過冷卻／raw lore 保存，錯配與被剝除的 payload 拒絕，19 行使用者 lore 不犧牲必需品質欄位。
  這是 storage-operation fixture，沒有新玩家互動模擬；原有故障注入／斷言不刪除。
- 語法、原生 item JSON 與來源差異在實際提交邊界檢查。完整必要 CI 仍由正式候選執行；沒有在本地跑全套玩家套件。

原生引擎的 float 運算／飢餓上限、食用取消與 callback 的實際順序、移動物品與停服重啟後的保存、
工具提示顯示及既有動作／聲音，仍需要相應 BDS／保存世界／客戶端證據。
純數值相符不代表品質成品已完成 LIVE 安裝，更不代表全部 Grilling 機制 1:1 還原。
