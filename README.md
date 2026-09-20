# Kaleidoscope Grilling — unofficial Bedrock port

煙火（Grilling）的非官方 Minecraft 基岩版移植工程。

**目前：A2.0 Gameplay Core 已建立第一條正式可玩閉環；仍不是 Java 全模組完整移植。**

唯一寫入目的地：`casama233/kaleidoscope-grilling-unofficial`，repository ID **1377218440**。

## A2.0：正式 Gameplay Core

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

`migration/bootstrap.py`與`development/run_plants.py`是一次性搬遷工具，不應在既有工程上重複執行。日常主素材重建使用`tools/build_assets.py`；動效建置器只重建獨立驗收台，不覆蓋主RP或原指南。

## 尚未完成

Minecraft實機下的 A2 烤爐／BlockEntity 驗收、Cookery油壺與專屬效果、熱食與完整調味、餐盤與擺放、自由組合串、榨油／大缸／厨具架、真實流體與剩餘粒子效果、指南動態搜尋／收藏／自訂配方頁面、完整玩法與多人驗收。魚腥草与花椒只有靜態素材，沒有種植、採收或樹木生成。

**Dash成功不等於bridge.圖形介面、Minecraft、BDS或材質／光照／動畫已驗收。** 來源與匯出解析分開，但離線圖像比較共用光柵器；新展示台只在標準20TPS下對齊主要時序，低TPS與Java牆鐘差異仍需處理。

## 來源、授權與資料保護

原作素材保留CC BY-NC-SA 4.0條件，原碼與衍生工具的BSD聲明與素材分開，Minecraft模板不套用CC聲明。主工程`source_manifest.json`、`ATTRIBUTION.md`與獨立驗收台`sources/manifest.json`保留出處，輸出BP/RP包含授權與致謝。

不提交使用者完整Cookery安裝包、私人宿主腳本、世界、憑證或機器資料。森羅物語指南維持一個煙火入口，不另發書物品。此前完整歷史HTML與全部舊比對圖未全數入庫；原交付附件保留原歷史範圍。
