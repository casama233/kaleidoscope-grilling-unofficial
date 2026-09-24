# A2.7.64 Skewer Held Display Parity 候選

目前可交付的 Gameplay Core 以本目錄為 **canonical runtime**：

- `behavior_pack/`：正式 BP；唯一 Script API 入口為 `scripts/main.js`。
- `resource_pack/`：正式 RP。
- `config.json`：bridge. Dash 編譯設定。

`development/gameplay_core/augment_a*.py` 是歷史版本的增量重播／取證工具，不是日常修改後再覆蓋本目錄的預設建置入口。新修正應先落到 canonical runtime，再由通用 release checker、Dash 比對與 deterministic packager 驗證。

A2.7.64 包含 A2.7.63 的調料瓶／Advanced Rack 修正，並完成 39 個 fixed skewer 的 held hierarchy：150 個 bite geometry 改為 `bound root -> display -> shell`，正式 attachable 不再移動 bound root，FP/TP 四組 transform 直接对齐 pinned Java display。玩法、咬合 stage、UV、配方與持久化不變。

完整說明見 `docs/RUNTIME-ARCHITECTURE.md`、`docs/STATUS-A2.7.64.md` 與 `docs/RENDER-AUDIT-A2.7.62.md`。
