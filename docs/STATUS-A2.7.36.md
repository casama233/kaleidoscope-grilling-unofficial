# A2.7.36 — Typed Cookery Oil Pot Block Bridge

本批只收斂一個 Java → Bedrock 差異：**Grilling typed oil 進入 Cookery 油壺後的方塊態生命週期**。

## 不再造一個油壺

Java 原作直接擴充 Cookery 的 `OilPotBlock` / `OilPotBlockEntity`；Bedrock 同樣繼續使用宿主：

- `kaleidoscope_cookery:oil_pot`
- `kc_oilpot:<dimension>:x,y,z`
- `kaleidoscope_cookery:has_oil`

A2.7.36 沒有新增第二個 Grilling 油壺。

同時直接復用前一批 A2.7.35 的 `a2735_player_io.js`，沒有把 main/offhand/creative helper 再複製一套回來。

## Java 1.1.1 鎖定契約

固定 commit `9a1acdab27698457bec16c9362678e574895a28c`：

- `OilPotBlockEntityMixin`
  - 保存 `GrillingOilType`
  - typed fluid capacity = 64
- `OilPotBlockMixin`
  - 放置時由 ItemStack 複製 oil type 到 block entity
  - 掉落時把 oil type 寫回 ItemStack
  - typed pot 阻止空手抽取與 Cookery native fat 灌入
- `OilFillingHandler`
  - Grilling bucket 對已放置 oil pot 每次 +8
  - 不同油種、native fat、超過 64 均拒絕

## Cookery Bedrock 1.0.6 鎖定契約

固定 mcaddon SHA-256：

`c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351`

宿主本身：

- block capacity = 256
- item amount key = `kc_oil_count`
- block amount key = `kc_oilpot:<dimension>:x,y,z`
- 玩家破壞掉落在 `world.afterEvents.playerBreakBlock`
- 爆炸掉落在 `world.afterEvents.blockExplode`

因此 A2.7.36 可以在 before-event 對 typed pot 接管破壞/爆炸，再生成保留 Grilling type 的 Cookery pot，且不會與宿主 after-event 雙掉落。

## A2.7.36 行為

- typed filled pot 放置後仍生成 Cookery oil-pot block，額外按座標保存 Grilling oil type；
- typed amount 限制為 64；
- 放置偵測同時檢查 clicked/adjacent 候選，兼容 Cookery replaceable placement 與普通放置；
- typed pot：
  - 空手交互被攔截，避免 Cookery 把內容當 native fat 抽出；
  - `kaleidoscope_cookery:oil` 被攔截，避免污染；
  - 三種 Grilling 油桶可直接灌入，每桶 +8；
  - 不同 oil type / native fat / >64 拒絕；
- 玩家破壞：取消原破壞，清理宿主 count + Grilling type，再生成保留 type/count 的 Cookery oil-pot ItemStack；
- 爆炸：從 impacted blocks 中移除 typed pot，再手動破壞和生成保留 type/count 的 drop，因此 Cookery 的 after-event 不會再生成未分類壺。

## 尚未完成

Java 把 oil type 加入 Cookery block state，能讓已放置油壺按油種切換視覺。Bedrock 的附屬包不能直接向依賴包既有 block schema 追加新的 custom state，所以本批只聲稱完成**語義生命週期**；placed typed-oil 顏色/模型差異仍是後續項。

仍未經真 Minecraft client / BDS 實機驗證：

- `minecraft_tested=false`
- `bds_tested=false`
