# A2.7.35 — Typed Cookery Oil Pot Block Bridge

本批只收斂一個 Java → Bedrock 差異：**Grilling typed oil 放進 Cookery 油壺後的方塊態生命週期**。

## 為什麼不是再做一個油壺

Java 原作直接 mixin Cookery 的 `OilPotBlock` / `OilPotBlockEntity`；因此 Bedrock 也繼續使用：

- `kaleidoscope_cookery:oil_pot`
- Cookery 的 `kc_oilpot:<dimension>:x,y,z` 方塊存量
- Cookery 的 `kaleidoscope_cookery:has_oil` 視覺有油狀態

不新增第二個 Grilling 油壺方塊。

## Java 1.1.1 鎖定契約

固定 `9a1acdab27698457bec16c9362678e574895a28c`：

- `OilPotBlockEntityMixin`
  - 另存 `GrillingOilType`
  - typed fluid capacity = 64
- `OilPotBlockMixin`
  - 放置時由 ItemStack 複製 oil type 到 block entity
  - 掉落時把 oil type 寫回 ItemStack
  - typed pot 阻止空手抽取與 Cookery native fat 灌入
- `OilFillingHandler`
  - Grilling bucket 對已放置 oil pot 每次加入 8 點
  - 不同油種 / native fat / 超過 64 時拒絕

## Bedrock host 探測結果

Cookery v1.0.6 自己只保存：

- block amount：`kc_oilpot:<dimension>:x,y,z`
- item amount：`kc_oil_count`
- capacity：256

它不知道 `kaleidoscope_grilling:oil_type`，所以 typed pot 若不做 bridge：

1. 放下去會丟油種；
2. 破壞/爆炸拿回來只剩未分類 Cookery pot；
3. Cookery native fat / 空手抽油行為會錯誤介入 typed oil。

## A2.7.35 實作

新增：

- `a2735_typed_oil_pot_block_core.js`
- `a2735_typed_oil_pot_block_runtime.js`

行為：

- typed filled pot 放置後，沿用 Cookery block，額外以 world dynamic property 保存該座標的 Grilling oil type；
- 同時把 host amount 限制在 64；
- 放置偵測同時檢查 clicked / adjacent 兩個候選位置，以兼容 Cookery replaceable placement 與普通放置；
- typed block 上：
  - 空手互動被攔截，避免 Cookery 抽出 native fat；
  - `kaleidoscope_cookery:oil` 被攔截，避免污染；
  - Grilling 三種油桶可直接灌入，每桶 +8；
  - 不同 oil type / native fat / >64 全部拒絕；
- 玩家破壞 typed pot：取消 host 原本的未分類 drop，改為生成保留 type + amount 的 Cookery oil-pot ItemStack；
- 爆炸：從 host impacted list 中抽出 typed pot，再手動破壞並生成保留 type + amount 的 drop，避免 Cookery explosion handler 先丟掉 type。

## 仍未聲稱完成的部分

Java 會把 `OIL_TYPE` 加到 Cookery block state，讓已放置油壺按油種切換視覺。Bedrock 附屬包不能直接向另一包既有 block schema 增加自訂 state；A2.7.35 因此只完成**語義生命週期**，不宣稱完成 placed typed-oil 顏色/模型差異。

另仍未在真 Minecraft client / BDS 實機驗證，因此保持：

- `minecraft_tested=false`
- `bds_tested=false`
