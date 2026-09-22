# A2.7.49 — 糖拌番茄 + 花椒蜂蜜

本批不重做舊 PR #46；直接復用它已驗證的 Java/Cookery 契約與原作素材，重新基於已發布 **A2.7.48 Pepper Tree Lifecycle** 收口兩個尚未進主幹的 Java 食品：

- `sugared_tomato` / 糖拌番茄
- `pepper_honey` / 花椒蜂蜜

## Java 1.1.1 固定契約

固定上游：`breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c`

- `ModItems.java` blob `a359de5425e3008e728e4790b7bd1b0fe92fbabf`
- 糖拌番茄：nutrition 6 / saturation modifier 0.65
- 糖拌番茄：`c:crops/tomato + minecraft:sugar`
- recipe blob `bd5dbd8d3ed3788e3637e3766d04243c32808cec`
- 花椒蜂蜜：nutrition 4 / saturation modifier 0.25
- 花椒蜂蜜：3 × `sichuan_pepper` + `minecraft:honey_bottle`
- 花椒蜂蜜：食用後 `numb` 1200 ticks
- recipe blob `2eeb3b30c9fd3090605c6c39c681e4d0d0b18a2e`
- 原圖 blob：
  - Sugared Tomato `da58483560e98eaeb3abc24973f0c1b247931c65`
  - Pepper Honey `0a629329dce3bd29c7d56baa5d2ebbf5693d6f6a`

## Cookery 復用

Cookery 1.0.6 已有 `kaleidoscope_cookery:tomato`，所以 Bedrock 配方直接使用宿主番茄，不建立第二個 tomato item。

CI 固定 Cookery 1.0.6 SHA-256：

`c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351`

並實際掃描 mcaddon 確認 tomato item 存在。

Java 的 `c:crops/tomato` 是跨模組 common tag；目前 required host 是 Cookery，因此本批只聲明 Cookery tomato 等價，不假稱支援任意第三方番茄。

## 不覆蓋 A2.7.47 Wedding Candy

舊 #46 的 effect core 基線早於 Wedding Candy，不能直接拿來覆蓋主幹。

A2.7.49 改為：

1. 新增小型 `a2749_sugared_tomato_pepper_honey_core.js`
2. 只向現有 `a2732_standalone_food_effect_core.js` 追加 `pepperHoneyEffectRow()`
3. 保留既有：
   - Roasted Sweet Potato / Warmth
   - Cold Houttuynia / Fire Resistance
   - Wedding Candy / Invincible
4. 沿用同一個 `a2732_standalone_food_effect_runtime.js`

所以沒有新增第二個 `itemCompleteUse` listener。

## 內容

- 2 個正式 food item
- 2 個 Java 對應 shapeless recipe
- 2 張 pinned Java 原圖
- en_US / zh_CN / zh_TW 名稱與 maxim key
- 正式加入現有 Grilling item catalog
- Pepper Honey 的 `numb` 1200 ticks 接回現有 A2.1/A2.2 Numb 玩家狀態與動畫

## 尚未宣稱

- maxim 翻譯已存在，但沒有偽造 Java hover-tooltip API。
- Java common tomato tag 的跨模組廣度未完整複刻。
- `minecraft_tested=false`
- `bds_tested=false`

## 本批後食品 ID 缺口

完成後，先前確認的獨立 Java 食品 ID 只剩：

- `houttuynia_stir_fried_pork`
- `green_pepper_squid_tentacles`
- `braised_chicken_wings`
- `potato_beef_stew`
- `red_sweet_potato_porridge`
- `sour_spicy_noodles`

其中前三個可直接復用已驗證的 Cookery v1 `wok` extension API；後三個復用 `stockpot_exact` / `stockpot_flex`。
