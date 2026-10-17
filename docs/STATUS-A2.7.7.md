# A2.7.7 — 烤架交易提交順序與 rollback

> 本批仍是穩定化，不新增食材、菜品、作物或 processing recipe。  
> Java 基線：Kaleidoscope Grilling 1.1.1 @ `9a1acdab27698457bec16c9362678e574895a28c`。  
> Bedrock：`@minecraft/server 2.9.0`。

## 1. 為什麼還要做這一層

A2.7.5 / A2.7.6 已經處理：

- 長按重複 block-use；
- Java shovel 熄火；
- 點火前刷油；
- Flint & Steel 耐久；
- deferred callback 的 stale intent；
- 主／副手資源交易。

但仍有「兩個 mutation 先後成功程度不同」的風險。

例如舊版刷油：

1. 先把油壺扣掉；
2. 再寫 Grill state。

如果第 2 步拋例外，油已經少了、烤架卻沒進入刷油 phase。

舊版取串則相反：

1. 先把熟串給玩家；
2. 再清 Grill slot。

若第 2 步失敗，來源還留在 Grill，產物已經到玩家手上，形成複製風險。

A2.7.7 專門收斂這些 commit-order 問題。

## 2. 狀態 + 手持資源：雙邊 rollback

以下操作改成同一個 transaction helper：

- Flint & Steel 點火；
- Cookery Oil Pot 刷油；
- Special Seasoning 撒料。

流程：

1. 先完整計算 next grill state；
2. 先完整建立 next hand stack；
3. 寫入 Grill state；
4. 寫入 used-hand resource；
5. 任一步拋例外 → 以 before snapshot 同時恢復 hand 與 Grill state。

`commitTwoParty()` 不把 rollback 本身的第二次例外往外炸，而是記錄 rollback error 數量。

這不是資料庫式 ACID；Bedrock Script API 沒有跨 world/inventory 的原生 transaction。但相較以前「一邊成功就算了」，現在至少具備明確 snapshot / rollback 邊界。

## 3. 取串：先移除來源，再交付

A2.7.6 以前：

`give(output) -> clear grill slot`

A2.7.7 改成：

`prepare output -> clear source slot -> deliver output`

如果 delivery 拋例外：

- 原 raw slot 立即恢復；
- 不 reset Grill phase；
- 顯示 rollback 提示。

### 交付策略

為避免 `Container.addItem` 在滿背包下出現「部分 merge 已發生、剩餘 spawn 又失敗」這種難 rollback 情況：

- 有已知空 inventory slot → 直接 `setItem(emptySlot, output)`；
- 沒有空 slot → 在玩家位置 spawn output。

所以在「背包沒有空格、但已有同類未滿 stack」的特殊情況，Java `placeItemBackInInventory` 可能會 merge，而 Bedrock A2.7.7 會掉在玩家腳邊。

這是刻意保留的安全差異：**寧願可見掉地，也不做不可逆 partial merge。**

## 4. 拆爐：掉落物 escrow

A2.7.6 以前：

1. spawn 內容掉落；
2. clear container；
3. clear state；
4. remove helper；
5. set block air。

如果 2~5 中途拋例外，就可能掉落已經生成，但來源 block 還存在。

A2.7.7 改成 escrow：

1. snapshot：
   - block permutation
   - Grill state
   - 3 個 slot
2. 先計算所有應掉物；
3. 把所有內容掉落 + 非 Creative 的 Grill item 生成成 escrow entities；
4. 再提交：
   - clear container
   - clear state
   - remove helper
   - set block air
5. 如果 destructive commit 失敗：
   - 對 escrow entity 呼叫 `Entity.remove()`
   - 恢復原 block permutation
   - 恢復 3 slots
   - 恢復 Grill state

`Entity.remove()` 在目前使用的 stable Script API 路徑可用，所以不需要 kill entity 或依賴掉落自清。

因 JS callback 同步執行，escrow 與來源同時存在的短暫窗口不會被另一個 script callback 插入執行。

## 5. A2.7.7 沒有聲稱什麼

這仍不是：

- 真正跨 Add-On ACID transaction；
- crash/power-loss journaling；
- Minecraft/BDS 實機 PASS；
- Cookery host 內部資料 transaction；
- 新內容批次。

Rollback 本身若遇到引擎持續拋例外，只能 best-effort；報告不會寫成絕對不可丟資料。

## 6. CI

A2.7.7 會完整重建 A2.0 → A2.7.6，再驗證：

- `commitTwoParty` 成功／primary failure／secondary failure／rollback failure；
- extract clear-before-deliver 順序；
- delivery 失敗 source restore；
- aborted extract 不 reset phase；
- break escrow spawn 在 destructive commit 之前；
- commit failure 會 remove escrow + restore snapshot；
- A2.7.6 intent/hand parity 保留；
- A2.7.5 input hardening 保留；
- A2.7.4 Java 原 GUI icons 保留；
- A2.7.3 suspended grill helper 保留；
- 全 gameplay JS 語法；
- Dash v1.2.0；
- source / dist 逐檔比較；
- mcaddon / brproject 打包。

仍保持：

- `minecraft_tested=false`
- `bds_tested=false`
