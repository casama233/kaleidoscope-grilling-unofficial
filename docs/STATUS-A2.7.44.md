# A2.7.44 — Skewer Plate HUD Provider

本批把 Skewer Plate 的 Java Jade 資訊接入 A2.7.39 共用準星 HUD，不新增輪詢器，也不重做 A2.5 的盤子狀態。

## Java 對照

固定 Java 1.1.1 / commit `9a1acdab27698457bec16c9362678e574895a28c`：

- `SkewerPlateProvider.java` blob `e230917adb32d8ae5d8b0837350ddb5bef7f4c98`
- `SkewerPlateBlockEntity.java` blob `b50903f3dcd6069d5b5b13133abc0d52eaf66dfd`

Java Jade 顯示：

- 已放置烤串 `x/5`
- 空盤：手持烤串加入
- 非空盤：空手取回最後放入的烤串
- 非空盤：破壞後整盤打包攜帶
- Java Jade 還會用 item elements 顯示盤中烤串圖示

## Bedrock 實作

A2.5 已經有：

- `PLATE_CAPACITY=5`
- `normalizePlateRows()`
- `readPlateBlock()`
- 加入 / 取回 / 打包邏輯

A2.7.44 不複製它們，只在同一 runtime 暴露：

`a25ReadPlateBlock(block)`

新的 provider 直接使用：

- `PLATE_BLOCK_ID`
- `a25ReadPlateBlock()`
- `PLATE_CAPACITY`
- `normalizePlateRows()`
- A2.7.39 共用 crosshair HUD registry

因此沒有第二套：

- plate dynamic-property key
- JSON parser
- 容量常量
- `system.runInterval`
- raycast

## UI 邊界

Java Jade 可以顯示實際 item icons。

Bedrock 目前共享 HUD 使用 actionbar RawMessage，沒有 Jade element 等價層；本批移植文字狀態與完整內容 signature。即使數量不變，只要盤內烤串內容改變，signature 仍會刷新。

不建立假的 item-icon API。

## 下一步

Skewer Recipe wall block 也已有 Java Jade provider，而且 A2.5 已保存 recipe block state；下一批可以同樣復用現有 recipe state reader，而不是另做 recipe storage。

## 驗證限制

- `minecraft_tested=false`
- `bds_tested=false`
