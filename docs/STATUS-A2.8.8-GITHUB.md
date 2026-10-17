# A2.8.8 Local Review：GitHub 整合紀錄

## 原始碼回傳

使用者要求將上一輪本地候選成果上傳回 GitHub。本次僅整合至 `codex/grilling-a288-local-review`，不直接更新 `main`、不建立 Release，也不部署伺服器。

- 凍結基線：`707d28edab4ea9af76878e0e29d8244848971db3`。
- 精確原始碼匯入提交：`fae9a0cdb434ec3e1ec08e948fe9e7652ce39923`。
- 25 個交付檔案均先核對原檔 SHA-256，再核對套用結果 SHA-256。
- `verify_current.py` 先核對原 git blob，再登記 `(2, 8, 8): verify_a288_local.py`；保留 A2.8.7 既有 gates。
- 由凍結提交重建 1,905 個 BP/RP 原檔雜湊，產生的基線清單與本地交付清單 SHA-256 完全相同。
- 傳輸過程對 `a23_hot_runtime.js` 暫時轉為 LF 套用文字差異，隨即恢復交付檔的 CRLF；最後仍以原交付 SHA-256 驗證，沒有更改其程式內容。
- 本提交移除一次性匯入 workflow 與傳輸分片，最終差異不保留它們。

## 驗證範圍

`STATUS-A2.8.8-LOCAL.md` 與 `projects/grilling/gameplay_core/review/` 內報告是**本地交付時的歷史快照**。當中的「未推送／完整 CI 未執行」描述該快照的狀態，不應當作後續 GitHub 工作流程的即時結果。

精確檔案匯入已完成；既有 `Grilling Gameplay Core — Canonical` CI 的結果以本 PR 對應的實際 Actions run 為準。只有該流程成功後，才能聲稱原始碼 gates、官方 Dash 編譯及 compiled/source 比對通過。

測試包由現有 canonical workflow 從本 PR 原始碼重新建置，輸出至 `Kaleidoscope-Grilling-Canonical-Review` artifact；未將本地候選 ZIP 冒充為已通過 GitHub CI 的 Release。

此回傳操作沒有進行 Minecraft 客戶端、Android、BDS、多人生存或效能驗收。UUID、內容 ID、存檔 key 與官方 Cookery 1.0.6 依賴沿用原交付版本；私人伺服器依賴重綁不在本次上傳範圍。
