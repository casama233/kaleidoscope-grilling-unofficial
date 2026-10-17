# A2.7.12 — 剩餘菜刀擊殺掉落：牛內臟 + 魷魚鬚

> Java 基線：Kaleidoscope Grilling 1.1.1 @ `9a1acdab27698457bec16c9362678e574895a28c`。  
> Cookery Bedrock：1.0.6，公開包 SHA-256 `c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351`。  
> 本批只完成 Java `KnifeDropHandler` 中 A2.7.10 尚未覆蓋的 cow / squid 分支。

## Java 1.1.1 真實語義

Java `KnifeDropHandler` 的前置條件：

1. DamageSource causing entity 是 Player；
2. 事件當下讀玩家**目前主手**；
3. 主手匹配 `#kaleidoscope_cookery:kitchen_knife`；
4. Looting 從這把刀讀取。

鎖定 NeoForge Java source Git blob SHA-1：

`4acd1490f9302e3698795c291e2907bdafaf14c8`

A2.7.10 已完成 chicken 分支；A2.7.12 補完其餘兩個。

## Cow

Java：

- entity: cow
- result: `kaleidoscope_cookery:raw_cow_offal`
- chance: **100%**
- count: `1 + random(0..1) + random(0..LootingLevel)`

沒有 Looting 時即 **1–2**。

這個 item 屬於 Cookery，不在 Grilling 重新註冊。CI 會從 checksum-pinned Cookery 1.0.6 公開包解析 `items/raw_cow_offal.json`，確認 identifier 確實是 `kaleidoscope_cookery:raw_cow_offal`。

## Squid

- entity: squid
- result: `kaleidoscope_grilling:squid_tentacle`
- chance: **50%**
- count: `2 + random(0..1) + random(0..LootingLevel)`

沒有 Looting 時，命中掉落就是 **2–3**。

`SQUID_TENTACLE` 在 Java 只是普通 `ingredient("squid_tentacle")`：stack 64、非食物、無 callback / effect。

A2.7.12 新增正式 Bedrock item，使用 Java 原貼圖，Git blob SHA-1 `60aab20cf2c9c4b250780430f7114c22ae7b9dff`。

## Bedrock 實作

A2.7.12 不複製刀具清單，而是直接重用 A2.7.10 的 `KITCHEN_KNIVES` / `isKitchenKnife(...)`。雞翅、牛內臟與魷魚鬚三個 Java death-drop 分支因此共用同一個 Cookery 1.0.6 刀具契約。

使用 stable `world.afterEvents.entityDie`：dead entity 必須是 cow 或 squid；`damageSource.damagingEntity` 必須是 player；事件當下玩家主手必須是 Cookery kitchen knife；Looting 從主手 item enchantable component 讀取。

### Projectile 邊界

與 A2.7.10 相同，本批不額外排除 projectile。Java 本身檢查的是 causing player + 事件當下玩家主手，而不是 direct projectile entity，因此 Bedrock 若把某種 projectile death 的 `damagingEntity` 回報為 player，也沿用同一語義。

## 下游鏈

A2.4 已經有 `squid_tentacle + squid_tentacle + squid_tentacle -> raw_squid_tentacle_skewer`，所以 A2.7.12 讓魷魚串的 Grilling 原料取得鏈正式可達。

牛內臟則恢復 Java 對 Cookery 的額外菜刀擊殺掉落；牛肉本身仍可接 A2.7.9 的砧板覆寫生成 `beef_chunks`。

## CI

A2.7.12 workflow 會重建 A2.0 → A2.7.11，跑 A2.7.12 pure/runtime tests，回歸 A2.7.10 Chicken Acquisition 與 A2.7.11 Mantou Chopping，驗證 Java squid_tentacle 原 texture blob，並 checksum-pin Cookery 1.0.6。

Cookery contract 會各自驗證 A2.7.10 chicken/knife、A2.7.11 mantou extension 與 A2.7.12 raw_cow_offal item；之後用官方 Dash v1.2.0 編譯、source/dist 逐檔比較，最後產出 `.mcaddon` / `.brproject`。

## 下一批

這批後，Java `KnifeDropHandler` 的 chicken / cow / squid 三條就完整了。下一批適合做 `houttuynia -> minced_houttuynia` 砧板加工，或開始 canola 作物取得鏈；pepper tree 世界生成另拆。

Advanced Rack、21 個 advancements / guide 動態進度、skewer plate renderer 仍屬較大系統，繼續後置拆批。

仍保持：

- `minecraft_tested=false`
- `bds_tested=false`
