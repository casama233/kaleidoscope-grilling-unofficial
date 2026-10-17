# A2.7.35 — Shared Player IO / 玩家手位基建收斂

本批不新增玩法，只剔除 active runtime 中完全相同的玩家手位/背包基礎操作。

## 排查結果

以下正式模組都各自重新實作：

- selected main-hand 讀取
- selected main-hand 寫入
- offhand 讀取
- offhand 寫入
- main/off hand 選擇
- 依 item id 找所在手位
- Creative 判斷

重複 consumer：

1. main.js
2. a25_plate_recipe_runtime.js
3. a26_oil_machine_runtime.js
4. a2722_cold_houttuynia_runtime.js
5. a23_oil_world.js

這些五處在基礎 I/O 層語義一致。

## A2.7.35

新增：

- a2735_player_io.js

提供：

- playerInventory
- getMainHand
- setMainHand
- getOffHand
- setOffHand
- getHand
- setHand
- findHand
- findHandEntry
- isCreative

五個 active consumer 改成 import/alias，不再自行定義 basic hand IO。

## 刻意不抽的東西

### give / inventory merge

不統一。

原因：

- main.js 使用 mergeIntoContainer，保留 Grilling 特殊堆疊規則
- plate / machine / cold 等多數使用 vanilla container.addItem
- fallback spawn 行為也不同

硬抽會改玩法語義。

### 牛肉砧板

a279_beef_board_runtime.js 暫不遷移。

它使用：

- EquipmentSlot.Mainhand
- getEquipmentSlot()
- slot.hasItem()
- slot.setItem()

這是交易驗證的一部分，不只是讀寫 convenience helper。

### 作物骨粉

a2731_farmland_crop_host_runtime.js 暫不遷移。

它需要取得 writable equipment slot，直接修改 bone meal stack。

## 效果

五個普通 consumer：

- duplicated player IO helper sets: 5 → 0
- shared player IO module: 0 → 1
- 不再各自 import EquipmentSlot / GameMode 只為 basic hand IO

牛肉砧板與骨粉作物：

- 保留 specialized writable-slot path

## 下一批基建候選

1. faceOffset / faceName / replaceable / target block helpers
2. 座標編碼 / position dynamic-property key helpers
3. CI 的 manifest version / Dash / package / publish boilerplate

仍保持：

- minecraft_tested=false
- bds_tested=false
