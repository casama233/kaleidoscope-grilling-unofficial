# Kaleidoscope Grilling — unofficial Bedrock port

煙火（Grilling）的非官方 Minecraft 基岩版移植工程。

**目前 canonical runtime：A2.7.65 Full Skewer Hand Geometry。核心玩法、穿串、調料、油系統、Advanced Rack、主要作物、花椒樹/世界生成、Cookery 菜餚與主要 advancement 已完成可實作 parity；目前主要剩餘工作是 Minecraft/BDS/多人實機驗收、client visual 打磨與 Bedrock 平台無法 1:1 的差異收斂。**

唯一寫入目的地：`casama233/kaleidoscope-grilling-unofficial`，repository ID **1377218440**。

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
