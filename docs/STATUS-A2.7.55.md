# A2.7.55 — Fortress Houttuynia Loot

本批補 Java `FortressHouttuyniaHandler`，讓折耳根除了堡壘內作物之外，也能從 Nether Fortress 寶箱取得。

## Java 固定契約

固定上游：

`breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c`

`FortressHouttuyniaHandler.java` blob：

`27af759e8f807e0f21dc887ca53594a596de72c1`

Java 只對：

`minecraft:chests/nether_bridge`

追加一個 pool：

- pool chance：65%
- rolls：1–2
- 每次 roll：Houttuynia × 1–3

也就是命中 65% 後，可能生成 1 或 2 個獨立折耳根 stack，每 stack 1–3 個。

## 復用 A2.7.54 Loot Wrapper 架構

不新增 chest-open Script runtime。

固定 Mojang 官方 Bedrock 樣本：

- `Mojang/bedrock-samples@46ba6ea985fb5a92d79a9419198f10dda14c199d`
- version `1.26.50.4`
- `behavior_pack/loot_tables/chests/nether_bridge.json`
- Git blob `071c1feeaccec0f2e9ee39074d76c5862681aa3c`

A2.7.55：

1. byte-for-byte 保存官方 `nether_bridge.json` 到：
   `loot_tables/kaleidoscope_grilling/vanilla/chests/nether_bridge.json`
2. 在 vanilla 路徑放薄 wrapper。
3. wrapper 第一 pool 引用官方 snapshot。
4. wrapper 第二 pool 引用：
   `loot_tables/kaleidoscope_grilling/fortress_houttuynia_bonus.json`
5. bonus table 精確保存 Java 的 65% / rolls 1–2 / count 1–3。

## 不重複造輪子

- 沿用 A2.7.54 已驗證的「vanilla snapshot + wrapper + bonus table」策略。
- 不掃玩家。
- 不掃堡壘。
- 不在開箱時猜測 structure。
- 不新增 tick/listener。
- 不改 Houttuynia Crop runtime。

## 兼容邊界

與 A2.7.54 相同，Bedrock 沒有 Java `LootTableLoadEvent.addPool()`。

因此必須覆蓋 vanilla `loot_tables/chests/nether_bridge.json` 路徑：

- `vanilla_loot_table_override=true`
- `loot_override_compatibility_risk=true`

若其他 Behavior Pack 也覆蓋 Nether Bridge chest table，pack priority 仍可能造成衝突；這是平台限制，不偽裝成已解決。

## 下一批

Java 生存取得仍有另一半：

`FortressWartReplacementHandler`

它會在 Nether Fortress bounding box 內，把約 25% Nether Wart 依 deterministic coordinate hash 替換成 Houttuynia Crop，並保留對應 age。

這一塊牽涉 structure/chunk 掃描，單獨做下一批，不和 loot overlay 混在一起。

## 驗證限制

- `minecraft_tested=false`
- `bds_tested=false`
- pinned Java handler / Mojang vanilla blob / wrapper / bonus / Dash build / compiled-output comparison 由 CI 驗證
