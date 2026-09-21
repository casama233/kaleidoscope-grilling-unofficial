# A2.7.20 — Roasted Sweet Potato / 烤番薯

> Java 基線：Kaleidoscope Grilling 1.1.1 @ `9a1acdab27698457bec16c9362678e574895a28c`。
> 本批補烤番薯成品、熔爐/煙燻爐/營火取得與基礎 Warmth 效果。

## Java item

`ROASTED_SWEET_POTATO` 是 `EffectFoodItem`：

- nutrition = 6
- saturationModifier = 0.2
- effect = `kaleidoscope_cookery:warmth`
- base duration = 600 ticks = 30 秒
- texture Git blob SHA-1 = `cc8bda808a99d38ecdae90a78a3acf6b7c0dea9a`

Java `EffectFoodItem` 會經 `CuisineQualitySupport.effectDuration` 調整效果時間。
目前 Bedrock port 沒有 Cuisine Quality metadata，因此本批只對齊**基礎 600 ticks**，不虛報 quality scaling。

## Bedrock 食物行為

這個 item 不加入串燒 `FOOD_DATA`，避免錯用串燒進食動畫。

它使用原生 `minecraft:food`：

- nutrition 6
- saturation modifier 0.2
- 正常 eat animation
- 原生 hunger/saturation consumption

另由 `a2720_roasted_sweet_potato_runtime.js` 在 `itemCompleteUse` 後寫入既有：

`kaleidoscope_grilling:a21_fx -> warmth`

若既有 Warmth 比 600 ticks 更長，不會被縮短。

因此可直接復用 main runtime 已有的 Warmth 行為。

## 三條 Java recipe

Java：

- Furnace：200 ticks，0.35 XP
- Smoker：100 ticks，0.35 XP
- Campfire：600 ticks，0.35 XP

三條 input tag 在鎖定基線解析為單一：

`kaleidoscope_grilling:sweet_potato`

Bedrock stable `minecraft:recipe_furnace` 支援 station tags，因此用一條 recipe 覆蓋：

- `furnace`
- `smoker`
- `campfire`
- `soul_campfire`

其中 `soul_campfire` 也符合 Java 的 campfire cooking recipe type 使用範圍。

Bedrock stable furnace recipe schema沒有 `cookingtime` 或 `experience` 欄位，所以：

- 正確工作站入口：完成
- 原生工作站時間：交由 Bedrock station mechanics
- Java 明示 0.35 XP：無直接 JSON 欄位，未宣稱精確

## Java contract pins

- `ModItems.java` `6f190e03dc1b7c54bbbae1d5d49d35c78c19b63a`
- `EffectFoodItem.java` `273712fad21b79049c5db3b16fdeca8076a8ebad`
- Sweet Potato ingredient tag `e37d8276f40197bd99d85733b6cb3ec9d6a9b44e`
- Furnace recipe `955b5e820c82345ce9c1f2b4defde40161098ca5`
- Smoking recipe `9c275528d8bb4dadec89bc64ec97a4c24ada4ca7`
- Campfire recipe `e455f4bedef55ccc8d291100765cebd838b7d5cd`

## 生存鏈

A2.7.19 已有：

`草帽打短草 → Sweet Potato → 種植/繁殖`

A2.7.20 新增：

`Sweet Potato → Furnace / Smoker / Campfire → Roasted Sweet Potato → Warmth`

所以烤番薯已正式成為可生存取得的有效食物。

## CI

沿用增量 published-baseline 模式：

1. 驗證已發布 A2.7.19。
2. 鎖 Java A2.7.20 contract。
3. 套用 A2.7.20。
4. 驗證原生 food、recipe、Warmth runtime。
5. 官方 Dash v1.2.0 全包編譯。
6. source/dist 逐檔比對。
7. main 才 publish artifact。

仍保持：

- `minecraft_tested=false`
- `bds_tested=false`
