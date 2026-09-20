# A2.0.0 — Gameplay Core

A2.0 是第一個正式 `kaleidoscope_grilling` 可玩核心。它不再使用 `kg_imm` 驗收物品代表正式玩法，而是新增正式 BP/RP、正式固定串物品，以及真正具有三個容器槽位的 `kaleidoscope_grilling:grill`。

基準：
- Java 原版：`breezeth-CN/KaleidoscopeGrilling` commit `9a1acdab27698457bec16c9362678e574895a28c`（1.1.1）
- Bedrock retail：26.51；內容格式以 1.26.50 為目標
- Script API：穩定版 `@minecraft/server 2.9.0`
- Cookery：1.0.6，BP `10f37ae2-9ccf-435f-b34b-0eec8191cd94`，RP `c89dc8df-c3fc-4bc8-8bd0-527abba76681`

## 已完成的核心閉環

### 正式固定串
從鎖定 Java `ModItems.java` 與 `grilling/skewers.json` 自動抽取而非手抄：

- 19 組可烤固定生串 → 對應熟串
- 普通串
- 謎之燒烤
- 黑暗燒烤
- 共 41 個正式串類食物物品
- 另有 5 個 A2.0 支援物品：三種暫時油刷、特殊調料瓶、空調料瓶
- 全部使用正式 `kaleidoscope_grilling:` namespace

牛肉、魚、羊肉、黃金串等營養／飽和值及 profile 已回讀生成結果抽查，與 Java 資料一致。

### 真正三槽烤爐
`kaleidoscope_grilling:grill` 使用新的 `minecraft:block_entity` 容器，實際有 3 個槽位。流程：

1. 打火石點火
2. 放入最多三個正式生串
3. 刷油
4. 翻面四次；每次 20 tick 冷卻
5. 撒料
6. 空手取串；蹲下可一次全取

狀態規則對齊 Java `GrillBlockEntity`：

- phase 0：等待刷油
- phase 1：翻面階段
- phase 2：等待調味／完成
- phase 3：過熟
- 800 個點火且有串的 tick 未完成 → phase 3
- phase 3 再 400 tick → 1–2 木炭並清空
- 中途破壞：phase0 返還生串；未完成返還謎之燒烤；已完成調味返熟串；phase3 返黑暗燒烤

三個物品槽由 BlockEntity 自身保存。流程 phase/flips/timer 等狀態使用穩定版 world dynamic properties 按「維度＋方塊座標」保存；**刻意不用 26.60 Preview 才提供腳本存取的 BlockDynamicPropertiesComponent**，避免 A2.0 變成 Preview 專用包。

### 真正食物與提前結算
正式串物品已使用 Bedrock `minecraft:food`、`minecraft:use_modifiers` 與 `minecraft:use_animation`。

- Java 六種 profile 資料沿用 A1.16 骨骼動畫
- 25 tick（1.25 秒）最低食用檢查點已在 A2 運行時實作
- 在完整動畫結束前、但已達 25 tick 時放開：腳本直接結算真實 hunger / saturation，並只消耗一次物品
- 完整食用則交回原生 Bedrock food chain
- 生蟲串、生末影珍珠串、生史萊姆串的噁心效果已接
- Java 原版能直接映射到 Minecraft 原版的熟串 Buff 已接，例如牛肉 Strength、雞皮 Speed、魷魚 Water Breathing、蘑菇 Night Vision、肉丸 Strength 等
- 黃金串的 10 秒 Invincible 先以 A2 自有持久時間＋ hurt-before-event 阻傷實作

## A2.0 驗證結果

成功 CI：
https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/35487932877

- Java 烤爐狀態機單測：16 / 16
- 生成後 A2 運行時模擬：19 / 19
  - 真三槽
  - 點火
  - 三串插入
  - 刷油
  - 四翻
  - 調味
  - 三串熟化輸出
  - 800 tick 過熟
  - 黑暗燒烤
  - 800+400 tick 木炭
  - 中途破壞 → 謎之燒烤
  - 25 tick 提前進食
  - hunger / saturation
  - 牛肉 Strength
  - A1.16 FOUR 玩家動畫
- 結構驗證：46 個正式物品、其中 41 個食物；19 組 raw→cooked；真 3 槽 BlockEntity
- 官方 bridge. Dash v1.2.0：實際編譯 121 個檔案
- 真 Dash 輸出逐檔比對：
  - BP 52 個檔案一致
  - RP 69 個檔案一致
- mcaddon / brproject ZIP 完整性通過

輸出 SHA-256：
- `Kaleidoscope_Grilling_A2.0_Gameplay_Core.mcaddon`: `a884ef3e8de58dbd4346532591e2b2ac1d0aaade2a0cec770cb9f6d79586b63f`
- `Kaleidoscope_Grilling_A2.0_Gameplay_Core.brproject`: `d917ae197db056d73aac4685e67246e7317918d4263f403583ea9d567d192851`

## 仍未達 Java 完全等價

A2.0 是「核心閉環」，不是全模組完成。

### 烤爐仍有差異
- Java 直接使用 Cookery `oil_pot` 的 `oil_count / grilling_oil_type`；A2.0 暫用三個正式煙火油刷物品代表三種熱持續時間
- 打火石耐久尚未扣除
- Cookery `extinguish_stove` 熄火工具尚未接
- Java 會依底部支撐在 flat / legged 外觀間切換；A2.0 第一版固定使用 legged 幾何
- 點火版自發光／光照幾何還沒有動態切換

### 調味／熱食未完整
- 特殊調料瓶目前只有 16 次使用計數；六種調料內容還沒保存到串
- Java 的 speed/strength/duration/totem/vitality/numbness 調料運算尚未接
- cooked stack 目前只寫 preliminary hot metadata，完整 HotUntil、熱食 Buff 時長翻倍、飽和加成、合併規則未接
- Cookery 專屬熟串效果（vigor、mustard、tundra_strider、preservation、flatulence、projectile_dodge、hinder、sulfur、warmth）目前不偽造替代效果；會提示待 A2.x 對接

### 食用表現未完全
- A1.16 玩家骨骼時間線已復用，但正式固定串目前仍主要用 16×16 原作圖示，尚未把每一種固定串的 3D attachable / 每口幾何切換接到正式物品
- 暫時把串的 max stack 設為 1，確保 item dynamic metadata 不會被堆疊語義破壞；Java 可堆疊行為稍後恢復
- 普通串的「最強之矛 vs 無敵」特殊致死／格擋邏輯尚未移植
- 黃金串 Invincible 已有核心阻傷，但粒子、generic-kill 例外與完整 Java 反饋仍待補

### 尚未進入 A2.0
- 自由／秘制串穿串與拆串
- 餐盤
- 串譜
- 榨油機
- 大缸
- 三種真流體
- 高級厨具架
- 作物生長／掉落
- 花椒世界生成
- 菜肴與 61 份 Java 配方的等價實作
- 成就
- 指南動態搜尋／收藏／自訂配方 UI
- Create / JEI / Jade / 女仆等 Java 生態功能的 Bedrock 等價方案

## 驗收邊界

A2.0 已通過原始資料鎖定、程式單測、模擬 Bedrock 事件宿主、結構檢查和真 Dash 編譯；**尚未在 Minecraft 26.51 客戶端或 BDS 實機啟動**。因此 BlockEntity 容器 UI、實際事件順序、動畫與物品位置、世界重進後狀態恢復仍需要下一層實機驗收。
