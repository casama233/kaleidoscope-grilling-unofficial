# A2.8.50 Bedrock 接口與原生食品

交付 [跨包接口 v1](BEDROCK-INTEGRATION-API.md)：实际出料核對、公開逐堆 data、展示註冊、確認回覆、重啟與有界防重播收據，以及可信新生成宿主接口。所有 2.8.48 聲畫、進食、指南與原生龍血修復保留。

獨立 BDS 的 2.8.49 候選發現可疑燉湯等原版食品沒有 scripting food component，出料接口錯誤拒絕；49 收據與 release-history 保留，未部署。50 改用既有釘選 Mojang 原版食物定義；data-driven 食物仍讀 native component，非食物拒絕，沒有私人資料／tag 推斷。新增回歸使用沒有 food component 的 vanilla 物品，避免替身誤認成原生證據。

包及模組升為 2.8.50，指南 payload 同步 0.3.19，canonical hash／歷史按唯一新版凍結。API ABI 仍為 v1，Cookery API 0.2.3、作者 UUID／hash 和第三方原包保持既有契約。完整家族 static／BDS／fresh saved-world 通過後按持續授權更新 live；Windows client 仍另行驗收。

原版要塞與熔爐仍缺少可靠的生成／取料宿主 callback；接口可實際呼叫，不冒稱已自動覆蓋原版。新的圖像／動態 GUI 及 Java 選用模組也不由此接口自動提供。
