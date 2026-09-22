# A2.7.60 — Pepper Worldgen BDS Fix

本批不新增玩法，只把已经在实际 BDS 服务器版验证过的 Pepper Tree worldgen schema 修正提升到正式 Gameplay Core。

## 问题

A2.7.59 的正式源包：

`behavior_pack/features/pepper_tree_worldgen.json`

使用：

```json
"trunk_lean": {
  "allow_diagonal_growth": false
}
```

实际 BDS 1.26.51.1 Content Log 已证明该 `acacia_trunk.trunk_lean` 缺少：

- `lean_height`
- `lean_steps`

会导致整棵 tree feature 注册失败，随后 feature rule 报：

`No definition found for feature 'kaleidoscope_grilling:pepper_tree_worldgen'`

结果是 Pepper Tree 根本不会自然生成。

A2.7.59 后续的服务器专用打包脚本已经临时补了这两个字段，并在隔离 BDS / 正式服得到 0 ERROR，但普通 gameplay_core / mcaddon 源包本身仍未修。

## A2.7.60 修正

正式 feature 改为：

```json
"trunk_lean": {
  "allow_diagonal_growth": false,
  "lean_height": {
    "base": 1,
    "intervals": [1],
    "min_height_for_canopy": 2
  },
  "lean_steps": {
    "base": 1,
    "intervals": [1]
  }
}
```

与已经通过 BDS 的 server-edition shim 使用相同值。

A2.7.60 之后，server-edition 的这条补丁会自然变成 no-op 防护，不再承担“只有服务器版才修世界生成”的职责。

## Mojang 官方案例

固定：

`Mojang/bedrock-samples@46ba6ea985fb5a92d79a9419198f10dda14c199d`

文件：

`documentation/Features.html`

Git blob：

`dfb66d2371e818bea6bfffb1c1785d956a76b6d6`

官方 `minecraft:tree_feature` 的 `acacia_trunk.trunk_lean` 示例明确包含：

- `allow_diagonal_growth`
- `lean_height`
- `lean_steps`

同一官方示例的 canopy 也使用 3:1 weighted leaf IDs；A2.7.59 的 25% 初始结果叶方案因此保持不动。

## 不改的内容

本批不动：

- Pepper Tree 3:1 normal / fruiting bridge 权重
- 25% Java 初始结果概率
- one-shot fruiting bridge canonicalization
- A2.7.48 Pepper lifecycle
- A2.7.53 Pepper advancement
- A2.7.54 village Pepper/Sapling loot
- Advanced Rack
- A2.7.56/A2.7.58 advancement runtime
- A2.7.57 Cookery metadata hardening

新增 listener = 0。
新增 interval = 0。

## 验证

CI 会执行：

- A2.7.59 published baseline verifier
- pinned Mojang tree-feature contract
- 已有 BDS server-shim evidence contract
- corrected feature byte-for-byte check
- `lean_height` / `lean_steps` exact schema
- 3:1 leaf weights regression
- Pepper lifecycle / Rack / advancement / Cookery regression
- 全部 JavaScript syntax
- checksum-pinned Dash build
- compiled output逐文件 compare
- mcaddon / brproject checksum + zip integrity

## 测试边界

这次新的 canonical mcaddon 仍会如实标记：

- `minecraft_tested=false`
- `bds_tested=false`

因为 A2.7.60 新产物本身还没有重新送进 BDS 实机。

但**完全相同的 trunk_lean 修正**已经由 server-edition shim 在 BDS 1.26.51.1 验证并获得 0 ERROR，所以报告另记：

- `prior_server_shim_bds_tested=true`
