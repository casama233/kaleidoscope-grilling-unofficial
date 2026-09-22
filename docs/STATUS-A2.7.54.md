# A2.7.54 — Village Pepper Loot

本批補 Java `VillagePepperLootHandler` 的村莊寶箱取得鏈。

## Java 固定契約

固定上游：

`breezeth-CN/KaleidoscopeGrilling@9a1acdab27698457bec16c9362678e574895a28c`

`VillagePepperLootHandler.java` blob：

`2ec1ae96d8bb7236463eff07127403da45bc8246`

Java 對所有 `minecraft:chests/village/*` 追加兩個**獨立** loot pool：

- 40%：`sichuan_pepper` × 3–10
- 20%：`pepper_sapling` × 1

兩個概率互相獨立，因此一個寶箱可以同時出現花椒與樹苗。

## 為什麼 Bedrock 不能直接照 Java append

Java 有 `LootTableLoadEvent`，可在 vanilla 表載入時 `addPool()`。

Bedrock 官方 loot-table 格式支援：

- referenced loot tables
- pool conditions
- `random_chance`
- `set_count`

但沒有 Java 同級的「對已存在 loot table append pool」Behavior Pack hook。

因此本批不做 Script runtime 猜測「哪個 chest 是 village chest」，也不靠玩家/村民距離近似判斷。

## Wrapper 策略

固定 Mojang 官方 Bedrock 樣本：

- repo：`Mojang/bedrock-samples`
- commit：`46ba6ea985fb5a92d79a9419198f10dda14c199d`
- sample version：`1.26.50.4`

與 gameplay core 的 `min_engine_version 1.26.50` 同一引擎線。

官方樣本共有：

- 15 張實際 `loot_tables/chests/village/village_*.json` chest tables
- 1 張共用 `village_bundle.json`

A2.7.54：

1. 將 15 張真正 chest table 以 **Git blob SHA 固定、byte-for-byte** 保存到：
   `loot_tables/kaleidoscope_grilling/vanilla/village/`
2. 原 vanilla 路徑放很薄的 wrapper：
   - pool 1 → 引用固定 vanilla snapshot
   - pool 2 → 引用共用 `village_pepper_bonus.json`
3. bonus table 只有 Java 的兩個獨立 pool。
4. **不覆蓋 `village_bundle.json`**，避免它被其他 village table 引用時重複抽 Pepper bonus。

這樣不需要在 15 張表中重複貼 Pepper pool，也不手工改 Mojang 原表內容。

## Wrapper 覆蓋的 15 張表

- armorer
- butcher
- cartographer
- desert house
- fletcher
- mason
- plains house
- savanna house
- shepherd
- snowy house
- taiga house
- tannery
- temple
- toolsmith
- weaponsmith

每張官方原表都以 Mojang commit + Git blob SHA 固定；上游樣本變動會讓 CI 直接失敗，而不是靜默漂移。

## 明確兼容邊界

Bedrock 這個做法仍必須在**相同 vanilla loot table 路徑**提供 wrapper。

因此：

- `vanilla_loot_table_override=true`
- `loot_override_compatibility_risk=true`

如果另一個 Behavior Pack 也覆蓋同一張 village chest table，最終結果受 pack priority 影響；Bedrock 沒有 Java 那種多模組 append event 可以自然合併。

這個風險比「複製後手工魔改 15 張 vanilla 表」小，但不能宣稱完全無衝突。

## 不新增 Script runtime

本批純資料驅動：

- 不新增 tick
- 不新增 chest-open listener
- 不掃村莊/玩家
- 不修改 Pepper Tree runtime
- 不修改 advancement runtime

## 驗證

CI 驗證：

- pinned Java handler
- 15 張 Mojang 1.26.50.4 snapshot Git blob
- wrapper 不遞迴引用自己
- bonus 40% / 3–10 與 20% / 1
- `village_bundle` 未覆蓋
- JSON
- Dash build
- compiled-output byte/JSON comparison

仍標記：

- `minecraft_tested=false`
- `bds_tested=false`

## 下一步

Pepper Tree 的主要世界取得鏈至此具備：

- 森林自然生成
- 樹苗生長
- 結果 / 採摘
- village chest 花椒 / 樹苗
- Mountain Fragrance advancement

下一批應重新掃 Java advancements / automation / optional compat，而不是繼續擴寫 Pepper Tree。
