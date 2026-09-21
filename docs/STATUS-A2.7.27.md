# A2.7.27 — Cookery Host Reuse / 附屬模組去重

> 本批不增加新物品或玩法；只審查並收斂「作為森羅物語附屬模組，哪些輪子不該由 Grilling 再造一次」。

## 參考宿主

Bedrock 宿主以 CurseForge 的 Kaleidoscope Cookery (Unofficial) v1.0.6 為準：

- CurseForge Project ID: 1673664
- 檔名：Kaleidoscope Cookery v1.0.6.mcaddon
- 發布日期：2026-09-18
- 已鎖公開包 SHA-256：
  c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351

Java 官方本體 KaleidoscopeMods/KaleidoscopeCookery 作為設計參考：
本體以通用 Recipe type / BlockEntity API 處理設備，附屬模組主要提供配方資料，而不是每道配方另寫設備 runtime。

## 已經做對：直接掛本體

- 指南已使用 Cookery Guidebook Extension API，只加入一個 Grilling 入口，沒有第二本書。
- 砧板與磨石的切割、stage、耐久、粒子、掉落、加工等設備行為由 Cookery 本體負責。
- mantou、red_chili、廚刀、草帽、油壺等直接依賴本體 ID，沒有複製同名物品。

## 確認存在的重複造輪子

A2.7.26 正式 gameplay main.js 同時載入 7 套幾乎相同的 Cookery recipe runtime：

- A2.7.2 Cookery processing
- A2.7.8 Basic chopping
- A2.7.11 Mantou chopping
- A2.7.13 Houttuynia processing
- A2.7.16 Canola processing
- A2.7.18 Onion processing
- A2.7.24 Red chili processing

每套都重複做：

1. 定義 KC_API / api_ready / register_recipe。
2. 訂閱 scriptEventReceive。
3. capability 過濾。
4. 向 Cookery 發送 recipe payload。

而且 A2.7.2 與 A2.7.8 都會發 startup api_ping；後續 slice 的註解卻一直假設只有一個 ping。

## A2.7.27 收斂方式

正式 runtime 改成：

- 1 個 Cookery host recipe runtime
- 1 個 api_ready listener
- 1 個 startup api_ping
- 1 張資料驅動 recipe table
- 共 9 條目前已發布配方
  - 5 條 chopping_board
  - 4 條 millstone

Cookery 仍負責所有設備機械行為；Grilling 只發布配方資料。

舊 A2.7.x core/runtime 檔不刪，因為歷史 CI slice 仍需要它們做可重建性驗證；正式 main.js 不再載入。

## 牛肉砧板為什麼保留 adapter

Cookery 1.0.6 directStation 的查找順序已鎖定驗證為：

BOARD_RECIPES[id] || getExtensionBoardRecipe(id)

minecraft:beef 在 Cookery 已有內建配方，因此 public extension recipe 無法覆寫 Java Grilling 要求的 beef_chunks ×2。

所以 A2.7.9 的 beef adapter 目前是「宿主 API 缺少 override / priority hook」造成的例外，不是一般附屬配方的模板。

只要未來 Cookery 提供 override priority API，應移除此 adapter。

## 官方 Java 本體帶來的設計原則

KaleidoscopeMods/KaleidoscopeCookery 本身採用：

- BaseRecipe：統一 recipe contract
- ChoppingBoardRecipe / MillstoneRecipe / PotRecipe：通用 recipe type
- IChoppingBoard / IMillstone / IPot：設備能力接口
- datagen builder：附屬內容只提交 ingredient / result / count / cuts / time 等資料

Bedrock Grilling 後續沿用同一原則：

**Cookery 管設備生命週期與互動；Grilling 只提供 recipe/data。**

只有宿主公開接口無法表達的 Java Grilling 特殊語義才寫 compat adapter。

## 下一批應繼續收斂

1. Cookery 油壺兼容
   - main.js 與 a26_oil_machine_runtime.js 現在各自解析 oil type / oil count / fill / lore。
   - 應收成一個共用 oil-pot adapter。

2. 作物 runtime
   - canola / onion / sweet potato 三套 farmland + light + random tick + bonemeal 幾乎重複。
   - 應做一個資料驅動 crop host；Houttuynia 只保留 soul sand / red variant 特例。
   - 這也更接近 Cookery Java BaseCropBlock 的思路。

3. 簡單食物效果
   - roasted sweet potato / cold houttuynia 目前各有 itemCompleteUse listener。
   - 後續新增菜品不再一道菜一個 listener，改成一張 food-effect table + 單一 handler。

4. CI / augment boilerplate
   - 歷史 workflow 保留。
   - 新 slice 應共享 manifest version patch、Dash build、package helper，避免每批複製數百行。

## 不應強行交給 Cookery 的 Grilling 專屬內容

- 烤架 phase / flips / oil / seasoning / overcook 狀態機
- 秘製串、串譜、串盤資料
- 榨油器與大缸
- 花椒樹與 Grilling 作物的內容定義
- Grilling 專屬模型、音效、動畫

原則不是「所有東西都交給 Cookery」，而是「宿主已經有通用設備或 API 的地方不重做」。

仍保持：

- minecraft_tested=false
- bds_tested=false
