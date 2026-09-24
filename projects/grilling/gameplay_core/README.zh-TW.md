# A2.7.61 Runtime Hygiene 候選

目前可交付的 Gameplay Core 以本目錄為 **canonical runtime**：

- `behavior_pack/`：正式 BP；唯一 Script API 入口為 `scripts/main.js`。
- `resource_pack/`：正式 RP。
- `config.json`：bridge. Dash 編譯設定。

`development/gameplay_core/augment_a*.py` 是歷史版本的增量重播／取證工具，不是日常修改後再覆蓋本目錄的預設建置入口。新修正應先落到 canonical runtime，再由通用 release checker、Dash 比對與 deterministic packager 驗證。

A2.7.61 不改 Java 烤架操作規則；除了減少空閒烤架與榨油器 registry 的無效寫入，也補上盤子／食譜／榨油器／大缸的一次手勢去重、主副手 intent 與 deferred revalidation。烤架下方支撐造成的 legged 狀態仍每 tick 同步，因此沒有用效能優化換掉 Java `updateShape` 對支撐變動的語義。

完整說明見 `docs/RUNTIME-ARCHITECTURE.md` 與 `docs/STATUS-A2.7.61.md`。
