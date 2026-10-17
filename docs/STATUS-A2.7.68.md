# A2.7.68 — 靈動視效宣告與成品防回退

基於現行測試分支 A2.7.67（4d02ce29331968fae73dd7c32841ac962c4ffbb5）。本次僅修改 BP/RP 的版本／名稱、相互依賴，以及 RP 的 `capabilities:["pbr"]`；全部非 manifest 遊戲資源維持 A2.7.67，含大缸材質、八份配方 unlock、穿串、手持與指南修正。

## 根因

酒館倉庫 `docs/VIBRANT-VISUALS.md` 記錄 BSM 更新覆蓋伺服器端 PBR 修補。公開煙火 A2.7.67 的 canonical RP 本身仍未宣告 pbr，重新下載便會再次丟失該宣告。不是再改亮度、MER 或魔法輪盤圖片即可解決的問題。

## 修正

- 在真正打包的 `projects/grilling/gameplay_core/resource_pack/manifest.json` 補入 pbr，不只修改安裝目錄或舊生成器。
- BP、RP、所有 modules 與 BP→RP 依賴同步升至 2.7.68，保留所有 UUID、Cookery 1.0.6 與 Script API 2.9.0／2.2.0。
- 保持最低引擎 1.26.50，已高於 Microsoft PBR 規則的 1.21.120；不任意提升所有第三方包的引擎版本。
- canonical verifier 及打包入口均檢查 PBR、最低版本、modules 與相依；打包前比對真實 Dash 輸出，打包後再次核對 archive manifests，拒絕陳舊或被重新生成的 manifest。
- 延用 A2.7.67 的全部資源／語義鎖，新增 8 個 manifest／匯出資料測試。未增加模擬玩家測試。

## 邊界與部署

PBR 宣告不等於完成逐像素材質設計或手機渲染驗收，也不能修好不支援的硬體、其他包的 HUD 或缺圖。本次沒有啟動 Minecraft 客戶端或 BDS；現有伺服器完整堆疊不在本次來源審核中。

使用完整 2.7.68 BP/RP 成對更新。伺服器的 world_behavior_packs.json、world_resource_packs.json 及已驗證相容的入向依賴需同步；不要把任何任意前置版本自動改成最高安裝版。私服 Cookery 1.0.7／UUID 重綁與第三方補丁仍須在私有整合流程保留，不納入本公開包。

官方規則：https://learn.microsoft.com/en-us/minecraft/creator/reference/content/mctoolsvalreference/chkmanif?view=minecraft-bedrock-stable （CHKMANIF134）。
