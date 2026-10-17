# A2.7.14 — Houttuynia Crop / 折耳根作物

> Java 基線：Kaleidoscope Grilling 1.1.1 @ `9a1acdab27698457bec16c9362678e574895a28c`。  
> 本批只做折耳根作物本體、種植、生長、紅株、骨粉、貼圖與掉落；不假裝完成 Nether Fortress 結構內生成。

## 本批完成

- `kaleidoscope_grilling:houttuynia` 同一個食物 item 可直接種植
- `kaleidoscope_grilling:houttuynia_crop` 8 階段 crop block
- `age = 0..7`
- `red_variant = false/true`
- farmland / soul sand 兩種基底
- Java placement 紅株規則
- Java CropBlock 生長速度與相鄰作物 crowding penalty
- Java 光照門檻
- 骨粉 +2..5 age
- Java 11 張 crop texture
- 成熟/未成熟掉落與 Fortune 0..3 精確分布

## Java source contract

鎖定：

- `HouttuyniaCropBlock.java` blob SHA-1 `c906c305a2ede0587bdf3d543f5782a05a16d71e`
- `FortressWartReplacementHandler.java` blob SHA-1 `e0e5116dbf5f084efad161b1c32190351345ca4c`
- blockstate blob SHA-1 `dbf5384b283635f91dfd9a68cf38f08437f99e16`
- crop loot blob SHA-1 `1affd5611dd36d3c8622aa04fd4a1c33b74f5300`

`verify_a2714_java_contract.py` 會在 CI 下載這四個固定檔案，以 Git blob SHA 驗證，並重新檢查 age、red variant、0.3 placement、亮度 8、Fortress 25%、wart age mapping 與 loot formula。

## 種植與紅株

Java `HouttuyniaCropBlock`：

- max age = 7
- farmland 或 soul sand 可種
- soul sand 放置必定 `red_variant=true`
- farmland 放置有 30% 機率紅株
- 一旦紅株，後續自然生長 / 骨粉仍保持紅株
- soul sand 上不論舊 state 為何都強制維持紅株

A2.7.14 用 `minecraft:block_placer` 把 A2.7.13 的同一個 `houttuynia` item 接到 crop，不另外造 seeds。`minecraft:use_modifiers.start_using` 改成 `if_first`，有效耕地/靈魂沙優先種植，其他情況仍保留食用行為。

## 生長

runtime 使用 Custom Components v2：

- `system.beforeEvents.startup` 註冊 `kaleidoscope_grilling:houttuynia_crop_logic`
- block JSON 直接掛 namespaced component
- `onRandomTick` 只在這個 crop 上執行
- 不用 `system.runInterval` 掃描玩家附近作物

生長速度按 Java/vanilla CropBlock：

- base speed = 1
- 正下方 dry farmland +1 / moist farmland +3
- 周圍八格 farmland 只算 1/4 權重
- X/Z 兩方向同時有同種 crop，或有對角同種 crop，speed /2
- growth chance = `1 / (floor(25 / speed) + 1)`
- 自然長大需要亮度 >=9

生存條件：

- soul sand：允許
- farmland：位置 raw light >=8

crop block `minecraft:light_dampening=0`，避免自訂 block 本身把光吃掉。

## 骨粉

Java `CropBlock.getBonemealAgeIncrease()` 是均勻 +2..5 age。A2.7.14 同樣做 +2..5，最多 clamp 到 age7。

Creative 以官方 `GameMode.Creative` 判斷，不消耗骨粉；Survival 會消耗一個。

## 視覺

Java blockstate：

- age0..4：紅/綠 variant 共用 stage0..4
- age5：normal=`stage5`, red=`stage5_2`
- age6：normal=`stage6`, red=`stage6_2`
- age7：normal=`stage7`, red=`stage7_2`

11 張貼圖全部從鎖定 Java commit 以 Git blob SHA 驗證下載。Bedrock 幾何採兩張 ±45° 平面，沿用 Microsoft 官方 custom crop sample 的 cross-crop 方式。

## 掉落

Java：

- 未成熟：固定 1 `houttuynia`
- age7：固定第一個 1，再有第二個 item stack 套 `binomial_with_bonus_count`
- `extra=1`
- `probability=0.5714286`
- Fortune enchantment

因此總數為 `2 + Binomial(FortuneLevel + 1, 0.5714286)`。

Bedrock loot table 用獨立 Bernoulli pools 重現這個分布：

- base 2
- 一次 0.5714286 bonus（Fortune 0 即存在）
- Fortune >=1 / >=2 / >=3 各多一次 0.5714286 bonus

所以 vanilla Fortune 0..3 分布完全對齊。非原版 over-level Fortune >3 不宣稱完全等價。

如果 crop 因耕地亮度不足而在 random tick 被清除，runtime 也會按當前 age 處理：未成熟掉 1；成熟使用 Fortune 0 的 Java 分布，不會一律退化成 1 個。

## Nether Fortress 仍未完成

Java 新 chunk 邏輯：

- 僅 Nether
- 僅真實 Nether Fortress bounding box
- 僅新 chunk
- fortress 內 Nether Wart 以 deterministic coordinate hash 做 25% 替換
- wart age 0 -> crop age 0
- wart age 1 -> crop age 3
- wart age 2 -> crop age 7
- 替換後 `red_variant=true`

A2.7.14 **沒有**用「附近有地獄磚就當要塞」之類 heuristic。目標 stable `@minecraft/server 2.9.0` 沒有可用的 stable generated-structure containment/bounding-box API；目前文件中的 generated-structure 查詢仍屬 pre-release，因此本批只保留 mapping/25% contract，不虛報世界生成 parity。

Fortress chest 額外 loot pool 也仍延後，因 stable loot table API 沒有安全的 additive vanilla-table mutation；整張覆寫 `chests/nether_bridge` 會傷害 Add-On 相容性。

所以本批後：

- 手動取得一個 Houttuynia 後的種植/繁殖循環：完成
- Houttuynia -> Minced Houttuynia：A2.7.13 已完成
- Nether Fortress 自然初始取得：未完成
- `survival_houttuynia_acquisition_complete=false`

仍保持：

- `minecraft_tested=false`
- `bds_tested=false`
