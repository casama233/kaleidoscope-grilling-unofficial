# A2.7.4 — Java 原版物品欄圖標逐檔同源

> 這是 A2.7.3 顯示穩定化之後的 icon hotfix。  
> **不新增食材、配方、方塊或玩法。**  
> 目標只有一個：固定串類在 Bedrock 物品欄中直接使用 Java 1.1.1 原模組預設的 GUI 圖標資源。

## 1. A2.7.3 的做法為什麼仍然不對

A2.7.3 已修掉最早的嚴重錯誤：不再把 Java 3D 模型 UV/material sheet 當成 Bedrock 2D icon。

但 A2.7.3 接著自己用 Python：

- 解析 Java item model；
- 套用 `display.gui`；
- 把 3D 模型光柵化成 64×64 PNG。

這仍不是 Java 原模組預設的物品欄顯示方式，而且第一版 renderer 的 Euler 旋轉乘法順序也與 Java/JOML `rotationXYZ` 不一致，因此生成出的串大多呈現不自然的直立狹長姿態。

更重要的是，重新核對 Java 1.1.1 後發現：**根本不需要重畫。**

## 2. Java 原模組已有正式 GUI icon

Java 上游：

`forge-1.20.1/.../skewer/SkewerGuiIconCache.java`

對固定配方串在預設配置下直接使用：

`textures/item/fixed_skewer_gui_16/*.png`

而：

`HotFoodConfig.USE_FIXED_SKEWER_64X_CACHE`

預設值為：

`false`

上游配置註釋也明確寫明：

- 開啟：固定配方串使用生成的 64×64 GUI 圖標；
- 關閉：使用**手繪 16×16 圖標（預設）**。

所以「Bedrock 物品欄跟 Java 一樣」最穩定的方式不是模擬 Java renderer，而是直接使用 Java 自己隨模組發布的這批正式 GUI PNG。

## 3. A2.7.4 的處理方式

Java 基線：

`breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c`

來源目錄：

`common/src/main/resources/assets/kaleidoscope_grilling/textures/item/fixed_skewer_gui_16/`

A2.7.4 對現有 41 個正式串類／失敗產物逐個建立映射，將 Java 原 PNG **原始 bytes** 放入：

`resource_pack/textures/items/<bedrock_item_id>.png`

每一張都：

- 必須是 16×16；
- 使用固定上游 commit；
- 使用 Git blob SHA-1 驗證；
- 不經 resize；
- 不經重新繪製；
- 不經色彩校正；
- 不經 Python 3D renderer。

因此對 39 個靜態圖標，A2.7.4 的最終 PNG 與 Java 原模組對應 GUI PNG 是逐 byte 同源的。

## 4. 兩個 Java 動畫 icon

Java 有兩個不是單一靜態圖：

### 熟史萊姆串

Java 在：

`grilled_slime_skewer_cooked_frame_0..4.png`

之間按：

`(gameTime / 4) % 5`

切換。

A2.7.4 目前使用 Java 原版：

`grilled_slime_skewer_cooked_frame_0.png`

所以圖像本身是**精確 Java frame 0**，但 Bedrock 物品欄動畫尚未標為完成。

### 謎之烤串

同理，Java 使用：

`mysterious_skewer_frame_0..4.png`

每 4 game ticks 切換。

A2.7.4 使用 Java 原版：

`mysterious_skewer_frame_0.png`

同樣是 exact frame 0，而不是完整動畫 parity。

這兩項被明確記錄為 **animation-only gap**，不拿一張靜態圖冒充完整 Java 動畫。

## 5. 與手持 3D 顯示完全分離

A2.7.4 只替換 `minecraft:icon` 最終引用的 PNG。

它不修改：

- attachables；
- A2.2 分口 geometry；
- 第一／第三人稱手持；
- 進食動畫；
- 烤架模型；
- A2.7.3 `grill_legs` helper；
- 配方或 gameplay script。

也就是：

- **物品欄 = Java 原版 GUI PNG**
- **手持／進食 = Bedrock 3D attachable**

不再互相污染。

## 6. CI 驗證

A2.7.4 CI 會從 A2.0 完整重建到 A2.7.3，再套這個 hotfix。

必須驗證：

- 正好 41 個正式 icon；
- 全部為 16×16；
- 每個 icon 的 Git blob SHA-1 等於鎖定 Java 上游；
- `item_texture.json` 仍指向正確 item id；
- 39 個 static exact；
- 2 個 exact frame-0 + animation gap；
- A2.7.3 烤架 helper 修復仍存在；
- 所有 gameplay JS 語法；
- checksum-pinned Dash v1.2.0；
- source / dist 逐檔一致；
- mcaddon / brproject 可完整打包。

## 7. 驗收邊界

這一版可以證明：

**PNG bytes 與 Java 原 GUI 資源完全相同。**

但在使用者真正把 A2.7.4 裝進 Minecraft 以前，仍保持：

- `minecraft_tested=false`
- `bds_tested=false`

也不把史萊姆／謎之烤串的 5-frame 動畫標成完成。

原本規劃的下一批基礎切配食材再次順延到 **A2.7.5**；在 UI/手持/烤架等實機底座通過前，不再往上堆新內容。
