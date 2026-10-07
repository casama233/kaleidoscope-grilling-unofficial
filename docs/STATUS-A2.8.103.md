# G103 烤串背包與指南圖示

修正未完成串與秘製串的原生背包圖示：舊產生器把 Java 的 `secret_skewer_stick.png` 三維模型 UV 圖集當成物品 sprite。空籤現在直接使用原作 16×16 GUI `stick.png`；完成籤以同一 GUI 竹籤及 `food_3_1` → `food_2_1` → `food_1_1` 遮罩合成，直接套用兩分支 `SkewerColorProvider.FALLBACK = 0xB86B45` 及原作 `applyMaskTone` 明暗規則。

來源為 breezeth-CN/KaleidoscopeGrilling `9a1acdab27698457bec16c9362678e574895a28c` 的既存公開 fixture。圖像素材由 breezeth／Kaleidoscope Official Production Team 提供，授權 CC-BY-NC-SA-4.0；本版完成籤圖示為依此授權改作。空籤素材位元組不變。`tools/build_skewer_inventory_icons.py --check` 重建檢查兩張 native sprite，歷史 `augment_a24.py` 也使用相同產生器。

固定完成籤是來源支持的代表性 fallback，作為明列的原生平台替代；不是紅蘿蔔配方預覽，也不是實際食材平均色。原作按每個物品食材數量、三份獨立顏色、熟食及隨機 variants 更新背包圖示的能力仍未實作／未驗證。本版不宣稱完成動態 GUI 還原或完整 Java 一比一。

物品身份及 icon routes 沿用既有定義；手持模型 UV、食材 metadata、染色、食物、配方與穿串流程不變。兩個 focused 圖示檢查涵蓋空籤來源、三份食材遮罩與前後覆蓋順序，以及 unfinished／三個 secret 身份的原生 icon route。

PR／CI 與部署結果由各自收據記錄，來源圖示並非真人渲染驗收。完整家族 static／BDS／存檔預檢與 live 部署仍各有證據邊界；在取得本版真人客戶端驗收前，維持 `client=false`、`production_ready=false` 與 `pending_client_acceptance`。

指南 catalog 0.3.34、傳輸 payload、兩張指南圖示及來源記錄同步至新 sprite。G102 已凍結但在遠端指南來源檢查失敗，未部署；保留其 release-history，最終候選另用 G103，沒有重用版號。
