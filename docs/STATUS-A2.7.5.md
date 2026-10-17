# A2.7.5 — 烤架輸入與核心互動加固

> 本批只修核心烤架互動，不新增食材、菜品或 processing recipe。  
> Java 基線：Kaleidoscope Grilling 1.1.1 @ `9a1acdab27698457bec16c9362678e574895a28c`。  
> Bedrock：`@minecraft/server 2.9.0`。

## 1. 長按使用鍵不再重複執行

Bedrock `PlayerInteractWithBlockBeforeEvent.isFirstEvent` 會區分：

- 首次按下：`true`
- 按住按鍵後的連續事件：`false`

A2.7.4 以前沒有使用這個欄位，因此 Grill、調料瓶、對方塊穿串與蹲下整理容器都有被長按重複觸發的真機風險。

A2.7.5：

- 首次事件才真正執行操作；
- 後續 hold-repeat 對我方 custom target 仍 cancel，避免掉進其他原生互動；
- 穿串對方塊亦只在首次事件排程一次。

這是本批最重要的真機輸入修正。

## 2. Java shovel 熄火語義

Java `GrillBlock` 使用：

`#kaleidoscope_cookery:extinguish_stove`

Cookery Java data 將該 tag 定義為 `#minecraft:shovels`，並把 Kitchen Shovel 加入 shovel tag。

A2.7.5 支援：

- wooden_shovel
- stone_shovel
- iron_shovel
- golden_shovel
- diamond_shovel
- netherite_shovel
- `kaleidoscope_cookery:kitchen_shovel`
- Bedrock Cookery 可見的 `kaleidoscope_cookery:oiled_kitchen_shovel` alias

烤架 lit 時持上述工具互動會：

- `lit=false`
- 保留 phase / flips / food / seasoning state
- 停止 tick cooking
- 播放熄火音效

Java 對 Kitchen Shovel 內部「有油」狀態還會清油；Bedrock Cookery 沒有公開 host API 讓 Grilling 安全修改這份私有狀態，因此 A2.7.5 不碰其 private data，只保證熄火。

## 3. 可以先刷油再點火

Java `GrillAutomationApi.brushOil` 檢查：

- phase == 0
- 至少一串
- 油量足夠

但**沒有要求 LIT=true**。

因此 Java 可：

放串 → 刷油 → 點火 → 翻面

A2.7.4 以前 Bedrock 額外要求先點火。A2.7.5 移除這個錯誤限制；烤架未點火時刷油後 phase 進 1，但 `tickState` 在 `lit=false` 時不推進烹飪時間，直到真正點火。

## 4. Flint & Steel 耐久

Java `ignite` 成功點火後會 `hurtAndBreak(1)`。

A2.7.5 使用 stable `minecraft:durability` component：

- 生存模式成功點火：damage +1
- 到 maxDurability：工具消失並播 break sound
- Creative：不扣
- unbreakable：不扣
- 已點火的烤架再次點擊：不扣

## 5. 本批刻意不做

- 新食材／菜品／加工配方
- entity interaction repeat（stable `PlayerInteractWithEntityBeforeEvent` 沒有 `isFirstEvent`）
- Cookery private oiled-shovel metadata
- automation lease / maid / Create 等 Java-only integration
- Minecraft / BDS 實機 PASS 宣稱

## 6. 驗證

CI 從 A2.0 完整重建到 A2.7.4，再套 A2.7.5，並驗證：

- 6 個 vanilla shovel + Cookery shovel selector
- hold-repeat gating
- durability edge cases
- generated `core_logic.brush` 可在 unlit phase 0 成功
- A2.7.4 Java 原 GUI icon 不回退
- A2.7.3 grill helper 不回退
- 全 gameplay JS `node --check`
- 官方 Dash v1.2.0
- source / dist 逐檔比較
- mcaddon / brproject 打包

仍保持：

- `minecraft_tested=false`
- `bds_tested=false`
