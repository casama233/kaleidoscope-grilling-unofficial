# A2.7.31 — Farmland Crop Host / 普通作物 Runtime 收斂

本批不新增作物、不改掉落數值，只把 Grilling 三套高度重複的普通農田作物 runtime 合成一個資料驅動 host。

## 為什麼這樣做

A2.7.30 前，以下三個 runtime 幾乎各自複製整套：

- canola
- onion
- sweet_potato

重複內容包括：

- 取得相鄰 block
- 取得光照
- farmland moisture
- 3×3 growth-speed 掃描
- 同種作物鄰接檢查
- age 讀寫
- 骨粉手位搜尋與消耗
- Creative 判斷
- mature unsupported drop
- random tick 生長

這是典型「同一輪子複製三次」。

## 先審查 Cookery Bedrock 宿主

仍以 CurseForge Kaleidoscope Cookery (Unofficial) v1.0.6 為宿主基線：

- Project ID 1673664
- File ID 8908596
- SHA-256 c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351

CI 會直接檢查：

- KC_EXTENSION_API.md
- scripts/api/extensionRegistry.js

目前沒有檢出公開 crop lifecycle registration surface，例如 register_crop / cropExtension / crop capability。

因此這批不能把 Grilling 作物直接「掛 Cookery API」；正確做法是把 Grilling 自己的普通作物 runtime 收斂成一個 host。

## 參考 Cookery Java 的方式，但不照抄行為

官方 KaleidoscopeMods/KaleidoscopeCookery 的 BaseCropBlock：

- Git blob: fd8c6aa62714043c42535027818ce6dd03b48b84
- 以共用 crop class 收納重複生命週期邏輯

這個「共用 host / per-crop data」架構值得直接參考。

但是 Java Grilling 的：

- CanolaCropBlock
- OnionCropBlock
- SweetPotatoCropBlock

都直接 extends vanilla CropBlock，而不是 Cookery BaseCropBlock。

所以本批只借架構，不導入 Cookery BaseCropBlock 的特殊成熟右鍵收割→age 5 行為，避免偏離 Java Grilling。

## A2.7.31 實作

新增：

- a2731_farmland_crop_host_core.js
- a2731_farmland_crop_host_runtime.js

資料表只列：

- crop id
- output id
- custom component id
- age state
- max age
- mature unsupported-drop random draw count

實際：

- canola survival / mature drop → 仍呼叫 a2715 core
- onion survival / mature drop → 仍呼叫 a2717 core
- sweet potato survival / mature drop → 仍呼叫 a2719 core
- bonemeal / growth speed / growth chance → 仍使用已驗證舊 core helper

因此這是 runtime 去重，不是重算玩法。

## 折耳根為什麼不併

Houttuynia 有 Grilling 特例：

- soul sand 可生存
- red_variant
- Nether wart 對應 / 特殊來源

所以 a2714_houttuynia_crop_runtime.js 繼續獨立載入。

## 草帽打草掉落

A2.7.19 已收斂成單一 CropDropHandler subscriber：

canola_seeds → sweet_potato → onion

A2.7.31 把這一個 subscriber 搬進共用 crop host，保持：

- Java branch order
- 六次 random draw 次序
- Fortune 計算
- Cookery straw_hat / straw_hat_flower 條件

不增加第二個 subscriber。

## 舊世界相容

三個 block JSON 不修改。

以下 custom component ID 完全保持：

- kaleidoscope_grilling:canola_crop_logic
- kaleidoscope_grilling:onion_crop_logic
- kaleidoscope_grilling:sweet_potato_crop_logic

age state 仍是：

- kaleidoscope_grilling:age
- 0..7

因此已存在的世界方塊不需要資料遷移。

## 舊 runtime 檔

舊：

- a2715_canola_crop_runtime.js
- a2717_onion_crop_runtime.js
- a2719_sweet_potato_crop_runtime.js

不刪除，保留給歷史 slice CI 重建。

正式 main.js 不再載入它們。

## 結果

普通 farmland crops：

- active runtime modules: 3 → 1
- startup subscribers: 3 → 1
- duplicated helper sets: 3 → 1
- grass acquisition subscribers: 1 → 1

折耳根：

- special runtime 保持獨立

仍保持：

- minecraft_tested=false
- bds_tested=false
