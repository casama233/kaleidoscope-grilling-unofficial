# A2.7.56 — P0 Official API Hardening

本批优先收束一个会直接影响 Cookery 菜品游戏性的稳定 API 风险，不新增玩法。

## 问题

A2.7.50 的 `applyFoodMetadata()` 原顺序是：

1. 写 Special Seasoning dynamic property
2. 写 HotFood lore / hot-until

但 Cookery 产出的菜是可堆叠 ItemStack。Microsoft 官方稳定 Script API 文档明确说明：含 custom data / properties 的 stack 不再 stackable；项目此前已经用“先写 lore，把 serving 变成 custom item，再写稳定 dynamic property”的模式规避 ItemStack 限制。

因此旧顺序存在 seasoning metadata 在 stack 仍是普通可堆叠物时被拒绝的风险。

## 修复

统一改成：

1. `setHotFood(stack, hotTicks)`
2. `setFoodSeasonings(stack, seasoning)`

HotFood 会先写 lore，再写 hot-until；之后 seasoning dynamic property 落在已经 custom/non-stackable 的 serving 上。

## 官方参考

实现前核对：

- Microsoft Learn — ItemStack / ContainerSlot：有 custom data/properties 的 item 不再 stackable。
- Microsoft Learn — Working With Events：WorldBeforeEvents 不允许直接修改 gameplay state，需要延后到可写阶段。
- Microsoft Learn — system.run guide：官方示例用 `system.run()` 把 before-event 的修改延后。
- Microsoft scripting samples 的 Container / DynamicProperties 模式继续作为项目的 API 使用参考。

## 不改架构

仍保留：

- Cookery public extension API
- 单一 Wok / Stockpot host
- `a2750_cookery_cuisine_runtime.js`
- inventory-delta output isolation
- typed oil
- HotFood
- Special Seasoning
- shared cuisine eat path

不读 `kc_station` 私有状态，也不新增 Wok / Stockpot。

## Fortress Wart Replacement 研究结论

同步核对官方 worldgen / Script API 后，仍没有 stable generated Nether Fortress bounding-box 查询。

- `/locate structure fortress` 可由命令定位，但 Script `CommandResult` 只返回 successCount，没有坐标输出。
- Feature Rule 条件按 biome / placement pass，不提供 structure bounds filter。
- `minecraft:ore_feature` 虽能只替换 Nether Wart，但全 Nether 使用会把 Bastion wart 一起替换，不等价于 Java Fortress-only。

所以本批不把 heuristic 冒充 parity。

## 验证

CI 会验证：

- 只改共享 food-state adapter
- HotFood 写入顺序严格早于 seasoning
- Wok / Stockpot 六道菜仍存在
- Cookery bridge 不读私有 host state
- A2.7.53 advancement 与 A2.7.54/55 loot overlay 保留
- 全 JS syntax
- 官方 Dash build + compiled-output comparison

仍保持：

- `minecraft_tested=false`
- `bds_tested=false`
