# A2.7.42 — Big Vat HUD Provider

本批把 Big Vat 接到 A2.7.39 的共享準星 HUD，不增加第二個輪詢器，也不重做 A2.6 的大缸狀態。

## Java 對照

固定 Java 1.1.1 / commit `9a1acdab27698457bec16c9362678e574895a28c`：

- `MachineHud.java` blob `2156ed061b5843618d6929ba5e5aa92aff0688a5`
- `BigVatBlockEntity.java` blob `66f372ba808a9373d06f6cf4e7246f4911139689`

Java Machine HUD 顯示：

- Big Vat 標題
- 內容物名稱
- 容量
- 「單一流體、不可混裝」提示

Java Big Vat 容量固定為 8 桶。

## Bedrock 實作

A2.7.42 新增：

- `a2742_big_vat_hud_core.js`
- `a2742_big_vat_hud_provider.js`

provider 直接復用：

`a26ReadVat(block)`

也就是 HUD 沒有自己：

- 讀 dynamic property
- parse Big Vat JSON
- 算容量
- 建 `system.runInterval`

仍由 A2.7.39 的單一準星 HUD runtime 統一輪詢。

## 顯示的真實 Bedrock 流體

目前 A2.6 `VAT_TYPES` 實際支援：

- water
- lava
- canola
- secret_chili
- premium_chili

A2.7.42 為這五種狀態提供本地化內容名稱，另有 empty 狀態。

## Java / Bedrock parity 邊界

Java 的 Big Vat 背後是標準 `FluidTank` / `IFluidHandler`，因此可接受額外已註冊流體。

Bedrock A2.6 目前沒有等價的通用流體能力層；它只實作上面五種 `VAT_TYPES`。

本批 HUD 嚴格顯示 Bedrock 真實能力，不建立假的通用 fluid API，也不把這個差異標成已完成。

## 順手收束 A2.7.40 Grill ready 契約

A2.7.40 玩家看到的 ready-to-take 文案本身正確，但內部狀態直接用了 Machine HUD 的 `message.kaleidoscope_grilling.grill_ready_to_take`，沒有保留 Java Jade 的 `jade.kaleidoscope_grilling.grill.ready`。

A2.7.42 將兩者分開：

- `grillHudStatusKey()` 返回 Java Jade 的 `jade...grill.ready`；
- actionbar 顯示時再映射到 Java Machine HUD 的 `grill_ready_to_take` 文案；
- en_US / zh_CN / zh_TW 補齊 `jade...grill.ready`。

這不新增另一套 Grill HUD，只修正既有 provider 的語義層。

## 下一步

共享 HUD 目前已有：

- typed Cookery Oil Pot
- Grill
- Oil Press
- Big Vat

下一個適合的小批是 Seasoning Bottle HUD，Java 已有 Jade/tooltip/HUD 對應資料，並且 Bedrock 主程式目前已經保存調料 ingredients / uses / variant。

仍不宣稱真機驗證：

- `minecraft_tested=false`
- `bds_tested=false`
