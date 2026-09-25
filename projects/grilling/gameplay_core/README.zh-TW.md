# Kaleidoscope Grilling Gameplay Core

目前 canonical runtime：**A2.7.71 Shared Series Groups**。

這個目錄下的 `behavior_pack/` 與 `resource_pack/` 是目前真正要編譯、驗證與打包的來源。歷史 `development/gameplay_core/aXX*`、`verify_aXX*` 與已封存的版本 workflow 保留作追溯；**不要再從舊 augment/workflow 生成回來覆寫 canonical runtime**。

## Canonical 路徑

```text
projects/grilling/gameplay_core/behavior_pack
projects/grilling/gameplay_core/resource_pack
        │
        ├─ python development/gameplay_core/verify_current.py
        ├─ bridge Dash v1.2.0 build
        ├─ python development/gameplay_core/verify_current.py --compiled
        └─ python development/gameplay_core/package_current.py
                 ↓
           artifacts/review/*.mcaddon
           artifacts/review/*.brproject
           artifacts/review/SHA256SUMS.txt
```

GitHub canonical gate 為 `.github/workflows/gameplay-core.yml`，直接監聽正式來源。通過驗證且 PR head 提交主旨以 `release:` 開頭時，工作流程建立附有測試包的 GitHub Prerelease；這不等於穩定版或實機驗收。

## A2.7.71：加入本體既有創造群組

煙火是森羅廚房的附屬。依使用者指定的 Chinese Food 1.0.2 和實際 Cookery 1.0.6 catalog，創造分類採用 Equipment 分頁，直接追加到本體 `kaleidoscope_cookery:itemGroup.name.*` 群組。

90 個既有可見項目分別併入本體的工具、烹飪設備、儲存與實用工具、作物與種子、材料、食物、方塊及食譜頁。**這是使用 8 個已存在群組，不是新增 8 組。** catalog 的 `group_identifier` 只填本體 `name`，不另外指定 `icon`，也不在煙火語言檔重新定義本體群組標籤。

A2.7.70 的 11 個煙火自建群組屬於錯誤方向，已移除；舊報告只保留作非創造資料與可見性基線。88 份內部／隱藏定義維持不變，物品和方塊 identifier 仍是煙火自己的 namespace。

`development/gameplay_core/fixtures/a2771-series-catalogs.json` 保存公開參考包的 catalog、群組標籤與 SHA256，不包含完整第三方資源包。分類檢查用這兩個真實 catalog 核對群組存在性與資料合併；六種包排序的資料檢查不是 Minecraft UI 實測。

## 互動架構

原作 Java 是規格。`core_logic.js` 與 `*_core.js` 負責規則，`main.js` 與 adapters 負責 Minecraft API／事件／交易，attachable、geometry、animation 與 HUD provider 負責顯示。

Grill 與 Seasoning Bottle 共用 hand intent。A2.7.62 將 signature／capture／recheck 拆成純 `a2762_interaction_intent_core.js` 與 Minecraft adapter，延後執行前重新確認槽位和物品資料。

穿串仍有 item/block/entity 事件來源，但它們只作適配，實際玩法收斂到同一個 `scheduleSkewerAction` executor，保留同 tick 去重。

## 既有修復與歷史狀態

A2.7.66 補齊特製調料瓶的 64 種顯示狀態，覆蓋 128 組有效使用次數／變體輸入；切換外觀保留配料、使用次數、變體、名稱、原始 lore、dynamic properties 與物品限制。Cookery 調味先準備新瓶，再提交背包與鍋具，失敗嘗試回滾；延後期間換槽或改變手持內容會取消。

A2.7.65 的 39 個烤串 attachable／150 個 bite-stage geometry 已改成 A2764 baked hand-space 路線。後續版本的具體功能變更見各自 `docs/STATUS-A2.7.xx.md`，不可把早期文件的待辦項當成最新狀態。

A2.7.71 只改創造分類與版本資料，沒有再次修改上述玩法、手持模型、進食邏輯或材質。

## Legacy workflow 封存

A2.0～A2.7.60 的 65 條版本化 `gameplay-core-a*.yml` 原 blob 保存在 `docs/legacy_workflows/`，不再由 Actions 註冊。不要搬回 `.github/workflows/`；canonical gate 會拒絕重新出現的舊 workflow。

## 版本與資料相容

保留 BP/RP/module UUID、既有物品與方塊 identifier、world dynamic-property key 和 Cookery 1.0.6 依賴。新版本須在 `verify_current.py` 註冊對應 verifier，不能只改 manifest 後跳過檢查。

## 驗證邊界

Node／Python／Dash／CI 只能證明規則、語法、資源引用、編譯與打包；**不能證明 Minecraft/BDS 實機、Android 畫面、透明排序、動畫與多人可靠性**。本版 Minecraft／BDS／client visuals 旗標仍為 false。

`reports/build.json` 是早期歷史基線。當前創造分類請讀 `reports/a2771-shared-creative-groups.json` 與 `docs/STATUS-A2.7.71.md`。
