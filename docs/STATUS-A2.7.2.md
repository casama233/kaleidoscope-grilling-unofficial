# A2.7.2 — Cookery 紅薯加工 adapter：Millstone + Chopping Board

> Java 基線：Kaleidoscope Grilling **1.1.1**，鎖定 `breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c`。  
> Bedrock：26.51 / content 1.26.50 / `@minecraft/server 2.9.0`。  
> Cookery Bedrock：**1.0.6**，公開原包 SHA-256 `c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351`。

A2.7.2 是 A2.7 的第二個小切片，只補 A2.7.1 紅薯粉／生苕皮相鄰的兩條 Cookery 加工流程，不擴張到其他菜品或整批 recipe。

## 1. 本輪重新核對的實包 API

不是猜 Cookery 方塊 ID 或私下 import 它的 scripts。

本輪用公開 CurseForge 1.0.6 檔案重新核對，下載檔 SHA-256 與此前實包審計完全一致。該包自帶 `documentation/KC_EXTENSION_API.md`，公開 Extension Recipe API v1：

- `kaleidoscope_cookery:api_ping`
- `kaleidoscope_cookery:api_ready`
- `kaleidoscope_cookery:register_recipe`

1.0.6 的 `api_ready` capability 包含 `chopping_board` 與 `millstone`。配方只存在當次 world session；移除 addon 後重載不留幽靈 recipe。Cookery 內建 recipe 優先，同一 `kind + source + recipe.id` 重複註冊是安全覆蓋。

A2.7.2 因此只透過這個公開 Script Event API 註冊，不 import / 修改 Cookery 私有腳本。

## 2. 紅薯物品

新增正式 gameplay item：

`kaleidoscope_grilling:sweet_potato`

對齊 Java `ModItems.SWEET_POTATO`：

- nutrition：3
- saturation modifier：0.1
- 最大堆疊：64
- 原作貼圖直接從鎖定 Java commit 取得，Git blob SHA-1：`6761c2d89d46df2e536dd6df3fe9fdb7c2262259`

Java 這個 item 同時是 `ItemNameBlockItem`，可放置 Sweet Potato Crop。A2.7.2 **只補物品與加工輸入**；作物種植、生長、收成仍是 A2.8，不把尚不存在的 Bedrock crop 假裝完成。

## 3. Cookery Millstone

Java：

`#kaleidoscope_grilling:ingredients/sweet_potatoes -> sweet_potato_powder x1`

鎖定 Java tag 實際只有：

`kaleidoscope_grilling:sweet_potato`

Bedrock 透過 Cookery API 註冊：

- kind：`millstone`
- input：`kaleidoscope_grilling:sweet_potato`
- output：`kaleidoscope_grilling:sweet_potato_powder x1`
- chance：1.0

因此直接使用 Cookery 1.0.6 自己的正常 Millstone 容量、動物綁定、加工、物品展示與出料，不另造第二套磨盤。

## 4. Cookery Chopping Board

Java：

- input：`sweet_potato_powder`
- cut count：**4**
- output：`raw_sweet_potato_sheet x1`

Bedrock 透過 Cookery API `chopping_board` kind 註冊相同 input / result / count / cuts。外部食材使用 Cookery 的 generic item-display fallback，因此不用修改 Cookery RP。

### 第二刀聲音差異

Java Grilling 另有 `ChoppingBoardBlockEntityMixin`：

- 當前食材是 sweet potato powder；
- `currentCutCount == 2`；
- 將該刀聲音替換成 `BUCKET_EMPTY`。

Cookery Extension Recipe API v1 沒有 per-cut sound 欄位。A2.7.2 **不覆寫 Cookery 主機腳本**只為模仿一個聲音，因此：

- 4 刀、產物與機器行為：已對齊；
- Java 第二刀特殊倒水聲：仍是明確的 audio-only 差異。

若未來 Cookery 公開 stage-sound hook，可再無侵入補上。

## 5. 註冊時序

Grilling 啟動後只發 `api_ping`。收到：

`kaleidoscope_cookery:api_ready`

才解析 `api=1` 與 `capabilities`：

- 有 `chopping_board` 才註冊砧板 recipe；
- 有 `millstone` 才註冊磨盤 recipe；
- 沒宣告 capability 就不猜；
- 非 API v1 不送 recipe。

目前 Gameplay Core manifest 本身仍硬依賴 Cookery 1.0.6，這層 capability gating 是額外防護與未來相容邊界。

## 6. 本輪沒有做

- Create Milling 的 100 tick sweet-potato → powder 路徑。
- Sweet Potato Crop 種植／生長／收成。
- 其他 chopping / pot / stockpot / flex / crushing / roasting 等 recipes。
- Java 第二刀 BUCKET_EMPTY 特殊聲。
- 其他缺失基礎食材與 12 道菜。
- Minecraft / BDS 實機驗收。

## 7. A2.7.2 後主要 Java 差異

基礎／加工物品剩：

`beef_chunks`, `canola_seeds`, `carrot_dice`, `chicken_skin`, `chicken_wing`, `houttuynia`, `minced_houttuynia`, `onion`, `potato_slice`, `raw_mantou_slice`, `red_chili_powder`, `squid_tentacle`。

`sweet_potato`, `sweet_potato_powder`, `raw_sweet_potato_sheet` 已 gameplay 化。

菜品仍缺：

`cold_houttuynia`, `pepper_honey`, `roasted_chicken_wing`, `roasted_sweet_potato`, `sugared_tomato`, `wedding_candy`, `houttuynia_stir_fried_pork`, `green_pepper_squid_tentacles`, `braised_chicken_wings`, `potato_beef_stew`, `red_sweet_potato_porridge`, `sour_spicy_noodles`。

其他大項仍是 Advanced Rack、四種 crop、Pepper tree/worldgen、其餘 processing recipes、21 advancements 等價層、Guide 動態內容、Plate 每根串 renderer，以及 Minecraft/BDS/多人實機驗收。

## 8. 驗證

A2.7.2 測試會鎖定：

- 公開 API v1 event 名稱。
- capability gating。
- Java sweet-potatoes tag 的唯一實際 selector。
- Millstone 1:1 input/output/chance。
- Chopping Board 4 cuts / count 1。
- 重複 `api_ready` 可安全重新註冊。
- sweet_potato food 數值與原貼圖 blob。
- 從 A2.0 → A2.7.2 的完整回歸。
- 官方 checksum-pinned bridge. Dash v1.2.0 編譯與 source/dist 逐檔比對。

**Node / Dash 通過仍不等於 Minecraft 26.51 客戶端或 BDS 實機驗收。**
