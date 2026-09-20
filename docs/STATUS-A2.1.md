# A2.1.0 — Cookery 油壺、調料、煙火氣與效果等價層

A2.1 建立在 A2.0 真三槽烤爐之上，重點把此前最影響「烤一串→趁熱吃掉」完整體驗的缺口補進正式 `kaleidoscope_grilling` Gameplay Core。

基準：
- Java Grilling 1.1.1：`breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c`
- Bedrock Cookery：使用者提供的 **Kaleidoscope Cookery 1.0.6**，SHA-256 `c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351`
- Cookery BP：`10f37ae2-9ccf-435f-b34b-0eec8191cd94`
- Cookery RP：`c89dc8df-c3fc-4bc8-8bd0-527abba76681`
- Bedrock retail 目標：26.51 / content 1.26.50
- Script API：穩定版 `@minecraft/server 2.9.0`

## 1. Cookery 油壺已直接接線

從實際 Cookery 1.0.6 包核對到：

- 空油壺：`kaleidoscope_cookery:oil_pot`
- 裝油油壺：`kaleidoscope_cookery:oil_pot_filled`
- 容量：256
- item dynamic property：`kc_oil_count`
- 舊版／無屬性的 filled pot 視為 256
- 油耗盡後回到空油壺

A2.1 烤爐現在直接接受 **Cookery 裝油油壺**，並和 Java `GrillAutomationApi.brushOil` 一樣：

> 爐上有幾串，就一次消耗幾點油。

例如三槽都有串：10/256 → 刷油後 7/256。

Bedrock Cookery 1.0.6 本身只有通用油，沒有 Java Grilling 的 `grilling_oil_type`。因此原生 Cookery 油壺目前使用 Java default/canola 的熱度 **1200 ticks**；A2.1 保留 Grilling 自有 oil_type 擴充鉤子，等真辣椒油流體進 A2.x 後再提供 12000 / 24000 ticks。

A2.0 三個臨時刷具仍保留作相容／測試入口，但正式流程會提示使用 Cookery 油壺。

## 2. 調料瓶不再只是動畫

新增正式：

- `kaleidoscope_grilling:seasoning_bottle` 方塊
- `empty_seasoning_bottle`
- `pending_seasoning`
- `special_seasoning`
- 六種正式調料材料：
  - 青辣椒粉
  - 花椒
  - 洋蔥粉
  - 魚腥草粉
  - 圖騰粉
  - 龍蛋粉

另外可加入原版：
- Redstone
- Gunpowder

流程：

1. 放下空調料瓶
2. 逐個加入最多 **8份**材料
3. 基礎三料必須包含：
   - `green_chili_powder`
   - `sichuan_pepper`
   - `onion_powder`
4. 空手取回後成為 Pending Seasoning
5. 持續使用 **80 ticks / 4秒**搖勻
6. 轉為 Special Seasoning，保留完整材料列表與隨機 variant 0–7
7. 成品瓶共有 **16次**使用

烤爐撒料時和 Java 一致按槽位收費：爐上3串，就扣3次，不再是 A2.0 固定扣一次。配料列表被保存到烤爐狀態，再寫入每根熟串。

目前調料瓶方塊實作一個可編輯瓶；Java 原版同一方塊最多能物理堆4瓶。四瓶物理堆疊仍是 A2.x 缺口。

## 3. Hot Food / 煙火氣

熟串現在保存：

`kaleidoscope_grilling:hot_until`

時間基準使用穩定版 `world.getAbsoluteTime()`，所以不是 `system.currentTick`，重進世界後不會重新開始倒數。

Java 的5秒分桶也保留：

> hot_until 向下取 100 ticks 的倍數。

手持熱串會顯示 🔥煙火氣剩餘時間。

熱著吃的核心規則：

- 飽食度 nutrition 不變
- **飽和度新增量 ×125%**
- 食物本身新加的 Buff 時長 ×2
- Grilling Invincible 不翻倍
- 調料效果在 Hot Food 翻倍之後才套，因此**調料效果不會再被煙火氣二次翻倍**

25 tick / 1.25 秒提前進食路徑也使用同一套熱食計算。

## 4. 六類調料效果

Java Grilling 的調料規則已接：

- Redstone → Speed
- Gunpowder → Strength
- Houttuynia Powder → duration
- Totem Powder → Heavy Metal / 死亡保護
- Dragon Egg Powder → Dragon Blood
- Sichuan Pepper ×4以上 → Numb

基礎 Buff 時間 3600 ticks。

魚腥草粉：
- 1–3份：時間 ×2
- ≥4份：時間 ×4

Redstone / Gunpowder：
- 1–3份：I
- ≥4份：II

花椒：
- 至少4份才啟動 Numb
- 基準900 ticks
- 同樣受魚腥草粉 ×2 / ×4

圖騰粉：
- Heavy Metal
- 受到致死傷害時保命到1HP
- 消耗 Heavy Metal
- 進入12000 ticks / 10分鐘 Heavy Metal Poisoning
- 中毒期間不能重新獲得該保命

龍蛋粉：
- Dragon Blood 已建立持續效果等價層
- Bedrock 使用 Health Boost 作穩定近似
- Java 精確是 +6 / +10最大生命；Bedrock目前是 Health Boost I/II 的 +4 / +8，因此**不是精確一比一**

Numb 的持續狀態已存在，但 Java 的「準星繞圈＋走路四肢夸張擺動」屬客戶端 Mixin 表現，A2.1 尚未完全還原。

## 5. Java Cookery 專屬效果的 Bedrock 等價層

Bedrock Cookery 1.0.6 **沒有** Java Cookery 的以下 effect IDs，所以 A2.1 沒有假裝宿主能直接提供，而是按 Java Cookery 源碼語義建立自己的持續狀態。

已實作：

- **Vigor**：衝刺期間阻止饑餓／飽和度下降的等價邏輯
- **Warmth**：附近熱源每秒回血1；下界每秒25%概率回血0.5
- **Flatulence**：蹲下按鍵上升沿提供 Y +0.75 衝量及粒子／聲音
- **Hinder**：持有效果者近戰命中 → 目標 Slowness II 100 ticks
- **Projectile Dodge**：投射物傷害取消，嘗試隨機閃現，並從效果剩餘時間扣200 ticks
- **Tundra Strider**：雪／冰面 Speed I；粉雪給少量上浮避免快速下沉
- **Mustard**：腳本方式排斥附近 Creeper
- **Sulfur**：腳本方式排斥附近 Phantom
- **Preservation**：危險食物完成後清除 Hunger / Poison / Nausea

其中：
- Vigor 是 Bedrock hunger/saturation 還原，不是直接操作 Java exhaustion 內部值。
- Tundra Strider 的粉雪完全可行走與 Java speed-factor 不是同一引擎機制。
- Mustard / Sulfur 是 scripted repel，不是 Java AI Goal / target 清除。

這三類屬**語義等價近似**，不是引擎級一比一。

## 6. 普通串與黃金串

黃金串：
- Invincible 改用**世界絕對時間**保存
- 傷害前事件中取消一般傷害
- `/kill` / override 類型不攔截
- 跨世界重進的時間語義比 A2.0 system.currentTick 版本穩定

普通串：
- 有 Invincible 時先消耗 Invincible
- 50% 機率擋住普通串致死效果
- 沒擋住則死亡
- 沒有 Invincible 時直接死亡

這與 Java `CursedSkewerItem` 的核心判定一致；成就尚未接。

## 7. 正式3D手持串

A2.1 將之前經過素材驗證的模型真正接回正式物品：

- 19種生固定串
- 19種熟固定串
- 普通串
- 合計 **39個正式 attachable**

根骨使用：

`q.item_slot_to_bone_name(context.item_slot)`

所以不再只是16×16 GUI圖示拿在手裡。

目前接的是每種串的**完整基礎3D外觀**。逐口咬食時切到 bite1/bite2/bite3/bite4 的正式幾何仍未放進 A2.1，因為那一層还需要 Minecraft 实机确认 item attachable 切换与 A1.16 玩家骨骼的同步方式。

## 8. 驗證

成功 CI：
https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/35489240344

行為測試：
- A2.0 Java 烤爐狀態機回歸：**16 / 16**
- A2.1 seasoning state：**4 / 4**
- A2.1 完整模擬運行：**18 / 18**
- 總計：**38 / 38**

18項 A2.1 模擬包含：
- 8份材料 → pending
- 80 tick搖瓶 → special
- Cookery油壺三串消耗3點
- 三串調味消耗3次
- 配料列表持久化
- HotUntil絕對時間分桶
- Hot Food 125%飽和
- 牛肉 Strength 熱食翻倍
- Redstone Speed不二次翻倍
- 4份花椒啟動Numb
- Vigor
- Hinder
- Projectile Dodge
- Golden Invincible
- Ordinary 50% challenge / 無Invincible致死

結構：
- 正式物品：**53**
- 正式食物：**41**
- 可烤固定串：**19組**
- 正式3D attachable：**39**
- Script API：**2.9.0**

官方 bridge. Dash v1.2.0：
- 實際編譯：**257 files**
- BP逐檔比對：**60**
- RP逐檔比對：**197**
- 全部一致

輸出 SHA-256：
- `Kaleidoscope_Grilling_A2.1_Gameplay_Core.mcaddon`
  `a897348791cd7732e763d58375c68892d24243cdc984927c9c797e06512b715d`
- `Kaleidoscope_Grilling_A2.1_Gameplay_Core.brproject`
  `e24e51f9622891e85c99f2ab0d43af1e5497e229dda6113ebea7eda746971fe0`

## 9. 仍未完成

A2.1 仍不是 Java 全功能版，下一批主要差距：

- Minecraft 26.51 客戶端／BDS 真實驗收
- 正式串逐口 3D bite-stage 切換
- Numb 準星與四肢視覺
- 調料瓶同方塊最多4瓶的物理堆疊
- Java辣椒油／熔岩辣椒油真流體及 Cookery 油壺類型
- 自由／秘制串
- 餐盤
- 串譜
- 榨油機
- 大缸
- 高級厨具架
- 作物生長／世界生成
- 61份配方等價層
- 成就
- 指南搜尋／收藏／自訂配方 UI
- Java模組生態兼容的 Bedrock 替代方案

A2.1 已通過鎖定來源、單元／模擬運行、結構檢查及真 Dash 編譯，但**沒有宣稱已在 Minecraft/BDS 實機運行**。
