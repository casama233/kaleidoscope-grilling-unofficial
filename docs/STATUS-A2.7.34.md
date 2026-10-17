# A2.7.34 — Cookery Oil Contract Fix / 油壺基建契約修正

本批是基建排查修復，不新增內容。

## 排查發現

A2.7.30 曾宣稱已把三個正式 oil-pot consumer 收到一個 adapter，但 A2.7.34 再掃 active runtime 時發現漏了：

- a23_oil_world.js

因此實際是 **4 個** consumer，不是 3 個。

a23_oil_world.js 仍自己：

- 讀 kaleidoscope_grilling:oil_type
- 讀 kc_oil_count
- 建立 kaleidoscope_cookery:oil_pot_filled
- 寫 lore / type / count

這就是第 4 套油壺契約。

## 更重要的語義混用

一次性 probe 直接讀固定 SHA 的 Cookery v1.0.6：

### 一般手持 ItemStack

oilPot.js：

itemOil(stack)

對 kc_oil_count 缺失採：

- 0

### 舊 filled pot 放成方塊

oilPot.js 的 placedItemOil()
與 replaceablePlacement.js 的 oilAmountFromItem()

對 filled item 缺失 kc_oil_count 採：

- 256

這是專門給 legacy placement 的 fallback。

A2.7.30 把「一般手持讀取」和「legacy placement fallback」混成同一個 read，導致一般消耗場景也可能憑空把缺失 count 的壺視為滿壺。

## Java 原作

固定基線 OilPotCompat.java：

- blob 4264ab947a4222784151fbd50ae84a1a8037d491
- FAT_CAPACITY = 256
- FLUID_CAPACITY = 64
- getCount() 缺失 component → 0

所以一般手持/消耗讀取採 0 同時符合：

- Java Grilling
- Cookery Bedrock v1.0.6 itemOil()

## A2.7.34

新增 corrected adapter：

- a2734_cookery_oil_pot_core.js
- a2734_cookery_oil_pot_adapter.js

明確分成：

- readCookeryOilPot()
  - 正常手持語義
  - missing count → 0

- readCookeryOilPotForPlacement()
  - legacy placement compatibility
  - missing filled count → capacity

正式 consumer 全部切到 A2.7.34：

1. main.js — 烤架刷油
2. a26_oil_machine_runtime.js — Big Vat
3. a2722_cold_houttuynia_runtime.js — 涼拌折耳根
4. a23_oil_world.js — 世界油源灌 Cookery 油壺

A2.7.30 adapter 保留作歷史 slice 重建，但不再是 active dependency。

## 原生 fat 不再被重標

舊 a23_oil_world：

若 filled pot 沒有 grilling oil type，只看 currentType 空字串，
可能把已有 Cookery native fat 的壺直接重新標成 canola / chili oil。

A2.7.34：

- untyped + count > 0 → native_fat，拒絕灌 Grilling typed oil
- empty pot / untyped count 0 → 可灌
- same typed oil → 可疊加
- different typed oil → 拒絕
- typed capacity 固定 64

這避免附屬模組破壞宿主內容。

## 目前剩餘基建重複

下一輪優先：

1. 玩家手位 / 背包 / Creative helper
   - main / plate / oil machine / crop / beef board / cold food 重複

2. faceOffset / 座標 key / Dynamic Property position key
   - plate / oil machine / oil world / main 重複

3. 每個 slice 的 manifest version / Dash / package / publish workflow 樣板
   - 歷史 workflow 保留
   - 新 slice 應改走 shared helper

仍保持：

- minecraft_tested=false
- bds_tested=false
