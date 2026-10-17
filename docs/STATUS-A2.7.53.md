# A2.7.53 — Mountain Fragrance Advancement

本批只補 Java 原版 Pepper Tree 採摘成就：

`mountain_fragrance` / 「山野麻香」。

不把 Village chest acquisition 混進同一批，避免因 Bedrock 沒有 Java LootTableLoadEvent 等價 append API 而把 vanilla village loot table 整張複製進 Grilling。

## Java 1.1.1 固定契約

固定上游 commit：

`breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c`

固定來源：

- `ModAdvancements.java` blob `2791f158caf5885946d377da0b2a3686dcc89146`
- `PepperLeavesBlock.java` blob `886ddfc434d38f3df6c440b8ea16c5b7b9569af4`
- `advancement/mountain_fragrance.json` blob `bf1cdf32fbba604779f7204ba6d63661c1696ac7`

Java 行為：

- 只在空手摘取 `HAS_PEPPER=true` 的 Pepper Leaves 時觸發
- 掉落 1–2 花椒後呼叫 `ModAdvancements.pepperPicked(player)`
- 對應 advancement：`mountain_fragrance`
- parent：`human_fireworks`
- frame：`goal`
- show toast：true
- announce to chat：true
- hidden：false
- reward：25 XP

## Bedrock 實作：共用一次性 Advancement Adapter

新增：

- `a2753_advancement_core.js`
- `a2753_advancement_runtime.js`

不是為花椒寫一個一次性特例，而是建立可繼續復用的：

`awardOneShotAdvancement(player, spec)`

共用能力：

- player dynamic property 一次性解鎖
- XP reward
- 全服公告
- 本地 goal 訊息
- translation key
- stable per-advancement key

Mountain Fragrance 使用：

`kaleidoscope_grilling:adv_mountain_fragrance`

作為一次性 player state。

## 不新增輪詢 / 事件訂閱

A2.7.48 已經有 Pepper Leaves custom component：

`onPlayerInteract`

本批只在既有摘取流程：

1. 生成 1–2 花椒
2. award Mountain Fragrance
3. 清除 `has_pepper`
4. 播放採摘音效

中插入一次 `awardMountainFragrance(player)`。

沒有：

- 新 `runInterval`
- 新 world event listener
- 新 player interact listener
- 在 breakLeaves 掉落路徑錯誤解鎖

因此剪刀/Silk Touch/破壞葉片掉出的花椒不會觸發此成就，對齊 Java `useWithoutItem`。

## UI 平台邊界

Bedrock 沒有 Java advancement tree / frame / toast 的同級 addon API。

因此本批：

- 保留 goal metadata
- 保留原版 title / description
- 保留一次性
- 保留 25 XP
- 保留 announce-to-chat
- 額外給達成玩家一條 localized goal 訊息
- 不偽造 Java advancement tree
- 不宣稱 native Java toast 1:1

狀態報告明確：

- `native_java_advancement_tree=false`
- `native_java_toast=false`

## 下一批

Village chest acquisition 仍缺：

- 所有 `minecraft:chests/village/*`
- 40%：Sichuan Pepper × 3–10
- 20%：Pepper Sapling × 1

Bedrock 官方 LootTable API 可讀/生成 loot，但沒有 Java `LootTableLoadEvent.addPool()` 同級 append hook；下一批應優先研究「不覆蓋整張 vanilla village loot table」的安全實作，而不是直接複製所有 vanilla 表。

## 驗證限制

- `minecraft_tested=false`
- `bds_tested=false`
- pinned Java contract / pure core / structure / JS syntax / Dash compile / compiled-output comparison 由 CI 驗證
