# A2.7.40 — Grill HUD Provider

本批只擴充 A2.7.39 的共享準星 HUD，不建立第二個輪詢器。

## Java 對照

固定 Java 1.1.1：

- `MachineHud.java` blob `2156ed061b5843618d6929ba5e5aa92aff0688a5`
- `GrillProvider.java` blob `01eff3e5fbba33d3303536df2633771c2dc15baa`
- `GrillBlockEntity.java` blob `6f12af87af8837dc2fec034efd6076bea49637bc`

Machine HUD 的 Grill 資訊：

- title
- phase timer：phase 0~2 為 800 ticks；phase 3 為 400 ticks
- flips：0/4
- seasoning added / none
- phase 2 + seasoned 時 ready-to-take

Jade 還提供狀態：

- need heat
- empty
- need oil
- flipping
- need flip
- need seasoning
- ready
- burning

Bedrock A2.7.40 把兩組資訊收進同一個 provider。

## 不重複讀 Grill state

新增：

`a2740_grill_state_adapter.js`

它成為 persisted Grill state 的 read adapter：

- canonical grill state key
- `readGrillState()`
- `occupiedGrillSlots()`

主 `main.js` 也改為引用這個 adapter，因此 HUD 不再複製：

- dynamic-property key 演算法
- JSON state read
- inventory occupied 計算

write/clear 仍由主 runtime 負責，但 key 也改引用 adapter 的 `grillStateKey`。

## 翻面常量收束

`core_logic.js` 新增：

`REQUIRED_FLIPS=4`

原本的：

- valid-state upper bound
- phase 1 -> phase 2 threshold

都改引用同一常量。HUD 同樣引用這個值，不再新增第三份硬編 `4`。

## HUD 刷新策略

Java 是獨立 GUI panel，可以每 frame 更新。

Bedrock 目前用 actionbar；若照 Java 每 tick 顯示 timer，會不停覆蓋互動提示。

因此：

- 狀態、翻面次數、flip cooldown 狀態、調料狀態：立即刷新
- timer：每 20 ticks（1 秒）取樣一次
- A2.7.39 全域準星輪詢仍維持 4 ticks
- 不新增任何 provider 專屬 `system.runInterval`

## 本地化

使用 Java 對應翻譯鍵並補：

- en_US
- zh_CN
- zh_TW

## 未做

本批不接：

- Oil Press
- Big Vat
- Seasoning Bottle

它們之後直接註冊至 A2.7.39 provider registry。

仍不宣稱真機驗證：

- `minecraft_tested=false`
- `bds_tested=false`
