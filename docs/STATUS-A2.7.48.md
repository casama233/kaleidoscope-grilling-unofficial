# A2.7.48 — Pepper Tree Lifecycle

本批填補 Java 內容中一直缺失的 Pepper Tree 核心生命週期；自然森林生成與村莊箱來源留給下一小批。

## Java 固定契約

固定 Java 1.1.1 commit `9a1acdab...`：

- `PepperLeavesBlock.java`
- `PepperLogBlock.java`
- `PepperSaplingBlock.java`
- `PepperTreeFeature.java`
- `StrippingHandler.java`

本批移植：

- Pepper Log / Leaves / Sapling 三個可放置方塊
- 樹苗 stage 0 -> 1 -> tree
- 隨機生長要求上方光照 >= 9，1/7 機率
- 骨粉 45% 成功率
- 樹高 2–3，Java 對應樹幹 / 樹冠形狀
- 新生成葉片 25% 帶花椒
- 空葉 1/20 random tick 結果
- 空手採收 1–2 花椒並回到未結果
- 葉片失去相連 Pepper Log 後衰敗
- 玩家放置葉片標成 persistent
- 踩葉片：Fox/Bee 免疫；其他生物有減速並每 20 ticks 最多受 1 點刺傷
- 剪刀 / Silk Touch 掉 Pepper Leaves
- Fortune 對 sapling / stick 的 Java loot 機率
- 有花椒的葉片被破壞時額外掉 1 花椒
- Pepper Log 可橫向放置
- 斧剝皮 -> vanilla Stripped Oak Log，保持 pillar axis
- Pepper Log -> 4 Oak Planks

## 不重複造輪子

- 樹苗/葉片生長使用專案現有 crops 相同的 block custom-component 模式。
- 骨粉手部 I/O 復用 `a2735_player_io.js`。
- 不建立任何 `system.runInterval`。
- 泥土判定使用 stable `Block.hasTag('dirt')`，不維護自己的 dirt 白名單（只有 API fallback）。
- 四份 Pepper geometry / texture 直接復用 A1 已轉好的資產，CI 逐位元比較，不重新建模。

## Bedrock 適配邊界

Java `entityInside` 會讓穿過葉子的生物持續變慢；Bedrock stable custom block 有 `onStepOn`，但沒有完全等價的「持續 inside callback」。

本批以 top collision + `onStepOn` 做刺傷/短時 Slowness，不建立每葉片 tick 掃描器。這個差異明確保留，不用全域輪詢硬補。

玩家精確破壞 Pepper Leaves 的掉落由 script 處理；爆炸/非玩家破壞走簡化 fallback loot，避免再複製一套 state-aware loot parser。

## 下一步 A2.7.49

- 森林自然 Pepper Tree worldgen
- Village chest：40% 花椒 3–10；20% Pepper Sapling
- `pepperPicked` advancement / Bedrock 對應
- 再核對 Pepper Tree acquisition 後是否還有世界內容差異

## 驗證限制

- minecraft_tested=false
- bds_tested=false
