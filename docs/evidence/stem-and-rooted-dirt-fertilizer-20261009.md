# 瓜梗與垂根施肥：來源、有限適配與原生待驗

核對日期：2026-10-09。這份增量記錄對應 G119 之後的 `plant_fertilizer.js`，
新增西瓜梗、南瓜梗與纏根泥土三個正式 Bedrock ID；既有 18 類 handler 保留，總數為 21 類。
狀態機、RNG 條件與交易順序已有程式；光照跨引擎等價、鄰居更新與實際玩家操作仍未驗收。

## 來源與方法

作者基準仍為 [Grilling 1.1.1／9a1acdab27698457bec16c9362678e574895a28c](https://github.com/breezeth-CN/KaleidoscopeGrilling/tree/9a1acdab27698457bec16c9362678e574895a28c)。
Forge 1.20.1 與 NeoForge 1.21.1 的 `OilResidueItem.useOn` 都是兩次 `super.useOn`，
任何一次接受動作，生存模式合計扣一個油渣。兩版對本頁三個植物的相關規則一致。

Minecraft 方法取自已驗來源的 Mojang 官方 client JAR、官方 mappings 與 CFR 0.152。
下載地址、SHA-1 和解码方式沿用[上一份植物證據](vanilla-plant-fertilizer.md#來源與可重現輸入)。
本次只在倉庫外追加所需 class 的解码，不發布 JAR、mappings 或反編譯全集。

| 原版方法 | Java 1.20.1 符號／原始行數 | Java 1.21.1 符號／原始行數 |
| --- | --- | --- |
| `StemBlock.isValidBonemealTarget` | `cxj.a`／91 | `dnv.b`／117 |
| `StemBlock.isBonemealSuccess` | `cxj.a`／96 | `dnv.a`／122 |
| `StemBlock.performBonemeal` | `cxj.a`／101–107 | `dnv.a`／127–133 |
| `StemBlock.randomTick` | `cxj.b`／61–82 | `dnv.b`／82–108 |
| `CropBlock.getGrowthSpeed` | `cre.a`／106–151 | `dht.a`／114–159 |
| `Direction.Plane` 水平方向／`getRandomDirection` | `ha$c`／495–497、509 | `ji$c`／508–510、522 |
| `LevelLightEngine.getRawBrightness` | `dwt.a`／163–166 | `eot.a`／163–166 |
| `RootedDirtBlock` 有效性／成功／作用 | `cvw.a`／18、23、28–29 | `dmj.b/a`／25、30、35–36 |

正式 Bedrock ID 與狀態仍取 Mojang
[`bedrock-samples` v1.26.50.4／46ba6ea985fb5a92d79a9419198f10dda14c199d](https://github.com/Mojang/bedrock-samples/tree/46ba6ea985fb5a92d79a9419198f10dda14c199d)，
尤其是[官方 block metadata](https://github.com/Mojang/bedrock-samples/blob/46ba6ea985fb5a92d79a9419198f10dda14c199d/metadata/vanilladata_modules/mojang-blocks.json)。
Java attached stem 到 Bedrock 同 ID 的方向狀態，另用 Geyser 開發者自己的
[固定 mappings](https://github.com/GeyserMC/mappings/blob/cc3afdc9b4a3d495c34d9c5e92819b9af8805c88/blocks.json)交叉核對；
這是狀態映射的佐證，不是 Bedrock 現用原生行為驗收。

## 瓜梗的完整一次作用

`minecraft:melon_stem` 與 `minecraft:pumpkin_stem` 共用有限 adapter：

1. 只接受整數 `growth=0..6` 且 `facing_direction=0` 的未附著梗。
   `growth=7` 不論是否已附著都不是有效骨粉目標；不消耗油渣。
   不把未證明的方向值 `1` 當作正常直立梗。
2. 每次增加 Java 的等機率整數 2、3、4 或 5，最多到 7。
   兩次作用分別抽樣；第二次讀第一次計畫後的狀態。
3. **僅在這一次剛到 7 時**執行成熟梗的 `randomTick`。
   即使沒有結出果實，這次施肥仍然有效；成熟後的下一次不再多抽一次結瓜。
4. 光照達到門檻 9 才計算周邊生長速度。3×3 下方土地以 Java 規則計分：基數 1，
   中心乾耕地加 1／濕耕地加 3，周圍耕地貢獻除以 4。
   同類未附著梗同时佔據 X 與 Z 軸，或有任何一株斜角鄰株，速度減半。
   Java 的 attached stem 是另一個 block；Bedrock 水平附著梗也因此不計入同類鄰株。
5. 以既有 `javaCropGrowthChance` 還原 `nextInt(floor(25/speed)+1)==0` 的機率。
   未命中只留下成熟梗，不結瓜，也不再抽方向。
6. 命中後只抽一次北、東、南、西，順序跟隨 Java `Direction.Plane.HORIZONTAL`。
   若該格非空氣，或下方不是原版 `#minecraft:dirt`／farmland，就停止；不搜尋其他空位、不重抽。
7. 有效空位才放置果實，然後把原梗設為朝向該果實的已附著狀態。

土地集合沿用已核對兩版 `#minecraft:dirt` 的既有集合，另加 farmland；
Java `rooted_dirt` 在 Bedrock 使用 `dirt_with_roots`。外部模組擴充 tag 沒有通用橋接。

| Java 狀態／輸出 | Bedrock 對應 |
| --- | --- |
| `melon_stem[age=0..7]` | `minecraft:melon_stem`，`growth=0..7`、`facing_direction=0` |
| `pumpkin_stem[age=0..7]` | `minecraft:pumpkin_stem`，`growth=0..7`、`facing_direction=0` |
| 附著方向北／東／南／西 | 相同梗 ID、`growth=7`、`facing_direction=2/5/3/4` |
| 西瓜果實 | `minecraft:melon_block` |
| 南瓜果實 | `minecraft:pumpkin` 的正式預設 permutation |

本次沒有替換 Bedrock 自己的自然 random tick，也沒有把已成熟的瓜梗變成無限施肥產瓜入口。
Java 與 Bedrock 的 RNG 序列來源不同；相同機率和抽樣條件不等於同一個世界 seed 產出相同序列。

## 光照：有明確推導的 adapter，尚非原生等價證明

Java 的 `getRawBrightness(pos, skySubtract)` 是方塊光與 `skyLight-skySubtract` 的最大值；
瓜梗傳入 **0**，所以原版此門檻保留未減去日夜值的 sky light。

實際使用的 [`@minecraft/server` 2.9.0 declarations](https://www.npmjs.com/package/@minecraft/server/v/2.9.0)
具有 `Block.getLightLevel()` 與 `Block.getSkyLightLevel()`。
[Microsoft stable 文件](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/block?view=minecraft-bedrock-stable#getlightlevel)
分別描述 total brightness 與 sky brightness；兩者都能因未載入等原因失敗，也不能在 restricted execution 中呼叫。
油渣既有 before-event 只擷取意圖，延後的正式作用才讀這兩個 API。

adapter 取 `max(total, sky)`，用明確讀出的天空光保留 Java 第二參數 0 的方向。
**這是依文件做的適配推論**：Microsoft 沒有保證該組合在全部夜間、天氣、維度及光照更新時序下
逐值等於 Java raw brightness，這部分維持待原生比對。
不能只看到 API 名称包含 light，就把此差異標成完全閉合。

兩個值都必須是 0–15 的整數。API 不存在、拋錯、返回非有限／非整數／超界值都會中止規劃，
不猜成 0 或 15，不扣物品、不提交已計畫的成熟狀態。
journal 同時保存 total 與 sky；即使最大值沒有變，任一原值變動也會在扣料前拒絕這次提交。

## 纏根泥土與交易次序

Java `RootedDirtBlock` 只問正下方是否為空氣；有效作用固定放置一個 hanging roots，
沒有額外 RNG。Bedrock handler 因此對 `minecraft:dirt_with_roots` 讀取、保存並重驗下方，
只在明確 `minecraft:air` 時寫成 `minecraft:hanging_roots`。
第二次油渣作用看見已有垂根就無效，所以只生成一格、只扣一份；Creative 不扣。

新增植物使用原有單入口、完整手持 ItemStack 快照、兩次規劃／一次結算和回滾隔離。
所有已讀的耕地、鄰株、果實目標、支撐以及根下空間都在提交前逐一重驗完整 permutation。
未知或未載入的鄰位不等於空氣；受影響的全部參與方塊都保留在故障隔離集合。

果實寫入需要早於梗附著。本次在 journal 的 `set` 增加明確的 `afterNeighbors` 選項，
只將成功結瓜的最終梗寫入排到其果實之後；其他既有 handler 的順序保持原來行為。
每個顯式方塊寫入都驗讀回值，失敗時沿用逆序回滾。
這仍是同步盡力回滾；Bedrock 自動鄰居更新、掉落、光照傳播及崩潰後恢復沒有因此變成跨引擎原子交易。

## 檢查與仍未閉合的範圍

本機僅做受影響 JavaScript 語法、diff、官方方法／ID／state／RNG 順序與 source-only 檢查。
没有新增或執行模擬玩家互動測試；完整既有必要來源測試仍交給整合 PR 的 CI。
原生待驗重點是：成熟一次與已成熟拒絕、乾濕耕地、單排與交叉鄰株、被擋的單一方向、
果實與附著梗的原生鄰居更新、夜間／雨雷／維度的光照，以及讀取失敗和回滾後實際世界狀態。
既有通用粒子也不代表已逐一還原 Java 每次施肥的粒子位置、次數或客戶端聲畫。

以下依舊不在此 adapter 的已實作範圍：甜菜的 Bedrock 中間 growth 反解、竹子 stop stage、
其他樹苗／蘑菇／海帶／下界藤與 feature 植物、外部土壤及植物 tag。
特別是甜菜的 0／3／4／7 代表值和竹子丟失 stop stage 的歷史顯示映射，
仍不足以推定其餘原生狀態；本次沒有猜測補齊。
