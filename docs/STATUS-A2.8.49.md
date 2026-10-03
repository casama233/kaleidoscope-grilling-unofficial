# A2.8.49 剩餘 Bedrock 接口

此版為未部署候選。原生 BDS 發現 vanilla 食物不公開 food component 而錯誤拒絕出料；已由 [2.8.50](STATUS-A2.8.50.md) 使用釘選 Mojang 定義修正。49 的原始 hash／歷史及失敗證據保留，不把它宣稱為驗收通過。

跨包出料現在可核對指定的實際食物並寫入公開 tick 期限／調味／逐堆 data；來源持久註冊與有界序號收據讓重播不再加熱。展示 provider 與現有手持 catalog 別名可跨 BP 註冊，重啟重新驗證。作者可用附帶的 client／stack SDK，保留原生物品與自己的交付流程。

自然生成宿主可提交可信的新要塞區塊 bounds／wart 座標，使用 Java 原哈希的 25% 選取、紅色與年齡映射；拒絕過期、範圍錯誤、變動資料、真人碰過的區塊及未解決操作。**原版要塞仍没有可靠 callback；自動自然替換未完成。** 新圖像、GUI tint、CapsLock 和 Java 選用模組仍有平台／宿主界線。

詳細契約、實例與限制見 [Bedrock Integration API v1](BEDROCK-INTEGRATION-API.md)。Java 熔爐熱食設定補齊 false／30 秒原預設，由真正 producer callback 呼叫，不猜測背包增加。既有 Cookery API 0.2.3、UUID、原作者 hash 登記、全部 2.8.48 修復保留；這不是第三方翻譯覆蓋。

包／模組為 2.8.49，指南 payload 同步 0.3.18；runtime hash 與 release-history 以 canonical gate 凍結。source 測試與 native BDS／saved world／Windows 分開記錄。live 開發更新必須先合併 PR 及完整家族准入；client=false 時 production_ready=false。
