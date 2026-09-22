# A2.7.43 — Seasoning Bottle HUD

本批把 Seasoning Bottle 接入 A2.7.39 的共享準星 HUD，同時把原本散在主 runtime 的調料核心常量與放置狀態讀寫收成共用契約。

## Java 對照

固定 Java 1.1.1 / commit `9a1acdab27698457bec16c9362678e574895a28c`：

- `SeasoningBottleHud.java` blob `01856ffcce5dcbeaf304f0f8adffc8a4f1daf667`
- `SeasoningBottleProvider.java` blob `57a0f4d20c6f4c961a9d4f88cb25b0d335687c9b`
- `SeasoningBottleBlockEntity.java` blob `c43cc4e4b8871f345dbe18d8d16bbcae2830bd8d`
- `SeasoningData.java` blob `435d3689b7bb1143d4cca0b0978c053c5ef61413`
- `SeasoningEffects.java` blob `f379ab061b4d9e4421d50cdc0546fbadceced387`

固定契約：

- 單瓶材料容量：8
- 最多堆疊：4 瓶
- 完成調料：16 次使用
- variant：0–7
- 基礎三料：綠辣椒粉、花椒、洋蔥粉
- Buff 類型：speed / strength / duration / totem / vitality / numbness
- numbness 至少 4 份花椒才啟用

## 共用契約

新增：

- `a2743_seasoning_contract_core.js`
- `a2743_seasoning_block_adapter.js`

唯一保存：

- 容量 / 堆疊 / 使用次數 / variant 上限
- item dynamic-property keys
- seasoning block IDs
- 基礎三料
- ingredient → effect kind 映射
- bottle data normalization
- effect preview 計數
- placed bottle stack read/write

主 `main.js` 的調料互動也改走這些共用常量與 adapter，HUD 不再自己 parse 第二份 `sb_...` dynamic property。

## HUD

新增：

- `a2743_seasoning_hud_core.js`
- `a2743_seasoning_hud_provider.js`

顯示最上層瓶：

- 未完成：材料容量 x/8 + 剩餘空位
- 完成：剩餘使用次數
- 基礎三料各自數量
- Buff 預覽
- 花椒不足 4 時顯示 Numb 尚未啟用

variant 不額外顯示；Java HUD 也不把 variant 當文字資訊。variant 仍包含在 HUD signature，變化時會刷新。

## 多瓶差異

Java Jade provider 只在 `bottle.count() == 1` 顯示；Java 自帶 SeasoningBottleHud 則直接讀 top bottle。

Bedrock 本批跟隨自帶 HUD 的語義：對 1–4 瓶堆疊都顯示最上層瓶，因為這才與實際互動對象一致。

## 不重複輪詢

Seasoning provider 不建立：

- `system.runInterval`
- raycast
- dynamic-property parser

仍完全使用 A2.7.39 單一 HUD runtime。

## 驗證限制

- `minecraft_tested=false`
- `bds_tested=false`
