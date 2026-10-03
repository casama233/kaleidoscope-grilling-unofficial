# Grilling 2.8.60: pepper tree world generation

Review candidate. No merge, public release or live deployment is implied.

## Reproduced native defect
In BDS 1.26.52.3, 24 placements of the former exact feature succeeded but produced two logs and zero leaves, even with random ticks disabled. Manually placed leaves had valid resource references, normalized fruiting state and survived beside logs. Native value-variant tests isolated the fixed two-block trunk/minimum canopy threshold, then showed radius-one random spread could not reproduce the source tree shape.

## Canonical repair
The existing natural feature/rule identifier now places a hidden, local ticking seed. It uses the same source-derived pepperTreePlan as sapling growth: 3–4 straight logs, a guaranteed eight-leaf ring and five-leaf crown, source lower-layer chances, paired bottom-cardinal decisions, and 25% initial fruiting probability. All leaves remain nonpersistent.

The shared placer resolves all planned blocks before writing, rolls back partial write failures, and defers at unloaded neighboring chunks. An obstructed/invalid seed is removed without filling or overwriting unrelated blocks. No global scan or automatic regrowth of player-placed logs is introduced. Existing leafless trees are not blindly reconstructed; this repair affects new generation and the shared sapling path.

## Evidence
- Current functional suite, source imports, seven targeted placement/rollback tests and historical icon/label guards pass locally
- Native draft test: 64 exact feature placements, both heights observed, 224 logs and 1,205 leaves retained after 200 accelerated random ticks
- Initial fruiting: 310/1,205 leaves (25.73%)
- Six soil types, invalid ground, blocked center, changed origin and side obstruction tested
- Actual chunk-border seed deferred without partial writes and resumed after the neighbor loaded
- 1,048 native assertions, zero failures; BDS exited normally with no logged errors

Detailed counts are in PEPPER-TREE-NATIVE-A2.8.60.json. Direct feature testing is distinct from automatic rule placement in new biome chunks. Client visuals, automatic fresh-chunk coverage and saved-world migration must be recorded separately. Full addon Java parity remains open.
