# A2.7.3 — 顯示／實機基線修復

> 本批**暫停新增配方與菜品**。先修使用者在 Minecraft 實機直接重現的兩個基礎錯誤：創造欄圖示破碎，以及懸空烤架只剩選取框、模型不可見。

## 1. 為什麼 A2.7.3 改成穩定化批次

A2.7.2 以前的離線驗證能證明：

- Java → Bedrock 幾何資料可逐面對應；
- 腳本語法、純邏輯與 Dash 編譯可通過；
- source / dist 檔案一致。

但這些**不能證明 Minecraft 引擎真的用我們預期的 UI / attachable / block renderer 路徑顯示**。

使用者實機截圖已證明至少兩個假設錯了，因此不再把「離線幾何相等」當成「顯示已完成」。

## 2. 創造欄圖示：根因已定位

A2.0 的 `build.py` 把 Java 3D item model 使用的材質／UV 貼圖：

`textures/item/fixed_skewers/*.png`

直接複製成 Bedrock：

`textures/items/<item>.png`

再交給 `minecraft:icon`。

這些 PNG 本來是**模型表面材質**，不是 GUI icon。Bedrock 因此正確地把整張材質表當作物品欄 2D 圖示，造成：

- 肉片／竹籤碎片；
- 顏色方格；
- 局部 UV；
- 「生黃金烤串」顯示成黃綠色材質塊。

A2.7.3 將三條路徑正式拆開：

1. **Inventory / Creative UI**：從鎖定 Java item model 的完整 3D elements + 原貼圖 + authored `display.gui` 姿態，離線光柵化成透明 64×64 icon。
2. **第一／第三人稱手持**：繼續由 Bedrock attachable 負責。
3. **進食分口**：繼續由 A2.2 staged attachable geometry / texture 負責。

不再拿 attachable 的 UV sheet 當 inventory icon。

本批覆蓋 41 個正式串類／失敗產物 icon；CI 會驗證透明背景、非空 silhouette、尺寸、圖像多樣性，並生成 contact sheet 供人工檢視。

## 3. 懸空烤架：根因與保守修復

A2.3 為了模仿 Java 的支腳，把完整 `grill_legged` 模型直接掛到主 block。該模型的腳從主 block 原點向下延伸到 **Y=-16**。

雖然 Bedrock 自訂 block geometry 在某些條件可超出單格，使用者實機已證明目前這條 `legged=true` renderer path 在目標環境會出現：

- gameplay state 還在；
- selection box 還在；
- **模型完全不可見**。

A2.7.3 不再讓主烤架是否可見依賴跨格負 Y geometry：

- 主 `kaleidoscope_grilling:grill` **永遠只渲染單格內的 flat / flat_lit 烤架頂部**。
- 懸空時，腳改成下方一格的內部 helper：
  `kaleidoscope_grilling:grill_legs`。
- helper：
  - 無碰撞；
  - 無選取框；
  - replaceable；
  - 不進創造欄；
  - 只包含原模型完全位於 Y≤0 的支腳 cube；
  - 所有 cube 平移到 helper 自己的 Y=0..16；
  - 跟隨主烤架方向。
- 有實體支撐時不建立 helper。
- 拆除主烤架或 registry 發現主烤架已不存在時清理 helper。

因此即使 helper 本身未來再有兼容問題，**烤架頂部也不應再次整體消失**。

## 4. Cookery 版本邊界重新收緊

參考：
https://www.curseforge.com/minecraft-bedrock/addons/kaleidoscope-cookery-unofficial

目前 CurseForge 的 v1.0.6：

- 上傳時間 2026-09-18；
- 檔案頁列出的 game versions 是 26.40 / 26.30；
- 專案描述寫 Requires Minecraft Version 26.3+。

因此不能只靠 manifest / Node 模擬就宣稱 Cookery 1.0.6 在 **26.51** 全功能實機通過。

Grilling 仍可保留 26.51 開發目標，但從 A2.7.3 起：

- Cookery 1.0.6 + 26.51 = **provisional runtime**；
- 只有 Minecraft 客戶端實測後才能逐項升級為 PASS；
- Cookery 公開 Script Event API 靜態／模擬測試通過，不等於整個 Cookery host 在新版本沒有 runtime regression。

## 5. 本批驗證標準

CI 必須通過：

- A2.0 → A2.7.2 全歷史回歸；
- 41 個 UI icon 真正重新 rasterize；
- icon contact sheet 生成；
- 主烤架不再引用 `grill_legged` geometry；
- helper geometry 全部限制於自己的 Y=0..16；
- helper 無碰撞／無選取；
- helper 建立、方向同步、拆除／孤兒清理邏輯存在；
- 所有 gameplay JS `node --check`；
- checksum-pinned bridge. Dash v1.2.0；
- source / dist 逐檔比較；
- 打包 mcaddon / brproject。

### 仍不能由 CI 宣稱

- Minecraft 26.51 實際 icon 最終畫面；
- 手持 attachable 最終第一／第三人稱效果；
- 懸空烤架 helper 實際 engine renderer；
- Cookery 1.0.6 各工作站在 26.51 的完整功能；
- BDS / 多人 / 重載持久化。

這些會在使用者拿到 A2.7.3 實機包後按 checklist 驗收。

## 6. 後續順序

在 A2.7.3 實機畫面未過關前，**不開始原本計畫的 A2.7.3 基礎切配食材**。

原「beef_chunks / chicken_skin / carrot_dice / potato_slice / raw_mantou_slice / squid_tentacle」切配批次順延為 **A2.7.4**。

A2.7.3 若還發現顯示或核心互動問題，繼續在 stabilization 系列修到可用，不用版本號掩蓋實機缺陷。
