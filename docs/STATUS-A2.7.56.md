# A2.7.56 — Event-driven Advancement Parity

本批擴展 A2.7.53 已建立的一次性 Bedrock advancement adapter，不建立第二套成就系統。

## 本批六個 Java advancement

- Looking the Part / 有模有樣 — 完成第一根串簽 — task — 10 XP
- Gleaming with Oil / 油光鋥亮 — 第一次成功刷油 — task — 10 XP
- Three Flavors Base / 三味打底 — 集齊三種基礎調料 — task — 10 XP
- World in a Bottle / 瓶中乾坤 — 調料瓶達 8 份材料 — goal — 25 XP
- Eat It Hot! / 趁熱吃！ — 吃仍帶煙火氣的熟串或 Secret Skewer — goal — 25 XP
- Neat and Orderly / 井井有條 — 放置 Advanced Rack — goal — 25 XP

## 復用

全部走 A2.7.53：

`awardOneShotAdvancement(player, spec)`

因此共用：

- player dynamic property 一次性持久化
- XP
- chat announcement
- localized self message
- stable advancement key

## 觸發點

不新增任何 listener / interval。

只在現有成功交易點插入 award：

- `threadCurrent()`
- Grill oil commit 成功後
- Seasoning ingredient 寫入成功後
- `afterCommitted()`
- Advanced Rack placement restore 成功後

這些都是 Java `ModAdvancements` 的同等事件。

## Fortress Wart Replacement

本批沒有實作。

官方 Bedrock Creator 文件目前沒有可對 legacy Nether Fortress 做 additive structure patch 的穩定資料驅動入口；Jigsaw 文件也明確指出多數 vanilla structures 仍為 legacy。用玩家附近掃方塊去猜 fortress 會：

- 誤傷玩家自己種的 Nether Wart
- 增加 tick / chunk 掃描負擔
- 不能真正證明在 fortress bounding box 內

因此暫列 `platform_blocked_without_intrusive_scan=true`，不以低品質近似冒充 Java parity。

## 下一批

剩餘 advancement 可分兩類：

1. inventory / dimension check：Human Fireworks、A Handful of Canola、Strength Makes Oil、Sweet Potato、Nether Taste、Better Write It Down
2. effect/food challenge：Mental Preparation Failed、Metallic Taste、Taste of Dragon、Metal Tolerance Failed、Strongest Shield、Strongest Spear、Fireworks Feast、Wedding Candy

應優先復用現有事件與 A2.7.53 adapter，不再建第二個 progression store。

## 驗證限制

- native_java_advancement_tree=false
- native_java_toast=false
- minecraft_tested=false
- bds_tested=false
