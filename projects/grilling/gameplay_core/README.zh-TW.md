# A2.7.63 Held Display Parity Batch 1 候選

目前可交付的 Gameplay Core 以本目錄為 **canonical runtime**：

- `behavior_pack/`：正式 BP；唯一 Script API 入口為 `scripts/main.js`。
- `resource_pack/`：正式 RP。
- `config.json`：bridge. Dash 編譯設定。

`development/gameplay_core/augment_a*.py` 是歷史版本的增量重播／取證工具，不是日常修改後再覆蓋本目錄的預設建置入口。新修正應先落到 canonical runtime，再由通用 release checker、Dash 比對與 deterministic packager 驗證。

A2.7.63 包含 A2.7.62 的 Big Vat corrective，並開始清理 Render Audit 揭露的手持 display parity：三種調料瓶把 Java FP/TP transform 套到安全的 child `display` bone；Advanced Rack 新增專用 held attachable 並套用 Java 明確存在的 FP-right / TP-right / TP-left transform。玩法、容量、互動與持久化格式不變。

完整說明見 `docs/RUNTIME-ARCHITECTURE.md`、`docs/STATUS-A2.7.62.md`、`docs/STATUS-A2.7.63.md` 與 `docs/RENDER-AUDIT-A2.7.62.md`。
