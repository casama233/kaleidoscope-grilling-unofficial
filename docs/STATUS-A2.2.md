# A2.2.0 — 逐口 3D、四瓶調料堆疊與 Numb 動作

A2.2 建立在 A2.1 的真三槽烤爐、Cookery 油壺、調料資料與煙火氣系統之上，這一輪主要收斂「真正拿在手上吃」的視覺同步與調料瓶物理形態。

基準：
- Java Grilling 1.1.1：`breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c`
- Cookery 依賴：Bedrock 1.0.6
- Bedrock retail：26.51 / content 1.26.50
- Script API：穩定版 `@minecraft/server 2.9.0`
- 不要求實驗開關

## 正式逐口 3D 串

39 個正式串 attachable 現在不再只顯示完整模型：

- 19 生固定串
- 19 熟固定串
- 普通串

每一種 attachable 會直接讀：

`query.is_using_item`

和：

`query.item_in_use_duration`

並在自身 render controller 裡切換 stage geometry / texture，不替換玩家手上的真正食物 ItemStack，因此不會打斷原生 use、25 tick 提前結算、Hot Food、調料資料或主／副手狀態。

本輪實際生成：

- **39 個 bite-stage attachable**
- **150 個真正不同的階段幾何檔**
- **150 張對應階段貼圖**
- 39 個完整態 + 111 個咬後態

Render Controller 固定提供 stage0–4 五個槽；不足四口的串只把最後一個真實咬後模型重用到後續槽，不把這些重用算成新模型。

例如牛肉串的實際 Molang：

```
q.item_in_use_duration >= 4.08333 → stage4
>= 3.45833 → stage3
>= 2.33333 → stage2
>= 0.95833 → stage1
否則 stage0
```

最後一輪 CI 額外硬驗證「最高咬口時間必須命中最高 stage」，避免條件巢狀順序導致高時間錯回早期模型。

## 六種進食規則同步

模型、玩家骨骼、聲音與粒子都沿用 A1.16 / Java 的原始咬點資料：

- ONE：1.16667、3.08333 秒
- TWO：0.95833、4.00000 秒
- THREE：0.95833、2.33333、3.54167 秒
- THREE_ALT：0.95833、2.16667、3.50000 秒
- FOUR：0.95833、2.33333、3.45833、4.08333 秒

每次真正跨過一個咬點時：

- 發出 5 個 `kaleidoscope_grilling:skewer_crumb` 食物碎屑粒子
- 播放一次輕量咀嚼聲
- attachable 同時進入下一個咬後模型
- 整段進食播放原作對應 profile 音軌：
  - ONE → one_skewer_eat
  - TWO → two_skewer_eat
  - THREE / THREE_ALT → three_skewer_eat
  - FOUR → four_skewer_eat
- 取消或完成時停止對應音軌

### THREE_RANDOM 修正

A2.1 有一個時序差異：THREE_RANDOM 物品的原生 Bedrock use duration 固定為 4.5 秒，但 Java 實際可能隨機到 5 秒 THREE。

A2.2 修正為：

- THREE_RANDOM 物品原生窗口固定 **5.0 秒**
- 隨機到 THREE → 正常在100 ticks完成
- 隨機到 THREE_ALT → 腳本在90 ticks準確提前結算並停止動畫／聲音
- 實際玩家骨骼、結算、聲音、粒子都使用一次決定的真實 branch

Attachable Molang 無法讀到服務端選出的 THREE / THREE_ALT branch，因此只有**3D模型階段**使用兩條時間線的中點：
- 0.95833
- 2.25000
- 3.52084

最大視覺階段偏差約 **1.67 ticks**。這個限制已明列，沒有把它稱為完全一比一。

## Numb 肢體動作

Java Numb 的走路異常擺臂／擺腿已轉成 Bedrock 玩家動畫：

- 依 `query.modified_move_speed` 決定幅度
- 依 `query.life_time` 形成連續波形
- 效果存在時短窗口循環刷新
- 吃串時不覆蓋進食動作
- 效果結束後回到 reset

Java 的第一人稱準星繞圈是 GUI Mixin。Bedrock 26.51 穩定 Script API 沒有安全的原生 HUD crosshair offset API，因此 **A2.2 不偽造準星位移**；這仍是明確差異。

## 四瓶調料物理堆疊

A2.1 的同一方塊只顯示1瓶。A2.2 現在正式使用四個無實驗 block identifier：

- `seasoning_bottle_1`
- `seasoning_bottle_2`
- `seasoning_bottle_3`
- `seasoning_bottle_4`

分別使用之前已轉換的原作1–4瓶布局幾何。

每一瓶各自保存：

```
kind
ingredients[]
uses
variant
```

所以可以出現例如：

1. 空瓶
2. Pending，內有自己的配料
3. Special，已用5次、variant 6
4. 另一個空瓶

空手會取最上層一瓶；取下後方塊外觀由4瓶變3瓶。Special 被取下時自己的 ingredients / uses / variant 不會跟其他瓶混在一起。破壞整個瓶組則逐瓶掉出各自完整資料。

為保持 **26.51 retail / 無實驗**，這裡刻意沒有使用自定義 block states；四種外觀用四個 block identifier 切換。

## 三種油型資料契約

A2.2 正式定義：

| 油型 | Hot Food 時長 |
|---|---:|
| canola | 1200 ticks |
| secret_chili | 12000 ticks |
| premium_chili | 24000 ticks |

Cookery `oil_pot_filled` 仍直接使用 `kc_oil_count` 作容量；可選的 Grilling `oil_type` 決定熱度類型。

### 為什麼這版沒有宣稱「真自訂流體」

Bedrock 26.51 stable 的公開 Script / block API 沒有可供 Add-On 註冊任意新 FluidType 的穩定接口；現有 liquid detection 也不是 Java Forge Fluid 的等價系統。

因此 A2.2 做的是**正式油型／容器資料契約**，不是假的「自訂流體方塊」。菜籽油、辣椒油、熔岩辣椒油真正世界流體仍保持未完成狀態。

## 驗證

最終成功 CI：

https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/35490679938

回歸／行為：

- A2.0 Java 烤爐狀態機：**16 / 16**
- A2.1 seasoning state：**4 / 4**
- A2.1 runtime：**18 / 18**
- A2.2 runtime：**12 / 12**
- 合計：**50 / 50**

A2.2 runtime 實際覆蓋：

- 4瓶外觀
- 4瓶獨立資料
- 取頂瓶後回到3瓶
- Special uses / variant 保留
- secret chili → 12000 tick heat
- FOUR 原作音軌啟動
- 第一口前不出粒子
- 第一口精確出5粒
- FOUR全4口共20粒
- 取消進食停止正確音軌
- THREE_RANDOM → THREE_ALT 在90 ticks完成
- Numb 肢體動畫刷新

結構：

- 正式物品：**53**
- 正式 food：**41**
- bite-stage attachable：**39**
- 真實 bite-stage geometry：**150**
- 調料瓶物理堆疊：**4**
- 正式油型契約：**3**
- 真自訂流體：**未實作**

官方 bridge. Dash v1.2.0：

- 實際編譯：**570 files**
- BP：**65** 個來源檔逐檔一致
- RP：**505** 個來源檔逐檔一致

最終輸出 SHA-256：

- `Kaleidoscope_Grilling_A2.2_Gameplay_Core.mcaddon`
  `e90670e1bd84d41259406b3497577a756ca6554d8898dac1699bda20a9787fa6`
- `Kaleidoscope_Grilling_A2.2_Gameplay_Core.brproject`
  `ea5033c0e19f04980132bbe6d1e678f383cfad6515ed5535ba72006f4c2b036c`

## 下一個主線缺口

A2.2 後，固定串「烤→調味→趁熱→逐口吃」的核心表現已經接近完整。下一階段應優先進：

1. **自由／秘制串**：木棍＋1–3食材、順序／OR材料、固定串匹配、Secret Skewer、拆串。
2. **餐盤**：最多5串，各自 ItemStack / Hot Food / seasoning 資料保留。
3. **串譜／指南玩家記錄**：固定串＋秘制串記錄，並跟既有 Cookery 單一指南入口及搜尋／收藏／自訂資料核心接線。
4. **榨油機＋大缸＋油餅流程**，使用已完成的靜態模型資產。
5. **作物與世界生成**：油菜、魚腥草、花椒、洋蔥、紅薯。
6. Minecraft 26.51 客戶端／BDS 真實驗收及多人競爭、區塊卸載、重進世界測試。

A2.2 目前通過的是鎖定來源、Node 模擬 Script API 宿主、結構檢查和真正 Dash 編譯。**仍沒有宣稱 Minecraft/BDS 實機驗收完成。**
