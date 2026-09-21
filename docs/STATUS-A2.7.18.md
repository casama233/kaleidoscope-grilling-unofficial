# A2.7.18 — Onion Processing / 洋蔥磨粉

> Java 基線：Kaleidoscope Grilling 1.1.1 @ `9a1acdab27698457bec16c9362678e574895a28c`。  
> 本批只補 `Onion -> Cookery Millstone -> Onion Powder ×1`。

## Java 配方與 tag 鏈

`kaleidoscope_grilling:millstone/onion_powder`：

- type: `kaleidoscope_cookery:millstone`
- ingredient: `#kaleidoscope_grilling:ingredients/onions`
- result: `kaleidoscope_grilling:onion_powder ×1`

鎖定 1.1.1 的 tag 鏈：

`#kaleidoscope_grilling:ingredients/onions`
→ `#c:crops/onion`
→ `kaleidoscope_grilling:onion`

Git blob SHA-1：

- recipe `763aaf30a9e7a6540f36406f5e7155a9eec9be4d`
- Grilling tag `38c13e1a55a253306b87c3e5c3795f832b9e2675`
- common tag `7ba3089ca4c404f7954bcd8d1533cd4ed62c8875`

所以對**鎖定 Java 基線本身**，Bedrock 直接以 `kaleidoscope_grilling:onion` 註冊是精確解析結果。

## Common-tag 相容性差異

Java 的 `c:crops/onion` 是 `replace:false` common tag，其他 Java 模組可以把自己的 Onion 加進來。

Cookery Bedrock Extension Recipe API 的 input 是 item identifier，並沒有對應的 cross-addon common-tag resolver。因此 A2.7.18 明確標記：

- 鎖定基線原生 Onion input：精確 ✅
- 第三方 Java-style `c:crops/onion` 動態擴展：未移植 ❌

不把「目前 tag 只有一個值」誤說成永遠等價。

## Cookery 1.0.6

使用公開 Recipe Extension API v1：

- `kind = millstone`
- capability gate = `millstone`
- `input = kaleidoscope_grilling:onion`
- `output = kaleidoscope_grilling:onion_powder ×1`
- chance = 1.0

不修改 Cookery 私有 script，也不新增第二個 `api_ping`。

CI 使用 checksum-pinned Cookery 1.0.6，確認：

- `api_ready` / `register_recipe` 還存在
- millstone extension lookup 還存在
- Cookery 自身沒有內建 `kaleidoscope_grilling:onion` 搶 precedence

Cookery archive SHA-256：

`c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351`

## 生存鏈

A2.7.17：

`草帽打短草 -> Onion -> 種植/繁殖`

A2.7.18：

`Onion -> Cookery Millstone -> Onion Powder ×1`

因此本模組 Onion 的生存取得與加工主鏈已閉環。

Java 另有 Create milling recipe；Bedrock Create 相容仍未做，但不是 Cookery 主生存鏈必要條件。

## CI 增量模式

從這批開始，小型 parity slice 不再每次從 A2.0 全量重建：

1. 直接使用 main 已正式 publish 的 A2.7.17 generated project。
2. 先跑 `verify_a2717.py` 與關鍵前序 regression，確保基線沒有漂移。
3. 只套用 A2.7.18 generator。
4. 跑 A2.7.18 + A2.7.17/A2.7.16 regression。
5. 用 checksum-pinned 官方 Dash v1.2.0 全包編譯。
6. 對 source/dist 逐檔比對。
7. PR 只上傳 review artifact；main 才 publish generated project/artifacts。

這比每個小批都重新跑 A2.0→最新快很多，同時仍用已發布基線、contract、回歸測試和完整 Dash compare 保住安全性。

仍保持：

- `minecraft_tested=false`
- `bds_tested=false`
