# A2.7.x 伺服器版（Senluo 部署）— 差異與引擎除錯紀錄

> 已部署版本：`artifacts/Kaleidoscope_Grilling_A2.7.20_Roasted_Sweet_Potato.mcaddon`（上游建置，未修改上游檔案）。
> 首輪為 A2.7.14（同一組差異，已在隔離引擎與正式服各驗證一次）；差異表與工具以最新產物為準，兩版輸入差異見 §7。
> 部署對象：實際運營的 Bedrock 專用伺服器 1.26.51.1，與森羅物語：廚房 1.0.6 併用。
> 本文件只記錄「伺服器版相對上游產物的差異」與「以伺服器自帶 Content Log／腳本除錯得到的結果」。

## 1. 為什麼需要伺服器版

上游產物直接在專用伺服器上會出現三類問題：相依識別碼指向公開版廚房包、若干腳本在**受限執行環境**（before 事件）中呼叫被禁止的 API、以及 1.20+ 配方／方塊元件 schema 與實際引擎版本不符。這些問題在 Java 版與用戶端不存在，只有在伺服器載入時才會顯現。

## 2. 差異清單（逐項可驗證）

| # | 檔案 | 上游 | 伺服器版 | 依據 |
|---|------|------|----------|------|
| 1 | `manifest.json`（BP／RP） | 相依 `10f37ae2-9ccf-435f-b34b-0eec8191cd94`（廚房 BP）、`c89dc8df-c3fc-4bc8-8bd0-527abba76681`（廚房 RP） | 改接該伺服器實際安裝的廚房包 `403f7a4a-a837-42c8-b5d3-76d5079ef269`、`8f39983b-00a6-4818-b489-0a73daf3bc87` | 相依必須能在世界內解析，否則管理器拒絕啟用 |
| 2 | `scripts/itemData.js`（新增） | 無 | 可堆疊物品的動態屬性／lore 一律走 lore-token + 世界動態屬性 | 穩定版 API 禁止在 `maxAmount > 1` 的 ItemStack 上寫動態屬性 |
| 3 | `scripts/blockSupport.js`（新增） | `block.isSolid`（mock 有、實際 BDS 未曝露） | `hasSolidTop()` 近似判定 | 穩定版未曝露 `isSolid` |
| 4 | `scripts/main.js` 等 6 檔 | 直接 `stack.get/setDynamicProperty`、`stack.get/setLore` | 改呼叫 `itemData.js` 轉接層 | 同上；共 81 處呼叫點 |
| 5 | `scripts/main.js` 調料瓶放置 | `world.beforeEvents.playerPlaceBlock` 內讀取手持物 | 改用方塊自訂元件 `senluo:grilling_bottle_place`（`system.beforeEvents.startup` 註冊） | 穩定版 2.9 於方塊元件提供 `beforeOnPlayerPlace`，before 事件拿不到原始手持堆疊 |
| 6 | `blocks/seasoning_bottle*.json`（5 檔） | 無自訂元件 | 加入 `"senluo:grilling_bottle_place": {}` | 搭配 #5 |
| 7 | `blocks/skewer_recipe.json`、`houttuynia_crop.json` | `"ambient_occlusion": false` | `0.0` | 欄位型別為數值 |
| 8 | `blocks/houttuynia_crop.json` | `"tag:minecraft:crop": {}` | 移除 | 該版本方塊 schema 無此元件；Content Log 逐次報錯，且腳本以方塊識別碼判斷，不依賴標籤 |
| 9 | `recipes/oil_press.json`、`oil_cake.json`、`big_vat.json` | 無 `unlock` | 補上 `unlock` | 1.20+ 配方缺少解鎖資料會被引擎拒絕 |
| 10 | `scripts/a23_oil_world.js` | `North:[0,0,1], South:[0,0,-1]` | 對調為 `North:[0,0,-1], South:[0,0,1]`；來源方塊缺失時保留註冊列；`compute()` 例外改為保留列 | 座標偏移與上游其他檔案慣例相反；避免暫時未載入區塊造成註冊遺失 |
| 11 | `scripts/a26_oil_machine_runtime.js` | 大缸放置分支在 before 事件內執行 `copy.amount=1` | 將該次寫入延後到 `system.run()` 內 | **受限執行環境禁止原生屬性寫入**，例外被外層空 `catch` 吞掉，導致放置大缸完全無效（見 §4） |
| 12 | `scripts/guide.js` + `guidePublisher.js` | 無（僅 `integration/cookery106` 測試包） | 由 `integration/cookery106` 的 publisher 產生指南入口，`REVISION` 改為 `server_a2_7_14`，內容改寫為 A2.7.14 實際可玩範圍 | 指南必須維持「廚房指南內的一個煙火入口」，不新增獨立指南書 |

## 3. 伺服器端報錯與處理（Content Log）

在隔離的 BDS 實例開啟 `content-log-file-enabled` / `content-log-console-output-enabled` 後逐輪修正：

1. `blocks/houttuynia_crop.json → components → tag:minecraft:crop: not present in the Schema` → 移除該元件（差異 #8）。
2. `1.20+ Recipes require unlock data`（榨油機／油餅／大缸）→ 補 `unlock`（差異 #9）。
3. `ItemStack::amount cannot be used in restricted execution`（a26 大缸放置）→ 差異 #11。
4. 部署後比對新舊啟動日誌：新日誌 **0 ERROR**，且先前的世界載入等待警告消失。

## 4. 引擎測試（隔離 BDS ＋ 模擬玩家）

以伺服器自帶 Content Log 與 `@minecraft/server-gametest` 的模擬玩家在隔離實例執行，非用戶端驗收。

**通過**

- 大缸：物品放置、空桶裝／倒油往返、榨油機（4 塊油餅、鐵砧壓榨達滿進度）將 4 桶油轉入相鄰大缸、油渣噴出、廚房油壺吸取（可堆疊物品中介資料經 lore-token 保存）。
- 烤爐：點火、手持生串放入消耗 1。
- 魚腥草作物：`age`／`red_variant` 狀態。
- 方塊支撐判定：草方塊計為實心頂面。
- 廚房指南：宿主（廚房包）註冊一個煙火入口、9 個條目。

**未涵蓋（不得計為已驗證）**

- 模擬玩家不執行原生方塊放置，因此「由物品原生放置榨油機／烤爐」未受測；大缸與調料瓶的原生放置路徑由模組自身處理函式覆蓋。
- 真實客戶端（iOS／Android／Windows）的模型、動畫、觸控與渲染未驗收。
- 多人、長時間負載未測試。

## 5. 尚待處理

- `All MaterialInstances must use the same render_method for a given block`：本批新增的套件在伺服器啟動時出現 26 次此警告（舊日誌為 0）。已靜態掃描兩包全部方塊檔（含 permutation）與資源包，未發現同一方塊混用 render_method 的情形，尚未定位到具體方塊；此警告僅提示可能影響用戶端渲染，無 ERROR。需要用戶端或逐包二分測試才能確認。
- `minecraft:block_placer` 警告 3 筆（`empty_seasoning_bottle`／`pending_seasoning`／`special_seasoning` 指向 `seasoning_bottle_1`）：與 A2.5 部署版本完全相同，屬上游既有狀態，非本次升級引入。
- 隔離測試中曾觀察到酒館桌／吧檯在重啟後未出現在原座標（同批的動態屬性與大缸方塊正常保留）；該測試世界的套件曾多次被覆寫，尚不能判定為模組缺陷，需在受控世界重測。

## 6. 重現

`tools/build_server_edition.py` 以倉庫內最新的 A2.7 產物為輸入，依上表逐項套用差異並自我檢查（每個取代都要求命中次數相符、且不得動到 `world`／`entity`／玩家的屬性呼叫），輸出可直接部署的 `BP/`＋`RP/` 目錄：

```
python tools/build_server_edition.py [--artifact PATH] [--version X.Y.Z] [OUT_DIR]
```

## 7. A2.7.20 追加處理

A2.7.15–A2.7.20 新增油菜／洋蔥／甘薯作物與烤甘薯，問題類別相同，工具已一併涵蓋：

- 新增 4 個作物方塊的 `tag:minecraft:crop` 移除（`canola_crop`／`onion_crop`／`houttuynia_crop`／`sweet_potato_crop`）。
- `ambient_occlusion` 布林值共 40 處改為數值。
- 新配方 `roasted_sweet_potato` 為熔爐配方，不需要 `unlock`（1.20+ 只要求工作台配方）。
- `main.js` 物品屬性呼叫點由 37 處增至 47 處，改寫改以「物品變數名」為準，並斷言世界／實體／玩家的同名呼叫數量不變。
- 引擎複驗（隔離 BDS）：指南入口仍為 9 個條目並由廚房宿主註冊；大缸放置與空桶往返透過。
