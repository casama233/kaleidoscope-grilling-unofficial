# A2.7.45 — Advanced Rack

本批補齊 P1 的第一部分：Java Advanced Rack gameplay。

## Java 固定契約

固定 Java 1.1.1 commit `9a1acdab...`：

- 9 compartments
- 0–4：seasoning
- 5–8：tools
- persistent filter
- deposit matching
- selected-hotbar swap/binding
- 8-block shortcut range
- first five occupied slots -> spice level 0–4
- breaking preserves contents + filters
- public borrow/return automation API

## Bedrock 映射

### 放置態

使用真正的 9-slot `minecraft:block_entity.container`，因此放在 Rack 內的 ItemStack 保持原生資料。

### 破壞後內容保存

原生 `minecraft:storage_item` 的總 weight 上限為 64，不能可靠保存 Java Rack 允許的 9 個不可堆疊工具；因此沒有把 Rack 偽裝成 bundle。

A2.7.45 使用**限定 Rack 合法物品**的 codec：

- type + amount
- dynamic properties
- raw lore / custom name
- durability
- enchantments
- adventure canDestroy/canPlaceOn

用途只限「Rack block -> Rack item -> Rack block」生命週期。

### 分類

Seasoning slots：

- Cookery oil pot / oil_pot_filled（Bedrock 兩 ID 映射為 Java 同一 oil-pot category）
- empty / pending / special seasoning bottles（同一 category）

Tool slots：

- Cookery iron/gold/diamond/netherite kitchen knives
- Cookery kitchen shovel
- flint and steel
- 另外接受 Cookery kitchen-knife / kitchen-shovel item tag

### UI

使用 `@minecraft/server-ui` ActionForm：

- 9 個 compartment
- swap selected hotbar
- deposit selected hotbar
- withdraw to inventory
- clear filter when empty
- deposit matching

沒有第二份物品狀態 parser。

### Shortcut

Java Caps-Lock -> `/kgrack` 無法直接移植，因 Bedrock custom command 必須有 namespace。

對應命令：

`/kaleidoscope_grilling:rack`

搜尋同維度 8 格內最近 Rack，打開同一 Rack UI。

### Automation

導出：

- `borrowAdvancedRackItem()`
- `returnAdvancedRackItem()`

receipt 保存 dimension / position / compartment，語義對齊 Java automation API。

## 資產

直接復用 repo 已轉換的：

- advanced_rack_0~4 geometry
- advanced_rack.png

沒有重新建模。

## 實機限制

- minecraft_tested=false
- bds_tested=false
