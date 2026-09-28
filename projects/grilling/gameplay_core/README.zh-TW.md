# 森羅煙火 A2.8.8 Local Review

這是本地候選版，不是已發布版本，也未部署至任何伺服器。
基線為 A2.8.7，GitHub commit `707d28edab4ea9af76878e0e29d8244848971db3`，
workflow run `36373807017`、artifact `10950386970`。

本輪實際修改：嚴格處理手持寫入失敗、穿串／拆串／烤架放串／調料瓶同步操作的最佳努力回滾、
延遲穿串的雙手與槽位快照、熱串整理先規劃再寫入、停止烤架無變化狀態重寫、顯示佇列同輪去重、離線暫存清理。

UUID、內容 ID、存檔 key、原料理規則與熱度分組、Cookery 1.0.6 依賴未更換。
沒有重製手持／透明材質、沒有新增指南書、沒有修改指南目錄、創造欄或配方資料。

## 驗證

在此目錄執行 `python review/validate_candidate.py`。需要 Python 3.10+ 與 Node.js；不下載依賴。
只做 JSON／JavaScript／引用／manifest／來源差异檢查及三個純演算法模組測試。
不模擬玩家，不啟動 Minecraft／BDS；也不把這些檢查當作手機渲染、多人生存或效能量測。
完整 repository 的既有 gates 與官方 Dash 應在整合分支繼續執行；這次未聲稱它們對候選版通過。

## 導入

只能先在備份世界或新測試世界導入候選 `.mcaddon`。
本候選依賴官方 Cookery 1.0.6 的 BP/RP UUID，不是帶有私人 UUID／補丁的伺服器整合包。
保留舊 pack UUID 代表 Minecraft 可能把候選視為更新而覆蓋同 UUID 的舊包；導入前請保留原包與世界备份。
完整回退方式是恢復備份的世界與 A2.8.7 原包，不能保證匯入較低 manifest 版本即可自動降版。

詳細根因、改動與未驗證邊界見 `review/CHANGELOG.zh-TW.md`。
原工程 README 原文保存在 `review/baseline-README.zh-TW.md`，原 reports 亦保留作歷史記錄，並非本輪驗收結果。
