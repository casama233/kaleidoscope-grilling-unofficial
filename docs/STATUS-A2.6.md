# A2.6 — Oil Press + Big Vat / 榨油器與大缸

> Java 基線：Kaleidoscope Grilling 1.1.1，`breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c`。  
> Bedrock：26.51 / content 1.26.50 / `@minecraft/server 2.9.0`。  
> A2.5 Skewer Plate + 串譜已於 PR #3 全 CI 綠燈後合併至 `main`。

## 1. 本輪 Java 對照

逐項核對：

- `OilPressBlock`
- `OilPressBlockEntity`
- `OilPressTools`
- `OilPressApi`
- `OilPressContainerApi`
- `AnvilPressAnimation`
- `BigVatBlock`
- `BigVatBlockEntity`
- `BigVatRenderer`
- `OilFillingHandler`
- `OilResidueItem`
- `press_stones` item tag
- `oil_press.json` / `big_vat.json` / `oil_cake.json`

## 2. 榨油器：已移植語義

- 最大 **4 油餅**。
- 未滿 4 個時，鐵砧／壓榨石不增加進度。
- Java `press_stones` 原樣鎖定：
  - stone
  - cobblestone
  - deepslate
  - cobbled_deepslate
  - blackstone
- 鐵砧、裂紋鐵砧、損壞鐵砧：每次 **+4**。
- press stone：每次 **+1**。
- 總進度 **16**。
- 每名玩家／每台榨油器 **10 tick** 冷卻。
- 敲擊動畫共 9 tick，真正加進度在 Java 的 **impact tick 6**；Bedrock 用 `playAnimation` + 延遲 impact 重建。
- 進度到 16 後還有 **10 tick completion delay**。
- 完成時掃描與 Java 同一立方範圍：X/Z ±4、Y ±2。
- 大缸優先且本輪只宣稱 Big Vat handler；成功時一次轉入 **4 桶 canola**。
- 完成同時產生 **4 個 oil_residue**；Java 無 Create 時會向榨油器朝向前方 eject，本輪同樣直接彈出。
- 如果沒有大缸、容量不足或大缸已有不同流體：
  - 進度回到 **15/16**；
  - 進入 `waitingForContainer`；
  - 之後任意右鍵榨油器會優先重查容器，不先處理手中物品。
- 破壞榨油器：
  - 返回榨油器；
  - 返回尚未壓掉的油餅；
  - 不保存 press progress，對齊 Java drops。
- `completionDelay` 用 world dynamic property + press registry 每 tick 推進，因此不像單純 `runTimeout` 那樣在世界重載後必然丟失。

## 3. 大缸：已移植語義

- 容量 **8 桶**。
- 同一時間只能一種流體。
- Stable Bedrock 可可靠支持：
  - water
  - lava
  - canola
  - secret_chili
  - premium_chili
- 支援三種 Grilling 油桶與水／熔岩桶灌入。
- 空桶可整桶取出。
- 三種油可直接灌入 Cookery 油壺：
  - 每桶 **8 oil points**；
  - 油壺容量 **64**；
  - 一次盡量抽取「大缸現有桶數」與「油壺剩餘整桶容量」兩者較小值；
  - 不允許混油。
- 破壞大缸時，把流體種類與桶數打包回 `kaleidoscope_grilling:big_vat` item；重新放置後恢復。
- 世界狀態以動態屬性保存，不靠 block state 當資料庫；block state 只負責可視化。
- Java Renderer 的液面高度不是 8 檔而是 **4 檔**：
  - 1–2 桶 → level 1
  - 3–4 桶 → level 2
  - 5–6 桶 → level 3
  - 7–8 桶 → level 4
- A2.6 按同一公式產生四級液面 geometry。

## 4. 模型／資產

不是重畫低精度替代品：

- 直接復用本倉庫 A1 已由 Java 原模型轉換出的：
  - `oil_press_frame`
  - `oil_press_hit_0..4`
  - `oil_press_oil1_1..4`
  - `oil_press_oil2..5`
  - `big_vat`
- A2.6 generator 把 Java multipart 榨油器模型合成 Bedrock block geometry：
  - cake_count 0–4
  - press_stage 0–4
  - cardinal facing
- `canola_powder`、`oil_cake`、`oil_residue` 物品圖直接取鎖定 Java commit，使用 git blob SHA-1 驗證。
- Big Vat 液面使用 geometry named material instance，三種油沿用 A2.3 world-oil 貼圖。

## 5. 新增基礎內容與配方

A2.6 同時補入：

- `canola_powder`
- `oil_cake`
- `oil_residue`
- `oil_press`
- `big_vat`

以及三份機器鏈 crafting recipe：

- oil cake
- oil press
- big vat

其中 Java 的 `minecraft:logs` 已保留為 Bedrock recipe tag。Java `c:fences` 跨模組 tag 在 A2.6 暫用 vanilla oak fence；等 A2.7 全 recipe pass 建立統一 tag compatibility 時再收斂。

## 6. Oil Residue

Java `OilResidueItem` 對同一目標連續呼叫兩次 `BoneMealItem.useOn`，但 stable Bedrock Script API 沒有「呼叫原版骨粉 useOn」的通用 API。

A2.6 對具有 numeric `growth/age` state 的作物做兩輪成長推進，並只消耗 1 個油渣。這涵蓋最重要的作物用途，但下列原版骨粉特殊目標仍不是 1:1：

- 樹苗長樹
- 草地散佈植物
- 花、蘑菇與其他自訂 bonemeal handler

因此這一項明確標成平台替代，不計作完全 1:1。

## 7. Forge / Create 平台差異

Java Big Vat 本體是 8000 mB `FluidTank`，因此 Forge 可接受任意第三方 Fluid；Bedrock stable 沒有等價的跨 addon `IFluidHandler` registry。

A2.6 不偽裝這部分已移植：

- 第三方任意流體：未支持。
- 非整桶 mB 精度：未支持；本模組可觀察的桶／油壺流程保持等價。
- Create funnel 自動插入 oil cake：沒有 Bedrock Create compatibility API，未支持。
- Create fluid tank 作為 press 輸出容器：未支持。
- Create item handler 自動接收 oil residue：未支持。

如果未來安裝目標 Bedrock Create addon 並公開穩定 API，可在獨立 compat layer 接入，不污染核心機器語義。

## 8. A2.6 後剩餘 Java 差異

### 核心方塊／世界

尚未 gameplay 化：

- `advanced_rack`
- `canola_crop`
- `onion_crop`
- `sweet_potato_crop`
- `houttuynia_crop`
- `pepper_log`
- `pepper_leaves`
- `pepper_sapling`
- 花椒樹 worldgen

`oil_press`、`big_vat` 已從缺口移除。

### 基礎／加工物品

仍包括：

`beef_chunks`, `canola_seeds`, `carrot_dice`, `chicken_skin`, `chicken_wing`, `houttuynia`, `minced_houttuynia`, `onion`, `potato_slice`, `raw_mantou_slice`, `raw_sweet_potato_sheet`, `red_chili_powder`, `squid_tentacle`, `sweet_potato`, `sweet_potato_powder`。

`canola_powder`、`oil_cake`、`oil_residue` 已移除。

### 菜品

仍包括：

`cold_houttuynia`, `pepper_honey`, `roasted_chicken_wing`, `roasted_sweet_potato`, `sugared_tomato`, `wedding_candy`, `houttuynia_stir_fried_pork`, `green_pepper_squid_tentacles`, `braised_chicken_wings`, `potato_beef_stew`, `red_sweet_potato_porridge`, `sour_spicy_noodles`。

### 資料／系統

仍要完成：

- 其餘 crafting / chopping / pot / stockpot / flexible cooking / milling / crushing / roasting / smoking / campfire / chili-oil mixing 等 recipe。
- `AdvancedRackBlock/Entity`。
- 四種 Grilling 作物及種子／採收。
- 花椒樹、樹苗、葉子、掉落與 worldgen。
- Java 21 advancements 的 Bedrock 等價進度。
- Guide 單一入口的完整動態內容與實機核驗。
- Plate BE 每根串的動態 3D renderer。
- Oil Residue 非 age-state bonemeal targets。
- 客戶端／BDS 實機與多人持久化驗收。

## 9. 下一批

- **A2.7**：基礎／加工物品 + 菜品 + 全 recipe reconciliation。
- **A2.8**：四種作物 + 花椒樹 + worldgen。
- **A2.9**：Advanced Rack + advancement + Guide/UI/剩餘 renderer。
- **A3.0**：Minecraft 26.51 客戶端 + BDS 多人、重載持久化、效能、舊世界遷移，最後重跑完整 Java 差異表。
