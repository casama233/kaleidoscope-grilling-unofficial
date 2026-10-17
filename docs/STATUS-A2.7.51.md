# A2.7.51 — Pepper Forest Worldgen

本批只補 Java Pepper Tree 的森林自然生成，不改 A2.7.48 已驗證的 Pepper Tree lifecycle runtime。

## Java 固定契約

Java 1.1.1：

- biome：`#minecraft:is_forest`
- rarity：每 chunk 1/16
- in-square placement
- water depth = 0
- surface heightmap
- vegetal decoration pass

## Bedrock 映射

使用原生資料驅動 worldgen：

- `minecraft:tree_feature`
- `minecraft:feature_rules`
- biome filter：`has_biome_tag == forest`
- `scatter_chance = 1/16`
- x/z 在 chunk 內 `0..15`
- y 使用 `query.heightmap(variable.worldx, variable.worldz)`
- `surface_pass`

不新增 Script API worldgen listener，也沒有 chunk/player 掃描器。

## 樹形

Bedrock tree feature 使用：

- trunk base 2 + interval 1 → Java 的 2–3 高度
- Pepper Log
- radius 1、height 3 的小型 random-spread canopy
- Pepper Leaves

A2.7.48 的 Pepper Leaves lifecycle 仍負責後續結果 / 採收 / decay。

### 明確差異

Java custom feature 會讓新生成葉片約 25% 直接帶花椒。

Bedrock stable `random_spread_canopy.leaf_blocks` 不提供同一 custom block 的 state-weighted leaf permutation，因此自然生成先使用未結果 Pepper Leaves；它們隨後仍按 A2.7.48 的 Java 1/20 random-tick 規則結果。

這個差異不靠新增第二個 `pepper_leaves_fruiting` 方塊硬補，避免重複狀態系統。

## 下一批

- Village chest acquisition：40% 花椒 3–10、20% Pepper Sapling
- `pepperPicked` advancement / Bedrock 對應
- 核對剩餘世界取得鏈

## 驗證限制

- minecraft_tested=false
- bds_tested=false
