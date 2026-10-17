# 下界藤油渣施肥與海帶阻塞點

核對日期：2026-10-09。這是[瓜梗／纏根泥土增量](stem-and-rooted-dirt-fertilizer-20261009.md)之後的第二批植物修復。
新增 `minecraft:twisting_vines`、`minecraft:weeping_vines` 兩個正式 ID，handler 總數由 21 類增至 23 類。
本頁記錄來源已核對的方向、尋端、age、RNG 與 journal 規劃；不代表已通過原生施肥或客戶端驗收。

## 作者與官方 Minecraft 方法

作者基準維持 [Grilling 1.1.1／9a1acdab27698457bec16c9362678e574895a28c](https://github.com/breezeth-CN/KaleidoscopeGrilling/tree/9a1acdab27698457bec16c9362678e574895a28c)。
`OilResidueItem.useOn` 對同一個原始使用位置呼叫兩次骨粉作用，任何一次接受便合計扣一個油渣，Creative 保留物品。
本次不能把第二次作用固定在第一次的舊末端；Java 第一格已經可能由 head 變為 body。

兩版官方 JAR／mappings 的來源與 SHA-1 沿用[植物來源記錄](vanilla-plant-fertilizer.md#來源與可重現輸入)。
下列方法均已從同一批驗證輸入以 CFR 0.152 只讀解码，原始 JAR 和輸出仍在倉庫外。

| 原版方法 | Java 1.20.1 符號／原始行數 | Java 1.21.1 符號／原始行數 |
| --- | --- | --- |
| `BlockUtil.getTopConnectedBlock` | `l.a`／243–253 | `l.a`／243–253 |
| `GrowingPlantBodyBlock.isValidBonemealTarget` | `csz.a`／60–61 | `djm.b`／64–65 |
| `GrowingPlantBodyBlock.performBonemeal` | `csz.a`／71–77 | `djm.a`／75–81 |
| `GrowingPlantHeadBlock.isValidBonemealTarget` | `cta.a`／91 | `djn.b`／95 |
| `GrowingPlantHeadBlock.performBonemeal` | `cta.a`／101–114 | `djn.a`／105–118 |
| `NetherVines.isValidGrowthState` | `cur.a`／11 | `dle.a`／11 |
| `NetherVines.getBlocksToGrowWhenBonemealed` | `cur.a`／15–21 | `dle.a`／15–21 |
| `TwistingVinesBlock` 長度／可長入 | `cyf.a/g`／17、27 | `dos.a/g`／25、35 |
| `WeepingVinesBlock` 長度／可長入 | `cyu.a/g`／17、27 | `dpn.a/g`／25、35 |

Java twisting vines 的建構方向是 `Direction.UP`，weeping vines 是 `Direction.DOWN`。
`GrowingPlantBodyBlock` 沿该方向穿過相連 body，找到 matching head，再把施肥委派給 head；
中途遇見別的植物、空隙或障礙，不會跨越去尋另一株。

## Bedrock 狀態與 head／body 轉換

正式 ID／完整 state schema 來自 Mojang
[`bedrock-samples` v1.26.50.4／46ba6ea985fb5a92d79a9419198f10dda14c199d](https://github.com/Mojang/bedrock-samples/tree/46ba6ea985fb5a92d79a9419198f10dda14c199d)，
其[官方 block metadata](https://github.com/Mojang/bedrock-samples/blob/46ba6ea985fb5a92d79a9419198f10dda14c199d/metadata/vanilladata_modules/mojang-blocks.json)
對兩種藤各列出一個 ID、各自一個整數 age state，值域均為 0–25；沒有另外的 body ID 或竹子式 stop stage。

[Geyser 開發者的固定 mappings](https://github.com/GeyserMC/mappings/blob/cc3afdc9b4a3d495c34d9c5e92819b9af8805c88/blocks.json)
另提供以下一對一 age 與 body 代表值。這份映射只作跨版本狀態佐證，未替代目前 Bedrock 引擎的原生驗收。

| Java | Bedrock |
| --- | --- |
| `twisting_vines[age=0..25]` | `minecraft:twisting_vines`，`twisting_vines_age=0..25` |
| `twisting_vines_plant` | 同一個 `minecraft:twisting_vines`，body 代表值 `twisting_vines_age=0` |
| `weeping_vines[age=0..25]` | `minecraft:weeping_vines`，`weeping_vines_age=0..25` |
| `weeping_vines_plant` | 同一個 `minecraft:weeping_vines`，body 代表值 `weeping_vines_age=0` |

因此 adapter 以連接關係分辨末端，不能以 age=0 判斷 body：真正的 head 也可能為 age=0。
從原始目標沿生長方向讀相連同 ID，最後一格是此次委派的 head，下一格決定可否生長。
每格 age 都必須是 0–25 整數；不修剪、取模或猜测異常資料。

新一格長出後，前一個 head 在虛擬 journal 中轉成 body 代表值 0；新 head 的 age 增加一，最多 25。
連續長多格時，中間新增格再轉成 body，只有最後末端保留其增齡值。
**age=25 仍可施骨粉**：原版骨粉有效性只查下一格能否長入；age=25 停止的是自然 random growth。
本次不替換 Bedrock 的自然 random tick。

## 長度 RNG、空間與第二次作用

`NetherVines` 的長度概率從 1 開始，每次抽樣成功就加一格並乘以 0.826，直到一次失敗。
完整長度先抽出，再按順序試放；每個新格僅能進入明確空氣。
前方遇見非空氣就停止該次生長，不穿透、不轉彎，也沒有任意的固定長度或高度截斷。
有效起始目標的第一次抽樣概率為 1，因此在正常 `Math.random()` 契約下至少規劃一格。
Java RNG 與 JavaScript RNG 序列不同；本次還原抽樣條件與概率，沒有宣稱世界 seed 序列相同。

第二次油渣作用仍由原來被點擊的方塊出發。它沿 journal 第一次作用後的虛擬同 ID 鏈，
尋找剛生成的新末端，再套用完全相同規則。
若第一次已長到障礙旁，第二次看見障礙便無效，但第一次仍可完成、總共只扣一個油渣。

所有被讀的既有鏈節、末端、空氣以及障礙都保存完整 permutation，提交前逐格重驗。
不能讀取、未載入、返回空 handle 或超出 Bedrock 可讀世界範圍會中止整筆規劃，
不將未知值當作空氣，也不提交第一個作用的半套結果。
這是交易守恆的有限適配；它沒有假定 Java 與 Bedrock 在世界高度邊界具有相同可放置範圍或扣料結果。

實際方塊更新仍經原有 acknowledged write、逆序回滾與所有 participant 的故障隔離。
只操作兩種藤的明確 permutation，不新增 helper entity、物品資料、持久鍵、feature generator 或第二個事件入口。
Bedrock 自動鄰居更新、可能的自然破壞／掉落，以及回滾後引擎的實際保存狀態仍須原生驗收。

## 海帶為何仍未加入

兩版 `KelpBlock` 已核對：每次骨粉固定延長 **1 格**，body 同樣向上尋 head。
`canGrowInto` 只要求 Java `Blocks.WATER`；原碼中 fluid amount=8 的條件位於
`getStateForPlacement`，不能錯套成骨粉生長條件。

| 海帶方法 | 1.20.1 | 1.21.1 |
| --- | --- | --- |
| `canGrowInto` | `cto.g`／28 | `dkc.g`／37 |
| `getBlocksToGrowWhenBonemealed` | `cto.a`／53 | `dkc.a`／62 |
| `getStateForPlacement` | `cto.a`／59–63 | `dkc.a`／68–72 |

Bedrock 的 `minecraft:kelp` 雖有完整 `kelp_age=0..25`，但水同時涉及主方塊
`minecraft:water`／`minecraft:flowing_water` 的 `liquid_depth`，以及含水植物的水體保存。
現有 journal 只保存／寫回 BlockPermutation；它尚未建立「原水位／流態 → 含水海帶 → 回滾原水體」的完整交易。
[`Block.isWaterlogged`／`setWaterlogged`](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/block?view=minecraft-bedrock-stable#setwaterlogged)
是含水狀態介面，单一布林值並不能自行證明精確液體層的回復。

因此沒有把海帶套進本次只處理空氣的下界藤 adapter。仍需先確認 Bedrock 放置含水海帶和恢復流動／靜止水、
液體層及原生 fluid update 的完整契約，才有足夠依據做出可回滾入口。

## 本機檢查與待驗收

本機範圍只有 JS 語法、diff、模組註冊、正式 ID／state 及兩版原始方法核對。
已逐一比對兩種藤的 26 個 head age、body 代表值和方向。
沒有新增／執行模擬玩家互動，也沒有把純規則／來源核對當作原生操作證據。
完整既有必要來源測試仍由整合 PR 的 CI 處理。

需要原生驗收的重點包括任意 body 點擊、age25、兩次作用尋新末端、受阻長度、主副手／Creative、
長鏈及區塊邊界、原生鄰居更新與失敗回滾，還有粒子位置／次數和實際聲畫。
甜菜中間 growth、竹子 stop stage、海帶流體交易、其他 feature 植物與外部 tag 仍未閉合。
