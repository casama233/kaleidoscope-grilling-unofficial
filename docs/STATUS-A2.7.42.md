# A2.7.42 — 糖拌番茄 + 花椒蜂蜜

本批只補兩個 Java 1.1.1 已有、目前 Bedrock gameplay core 尚未正式存在的食物：

- `sugared_tomato` / 糖拌番茄
- `pepper_honey` / 花椒蜂蜜

不把花椒樹、炒菜、燉菜或 Advanced Rack 混進同一批。

## Java 1.1.1 鎖定契約

固定上游提交：`breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c`

- `ModItems.java` blob：`a359de5425e3008e728e4790b7bd1b0fe92fbabf`
- 糖拌番茄：nutrition 6，saturation modifier 0.65，`c:crops/tomato + minecraft:sugar`
- 糖拌番茄 recipe blob：`bd5dbd8d3ed3788e3637e3766d04243c32808cec`
- 花椒蜂蜜：nutrition 4，saturation modifier 0.25
- 花椒蜂蜜：3 × `sichuan_pepper` + `minecraft:honey_bottle`
- 花椒蜂蜜：食用後 `kaleidoscope_grilling:numb` 1200 ticks
- 花椒蜂蜜 recipe blob：`2eeb3b30c9fd3090605c6c39c681e4d0d0b18a2e`

## Bedrock 實作

必要前置 Cookery 1.0.6 已提供 `kaleidoscope_cookery:tomato`，因此直接使用宿主番茄，不建立第二個 tomato item。

新增：

- `sugared_tomato` food item + shapeless recipe
- `pepper_honey` food item + shapeless recipe
- Java 原作兩張 16×16 item texture
- en_US / zh_CN / zh_TW 名稱與 maxim 翻譯鍵

紋理固定：

- `sugared_tomato.png` blob `da58483560e98eaeb3abc24973f0c1b247931c65`
- `pepper_honey.png` blob `0a629329dce3bd29c7d56baa5d2ebbf5693d6f6a`

Java 的 `c:crops/tomato` 是跨模組 common tag；Bedrock 這批只對 required host 的 Cookery tomato 建立等價配方，不宣稱支援任意第三方番茄。

## 不重複造 effect listener

A2.7.32 已有單一 `itemCompleteUse` standalone-food effect runtime。

本批只擴充既有 registry：

- Pepper Honey → persistent `numb`, 1200 ticks

沒有新增第二個食物完成事件 listener；現有 A2.1/A2.2 `a21_fx` / Numb 玩家動作直接接收狀態。

糖拌番茄沒有額外效果，所以不加入 effect registry row。

## Cookery 宿主核驗

CI 固定下載公開 Kaleidoscope Cookery (Unofficial) v1.0.6：

- CurseForge Project ID 1673664
- File ID 8908596
- SHA-256 `c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351`

並從真實 mcaddon 中確認 `kaleidoscope_cookery:tomato` item 存在。

## 尚未宣稱 1:1 的細節

- maxim tooltip 已有翻譯鍵，但本批沒有另造 Bedrock hover-tooltip runtime。
- Java common tomato tag 的跨模組廣度未移植。
- `minecraft_tested=false`
- `bds_tested=false`

## 本批後的 Java item 缺口

對 pinned Java `ModItems` 與目前 Bedrock `behavior_pack/items` 做檔名級核對後，本批前明確缺 9 個 Java 註冊 item；補掉這兩個後剩：

1. `houttuynia_stir_fried_pork`
2. `green_pepper_squid_tentacles`
3. `braised_chicken_wings`
4. `potato_beef_stew`
5. `red_sweet_potato_porridge`
6. `sour_spicy_noodles`
7. `wedding_candy`

非 item 註冊層的主要內容缺口仍包括：

- Pepper Tree 生長 / 掉落 / worldgen
- Advanced Kitchen Rack gameplay

其中六道鍋料理應優先復用 Cookery 現有設備與 extension recipe host，不在 Grilling 重做一套鍋具。
