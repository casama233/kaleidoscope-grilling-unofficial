# Kaleidoscope Grilling Gameplay Core

目前 canonical runtime：**A2.7.62 Runtime Split**。

這個目錄下的 `behavior_pack/` 與 `resource_pack/` 是目前真正要編譯、驗證與打包的來源。歷史 `development/gameplay_core/aXX*`、`verify_aXX*` 與 `.github/workflows/gameplay-core-aXX.yml` 保留作版本追溯；**新修改不要再從舊 augment/workflow 生成回來覆寫 canonical runtime**。

## Canonical 路徑

```text
projects/grilling/gameplay_core/behavior_pack
projects/grilling/gameplay_core/resource_pack
        │
        ├─ python development/gameplay_core/verify_current.py
        │
        ├─ bridge Dash v1.2.0 build
        │
        ├─ python development/gameplay_core/verify_current.py --compiled
        │
        └─ python development/gameplay_core/package_current.py
                 ↓
           artifacts/review/*.mcaddon
           artifacts/review/*.brproject
           artifacts/review/SHA256SUMS.txt
```

GitHub 的 canonical gate 是 `.github/workflows/gameplay-core.yml`，它直接監聽 `projects/grilling/gameplay_core/**`。版本號 workflow 是歷史重建入口，不是新改動的預設入口。

## 互動架構

原作 Java 是規格。Bedrock 端把責任分成：

1. **規則層**：`core_logic.js`、各 `*_core.js`；
2. **Bedrock 適配層**：`main.js`、player/state adapters、事件路由與交易提交；
3. **顯示層**：attachable、geometry、animation、HUD provider。

A2.7.61 起，Grill 與 Seasoning Bottle 的 block interaction 共享同一套 hand intent。A2.7.62 再把 stack signature / capture / recheck 拆成純 `a2762_interaction_intent_core.js` 與 Minecraft `a2762_interaction_intent_adapter.js`，`main.js` 不再持有這組快照實作。Seasoning 仍使用實際操作手，不再硬編碼主手。

穿串因 Bedrock stable 沒有完全等價於 Forge `RightClickItem` 的 generic use-button 事件，對不可原生 use 的食材仍需要 item/block/entity 多個事件來源；它們只作事件適配，實際穿串仍收斂到同一個 `scheduleSkewerAction` executor，並有同 tick 去重。這是平台差異，不應再複製一套穿串規則。

## Legacy workflow 封存

A2.0 ～ A2.7.60 的 65 條 `gameplay-core-a*.yml` 已原 blob 移到 `docs/legacy_workflows/`，不再由 GitHub Actions 註冊。它們只作歷史追溯；不要搬回 `.github/workflows/`。`verify_current.py` 會對重新出現的版本化 gameplay workflow fail closed。

## 版本與資料相容

不要為重構更換既有：

- BP/RP header UUID；
- module UUID；
- 物品／方塊 identifier；
- world dynamic-property key；
- Cookery 依賴 UUID。

`verify_current.py` 會 fail closed 檢查這些核心身份。新版本需要新增對應 release verifier 並在 `verify_current.py` 註冊，不能只改 manifest version 後跳過驗證。

## 驗證邊界

CI／Dash／Node 檢查只能支持結構、規則、編譯與打包結論。**它不等於 Minecraft/BDS 實機測試，也不能證明 Android 手持模型、材質、HUD 或動畫正確。** 客戶端視覺問題必須以實機畫面與 Content Log 驗收。

早期 `reports/build.json` 是 A2.4 歷史基線，不是目前版本總結。當前版本請看最新 `reports/a27xx-*.json` 與 `docs/STATUS-A2.7.xx.md`。
