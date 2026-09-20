# A2.3.0 — Hot Food 堆疊、烤爐四態、效果收斂與世界油模擬

A2.3 建立在 A2.2 的固定串／逐口3D核心之上，處理此前列出的五項重要差異：Hot Food 堆疊與 OrderToCook 冰箱整理語義、烤爐 flat/legged + lit/unlit、Cookery Java 效果的引擎差異、Numb 準星可行性、以及三種世界油。

基準：
- Java Grilling 1.1.1：`breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c`
- Cookery 依賴：Bedrock 1.0.6
- Bedrock retail：26.51 / content 1.26.50
- Script API：穩定版 `@minecraft/server 2.9.0`
- 不要求實驗開關

## 1. Hot Food 堆疊與「冰箱整理」

41個正式食物現在恢復：

`minecraft:max_stack_size = 64`

Bedrock 對含 Dynamic Properties 的 ItemStack 會判定為不可原生自動堆疊，因此 A2.3 不刪除 HotUntil / seasoning 來換堆疊，而是以腳本手動整併。

### 合併規則

只有：
- 同一物品類型
- 除 HotUntil、模型變體、作者資訊外，其餘自訂資料一致
- 熱／冷狀態相同

才可做一般合併。

兩堆熱串合併時按 Java `HotFoodMerge`：

`newRemaining = (heatA*countA + heatB*countB) / (countA+countB)`

並重新按100 ticks / 5秒分桶寫回 HotUntil。

例如：

- 2根剩1200 ticks
- 1根剩600 ticks

合併後3根剩約1000 ticks。

烤爐出爐進玩家背包時會先嘗試併入已有相容堆。

### OrderToCook Refrigerator 語義

Java 的「冰箱」不是 Grilling 或 Cookery 自己的保鮮箱，而是可選 Java 模組 **OrderToCook** 的 Refrigerator。

Grilling 的相容層只做：
- 串類整理／壓縮
- 同資料串的 HotUntil 加權平均
- Normal Sort：熱度差 ≤ 6000 ticks（5分鐘）才合併
- Full Sort：忽略熱度差做完整整併

**不會延長 HotUntil、不會停止熱食倒數，也不是冷藏保鮮機制。**

Bedrock 沒有 OrderToCook，所以 A2.3 將核心整理算法做成通用容器功能：
- 蹲下＋空手互動 Chest
- Trapped Chest
- Barrel

會執行 Normal Sort（5分鐘熱度窗口）。

Full Sort 算法已保留在核心，但目前沒有另造不自然的玩家按鍵／道具去模擬 OrderToCook GUI 按鈕。

Java 相容層內部可把冰箱整理堆到128；Bedrock A2.3 遵循正式物品上限64。

## 2. 烤爐 flat / legged + lit / unlit

正式 `kaleidoscope_grilling:grill` 現在新增兩個穩定 custom block states：

- `kaleidoscope_grilling:legged`
- `kaleidoscope_grilling:lit`

四套原始已驗證模型正式接入：

- flat + unlit
- flat + lit
- legged + unlit
- legged + lit

仍保留原本 cardinal direction state 與3槽 BlockEntity；切換只使用同一 block type 的 BlockPermutation，不重建方塊，所以容器槽位和世界持久狀態不應因視覺切換而重置。

### 支撐判定

Java 使用：

`!below.isFaceSturdy(Direction.UP)`

Bedrock 26.51 stable 沒有同等的 top-face-sturdy 判定，因此使用：

`legged = !below.isSolid`

這是目前最接近的穩定引擎判定。一般完整方塊／空氣與原作行為一致；特殊半磚、極薄支撐仍可能有差異，需 Minecraft 實機檢查。

### 點火視覺

點火狀態立即同步 `lit=true`，切換到原作 lit geometry + `grill_lit` 貼圖。

Bedrock lit 材質：
- face_dimming=false
- ambient_occlusion=0
- light_emission=13

原 Java GrillBlock 本身並沒有真正 block light emission；它使用火焰模型／貼圖。因此 Bedrock 的13級動態光是依使用者需求增加的視覺增強，不冒充 Java 精確行為。

## 3. Cookery 效果引擎差異收斂

### Tundra Strider

Java公式：

`1.1 + max(1-friction,0)*0.5`

A2.3 不再固定塞 Speed I，而是按站立方塊使用接近 Java 的水平速度增量：

- snow-like：約1.30
- ice / packed / frosted：約1.11
- blue ice：約1.1055

Powder Snow 仍以穩定 API 的向上 impulse 模擬「不下沉」。Bedrock無法直接覆寫 block speed factor 或 PowderSnow canWalkOnPowderSnow，因此這部分仍為語義近似。

### Mustard

Java：Creeper 動態加入 AvoidEntityGoal，半徑6，逃跑速度1 / 1.2。

Bedrock stable 沒有可寫 AI Goal／target API。A2.3 把腳本排斥收斂到**6格範圍的 flee-like push**，但仍不是原生 AI Goal。

### Sulfur

Java：每5 ticks，在水平±8、垂直±16 AABB 內，如果 Phantom 的 target 是效果持有者，就清掉 target。

Bedrock stable 的 Entity.target 仍是 experimental/read-only，不能安全清 target。A2.3 改成精確使用 **8×16 AABB-like 範圍**篩選，再做 flee-like push；比 A2.2 的球形16格更接近，但仍不是 target=null 的引擎級一比一。

### Dragon Blood

Java：
- I：max health +6
- II：max health +10

A2.2 只有 Health Boost I/II → +4/+8。

A2.3 改為：
- 原生 Health Boost 顯示 +4/+8
- 再加2點腳本虛擬生命池
- 傷害先消耗這2點，再把剩餘傷害以原 cause 重新套用
- 所以**總有效生命提升為精確 +6/+10**

限制：Bedrock HUD 顯示的原生最大生命仍只看到 +4/+8；額外2點是腳本傷害池，不會多畫1顆心。這是總有效HP精確、UI最大生命非1:1。

## 4. Numb 準星

A2.2 已完成 Java Numb 的四肢異常擺動。

Java 準星繞圈是直接 Mixin HUD crosshair render position。Bedrock 26.51 stable 沒有：
- per-player crosshair offset API
- 安全的腳本 HUD 元素座標覆寫

A2.3 **沒有**加入全局 `ui/hud_screen.json` 覆蓋，因為那會：
- 對所有玩家生效
- 容易跟 Cookery／其他 RP 衝突
- 無法只在 Numb 效果期間安全控制

因此 Numb 準星仍明確標為「26.51 stable 無安全等價」，不是漏做或假裝完成。

## 5. 三種世界油

Bedrock 26.51 stable 仍不能讓 Add-On 註冊新的引擎 `LiquidType`，所以不能得到 Forge Fluid 完全同等的引擎流體。

A2.3 不再停留在資料契約，而是新增**世界可用的 scripted fluid simulation**：

- canola oil
- secret chili oil
- premium chili oil

每種：
- 8個液面高度
- 無碰撞
- 可被方塊取代
- source level 0
- 向下優先流動
- 遇阻後水平擴散
- 不同黏度使用不同更新頻率
- 移除 source 後清理自身生成的 flowing cells
- 油桶可放置 source
- 空桶可回收 source
- Cookery 空油壺可直接從 source 灌滿256
- 油型寫入 `kaleidoscope_grilling:oil_type`

Java油參數保留為設計基準：
- 菜籽油 density 900 / viscosity 1600
- 辣椒油 950 / 1800
- 熔岩辣椒油 1000 / 2000
- 熔岩辣椒油世界方塊 light_emission 15

A2.3 的更新頻率依黏度分級，但這仍是腳本流體，不是 Forge／Bedrock engine LiquidType，因此水下物理、游泳、原生流體混合、引擎流速等不宣稱1:1。

## 驗證

成功 CI：
https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/35492689153

回歸／行為：
- A2.0：16/16
- A2.1 state：4/4
- A2.1 runtime：18/18
- A2.2 runtime：12/12
- A2.3 Hot Food 純算法：5/5
- A2.3 runtime：15/15
- 合計：**70/70**

A2.3 runtime 實際測到：
- 熱串數量加權合併
- Chest Normal Sort 五分鐘窗口
- 無支撐→legged
- 點火→lit
- 加實心支撐→flat
- Dragon Blood 2點差額傷害池
- Dragon Blood 剩餘傷害重播
- Tundra snow-like 30%水平增量
- Mustard 6格 flee
- Sulfur 8×16範圍
- 油桶放 source
- 菜籽油水平流動
- 空桶回收
- source 移除後清理流動油
- Cookery 空油壺從世界油灌滿256並保存油型

官方 bridge. Dash v1.2.0：
- 實際編譯：592 files
- BP：74個來源檔逐檔一致
- RP：518個來源檔逐檔一致

輸出 SHA-256：
- `Kaleidoscope_Grilling_A2.3_Gameplay_Core.mcaddon`
  `4c9cf36606366697e484d52cfbab6debb34eaf9086be3a8e89e739fe7ca90bdc`
- `Kaleidoscope_Grilling_A2.3_Gameplay_Core.brproject`
  `acb8959a05768f825a97921b4d0a987c59e8cfe8b11069c7dfc3ecd13182cd82`

## 驗收邊界

仍沒有 Minecraft 26.51 客戶端／BDS 實機驗收。

尤其需要實機觀察：
- custom block states 切換是否在 BlockEntity 容器開關／區塊卸載時保持槽位
- lit材質與13級動態光實際效果
- scripted oil 在區塊邊界、多來源重疊、伺服器延遲下的表現
- Hot Food amount>1 + Dynamic Properties 在真遊戲存檔／搬箱／丟地上的序列化
- Tundra velocity 模擬手感
- Dragon Blood HUD與2點虛擬生命的玩家理解

Numb準星和真正引擎LiquidType仍是明確的平台差異。
