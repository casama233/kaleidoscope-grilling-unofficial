# A2.8.29 — storage-derived grill contents

## 已實作

烤架三格現在由權威原生容器衍生顯示，每一格保留原槽位，空格不重排。19 種固定烤串有原版六段烹調貼圖；生串、上油／翻面、烤熟與焦黑由現有爐狀態同步。翻面顯示使用 Java 的 700 毫秒、每次 180 度轉動與 0.28–0.38 格跳起範圍。跳起高度以槽位／位置種子重建，未宣稱與 Java RandomSource 的每個亂數相同。

Java 1.1.1 發行 JAR 的 SHA256、260 個使用到的原版模型／貼圖及逐檔 SHA256 記錄在 `development/gameplay_core/fixtures/released-grill-1.1.1/source-manifest.json`。爐面 mesh 由當前 canonical 完整烤串 geometry 去掉手持綁定，沿用既有 UV 與立方體轉動；114 張烹調 atlas 由原版貼圖組合，並以 RGBA 比對確認欄位。未更改手持骨架、方塊身份或原版 Cookery 文件。

渲染實體為 transient，沒有物品欄。新增只讀 `peekStationContainer`，不建立容器、不重綁擁有者、不寫入食材；隔離或不可讀資料使顯示清除。每五 tick 更新鄰近玩家的顯示，最多 1024 個 helper；離開、破壞、區塊卸載與腳本重載會回收 helper，並保留 backing inventory。新世界沒有真人玩家時不建立常駐顯示。

版本同步至 BP／RP／模組／相互依賴、baseline、bridge 工程名稱及指南 payload 0.3.7，並追加 release history。接續已合併 PR #99 的 A2.8.28 音效與指南修復；其差異已保留。

## 驗證

完整來源檢查通過；新增 10 個回歸情境涵蓋所有固定烤串階段、空槽、四向位置、狀態變更沿用 helper、可見範圍、卸載回收、顯示失敗及只讀儲存。隔離家族 BDS 載入、原生 property／metadata 與重啟證據將另行記錄。腳本與 BDS 驗證不能代替真人畫面。

## 尚未結案

- 秘製串目前僅使用原有物品圖示；依食材組成的個人化 3D 外觀仍缺少。跨包自訂生串的 world mesh 尚未有註冊合約。
- 廚具架的實際工具與餐盤內容仍待下一批顯示修復。
- 翻面方向、貼圖可讀性、遮擋、光影與客戶端 frame timing 需要 Windows／觸控真人驗收。
- 生產仍是 A2.8.21。本批不具備新候選的真人客戶端與完整舊存檔遷移證據；不得重用先前收據的延期驗收批准或直接覆寫正式包。
