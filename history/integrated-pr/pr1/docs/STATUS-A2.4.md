# A2.4.0 — 手工穿串、秘制烤串與 Java 差異重盤點

A2.4 建立在 A2.3 的固定串／逐口 3D／Hot Food／烤爐／調料／世界油核心之上，開始補齊 Java Grilling 1.1.1 最大的一段缺口：**玩家不是直接拿到生串，而是從木棍與食材逐份穿成固定串或秘制烤串**。

本文件同時重新區分兩條基準：

- **Grilling 本體基準**：Java `breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c`（Grilling 1.1.1）
- **Cookery 依賴基準**：目前 Bedrock 仍依賴 Kaleidoscope Cookery Bedrock **1.0.6**
- **Java Cookery 現況**：CurseForge 正式版已到 **1.5.0（2026-09-18）**
- Bedrock retail：26.51 / content 1.26.50
- Script API：穩定版 `@minecraft/server 2.9.0`
- 不要求實驗開關

> 注意：這個倉庫是 **Grilling 的 Bedrock 移植**。  
> 因此「Grilling 1.1.1 功能差異」與「Cookery 1.5.0 相對 Bedrock Cookery 1.0.6 的依賴漂移」必須分開處理。後者不是單靠 Grilling 包就能完整修復。

---

## 1. A2.4 新增：Java 20 條手工穿串規則

Java `grilling/skewers.json` 中有 **20 條可穿串結果**：

1. 生牛肉串
2. 生五花肉串
3. 生雞皮串
4. 生雞中翅串
5. 生魷魚鬚串
6. 生魚串
7. 生苕皮串
8. 生土豆片串
9. 生毛毛蟲串
10. 生蘑菇串
11. 生饅頭片串
12. 生終界珍珠串
13. 生肉丸串
14. 生史萊姆串
15. 生肉骨串
16. 生煎蛋串
17. 生麵筋串
18. 生羊肉串
19. 生黃金串
20. 普通烤串

A2.3 的說法「19 組 raw→grilled + ordinary」本身沒有漏掉 Gluten；A2.4 現在把這 **20 條有序食材規則**真正接到玩家操作，而不只是保留最終成品 ID。

規則來源直接對照 Java：

- 牛肉塊 + 紅辣椒 + 牛肉塊 → 生牛肉串
- 五花肉 + 青辣椒 + 五花肉 → 生五花肉串
- 雞皮 ×2 → 生雞皮串
- 雞翅 + 紅辣椒 + 雞翅 → 生雞中翅串
- 魷魚鬚 ×3 → 生魷魚鬚串
- 鱈魚／鮭魚／熱帶魚／河豚 → 生魚串
- 生苕皮 + 折耳根末 ×2 → 生苕皮串
- 土豆片 ×3 → 生土豆片串
- 毛毛蟲 → 生毛毛蟲串
- 紅／棕蘑菇 + 胡蘿蔔粒 + 紅／棕蘑菇 → 生蘑菇串
- 生饅頭片 ×3 → 生饅頭片串
- 終界珍珠 + 甜菜根 + 終界珍珠 → 生終界珍珠串
- 生肉丸 ×3 → 生肉丸串
- 史萊姆球 + 折耳根 + 史萊姆球 → 生史萊姆串
- 生小切肉 + 骨頭 + 生小切肉 → 生肉骨串
- 煎蛋 ×2 → 生煎蛋串
- 生麵團 ×2 → 生麵筋串
- 生羊排 + Cookery 油 + 生羊排 → 生羊肉串
- 金蘋果 + 不死圖騰 + 金胡蘿蔔 → 生黃金串
- 毒馬鈴薯 + 蜘蛛眼 + 河豚 → 普通烤串

### 操作

與 Java 語義一致：

- 副手：木棍／未完成烤串／未烤熟秘制烤串
- 主手：食材
- 互動：向串上增加一份食材
- 最多三份
- 完整命中固定配方：直接轉成對應固定串
- 三份仍未命中固定配方：轉成秘制烤串
- 蹲下互動未完成串／可拆的生串：返還食材與木棍

A2.4 已攔截：
- `WorldBeforeEvents.itemUse`
- `playerInteractWithBlock`
- `playerInteractWithEntity`

以盡量覆蓋 Bedrock 不同的右鍵／使用入口。

### Bedrock 輸入邊界

Java Forge 能直接接管 `RightClickItem`，即使主手物品本身沒有原生 use 行為也可攔截。

Bedrock stable 的 `itemUse` 語義是「物品成功被使用」，所以**某些沒有任何原生使用動作的 vanilla 物品在純空氣右鍵時是否送出事件，需要 Minecraft 實機驗收**。

對方塊／實體互動已另外接管，因此即使純空氣右鍵受引擎限制，仍有 stable API 可玩的穿串入口。這一點不能在沒有客戶端實機測試前宣稱與 Forge 100% 相同。

---

## 2. A2.4 新增：未完成烤串與秘制烤串

新增正式物品：

- `kaleidoscope_grilling:unfinished_skewer`
- `kaleidoscope_grilling:secret_skewer`

秘制烤串跟 Java 一樣使用**同一個 item ID**，用自訂資料記錄 raw/cooked，而不是另造 raw_secret / cooked_secret 兩個 ID。

每根串目前保存：

- 最多 3 個食材 ID
- 3 個視覺 variant seed
- 作者名稱
- 作者 ID
- cooked 狀態

烤爐插入、取出、烤焦／神秘失敗分支都已改為保留 ItemStack 自訂資料；A2.3 原本重新 `new ItemStack` 的路徑會丟掉 Secret Skewer 內容，A2.4 已修復。

---

## 3. Secret Mix 營養公式

Java `SecretSkewerItem` 公式已移植：

1. 把三份食材的 nutrition 相加
2. saturation modifier 依各食材 nutrition 加權
3. 基礎係數 `0.6`
4. 有重複食材再乘 `0.8`
5. nutrition 向下取整，最少 1
6. 生秘制串再把 nutrition ×0.5、saturation ×0.5
7. 熟秘制串使用熟食映射後的食材資料計算

即：

`finalNutrition = floor(sumNutrition × 0.6 × duplicatePenalty)`

其中：

`duplicatePenalty = 0.8`（有重複）或 `1.0`（無重複）。

A2.4 不是把所有食物數值抄死，而是使用 Bedrock `minecraft:food` component 的 `nutrition` / `saturationModifier` 讀取可用資料。

### 尚未 1:1 的 Secret Mix 細節

Java 會保存完整 Ingredient ItemStack，並在吃完時逐份執行：

- 食材自己的 FoodProperties
- 食材自己的效果
- 食材自己的 craft remainder
- smoking recipe 對任意食材的熟食解析
- 完整 NBT

A2.4 目前為穩定版 Bedrock 實作：

- 保存食材 **ID**，不是每份完整 ItemStack payload
- 內建常見 vanilla 生→熟映射
- 不會自動查詢任意 mod smoking recipe manager
- 尚未逐份重播任意第三方食材的 on-consume side effects / remainder
- 秘制串目前使用靜態串籤 icon，尚未做 Java generated-model 的三食材動態拼模

因此 Secret Mix 的**核心配方、作者、熟/生、營養數學與烤爐流程已可玩**，但完整第三方物品語義與動態外觀仍是待辦。

---

## 4. A2.4 新增的穿串原料

為了讓 Java 固定串配方不再引用不存在的 Grilling ID，Gameplay Core 新增：

- `beef_chunks`
- `chicken_skin`
- `chicken_wing`
- `squid_tentacle`
- `raw_sweet_potato_sheet`
- `minced_houttuynia`
- `potato_slice`
- `carrot_dice`
- `raw_mantou_slice`
- `houttuynia`

並直接導入 Java 原版 16×16 item texture。

### 重要：目前是「物品存在」，不等於完整取得鏈已移植

這批物品目前可以被命令／創造模式取得並參與穿串。

它們在 Java 中依賴的：

- 砧板加工
- 作物
- 掉落
- 世界生成
- Cookery 處理鏈

仍要在後續 A2.x 補齊。這是目前完整生存流程最大的缺口之一。

---

## 5. 與 Java Grilling 1.1.1 的剩餘差異矩陣

| 系統 | A2.4 狀態 | 差異 |
|---|---|---|
| 20 條固定串成品 | 已有 | A2.3 已有 19 raw→grilled + ordinary；A2.4 接上手工組裝 |
| 手工逐份穿串 | **A2.4 新增** | 純空氣右鍵對「無 use 行為 vanilla 物品」需實機驗收 |
| Unfinished Skewer | **A2.4 新增** | 動態食材模型未做 |
| Secret Skewer | **A2.4 新增，可玩核心** | 完整 ItemStack/NBT、任意熟食 recipe、食材 consume callback、動態拼模待補 |
| 烤爐 3 槽／進度／翻面／失敗 | 已有 | 實機 BlockEntity 壓力測試仍缺 |
| 烤爐 flat/legged/lit/unlit | 已有 | 支撐判定為 stable API 近似 |
| Oil Brush | 已有 | 已有三油工具與世界油；與 Java/Cookery 油容量仍需再校正 |
| Seasoning | 已有主要核心 | Java HUD/Mixin 級細節仍有差異 |
| Hot Food / HotUntil | 已有主要核心 | Forge Mixin/tooltip/第三方容器 hook 非 1:1 |
| 固定串逐口 3D | 已有 | 已做 A2.1/A2.2 |
| Secret 串逐口動態食材 3D | 未完成 | Java generated model 無 stable 直接等價，需要自訂幾何／render controller 方案 |
| Skewer Recipe Book 串譜 | **未完成** | Java 可記錄固定/秘制串、牆掛、木棍自動從背包扣料穿串 |
| Skewer Plate 烤串盤 | **未完成** | Java 可裝最多 5 串、方塊放置、取回、從盤中吃營養最高的一串 |
| Advanced Kitchen Rack | **未完成** | 5 調料 + 4 工具、快速選取與返還流程未做 |
| Oil Press 榨油機 | **未完成** | 4 oil cake、16 progress、砧/石加壓與 oil residue 流程未做 |
| Big Vat 大缸 | **未完成** | 榨油儲液／互動鏈未做 |
| Canola 作物 | **未完成** | 已有模型資產，但 Gameplay Core 尚未註冊生長／掉落／取得鏈 |
| Onion 作物 | **未完成** | 同上 |
| Sweet Potato 作物 | **未完成** | 同上 |
| Houttuynia 作物／自然生成 | **未完成** | A2.4 只有 item；作物與 Nether 生成未接 |
| Pepper Tree / Sichuan Pepper 世界生成 | **未完成** | 森林/村莊生成、果實葉、傷害/阻擋等未接 |
| Grilling 食材加工配方 | **未完成** | 砧板／合成／來源鏈仍缺 |
| Java Advancements | 大部分未對齊 | 需另做 Bedrock advancement/事件等價 |
| Java Sounds / action feedback | 部分 | 穿串先以原生 pop；專用聲音仍需資產／事件核對 |
| JEI / Jade / KubeJS / Create 相容 | Java-only 生態 | 不視為 Bedrock 核心玩法 1:1；應以 Bedrock 對應 UX/automation 重做 |
| Numb crosshair Mixin | stable 無安全 1:1 | A2.3 已記錄 |
| Forge LiquidType | stable 無引擎 1:1 | A2.3 已有 scripted world oil |

---

## 6. Cookery 1.5.0 依賴漂移

截至 2026-09-18，Java Kaleidoscope Cookery 正式版已從早期 1.0.x 發展到 **1.5.0**。

1.5.0 主要新增／調整：

- Teapot HUD 與自動化
- Teapot 可接收任意單物品並在無配方時製作 Mystery Tea
- Tea Seeds
- 六階段 Tea Plants
- Fresh / dried / roasted Tea Leaves 處理鏈
- Bamboo Tray 乾燥／淋濕與 hopper/piston/dispenser 自動化
- Tea Bags
- Teacup 調整
- Tea Egg
- Clay Pot Milk Tea
- Butter Tea
- Eight Immortals Table / Long Bench
- Tea Banner
- Red Lantern
- Scarecrow 調整
- Create / knife tag / KubeJS 等修正

目前 Grilling Gameplay Core 的 manifest 仍正確依賴 **Bedrock Cookery 1.0.6**，因為那是現有 Bedrock port 可用版本。

這代表：

- **Grilling 1.1.1 本身的功能可以繼續移植**
- 但所有依賴 Cookery 1.1→1.5 新物品／新方塊／新加工能力的跨模組完全一致性，必須先把 **Cookery Bedrock 從 1.0.6 往 1.5.x 補齊**
- 不應在 Grilling 內複製一套 Tea Update 來假裝 Cookery 已升級，否則 namespace、存檔相容與日後正式 Cookery port 都會衝突

因此後續應把工作拆成：
1. Grilling 1.1.1 核心完全移植
2. Cookery Bedrock 1.0.6 → Java 1.5.0 的獨立升級線
3. 最後重新做兩者整合驗收

---

## 7. A2.4 驗證

新增 CI：

`.github/workflows/gameplay-core-a24.yml`

目前驗證：

- 20 條 Java 穿串配方數量
- 牛肉串順序
- 四種魚 alternative
- 普通串配方
- Gluten 串配方
- Golden 串順序
- 非固定前綴進入 Secret Mix
- 外部 food compatibility fallback
- 非食物／未配置物品拒絕
- 3 食材硬上限
- prefix 預期長度
- raw fixed set
- 重複食材判定

A2.4 新規則測試：**13/13**。

CI 另外執行：

- `node --check`：A2.4 rules / runtime / main
- `verify_a24.py`：物品、語言、texture atlas、manifest、Cookery 依賴、Script API、20 規則與關鍵 runtime hook
- checksum-pinned 官方 bridge. Dash v1.2.0 真實編譯

第一輪 CI 已通過：

https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/35495666456

A2.3 既有 70/70 仍是前一版已驗證基準；A2.4 的新 CI 不把舊數字重複計入新測試總數。

---

## 8. 下一批實作優先順序

按照「先讓生存玩法真正閉環，再補展示/相容」：

### P0 — 生存取得鏈
1. 砧板／合成取得：beef chunks、chicken skin/wing、squid tentacle、potato/carrot/mantou/sweet-potato/houttuynia processing
2. Canola / Onion / Sweet Potato / Houttuynia crops
3. Pepper Tree / Sichuan Pepper 世界生成與掉落

### P1 — 串系統完整化
4. Skewer Recipe Book
5. Skewer Plate
6. Secret Skewer 動態三食材模型
7. Secret Skewer 完整 per-ingredient effect/remainder 語義

### P2 — 油與廚房設備
8. Oil Press
9. Big Vat
10. Advanced Kitchen Rack
11. 重新核對 Java 最新 Oil Pot 的 64-point 語義；A2.3 目前 Cookery oil pot 模擬仍是 256，需要與 Grilling 1.1.1 的相容層重新校正

### P3 — 完整驗收
12. Minecraft 26.51 客戶端
13. BDS
14. 多人同步
15. 區塊卸載／重載
16. 堆疊、丟地、箱子搬運、死亡掉落時的 Dynamic Properties
17. 性能與大量 scripted oil/crop tick 壓力測試

---

## 9. A2.4 驗收邊界

目前仍**沒有 Minecraft 26.51 客戶端／BDS 實機驗收**。

本輪尤其必測：

- 主手 vanilla 食物 + 副手木棍的純空氣右鍵是否穩定送出 itemUse
- 主手無原生 use 行為物品（例如 bone）純空氣右鍵
- 對方塊／實體右鍵穿串是否不觸發原本交互
- 副手多根木棍時只消耗 1 根
- 未完成串拆解是否完整返還
- 固定串被穿成後是否正確保留 metadata
- 秘制串放入烤爐、區塊卸載後再取出，食材／作者是否仍存在
- 熟秘制串的動態 nutrition / saturation
- 重複食材 0.8 penalty
- Hot Food + seasoning 與 secret metadata 同時存在時的合併／存檔
- multiplayer 同 tick 穿串 debounce

A2.4 的結論不是「完全移植已完成」，而是：**最核心的 Java 手工穿串 → 固定串／秘制串 → 烤爐 → 進食流程已正式開始閉環；剩餘大頭現在集中在生存取得鏈、串譜／餐盤、機器／作物／世界生成，以及 Secret Mix 的完整 ItemStack 級語義。**
