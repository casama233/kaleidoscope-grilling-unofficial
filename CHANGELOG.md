# 維護變更

## 2.8.116：保留前方花／藤的互動目標

承接115的餐盤營養與防誤食修補，視線查詢明確保留passable block輪廓，
避免盤子在花／藤後面時攔錯目標；液體設定維持Java Fluid.NONE對應。
包／模組／配對依賴116、guide0.3.46及兩個bridge輸出名称同步。
115維持原frozen身份與失敗CI記錄，未合併／部署，不重用該身份。
[來源、界線與LIVE場景](docs/STATUS-A2.8.116.md)。

## 2.8.115：餐盤營養與插串誤食

在hunger寫入後刷新saturation並尊重原生界限，避免餐盤獎勵因舊view回滾；
仲裁盤子與item-use，防止插串後誤吃剩餘串，保留合法使用與較近entity互動。
只沿用受影響既有檢查；guide身份同步0.3.45，其他配方、UUID與現行修補保留。
[來源、證據界線及真人場景](docs/STATUS-A2.8.115.md)。

## 2026-10-08：建置、驗證與文件重整

本輪是工具與文件調整，canonical BP/RP、UUID、相依及 release-history 沒有變動；
遊戲版本保持 2.8.114，無需建立新遊戲候選或重啟 LIVE。

- 舊 A2.0 `build.py` 預設拒絕執行，必須明確指定全新、位於 Git 工作樹外的歷史輸出；移除刪除現行 gameplay_core 的路徑。現行 release 仍直接封裝 canonical packs。
- 將兩個帶主幹寫入步驟的歷史 localization workflows 移至 `docs/legacy_workflows`，不再作為 Actions 入口。66 個舊 augment 保留原版本 gate；它們仍是歷史工具，未宣稱整條舊生成鏈可隔離重建現行版本。
- 當前 CI 的同一次來源驗證只執行一次四組重複工作：熱食合併、調料原生儲存、瓶子第一人稱來源檢查、進食動畫產物檢查。只有成功且命令／目錄／環境相同的工作可重用；失敗不記錄成功。歷史獨立 verifier 保留原行為。
- README 改為現行使用入口；Java 狀態集中在 [PARITY-MATRIX.md](docs/PARITY-MATRIX.md)，具體問題在 [BUGS.md](docs/BUGS.md)。完整舊敘述留在 Git 歷史，Phase 0 報告保留原快照。
- 維護規則明訂優先重用既有檢查，本機針對性診斷、完整必要套件交 CI；新測試須有具體未覆蓋故障，文件整理不新增測試。

此重整不修復餐盤、任意食材 GUI 或完整進食聲畫，不代表 Java 一比一驗收完成。
未合併功能與調料 registry 原型保留，處置依 [PR 稽核](docs/audit/PR-TRIAGE.md) 逐項決定。

## 歷史版本

包版本的正式身份以 [release-history.json](release-history.json) 為準；
每版範圍見 `docs/STATUS-A*.md`。
[重整前 README](https://github.com/casama233/kaleidoscope-grilling-unofficial/blob/6fc3ab711e90ae9f23739b18b1f28ef5f31bbf8a/README.md) 保留歷史開發與有限驗收記錄。
不要把舊候選的測試、部署或真人觀察沿用成現行全部功能通過。
