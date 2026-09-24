# A2.7.62 Big Vat Render Corrective 候選

目前可交付的 Gameplay Core 以本目錄為 **canonical runtime**：

- `behavior_pack/`：正式 BP；唯一 Script API 入口為 `scripts/main.js`。
- `resource_pack/`：正式 RP。
- `config.json`：bridge. Dash 編譯設定。

`development/gameplay_core/augment_a*.py` 是歷史版本的增量重播／取證工具，不是日常修改後再覆蓋本目錄的預設建置入口。新修正應先落到 canonical runtime，再由通用 release checker、Dash 比對與 deterministic packager 驗證。

A2.7.62 包含 A2.7.61 的 runtime hygiene，並針對實機回報補上 Big Vat 渲染 corrective：世界模型改用四條實體頂圈、主 shell 改為 opaque，移除透明洞邊緣漏草地的成因；手持則新增穩定 attachable，真正套用 Java first/third-person display transform。玩法、容量、流體與持久化格式不變。

完整說明見 `docs/RUNTIME-ARCHITECTURE.md`、`docs/STATUS-A2.7.61.md` 與 `docs/STATUS-A2.7.62.md`。
