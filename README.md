## Current maintained baseline: 2.8.92

**G92 手持餐盤客戶端診斷候選**：預設關閉；只對既有 QA 標記與指定單列餐盤加入限量 client Molang 記錄、四個判定柱及常量食材對照，保留資料與正式顯示路徑。此隔離候選未整合最新 main，也未宣稱修復秘製內容或 CI／真人驗收通過。見 [G92 範圍](docs/STATUS-A2.8.92.md)。

**G91 Cloud 表達式候選**：修正 G90 原生載入確認的 Cloud 粒子 Molang 語法錯誤，保留相同速度向量、單位及既有餐盤功能。G90 觀察與新候選驗證分開記錄。見 [G91 範圍](docs/STATUS-A2.8.91.md)。

**G90 手持餐盤候選**：整合 current main 的油液所有權／原作傷害回饋與 G89 放置餐盤修復，加入只讀的雙手盤中內容顯示、快取失效及讀寫錯誤恢復保護。相同編號的兩條 G83／G84 來源明列保留；原生手持驗證及家族准入仍待完成。見 [G90 範圍](docs/STATUS-A2.8.90.md)。

**G89 餐盤朝向／普通串候選**：依 G88 四向觀察與原作矩陣修正 native mesh yaw，並讓普通串使用既有完整原作網格及餐盤專用顯示，避免持物查詢缺失造成空盤。保留已驗證的 G88 進食、插入及數量更新修復；本候選仍須原生驗證。見 [G89 範圍](docs/STATUS-A2.8.89.md)。

**G88 餐盤互動／姿態候選**：保留已凍結的 G87 修復，補上顯示 helper 移除失敗時的封閉保護與真實 discard 路徑測試；使用全新身份，不覆寫 G87。原生互動與姿態仍須本候選驗證。見 [G88 範圍](docs/STATUS-A2.8.88.md)。

**G87 餐盤互動／姿態候選**：根據 G86 真實客戶端觀察修復指向餐盤時的原生進食漏取消，並在數量改變造成槽位 yaw 更新時重建該顯示 helper。保留 G86 色盤、資料及飽和度修復；新候選仍須原生驗收。見 [G87 範圍](docs/STATUS-A2.8.87.md)。

**G86 一致來源整合候選**：以已合併的 G82 原作 Cookery 色盤來源為基線，保留 G83–G85 完整餐盤顯示、診斷、原生飽和度上限修復及生成 yaw 初始化。新的整合身份不覆寫舊候選；原生舊候選結果不等於 G86 驗收。見 [G86 範圍](docs/STATUS-A2.8.86.md)。

**G82 原作食材色彩修復**：直接核對官方 Java 廚房兩個分支的 99 種粒子貼圖色彩，98 種保留，「可疑炒菜」按原作修正七個烹調階段。既有 G81 修復保留；其他來源缺口與真人聲畫仍明列。見 [本版範圍](docs/STATUS-A2.8.82.md)。

**G85 原生餐盤修復候選**：以 G84 真實診斷確認的 saturation setter 上限錯誤為依據，於飢餓值更新後重新取得當前飽和度元件並遵守其有效上限，避免獎勵失敗回滾整次進食。盤中 helper 使用原有計算的 yaw 初始化生成，保留原作斜列；新候選仍須原生驗收。見 [G85 範圍](docs/STATUS-A2.8.85.md)。

**G84 餐盤姿態／診斷候選**：保留 G83 已限定實測的完整盤中食材、取回／插回與重新載入顯示；加入盤中 helper 的原生 body/head 對齊元件，並把已有的預設關閉診斷延伸至營養回報各子步驟與白名單錯誤分類。沒有猜測或修改營養 setter／計算；原生新候選仍待驗收。見 [G84 範圍](docs/plate-lineage/STATUS-A2.8.84.md) 及 [G83 限定原生結果](docs/NATIVE-PLATE-G83-BOUNDED-20261007.md)。

**G83 餐盤顯示修復審查候選**：修正原生測試中資料存在卻只見空盤／細碎像素的內容顯示，以既有原作完整烤串幾何、個人食材色盤及 1–5 根排位取代餐盤上的原生持物圖示。成功放置後立即排入顯示佇列。資料、交易及其他工作站保持原行為；實機新候選仍待驗收，沒有合併、發版或 live 更新。見 [本版範圍](docs/plate-lineage/STATUS-A2.8.83.md)。

**G81 一致來源修復候選**：整合已重現的停止→登出結算競態與上層罐子投影方向修正；兩套不同 G80 各保留原提交／聲明，不重用其身份。保留既有掛架互動、資料與進食防護，真人輸入／聲畫仍待 dot。見 [本版範圍](docs/STATUS-A2.8.81.md)。

**2.8.78 一致來源整合候選**：保留已發布 G74，整合原生合法的五罐四鉤廚具架／串盤別名、熱度到期資料回復，以及調料 JSON 比較與出料守恆修正。兩套不同的 G75 提案各保留原來源／收據，不合併或重用其版號；目前以全新候選進入 Git／家族准入。見 [本版範圍](docs/STATUS-A2.8.78.md)。平台差異明列，dot 客戶端驗收仍待完成。

**2.8.73 原作聲效與致死邏輯修復**：普通串補齊原作致死聲效／粒子，改走傷害路徑；修正 Heavy Metal 誤讀原生暫存生命值的致死／非致死判定。選定效果改用 Java 原始音源與 sprite。這不是 100% 還原或真人驗收；較早的暫緩部署要求已依使用者接受明列平台差異的回覆調整；來源／家族准入後更新 live，真人驗收獨立記錄。見 [本版範圍](docs/STATUS-A2.8.73.md) 與 [完整目標及缺口](docs/JAVA-FIDELITY-GOAL-20261007.md)。

**2.8.69 測試發佈候選**：整合秘製串幾何／原色、持物校準、完成後顯示所有權及食材薄片 alpha 輪廓／側面 UV 修復，保留 2.8.67 修復。限定牛肉 helper 外觀及獨立 6,500 ms 進食終點觀察見 [G69 範圍](docs/STATUS-A2.8.69.md)。先前錄影的變慢原因仍未釐清；未宣稱全部 213 食物、完整 Java／各視角或家族存檔／真人驗收通過。保持 client=false、production_ready=false、pending_client_acceptance。

**2.8.67 綜合修復候選**：整合 G66 的花椒樹、秘製串顯示、原生進食、調味瓶及第四次翻面快照來源，補上實際 25-tick 原生進食開關、Cookery 熱食／調料總開關、油液回滾與重複查詢修復，以及 Heavy Metal 重複延遲結算保護。逐項修復與仍未完成的要塞生成、致死判定及客戶端能力見 [G67 狀態](docs/STATUS-A2.8.67.md)。新版本不沿用 G66 的限定真人觀察作為驗收；`client=false`、`production_ready=false`、`pending_client_acceptance`。Git、家族准入與 live 部署以各自的新收據為準。

以下舊版候選敘述屬私人開發分支；衝突版本的原文保留在隔離歷史，並不改寫同號公開發版。

前候選修正調味瓶取回後手持內容不可見，以及第三人稱烤串錯套第一人稱位移的問題；仍須完成原生客戶端回歸，詳見 [2.8.61 範圍](docs/STATUS-A2.8.61.md)。完整 Java 一致性尚未驗收。

本候選修正自然生成花椒樹只有木頭的問題，改用與樹苗共用的 Java 樹形生成計畫，並保護區塊邊界及障礙物。原生 BDS 64 棵與 1,048 項斷言通過；詳見 [2.8.60 範圍](docs/STATUS-A2.8.60.md)。不會盲目補葉到玩家放置的木頭上。

前候選修正 Windows／Linux 動畫產生器的零值符號與初始角度分支差異，保留逐位元重建檢查；詳見 [2.8.59 範圍](docs/STATUS-A2.8.59.md)。完整客戶端／Java 一致性仍未驗收。

前候選修正烤串進食計時與第一人稱骨架疊加，並修正烤串／調味瓶副手不可見的原生骨架定位。牛肉串、饅頭片串及取消換物已做限定客戶端回歸；完整 Java 動畫、原生副手進食及其餘缺口仍未驗收。詳見 [2.8.58 範圍與證據](docs/STATUS-A2.8.58.md)。此為審查候選，不代表已合併、發版或部署 live。

前候選修正真實客戶端進食結束後進度條持續殘留，以獨立的透明度／等待／消失鏈處理，保留其他附加包的提示。已實測提前鬆手與完整進食；驗收範圍及限制見 [2.8.57 說明](docs/STATUS-A2.8.57.md)。

前候選將秘製串熟食快照移到第四次成功翻面，以交易回滾保護全部串與烤架狀態，詳見 [2.8.56 範圍](docs/STATUS-A2.8.56.md)。

前候選修正高級廚具架放置後的內容顯示選擇：上層不重複生成瓶子、下層只顯示前三個非空工具，保留全部九格儲存。完整 FIXED 姿態仍需另外驗收，詳見 [2.8.55 範圍](docs/STATUS-A2.8.55.md)。

前候選補回 Java 放開進食時的 1 tick 寬限：23 tick 不結算、24／25 tick 可結算；保留完成事件優先及物品身分驗證。詳見 [2.8.54 驗證範圍](docs/STATUS-A2.8.54.md)。

前候選修正潛行進食、烤串盤滿飽食限制、盤中熱食倍率及組串／插串音效，保留 2.8.52 調味瓶掛接修復。詳見 [2.8.53 驗證範圍](docs/STATUS-A2.8.53.md)；真人客戶端驗收仍獨立記錄。

本版補齊跨包出料、逐堆變體、展示註冊與權威新生成宿主接口，詳見 [A2.8.51](docs/STATUS-A2.8.51.md) 及 [API v1](docs/BEDROCK-INTEGRATION-API.md)。完整保留 2.8.48 聲畫及第三人稱進食修復。原版要塞 callback、任意新圖像及 Windows 真人驗收仍另有界線。

前版統一煙火物品及工作站提示中的藍色斜體系列標籤；三語品名、指南分類與 2.8.45 的修復保留。詳見 [A2.8.46 物品標籤](docs/STATUS-A2.8.46.md)，真人提示顯示仍待確認。
本版修復食用完成時的熱度判定、服務端與模型共享的隨機吃法、可反覆治療的原生龍血生命上限，以及秘製串三食材手持顯示。包含 2.8.42 角色效果快取與 canonical 2.8.43 第一人稱框架修復。詳見 [當前修復與驗收矩陣](docs/CURRENT-REPAIR-STATUS.md) 與 [A2.8.45](docs/STATUS-A2.8.45.md)；真人驗收、秘製動態 GUI 及部分 Java 平台能力仍有缺口。

[本版提示與圖形 HUD 修正／未完成項](docs/STATUS-A2.8.40.md)：以 Java 原作觸發、翻譯與圖形為準，移除自創文字條。

Public oil and food output APIs, shared guide localization, native station contents and failure recovery: [release scope](docs/STATUS-A2.8.40.md). Real-client and Java platform differences are recorded separately.

Canonical runtime and dependencies: [baseline.json](baseline.json). Build from this source; no private gameplay patch layer is required. Read [baseline maintenance](docs/BASELINE-MAINTENANCE.md) before importing historical artifacts or deploying.

> 歷史 A2.8.47 維護記錄：**非當前版本** — [正式來源修訂](docs/STATUS-A2.8.40.md) · [全部問題追蹤](docs/REPAIR-TRACKER.md)。A2.8.10 結算修復與穩定 API adapter 已收回正常 runtime；整體 Java 功能及客戶端驗收尚未完成。

# Kaleidoscope Grilling — unofficial Bedrock port

煙火（Grilling）的非官方 Minecraft 基岩版移植工程。

**當前 runtime 身份以 baseline.json 與頁首狀態為準，依賴作者原版 Cookery 1.6.0。正式打包直接輸出此來源，不使用 server-edition 玩法注入。爐／串架使用原生容器實體儲存，不要求 upcoming_creator_features；隔離 BDS 探針已通過，A2.8.40 補齊餐盤放置／插串／取串的寫入確認與回滾；A2.8.31 的牛肉塊與切雞副產物仍需整套家族的砧板 API。驗收證據以部署收據為準。**

唯一寫入目的地：`casama233/kaleidoscope-grilling-unofficial`，repository ID **1377218440**。

## 歷史開發與發佈記錄

以下舊版本段落保留當時的開發狀態；A2.3／A1.x 產物和舊廚房依賴不是當前正式建置入口。當前來源以 baseline.json 和 release notes 為準。

## A2.3：Hot Food堆疊＋烤爐四態＋世界油

- **[A2.3 可導入 Gameplay Core mcaddon](artifacts/Kaleidoscope_Grilling_A2.3_Gameplay_Core.mcaddon)**
- **[A2.3 bridge. 工程](artifacts/Kaleidoscope_Grilling_A2.3_Gameplay_Core.brproject)**
- **[A2.3 完成範圍與平台差異](docs/STATUS-A2.3.md)**
- **[成功 CI：70項回歸／行為測試＋官方 Dash](https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/35492689153)**

41種正式食物恢復最大64堆疊；含HotUntil／seasoning的串由腳本安全合併，熱度按數量加權平均。蹲下＋空手互動 Chest／Trapped Chest／Barrel 可執行 Java OrderToCook Refrigerator 的 Normal Sort 語義（熱度差≤5分鐘才合併）。「冰箱」在 Java 原版只是 OrderToCook 可選模組的整理相容，不會延長 HotUntil。

烤爐現在用同一個3槽 BlockEntity 的 custom states 在 **flat/unlit、flat/lit、legged/unlit、legged/lit** 四態切換；lit 使用原作火焰模型／貼圖，並加 face-dimming off、AO 0、light emission 13。支撐判定使用 stable Bedrock 的 `!below.isSolid` 近似 Java top-face-sturdy。

Dragon Blood 總有效生命已做到 +6/+10（原生可見 +4/+8 加2點腳本傷害池）；Tundra Strider 改按雪／冰摩擦語義提供約1.30／1.11／1.1055速度因子；Mustard維持6格 flee-like，Sulfur改成水平8／垂直16範圍。Numb準星仍不覆寫全局HUD，因26.51 stable沒有安全per-player crosshair offset API。

三種油現在有 **8級世界液面、向下優先／水平擴散、桶收放、Cookery油壺灌裝**；仍明確標為 scripted fluid simulation，而不是 Forge/Bedrock engine LiquidType。

## A2.2：逐口3D＋四瓶調料堆疊＋Numb動作（歷史基線）

A2.2 把固定串的「真正拿在手上吃」接回正式 Gameplay Core：39個正式 attachable 依 `query.item_in_use_duration` 在原作咬點切換完整／bite-stage 幾何，不替換邏輯 ItemStack，因此保留 A2.1 的 Hot Food、調料、25 tick 提前結算與主／副手資料。

- **[A2.2 可導入 Gameplay Core mcaddon](artifacts/Kaleidoscope_Grilling_A2.2_Gameplay_Core.mcaddon)**
- **[A2.2 bridge. 工程](artifacts/Kaleidoscope_Grilling_A2.2_Gameplay_Core.brproject)**
- **[A2.2 完成範圍與已知引擎差異](docs/STATUS-A2.2.md)**
- **[最終成功 CI：50項回歸／行為測試＋官方 Dash](https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/35490679938)**

本輪生成 **39個逐口 attachable、150個真實階段幾何**；每個實際咬點同步5個食物碎屑粒子和對應原作進食音軌。THREE_RANDOM 的原生使用窗口修正為5秒；若本次選到 THREE_ALT，腳本在90 ticks精確提前結算。模型本身因 Molang 無法讀服務端選中的 branch，採兩條時間線中點，最大模型階段偏差約 **1.67 ticks**；邏輯、骨骼、聲音與粒子仍使用真分支。

調料瓶現在最多物理堆 **4瓶**，每瓶獨立保存 kind／ingredients／uses／variant，取頂瓶或拆整組都不混資料。為維持26.51 retail且不開實驗，使用四個 block identifier 而非自訂 block states。

Numb 的 Java 四肢異常擺動已轉成 Bedrock 玩家骨骼動畫；Java GUI Mixin 的準星繞圈沒有穩定 Bedrock HUD offset API，因此沒有偽造完成。菜籽油／辣椒油／熔岩辣椒油則先建立3種正式油型資料契約；26.51公開穩定API沒有真正自訂 FluidType 註冊能力，所以**本版沒有宣稱真自訂流體已完成**。

最終驗證：A2.0 **16/16**、A2.1 state **4/4**、A2.1 runtime **18/18**、A2.2 runtime **12/12**，合計 **50/50**；官方 Dash v1.2.0 實際編譯 **570 files**，BP **65**、RP **505** 逐檔一致。

## A2.1：油壺＋調料＋煙火氣＋效果等價層（歷史基線）

A2.1 把 A2.0「烤得熟」推進到「**用 Cookery 油壺刷油、自己配調料、趁熱吃並得到原作語義效果**」。

- **[A2.1 可導入 Gameplay Core mcaddon](artifacts/Kaleidoscope_Grilling_A2.1_Gameplay_Core.mcaddon)**
- **[A2.1 bridge. 工程](artifacts/Kaleidoscope_Grilling_A2.1_Gameplay_Core.brproject)**
- **[A2.1 完成範圍、效果等價與差異](docs/STATUS-A2.1.md)**
- **[成功 CI：38項行為驗證＋官方 Dash](https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/35489240344)**

核心新增：

- 直接識別 Cookery 1.0.6 的 `kaleidoscope_cookery:oil_pot_filled` 與 `kc_oil_count`，**每根串消耗1點油**。
- 正式調料瓶方塊與六種調料材料；最多8份配料，基礎三料齊全後取回，**搖80 ticks**成 Special Seasoning。
- Special Seasoning 共16次使用；爐上3串一次撒料就**消耗3次**，完整配料列表跟著熟串保存。
- Hot Food 使用 `world.getAbsoluteTime()` 與100 tick分桶；熱著吃時**新Buff時長×2、飽和度×125%**，調料效果不再被二次翻倍。
- Java Cookery 在 Bedrock 宿主中不存在的 Vigor / Warmth / Flatulence / Hinder / Projectile Dodge / Tundra Strider / Mustard / Sulfur / Preservation，按 Java 源碼做 Bedrock 語義等價層。
- Heavy Metal、Heavy Metal Poisoning、Dragon Blood、Numb 調料進階效果開始工作。
- 黃金串 Invincible 改用世界絕對時間；普通串恢復「消耗無敵＋50%格擋，否則致死」核心規則。
- 19生＋19熟＋普通串，共 **39個正式3D手持 attachable**，不再只有GUI圖示。

驗證：A2.0回歸 **16/16**、A2.1狀態 **4/4**、A2.1完整模擬 **18/18**，總計 **38/38**；官方 bridge. Dash v1.2.0 實際編譯 **257 files**，BP **60**、RP **197** 逐檔與真實輸出一致。

**仍未做 Minecraft 26.51 客戶端／BDS 實機驗收。** Tundra Strider、Mustard、Sulfur、Dragon Blood、Numb 有明確的 Bedrock 引擎差異；詳細邊界見 A2.1 狀態頁。

## A2.0：正式 Gameplay Core（歷史基線）

A2.0 不再以 `kg_imm` 測試物代表玩法。新增正式 `kaleidoscope_grilling` BP/RP，以及真正具有 **3 個 BlockEntity 容器槽**的 `kaleidoscope_grilling:grill`。

目前核心閉環：

**點火 → 最多三串生串 → 刷油 → 四次翻面 → 撒料 → 熟串出爐**，並包含 Java 原版的 800 tick 過熟、再 400 tick 燒成木炭、中途拆爐產生謎之燒烤、過熟取出黑暗燒烤。

- **[A2.0 可導入 Gameplay Core mcaddon](artifacts/Kaleidoscope_Grilling_A2.0_Gameplay_Core.mcaddon)**
- **[A2.0 bridge. 工程](artifacts/Kaleidoscope_Grilling_A2.0_Gameplay_Core.brproject)**
- **[A2.0 完成範圍與 Java 差異](docs/STATUS-A2.0.md)**
- **[A2.0 正式工程](projects/grilling/gameplay_core/)**
- **[成功 CI：狀態機＋模擬世界＋官方 Dash](https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/35487932877)**

從鎖定 Java 1.1.1 自動抽取 **19組固定生串→熟串**、營養／飽和、動畫 profile 及熟串效果資料；目前生成 **46個正式物品，其中41個為真正 food item**。25 tick（1.25秒）提前進食檢查點已接入真 hunger/saturation，能直接等價的原版 Minecraft Buff 也已接上。

A2.0 特別維持 **Bedrock 26.51 retail**：使用穩定版 `@minecraft/server 2.9.0`。三個物品槽由新 BlockEntity 容器保存；phase/flips/timer 透過穩定的 world dynamic properties 按座標保存，沒有要求 26.60 Preview 才完整可用的 per-block scripting API。

實際驗證：Java狀態機 **16/16**、生成後 A2 runtime 模擬 **19/19** 通過；官方 bridge. Dash v1.2.0 實際編譯 **121個檔案**，BP **52**、RP **69** 個來源檔逐一與真實 Dash 輸出一致。

**尚未做 Minecraft／BDS 實機驗收。** Cookery 油壺直接接線、Cookery 專屬效果、完整熱食／調味資料、正式3D分口串、普通串致死特殊規則、自由秘制串和其餘機器留給 A2.x。

## A1.16：Cookery 依賴＋六種進食規則＋玩家主副手

A1.16 不再把動效包當成獨立正式結構：BP 明確依賴 Kaleidoscope Cookery 1.0.6 的 BP，RP 明確依賴 Cookery 1.0.6 的 RP；Cookery 本體不打進本倉庫或測試包。

新增原作六種進食規則 ONE／TWO／THREE／THREE_ALT／THREE_RANDOM／FOUR。THREE_RANDOM 在開始時只決定一次 THREE 或 THREE_ALT，之後由同一 resolved profile 驅動總長、玩家骨骼、分口與音效，不會每一口重抽。

- **[下載 Cookery 依賴 A1.16 測試包](artifacts/Grilling_Immersion_Lab_A1.16.mcaddon)**
- **[下載 A1.16 bridge. 工程](artifacts/Grilling_Immersion_Lab_A1.16.brproject)**
- **[A1.16 實際進度、六種規則、測試方式與邊界](docs/STATUS-A1.16.md)**
- **[A1.16 玩家綁定工程](projects/grilling/integration/immersion_lab/)**
- **[成功的官方 Dash／行為驗證工作流程](https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/35484643707)**

本輪生成 16 條玩家動畫：五個 resolved 進食 profile × 主／副手、刷油 × 主／副手、撒料 × 主／副手、拿起／收回 reach × 主／副手。沒有覆寫 minecraft:player；手持物使用 attachable 綁定 rightItem／leftItem。ONE 與 THREE 會驅動第二隻手，但只有對側手為空時才暫放來源衍生咬塊，不覆蓋玩家已有物品。

刷油保留原作 1 秒核心、撒料保留原作 0.5 秒核心；各自在前後新增 0.15 秒拿起／收回。操作必須靠近並面向爐心，接觸聲在拿起過渡後才觸發。進食六種規則本身不加時，咬點維持原作時間。

實際結果：六種規則／流程 21 項通過，實際 A1.16 adapter 在模擬事件宿主中 15 項通過；Cookery 依賴、16 條動畫、4 套 attachable 幾何及 6 個 profile selector 的結構檢查通過。Windows 上官方 bridge. Dash v1.2.0 實際編譯 77 個檔案，RP 48、BP 28 份檔案逐一和編譯輸出一致。

**Minecraft 客戶端／BDS、真實 FOV／皮膚、左撇子設定和最後接觸位置仍需實機驗收。** 目前測試包不扣材料、不回復飢餓、不註冊正式配方；正式生存加工邏輯仍待接線。

A1.15 的獨立驗收台及逐幀檢查頁保留為歷史動效基線：[A1.15 狀態](docs/STATUS-A1.15.md)。

## A1.14累積素材基線

| 內容 | 已驗證範圍 |
|---|---|
| 累積素材 | 381份Bedrock `.geo.json`、381份對應 `.bbmodel`、171張圖集；不是762種食物 |
| 植物 | 魚腥草11個外觀＋花椒樹苗／原木／兩種樹葉 |
| 來源 | 669份來源記錄；烤爐保留fork來源，Minecraft模板另列權利歸屬 |
| 原有素材保護 | A1.12的888份模型／編輯檔／圖集和628份來源保持SHA-256不變 |
| 靜態幾何審查 | 全部381候選有向表面與UV一致；植物新增120對八角度圖片一致 |
| bridge.編譯 | 官方Dash v1.2.0實際編譯主RP及指南BP/RP並核對輸出 |
| 玩家筆記核心 | 27項模擬玩家儲存測試通過；尚未接入原指南動態操作頁面 |

歷史範圍、植物透明面修正與限制見 **[A1.14實際進度](docs/STATUS-A1.14.md)**。本批新增的一個動作展示場景不計入381種靜態候選。

## 工程位置

- **[主素材工程](projects/grilling/)**：在bridge.開啟此資料夾，不是倉庫根目錄。
- **[獨立指南章節測試工程](projects/grilling/integration/cookery106/)**：我方BP/RP，不含Cookery原包。
- **[可編輯模型](projects/grilling/editor/generated/)**、**[Bedrock幾何](projects/grilling/resource_pack/models/entity/kg_a1/)**、**[貼圖圖集](projects/grilling/resource_pack/textures/kg_a1/)**。
- **[玩家筆記核心](notebook/)**：搜尋、收藏、有順序的自訂配方及玩家儲存適配器。
- **[動效建置與測試來源](development/immersion/)**：A1.15 原始動效基線。
- **[玩家骨骼／相機綁定建置與測試](development/player_binding/)**：A1.16 六種規則與主／副手。
- **[A2 Gameplay Core 建置與測試](development/gameplay_core/)**：正式烤爐、固定串與食物閉環。

## 植物離線預覽

這些圖片由實際匯出幾何渲染，不是Minecraft截圖。樹葉未套用生態域染色；樹木世界生成尚未完成。

[魚腥草八階段](projects/grilling/reports/plants/houttuynia-ages.png) · [後期紅色變體](projects/grilling/reports/plants/houttuynia-red-variants.png) · [花椒部件](projects/grilling/reports/plants/pepper-parts.png)

## 可重跑的檢查

```sh
node notebook/test.mjs
node development/immersion/test.mjs
node --experimental-vm-modules development/immersion/test_runtime.mjs
node development/player_binding/test.mjs
node --experimental-vm-modules development/player_binding/test_runtime.mjs
node development/gameplay_core/test_core.mjs
python development/gameplay_core/build.py
node --experimental-vm-modules development/gameplay_core/test_runtime.mjs
python development/gameplay_core/verify.py
python development/gameplay_core/augment_a21.py
node development/gameplay_core/test_a21_core.mjs
node --experimental-vm-modules development/gameplay_core/test_a21_runtime.mjs
python development/gameplay_core/verify_a21.py
python development/gameplay_core/augment_a22.py
node --experimental-vm-modules development/gameplay_core/test_a22_runtime.mjs
python development/gameplay_core/verify_a22.py
python -m pip install numpy==2.3.5 Pillow==12.3.0
python projects/grilling/tools/build_assets.py
python development/immersion/verify.py
```

重建動效需要固定上游提交的本地快照：

```sh
python development/immersion/build.py --upstream /path/to/KaleidoscopeGrilling-9a1acdab27698457bec16c9362678e574895a28c
```

安裝bridge.官方Dash後，在要編譯的工程目錄執行 `dash_compiler build`（Windows独立程式可用 `dash.exe build`）。動效工程編譯後，可在倉庫根目錄執行 `python development/immersion/verify.py --compiled` 比較輸出。

先前成功流程：

- [A1.12素材重建及集合雜湊核對](https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/35451900945)
- [植物幾何及120對八角度比較](https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/35452356584)
- [主RP＋指南BP/RP的真實Dash編譯](https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/35452461036)
- [筆記資料核心測試](https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/35450471711)
- [A1.15 沉浸動效驗收](https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/35455778472)
- [A1.16 Cookery依賴＋六種玩家動畫驗收](https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/35484643707)
- [A2.0 Gameplay Core 完整CI](https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/35487932877)
- [A2.1 Cookery油壺／調料／煙火氣完整CI](https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/35489240344)
- [A2.2 逐口3D／四瓶調料／Numb完整CI](https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/35490679938)
- [A2.3 Hot Food／烤爐四態／世界油完整CI](https://github.com/casama233/kaleidoscope-grilling-unofficial/actions/runs/35492689153)

`migration/bootstrap.py`與`development/run_plants.py`是一次性搬遷工具，不應在既有工程上重複執行。日常主素材重建使用`tools/build_assets.py`；動效建置器只重建獨立驗收台，不覆蓋主RP或原指南。

## 尚未完成

目前剩餘重點已從「補主要玩法」轉為**成品驗收與平台差異**：Minecraft 客戶端中的手持/放置模型、透明材質、HUD/動畫與不同 FOV；BDS 長時間運行、重進世界持久化、多人同時操作與效能；Guide + Cookery 1.0.6 組合的多人語言實測；以及 Bedrock stable API 無法 1:1 的 Java 行為（例如真自訂 FluidType、Pepper Leaves `entityInside`、Numb per-player 準星偏移、任意 modded smoking recipe lookup）。

自由／秘制串、餐盤、串譜、榨油／大缸／Advanced Rack、作物種植、花椒樹 lifecycle / acquisition / forest worldgen 等早期 README 所列缺口後續已實作，請以最新 `projects/grilling/gameplay_core/reports/a27xx-*.json` 與 `docs/STATUS-A2.7.xx.md` 為準。

**Dash/Node/靜態 reference gate 成功不等於 Minecraft、BDS 或 client visual 已驗收。** A2.7.63 新增的 visual gate 只保證 attachable / geometry / render controller / animation / atlas 引用鏈不斷；實際手感與畫面仍需真機驗收。

## 來源、授權與資料保護

原作素材保留CC BY-NC-SA 4.0條件，原碼與衍生工具的BSD聲明與素材分開，Minecraft模板不套用CC聲明。主工程`source_manifest.json`、`ATTRIBUTION.md`與獨立驗收台`sources/manifest.json`保留出處，輸出BP/RP包含授權與致謝。

不提交使用者完整Cookery安裝包、私人宿主腳本、世界、憑證或機器資料。森羅物語指南維持一個煙火入口，不另發書物品。此前完整歷史HTML與全部舊比對圖未全數入庫；原交付附件保留原歷史範圍。

## bridge. canonical authoring

Open the repository-root `config.json`, which points to the current locked BP and RP. See [the bridge. workflow](docs/BRIDGE-WORKFLOW.md) for editor settings, portable `.brproject` export, schema limitations and exact runtime comparison.

Current rack hit correction: [G79 scope](docs/STATUS-A2.8.80.md).
