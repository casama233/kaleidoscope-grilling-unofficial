# A2.7.39 — Shared Crosshair HUD

本批把 Java typed oil-pot HUD 以 Bedrock 可維護的方式接回來，但不為油壺單獨建立輪詢系統。

## Java 對照

Java 1.1.1 的 `OilPotHud`：

- 準星指向 Cookery oil pot block entity 時顯示；
- 顯示油種/油脂、目前數量、容量、剩餘容量；
- typed oil 容量 64；
- Cookery fat 容量 256；
- UI 每幀可跟隨狀態更新。

A2.7.38 已固定：

`OilPotHud.java` blob
`40c6f7e19c50d3081a16c8c93b3cfc06f0db532d`

## Bedrock 實作

新增一個共用 HUD runtime：

`a2739_crosshair_hud_runtime.js`

它只做一次全域輪詢：

1. 每 4 ticks 掃描玩家；
2. `getBlockFromViewDirection(maxDistance=6)` 取得準星方塊；
3. 依 priority 詢問已註冊 provider；
4. provider 回傳 `signature + RawMessage`；
5. signature 沒變就不重寫 actionbar。

因此每個機器不需要自己建立 `system.runInterval`。

「signature 沒變就不重寫」也避免 HUD 持續蓋掉互動錯誤提示；油量成功改變時 signature 才更新。

## Cookery oil-pot block adapter

新增：

`a2739_cookery_oil_pot_block_adapter.js`

把已放置 Cookery oil pot 的：

- type
- count
- capacity
- remaining
- dynamic-property read/write/clear
- `kaleidoscope_cookery:has_oil` state 同步

集中在一處。

A2.7.36 的：

- 放置恢復
- typed oil 填充
- 玩家破壞
- 爆炸掉落

也改走這個 adapter。

新的 HUD provider 不直接碰：

- `kc_oilpot:...`
- A2.7.36 typed-oil world property
- Cookery `has_oil` 寫入

## 第一個 provider：Cookery Oil Pot

`a2739_oil_pot_hud_provider.js`

覆蓋 Java 的四種狀態：

- empty
- native Cookery fat
- canola
- secret_chili
- premium_chili

顯示內容使用 Resource Pack 翻譯鍵，不硬編單一語言。

已補：

- en_US
- zh_CN
- zh_TW

## API 邊界

manifest 仍固定 `@minecraft/server 2.9.0`。

A2.7.39 使用的 Bedrock API：

- `Entity.getBlockFromViewDirection`
- `BlockRaycastOptions.maxDistance`
- `ScreenDisplay.setActionBar(RawMessage)`

不新增 server-ui 依賴。

## 未做

這一批只接 oil pot provider。

下一批可以直接在相同 HUD runtime 上加入：

- Grill
- Oil Press
- Big Vat
- Seasoning Bottle

不再新增第二個輪詢器。

仍不宣稱真機驗證：

- `minecraft_tested=false`
- `bds_tested=false`
