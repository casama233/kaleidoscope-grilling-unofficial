# A2.7.67：伺服器差異清單追查

對照 `docs/STATUS-A2.7.14-SERVER.md` §5、§11、§12 與使用者 2026-09-25 的新 Content Log。該舊文件是多輪私服部署歷史，不表示全部舊 shim 都應再複製進公開包。

## 已直接修入本輪來源

來源基線為正在發行 A2.7.66 測試包的 `refactor/canonical-runtime-interactions-20260924`，commit `b2e575cd8c1687e6ec6165c6c7f30f3b38a20a44`。不是用 main 的舊 A2.7.60 runtime 覆蓋它，也不因此合併整個尚在審核的 PR #70。

1. 八份工作台配方：oil_press、advanced_rack、oak_planks_from_pepper_log、big_vat、secret_chili_oil、pepper_honey、oil_cake、sugared_tomato。各加一個來自實際材料的 unlock，材料、數量、形狀、輸出完全不變。熔爐配方不硬塞 unlock。
2. 大缸 `big_vat.json` 的六份宣告材質表確實同時使用外殼 alpha_test 與 fluid blend。統一為 blend，保留水與油透明度、原本貼圖、光照旗標和幾何。有效 base/permutation 共 11 組受影響，不將此計數冒充舊日誌 26 筆警告的一一對應。
3. 新增 A2.7.67 verifier：23 個方塊、133 組材質配置、72 個 block_placer 引用及全部 8 份工作台配方檢查；另外逆向扣除九份資料檔的授權改動後，核對 1,239 個非 manifest runtime 檔的正規化內容雜湊，防止其他遊戲、腳本、美術、存檔格式被改動。

## 未擅自改動／尚待查證

- 私服 Cookery UUID 改接屬部署差異，公開包仍依賴官方 Cookery 1.0.6，不寫死私服 UUID。
- 舊版 itemData、支撐判斷、before-event 延後、油流 unloaded 區塊保留、指南等伺服器 adapter 沿用既有部署處理；本次沒有宣稱它們全數被公開本體吸收，也沒有移除部署需要的 adapter。
- 舊記錄的三筆調料瓶 block_placer 警告指向實際存在的 seasoning_bottle_1；目前 64 個內容狀態共用該方塊。沒有證据支持刪除這條放置路線來消警告。
- `Block  couldn't be found in the registry` 缺少 identifier、來源檔與前文，不能只憑這一行認定是煙火或酒館。靜態檢查未找到本包空 block_placer 或不存在的本包目標；不把未知 ID 改成 air。
- 舊隔離世界重啟後酒館桌／吧檯消失的紀錄尚未在固定包組合重現；不清理使用者世界，也不以靜態檢查冒充持久化驗收。
- 魔法輪盤紫黑缺圖與酒館 title 通道干擾屬獨立調查。酒館修正移除 title 資料傳輸及閒置 ktmix:off；沒有改寫 A Magic Way、UI Queue 或 Novelty API 原包。

## 檢查邊界

本輪只做實際 JSON／JavaScript、配方、引用、材質一致性、舊美術資產與建置內容校驗；沒有執行 Minecraft 客戶端、BDS 或模擬玩家互動測試。統一 blend 後的實際排序／透明效果、警告是否完全消失，以及空方塊 registry 錯誤仍須新 Content Log 與受控包順序驗收。

伺服器升級時不要混用 2.7.66 BP 與 2.7.67 RP。原有私服轉接流程仍需按自己安裝的 Cookery UUID 處理，不能把公開測試包稱為已完成私服適配的成品。
