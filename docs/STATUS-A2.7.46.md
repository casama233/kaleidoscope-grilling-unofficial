# A2.7.46 — Wedding Candy

本批回到「Java 原版仍有、Bedrock 主幹尚未存在」的實際內容缺口，移植 `wedding_candy`（喜糖），不碰已有併發分支正在做的 Advanced Rack / Cookery host 工作。

## Java 1.1.1 固定契約

固定上游 commit：`9a1acdab27698457bec16c9362678e574895a28c`。

- `ModItems.java` blob `6f190e03dc1b7c54bbbae1d5d49d35c78c19b63a`
- `WeddingCandyItem.java` blob `5c1037e0c9e97583eaa8ef852327b0c4e3d2f914`
- `WeddingCandyHandler.java` blob `310f5bd4d49bd2bbd6fbada87a51677ef7d4636a`
- `advancement/wedding_candy.json` blob `22f03c57420d1038767d53830eeca974fea70cec`
- `wedding_candy.png` blob `d7ca9f5dfa61d6658372d8e181283fb5bf756d78`

原版行為：

- nutrition `20`
- saturation modifier `0.5`
- `alwaysEdible`
- 吃完獲得 `invincible` 15 秒（300 ticks）
- 活動時區：`Asia/Shanghai`
- 活動日期：2026-09-01 ～ 2026-09-12
- 當日累計在線 `日期 × 60` 秒後，發放 `日期` 顆喜糖
- 當日只領一次
- Java 隱藏 advancement 同時給 50 XP

## Bedrock 實作

### 1. 物品

新增 `kaleidoscope_grilling:wedding_candy`：

- 64 堆疊
- nutrition 20
- saturation modifier 0.5
- `can_always_eat=true`
- 使用 Java 原圖，增補流程用 pinned git blob 驗證後下載
- 加入既有 `item_texture.json` 與 Grilling item catalog

### 2. Invincible 不另造效果 listener

A2.7.32 已把獨立食物效果收進：

`a2732_standalone_food_effect_runtime.js`

而 `main.js` 已經有 `invincible` 的實際受傷取消邏輯。

因此 A2.7.46 只向既有 effect table 增加：

`wedding_candy -> persistent_fx(invincible, 300 ticks)`

不新增第二個 `itemCompleteUse` listener。

### 3. 婚禮活動取得鏈

新增一個每 20 ticks 執行一次的活動 runtime，按照 Java 原版：

- 用 UTC+8 算上海日曆，不依賴伺服器本地時區
- 僅在 2026-09-01 ～ 09-12 生效
- 每秒累計在線時間
- 跨日重置當日進度
- 達成 `day × 60` 秒時發放 `day` 顆
- player dynamic property 保存 tracking / seconds / claimed date
- 同時給 50 XP，保留 Java advancement 的 gameplay reward

目前日期已經晚於 Java 原活動窗口；這是原版契約本身的結果，不把活動日期偷偷延長。

## 平台邊界

Java 的兩行 hover tooltip 與隱藏 advancement toast 沒有在本批偽造一套 Java UI：

- tooltip 翻譯 key/value 保留\n- 50 XP gameplay reward 保留\n- `advancement_ui=false`\n- `intrinsic_java_hover_tooltip=false`\n\n## 這一批後仍確認缺的 Java 食品 ID\n\n主幹在本批前靜態搜尋仍不存在：\n\n- `sugared_tomato`（已有其他工作分支）\n- `pepper_honey`（已有其他工作分支）\n- `houtttuynia_stir_fried_pork`
- `green_pepper_squid_tentacles`
- `braised_chicken_wings`
- `potato_beef_stew`
- `red_sweet_potato_porridge`
- `sour_spicy_noodles`

本批完成後 `wedding_candy` 從這份缺口中移除。

## 驗證限制

- `minecraft_tested=false`
- `bds_tested=false`
- 結構、純 core、JS syntax、pinned Java contract、Dash build 與編譯輸出一致性由 CI 驗證
