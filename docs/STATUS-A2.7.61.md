# A2.7.61 — Runtime Hygiene

本批目標不是再補一個玩法，而是把 A2.7.60 之後的正式執行路徑先整理成可維護、可重現的基線。

## 根因

目前正式 Gameplay Core 已累積大量 `a27xx_*_runtime.js`、版本化 augmenter 與版本化 CI。它們保存了很有價值的移植歷史，但若把歷史升級工具也當成「目前來源」，容易再次出現：

- 改到 development 歷史檔，但正式 BP/RP 沒有同一內容；
- 每個小版本再複製一份 workflow，驗證入口持續膨脹；
- runtime 模組各自訂閱事件，之後新增功能時難以判斷同一手勢由誰負責；
- 空閒設備仍在高頻輪詢中做不必要的持久化寫入。

實際檢查也確認目前 A2.7.60 正式 `a26_oil_machine_runtime.js` 已包含後續 Cookery adapter/player-IO 改造，與早期 `development/gameplay_core/a26_oil_machine_runtime.js` 並非同一 blob。這不是把舊檔覆蓋回去的理由，反而說明目前正式 pack 必須被明確視為 canonical runtime。

## Java 規格核對

重新讀取 Java `GrillBlock.use()` 後，本批確認目前 Bedrock 主優先序仍保持：

1. flint and steel 點火；
2. extinguish_stove 類工具熄火；
3. oil pot 刷油；
4. special seasoning 調味；
5. 非空手嘗試插串；
6. 空手翻面；
7. 空手顯示缺油／缺調味提示；
8. 可取出時空手取串，潛行連續取出。

因此 A2.7.61 不重寫烤架狀態機，不把效能整理混成玩法改版。

## 實際改動

### 烤架

舊行為：registry 中每個烤架每 tick 都呼叫 `writeState`，即使 `tickState` 結果完全沒變，也會重寫 world dynamic property。

新行為：

- 比較 normalize 後的完整狀態；
- 只有 phase/timer/flips/cooldown/seasoned/failed/heat/lit/seasonings 任一欄真正變化時才重寫持久資料；
- `syncGrillPermutation` 仍每 tick 執行，保留支撐方塊改變後 legged 狀態的更新；
- 加熱／冷卻中的有效 timer 仍逐 tick 保存。

### 榨油器

舊行為：

- completionDelay tick 透過 `writePress` 更新後，又進 `registerPress` 重新讀一次 registry；
- interval 結束時無論 registry 是否變化都 `saveReg(keep)`。

新行為：

- registry 迭代內使用 `writePress(block, state, false)`，避免已註冊設備再查一次 registry；
- 只有 keep 長度改變時才重存 registry；
- completionDelay 仍維持 1 tick 更新，沒有改 Java 時序。

### 建置

- `projects/grilling/gameplay_core/{behavior_pack,resource_pack}` 明確成為 canonical runtime。
- 新增通用 `tools/check_grilling_release.py`。
- 新增 deterministic `tools/build_grilling_release.py`。
- 新增單一 canonical CI，未來常規 runtime 修正不必再複製一份 A2.7.x workflow。
- 歷史 augmenter/workflow 暫不刪除，先降為 provenance/replay；避免一次清理掉唯一歷史證據。

## 本批檢查

通用 checker 會驗證：

- 所有 canonical JSON 可解析；
- BP/RP UUID 未變；
- BP/RP 版本與相互依賴一致；
- Cookery 1.0.6 依賴未被私服 UUID 汙染；
- pack 只有一個 Script API entry：`scripts/main.js`；
- 本地 JS import 全部存在且不逃出 canonical scripts tree；
- 全部 JS 通過 `node --check`；
- block/item identifier 不重複；
- 公開 Gameplay Core 沒重新帶入整份 player override；
- Dash compiled output 與 canonical source 逐檔對應；
- candidate mcaddon ZIP、manifest、entry 與 SHA-256 正確。

## 尚未證明

- 沒有執行模擬玩家互動測試。
- 這批新 A2.7.61 candidate 尚未由 Minecraft 客戶端、Android 或 BDS 實機驗收。
- 本批沒有宣稱所有 runtime listener 已經合併；事件入口收斂會分小批處理，先從有重疊風險的 block interaction 開始。
- 手持模型、透明材質、HUD coexistence 與多人互動不因 CI 通過而視為已驗收。
