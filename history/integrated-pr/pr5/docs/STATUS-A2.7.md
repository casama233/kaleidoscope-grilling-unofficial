# A2.7 — 全 Java Item Registry + 61 Recipe Reconciliation

> Java 基線：Kaleidoscope Grilling 1.1.1，`breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c`。  
> Bedrock：26.51 / content 1.26.50 / `@minecraft/server 2.9.0`。  
> A2.6 Oil Press + Big Vat 已通過全鏈 CI、官方 Dash 編譯與 source/dist 比對並發布至 `main`。

A2.7 的目標不是只「多放幾個物品」，而是把 Java `ModItems` 與 `common/.../recipes/` 做一次完整 registry / recipe reconciliation，讓之後 A2.8/A2.9 不再靠印象補內容。

## 1. Java Item Registry 差異：27 → 0

A2.6 後，以 Java `ModItems` 與正式 gameplay BP 比對，仍缺 27 個正式 item。A2.7 全部接入：

- 基礎／加工：
  - beef_chunks
  - canola_seeds
  - carrot_dice
  - chicken_skin
  - chicken_wing
  - houttuynia
  - minced_houttuynia
  - onion
  - potato_slice
  - raw_mantou_slice
  - raw_sweet_potato_sheet
  - red_chili_powder
  - squid_tentacle
  - sweet_potato
  - sweet_potato_powder
- 菜品：
  - braised_chicken_wings
  - cold_houttuynia
  - green_pepper_squid_tentacles
  - houttuynia_stir_fried_pork
  - pepper_honey
  - potato_beef_stew
  - red_sweet_potato_porridge
  - roasted_chicken_wing
  - roasted_sweet_potato
  - sour_spicy_noodles
  - sugared_tomato
  - wedding_candy

27/27 都直接使用鎖定 Java commit 的原版 item texture，並由 git blob SHA-1 驗證；不畫替代貼圖。

A2.7 後，**Java ModItems registry 的正式 item identifier 差異為 0**。作物對應 item（canola_seeds / onion / houttuynia / sweet_potato）雖已存在，但種植方塊仍按既定計畫留給 A2.8。

## 2. 食物數值與特殊行為

Java 數值已逐項鎖定：

- chicken_wing：2 / 0.06
- houttuynia：2 / 0.2
- sweet_potato：3 / 0.1
- roasted_sweet_potato：6 / 0.2，Warmth 600 ticks
- roasted_chicken_wing：5 / 0.12
- cold_houttuynia：6 / 1.0，Fire Resistance 1200 ticks
- sugared_tomato：6 / 0.65
- pepper_honey：4 / 0.25，Numb 1200 ticks
- wedding_candy：20 / 0.5，always-eat，Invincible 300 ticks
- houttuynia_stir_fried_pork：9 / 0.7
- green_pepper_squid_tentacles：8 / 0.6
- braised_chicken_wings：10 / 0.8
- potato_beef_stew：12 / 0.9
- red_sweet_potato_porridge：14 / 0.071429，Flatulence 900 + Warmth 900
- sour_spicy_noodles：10 / 0.6，Warmth 900

所有新增可食物都有 stable Bedrock 所需的 `minecraft:food + minecraft:use_modifiers + minecraft:use_animation`，不是只有 JSON 中存在 nutrition。

### Sweet Potato Powder

Java `SweetPotatoPowderItem`：

- use duration 30 ticks
- bow animation
- 完成後整疊變成同數量 raw_sweet_potato_sheet
- 播放 leather equip sound

A2.7 按同一語義腳本化。

## 3. Cookery Cuisine Quality：新發現的 Java 差異

此前 A2.x 狀態表沒有把 Grilling 菜餚對 Cookery `QualityUtils` 的依賴完整列出。

Java `QualityUtils`：

- quality NBT key：`kaleidoscope_cookery:quality`
- Quality ratios：
  - SUPERB id 0 → 1.2
  - EXCELLENT id 1 → 0.9
  - STANDARD id 2 → 0.6
  - POOR id 3 → 0.3
- 帶品質食物：
  - nutrition = round(raw nutrition × ratio)
  - saturation modifier = raw saturation modifier × ratio
  - effect duration = round(raw duration × ratio)

A2.7 的 11 個品質感知 Grilling 食物已寫入相同公式，runtime 可在取得品質 ID/ratio 時調整 hunger、saturation 與 effect duration。

但 **Cookery Bedrock 1.0.6 的品質實際 storage contract 尚未從公開 API 文件精確綁定**。A2.7 只探測同名 dynamic property 與 Grilling 顯式 compatibility ratio，不宣稱 Cookery 1.0.6 品質已實機互通。這仍需真包 API schema / Minecraft 實機確認。

## 4. Java 61 份 recipe：完整來源鎖定

A2.7 新增 `a27_recipe_sources.json`，對 61/61 份 Java 1.1.1 recipe JSON 保存：

- path
- git blob SHA-1
- byte size

重建時逐份從鎖定 commit 讀取並驗證 blob SHA；上游內容若漂移會直接失敗。

完整分類：

- **18** vanilla-direct 類
- **24** Cookery machine 類
  - 其中 **22** 是 Grilling 核心
  - **2** 是 Tavern 條件配方
- **16** Create-only optional integration
- **3** Grilling custom serializers

總計：18 + 22 + 2 + 16 + 3 = **61**。

## 5. Vanilla-direct 配方

A2.7 已生成／校正 stable Bedrock 能直接表示的核心配方。

### 已接入

- big_vat
- oil_cake
- oil_press
- grill
- empty_seasoning_bottle
- pepper_honey
- sugared_tomato
- secret_chili_oil
- premium_chili_oil
- clear_skewer_recipe_book（Bedrock substitution）
- clear seasoning 三種輸入
- roasted_chicken_wing
- roasted_sweet_potato

### A2.6 配方修正

A2.6 的 Big Vat 暫時把 Java `forge:ingots/brick` 映成 brick block；A2.7 修正為真正的 `minecraft:brick` item。

Oil Press：

- logs → Bedrock 官方 `minecraft:logs` recipe tag
- iron ingot → exact item
- hopper → exact item
- Java `minecraft:fences` 群組在 stable Bedrock recipe tag 清單無同等標籤，所以目前使用 oak_fence 代表；列為 recipe-selector 差異。

Empty Seasoning Bottle：

- Java 接受所有 wooden buttons + colorless glass
- Bedrock stable 無對等官方 recipe input group
- A2.7 以 oak_button + glass 代表；列為 selector 差異。

### 容器返還

Java crafting remainder 不會被忽略：

- pepper_honey：返還 glass bottle
- secret_chili_oil：返還 1 empty bucket
- premium_chili_oil：返還 2 empty buckets

利用 Bedrock shapeless recipe 的多結果輸出實現。

### Furnace / smoker / campfire

Java 分別有 smelting / smoking / campfire JSON，且帶不同 cookingtime / experience。

Bedrock `minecraft:recipe_furnace` 只有 station tags，沒有同等 per-recipe cookingtime / experience 欄位。A2.7 將每種食物合併為一份：

- furnace
- smoker
- campfire
- soul_campfire

輸入／輸出一致，但 Java 的 200/100/600 tick 與 0.35 XP 不能 1:1 寫進 Bedrock recipe JSON，保留平台差異標記。

## 6. 三個 Grilling custom recipe serializers

### Skewer Recipe Book

A2.5 已完成真正核心語義：

- 固定生串／秘制串記錄
- 保存 metadata
- 木棍＋背包自動取料
- 掛牆 recipe block

因此 A2.7 不重造第二套。

Java `clear_skewer_recipe_book` 會回到 Cookery `recipe_item`；實際 Bedrock Cookery 1.0.6 已觀察 registry 沒有該 item ID，所以 A2.7 的等價結果是**新的空白 Grilling skewer_recipe_book**，即清除動態記錄而保持可再次記錄。

### Clear Seasoning

Java custom serializer 接受：

- pending_seasoning
- special_seasoning
- 帶 SeasoningData 的 empty_seasoning_bottle

結果都是乾淨 empty_seasoning_bottle。

A2.7 建立三個單物品清理 recipe；乾淨 empty bottle 也能做一次 no-op 清理，這是 Bedrock recipe JSON 無法判斷 dynamic-data existence 造成的無害擴展。

### Cold Houttuynia

Java 精確條件：

- 3 份 Houttuynia
- 1 個 premium_chili Oil Pot
- oil count ≥ 2
- 合成後 oil pot 保留並扣 2 points

Bedrock recipe JSON 無法在 remainder 上修改 dynamic property，所以 A2.7 使用 stable Script API 等價交易：

- 主手 Houttuynia
- 副手 premium_chili Cookery Oil Pot
- 潛行使用
- 背包至少 3 份 Houttuynia
- 精確消耗 3 份 + 2 oil points
- 產出 cold_houttuynia
- 油量歸零時回到 Cookery empty oil pot

材料／狀態交易等價，但輸入介面不是 Java crafting grid，明確標記為 UI/platform substitution。

## 7. Cookery 機器配方：22 核心 + 2 Tavern conditional

Java 24 份 Cookery recipe：

- Chopping Board：5
- Millstone：7
- Pot：3
- Flex Pot：3
- Stockpot：3
- Flex Stockpot：3

其中：

- `stockpot/sour_spicy_noodles`
- `flex_stockpot/sour_spicy_noodles`

都明確帶 `forge:mod_loaded(kaleidoscope_tavern)` 並依賴 `kaleidoscope_tavern:vinegar`。

因此它們屬於 **Tavern integration**，不是 Grilling 單獨安裝時的核心缺失。Tavern 是另一個獨立移植專案，不把 vinegar 或 Tavern namespace 假造進本倉庫。

其餘 22 份 A2.7 已：

- 逐份 SHA-pinned
- 逐份解析
- 原樣保存 Java machine recipe contract
- 生成 `a27_cookery_recipes.js` runtime catalog

### 還沒冒充完成的最後一步

Cookery Bedrock v1.0.6 的真包審計已確認存在公開 extension recipe API 與 `KC_EXTENSION_API.md`，但目前倉庫可恢復的審計產物只保存了 API 存在性與檔案 SHA，**沒有保存 `register_recipe` payload 的完整欄位 schema**。

因此 A2.7 **沒有猜一個 JSON 格式去發 Script Event**。目前狀態是：

- 22 份核心 Cookery recipe：來源與 catalog 完成
- Cookery API publisher：**未綁定**
- 對外完成宣稱：**不算已在 Cookery 機器中可製作**

這是 A2.7 後最大的 gameplay recipe 差異。拿到／重新檢視 1.0.6 `KC_EXTENSION_API.md` 或 `extensionRegistry.js` 後，只需新增 publisher，無需重新整理 22 份 recipe。

## 8. Create-only 16 份

Java 16 份配方只在 Create 安裝時存在：

- crushing 1
- milling 7
- filling 6
- mixing 2

Bedrock 核心沒有對等 Create API，因此不把它們計入 Grilling 核心缺失。來源仍 16/16 鎖定在 recipe report，未來若選定 Bedrock Create addon，可另開 compat publisher。

## 9. 延後 2 份 direct recipe

- `advanced_rack.json`：A2.9 Advanced Rack 本體尚未建立
- `oak_planks_from_pepper_log.json`：A2.8 Pepper Log 尚未建立

不是漏核對；來源已在 61 清單中，會在輸出 item/block 存在的里程碑啟用。

## 10. A2.7 後剩餘 Java 差異

### 真正未完成的 Grilling 核心內容

- 22 份 Cookery machine recipe 的 **正式 1.0.6 API publisher**
- Cookery Bedrock 品質 storage contract 綁定
- 四種 crop：canola / onion / sweet potato / houttuynia
- pepper log / leaves / sapling / worldgen
- Advanced Rack
- 21 Java advancements 的 Bedrock 等價進度
- Cookery guide 單一 Grilling entry 的最終動態整合與實機確認
- Skewer Plate world renderer 的逐根串 3D 視覺
- Oil Residue 對 sapling / grass / special bonemeal target 的完整等價
- Minecraft 26.51 客戶端 + BDS 多人／重載持久化驗收

### 固有平台／可選整合差異

- 16 Create recipes：optional integration
- 2 Tavern vinegar recipes：Tavern integration
- 任意 Forge FluidType
- Numb per-player crosshair
- Mustard 原生 AI goal / Sulfur target clear
- JEI/Jade/KubeJS/Touhou Little Maid/OrderToCook 原模組 UI/automation 本身

## 11. 下一步

A2.8 仍按既定順序：

- canola/onion/sweet potato/houttuynia crops
- pepper log/leaves/sapling
- pepper tree worldgen + loot
- 啟用 oak_planks_from_pepper_log

A2.9：

- Advanced Rack
- 啟用 advanced_rack recipe
- advancements
- guide/UI/render remaining parity
- 若 Cookery 1.0.6 API schema 已取得，同時把 22 machine recipe publisher 合入；若更早取得，可在 A2.7.x 直接補，不必等 A2.9。

A3.0：

- Minecraft 26.51 client
- BDS multiplayer
- save/reload
- performance
- migration
- 最終 Java 1.1.1 差異表
