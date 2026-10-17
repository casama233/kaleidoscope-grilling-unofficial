# A2.7.1 — 紅薯粉持續揉捏 → 生苕皮

> Java 基線：Kaleidoscope Grilling **1.1.1**，鎖定 `breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c`。  
> Bedrock：26.51 / content 1.26.50 / `@minecraft/server 2.9.0`。  
> 這是 A2.7 的**第一個小切片**，不是「A2.7 全配方已完成」。

## 1. 為什麼先切這一條

A2.6 後最大的工作包是「缺失基礎／加工物品 + 菜品 + 全 recipe reconciliation」。一次做完會把物品註冊、Cookery 加工機、Create-only 配方和菜品效果混成一個很難驗證的大提交。

A2.7.1 只收斂 Java 裡有獨立 Item 行為、可單獨驗證的：

`SweetPotatoPowderItem` → `RawSweetPotatoSheetItem`

## 2. Java 1.1.1 原始語義

`SweetPotatoPowderItem`：

- 使用時開始持續動作。
- `getUseDuration = 30 ticks`，即 **1.5 秒**。
- 使用動畫為 `BOW`。
- 完成後播放 `ARMOR_EQUIP_LEATHER`，音量 **0.8**、音高 **1.1**。
- 不是只轉換 1 個：Java 直接回傳 `new ItemStack(RAW_SWEET_POTATO_SHEET, s.getCount())`，因此**整個起始堆疊等量轉成生苕皮**。

`RawSweetPotatoSheetItem` 本身沒有額外 gameplay callback，只提供取得方式提示。

## 3. A2.7.1 已完成

正式 Gameplay Core 新增：

- `kaleidoscope_grilling:sweet_potato_powder`
- `kaleidoscope_grilling:raw_sweet_potato_sheet`

兩張物品貼圖直接取鎖定 Java commit，使用 Git blob SHA-1 驗證，不使用重畫替代素材。

紅薯粉：

- 最大堆疊 64。
- 主手／副手均可使用。
- 使用時間 1.5 秒。
- bow use animation。
- 開始使用時記錄**手別、槽位與起始數量**。
- 提前放開只清除狀態，不轉換。
- `itemCompleteUse` 後把起始整疊等量換成生苕皮。
- 完成後播放 leather-equip 音效。
- 若完成事件到下一 tick 間原槽被其他內容佔用，不覆寫玩家新物品，而是把結果安全放回背包／掉落。

### Bedrock stable 的輸入替代

Bedrock retail 要讓普通自訂物品穩定產生 start/stop/complete-use 事件，需要一個原生「可使用」component。A2.7.1 使用：

- `minecraft:food`，nutrition = 0、saturation = 0、can_always_eat = true；
- `minecraft:use_modifiers`，1.5 秒；
- `minecraft:use_animation = bow`。

`minecraft:food` 在這裡**只作輸入事件 shim**，實際結果由腳本按 Java 規則替換整疊，不增加飢餓／飽和。為避免這個 shim 讓紅薯粉被 A2.4 誤判成「可自由穿入秘制串的食物」，A2.7.1 在穿串 edible 判定中明確排除 `sweet_potato_powder`。

Minecraft 實機仍需確認是否會短暫產生 Bedrock 原生 food 聲音／粒子；腳本在完成時嘗試停止 `random.eat` 並播放 Java 對應 leather-equip 聲音。未做實機前不把這項視聽細節標成 1:1。

## 4. 這一小批刻意沒有做的相鄰內容

Java 同一條材料鏈還有：

1. **Cookery Chopping Board**：紅薯粉切 **4 刀** → 生苕皮；Java 在第 2 刀還把聲音替換成倒水聲。
2. **Cookery Millstone**：sweet-potatoes tag → 紅薯粉。
3. **Create Milling**：安裝 Create 時，100 processing time 的 sweet-potatoes → 紅薯粉。

以上沒有在 A2.7.1 冒充完成。原因是它們屬於「加工機／配方 adapter」而不是這次的獨立 Item 行為，而且 `sweet_potato` 正式作物仍排在 A2.8。

下一個小切片應優先做 **A2.7.2 Cookery 加工 adapter：Millstone + Chopping Board**，再逐批吃掉其餘 chopping / pot / stockpot / flex recipes。

## 5. A2.7.1 後的 Java 差異

### 已從「物品尚未 gameplay 化」移除

- `sweet_potato_powder`
- `raw_sweet_potato_sheet`

但紅薯粉的**正常生存取得**仍未完整，因 Millstone / Create Milling 尚未接線。

### 仍缺基礎／加工物品

`beef_chunks`, `canola_seeds`, `carrot_dice`, `chicken_skin`, `chicken_wing`, `houttuynia`, `minced_houttuynia`, `onion`, `potato_slice`, `raw_mantou_slice`, `red_chili_powder`, `squid_tentacle`, `sweet_potato`。

### 仍缺菜品

`cold_houttuynia`, `pepper_honey`, `roasted_chicken_wing`, `roasted_sweet_potato`, `sugared_tomato`, `wedding_candy`, `houttuynia_stir_fried_pork`, `green_pepper_squid_tentacles`, `braised_chicken_wings`, `potato_beef_stew`, `red_sweet_potato_porridge`, `sour_spicy_noodles`。

### 仍缺系統／世界內容

- 其餘 crafting / chopping / pot / stockpot / flexible cooking / milling / crushing / roasting / smoking / campfire / chili-oil mixing 配方。
- `advanced_rack`。
- Canola / Onion / Sweet Potato / Houttuynia 四種作物。
- Pepper log / leaves / sapling、掉落與 worldgen。
- Java 21 advancements 的 Bedrock 等價記錄。
- Guide 單一入口的完整動態內容。
- Plate 世界方塊逐根串動態 3D renderer。
- Oil Residue 對非 age-state 骨粉目標的差異。
- Minecraft 客戶端 / BDS / 多人 / 重載持久化實機驗收。

## 6. 驗證邊界

新增純邏輯測試鎖定：

- 30 ticks / 1.5 秒。
- 29 ticks 不完成、30 ticks 才完成。
- 1、37、64 個紅薯粉等量轉換。
- 非紅薯粉不觸發。
- Java Chopping Board 的 4-cut 數值以常數保留給下一小批。

CI 從 A2.0 一路重建到 A2.6，再套 A2.7.1，對所有 gameplay script 執行 `node --check`，跑 A2.4/A2.5/A2.6/A2.7.1 純邏輯回歸，最後用 checksum-pinned bridge. Dash v1.2.0 編譯並逐檔比較 source / dist。

**Dash / Node 通過仍不等於 Minecraft 26.51 客戶端或 BDS 實機通過。**
