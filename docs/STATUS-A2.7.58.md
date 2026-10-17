# A2.7.58 — Challenge Advancement Parity

本批繼續復用 A2.7.53 的一次性 Bedrock advancement adapter，收掉 7 個已經有精確事件點的 Java advancement。

## 本批 7 個 advancement

- Mental Preparation Failed — 吃生豬兒蟲串 — challenge — 50 XP
- Metallic Taste — 搖勻含不死圖騰粉的特製調料 — goal — 25 XP
- Taste of Dragon — 搖勻含龍蛋粉的特製調料 — goal — 25 XP
- Metal Tolerance Failed — 重金屬中毒期間再次嘗試獲得 Heavy Metal — challenge — 50 XP
- The Strongest Shield — Ordinary Skewer + Invincible 挑戰中成功擋下 — challenge — 50 XP
- The Strongest Spear — 同一挑戰中未擋下 — challenge — 50 XP
- Wedding Candy for You! — 活動喜糖第一次領取 — hidden challenge — 50 XP

## 精確 Java 事件對照

固定 Java 1.1.1：

- `recordFoodFinished()` -> Mental Preparation Failed
- `PendingSeasoningItem.finishUsingItem()` -> Metallic Taste / Taste of Dragon
- `AdvancedSeasoningHandler.apply()` -> Metal Tolerance Failed
- `CursedSkewerItem.afterFoodCommitted()` -> Strongest Shield / Spear
- `WeddingCandyHandler` -> Wedding Candy

沒有新增 gameplay listener。

## Wedding Candy XP 修正

A2.7.47 為了保留 Java advancement reward，直接在每日喜糖發放時 +50 XP。

但 Java 的 50 XP 來自一次性 advancement；同一玩家即使活動期間多天領喜糖，advancement reward 只會成功一次。

A2.7.58：

- 移除 `a2747_wedding_candy_runtime.js` 的直接 `rewardExperience()`
- 改走 `awardWeddingCandy(player)`
- 第一次成功解鎖給 50 XP
- 後續活動日仍可按 Java 規則領喜糖，但不再重複給 50 XP

## 共用 adapter UI 修正

A2.7.53 原 adapter 對所有 frame 都顯示 Goal 文案。

本批不另造 UI，而是讓同一 adapter 根據 `spec.frame` 使用：

- task
- goal
- challenge

三組翻譯訊息。

既有 A2.7.53 / A2.7.56 成就也因此得到正確 frame 提示。

## Ordinary Skewer

沿用現有 Bedrock Invincible / Ordinary Skewer 邏輯：

- challenged=false -> 正常詛咒死亡，不解鎖 Shield/Spear
- challenged=true + 50% block -> Strongest Shield
- challenged=true + 未 block -> Strongest Spear，再執行原死亡流程

判定抽成 pure `ordinaryChallengeOutcome()`，讓遊戲行為與成就使用同一個 50/50 結果，不各抽一次 RNG。

## 不重複造輪子

- progression store：A2.7.53
- XP：A2.7.53
- announcement：A2.7.53
- persistent completion：A2.7.53
- Wedding Candy interval：A2.7.47 原有
- Heavy Metal / Dragon / Invincible gameplay：現有 main.js

新增 listener = 0
新增 interval = 0

## 仍未處理

- Fireworks Feast：需要持久化記錄完整食物集合
- inventory/dimension 型 advancement：
  - Human Fireworks
  - Better Write It Down
  - A Handful of Canola
  - Strength Makes Oil
  - Sweet Potato
  - Nether Taste

Fortress Wart replacement 仍維持 A2.7.56 記錄的平台限制，不使用玩家附近掃描冒充 structure bounding-box parity。

## 驗證限制

- native_java_advancement_tree=false
- native_java_toast=false
- minecraft_tested=false
- bds_tested=false
