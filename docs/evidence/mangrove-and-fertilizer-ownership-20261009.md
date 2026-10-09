# 紅樹施肥分支與肥料回復所有權

核對日期：2026-10-09。本頁增量納入 [G122](../STATUS-A2.8.122.md)，接續 G120 並由 G121 保留的 23 個 handler ID，加入紅樹葉、
**乾燥且懸掛的**紅樹胎生苗兩個有限入口，合計 25 個 ID；
並修復原植物 journal 在未知回復結果下仍退肥料、回復覆蓋其他寫入的問題。
地植紅樹長樹、含水胎生苗，以及本頁列出的其他植物仍未實作。
ID 計數不表示該植物的所有狀態、原生施肥、保存或客戶端表現已完整還原。

## 本次來源與狀態證據

作者基準仍為 [Grilling 1.1.1／9a1acdab27698457bec16c9362678e574895a28c](https://github.com/breezeth-CN/KaleidoscopeGrilling/tree/9a1acdab27698457bec16c9362678e574895a28c)。
兩個維護分支的 `OilResidueItem.useOn` 均在原使用位置執行兩次骨粉作用，
任何一次接受便合計扣一份油渣，Creative 保留物品。
本次沿用[先前記錄](vanilla-plant-fertilizer.md#來源與可重現輸入)的官方 JAR、
官方 mappings 及已驗 SHA-1 的輸入，以 CFR 0.152 只讀解碼下面的方法。
官方原始檔與解碼輸出放在倉庫外，不打入發布包。

| 方法 | Forge／Minecraft 1.20.1 符號與原始行數 | NeoForge／Minecraft 1.21.1 符號與原始行數 |
| --- | --- | --- |
| `MangroveLeavesBlock.isValidBonemealTarget` | `cue.a`／17 | `dks.b`／25 |
| `MangroveLeavesBlock.isBonemealSuccess` | `cue.a`／22 | `dks.a`／30 |
| `MangroveLeavesBlock.performBonemeal` | `cue.a`／27–28 | `dks.a`／35–36 |
| `MangrovePropaguleBlock.isValidBonemealTarget` | `cuf.a`／128 | `dkt.b`／138 |
| `MangrovePropaguleBlock.isBonemealSuccess` | `cuf.a`／133 | `dkt.a`／143 |
| `MangrovePropaguleBlock.performBonemeal` | `cuf.a`／138–143 | `dkt.a`／148–153 |
| `MangrovePropaguleBlock.isFullyGrown` | `cuf.n`／150 | `dkt.n`／160 |
| `createNewHangingPropagule` | `cuf.b`／154、158–160 | `dkt.c/b`／164、168–170 |

Bedrock 正式 ID／state 仍用 Mojang
[`bedrock-samples` v1.26.50.4／46ba6ea985fb5a92d79a9419198f10dda14c199d](https://github.com/Mojang/bedrock-samples/tree/46ba6ea985fb5a92d79a9419198f10dda14c199d)。
[官方 block metadata](https://github.com/Mojang/bedrock-samples/blob/46ba6ea985fb5a92d79a9419198f10dda14c199d/metadata/vanilladata_modules/mojang-blocks.json)
列出 `minecraft:mangrove_leaves` 的 `persistent_bit`、`update_bit`，
以及 `minecraft:mangrove_propagule` 的布林 `hanging` 和整數 `propagule_stage=0..4`。

不能把舊版 Geyser 將 Java sapling STAGE 投影到 `propagule_stage` 的資料繼續當成現用映射。
此次另讀取 Geyser 自己的**當前 generator 固定提交**
[`bfafbeb990d8c53f6a0c1accea6d5f622f134277`／`BlockMappers.java`](https://github.com/GeyserMC/mappings-generator/blob/bfafbeb990d8c53f6a0c1accea6d5f622f134277/src/main/java/org/geysermc/mappings/definitions/block/state/BlockMappers.java)。
取得的原文已對上 Git blob `68bd7366ca93f421afc7f07060d4ad20d40deeff`。
這份來源明確把 `MangrovePropaguleBlock.HANGING` 直接映射、把 **AGE** 映到 `propagule_stage`。
相應[現用 mappings 說明](https://github.com/GeyserMC/mappings/blob/0fd435d3d4617dd458c6ee0e6889a5245483bf5f/README.md)
標示 Java 26.2／Bedrock 1.26.50；本次只用它佐證現用 Bedrock 的狀態表示，
玩法依然是上表已分別解碼的 Minecraft 1.20.1 與 1.21.1。

## 葉下生成與懸掛成熟

兩版原方法在這一分支一致：葉子只查正下方空氣，生成 `HANGING=true, AGE=0` 的苗；
懸掛苗未到 4 時骨粉必定成功，每次 AGE 增加 1；沒有長樹 RNG 或 feature 呼叫。

| 原始目標／狀態 | 油渣第一次 | 同一原始目標的第二次 | 肥料結算 |
| --- | --- | --- | --- |
| 紅樹葉，正下方為明確乾燥空氣 | 下方生成 `hanging=true, propagule_stage=0` | 原目標仍是葉子；下方已非空氣，因此無效 | 合計 1 份 |
| 紅樹葉，下方非空氣 | 無效 | 無效 | 不扣 |
| 乾燥懸掛苗，stage 0 | 0→1 | 1→2 | 合計 1 份 |
| 乾燥懸掛苗，stage 1 | 1→2 | 2→3 | 合計 1 份 |
| 乾燥懸掛苗，stage 2 | 2→3 | 3→4 | 合計 1 份 |
| 乾燥懸掛苗，stage 3 | 3→4 | 成熟，無效 | 合計 1 份 |
| 懸掛苗，stage 4 | 成熟，無效 | 無效 | 不扣 |
| `hanging=false`、含水、未知／越界 age | 未接入這個有限分支 | 不執行替代長樹 | 不扣 |

普通骨粉使用相同 handler 時只有一次作用；Creative 不扣。
對葉子施肥不會順便成熟剛生成的苗，因為作者兩次呼叫保留原始點擊位置。
苗的第二次作用读取 journal 的第一次結果，不重讀並重用舊 age。
未載入的下方、未知水狀態或不能解析的正式 permutation 會中止整筆規劃。

## 乾燥邊界也屬於 journal 快照

實际 [`@minecraft/server` 2.9.0 declarations](https://www.npmjs.com/package/@minecraft/server/v/2.9.0)
以及 Mojang 相同固定 tree 的 bindings 已核對 `Block.isWaterlogged`、
`Block.setPermutation`、`World.getEntity`、`Entity.id/isValid/remove`、
`ItemStack.clone/isStackableWith`。沒有使用僅在新 preview 文件出現的 setter。

紅樹這兩個入口要求可寫位置的 `isWaterlogged` 明確為 `false`。
`undefined`、非布林值或 getter 拋錯都不視為乾燥；`true` 也不進入這次適配。
這個布林值和完整 permutation 一起保存，扣料前重驗，真正寫入前及寫後再次驗證，
回復時同樣參與 before／after 所有權判斷。
不呼叫 `setWaterlogged(false)` 強行清水，也不把布林狀態當成完整液體層。

水狀態在規劃／提交前變成未知時，沒有成本或生長提交。
若原生寫入已嘗試後才出現含水或其他未知狀態，回復不能冒充成功，
這次已扣的肥料保留、相關位置隔離，等待實際世界證據處理。

## 修復的共用守恆缺口

原 `commitSteps` 在逆序回復某一步失敗後，仍會繼續回復其他步驟。
植物 journal 原先把肥料扣除放第一步，回復又直接把原手持快照寫回，形成兩個確定的缺口：

1. 方塊、掉落或其移除結果未知，肥料仍退回，可能留下有產出而未付費的一次作用。
2. 手持槽在成本扣除後已被另一個寫入改變，回復仍覆蓋它，可能損失另一個物品或錯退肥料。

新增 `plant_fertilizer_transaction_core.js`，只供現有植物入口使用，未改動通用 `commitSteps`。
它把植物／掉落回復結果與肥料回復條件綁在同一同步交易內：

- 每個明確方塊／手持寫入先讀回其 preimage，再嘗試寫入並驗證 after。
  寫入拋錯即走回復，不把 `void` 或例外當成功。
- 回復看到精確 before，表示此快照已回復，不再補寫；看到精確 after 才有條件寫回 before。
  其他值、讀取失敗、未知 precondition 或未建立寫入所有權都保留現狀並報為回復錯誤。
- setter 寫完才拋錯時，回復後再次讀到精確 before 才確認回復成功。
  setter 靜默忽略、仍為 after 或返回第三種值都不會得到成功回復認定。
- 任一植物／掉落回復拒絕或拋錯，肥料補償不再執行。其餘步驟仍按原順序盡力回復，
  並沿用 `commitPlantSteps` 對全部已讀／已寫參與位置的故障隔離。
- 全部產物與方塊都已確認回復，才以原生 ItemStack 克隆恢復原手持。
  不能取得原槽或槽中已是另一份資料時，不覆寫、不往其他槽補發。

為保持瓜梗及其他已支援植物的原生鄰位更新順序，方塊寫入接受「仍是原 before」，
或「已被先前步驟更新成**精確計畫 after**」兩種狀態。
其他非計畫狀態不會被強行覆蓋。這依然是同步、以可讀快照為界的所有權保護；
相同值被移除又重建等 ABA 情況沒有額外的原生世界版本序號可供證明。

粉紅花簇、雙高花的原有掉落也加上 entity ID／`World.getEntity` 的讀回確認。
逆序移除前再次查同一 entity ID、有效性及完整可堆疊物品相等；
被拾取、合併、改量、改資料或無法讀取的掉落不會當作自己已移除，也不會刪掉改變後的物品。
只有此次移除後 `getEntity(id)===undefined` 才確認移除完成。

物品比對使用 type、amount 加原生 `isStackableWith`，沒有加入可見 lore／ID 推導完整 NBT 的降級比對。
這些肥料及新增／既有花類掉落均是可堆疊物品；原生比較不支持或拋錯時保守失敗。
JavaScript clone／storage 回歸不能證明每種原生資料跨重啟的保存行為。

## 剩餘植物的精確缺口

這次有重新查**當前** generator；沒有只重述歷史映射，也沒有把證據不足叫成引擎必然做不到。

| 未接入範圍 | 已確認的 Java／Bedrock 資料 | 真正還欠的契約 |
| --- | --- | --- |
| 甜菜根 | 兩版 `BeetrootBlock.getBonemealAgeIncrease` 分別為 `cpi.a`／57、`dft.a`／65：沿用 2–5 隨機整數後整除 3，可能有效而增齡 0。當前 generator 仍只給 Java 0/1/2/3→Bedrock 0/3/4/7。 | Mojang metadata 列出原生 growth 0–7；官方材質只列四張 stage 圖，不能由圖數或單向代表值反推 1、2、5、6 的玩法階段。尚缺可驗證的中間狀態讀／寫與原生成長契約。 |
| 竹子／竹筍 | 兩版 `BambooStalkBlock` 同時有 AGE、LEAVES、STAGE；有效性看整株高度＜16 及頂端 STAGE≠1，單次抽 1–2 格。當前 generator 把 AGE→粗細、LEAVES→葉型，**STAGE 始終輸出 age_bit=false**。 | `age_bit` 確實存在，不能宣稱 Bedrock 缺少這個布林欄位。generator 的視覺投影故意丟失 STAGE；其註解對服務端跳 tick 的用途也只是推测，還不能證明 true/false 與停止施肥／自然生長的完整對應。竹筍第一作用長成竹後第二作用會進入此分支，不能只接半套。 |
| 海帶 | 兩版每次骨粉延長 1 格；`canGrowInto` 要 Java WATER，fluid amount=8 是放置條件而不是骨粉條件。Bedrock 主方塊 water／flowing_water 都有 liquid_depth 0–15；kelp 有 age 0–25。 | 需要完整保存與還原水主層／第二液體層、流態和原生 fluid update。Block 與 Structure 的 waterlogged 讀取都只回布林，尚不能用它驗證精確原水層。 |
| 地植紅樹／其他 feature 植物 | 2.9.0 有 `Dimension.placeFeature/placeFeatureRule`。原 Java 樹、蘑菇、苔蘚等各有目標有效性、選 feature、RNG、空間和替換規則。 | API 沒有提供通用骨粉呼叫或 feature 實際寫入 journal；仍需逐植物計畫、完整原位保存、寫後驗證及回復，不能直接宣稱 feature 呼叫等於兩次骨粉。 |

海帶這次還查了 `StructureManager.createFromWorld` 和 `Structure`。
後者提供 `getBlockPermutation(location)`、`getIsWaterlogged(location): boolean`、
`setBlockPermutation(location, permutation, waterlogged?: boolean)`；
它的 `ISerializable` 基底在實際 2.9.0 bindings 沒有公開序列化方法，不能假設存在 raw NBT accessor。
[Microsoft Structure 文件](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/structure?view=minecraft-bedrock-stable)
也沒有給第二液體層的精確 permutation getter。
這不排除未來用可驗證的原生結構快照完成水體回復，卻不足以把目前布林回讀當成該證據。

## 驗證與限制

本機檢查為改動 JavaScript 語法、diff、官方 Java 方法／Mojang state／固定 SDK 核對，
以及 `test_plant_fertilizer_storage.mjs` 的 **7 個純 storage 回歸**。
回歸直接調用實際 production helpers，涵蓋扣料先／後拋錯、精確全回復、
方塊／掉落回復失敗仍保留成本、不同槽所有者不覆寫、靜默未回復、
第三種原生狀態隔離及舊的相同 debit 不被冒領退款。
沒有新增或執行模擬玩家互動測試，也沒有本機重跑完整 verify_current。
整合 PR 保留全部既有必要 CI，並加掛這個具體守恆故障的 storage 檢查。

仍須原生確認紅樹葉下放置／懸掛生長、主副手、Creative、載入邊界、
隱含鄰位更新／掉落、物品合併與拾取、故障隔離跨保存／重載，以及粒子與手機聲畫。
原生自動更新可能影響 journal 外的方塊；同步回復、記憶體隔離及既有持久標記
不構成伺服器崩潰時的原子提交保證。`client=false`、`production_ready=false` 維持不變。
