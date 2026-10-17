# A2.7.22 — Cold Houttuynia / 涼拌折耳根

> Java 基線：Kaleidoscope Grilling 1.1.1 @ `9a1acdab27698457bec16c9362678e574895a28c`。
> 本批只補一個小閉環：涼拌折耳根的食物本體、Java 配料/油消耗語義，以及基礎抗火效果。

## Java item

`COLD_HOUTTUYNIA` 是 `EffectFoodItem`：

- nutrition = 6
- saturationModifier = 1.0
- effect = `minecraft:fire_resistance`
- base duration = 1200 ticks = 60 秒
- texture Git blob SHA-1 = `98d59596cc06892e78d6d90d3e8ed2303151f841`

Java 的 `EffectFoodItem` 會透過 Cuisine Quality 調整食物屬性與效果時長。Bedrock 目前仍沒有這套 quality metadata，因此 A2.7.22 對齊基礎 1200 ticks，不宣稱 quality scaling 或原版 tooltip 完成。

## Java 自訂配方

鎖定 Java 的 `ColdHouttuyniaCraftingRecipe` 不是普通 shapeless JSON。它要求：

- 4 個 occupied slots
- 其中恰好 3 格為 `#kaleidoscope_grilling:ingredients/houttuynia`
- 此 tag 在 1.1.1 鎖定基線只解析為 `kaleidoscope_grilling:houttuynia`
- 另外 1 格必須是油壺
- 油型必須是 `premium_chili`
- 油量至少 2
- 合成後保留油壺，只扣 2 點油
- 若扣完為 0，Java `OilPotCompat.consume` 會清空油型

上游 contract pins：

- `ModItems.java` — `6f190e03dc1b7c54bbbae1d5d49d35c78c19b63a`
- `EffectFoodItem.java` — `273712fad21b79049c5db3b16fdeca8076a8ebad`
- `ColdHouttuyniaCraftingRecipe.java` — `e309072bf8b8398317f4b312df59726159848fbe`
- `OilPotCompat.java` — `4264ab947a4222784151fbd50ae84a1a8037d491`
- Houttuynia ingredient tag — `05ca6efd89873ba77e4257404337212c0a416ff1`
- custom recipe stub — `58087181db700f9d5ee8405db63f6333f9d5764c`

## Bedrock 等價層

Bedrock stable recipe JSON 無法依 Cookery 油壺的動態資料判斷油型並只扣其中 2 點，所以這批**沒有**放一條錯誤的普通 shapeless recipe。

改為明確的腳本合成手勢：

1. 蹲下。
2. 對工作台互動。
3. 主手持至少 3 個折耳根。
4. 副手持 Cookery 已裝油油壺，油型為 `premium_chili` 且至少 2 點。
5. 產出 1 份涼拌折耳根，主手扣 3 個折耳根，副手油壺精確扣 2 點；扣至 0 時轉回空油壺。

因此：

- 原料種類：精確
- 原料數量：精確
- 油型：精確
- 油量消耗：精確
- 油壺保留：精確
- Java crafting-grid UI / 任意槽位排列：**不精確，是 Bedrock 平台差異**

這比用一整桶辣椒油替代 2 點油更接近 Java 生存玩法，也不會讓錯誤 native recipe 偷吃掉完整油容器。

## 進食效果

物品使用原生 Bedrock food consumption：

- nutrition 6
- saturation modifier 1.0
- 1.6 秒 eat animation

`itemCompleteUse` 後加 1200 ticks Fire Resistance。Cuisine Quality 的效果時長縮放與 maxim/quality tooltip 仍未移植。

## 生存鏈

已有：

- A2.7.13 / A2.7.14：折耳根加工與作物
- A2.3 / A2.6：高級辣椒油世界油、桶/油壺與機器鏈

本批接成：

`折耳根 ×3 + 高級辣椒油壺 2點 → 涼拌折耳根 → 60秒基礎抗火`

## CI

本批沿用 published-baseline 增量模式：

1. 驗證已發布 A2.7.21。
2. 鎖定 Java A2.7.22 contract。
3. 跑純邏輯測試，覆蓋正確配方、錯油、油不足、材料不足、0 油回空壺。
4. 套用 A2.7.22。
5. 驗證 item / texture / runtime / parity report。
6. 官方 Dash v1.2.0 全包編譯。
7. source/dist 逐檔比對。
8. main 才 publish mcaddon / brproject。

仍保持：

- `minecraft_tested=false`
- `bds_tested=false`

## 下一批候選

高價值且可小批量繼續的 Java 缺口包括：糖拌番茄、花椒蜂蜜、幾個正式菜品、紅薯粥/酸辣粉，以及之後較大的花椒樹/Advanced Rack。純 GUI/Cuisine Quality 類差異繼續單獨標記，不為了「看起來 100%」而虛報。
