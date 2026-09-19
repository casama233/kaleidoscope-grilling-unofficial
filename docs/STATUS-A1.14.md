# A1.14.0 — 素材入庫、植物外觀與實際 Dash 編譯

本記錄對應 2026-09-19 的已完成遠端工作。唯一寫入目標為 `casama233/kaleidoscope-grilling-unofficial`（ID `1377218440`）。沒有再次修改 Tavern 倉庫、原始 Cookery 安裝包或使用者世界。

## 1. 已入庫，不再只有 notebook

`projects/grilling/` 已包含 A1.12 的 628 份原始來源快照、366 份 `.geo.json`、366 份對應 `.bbmodel`、156 張模型圖集、必要建置與幾何審查工具，以及我方 Cookery 1.0.6 指南章節測試 BP/RP 和 27 張 PNG（含包圖示）。

來源集合、888 份模型／編輯檔／圖集，以及指南 PNG 的路徑＋SHA-256 集合均與實際 A1.12 交付基線完全一致。628 份來源中仍保留原先一份非精確序列化 JSON 的明示例外；沒有改稱每份來源都與上游原始位元組相同。

- 匯入成功工作流程：https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/35451900945
- 集合核對：`migration/result.json`
- 逐候選面向核對：`projects/grilling/reports/migration-verification.json`
- 素材基線 ZIP SHA-256：`5913ef9efd6c434e5a6e77cb24e2fcc4a770a6883f09d3d468d077a069fb5922`

**入庫範圍不是全部歷史附件。** 先前完整 HTML、數千張歷史比對 PNG、全部歷史測試與輔助工具未在本輪全數提交；原交付附件仍是歷史留存。沒有把新的遠端重建冒稱為重跑全部歷史測試。

## 2. 新植物素材

| 素材 | 本輪新增 | 邊界 |
|---|---:|---|
| 魚腥草 | 11 個外觀 | age 0–7，加上 age 5、6、7 的紅色變體；16 組宣告狀態選擇11個外觀 |
| 花椒樹部件 | 4 個外觀 | 樹苗、原木、未結果樹葉、結果樹葉；不是已完成世界生成的整棵樹 |

新增41份來源，累積669份來源記錄。累積381份 `.geo.json`、381份 `.bbmodel`、171張模型图集、116套按座標／尺寸／旋轉去重的幾何。

已核對全部381個候選的有向表面及UV；新增15個候選各8角度，共120對圖片全部一致。A1.12的888份既有輸出、628份既有來源均保持SHA-256不變。舊候選的八角度圖片沒有在本輪全部重繪。

- 成功流程：https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/35452356584
- 結果：`projects/grilling/reports/plants/verification.json`
- 圖片：`projects/grilling/reports/plants/houttuynia-ages.png`、`houttuynia-red-variants.png`、`pepper-parts.png`
- 各角度原始／匯出 PNG：`projects/grilling/reports/multiview/`

### 轉換與失敗記錄

原生參考模板的預設完整方塊UV已顯式化；花椒樹苗的Java rescale在旋轉前按原樞軸烘焙，沒有直接忽略。缺少rescale的反例能被檢查捕獲。

第一輪流程35452210154在樹苗透明交叉面的圖片比较處失敗，未提交新素材。對稱面深度計算的浮點尾差造成前後繪製順序不穩定；僅把透明片段的排序鍵取至1e-9模型單位，沒有改真正頂點、深度緩衝或圖片允許誤差。再次執行後120對零像素差。幾何容差仍是1e-7，圖片容差仍是0。

樹葉原始tintindex被獨立記錄為待材質接線，本次預覽是**未套用生態域染色的來源參考**，不是最終遊戲葉色。相鄰面剔除、透明排序的Minecraft表現，以及作物生長、採集、掉落、樹木世界生成仍未驗收。

來源與匯出使用獨立解析路徑，但共用離線相機與光柵器；自動比對不是Minecraft實機驗收，也不等於逐張人工視覺檢查。

## 3. 真正 bridge. Dash CLI 已編譯成功

在 Windows GitHub Actions 執行 bridge. 官方獨立 Dash v1.2.0；下載可執行檔的SHA-256與官方release資產摘要一致。

工作流程：https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/35452461036

| 實際步驟 | 結果 |
|---|---|
| 主素材RP執行 `dash.exe build` | 成功，編譯器記錄554個檔案 |
| 指南BP/RP執行 `dash.exe build` | 成功，編譯器記錄34個檔案 |
| 主RP JSON結構／PNG對照 | 553個範圍內檔案一致 |
| 指南RP JSON結構／PNG對照 | 27個範圍內檔案一致 |
| 指南BP JSON結構／PNG／JS對照 | 5個範圍內檔案一致 |

編譯器總檔案數與比較數不同，是因為比較程式只納入JSON、PNG、JS；其他檔案不灌入比較數。這些是資源搬運／編譯输出一致性，不是全Bedrock語義schema或遊戲功能驗收。

`development/verify_dash_outputs.py`先按原UUID找到實際編譯包，再對比，沒有用來源目錄假裝編譯目錄。`verification.json`中較早的`bridge_tested:false`保留其原測試時點；此後新增的Dash流程才是CLI編譯證據。**bridge.圖形介面匯入、Minecraft客戶端、BDS與真實渲染仍未驗收。**

## 4. 指南與筆記

仍維持森羅物語原指南內的一個煙火章節，不新增書物品、不覆蓋宿主。A1.12章節發布器及內容保持原樣，未宣稱新植物已在指南中增加新頁面。

根目錄`notebook/`保留A1.13 Recovery的玩家獨立搜尋、收藏與自訂配方資料核心；27項模擬玩家儲存測試已在GitHub Actions成功執行（35450471711）。**原書內的動態搜尋、收藏按鈕、自訂配方編輯回調與跨世界重啟儲存仍未接通。**

## 5. 下一批缺口

- 餐盤本體與1–5串擺放、姿態及相應引用的授權／來源確認。
- 自由組合串的實際部件、組合外觀與動態配色，不能用固定串或通用棕色模型冒充。
- 液面／流動／粒子，原點與自發光材質；油餅與油的流體行為分開驗收。
- 第一／第三人稱、主／副手、地面掉落姿態，以及不同食用、刷油、調味、翻面動作。
- 指南動態頁面接線、自訂配方儲存、完整加工配方與多人遊戲驗收。

本批没有宣稱全模組素材或玩法已完成，沒有新增可遊玩完整mcaddon。
