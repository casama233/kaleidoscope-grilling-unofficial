# A2.8.45：熱食結算、共享吃法與原生龍血生命

完成六種料理食用时，重查權威 hotUntil，避免開始還熱、完成已冷卻卻獲得熱食加成。THREE_RANDOM 每次只選一次分支並同步玩家 eat_profile、eat_hand，使各手附件的曲線與咬點對應同一服務端狀態；未使用的手不跟著消失食材。

龍血以原生 minecraft:health component groups 提供 26／30 最大生命。初次補 6／10、升級只補差額 4、同級刷新不再次治療，到期／奶／重生恢復 20，後續傷害與反覆治療由引擎處理。Mojang 1.26.30 玩家 JSON 以 commit／hash 釘選，生成器證明除自有 namespace 的 properties／groups／events 外原版內容完全相同；不新增 RP player replacement。完整家族組裝必須拒絕另一份 BP minecraft:player，避免依排序暗中互相覆蓋。

秘製串新增三個獨立手持食材槽，主副手各保存三個索引，共登記 213 個已知原版／自有／Cookery 食物圖示。只引用作者貼圖，沒有複製第三方私有檔案；採穩定雙面 cube 切片，不要求 texture_mesh 實驗。食材未知時保留竹籤及已有 lore，不猜測一張錯誤圖示。Native 背包 GUI 仍為固定圖示；原作 tint／幾何、未登記第三方食物與 Java 第二截模型尚未完整等價。

BP／RP／module／pair dependency／baseline／release history 同步 2.8.45，保留 canonical 2.8.42 效果快取及 2.8.43 原生第一人稱框架修復。本輪先前未合併的 local 2.8.43 與 canonical 2.8.43 發生併行身份衝突，已撤回 local 身份；commit、兩組 hash 與開發證據保留，不把不同 bytes 標成正式 2.8.43。本輪 2.8.44 候選保留開發用途，合併後以新 2.8.45 重新驗證。秘製串以 7 個共享幾何選擇 213 張已知圖示，避免重複模型；指南／Cookery API 仍維持未變更的 0.3.14／0.2.3。

版本驗證包含全部既有回歸、兩手／兩視角的兩條隨機分支及未使用手檢查、原版玩家保留、生成重現、熱度邊界與額外治療規則。BDS 零玩家探針與全家族載入／重啟各自留證；Windows 真人心形、奶、死亡、聲畫與多人結果另記。完整未閉合範圍見 [當前矩陣](CURRENT-REPAIR-STATUS.md)，不得寫成「全部細節已修好」或正式已部署。
