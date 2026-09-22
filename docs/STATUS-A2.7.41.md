# A2.7.41 — 糖拌番茄 + 花椒蜂蜜

本批只補兩個 Java 1.1.1 已有、目前 Bedrock gameplay core 尚未正式存在的食物：

- `sugared_tomato` / 糖拌番茄
- `pepper_honey` / 花椒蜂蜜

不把花椒樹、炒菜、燉菜或 Advanced Rack 混進同一批。

## Java 1.1.1 鎖定契約

固定上游提交：

`breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c`

`ModItems.java` blob：

`a359de5425e3008e728e4790b7bd1b0fe92fbabf`

### 糖拌番茄

Java：

- nutrition = 6
- saturation modifier = 0.65
- shapeless：`c:crops/tomato` + `minecraft:sugar`
- recipe blob：`bd5dbd8d3ed3788e3637e3766d04243c32808cec`

Bedrock 必要前置 Cookery 1.0.6 已提供自己的 `kaleidoscope_cookery:tomato`，因此本附屬直接使用宿主番茄，不建立第二個 tomato item。

Java 的 `c:crops/tomato` 是跨模組 common tag；Bedrock 這批只對 required host 的 Cookery tomato 建立等價配方，因此不宣稱保留任意第三方番茄的 tag 廣度。

### 花椒蜂蜜

Java：

- nutrition = 4
- saturation modifier = 0.25
- shapeless：3 × `sichuan_pepper` + `minecraft:honey_bottle`
- 食用後 `kaleidoscope_grilling:numb` 1200 ticks
- recipe blob：`2eeb3b30c9fd3090605c6c39c681e4d0d0b18a2e`

## Bedrock 實作

新增兩個正式 food item、兩個工作台 shapeless recipe，並直接使用 Java 原作 item texture：

- `sugared_tomato.png` blob `da58483560e98eaeb3abc24973f0c1b247931c65`
- `pepper_honey.png` blob `0a629329dce3bd29c7d56baa5d2ebbf5693d6f6a`

補齊 en_US / zh_CN / zh_TW 名稱與 maxim 翻譯鍵。

## 不重複造 effect listener

A2.7.32 已有單一 `itemCompleteUse` 的 standalone-food effect runtime。

本批只擴充它的 registry：

- Pepper Honey → persistent `numb`, 1200 ticks

沒有新增第二個食物完成事件 listener；現有 A2.1/A2.2 的 `a21_fx` / Numb 玩家動作直接接收這個狀態。

糖拌番茄沒有額外效果，所以不加入 effect registry row。

## Cookery 宿主核驗

CI 固定下載公開的 Kaleidoscope Cookery (Unofficial) v1.0.6：

- CurseForge Project ID 1673664
- File ID 8908596
- SHA-256 `c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351`

並從真實 mcaddon 中確認 `kaleidoscope_cookery:tomato` item 存在；不以 Java Cookery source 代替 Bedrock 宿主契約。

## 仍未宣稱完成的細節

- Java FlavorFoodItem / EffectFoodItem 的 maxim tooltip 文字已提供翻譯鍵，但這批沒有另外造一套 Bedrock hover-tooltip runtime，因此不宣稱 tooltip 顯示 1:1。
- Java common tomato tag 可以接其它相容模組番茄；Bedrock 本批只支援 required Cookery host tomato。
- 尚未 Minecraft client / BDS 實機驗證：`minecraft_tested=false`、`bds_tested=false`。

## 後續內容缺口

完成本批後，內容面的高價值剩餘項目主要是：

1. `houttuynia_stir_fried_pork`
2. `green_pepper_squid_tentacles`
3. `braised_chicken_wings`
4. `potato_beef_stew`
5. `red_sweet_potato_porridge`
6. `sour_spicy_noodles`
7. `wedding_candy` + 原作按上海時區發放/領取規則
8. Pepper Tree 生長 / 掉落 / worldgen（目前只有靜態模型與花椒 item）
9. Advanced Kitchen Rack gameplay

其中 1–6 應優先復用 Cookery 現有烹飪設備/extension recipe host，而不是在 Grilling 重新做一套鍋具。
