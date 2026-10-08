# G118：原作機制對照修補

2026-10-08。從 canonical G117／`baea844ecb8275dcdb2cfed3faa971f589953585` 整合三路代理修補。
Java 對照維持作者 [1.1.1／9a1acdab](https://github.com/breezeth-CN/KaleidoscopeGrilling/tree/9a1acdab27698457bec16c9362678e574895a28c)，
本日重新讀取官方專案與上游來源；主邏輯以 NeoForge 1.21.1 為主，共用資料與 Forge 1.20.1 差異分開核對。
包／模組與配對依賴為2.8.118，guide為0.3.48；來源身份以`baseline.json`和append-only `release-history.json`為準。
UUID、Cookery1.6.0、server2.9.0／server-ui2.2.0維持既有契約。

## 稽核編號與實際修補

F01–F16沿用本日一比一稽核編號。「來源修補」只表示目前程式及所列回歸，沒有代表原生／真人已接受。

| 編號 | 原問題與修正後結果 | 主要來源 |
| --- | --- | --- |
| F01 | 承接PR180的G117修補：手持提前食用在hunger增加後重新取得saturation，尊重即時effectiveMax，失敗回滾。 | `main.js::hungerSettle`；[G117](STATUS-A2.8.117.md) |
| F02 | 廚具架在before入口及deferred結算均確認爆炸未取消；重驗方塊狀態、容器owner與filter，保留取消或替換後的架子。 | `a2746_advanced_rack_runtime.js` |
| F03 | 串譜放置、扣手持、存record、取回、掉落和清理共用既有交易工具。確認交付後才清來源；失敗回滾；credited重載只清理，不再次發書。爆炸先保護錄製方塊，再以快照結算；方塊tick補非玩家支撐改動。 | `a25_plate_recipe_runtime.js`；`blocks/skewer_recipe.json` |
| F04 | 油渣調用與骨粉相同的植物handler，規劃兩次作用、只扣一顆；包含四種自家作物、花椒苗及三種明列原版作物。重驗完整手持與目標狀態，方塊／整樹修改失敗回滾。 | `plant_fertilizer.js`；`a26_oil_machine_runtime.js`；各crop／pepper runtime |
| F05 | 自然凋葉按無工具、Fortune 0掉落規則處理；persistent葉和未知區塊支撐保留。人工拆葉重新核對完整狀態，避免先採果後再按舊快照多出果。 | `a2748_pepper_tree_runtime.js` |
| F06 | 大缸材料與解鎖改為7顆`minecraft:brick`，保留原排列、桶與成品數。 | `recipes/big_vat.json` |
| F07 | 78個允許鏡射的有效配方，覆蓋12種原版柵欄的144種左右組合，包括異木種與下界磚柵欄。 | `recipes/oil_press.json`、`recipes/oil_press_fences/` |
| F08 | 魚腥草堆肥65%；花椒苗與花椒葉各30%。花椒葉以同ID的block-placer item提供原生堆肥元件。 | `items/houttuynia.json`、`pepper_sapling.json`、`pepper_leaves.json` |
| F09 | 榨油進度到16仍須完成10 ticks；互動只允許已進入waiting的缺容器情況重試，不能跳過正常倒數。 | `a26_oil_machine_runtime.js` |
| F10 | 自訂效果快照保存食用開始時剩餘duration；完成時只加倍新增duration，維持invincible排除。800→900的案例應得1000 ticks，不再把食用經過90 ticks多算進去。 | `main.js::fxSnapshot`／`doubleNewFx` |
| F11 | 合併比對忽略真正`SECRET_CREATOR_KEY`及與該作者精確匹配的自動lore，保留命名、配方、調味、外來資料與自訂文字。串譜換作者前先清可確認的舊作者行，避免模板作者殘留。 | `a23_hot_runtime.js`；`a25_plate_recipe_runtime.js::craftFromBook` |
| F12 | 成功取放改用已登錄的`block.itemframe.add_item`／`block.itemframe.remove_item`。 | `a2746_advanced_rack_runtime.js` |
| F13 | 串譜按黏貼的指定側面判定支撐，選取框改回10×13×0.25。區分collision與support shape：葉塊不支撐，靈魂砂／堆肥箱側面可支撐，開啟地板門只有一側；樓梯依朝向／轉角。未知形狀不推定支撐。 | `blockSupport.js`；`blocks/skewer_recipe.json`；[官方形狀取證](evidence/g118-support-shapes.md) |
| F14 | 放盤要求完整立方碰撞；單串與打包餐盤共用Cookery桌面截獲開關。瓶子的既有頂面支撐判據保持獨立。 | `blockSupport.js`；`a25_plate_recipe_runtime.js::placePlateOn` |
| F15 | 烤架出料先為整批預留原生相容的未滿stack，再空槽／掉落餘量；中途寫入失敗回復整批。 | `main.js::extract`／`rack_transfer_plan.js::planInventoryInsert` |
| F16 | Creative刷油與撒料依planner扣量，修除提交函式的第二層豁免；Creative打火石仍免耗耐久。 | `main.js::planCookeryOil`／`commitGrillAndHand` |

上述runtime檔案均在[canonical scripts](../projects/grilling/gameplay_core/behavior_pack/scripts/)；
物品、方塊與配方則在同一canonical BP的對應目錄，沒有安裝時補丁。
指南三語與實際材料、支援植物及完成等待同步，沿用Cookery內單一煙火入口。

## 放置餐盤與牆上串譜顯示

放置餐盤新增專用的實際串模型路徑：固定生／熟串與秘製串各用一個transient helper，
直接讀取已保存的ItemStack及既有食材palette，依原作1–5份布局、四朝向及FIXED變換定位。
共用既有烤架mesh，沒有更改來源物品、模型palette或容器ownership；普通／外部物品保留明列的generic後備路徑。

牆上串譜優先還原`recordedStack`，提供38種固定生／熟串與普通串，共39個GUI模型索引；
熟史萊姆使用原作五張動畫幀，秘製串使用保存食材的扁平模型後備。
固定圖示及五幀PNG逐檔與Java GUI-16來源比對，整檔bytes相同；紙面也同步為10×13。
這些來源與資產證據不代表引擎實際渲染已通過。

成功交易後僅排入去重的座標佇列，渲染時重新讀取權威內容。更新與清理共用有預算的排程，
不讀取觀察範圍外的區塊；spawn結果不明、helper仍有效或移除無法確認時保留tracking與配額，
避免反覆生成與漏算。無關原版方塊不填入工作站佇列，已知目標破壞後仍能清理。
史萊姆以四tick時鐘計算當前幀；附近目標較多時可跳過中間幀，不承諾高負載下每四tick均呈現。

## 針對性證據

| 受影響入口 | 已執行結果與範圍 |
| --- | --- |
| `test_food_finish.mjs` | 5／5；自訂／原生效果duration與排除項。 |
| `test_full_skewer_flow.mjs` | 30／30；原生相容堆疊、整批預留、掉落餘量、回滾及Creative油／調料／打火石。與G117整合的fixture衝突解決後同入口再通過。 |
| `test_core_skewer_cycle.mjs` | 33／33；CI指出舊VM未提供新的實際planner及配方掃描未處理子目錄，已補正。以異質metadata保持第二槽寫入故障可達，保留整批回滾並比對完整原始資料；遞迴檢查全部配方。 |
| `test_hot_food_manual_merge.mjs` | 9組PASS；真正作者鍵、翻譯／legacy自動lore、metadata與來源餘量。 |
| `test_plant_fertilizer_runtime.mjs` | 30／30；載入實際植物模組與油渣事件，涵蓋hand／target過期、整樹回滾、未知掉落與多人先採果競態。 |
| `test_oil_transactions.mjs` | 21／21；保留交易檢查，新增正常10-tick等待與waiting重試。 |
| `test_pepper_worldgen_seed.mjs`／`test_a2714_runtime.mjs` | 各8項PASS；既有生成、部分寫入回滾與魚腥草處理保留。 |
| `test_rack_transactions.mjs` | 49／49；取消、event不可讀、方塊／owner替換與音效路由。 |
| `test_plate_transactions.mjs`／`test_recipe_book_safety.mjs` | 63／63與18／18；串譜放置、取回、保存、掉落、支撐例外、credited重載、未知交付隔離、成功後顯示更新及換作者前調用真實lore清理函式。 |
| `test_plate_recipe_visual.mjs` | 新增16項PASS；實際renderer的內容分流、metadata保留、重排、四向定位、動畫幀、生成／移除未知結果、重載索引、配額與有界佇列。與既有盤交易、rack及第四翻快照共119項通過；再加受影響的parity／recipe-book入口，顯示收尾批次共149項。 |
| 配方／堆肥靜態核對 | 大缸材料及unlock、78有效柵欄配方覆蓋144組、三項堆肥率符合選定來源。 |

Java基線代理另外讀取兩版Mojang官方client JAR中的fences／wooden_fences tag並驗SHA1，
確認均為11種木柵欄加下界磚柵欄，沒有加入較新版本的pale oak。
同批官方JAR與mappings也確認葉塊、靈魂砂、地板門、堆肥箱、煉藥鍋、玻璃／冰及樓梯的水平支撐語義，
具體下載雜湊、方法及幾何保存在[可重現取證](evidence/g118-support-shapes.md)。
這是來源資料核實，未執行原mod JAR，也未擴大A證據範圍。
另由独立代理覆核串盤FIXED旋轉取消、1.2倍淨縮放、mesh偏移補償與所有1–5份布局；
此為來源數學覆核，未以Bedrock客戶端執行。顯示資產生成一致性由`tools/build_plate_display.py --check`檢查。
所有API doubles檢查屬B；語法、生成一致性、來源witness、版本與封裝只屬前置完整性检查。
本機不重跑歷史全套；同一候選完整必要套件由PR CI執行。
CI也要求五份工作站開發鏡像與canonical一致；已同步唯一落後的廚具架鏡像並通過原檢查。
物品圖示的歷史守衛追加G118花椒單檔見證：保留G60→67→68前像鏈，再與公開候選`dccbe92a`的整檔bytes比較；圖示入口6／6及原歷史來源入口12／12通過。19個commit引用均明列，原93-object provenance包維持不變。
花椒接觸測試的舊VM補載真正`plant_fertilizer.js`及其production依賴，保留接觸範圍、查詢次數、豁免、傷害與冷卻斷言，另確認樹苗已註冊且使用同一互動callback；該入口10／10通過。另一代理唯讀檢查目前驗證鏈中的同類載入點，未發現第二個缺注入caller。
以上CI收尾只修改非輸出鏡像／測試，G118凍結的BP／RP與封裝雜湊維持相同。

## 明確保留的差異與恢復界線

- **通用施肥未全閉合。** 現在支援油菜、洋蔥、甘薯、魚腥草、花椒苗、小麥、胡蘿蔔、馬鈴薯。其他原版植被與外部模組植物沒有通用native bone-meal橋。花椒苗是有效目標時，即使兩次45%抽樣都沒长大仍扣一顆，與Java成功使用語義相同。
- **外部材料／形狀需適配。** 配方覆蓋選定Java的12種vanilla fences，不聲稱其他模組加入tag的材料也可用。側面／完整方塊判據只承認已知類別；未知vanilla或add-on形狀拒絕新附著，但保留既有附著等待可判定狀態。
- **串譜支撐時序有差異。** 玩家破壞與爆炸有即時回檢，其他變更由20-tick方塊輪詢發現；Java updateShape的事件時序尚非完全等價。重載與方塊tick行為需真BDS核對。
- **未知交易不盲目重發。** 已確認交付的串譜receipt可在重載時清來源；prepared／未知spawn、無法確認cleanup或回滾失敗會保留原record並隔離。花椒葉同樣封鎖未確認掉落的重試。這避免重複發物，不等於對任意進程崩潰提供跨引擎原子交易；隔離資料需依實際世界證據恢復。
- **歷史作者文字保持保守。** 已存在且不符合目前canonical作者的舊模板行，無法證明其自動來源時保留；新的串譜製作不再產生該類殘留。
- **聲畫與宿主缺口仍獨立。** 本版新增放置餐盤及牆上結果圖示的來源實作；四朝向、光照、遮擋、動畫與重載仍待原生／client驗收。手持餐盤五份內容及其decoder、任意秘製串inventory圖示、Cookery正常producer、彈性炒菜與完整玩家聲畫尚未閉合。沒有以額外HUD替代缺失畫面。

## 當前部署與真人接受

G118必須有自己的完整家族static／BDS首次載入／重啟、最新停服世界rehearsal及LIVE讀回；
G114／G116／G117的既有收據不能用來接受本次變更。
本輪工作環境未取得BSM／luosen受管伺服器入口或當前完整家族候選與世界收據，
因此本頁沒有宣稱已更新LIVE、完成原生操作或真人驗收。
維持`client=false`、`production_ready=false`、`pending_client_acceptance`，直到同一候選的實际證據成立。

優先真人場景：生存正常取得原料→榨油→油渣再耕種→同瓶刷油／調味→滿包取串→食用；
另測跨作者秘製串／串譜製作、1–5份放盤、牆上串譜四朝向、取消爆炸及正常重登。
正常操作與故障注入證據分開，禁止模擬玩家代替實際接受。
