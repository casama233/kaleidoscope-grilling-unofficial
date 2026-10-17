# 歷史生成器的使用界線

現行 release 直接封裝 `baseline.json` 指向的 canonical BP/RP：

```sh
python3 development/gameplay_core/package_current.py --output-dir artifacts/review
```

`development/gameplay_core/build.py` 是 A2.0／Cookery 1.0.6 的歷史重建器，不是現行建置入口。沒有明確輸出參數時，它在讀來源、取上游或寫檔前拒絕執行。若需要研究舊產物，必須指定全新的絕對路徑，且不得位於任何 Git checkout／worktree 內：

```sh
python3 development/gameplay_core/build.py --legacy-output /tmp/grilling-a2-legacy-new
```

此命令會讀取鎖定的舊上游與本機歷史素材。輸出只供歷史研究，不能用作現行 release／家族候選／部署來源。既有目錄一律拒絕；重建器不再刪除輸出。上游或生成失敗可能留下不完整目錄，下一次應另選新路徑。

66 個 `augment_*.py` 保留原前版 report／manifest 身份檢查，G114 會在修改前被拒絕；它們沒有隔離輸出參數。部分會呼叫 `ROOT/tools` 的其他生成器，因此不能只改 `P/BP/RP` 或把舊輸出複製回 canonical 來接續。這輪沒有把整條歷史 augment 鏈改造成安全的隔離重建工具，也沒有變更供驗證器匯入的 helper 函式或現行 `--check` 素材工具。

兩個舊語言自動寫入流程已移到 `docs/legacy_workflows/localization-a2728-a114.yml` 和 `localization-a2729-a115.yml`。它們保留歷史內容供閱讀，已不在 GitHub 可執行的 `.github/workflows` 中。現行 release 與 CI 不透過這兩個舊增補流程。

這些工具／文件修補不改 canonical runtime、版本、UUID 或 release history，無需升包或重啟 LIVE。來源、發版、候選、備份、遷移及部署的完整性關卡保持原流程。
