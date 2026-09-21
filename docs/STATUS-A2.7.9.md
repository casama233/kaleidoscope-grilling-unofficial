# A2.7.9 — Beef Chunks / Cookery 牛肉砧板覆寫

> Java 基線：Kaleidoscope Grilling 1.1.1 @ `9a1acdab27698457bec16c9362678e574895a28c`。  
> Cookery Bedrock：1.0.6，公開包 SHA-256 `c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351`。  
> 本批只修 `beef_chunks` 與牛肉砧板衝突，不順帶塞入其他食材。

## Java 真實語義

Java Grilling 在 Cookery namespace 下提供：

`kaleidoscope_cookery:chopping_board/raw_cow_offal`

內容為：

- input: `minecraft:beef`
- cut_count: **4**
- model_id: `kaleidoscope_cookery:raw_cow_offal`
- result: `kaleidoscope_grilling:beef_chunks ×2`

因此它不是新增一條平行 recipe，而是改寫 Cookery 原本牛肉砧板輸出；顯示模型仍故意沿用 Cookery 的 raw cow offal 模型。

`beef_chunks` 本身只是普通 `Item(new Item.Properties())`：

- stack 64
- 非食物
- 無 callback / 特效

## 為什麼不能只用 Extension Recipe API

精確 Cookery Bedrock 1.0.6 中：

`BOARD_RECIPES["minecraft:beef"] = raw_cow_offal ×2 / 4 cuts`

而 directStation 查找順序是：

`BOARD_RECIPES[id] || getExtensionBoardRecipe(id)`

built-in 永遠先命中，所以把 beef recipe 發到公共 `register_recipe` 只會「註冊成功但永遠不會被使用」。

A2.7.9 不再用這種假 parity。

## Grilling 側最小覆寫

沒有修改 Cookery mcaddon，也沒有複製其私有 script。

Grilling 在自己的既有 `playerInteractWithBlock` before-event 流程最前面增加 beef-board adapter：

1. 目標必須是 `kaleidoscope_cookery:chopping_board`。
2. 空砧板 + 主手牛肉：
   - cancel 原 interaction；
   - 只有 first event 才排程一次；
   - `system.run` 後重新驗證 block、station state、selected slot、完整 stack signature。
3. 以 Cookery 自己的 station schema 寫入：
   - `input=minecraft:beef`
   - `cuts=0`
   - `max=4`
   - `result=beef_chunks ×2`
   - `extension=false`
4. Survival 扣 1 個牛肉；Creative 不扣。
5. 後續刀具互動完全回到 Cookery：
   - 4 次耐久切割
   - staged cut state
   - 最後一次 release output
   - 潛行取消返還
   - 拆板 / 爆炸 spill

## 為什麼模型不再是 generic floating item

Cookery 1.0.6 的 native mapping：

`BOARD_MODEL_INDEX["minecraft:beef"] = 0`

而 Java recipe 的 `model_id` 本來就是 `kaleidoscope_cookery:raw_cow_offal`。

A2.7.9 保持 `input=minecraft:beef`，並立即同步：

- `board_has_food=true`
- `board_model=0`
- `extension_board_model=0`
- `cut_stage=0`

所以結構上重用 Cookery 的原生牛肉 staged board model，而不是 A2.7.8 那種第三方 ingredient fallback。

這只能稱為 **結構／映射對齊已驗證**；在使用者實際 Minecraft 客戶端跑過前，仍不把 renderer 寫成實機 PASS。

## 舊世界 migration

若世界裡已有尚未完成的 built-in beef 狀態：

`minecraft:beef -> raw_cow_offal`

第一次再次互動時：

- 該 interaction 被吃掉一次；
- 保留目前 `cuts`；
- 只把 result 改成 `beef_chunks ×2`；
- 不再扣第二份牛肉。

下一次互動由 Cookery 正常繼續。

這避免舊世界在升級後仍產出 raw cow offal。

## 交易安全

新放入採 state / permutation / main-hand 三方 snapshot：

- 先寫 canonical station state；
- 驗證讀回；
- 設定 native board permutation；
- 再提交主手扣除；
- 任一步拋例外，best-effort 回滾：
  - 原手持 stack
  - 原 dynamic-property raw value
  - 原 block permutation

另外 deferred callback 前會比較 selected slot + stack signature；玩家在 before-event 後切換物品，就不再扣物、不寫 state。

## 下游作用

A2.4 的 fixed skewer table 已經存在：

`beef_chunks + red_chili + beef_chunks -> raw_beef_skewer`

所以 `beef_chunks` 一旦真正可取得，牛肉串的固定配方鏈也恢復可達；本批不重寫 skewering 系統。

## CI

A2.7.9 除完整重建 A2.0 → A2.7.8 外，還會下載**精確 SHA-256 的 Cookery 1.0.6 公開包**，只做契約驗證，不發布 Cookery 包本身。

契約 gate 會確認：

- beef native model index = 0
- built-in 優先於 extension 的 lookup
- station key schema
- insertion state schema
- knife completion semantics
- built-in beef = raw_cow_offal ×2 / 4 cuts

若 Cookery 內容與目前 adapter 假設不一致，CI 直接失敗。

仍保持：

- `minecraft_tested=false`
- `bds_tested=false`
- `engine_rendering_verified=false`
