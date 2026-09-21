# A2.7.30 — Cookery Oil Pot Adapter / 油壺宿主契約收斂

本批不新增菜品，只修正 Grilling 對 Cookery 油壺的重複狀態讀寫。

## Bedrock 宿主

以 CurseForge Kaleidoscope Cookery (Unofficial) v1.0.6 為宿主基線：

- CurseForge Project ID: 1673664
- File ID: 8908596
- 發布日期：2026-09-18
- SHA-256: c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351

Cookery 本體擁有：

- kaleidoscope_cookery:oil_pot
- kaleidoscope_cookery:oil_pot_filled
- kc_oil_count
- 原生未標 Grilling type 的油壺容量 256

Grilling 只追加自己的 typed oil metadata：

- kaleidoscope_grilling:oil_type
- canola
- secret_chili
- premium_chili
- typed oil capacity 64

## A2.7.29 前的重複層

三個正式 gameplay consumer 各自理解一次油壺格式：

1. main.js — 烤架刷油
2. a26_oil_machine_runtime.js — Big Vat 灌 Cookery 油壺
3. a2722_cold_houttuynia_runtime.js — 涼拌折耳根消耗 premium_chili

它們各自讀 type/count、建立剩餘 ItemStack，Big Vat 對缺失 count 還與另外兩處採不同 fallback。

## A2.7.30

新增唯一 compatibility boundary：

- a2730_cookery_oil_pot_core.js
- a2730_cookery_oil_pot_adapter.js

三個 consumer 不再直接知道：

- kc_oil_count
- kaleidoscope_grilling:oil_type
- kaleidoscope_cookery:oil_pot
- kaleidoscope_cookery:oil_pot_filled

只透過：

- readCookeryOilPot
- buildCookeryOilPot
- planCookeryOilPotConsumption

## 行為保持與修正

正常 stack 規則保持：

- Cookery 原生未 typed 油：256 點
- Grilling typed oil：64 點
- 扣到 0 → Cookery empty oil pot
- typed oil 寫回 oil_type
- count 寫回 kc_oil_count
- 已填充 stack 優先 clone，保留其它宿主/第三方 metadata，再更新 count/type/lore

一致性修正：

- filled pot 缺 count 時統一按容量視為 full
- typed → 64
- untyped → 256

這消除 Big Vat 過去會把同一類 legacy/malformed typed stack 讀成 0，而烤架/涼拌折耳根讀成 64 的差異。

## 為什麼這不是再造油壺

adapter 不實作 Cookery 油壺的設備玩法，也不註冊第二種 oil pot。

它只是 Grilling 對 Cookery host-owned ItemStack contract 的唯一邊界。Cookery 若更新欄位，只改這裡，不再改烤架、大缸與每一道用油料理。

## CI

CI 會下載固定 SHA-256 的 Cookery v1.0.6 公開包，確認：

- empty/filled oil pot item ID 仍存在
- kc_oil_count 仍由 Cookery scripts 使用
- 256-point native capacity 契約仍存在
- Grilling 的 oil_type 不屬於 Cookery host，仍為 child-owned extension metadata

同時確認三個正式 consumer 已沒有任何 host oil-pot 欄位或 item ID literal。

仍保持：

- minecraft_tested=false
- bds_tested=false
