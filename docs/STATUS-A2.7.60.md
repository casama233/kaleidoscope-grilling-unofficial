# A2.7.60 — Inventory / Dimension Advancement Parity

本批繼續使用 A2.7.53 的一次性 progression adapter，移植 Java `ModAdvancements.onPlayerTick()` 的 inventory / dimension 類 advancement。

## 本批內容

每 20 ticks 對每位玩家做一次 inventory milestone 判定：

- Human Fireworks / 人間煙火
  - 背包持有 Grill
  - task / 10 XP
- Looking the Part / 有模有樣
  - 背包持有任意 Java raw skewer
  - 復用 A2.7.56 同一 advancement spec
- Better Write It Down / 好記性不如爛筆頭
  - 持有 Skewer Recipe Book
  - task / 10 XP
- A Handful of Canola / 一把油菜籽
  - 持有 Canola Seeds
  - task / 10 XP
- Strength Makes Oil / 力大出油
  - 持有 Oil Residue
  - goal / 25 XP
- Sweet Potato / 紅苕
  - 持有 Sweet Potato
  - task / 10 XP
- Nether Taste / 地獄口味
  - 當前維度是 Nether 且持有 Houttuynia
  - goal / 25 XP

## 不新增第二個 timer

Java 每 20 ticks 跑一次。

Bedrock 主 `main.js` 已經有一個遊戲主迴圈，因此 A2.7.60 只在既有 player loop 裡加入：

`if(system.currentTick%20===0) awardInventoryAdvancements(player)`

沒有：

- 新 `system.runInterval`
- 新 world event listener
- 新 progression store

## RAW skewer 清單不重複維護

不另寫 raw-skewer ID 陣列。

runtime 直接使用：

`Object.keys(RAW_TO_COOKED)`

因此 Grill 真正認得的 raw skewer 與 advancement 使用同一來源。

## Inventory 適配

Bedrock player inventory container 不包含 offhand；Java `Inventory.contains()` 的語義更廣。

因此本批：

- 掃現有 player inventory container
- 再復用 `a2735_player_io.getOffHand()`

避免玩家把目標物放副手時漏判。

## 已有 Looking the Part 不重複

A2.7.56 已在玩家親手完成串簽時直接 award Looking the Part。

Java 同時還有「背包持有任意 raw skewer」tick fallback。

A2.7.60 只是補這個 Java fallback，仍使用同一 one-shot property；不會重複給 XP。

## 下一步

Java advancement 主要剩：

- Fireworks Feast：需要持久化記錄 29 個食物集合
- 可能需要重新掃 Java root/parent 關係與 guide/UI parity

Fortress Wart Replacement 仍維持已記錄的平台限制，不用附近方塊掃描冒充 structure bounds。

## 驗證限制

- native_java_advancement_tree=false
- native_java_toast=false
- minecraft_tested=false
- bds_tested=false
