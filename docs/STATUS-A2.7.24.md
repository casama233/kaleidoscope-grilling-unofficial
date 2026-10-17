# A2.7.24 — 紅辣椒粉＋秘製辣椒油生存入口

> Java 基線：Kaleidoscope Grilling 1.1.1 @ `9a1acdab27698457bec16c9362678e574895a28c`。
> 本批在已發布 A2.7.23 創造欄整理之上，補「紅辣椒加工 → 秘製辣椒油」完整生存鏈。

## Java item 與創造欄順序

`RED_CHILI_POWDER` 是普通 ingredient item，預設 64 堆疊。

Java `ModCreativeTabs` 對未特殊處理的內容按 `ModItems.ITEMS` 註冊順序輸出。鎖定 1.1.1 中順序是：

`canola_powder → red_chili_powder → onion`

因此 Bedrock A2.7.23 的「森羅物語：煙火」折疊群組同步插入此位置，群組總條目由 76 變 77；不讓新物品重新散落到普通創造欄。

texture Git blob SHA-1：

`57936897efae12b743a539f0bf1dac54d45dda39`

## Cookery 磨石加工

Java：

`kaleidoscope_cookery:red_chili → Millstone → kaleidoscope_grilling:red_chili_powder ×1`

recipe Git blob：

`986d4c5930293b380f984f1cecfb0d0d661d5540`

Bedrock 沿用已驗證的 Cookery 1.0.6 公開 extension API：

- `api_ready`
- capability `millstone`
- `register_recipe`
- 不額外發第二個 api ping
- 不改 Cookery 私有腳本

CI 會下載固定 SHA-256 的 Cookery 1.0.6，確認 `kaleidoscope_cookery:red_chili` 及 millstone extension path 仍存在。

## 秘製辣椒油配方

Java 是普通 shapeless：

- `canola_oil_bucket ×1`
- `red_chili_powder ×3`
- → `secret_chili_oil_bucket ×1`

recipe Git blob：

`a8bf9c6b177a9b943829e68179ff2b06c9123b0e`

沒有動態 NBT 或 Forge-only 條件，因此 Bedrock 直接使用原生 `minecraft:recipe_shapeless`，原料種類與數量可精確對齊。

## 生存鏈閉環

A2.3 / A2.6 已有秘製辣椒油的世界油、桶、大缸、Cookery 油壺與烤串刷油支援，但先前沒有正式生存製作入口。

A2.7.24 後：

`Cookery 紅辣椒 → 磨石 → 紅辣椒粉 ×3 + 菜籽油桶 → 秘製辣椒油桶 → 世界油 / 大缸 / 油壺 / 烤串`

因此秘製辣椒油正式從「已註冊功能」變成「可生存取得功能」。

## Create 差異

Java 另有 Create milling recipe（processing time 100）。目前目標 Bedrock 包沒有已鎖版本且可驗證的 Create compatibility API，因此不偽造此支援；Cookery Millstone 已足以完成模組本身的生存鏈。

## CI

1. 驗證已發布 A2.7.23 Creative Catalog。
2. 鎖 Java ModItems / ModCreativeTabs / millstone / secret chili oil / texture contract。
3. 驗證固定 Cookery 1.0.6 red chili + millstone extension。
4. 跑純邏輯測試。
5. 生成 item / texture / shapeless recipe / runtime。
6. 驗證創造群組 77 項與 Java 註冊相鄰順序。
7. 檢查全部 gameplay JS 語法。
8. 官方 Dash v1.2.0 編譯並逐檔比對。
9. main 才發布 mcaddon / brproject。

仍保持：

- `minecraft_tested=false`
- `bds_tested=false`
