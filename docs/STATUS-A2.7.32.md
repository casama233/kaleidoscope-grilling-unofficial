# A2.7.32 — Standalone Food Effect Registry / 非烤串料理效果收斂

本批不新增菜品、不改營養值、不改配方，只收斂「非烤串料理吃完後效果」的 runtime。

## 為什麼要修

主烤串系統其實已經做對：

- main.js 使用集中式 COOKED_EFFECTS
- 所有烤串固定效果由同一 applyFixedEffect 處理

不需要再造第二套烤串效果系統。

真正重複的是 standalone foods：

- roasted_sweet_potato 自己一個 itemCompleteUse subscriber
- cold_houttuynia 自己一個 itemCompleteUse subscriber

如果剩餘菜品照這個模式加入，之後每一道帶效果料理都會再多一個 listener。

## A2.7.32

新增：

- a2732_standalone_food_effect_core.js
- a2732_standalone_food_effect_runtime.js

目前 registry 只有已經發布的兩列：

1. roasted_sweet_potato
   - persistent FX: warmth
   - 600 ticks
   - stacking = max(existing until, now + 600)

2. cold_houttuynia
   - native effect: fire_resistance
   - 1200 ticks
   - showParticles = true

共用 runtime 只訂閱一次 itemCompleteUse。

## 保留既有特殊邏輯

### 烤番薯

舊 a2720 core 不改。

新的 persistent effect 計算直接重用 nextWarmthUntil，因此保持：

- 第一次吃：now + 600
- 既有較短 warmth：延長到 now + 600
- 既有更長 warmth：不縮短

舊 a2720 runtime 檔仍保留給歷史 slice CI，但 main.js 不再載入。

### 涼拌折耳根

a2722 runtime 仍然正式載入，因為它還負責：

- 潛行 + crafting table 的特殊合成 gesture
- 3 個折耳根
- premium_chili oil -2
- ItemStack 交易與 rollback

A2.7.32 只從它移除 fire_resistance 的 itemCompleteUse subscriber。

食用效果改由共用 handler 負責。

## 與 A2.7.30 油壺 adapter 的關係

cold_houttuynia 的合成仍走：

- readCookeryOilPot
- buildCookeryOilPot

所以本批不會把已收斂的 Cookery oil-pot 邏輯拆回去。

## 為後續菜品準備

registry 每個 item 可以有 effects 陣列，因此後續可以直接支援：

- 單一 native effect
- 多個 native effect
- persistent Grilling/Cookery-style FX
- 同一道料理同時多效果

這正好適合剩餘 Java 菜品，例如：

- red_sweet_potato_porridge：flatulence + warmth
- sour_spicy_noodles：warmth

後續不需要再增加一菜一 listener。

## 驗證

CI 會同時跑：

- A2.7.31 baseline
- A2.7.20 Java roasted sweet potato contract
- A2.7.22 Java cold houttuynia contract
- 新 registry pure-core tests
- 新 unified runtime VM test
- Dash compile
- source/dist byte/JSON compare

仍保持：

- minecraft_tested=false
- bds_tested=false
