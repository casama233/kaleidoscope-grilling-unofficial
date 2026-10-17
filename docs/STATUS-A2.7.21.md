# A2.7.21 — Roasted Chicken Wing / 烤雞翅

> Java 基線：Kaleidoscope Grilling 1.1.1 @ `9a1acdab27698457bec16c9362678e574895a28c`。
> 本批補烤雞翅成品與熔爐 / 煙燻爐 / 營火取得。

## Java item

`ROASTED_CHICKEN_WING` 是 `FlavorFoodItem`：

- nutrition = 5
- saturationModifier = 0.12
- texture Git blob SHA-1 = `88d0b45b57a7958f185f9b292eda18d5b57dac42`

`FlavorFoodItem` 本身沒有固定 potion/effect；它做的是：

- `CuisineQualitySupport.foodProperties(...)`
- maxim tooltip
- Cuisine Quality tooltip

因此 Bedrock 本批可精確對齊基礎食物數值，但目前沒有 Cuisine Quality metadata，不能宣稱 quality scaling。

## Chicken Wing input

A2.7.10 已有 Chicken Wing 生存取得。

Java ingredient tag：

`#kaleidoscope_grilling:ingredients/chicken_wings`

鎖定 1.1.1 內容只有：

`kaleidoscope_grilling:chicken_wing`

tag Git blob SHA-1：`308ad7c5d7cc2d5137aa07a0381e785ab6a5caad`。

所以對鎖定 Java 基線，Bedrock recipe 直接 input `kaleidoscope_grilling:chicken_wing` 是精確解析結果。

## 三條 Java recipe

- Furnace：200 ticks，0.35 XP
- Smoker：100 ticks，0.35 XP
- Campfire：600 ticks，0.35 XP

Java recipe Git blob：

- furnace `7227f7b48f3f5edf02b5c26e773ab17e75a262f4`
- smoking `a1eb36ba0ee1cf419a2b5b80035f499061f2f233`
- campfire `38e901f9f4d4232722e87b557ff1133e81daa1cf`

Bedrock 使用一條 stable `minecraft:recipe_furnace` 覆蓋：

- `furnace`
- `smoker`
- `campfire`
- `soul_campfire`

同 A2.7.20：Bedrock stable furnace recipe schema 沒有 `cookingtime` / `experience` 欄位，因此工作站入口可對齊，但 Java 明示 cooking time 和 0.35 XP 不宣稱精確。

## FlavorFoodItem 差異

完成：

- 基礎 nutrition 5
- 基礎 saturation modifier 0.12
- 原生進食

未完成：

- Cuisine Quality 對 food properties 的縮放
- Java maxim / Cuisine Quality tooltip

這些不阻礙主要玩法與生存取得。

## 生存鏈

A2.7.10：

`玩家用 Cookery kitchen knife 擊殺雞 → Chicken Wing`

A2.7.21：

`Chicken Wing → Furnace / Smoker / Campfire → Roasted Chicken Wing`

所以烤雞翅正式成為可生存取得的食物。

## CI

沿用已驗證的增量 published-baseline 模式：

1. 驗證已發布 A2.7.20。
2. 鎖 A2.7.21 Java contract。
3. 套用 A2.7.21。
4. 驗證 item / recipe / texture / survival chain。
5. 官方 Dash v1.2.0 全包編譯。
6. source/dist 逐檔比對。
7. main 才 publish artifact。

仍保持：

- `minecraft_tested=false`
- `bds_tested=false`
