# A2.8.51 Bedrock 接口與精確 Java-long 運算

完整提供 API v1 的跨包出料、逐堆展示、catalog 別名及可信新生成宿主接口，包含 2.8.50 釘選 Mojang 原版食品辨識。

2.8.50 的隔離原生 BDS 在座標 (2,64,0) 使用 BigInt 計算時與獨立 Java-long 結果不符，因此未部署。此版改用四段 16-bit 整數運算；所有中間值小於 2^35，精確保持 Java overflow、unsigned shift 及 signed floorMod。277 筆獨立 Java 向量包括正負座標、邊界及隨機點；原生方塊探針仍須逐項核對，不能調整預期值讓舊錯誤通過。

包及模組升為 2.8.51，指南 payload 同步 0.3.20，canonical hash／歷史按唯一新版凍結。API ABI 為 v1；Cookery API 0.2.3 及作者身份不變。49／50 的原始 hash、歷史及失敗證據保留。

完整家族 static／BDS／fresh saved-world 通過後按持續授權更新 live。Windows client、真正熔爐宿主與原版自然要塞 callback 仍另行驗收；詳見 [API 契約](BEDROCK-INTEGRATION-API.md)。
