# A2.7.59 — P1 Completion

本批不是重做 P1，而是對已經並行落地的 P1 做完整 parity audit，補掉最後一個可修的 Java 差異。

## Advanced Rack

A2.7.46 已確認完整覆蓋 Java 核心 gameplay：

- 9 compartments
- 0–4 seasoning / 5–8 tools
- persistent filters
- matching deposit
- selected-hotbar swap + binding
- 8-block nearest-rack shortcut
- spice level 0–4
- break -> item -> place 保存內容與 filters
- borrow / return automation API

Bedrock 使用 ActionForm UI 與 /kaleidoscope_grilling:rack 作為 Java GUI / Caps-Lock /kgrack 的平台等價映射。

本批不重寫 Rack。

## Pepper Tree

既有版本：

- A2.7.48 lifecycle
- A2.7.51 forest worldgen
- A2.7.53 Pepper harvest advancement
- A2.7.54 village Pepper / Sapling acquisition

### 本批修正：自然生成 25% 結果葉

Java PepperTreeFeature.leafState() 使用 random.nextInt(4) == 0，即每片新生成葉約 25% 初始帶花椒。

A2.7.51 因為 Bedrock tree feature 不能直接對同一 custom block 的不同 state 設定 weighted permutation，當時全部生成未結果葉。

A2.7.59 使用官方資料驅動模式：

- canopy weighted leaf IDs：canonical pepper_leaves weight 3；internal pepper_leaves_fruiting_bridge weight 1
- bridge 沒有 item、沒有 loot、沒有獨立 gameplay
- minecraft:tick 只執行一次（1 tick）
- tick 後轉成 canonical pepper_leaves，has_pepper=true，persistent=false

所以玩家後續互動、採摘、decay、掉落仍全部走 A2.7.48 的唯一 Pepper Leaves lifecycle。

官方 Bedrock samples 同樣使用 3:1 weighted leaf IDs（azalea / flowering azalea）；minecraft:tick 官方 schema 支援 looping=false 的 one-shot tick。

## Stable API 平台限制

Java PepperLeavesBlock.entityInside 可在 entity 持續穿過葉片時不斷施加移動阻力。

目前 Bedrock stable BlockCustomComponent 沒有 onEntityInside 等價事件；可用的是 onStepOn/onStepOff/onTick。

A2.7.48 已使用 top collision、onStepOn、短時 Slowness、20 tick damage throttle、Fox / Bee 免疫。

本批不增加全域 entity×leaf 掃描器來假模擬 Java callback，因為那會用昂貴輪詢換取平台 API 本身不存在的細節。

因此：P1 可實作 gameplay / acquisition / worldgen parity 完成；entityInside callback 本身記錄為 Bedrock stable API 平台差異。

## 驗證限制

- minecraft_tested=false
- bds_tested=false
