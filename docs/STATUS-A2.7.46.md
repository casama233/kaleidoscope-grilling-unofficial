# A2.7.46 — Advanced Rack Foundation

本批開始真正的大 gameplay parity：Advanced Kitchen Rack。

範圍刻意只做「共同底座」，不先假裝 Java Screen/Menu 已移植完成。

## Java 固定契約

Java 1.1.1：

- 9 個 compartment
- 0–4：seasoning
- 5–8：tool
- 首次存入一個空 filter 槽時，自動記住該類型
- 有物品時不能清 filter
- 前五格的 occupied 數量映射到 `spice_level 0..4`
- 油壺互相視為同類
- empty/pending/special seasoning bottle 互相視為同類
- 耐久工具按實際 item 類型匹配

## 復用而不是重造

調料分類直接引用既有契約：

- A2.7.34 Cookery Oil Pot IDs
- A2.7.43 Seasoning Bottle IDs

工具分類使用 Bedrock stable `ItemStack.getTags()/hasTag()` 對應 Java：

- `kaleidoscope_cookery:kitchen_knife`
- `kaleidoscope_cookery:kitchen_shovel`
- vanilla flint and steel

因此不維護一份金/鐵/鑽石/下界合金菜刀 ID 白名單。

## 原生 9 格容器

Advanced Rack block 使用 Bedrock 已在 Grill 上驗證過的：

`minecraft:block_entity.container.slot_count = 9`

所以 items 交給原生 block container 保存；Grilling 只保存 Java 額外的 filter metadata。

## 視覺資產

沒有重新轉模。

A1 階段已存在：

- `advanced_rack_0..4.geo.json`
- `advanced_rack.png`

A2.7.46 直接複製這些已轉好的資產到 gameplay_core。

## 本批故意不做

- Java AdvancedRackMenu / Screen
- shortcut selection GUI
- hotbar binding / swap
- depositMatching
- Automation borrow/return
- 破壞後整架帶內容打包
- 生存合成

這些全部建立在本批同一個 container/filter 核心上，後續不再新建 Rack state。

## 驗證限制

- minecraft_tested=false
- bds_tested=false
