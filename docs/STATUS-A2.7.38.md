# A2.7.38 — Shared Oil Contract

本批先完成 typed oil 顯示審查，再處理審查中暴露出的重複實作。

## Java 顯示契約

固定 Java 1.1.1 source：

- `OilPotCompat.java` blob `4264ab947a4222784151fbd50ae84a1a8037d491`
- `OilPotBlockMixin.java` blob `7d76cdb8e47203b42ae66c0aef99f3c7fc1d1800`
- `ClientSetup.java` blob `227d21a500f284cec1f2061ffa935457051e4596`
- `OilPotHud.java` blob `40c6f7e19c50d3081a16c8c93b3cfc06f0db532d`

Java 的 typed oil pot 顯示依賴：

1. 向 Cookery OilPotBlock 注入額外 `OIL_TYPE` block state；
2. 向 Cookery oil-pot item 註冊 `kaleidoscope_grilling:oil_type` item model property；
3. 準星指向油壺時渲染專用 HUD；
4. JEI display stack 才會調用 `nameForDisplay` 取得油種名稱。

### Bedrock 邊界

Bedrock 附屬 BP 不能安全地向另一個 BP 已定義的 `kaleidoscope_cookery:oil_pot` 追加自訂 block state。

因此 A2.7.38 **不**：

- 複製一個 Grilling 專用油壺 block；
- 用第二套 item ID 冒充 Cookery 油壺；
- 為三種顏色重做一套平行容器生命週期。

這些視覺差異留給之後的共享 host-visual adapter；準星 HUD 也應與 grill / press / seasoning 等一起進共享 HUD 層，而不是油壺各自建立輪詢框架。

## 本批真正修正：油契約去重

新增純邏輯單一來源：

`a2738_oil_contract_core.js`

唯一保存：

- Cookery fat capacity：`256`
- Grilling typed-fluid capacity：`64`
- 每個 Grilling 油桶：`8` 點
- typed oil：`canola / secret_chili / premium_chili`
- oil type normalization
- capacity lookup
- bucket ID → oil type lookup（由呼叫者現有 registry 推導）

### 收束的消費者

- A2.4 skewering oil helpers
- A2.7.34 Cookery oil-pot core
- A2.7.36 placed Cookery typed-oil-pot bridge
- A2.7.37 offhand item fill

A2.7.36 原本自己硬編的三個 bucket ID registry 已移除，改為直接使用 `a23_oil_world.js::OIL_TYPES`。

A2.7.36 / A2.7.37 也不再各自硬編 `8` 或 `64`。

## Server Edition

目前 `tools/build_server_edition.py` 已同時包含歷史 `a2730` 與正式 `a2734_cookery_oil_pot_adapter.js` 的 itemData rewrite entry；不存在 adapter 改名後漏 rewrite 的缺口。

## 驗證

CI 驗：

- A2.7.37 published baseline；
- pinned Java display/typed-oil contract；
- pinned Cookery 1.0.6 host contract；
- shared pure core；
- 四個既有 oil consumer 是否真的引用共享契約；
- A2.7.36 runtime 不再含第二份 bucket registry；
- Dash 真編譯 + source/output compare；
- mcaddon / brproject 打包。

仍不宣稱真機測試：

- `minecraft_tested=false`
- `bds_tested=false`
