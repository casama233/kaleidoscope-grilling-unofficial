# A2.7.45 — Skewer Recipe HUD Provider

本批把掛牆 Skewer Recipe 的 Java Jade 資訊接入 A2.7.39 共用準星 HUD，不新增配方儲存層。

## Java 對照

固定 Java 1.1.1 / commit `9a1acdab27698457bec16c9362678e574895a28c`：

- `SkewerRecipeProvider.java` blob `b7e215c8100cdd81e317c0b4ed127376fc2b07e1`
- `SkewerRecipeBlockEntity.java` blob `3b0ea57caa94eb139421cb7e9c14165eebe76d57`

Java Jade 顯示：

- 記錄的烤串
- 記錄烤串的小圖示與名稱
- 所需食材
- 食材小圖示
- 「木棍右鍵掛牆串譜可快速串簽」提示

## 重點：復用 A2.5 Recipe Book 狀態

A2.5 已經有完整鏈：

`readRecipeBlock() -> restoreStack() -> readBookRecord() -> bookIngredientSlots()`

A2.7.45 只在同一 runtime 封裝一個只讀：

`a25ReadRecipeBlockSnapshot(block)`

它回傳：

- `resultId`
- A2.5 已解析好的 `ingredientSlots`

HUD 不直接讀：

- `BOOK_RECORD_KEY`
- world dynamic property
- recipe block JSON
- recorded book JSON

因此固定配方與秘制串都繼續使用 A2.5 原本的材料邏輯。

## UI 適配

Java Jade 可以畫 item elements；Bedrock actionbar RawMessage 沒有同等 item icon element。

本批不建立假的 icon API，而是用本地化物品名稱：

- 原版：`minecraft:golden_apple -> item.golden_apple.name`
- 自訂：`kaleidoscope_grilling:... -> item.kaleidoscope_grilling:....name`

所以 HUD 仍可讀地顯示「記錄串類 + 食材 + 掛牆用法」，並保留完整 recipe/ingredient signature。

## 不重複輪詢

provider 不建立：

- `system.runInterval`
- raycast
- dynamic-property parser

全部走 A2.7.39 共用 HUD runtime。

## 下一步

HUD/Jade 小缺口進一步減少後，應回到較大的 gameplay parity：

- Advanced Rack
- automation / compat APIs
- Java Create / Maid / refrigerator 等整合的 Bedrock 等價策略

這些不應以「再造 Java API」的方式硬搬，需要優先復用 Cookery/Bedrock 已有容器與 Script API。

## 驗證限制

- `minecraft_tested=false`
- `bds_tested=false`
