# Legacy Gameplay-Core Workflows

這個目錄保存 A2.0 ～ A2.7.60 的版本化 GitHub Actions workflow 原檔。

它們在 A2.7.62 起從 `.github/workflows/` 移出，因此：

- GitHub Actions 不再自動或手動註冊這 65 條歷史 workflow；
- 原始 YAML/blob 內容保留，可供版本追溯、比對舊發布流程與事故調查；
- **不得把這些檔案移回 `.github/workflows/` 作為新版本建置入口**；
- 目前唯一 gameplay-core 自動驗證入口是 `.github/workflows/gameplay-core.yml`；
- 新版本只擴充 `development/gameplay_core/verify_current.py` 的 release verifier registry。

之所以直接封存而不是繼續讓舊 workflow 可 dispatch，是因為部分早期 workflow 具有 commit/push 發布步驟。即使只手動觸發，也有把舊生成器結果寫回目前 canonical runtime 的風險。

需要重建舊版時，應在隔離分支／本地環境閱讀對應 YAML 和 `development/gameplay_core/augment_aXX.py`，不要對目前 main 執行歷史 publish 步驟。
