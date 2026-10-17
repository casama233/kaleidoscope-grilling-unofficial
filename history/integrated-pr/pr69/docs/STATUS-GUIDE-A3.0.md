# Guide A3.0 — 內容重做記錄（現已內建煙火）

**安裝說明已修正：A3 是指南內容版本，不是另一個 addon。自煙火 A2.7.65 起，全部指南內容直接在煙火既有 BP／RP 中，顯示於 Cookery 原指南的煙火附屬章節。**

上一版將指南獨立打包、要求額外啟用 BP／RP 的交付方式是錯誤的，現已停用。
只保留「Cookery 本體＋煙火（含指南）」安裝關係。新狀態及檢查見 `docs/STATUS-A2.7.65.md`；舊包、舊 workflow 與取證資料封存於 `history/standalone-guide-a3`，不作發布入口。

## 保留的內容改進

由五個教學章節改成按物品查找的百科，module ID 保持 `kg_a1:grilling`。
實際核對 Cookery 基岩 1.0.6 的指南、語言資料與擴充接口；分類不是按 Java 百科臆造。
本體指南 UI 檔 SHA-256：`acff33eec87add1c149aff3789b1b9ec62dd1ef642a5bc7d2b2f1b70dd6332ff`。
本體原始 archive SHA-256：`c589efb60277bea295ac12ef760d8f2c7e8af3ea62e809b320862bd786033351`。

六個有內容的頂層分類：工作站、食物百科、工具與裝備、儲存與實用功能、耕作與收成、進度與指南物品。
食物按燒烤架、手工穿串、炒鍋、湯鍋、合成與加熱、砧板加工、磨石加工、食材與其他食物八組查找。

76 個唯一條目涵蓋 88 個非歷史油刷 item；19 組生熟烤串合頁，三種調料瓶狀態合頁。
同一物品可在不同製作分類找到，但只保存一份 entry；取得、用途、操作、配方與效果留在同頁。
77 個配方變體保留替代材料，穿串保留順序，工作台有序配方保留九宮格，不錯寫成任意擺放。
69 張物品／植物圖標按真實 BP icon、RP atlas 和 PNG 核對；其他分類及設備使用已有預覽圖。

## 內容限制仍如實保留

未核實的首份取得路徑不以 Java 配方冒充已實裝；包括初始空瓶的說明。
酸辣粉保留酒館醋的依賴，喜糖保留活動日期。
未修正的 Cookery 1.0.6 Guide API 可回退為繁中正文；本次不覆蓋本體，也不要求另一個相容 addon。

## 現行來源与檢查

唯一編輯源：`projects/grilling/guide/catalog.a3.json`。
`tools/build_grilling_guide.py` 輸出到完整煙火 `gameplay_core`；`tools/check_grilling_guide.py` 核對內容與內建交付約束。
發布只使用完整產品 `tools/build_grilling_release.py`。
分類索引：`docs/GUIDE-INDEX-A3.md`。

資料檢查涵蓋分類可達性、88 個物品、20 組固定串、15 組 Cookery 精確加工註冊、營養及圖標來源；Script Event 純資料編碼為 208 則，最長 1638 字元。
沒有模擬玩家互動；資料、語法、Dash 與 ZIP 核對不能代替實機表單排版和觸控驗收。
