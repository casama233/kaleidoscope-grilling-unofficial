# Phase 0：從現行來源封裝

基準：`6fc3ab711e90ae9f23739b18b1f28ef5f31bbf8a`／2.8.114。
本輪已從乾淨固定版本 worktree 封裝一次；沒有執行歷史 generator。

## 正確入口

```sh
git clone https://github.com/casama233/kaleidoscope-grilling-unofficial.git
cd kaleidoscope-grilling-unofficial
git checkout --detach 6fc3ab711e90ae9f23739b18b1f28ef5f31bbf8a
git status --short
GIT_COMMIT=6fc3ab711e90ae9f23739b18b1f28ef5f31bbf8a python3 -B development/gameplay_core/package_current.py --output-dir artifacts/review
```

最小 direct export 只需 Git、Python 標準庫；本輪用 Python 3.12.3。
輸出目錄必須位於 checkout 內，既有 `artifacts/review` 已被忽略。
封裝器會先確認 release baseline 與現行來源，輸出 mcaddon、brproject 和 build report。
本輪輸出 2.8.114 成功，工作區仍乾淨；沒有新版、發佈或 client 驗收。
上面的網路 clone 是可供重現的步驟，本輪實際使用的是共享 Git objects 的新乾淨 worktree。

bridge 使用根 `config.json`。本機 Linux 的 PATH 沒有 bridge `dash_compiler`／`dash.exe`；
`/usr/bin/dash` 是 POSIX shell。本輪沒有本機 Dash compilation。
原候選的 Windows CI 直接下載官方 pinned Dash v1.2.0，編譯 canonical project；
詳見 [gameplay-core workflow](../../.github/workflows/gameplay-core.yml)
與 [bridge workflow](../../.github/workflows/bridge-project.yml)。
本輪 `compiled_export_verified=false`、`bds_tested=false`、`client_visuals_tested=false`；
這些值是這次封裝的範圍，不覆蓋既有家族的 BDS 保存證據。

## 舊入口的真實風險

`development/gameplay_core/build.py` 不是現行建置前置。
其 `main()` 會在讀取來源後刪除 `projects/grilling/gameplay_core`，生成 A2.0.0／Cookery1.0.6，
並把舊 development scripts 複製回該路徑。
`augment_a21.py`／`augment_a22.py` 只是歷史 A2.0→A2.1→A2.2 的手動序列。
補上這兩步也無法重建今日 G114；不得在現行工作區照附件 README 執行。

實際 release 路徑是：

```text
tools/build_grilling_release.py（相容入口）
  → development/gameplay_core/package_current.py
  → baseline / generic / vibrant gates
  → 直接 canonical BP/RP
  → mcaddon / brproject
```

現行 CI 沒有執行舊玩法 augment。
一些素材產生器的 `--check` 是現行驗證中的來源診斷，不能據此說 release 仍疊加 gameplay patches。
正式規則見 [BRIDGE-WORKFLOW.md](../BRIDGE-WORKFLOW.md) 與 [BASELINE-MAINTENANCE.md](../BASELINE-MAINTENANCE.md)。

必要完整性關卡保護來源與部署，不認證玩法／畫面。
本次無需為文檔盤點重跑整套功能或啟動 BDS。
