# A2.7.10 — 雞皮 / 雞翅生存取得鏈

> Java 基線：Kaleidoscope Grilling 1.1.1 @ `9a1acdab27698457bec16c9362678e574895a28c`。  
> Cookery Bedrock：1.0.6，公開包 SHA-256 `c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351`。  
> 本批只補 `chicken_skin` 與 `chicken_wing`，不順帶做魷魚須、饅頭片或熟雞翅菜品。

## 1. Java 真實來源

### Chicken Skin

Java 並沒有一條新的 chicken_skin Chopping Board recipe。

Cookery 原本的：

`minecraft:chicken -> kaleidoscope_cookery:raw_cut_small_meats ×2 / 4 cuts`

仍然正常執行。

Grilling 的 `ChoppingBoardBlockEntityMixin` 只在 Cookery `onCutItem` 完成前記錄：

- current stack = raw chicken
- current cut count >= max cut count
- max cut count > 0

而且只有 Cookery `onCutItem` 真正回傳成功時，才額外：

`chicken_skin × (1 + random 0..2)`

因此正確語義是：

**原 Cookery 結果 + 額外雞皮 1–3**

而不是把 `raw_cut_small_meats` 換成雞皮。

Java mixin Git blob：
`3b201faf83c2b8aa29008d1d63185d7738f6a2f1`

### Chicken Wing

Java `KnifeDropHandler`：

1. `DamageSource.getEntity()` 必須是 Player；
2. 在 LivingDropsEvent 當下讀玩家目前主手；
3. 主手必須匹配 `#kaleidoscope_cookery:kitchen_knife`；
4. entity type 必須是 chicken；
5. chance = 100%。

數量：

`1 + random(0..1) + random(0..LootingLevel)`

沒有 Looting 時就是 **1–2 個**。

Java KnifeDropHandler Git blob：
`8a6e2705d46ec9535dc35b8baf203d3411c84e6e`

## 2. Bedrock Chicken Skin adapter

Cookery Bedrock 1.0.6 的 exact contract：

- `BOARD_RECIPES["minecraft:chicken"] = raw_cut_small_meats ×2 / 4 cuts`
- native board model index for chicken = **2**
- completion action在 `cuts >= max` 時 pop result 並 clear station state
- station state key = `kc_station:<dimension>:x,y,z`

A2.7.10 不 cancel Cookery 這個完成 interaction。

Grilling 只在 before-event 偵測到：

- chopping_board
- state = raw chicken
- cuts >= 4
- result = raw_cut_small_meats ×2
- first event
- 主手為 Cookery kitchen knife

時建立一次性 completion watch。

下一 callback：

- 如果 Cookery state 已 clear / advance，視為原完成成功；
- 額外在砧板位置生成 chicken_skin 1–3；
- 如果 state 沒變，視為 Cookery completion 沒成功，不給 bonus。

每個 station key 同一 callback window 最多一個 pending watch，避免兩名玩家同 tick 對完成態砧板互動造成 bonus duplication。

## 3. Bedrock Chicken Wing drop

Bedrock stable `world.afterEvents.entityDie` 提供：

- `deadEntity`
- `damageSource`
- `damageSource.damagingEntity`

A2.7.10 僅在：

- dead entity = `minecraft:chicken`
- damaging entity = `minecraft:player`
- 玩家當下主手 = Cookery kitchen knife

時生成 chicken_wing。

Cookery 1.0.6 的 knife set 精確鎖定為：

- iron_kitchen_knife
- gold_kitchen_knife
- diamond_kitchen_knife
- netherite_kitchen_knife

Looting 從 item `minecraft:enchantable` component 的 `getEnchantment('looting')` 讀取。

### Projectile 邊界

A2.7.10 **沒有自行排除 projectile**。

原因不是疏漏，而是 Java 實際代碼只檢查 causing entity 是 Player，再檢查玩家事件當下主手是不是 knife，沒有檢查 direct entity 是否為 projectile。

因此如果 Bedrock 的 `damagingEntity` 對某個 projectile death 回報玩家，且死亡當下玩家主手為 kitchen knife，這版會照 Java 實際實作給掉落。

## 4. 物品本體

### Chicken Skin

- stack 64
- 非食物
- 無特殊 callback
- Java 原 texture Git blob：
  `5a8517468ed9da877b219047e1032d3a4c728bfc`

### Chicken Wing

Java：

- stack 64
- nutrition = 2
- saturation modifier = 0.06
- 無額外效果

Bedrock：

- nutrition 2
- saturation_modifier 0.06
- 1.6 秒普通 eat use
- 可副手使用
- 不 always-eat

Java 原 texture Git blob：
`4adb1a131eb7f0dda0ed43f616e1dd561c7b3e71`

## 5. 下游鏈

A2.4 fixed-skewer table 已經有：

- `chicken_skin + chicken_skin -> raw_chicken_skin_skewer`
- `chicken_wing + red_chili + chicken_wing -> raw_mid_wing_skewer`

所以本批讓兩條原本「recipe 存在但 Grilling 原料不可生存取得」的固定串鏈恢復可達。

其中 mid-wing 仍依賴 Cookery `red_chili` 可取得性；本批不重寫 Cookery 辣椒內容。

## 6. CI / 誠實邊界

A2.7.10 workflow 會：

- 完整重建 A2.0 → A2.7.9
- 跑 chicken acquisition pure/runtime tests
- 驗證 Java 原 texture blob
- 下載 checksum-pinned Cookery 1.0.6
- 驗證 chicken board recipe / native model / knife IDs / completion contract
- 官方 Dash v1.2.0
- source / dist 逐檔比較
- mcaddon / brproject 打包

不發布 Cookery 原包。

仍保持：

- `minecraft_tested=false`
- `bds_tested=false`
- `engine_rendering_verified=false`
