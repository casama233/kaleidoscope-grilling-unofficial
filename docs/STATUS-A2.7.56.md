# A2.7.56 — P0 Official API Hardening

這一批不新增玩法，專門把已完成的 Cookery Wok/Stockpot P0 整合拿去對照 Microsoft 官方 Bedrock Script API 與官方 samples，修掉一個可以實際影響 seasoning metadata 的寫入順序問題。

## 官方案例對照

Microsoft Learn — ItemStack stable API:
https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/itemstack?view=minecraft-bedrock-stable

ItemStack.setDynamicProperty 明確只支援 non-stackable items。

Microsoft Learn — ContainerSlot stable API:
https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/containerslot?view=minecraft-bedrock-stable

官方定義：max stack > 1 且沒有 custom data/properties 才屬於 stackable。

Microsoft Learn — Working With Events:
https://learn.microsoft.com/en-us/minecraft/creator/documents/scripting/events?view=minecraft-bedrock-stable

WorldBeforeEvents listener 不能直接修改 gameplay state。

Microsoft 官方 minecraft-scripting-samples，固定 commit:
https://github.com/microsoft/minecraft-scripting-samples/commit/73a171fc8393a1052b4ca0669dc82231f775d8b1

Containers.ts 以 Container.setItem 做精確 slot replacement。
DynamicProperties.ts 以 world dynamic property + JSON 字串保存結構化狀態。
custom-components/scripts/main.ts 提供官方 item consume / complete-use component 範例。

## 修正

A2.7.50 的 applyFoodMetadata 原本順序：

1. seasoning dynamic property
2. HotFood lore + hot dynamic property

Cookery 菜品本身 max stack > 1，因此第 1 步可能在 item 還可堆疊時被 stable API 拒絕；catch 會讓錯誤靜默，造成「看起來有煙火氣，但 seasoning data 不一定留下」。

A2.7.56 改成：

1. 先寫 HotFood lore，使這份出菜成為 custom / non-stackable serving。
2. 再寫 hot dynamic property。
3. 最後寫 seasoning dynamic property。

沒有新增第二套 Wok/Stockpot，也沒有讀 Cookery 私有 kc_station:*。

## 保留的既有架構

Cookery recipe 仍只走公開 v1 Script Event extension API。
Wok/Stockpot 本體仍完全由 Cookery 1.0.6 擁有。
Grilling 只保存自己的 typed-oil / seasoning sidecar。
before block interaction 只讀與 cancel；inventory/state commit 延後至 system.run。
出菜仍用 inventory before/after delta，只裝飾本次新增的 serving。
3 個 Wok 菜 + 3 個 Stockpot 菜保持不變。

## Java 語義核查

StockpotBlockEntityMixin 本身沒有在每批結束時清空 grilling$seasoning，因此目前 Bedrock Stockpot sidecar 持續保留 seasoning 並不是移植 bug；沒有擅自改掉。

Java FlexPot 仍沒有對應 Cookery Bedrock v1 公開 Wok-flex API；本批仍不以錯誤 batching 偽裝。

## 測試邊界

本批包含結構驗證、JavaScript syntax check、Dash output compare、固定 Microsoft 官方 sample commit contract；不宣稱 Minecraft client 或 BDS 實機測試。
