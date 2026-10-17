# 炒鍋 exact／flex：來源、品質與剩餘實作邊界

核對日期：2026-10-09。這是 G120 的來源審查與後續實作規格，**沒有新增 `wok_flex` capability、配方註冊或未接通的 runtime module**。
現行三菜的 6／5／6 個食材來自原作的 exact pot 配方，並非無據配方；缺口是另一條 flex 路徑，
以及 exact 與 flex 共用的完整料理狀態、油備料時鐘、普通食材輸入鎖、所有權保存與 quality 食用。
這些功能尚未實作，不能歸類成只待原生驗收，也不是已證明不可實作。

## 固定來源

| 來源 | 已讀版本／revision | 本頁採用的方法或資料 |
| --- | --- | --- |
| Grilling | [1.1.1／`9a1acdab27698457bec16c9362678e574895a28c`](https://github.com/breezeth-CN/KaleidoscopeGrilling/tree/9a1acdab27698457bec16c9362678e574895a28c) | Forge 1.20.1 與 NeoForge 1.21.1 的 common 配方／tags、`ModItems.dish`、`FlavorFoodItem`、`CuisineQualitySupport`、`PotBlockEntityMixin` |
| Java Cookery Forge | [1.6.0／`2f4e386ce23f49a385ddf003c67fc6415c55417a`](https://github.com/KaleidoscopeMods/KaleidoscopeCookery/tree/2f4e386ce23f49a385ddf003c67fc6415c55417a) | `BaseRecipe`、`PotRecipe`、`FlexPotRecipe`、兩個 serializer、`PotBlock`、`PotBlockEntity`、`QualityEvaluator`、`Quality`、`QualityUtils` |
| Java Cookery NeoForge | [1.6.0／`4d39e36cfa749939ba5f9d6d3b715ef9a984cb9c`](https://github.com/KaleidoscopeMods/KaleidoscopeCookery/tree/4d39e36cfa749939ba5f9d6d3b715ef9a984cb9c) | 同組方法；`SimpleInput`／`RecipeHolder`／data component 與 Forge 的 `SimpleContainer`／NBT 分開核對 |
| Forge matcher | [`71d814ffa64fce31b5bf4bebf04915f299a69ae8`](https://github.com/MinecraftForge/MinecraftForge/blob/71d814ffa64fce31b5bf4bebf04915f299a69ae8/src/main/java/net/minecraftforge/common/util/RecipeMatcher.java) | `findMatches` 要求一對一完整配對，不能忽略多餘輸入 |
| NeoForge matcher | [`a2d6402a3c1eec093aef7e7d10ac5145906c199e`](https://github.com/neoforged/NeoForge/blob/a2d6402a3c1eec093aef7e7d10ac5145906c199e/src/main/java/net/neoforged/neoforge/common/util/RecipeMatcher.java) | 相同的一對一配對契約 |
| Bedrock API | [`@minecraft/server` 2.9.0](https://www.npmjs.com/package/@minecraft/server/v/2.9.0) 與 [Microsoft `World.seed`](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/world?view=minecraft-bedrock-stable#seed) | 已有唯讀 `seed: string`，不是缺 API 的阻塞 |

Cookery 的 Java 檔案位於 `src/main/java/com/github/ysbbbbbb/kaleidoscopecookery/`；
配方／serializer 分別在 `crafting/recipe/` 與 `crafting/serializer/`，鍋在 `block/kitchen/`／`blockentity/kitchen/`，品質在 `item/quality/`。
兩個 Cookery branch 的 `gradle.properties` 都標示 1.6.0；以上是本次實際讀過的固定 source revision，沒有把不同 loader 的 bytecode 或食物數值表示合併成一份。
Forge／NeoForge matcher 是各自官方維護分支的固定來源審查，不是本頁重新建構 Cookery 發布 JAR 的證據。

Mojang 官方 `Ingredient.test` 另用[既有官方 JAR／mappings](vanilla-plant-fertilizer.md#來源與可重現輸入)只讀解碼核對：
1.20.1 是 `ciz.a`，原始行 55–68；1.21.1 是 `cyw.a`，原始行 61–74。
空 ingredient 只匹配空 stack；一般 item／tag ingredient 按其列出的 Item 匹配。

作者 Bedrock 1.6.0 的入口取自
[原始 mcaddon](https://edge.forgecdn.net/files/9054/164/Kaleidoscope%20Cookery%20v1.6.0.mcaddon)，
archive SHA-256 `da12fe6d39d7514aff1de3c963d69899324d771be5ca0fc3da1ccb759c7ad458`。
只讀 exact 檔案的 SHA-256 為：

- `scripts/api/extensionRegistry.js`：`4f02f0705fe6cd1578485490a404bff7887ceb8ace9fec9c9f61863e3cdd1723`。
- `scripts/custom_components/blocks/directStation.js`：`19207a023a04da532ff9e34cd95413f09cf000fc672255c03633a7bcb2744ad4`。

原始第三方腳本、mcaddon、Java clone、官方 class 與解碼輸出均不加入本倉庫。後續掛鉤必須繼續用既有原檔 hash 保護，
只發布 Grilling 自有 module 與可審查的短 insertion；同一宿主檔案的多條修復最後合併計算一份 patched hash。

## 三菜有兩條配方，exact 必須保留優先

以下名稱省略共同 namespace；`chicken_wings`、`houttuynia`、`squid_tentacles`、`onions` 是原作 ingredient tags。
來源資料分別在
[`common/.../recipes/pot`](https://github.com/breezeth-CN/KaleidoscopeGrilling/tree/9a1acdab27698457bec16c9362678e574895a28c/common/src/main/resources/data/kaleidoscope_grilling/recipes/pot)、
[`recipes/flex_pot`](https://github.com/breezeth-CN/KaleidoscopeGrilling/tree/9a1acdab27698457bec16c9362678e574895a28c/common/src/main/resources/data/kaleidoscope_grilling/recipes/flex_pot)，
NeoForge 使用同樹的 `recipe/pot` 與 `recipe/flex_pot`。

| 菜品 | 原 exact 配方 | 原 flex ingredient slots | 結果／容器／時間／翻炒 |
| --- | --- | --- | --- |
| 魚腥草炒肉 | 魚腥草 tag ×3、`minecraft:porkchop` ×3 | 魚腥草 tag、`minecraft:porkchop` | 1 份、1 個碗、200 ticks、3 次 |
| 青椒魷魚 | `kaleidoscope_cookery:green_chili` ×2、魷魚須 tag ×2、洋蔥 tag ×1 | 青椒、魷魚須 tag、洋蔥 tag | 1 份、1 個碗、200 ticks、3 次 |
| 紅燒雞翅 | 雞翅 tag ×3、`minecraft:sugar` ×3 | 雞翅 tag、`minecraft:sugar` | 1 份、1 個碗、200 ticks、3 次 |

flex JSON 明寫 `time=200`、`stir_fry_count=3`；exact JSON 省略這兩個欄位，但**兩個分支的 `PotRecipeSerializer` 預設同樣是 200／3**。
`BaseRecipe.assemble` 只複製配方的 result；這六條配方的結果都是固定一份。
現行 `a2750_wok_food_core.js` 的 6／5／6 個食材即對應上表 exact 配方，可以保留。

`PotBlockEntity.startCooking` 先找 `POT_RECIPE`，找不到才找 `FLEX_POT_RECIPE`，兩者都沒有才走迷之炒菜。
exact 成功時不走 `applyFlexRecipe`，所以也不計 flex 品質。
不能讓較寬的 flex 或 Bedrock 的 batch resolver 蓋過一條已匹配的 exact recipe。

### Flex 的「自由比例」實際含義

`FlexPotRecipe.matches` 遍歷九槽輸入，以 **Item 身分**去重，保留每個不同物品第一次出現的 stack，
再補空槽到九槽；`BaseRecipe.fillInputs` 也把 ingredient 補空到九槽，最後交給 `RecipeMatcher.findMatches`。
因此：

1. 重複投入同一物品可以改變比例，但不增加配對時的種類數，也不把產量乘成多份。
2. 所有不同物品都必須能一對一對應到 ingredient slots；不能忽略陌生食材，也不是「至少包含這幾樣」。
3. 兩種不同物品即使屬於同一 tag，仍是兩種 Item；不能先按 tag 把它們合併。只有一個該 tag slot 時，額外種類仍會影響是否能完整匹配。
4. ingredient 的宣告順序不影響能否一對一匹配，但會被品質比例向量使用，註冊／正規化時應保留此順序。

原作 [`tags/items/ingredients`](https://github.com/breezeth-CN/KaleidoscopeGrilling/tree/9a1acdab27698457bec16c9362678e574895a28c/common/src/main/resources/data/kaleidoscope_grilling/tags/items/ingredients)
中，前三個 tag 的本模組成員分別為 `chicken_wing`、`houttuynia`、`squid_tentacle`。
Forge 的 onions 指向 `#forge:crops/onion`，NeoForge 指向 `#c:crops/onion`；Grilling 對兩者都加入 `kaleidoscope_grilling:onion`。
這是已讀的本模組成員，不代表可以把外部模組向共享 tag 追加的所有成員猜成同一物品。
後續窄 adapter 要明列已驗證的 alternatives；沒有動態 tag 橋時，不能宣稱承接任意 Java datapack tag。

## Java 時鐘與料理狀態

下表直接對應 `PotBlockEntity` 的 `placeOil`、`tick`、`tickPutIngredient`、`onShovelHit`、
`tickCooking`、`tickFinished`、`tickBurnt`、`addIngredient`、`removeIngredient`、`takeOutProduct`。
`tick` 只在有熱源時推進；它先把正數 `currentTick` 減一，再執行當前狀態的處理。

| 狀態／動作 | 來源規則 | 現行 Bedrock host 的差異 |
| --- | --- | --- |
| 倒油，進入備料 | `PUT_INGREDIENT_TIME=1200`；有沒有放食材都會用掉這段有熱源的時間 | `oilTicks` 只在空鍋時遞減，有食材即保留 |
| 增減普通食材 | 只允許 `PUT_INGREDIENT`；操作不重設備料時鐘 | 每次增減都重算 recipe／重設 progress，烹飪中也能改 |
| 第一鏟 | 有食材時先 `startCooking`，把烹飪剩餘時間設成 200；同次動作接著扣一次翻炒要求 | 第一個食材已使 `started=true`；鍋鏟只把 `stirs` 設成 1 |
| 備料時間耗盡 | 有食材自動 `startCooking`，尚未翻炒時仍欠 3 次；空鍋則 reset | 沒有相同的非空備料倒數與自動切階段 |
| 其餘翻炒 | COOKING 中把大於零的剩餘翻炒數逐次減一 | 每次都覆寫成 `stirs=1`，無累計三次 |
| 200 tick 烹飪完成 | 欠任何翻炒就把結果換成 `suspicious_stir_fry`、容器改碗；仍進 FINISHED | 少一翻時等待 60 tick grace，再變焦炭 |
| 沒配方 | 迷之炒菜，200 tick，要求翻炒數是 0 | 宿主暫定迷之菜仍走一翻／grace 邏輯 |
| 完成後未取出 | FINISHED 可在熱源上等 800 tick，之後 BURNT 再等 400 tick | 完成後 400 tick 直接變持續焦炭清理狀態 |
| 燒焦後取出／耗盡 | BURNT 取出黑暗料理；400 tick 耗盡 reset 並掉 1–3 炭 | 焦炭一直留在鍋中，空手清理領取；G120 的守恆修復不等於這段 Java 時序已還原 |

三條 exact 與三條 flex 配方的結果都只要一個碗。Java `takeOutWithCarrier` 按結果 count 要求和扣除碗後，一次交付結果並 reset；
這裡不能因輸入重複就沿用宿主的多份逐碗 batch。
Java 存檔保存 inputs、carrier、result、status、currentTick、stirFryCount；未完成流程不能只保存某個配方 ID 或一個 `started` flag。

普通食材鎖不能順便擋掉 Grilling 的既有特殊調味：兩分支 `PotBlockEntityMixin` 在 `addIngredient` HEAD 攔截特殊調味，
也在倒油前後保存油種、`startCooking`／取出時寫入熱度與調味、reset／save／load 時維護它們。
後續 lifecycle adapter 必須保留這些修復與配置分支。
另有獨立互動差異：Java `PotBlock.use`／NeoForge `useItemOn` 以 0.25 機率進入鍋鏟耐久消耗，之後才交給原生耐久／附魔規則；
不能把宿主通用 `dmgTool` 視為已證明相同。

## 品質：seed 已可讀，保存與食用仍缺接線

`applyFlexRecipe` 把 **固定九槽的 `this.inputs`**、配方的 padded ingredients、原 Java recipe ID、世界 seed
傳給 `QualityEvaluator.evaluate`，把結果寫到成品上。Forge 寫 `kaleidoscope_cookery:quality` NBT int，NeoForge 用 QUALITY data component。
這三條配方的原 ID 是 `kaleidoscope_grilling:flex_pot/<菜名>`；不能以現在 `wok/<菜名>` 的註冊 alias 代替它計 seed。

品質算法要保留以下來源細節：

- 專用 seed 是 Java long 的 `worldSeed * 31 + recipeId.hashCode()`，其中 recipeId 是 Java `ResourceLocation`；使用 `java.util.Random`，並依同一 RNG 做 `Collections.shuffle`。
  seed 字串要精確解析為 64-bit 整數，不能先轉成可能失真的 JavaScript Number，也不能以時間、`Math.random()` 或固定 0 代替。
  `recipeId.hashCode()` 按兩版官方 `ResourceLocation` 實作，為有符號 int32 的 `31 * namespace.hashCode() + path.hashCode()`，含乘加溢位；結果符號延伸為 long，再參與 64-bit seed 運算，不等於完整 `namespace:path` 字串的 hash。
- 去除空 ingredient 後，二種類的比例池是 `2+nextInt(3)`、`1+nextInt(2)`；三種類則多一個 `1+nextInt(3)` 槽，完整順序是大、中、小後 shuffle。
- 每個 ingredient 分別計算原 inputs 中匹配的槽數，與亂數比例向量做 cosine 相似度的四次方。
  quantity factor 是 `0.8 + 0.2 * (inputs.size()/9)`。**鍋傳入的是固定九槽 list，包含空槽，因此此呼叫的 quantity factor 是 1**，不可改成已投入物品數除以 9。
- 得分依 SUPERB、EXCELLENT、STANDARD、POOR 順序比較 0.95、0.82、0.55、0；對應保存 ID 為 0、1、2、3。

| 品質 | 門檻 | 品質倍率 |
| --- | --- | --- |
| SUPERB／極佳 | ≥ 0.95 | 1.2 |
| EXCELLENT／優秀 | ≥ 0.82 | 0.9 |
| STANDARD／普通 | ≥ 0.55 | 0.6 |
| POOR／生疏 | ≥ 0 | 0.3 |

Grilling 的三菜是 `ModItems.dish` 建立的 `FlavorFoodItem`；其 `getFoodProperties` 經 `CuisineQualitySupport` 呼叫 Cookery `QualityUtils`。
魚腥草炒肉、青椒魷魚、雞翅的原營養依序是 9、8、10，原 saturation modifier 是 0.7、0.6、0.8。
**沒有 quality metadata 時保持原基礎數值**，不能把「沒有品質」當成 STANDARD 然後乘 0.6。

有品質時，兩分支都以 `Math.round(倍率 × 原 nutrition)` 計算營養；飽和表示必須區分：

- Forge 1.20.1 的 `modifyFoodProperties` 把 **saturation modifier** 乘品質倍率，結果仍交給該版原生食用。
- NeoForge 1.21.1 把 `FoodProperties.saturation()` 這個**飽和恢復值**乘品質倍率，並非再次按新 nutrition 重建一份 Forge modifier 公式。

Cookery 的泛用品質工具也能縮放保證觸發的效果時長，Grilling 的 EffectFoodItem／DualEffectFoodItem 另有 duration 支援。
**上述三菜本身沒有自身藥水效果**；泛用 duration 公式與三菜 nutrition／saturation 規則需分開。
油熱度／調味附加效果屬於另一條既有機制，不能拿品質倍率替換它們。

Bedrock 2.9.0 的 `World.seed` 已在 declarations、固定官方 bindings 與 Microsoft 文件確認可讀。
目前未完成的是輸出 metadata、單次交付／回收、lore／堆疊、食用輸入快照與實際營養結算的整條接線：

- `host_api/food_api_core.js::normalizePublicFood` 只保留 `v/hotUntil/seasoning/nativeVariant`，沒有 quality；只往 payload 塞新欄位會被正規化丟掉。
- `a2750_food_state_adapter.js` 現在只處理熱度／調味；冷卻清理、再裝盤、保存或回收都必須保留品質。
- `main.js` 的 `CUISINE_FOOD_SET` 食用路徑使用原生基礎 food 值，主要追加熱食效果；沒有品質版 hunger／saturation 提交。
  成品品質必須綁定實際吃掉的那份 stack，與取消、換手、重複完成事件及已結算狀態共同核對，不能只在 start event 記一個等級後無條件加減數值。

## 可接續實作的拆分與宿主掛鉤

以下是**尚未啟用的候選契約**，不是目前已支援的 extension API：

```json
{
  "api": 1,
  "kind": "wok_flex",
  "source": "kaleidoscope_grilling",
  "recipe": {
    "id": "kaleidoscope_grilling:flex_pot/braised_chicken_wings",
    "ingredients": [["kaleidoscope_grilling:chicken_wing"], ["minecraft:sugar"]],
    "result": "kaleidoscope_grilling:braised_chicken_wings",
    "count": 1,
    "carrier": "minecraft:bowl",
    "time": 200,
    "stirs": 3
  }
}
```

實際 ready capability 只能在下列必需接線可用後廣播 `wok_flex`。
原 exact `wok` 註冊與 source IDs 可保留相容性；flex recipe 要獨立 registry，不進 `wokBatchRecipe`。
青椒／魷魚／洋蔥與魚腥草／豬肉按上表原順序建立 alternatives slots。

| 步驟 | 自有模組責任 | 原 host 的準確掛鉤／資料邊界 | 完成條件 |
| --- | --- | --- | --- |
| 1. Pure 配方與品質 | 有界九槽、Item 去重後完整配對、exact 優先、固定 count、原 ID／Java RNG 品質 | `extensionRegistry` 的 capability／register 分派；`directStation::wokRecipe` 先保留 exact 再找 flex，不能讓 batch 蓋過 | 配方、tag alternatives、品質輸入與 branch 數值語義均明列；未知資料拒收，不能默認成功 |
| 2. 已保存的備料與烹飪 | versioned phase、remainingTicks、remainingStirs、完整 inputs／result／carrier、一次批次身分 | `placeOil` 全部成功分支（含共享油容器）建立備料時鐘；`potInteract` 普通投入／取回／鍋鏟；`potTick` 前端擇一處理自有狀態 | 1200 備料時鐘從油開始，不從最後投料或辨認出 Grilling 菜時開始；第一鏟記作一次；cooking 不再改普通食材 |
| 3. 成本與回復 | 實際油／手持食材／容器／鍋鏟完整前後像、保存回讀、未知結果隔離 | 不能直接把吞例外的 `save` 當提交；與原 `consume`、`removeLastAndGive`、全部倒油分支一起處理 | 成本前先準備交易，狀態寫入回讀後才宣稱擁有輸入；寫後拋錯、未知寫入、reload、舊 callback 不重扣或發回同份 |
| 4. 完成與領取 | 成品／迷之／燒焦階段、epoch、metadata、領取／破壞互斥 | `potTick` 完成與 `burnWok`、`potInteract` 成品／焦炭領取、`spillDirectStationContents`；共同使用現有 cuisine receipt／recovery fence | 200 tick 缺翻炒出迷之；保存 800／400 後段狀態；同一 epoch 原料、菜品、黑暗料理、炭不能重複兌現；保留 G120 已有守恆修復 |
| 5. 品質食品與食用 | 跨 pack schema、quality 讀寫／lore、完整 stack identity、實際營養與 hot／seasoning 合成 | `food_api_core`、cuisine 輸出／回收 metadata、`a2750_food_state_adapter`、食物 snapshot／plate 與 `main.js` 的 cuisine 食用入口 | 無 quality 的 exact 菜保持基礎數值；flex 品質從保存的配方／seed 產生並只結算一次；branch 飽和值不能混用 |
| 6. 消費者與 guide | 可用能力、兩條配方呈現、實際支援範圍 | `a2727_cookery_host_recipes_core`、`a2750_wok_food_core` 與 guide；既有 guide 中 `wok_flex` 不能落入 Stockpot 分類 | producer／consumer／ready／guide 與完整已啟用功能一致，才啟用新註冊 |

既有 active host 記錄沒有「非空時流逝的備料時間」，`progress` 又可能多次被投料重設；不能從舊記錄倒推出真實 1200 tick 前像。
遷移需明確保留／排空 legacy batch 的路徑，或採用有所有權的顯式轉移，不能默認補滿 1200、清掉舊材料或重開一份輸出。
某個半成品輸入（例如只有糖）也不能可靠識別將來是否是 Grilling 菜，因此備料起時計錄必須早於完整 recipe 匹配。

**本次判定**：matcher 與固定產量可以寫成純函式；正確的第一鏟／200 tick／三翻結束結果，必須連帶接通備料、輸入鎖與已保存料理階段。
只改 `stirs=3`、只多註冊三條 flex、或只算一個 quality 欄位，都不足以完成該機制。
下一輪可以按上述邊界以 Grilling 自有模組與原 hash 保護掛鉤實作；G120 不加入不可用模組，不宣稱這些缺口已閉合。

## 本頁驗證範圍

已讀兩分支固定來源、原始 Bedrock host exact 檔案、目前自有 producer／metadata／食用入口，並只讀解碼官方 `Ingredient.test`。
本次沒有新增或執行玩家／世界模擬，沒有把來源公式複製成循環自證的測試，沒有運行全套既有遊戲測試，也沒有改版本或 freeze。
後續功能實作才依實際改動跑必要 CI 與保存世界驗證；原生食用、動畫、聲音與渲染仍需其相應驗收。
