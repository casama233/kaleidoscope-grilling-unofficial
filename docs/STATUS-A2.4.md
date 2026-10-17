# A2.4.0 — 手工穿串、秘制串與油壺 Java 語義修正

A2.4 建立在已驗證的 A2.3 上，優先修掉兩類目前 Bedrock 與 Java 1.1.1 真正不一致的行為：

- Cookery 油壺：普通 fat 容量 256；Grilling 三種 typed fluid oil 容量 64；每桶 8 點。A2.3 把 typed oil 也當成 256。
- Java HotFoodConfig 預設允許烤串滿飽食度進食；A2.3 food component 仍是 can_always_eat=false。

同時補回 Java 烤串最核心的生存製作鏈：副手木棍／未完成串 + 主手食材逐個穿串 → 固定配方或秘制串 → 可拆解 → 可上烤爐。

基準：

- Java Grilling 1.1.1：breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c
- Java 配方資料：common/src/main/resources/data/kaleidoscope_grilling/grilling/skewers.json
- Cookery 依賴：Bedrock 1.0.6
- Bedrock retail：26.51 / content 1.26.50
- Script API：穩定版 @minecraft/server 2.9.0
- 不要求實驗開關

> 注意：Kaleidoscope Tavern 與 Kaleidoscope Grilling 是兩個不同 Java 專案。本倉庫與 A2.x 狀態檔的對照基準一直是 Kaleidoscope Grilling 1.1.1；若之後要另外移植 Tavern，應另開專案／里程碑。

## 1. Java 20 條穿串配方

A2.4 將 Java skewers.json 的 20 條配方完整轉成資料驅動純邏輯表：

raw_beef_skewer、raw_pork_belly_skewer、raw_chicken_skin_skewer、raw_mid_wing_skewer、raw_squid_tentacle_skewer、raw_fish_skewer、raw_sweet_potato_sheet_skewer、raw_potato_slice_skewer、raw_caterpillar_skewer、raw_mushroom_skewer、raw_bun_slice_skewer、raw_ender_pearl_skewer、raw_meatball_skewer、raw_slime_skewer、raw_meat_and_bone_skewer、raw_fried_egg_skewer、raw_gluten_skewer、raw_lamb_skewer、raw_golden_skewer、ordinary_skewer。

支援 selector 替代項，例如 fish recipe 的 cod / salmon / tropical_fish / pufferfish，以及 mushroom recipe 的 brown / red mushroom。

## 2. 手工穿串

Java 行為：

- 副手是 stick / unfinished_skewer / 未烤 secret_skewer
- 主手是一個可穿串食材
- 每次右鍵加入一個食材，最多 3 個
- 命中完整固定配方時直接變成固定生串
- 3 個食材仍未命中固定配方時變成 Secret Skewer
- Secret Skewer 保存製作者
- 潛行右鍵可拆解未完成串、手工固定生串、未烤秘制串，返還食材與木棍

A2.4 已加入 unfinished_skewer、secret_skewer、a24_skewering_core.js、食材快照、固定配方解析、Secret creator metadata、潛行拆解、Secret raw 上烤爐，以及固定生串手工資料在烤熟後的保存。

### Bedrock stable 的輸入限制

WorldBeforeEvents.itemUse 只會在「物品成功被使用」時觸發；stable 2.9 沒有一個可攔截所有裝置之 generic Use/Interact 鍵的公開事件。

因此：

- food／本身可 use 的食材：可直接對空氣穿串
- 本身沒有任何 use 行為的食材：可在對方塊或實體按使用時由 playerInteractWithBlock / playerInteractWithEntity 捕捉
- 純空氣 + 無原生 use 行為物品仍不是 Java RightClickItem 的完全 1:1

## 3. Secret Skewer 營養

Java 公式：

- 只統計可食用 ingredient
- cooked nutrition = floor(sum(nutrition) × coefficient)，最少 1
- coefficient 正常 = 0.6
- 有重複「同物品 + 同資料」食材時再 ×0.8，即 0.48
- saturation modifier = 以 nutrition 加權平均
- raw Secret 再將 nutrition 與 saturation 各減半

A2.4 純邏輯測試覆蓋上述公式。Secret item 的 Bedrock native nutrition 設為 0，實際營養由腳本按保存的 ingredient 快照結算，避免固定 food component 與動態公式重複計算。

### 烤熟 ingredient

Java 會對 Secret 的每個 ingredient 查 smoking recipe，保存 CookedIngredientStacks，之後用烤熟 ingredient 計算營養。

Bedrock stable 2.9 沒有任意 recipe-manager 查詢 API，所以 A2.4：

- 實作 vanilla smoking 對應：beef / porkchop / chicken / mutton / rabbit / cod / salmon / potato / kelp
- 其他 ingredient 回退原 ingredient 營養

因此「任意模組食材的 smoking recipe 自動解析」仍是平台差異。

### finishUsingItem

Java Secret 食用後會逐個呼叫 ingredient 的 finishUsingItem。A2.4 可由 ItemFoodComponent.usingConvertsTo 還原常見容器 remainder，但無法泛化執行另一個物品類別的 Java callback。

## 4. Cookery 油壺 256 / 64 修正

Java OilPotCompat：

- FAT_CAPACITY = 256
- FLUID_CAPACITY = 64
- 三種 Grilling fluid oil 每桶增加 8 點
- canola heat = 1200 ticks
- secret_chili = 12000 ticks
- premium_chili = 24000 ticks

A2.4：

- 普通 Cookery fat：256
- typed Grilling oil：64
- 世界 source → Cookery pot 每次只代表一桶，加入 8/64
- 同油型可繼續加入
- 不允許不同 typed oil 混裝
- 不允許 fat 狀態直接混入 typed oil
- 烤爐刷油按實際串數消耗點數

## 5. 滿飽食度進食

Java HotFoodConfig.ALLOW_SKEWERS_AT_FULL_HUNGER 預設為 true。

A2.4 將所有正式 skewer food 的 minecraft:food.can_always_eat 改為 true；新增 Secret Skewer 同樣允許滿飽食度食用。

## 6. 64 疊加 + Dynamic Properties 真機風險修正

Script API 2.9 文件對 ItemStack.setDynamicProperty 明確指出：該方法只適用於已屬於 non-stackable/custom-data 狀態的 ItemStack。

A2.3 的 cooked stack 流程是先建立 max-stack-64 ItemStack，再先寫 HotUntil dynamic property，最後才寫 lore。真機中 dynamic-property 寫入存在 UnsupportedFunctionalityError 被 catch{} 吞掉的風險。

A2.4 改為：

1. 先寫 Hot lore／手工串 lore，使 stack 先帶 custom data
2. 再寫 dynamic property
3. 後續手動合併仍由 A2.3 mergeIntoContainer / refrigerator compaction 處理

這一項只有 Minecraft 26.51 / BDS 實機才能最終證明，CI mock / Node 測試不能宣稱引擎序列化已驗收。

## 7. A2.4 後仍未完成的 Java 核心內容

### 7.1 功能方塊

Java 共 14 個主要 block registrations；A2.4 仍缺：

- big_vat
- oil_press
- advanced_rack
- skewer_plate
- skewer_recipe
- canola_crop
- onion_crop
- sweet_potato_crop
- houttuynia_crop
- pepper_log
- pepper_leaves
- pepper_sapling

建議優先依賴順序：Skewer Plate → Recipe Book / Skewer Recipe → Oil Press + Big Vat → Advanced Rack → crops + pepper tree/worldgen。

### 7.2 正式 gameplay item

以 Java ModItems registry 與目前正式 gameplay BP 對照，A2.4 補入 unfinished_skewer / secret_skewer 後，仍有下列 Java item 尚未正式接入 gameplay core：

- 基礎食材／加工：beef_chunks、canola_powder、canola_seeds、carrot_dice、chicken_skin、chicken_wing、houttuynia、minced_houttuynia、oil_cake、oil_residue、onion、potato_slice、raw_mantou_slice、raw_sweet_potato_sheet、red_chili_powder、squid_tentacle、sweet_potato、sweet_potato_powder
- 單品／菜餚：cold_houttuynia、pepper_honey、roasted_chicken_wing、roasted_sweet_potato、sugared_tomato、wedding_candy、houttuynia_stir_fried_pork、green_pepper_squid_tentacles、braised_chicken_wings、potato_beef_stew、red_sweet_potato_porridge、sour_spicy_noodles
- 系統物品：skewer_plate、skewer_recipe_book

部分貼圖／模型可能已存在於 A1/static 資源，但「有資產」不等於已成為正式 gameplay item。

### 7.3 配方與加工鏈

Java pinned resources 含 61 個 recipe JSON。Bedrock gameplay BP 目前沒有完整對應的 recipes 集合；已有 grill / seasoning / oil 腳本只覆蓋其中一部分語義。

尚需完整核對並移植 crafting、chopping board、pot / stockpot / flex variants、milling / crushing / millstone、oil filling、chili oil mixing、roasting / smoking / campfire、oil cake / oil press，以及 guide / recipe book clear/reset recipes。

Create 專用配方若 Bedrock 沒有對應 Create 模組，只能標為 Java integration 或另做等價加工流程，不能假裝原模組相容。

### 7.4 Skewer Plate

Java語義：

- 容量 5
- 空手取出最後一串
- 持串放入
- sneak-use 可放置裝好內容的 plate
- 打破後 plate item 保存內容
- plate item 本身可食用，會挑內容中的高營養串
- 可在 Cookery table 上放 plate（預設 config true）

A2.4 尚未做。

### 7.5 Recipe Book / recipe display

Java 有 skewer_recipe_book、skewer_recipe block、recipe display/clear，以及 JEI threading / secret threading / grilling / oil pressing / seasoning categories。A2.4 尚未做正式等價 UI。應優先使用現有 Cookery guide 的 Grilling entry，而不是另造一套重複 guide。

### 7.6 Oil Press + Big Vat

Java：

- Oil Press 最多 4 個 oil cake
- 每個完成循環 progress 16
- anvil 一次 +4
- press stone 一次 +1
- 完成後輸出 4 oil residue
- Big Vat 容量 8 buckets
- 單一 typed fluid，不混油
- 可與 Oil Pot 以每 bucket = 8 points 交換

A2.4 尚未做。

### 7.7 Advanced Rack

Java block/item 的儲存／展示與互動仍未移植。

### 7.8 作物與世界生成

尚缺 Canola、Onion、Sweet potato、Houttuynia 四種 crop，以及 Pepper tree 的 log / leaves / sapling、configured_feature、placed_feature 與對應 block loot semantics。

### 7.9 Advancements

Java 有 21 個 Grilling advancements。Bedrock Add-On 沒有 Java advancement JSON 的原生等價；若要求玩法成就同等，需要用腳本事件 + 自訂提示／記錄層模擬，不能宣稱為 Minecraft 原生成就。

## 8. 仍屬平台差異的部分

即使後續把所有 gameplay content 補齊，下列項目也不應寫成「Java 1:1」：

- 真正 Forge FluidType / Liquid physics
- Numb per-player moving crosshair
- Mustard 原生 AvoidEntityGoal
- Sulfur 直接清 Phantom target
- Java top-face-sturdy 與 Bedrock isSolid 差異
- Dragon Blood HUD 額外 +2 HP 顯示
- OrderToCook 原模組 GUI / 128-stack 行為
- Java ItemStack NBT 任意完整序列化
- 任意 modded smoking recipe manager 查詢
- arbitrary ingredient finishUsingItem callback
- 純空氣、無原生 use 行為物品的 generic right-click 捕捉
- JEI / Jade / Create / KubeJS / Touhou Little Maid 等 Java-only mod integration 本身

這些可以做 Bedrock 語義模擬，但必須保留「近似／替代」標記。

## 9. 下一里程碑

為了最快把核心玩法補齊，按依賴關係拆：

- A2.5：Skewer Plate + Recipe Book / Skewer Recipe display
- A2.6：Oil Press + Big Vat + oil cake/residue
- A2.7：全部 Grilling 基礎食材、菜餚與 61 recipe processing chain
- A2.8：四種 crop + Pepper tree/worldgen + loot
- A2.9：Advanced Rack + guide polish + remaining effect/UI approximations
- A3.0：Minecraft 26.51 + BDS 實機 multiplayer 驗收、存檔遷移、性能與最終差異表

## 10. A2.4 驗證邊界

新增純邏輯測試覆蓋 20 條 recipe、selector、unfinished/secret fallback、三料上限、disassembly eligibility、Secret 0.6 / duplicate 0.8 / raw 0.5 公式，以及 fat 256 / typed oil 64 / bucket 8 / 不混油。

CI 會從 A2.0 → A2.1 → A2.2 → A2.3 → A2.4 全量重建，對 script 執行 node --check，執行 A2.4 verifier，使用 checksum-pinned bridge. Dash v1.2.0 編譯並逐檔比對，再產出 mcaddon 與 brproject。

在實際 Minecraft / BDS 驗證完成前，以下仍標為未驗收：

- max-64 + custom lore + dynamic property 的真機保存／拆分／合併
- offhand threading 在鍵鼠／手把／觸控的輸入覆蓋
- Secret dynamic nutrition / remainder
- Grill 保存 Secret metadata
- typed oil 8/64 world source transaction
- multiplayer concurrent interaction
