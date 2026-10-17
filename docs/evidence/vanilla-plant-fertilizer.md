# 原版植物油渣適配：Java 方法與 Bedrock 狀態

核對日期：2026-10-09（香港）。本頁對應 `plant_fertilizer.js` 的有限原版植物適配，
以及 `a26_oil_machine_runtime.js` 傳入實際物品 ID 的單一施肥入口。
這是來源／資料核對；沒有執行模擬玩家互動，也沒有宣稱 BDS 原生操作或客戶端已接受。

## 來源與可重現輸入

模組規格維持作者 [1.1.1／9a1acdab27698457bec16c9362678e574895a28c](https://github.com/breezeth-CN/KaleidoscopeGrilling/tree/9a1acdab27698457bec16c9362678e574895a28c)。
[Forge OilResidueItem](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/forge-1.20.1/src/main/java/cn/breezeth/kaleidoscope_grilling/oil/OilResidueItem.java)
與 [NeoForge OilResidueItem](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/oil/OilResidueItem.java)
的方法一致：兩次呼叫 `super.useOn`；任何一次 `consumesAction()` 為真，生存模式總共扣一個油渣；
Creative 保留原數量。有效目標沒有生長、沒有掉落，與無效目標是不同結果。

原版方法來自 Mojang 官方 JAR，下載後逐項驗 SHA-1，再以官方 mappings 和 CFR 0.152 只讀解碼。
以下 JAR、mappings、解码输出及原始第三方資料保存在倉庫外，不隨包發布。

| Minecraft | 檔案 | SHA-1／官方下載 |
| --- | --- | --- |
| 1.20.1 | client JAR | [`0c3ec587af28e5a785c0b4a7b8a30f9a8f78f838`](https://piston-data.mojang.com/v1/objects/0c3ec587af28e5a785c0b4a7b8a30f9a8f78f838/client.jar) |
| 1.20.1 | client mappings | [`6c48521eed01fe2e8ecdadbd5ae348415f3c47da`](https://piston-data.mojang.com/v1/objects/6c48521eed01fe2e8ecdadbd5ae348415f3c47da/client.txt) |
| 1.21.1 | client JAR | [`30c73b1c5da787909b2f73340419fdf13b9def88`](https://piston-data.mojang.com/v1/objects/30c73b1c5da787909b2f73340419fdf13b9def88/client.jar) |
| 1.21.1 | client mappings | [`2244b6f072256667bcd9a73df124d6c58de77992`](https://piston-data.mojang.com/v1/objects/2244b6f072256667bcd9a73df124d6c58de77992/client.txt) |

例如 `SweetBerryBushBlock` 在兩版分別是 `cxr.class`、`doc.class`。
下載 [CFR 0.152](https://www.benf.org/other/cfr/cfr-0.152.jar)，抽出該 class，
以 `java -jar cfr-0.152.jar doc.class --extraclasspath client.jar --outputdir decoded` 查看方法，
再透過同版 mappings 還原符號。下表的行數來自 Mojang mappings 中的原始方法範圍。

| 方法 | 1.20.1 符號／原始行數 | 1.21.1 符號／原始行數 |
| --- | --- | --- |
| `BoneMealItem.growCrop` | `cdu.a`／66–81 | `csq.a`／70–84 |
| `ServerPlayerGameMode.useItemOn` | `aih.a`／322–368 | `aqw.a`／327–380 |
| `CocoaBlock.performBonemeal` | `cqt.a`／144–145 | `dhf.a`／152–153 |
| `SweetBerryBushBlock.performBonemeal` | `cxr.a`／130–132 | `doc.a`／146–148 |
| 甜莓先處理物品／採果 | `cxr.a`／93–110 | `doc.a`／102–108、113–126 |
| `PinkPetalsBlock.performBonemeal` | `cuy.a`／81–88 | `dll.a`／112–118 |
| `CaveVinesBlock.performBonemeal` | `cqj.a`／80–81 | `dgv.a`／86–87 |
| `CaveVinesPlantBlock.performBonemeal` | `cqk.a`／63–64 | `dgw.a`／68–69 |
| `TallFlowerBlock.performBonemeal` | `cxs.a`／29–30 | `dod.a`／36–37 |
| `TallGrassBlock.performBonemeal` | `cxt.a`／38–43 | `doe.a`／46–51 |
| `BushBlock.mayPlaceOn` | `cpv.d`／18 | `dgh.b`／22 |
| `Block.popResource`／掉落規則 | `cpn.a`／358–365、387–394 | `dfy.a`／366–373、395–402 |

Bedrock ID、狀態名稱與型別使用 Mojang 的
[`bedrock-samples` v1.26.50.4／46ba6ea985fb5a92d79a9419198f10dda14c199d](https://github.com/Mojang/bedrock-samples/tree/46ba6ea985fb5a92d79a9419198f10dda14c199d)：
[mojang-blocks.json](https://github.com/Mojang/bedrock-samples/blob/46ba6ea985fb5a92d79a9419198f10dda14c199d/metadata/vanilladata_modules/mojang-blocks.json)、
[mojang-items.json](https://github.com/Mojang/bedrock-samples/blob/46ba6ea985fb5a92d79a9419198f10dda14c199d/metadata/vanilladata_modules/mojang-items.json)、
[blocks.json](https://github.com/Mojang/bedrock-samples/blob/46ba6ea985fb5a92d79a9419198f10dda14c199d/resource_pack/blocks.json) 與
[terrain_texture.json](https://github.com/Mojang/bedrock-samples/blob/46ba6ea985fb5a92d79a9419198f10dda14c199d/resource_pack/textures/terrain_texture.json)。
這些原始檔已與該固定 Git tree 的 blob SHA 比對。

Java age／flower_amount 到 Bedrock state 的歷史映射，另以 Geyser 開發者自己的
[`GeyserMC/mappings` cc3afdc9b4a3d495c34d9c5e92819b9af8805c88／blocks.json](https://github.com/GeyserMC/mappings/blob/cc3afdc9b4a3d495c34d9c5e92819b9af8805c88/blocks.json)
交叉核對。此提交是其 1.20.5 映射，僅作映射佐證；Mojang 現用 schema／ID 仍吻合，
不等於已在 Bedrock 1.26.50 操作驗收。不能從 schema 容許 `growth=0..7`，推定每個植物都在 7 成熟。

## 本次新增的明確契約

| 輸入植物／正式 Bedrock ID | 單次 Java 骨粉作用 | 油渣的兩次作用及入口 |
| --- | --- | --- |
| 可可 `minecraft:cocoa` | `age<2` 才有效，固定 +1，沒有生長 RNG。 | 初始 0 可到 2；初始 1 第一次成熟、第二次無效；都只扣一個。`direction` 及其餘原狀態保留。 |
| 甜莓 `minecraft:sweet_berry_bush` | Java age 0–3 對 Bedrock `growth=0..3`；有效作用固定 +1，到 3 成熟。 | **主手非潛行**時，初始 0／1 攔截油渣，兩次可到 2／3；初始 2／3 讓原生採果先處理，油渣不扣。潛行或實際副手 use 的規則見下文，age 2 可施肥到 3。入口條件只檢查一次，第一次長到 2 不會把第二次作用改成採果。 |
| 粉紅花簇 `minecraft:pink_petals` | Java flower_amount 1–4 對 `growth=0..3`。不足 4 份加一份；已滿則掉一個同物品。 | 初始 `growth=2`：長滿後掉一個；初始 3：規劃兩次獨立的一個物品掉落。保留 `minecraft:cardinal_direction`。`doTileDrops=false` 不掉物，但兩次仍是有效作用，總共扣一個。 |
| 無果洞穴藤 `minecraft:cave_vines` | head／body 方法都只設 `BERRIES=true`，不延長藤蔓。 | 下鄰仍為藤蔓時轉 `minecraft:cave_vines_body_with_berries`，否則轉 `minecraft:cave_vines_head_with_berries`；保留 `growing_plant_age` 與位置。第二次看見已有果實，不再作用。含果 ID 不註冊，原生採果保留。 |
| 向日葵／紫丁香／玫瑰叢／牡丹：`minecraft:sunflower`、`minecraft:lilac`、`minecraft:rose_bush`、`minecraft:peony` | `TallFlowerBlock` 在任一半都是有效目標，每次向地面掉一個同種花；`Block.popResource` 尊重 `doTileDrops`。 | 完整匹配的上／下半均可使用，油渣規劃兩次獨立掉落。兩半的 `upper_block_bit` 和完整 permutation 都入快照；對應半不存在、類型被換或狀態不一致時不扣料、不產出。 |
| 短草／蕨：`minecraft:short_grass`、`minecraft:fern` | 目標與作用成功判斷都是 true；實際生長還要能存活且上方空氣，才放置雙高草／大蕨。 | 有空間時變為 `minecraft:tall_grass`／`minecraft:large_fern` 的上下半；第一個作用完成後，第二個目標已不是短草 handler。空間被實體方塊堵住時不長大，但兩次仍是有效作用，生存扣一個、Creative 不扣。 |

甜莓的特殊入口来自兩版 Java 的精確判斷：原版只對 **`Items.BONE_MEAL` 這個 ID** 略過未成熟甜莓的採果。
`OilResidueItem` 繼承類別，並不會讓它的 item ID 等於骨粉。
本次玩法主對照維持 NeoForge 1.21.1：`ServerPlayerGameMode.useItemOn` 在潛行且有手持物品時略過區塊互動；
非潛行的 `useWithoutItem` 也只在主手分支觸發。因此實際潛行／副手 item-use 可以對 age 2 施肥，
age 3 則仍是無效骨粉目標、不扣料、不把本次 item-use 改成採果。
**Forge 1.20.1 有分支差異**：其舊 `BlockState.use` 會收到當前 hand，非潛行副手也有區塊採果判斷。
本次没有把這兩個呼叫链標示成完全相同，也沒有重建 Java 客戶端先主手後副手的整套選擇流程。

`hasPlantFertilizer(block,itemId,hand,secondaryUse)` 同時供 before-event 與 `usePlantFertilizer` 最初取得物品後使用，
避免新增 caller 繞過這個優先序；before-event 保存的潛行狀態在 deferred 執行時重驗，原有 hand／雙手快照驗證繼續保留。
`usePlantFertilizer` 提交前也重驗初始潛行狀態。內部兩次 handler 仍按骨粉規則執行，不中途重跑採果入口。

短草的土壤取兩版官方 `#minecraft:dirt`：dirt、grass_block、podzol、coarse_dirt、mycelium、rooted_dirt、
moss_block、mud、muddy_mangrove_roots，再加 `BushBlock` 明列的 farmland。
Java `rooted_dirt` 使用 Bedrock 的正式 `minecraft:dirt_with_roots`；其餘保持相同 ID。
這些對應 ID 全部存在於上述現用 Bedrock metadata。外部模組添加的土壤 tag 沒有通用橋接。

## 一次交易中的保存與未知結果

沿用原有唯一事件入口、油渣兩次／骨粉一次、完整 ItemStack 比對與 Creative 語義。
生長 journal 現在同時記住「讀取但不改動」的鄰位，以及實際寫入的方塊；
提交前重验手持完整資料、目標與所有已讀鄰位的完整 permutation。
任一讀取返回未載入、無法讀取或已被替換，都不把它當作空氣。

扣料、方塊更新及本批掉落在同一 `commitSteps` 中結算，失败回滾已嘗試步驟。
掉落保留每次 `spawnItem` 的 handle，確認 entity 有效且物品及數量與計畫相符才承認交付；
回滾還需確認該 entity 已移除。未知 spawn／移除結果或回滾失敗會保留恢復標记。
隔離涵蓋所有參與方塊；雙高花的另一半不能繞過未知交付後的封鎖。

掉落位置使用 Java `Block.popResource` 的 +/-0.25 區塊內偏移及 item 半高偏移；
Bedrock 的原生拾取時序、掉落運動、方塊鄰居更新與聲畫仍需原生驗收。
這是同步盡力回滾，不是對任意伺服器崩潰提供跨引擎原子交易。已隔離資料必須依世界證據恢復。

## API 邊界與明確未加入

已核對發布使用的 [`@minecraft/server` 2.9.0](https://www.npmjs.com/package/@minecraft/server/v/2.9.0)
實際 TypeScript declarations；其官方 tarball SHA-1 為 `be4764c752d180b35edac475bcd017886ec5ce71`。
該版本有 [`Dimension.placeFeature`／`placeFeatureRule`](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/dimension?view=minecraft-bedrock-stable#placefeature)，
但沒有通用 bone-meal／fertilize 呼叫。`placeFeature` 需要指定 feature，沒有提供 Java 目標有效性、
植物特有 RNG、特徵選擇及可回滾寫入清單，所以本次沒有用它或 `runCommand` 偽裝骨粉操作。

- **甜菜未加入。** Java 的增齡為 `floor(random integer 2..5 / 3)`，存在有效但增齡 0 的結果。
  歷史映射給 Java 0／1／2／3 對 Bedrock 0／3／4／7 的代表值，但不足以證明原生中間狀態如何反解。
  不把 0–7 直接当 Java age，也不自行猜一組分段公式。
- **南瓜／西瓜梗未加入。** `StemBlock.performBonemeal` 長到 7 後還會呼叫當次 `randomTick`，
  涉及光照、耕地速度、隨機方向、果實放置及梗狀態。僅加齡會漏掉原作行為。
- **竹子未加入。** Java 有獨立的停止生長 stage、厚度、葉型與最多 16 格的整株規則；
  歷史顯示映射丟棄了部分 stage，不能據此推定 Bedrock `age_bit` 是完整等價狀態。
- 其他樹苗、蘑菇、海帶、下界藤、苔蘚／草地 feature、水下植被、豬籠草及外部植物仍需各自適配。
  G118 原有四作物、花椒苗、小麥、胡蘿蔔與馬鈴薯的 handler 繼續保留。

## 本機檢查範圍

本次僅做受影響 JS 語法、diff 完整性、兩版 Java 方法、官方 Bedrock ID／狀態／物品與 SDK 符號核對。
沒有新增或執行模擬玩家互動測試；完整既有來源／canonical 必要檢查由整合 PR 的 CI 處理。
原生載入、正常玩家施肥與採果、上下半交互、跨區塊／重載及手機聲畫均維持待驗收。
