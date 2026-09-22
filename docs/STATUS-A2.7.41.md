# A2.7.41 — Oil Press HUD Provider

本批只把 Oil Press 接到 A2.7.39 建立的共享準星 HUD，不新增第二個輪詢器。

## Java 對照

固定 Java 1.1.1 / commit `9a1acdab27698457bec16c9362678e574895a28c`：

- `MachineHud.java` blob `2156ed061b5843618d6929ba5e5aa92aff0688a5`
- `OilPressProvider.java` blob `356e10a5ca536d91e3770c4e6389589214da0813`
- `OilPressBlockEntity.java` blob `c7447be63135f52e15646587226339b3d8036738`

本批 HUD 顯示：

- 油餅 `0/4`
- 壓榨進度 `0/16`
- 附近大缸：不存在 / 流體不相容 / 容量不足 / 可接收
- 大缸目前桶數 `x/8`

## 重點：不重做附近容器掃描

A2.6 已有 `scanVat()`，榨油完成本來就依靠它尋找附近 Big Vat。

A2.7.41 只在同一 runtime 暴露：

`a26ProbePressContainer(block)`

HUD provider 同時復用：

- `a26ReadPress()`
- `a26ReadVat()`
- `a26ProbePressContainer()`

因此沒有：

- 第二套 9×5×9 掃描
- 第二套大缸容量判斷
- 第二套 Oil Press state parser
- provider 專屬 `system.runInterval`

## Bedrock 適配邊界

Java 的 `OilPressContainerApi` 還能對接其他 fluid handler / Create tank。

目前 Bedrock A2.6 真正實作的輸出宿主仍是 Grilling Big Vat，所以 HUD 也只描述 Big Vat；不虛構尚未存在的通用流體容器相容層。

這項仍列為後續 parity 差異，而不是在 HUD 再造一套假 API。

## 未做

下一批仍可直接接同一 HUD registry：

- Big Vat
- Seasoning Bottle

另外 Java 專用整合（Create / Jade / JEI 等）的 Bedrock 對應策略仍需逐項判定，不把「沒有等價 Bedrock API」誤報成已完成。

## 驗證限制

CI / Dash 編譯可驗證結構與打包，但仍不代表真機：

- `minecraft_tested=false`
- `bds_tested=false`
