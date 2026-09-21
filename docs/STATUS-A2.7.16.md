# A2.7.16 — Canola Processing / 油菜籽磨粉閉環

> Java 基線：Kaleidoscope Grilling 1.1.1 @ `9a1acdab27698457bec16c9362678e574895a28c`。  
> 本批只補 `canola_seeds -> Cookery Millstone -> canola_powder ×1`。

## Java 配方

`kaleidoscope_grilling:millstone/canola_powder`：

- type: `kaleidoscope_cookery:millstone`
- ingredient tag: `#kaleidoscope_grilling:ingredients/canola_seeds`
- result: `kaleidoscope_grilling:canola_powder ×1`

鎖定 Java 1.1.1 的 tag 實際只有：

`kaleidoscope_grilling:canola_seeds`

所以 Bedrock 公開 Extension Recipe API 直接使用單一 item input，對鎖定 Java 基線是精確集合等價。

Java recipe Git blob SHA-1：`83ef97ff4834dc130ac5be6b6793e7d4a6d0b86c`。  
Java tag Git blob SHA-1：`a69045793742c008107e10bf854406137ee83a41`。

## Cookery 1.0.6

A2.7.16 使用已由 A2.7.2 驗證過的公開 Recipe Extension payload：

- API = 1
- kind = `millstone`
- source = `kaleidoscope_grilling`
- capability gate = `millstone`
- output count = 1
- chance = 1.0

本模組只監聽 `kaleidoscope_cookery:api_ready`，不新增額外 `api_ping`。

CI 會下載 checksum-pinned Cookery 1.0.6，重新驗證：

- `api_ready` / `register_recipe` public extension surface 仍存在
- millstone extension path 仍存在
- Cookery 內沒有 `kaleidoscope_grilling:canola_seeds` built-in recipe/input 搶先覆蓋

Cookery 公開包 SHA-256：

`c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351`

## 生存鏈現在閉環

A2.7.15 已有：

`戴 Cookery 草帽打短草 -> canola_seeds -> 種植/繁殖`

A2.7.16 新增：

`canola_seeds -> Cookery Millstone -> canola_powder ×1`

repo 原有：

`8 canola_powder + 1 wheat -> oil_cake`

A2.6 原有：

`4 oil_cake -> Oil Press -> 4 buckets canola oil -> Big Vat / Oil Pot`

所以從 A2.7.16 起，**Canola Oil 的生存取得主鏈完整閉環**。

## Create 相容

Java 另有 Create crushing / milling 的 canola powder recipe。這些是可選 mod 相容，不是原版 + Cookery 生存鏈必要條件。

Bedrock 目前沒有對應 Create port，因此本批保持：

- `create_milling_ported=false`
- `required_for_survival_chain=false`

這不影響 Canola Oil 主生存鏈已閉環的結論。

## 回歸

A2.7.16 會至少回歸：

- A2.7.15 Canola Crop + Straw Hat Acquisition
- A2.7.14 Houttuynia Crop
- A2.7.13 Houttuynia Processing
- A2.6 Oil Press / Big Vat

並做官方 Dash v1.2.0 編譯與 source/dist 逐檔比對。

仍保持：

- `minecraft_tested=false`
- `bds_tested=false`
