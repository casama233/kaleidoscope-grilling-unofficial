# A2.5 — Skewer Plate + 串譜 / Recipe Book

> 基線：Kaleidoscope Grilling **1.1.1**，鎖定 `breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c`。  
> Bedrock：26.51 / content 1.26.50，`@minecraft/server 2.9.0`，Cookery Bedrock 1.0.6 依賴維持不變。

A2.5 以 A2.4 為實際基線。A2.3 已不是 `main` 最新狀態；A2.4 已先完成 20 組 Java 穿串配方、自由秘制串、生串拆解、64/256 油壺容量語義與堆疊資料修正。

## 0. 專案範圍核對

使用者附的 CurseForge **Kaleidoscope Tavern** 與本倉庫目標 **Kaleidoscope Grilling** 是兩個獨立 Java 模組。本倉庫仍只移植 Grilling；Tavern 不混入 Grilling namespace、進度百分比或成品包。若之後移植 Tavern，應另建里程碑／專案。

## 1. 本輪對照的 Java 類

本輪逐項核對：

- `SkewerPlateBlock`
- `SkewerPlateBlockEntity`
- `SkewerPlateItem`
- `SkewerPlatePlacement`
- `SkewerRecipeBookItem`
- `SkewerRecipeBookHandler`
- `SkewerRecipeCraftingRecipe`
- `SkewerRecipeBlock`
- `SkewerRecipeBlockEntity`

並沿用 A2.4 已鎖定的 `SkewerRecipes` 20 組配方資料。

## 2. Skewer Plate 已移植語義

已實作：

- 容量固定 **5**。
- 手持可接受烤串右鍵放入。
- 空手右鍵以 **LIFO** 取回最後放入的一串。
- 放入／取出保留整個 ItemStack 的名稱、lore、primitive dynamic properties；因此 HotUntil、調料、秘制串原料／熟化旗標／製作者資料可以跟著盤子移動。
- 蹲下對方塊頂面使用已裝串盤子可放置。
- 與 Java `SkewerPlatePlacement` 一致，也支援 **蹲下直接拿一根串放成一盤一串的世界方塊**。
- 普通實心頂面與 `kaleidoscope_cookery:table` 可作支撐。
- 破壞有內容的盤子時，世界狀態重新封裝回 `kaleidoscope_grilling:skewer_plate`；空盤不掉盤子，對齊 Java `getDrops`。
- 盤子物品可吃；選擇規則是 **nutrition 最大者，平手取最先放入者**，對齊 Java strict `>` 選擇。
- 吃完只移除被選中的一串；仍有內容就留下重新封裝的盤子，最後一串吃完盤子消失。
- 被吃的巢狀串重新走既有 A2.4 營養、Hot Food、調料、固定效果、Secret Skewer 剩餘物與負面效果處理。

Bedrock 內部世界方塊使用 `kaleidoscope_grilling:skewer_plate_block`，物品仍維持 Java 對外 ID `kaleidoscope_grilling:skewer_plate`。原因是 Bedrock stable 無法同時把同一 identifier 當成「帶 food / dynamic item data 的自訂物品」與可腳本保存內容的 custom block item；這是內部實作差異，不改玩家取得的盤子物品 ID。

## 3. 串譜 / Recipe Book 已移植語義

已實作：

- 新增 `kaleidoscope_grilling:skewer_recipe_book`。
- 可記錄 A2.4 20 組固定生串／普通串。
- 秘制串只有完整 **3 原料**時可記錄，並保存原串完整 metadata。
- 記錄後以副手木棍使用串譜：
  - 依 Java 配方 selector 順序掃描玩家背包；
  - 跳過當前手持串譜槽；
  - 重複原料會正確預留數量；
  - 任一材料缺失時整次操作不扣任何物品；
  - 成功才一次性扣材料與 1 根木棍；
  - 固定串產生對應 raw skewer；
  - 秘制串重建記錄原料，並把 creator 更新為目前玩家。
- 記錄完成的串譜可貼在方塊水平側面，建立 `kaleidoscope_grilling:skewer_recipe`。
- 掛牆串譜手持木棍右鍵可直接製作。
- 空手右鍵掛牆串譜可拆下並取回原書。
- 直接破壞亦返還保存完整資料的串譜。
- 支撐方塊被玩家破壞後會檢查四周掛牆串譜並掉落，近似 Java `canSurvive/updateShape`。

### Java shapeless NBT recipe 的 Bedrock 替代

Java `SkewerRecipeCraftingRecipe` 可以在 crafting result 中直接寫 NBT 並把原串當 remainder。Bedrock 26.51 stable recipe JSON 不能可靠產生依輸入變化的 dynamic-property output。

因此 A2.5 用穩定等價流程：

- 空串譜 + 副手完整生串 → 使用鍵記錄，原串不消耗；
- 若 Cookery 1.0.6 暴露 `recipe_block / recipe / recipe_item`，蹲下持該空白食譜並把生串放副手，也可直接轉成已記錄串譜。

核心結果與 Java 相同：**消耗一份空白食譜媒介、保留被記錄的生串、得到帶配方資料的串譜**。實機需再確認 Cookery 1.0.6 實際空白食譜 identifier。

## 4. 資產

- 串譜物品圖：Grilling 鎖定提交原資產。
- 盤子底圖：Cookery 上游 plate 原資產，SHA-1 鎖定。
- 掛牆食譜紙：Cookery 上游 recipe_block 原資產，SHA-1 鎖定。
- 盤子與食譜紙都建立 Bedrock geometry，而不是使用未授權／未追蹤的本機資產。

目前盤子世界模型只精確表現盤體與 `plate_count` 狀態；Java BlockEntityRenderer 會把每根實際串以各自模型插在盤上，Bedrock stable 本輪仍沒有逐根動態材質／模型 renderer，所以**世界中每根串的個別外觀尚未宣稱 1:1**。資料與互動已保存。

## 5. 驗證

A2.5 新增：

- `development/gameplay_core/a25_plate_recipe_core.js`
- `development/gameplay_core/a25_plate_recipe_runtime.js`
- `development/gameplay_core/test_a25_core.mjs`
- `development/gameplay_core/augment_a25.py`
- `development/gameplay_core/verify_a25.py`
- `.github/workflows/gameplay-core-a25.yml`

純邏輯測試覆蓋容量、第五／第六根邊界、LIFO、nutrition 平手規則、固定／秘制串譜、重複材料預留、槽排除與缺料原子失敗。CI 仍會從 A2.0 → A2.5 全鏈重建，再用官方 Dash v1.2.0 編譯並逐檔比較 source/dist。

**Notebook / Node / Dash 通過仍不等於 Minecraft 客戶端或 BDS 實機通過。** A2.5 目前仍標記 `minecraft_tested=false`、`bds_tested=false`。

## 6. A2.5 後仍與 Java 1.1.1 有差異

### 6.1 尚未建立的核心方塊

- `big_vat`
- `oil_press`
- `advanced_rack`
- `canola_crop`
- `onion_crop`
- `sweet_potato_crop`
- `houttuynia_crop`
- `pepper_log`
- `pepper_leaves`
- `pepper_sapling`

`skewer_plate` 與 `skewer_recipe` 從這份清單移除。

### 6.2 尚未完整 gameplay 化的基礎／加工物品

仍包括：

`beef_chunks`, `canola_powder`, `canola_seeds`, `carrot_dice`, `chicken_skin`, `chicken_wing`, `houttuynia`, `minced_houttuynia`, `oil_cake`, `oil_residue`, `onion`, `potato_slice`, `raw_mantou_slice`, `raw_sweet_potato_sheet`, `red_chili_powder`, `squid_tentacle`, `sweet_potato`, `sweet_potato_powder`。

### 6.3 尚未完整 gameplay 化的菜品

`cold_houttuynia`, `pepper_honey`, `roasted_chicken_wing`, `roasted_sweet_potato`, `sugared_tomato`, `wedding_candy`, `houttuynia_stir_fried_pork`, `green_pepper_squid_tentacles`, `braised_chicken_wings`, `potato_beef_stew`, `red_sweet_potato_porridge`, `sour_spicy_noodles`。

### 6.4 配方／加工鏈

Java data 仍有約 **61 份 recipe JSON** 需要逐份收斂到 Bedrock：

- vanilla crafting
- chopping board
- pot / stockpot / flexible cooking
- milling / crushing / millstone
- oil filling / chili-oil mixing
- roasting / smoking / campfire
- oil cake / oil press
- guide / recipe reset 等資料行為

A2.4 的 20 組穿串 selector 已成 gameplay；A2.5 串譜會直接使用同一張表，不重複維護第二套配方。

### 6.5 機器／世界

- Oil Press + Big Vat：尚未移植。
- Advanced Rack：尚未移植。
- 四種 Grilling 作物與花椒樹生長／掉落／worldgen：尚未移植。
- Java 21 個 advancements：尚未做 Bedrock 腳本等價。
- Guide：必須繼續維持 Cookery 既有指南中的單一 Grilling entry，不新增第二本實體指南；目前動態整合仍需實機確認。
- Java Plate BE 的逐根串 3D renderer：尚有視覺差異。

### 6.6 固有平台差異

- Forge/Fabric 自訂 FluidType ↔ Bedrock scripted fluid simulation。
- Java GUI Mixin 的 Numb 準星偏移 ↔ stable Bedrock 無安全 per-player crosshair offset。
- Java advancement / recipe serializer / block entity renderer 無 1:1 Bedrock API；只能做語義替代。

## 7. 下一批

建議維持既定順序：

- **A2.6**：Oil Press + Big Vat。
- **A2.7**：缺失基礎物品／菜品 + 全 61 processing recipes。
- **A2.8**：四種作物 + 花椒樹 + worldgen。
- **A2.9**：Advanced Rack + Guide / advancement / 剩餘 UI 與效果差異。
- **A3.0**：Minecraft 客戶端 + BDS 多人、持久化、效能、舊世界遷移，最後重新跑完整 Java 差異表。

