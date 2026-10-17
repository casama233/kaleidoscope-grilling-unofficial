# G124：調料資料映射與來源冗餘整理

精確 predecessor 為 G123 main `080b04959f469626da36180198da6489435df5be`。來源修補先記為 `7d007865`；版號、包／模組與自有相依同步為 2.8.124，指南資料 0.3.54。G123 的三語正文掛鉤／family API 0.2.10、G122 的鍋具守恆、原生食物品質與施肥所有權保持，舊 STATUS／release-history 不改寫。

目前 Java 作者 1.1.1 的 Forge／NeoForge 維護發布與 2026-10-09 10:23 UTC 作者查核一致。對照選定 [GrillingDataManager](https://github.com/breezeth-CN/KaleidoscopeGrilling/blob/9a1acdab27698457bec16c9362678e574895a28c/neoforge-1.21.1/src/main/java/cn/breezeth/kaleidoscope_grilling/data/GrillingDataManager.java)：資料 reload 從預設 map 合併各根，同 ID 由後根覆寫；取料及食用時讀目前映射。兩分支的此段行為已核對；這是來源對照，沒有宣稱執行完整 Java JAR。

G123 取料與食用都查固定 `SEASONING_KINDS`，HUD 又有另一條計數路徑，無法接收明確的新資料映射。G124 自有 `seasoning_registry_core.js` 統一預設與有效 map，main 取料、production 食用與 HUD 共用。食物仍保存原 ingredient IDs，reload 不改既有瓶子／食物；未知或空 kind 可作材料但不授予虛構效果。三個必要 base ID、8 格容量、16 次用量、原效果門檻及配方不變。

現有公開 Server-only API 新增 `replace_seasoning_data`／`seasoning_data_roots_v1`，沿用已存在的登記保存、30,000-byte 上限、讀回及回滾。資料先完整驗證再提交；保存後拋錯仍恢復記憶體及持久資料，未確定回復維持原有 fail-closed 行為。舊 v1 存檔無 `seasonings` 欄位仍載入預設。使用契約見 [integration API](BEDROCK-INTEGRATION-API.md#調料資料重新載入)。

未合併的 `grilling-seasoning-registry-20261008` 原型完整保留；本分支只承接已核對的必要自有邏輯，並集中預設表。沒有完整 Cookery 私有腳本、原包或世界進入公開 Git，也没有新增未知宿主能力、輪詢提示或成功操作 Actionbar。

本機僅執行受影響的既有 integration 與 production 食用檢查，增加保存重載／錯誤根／寫入故障及已存食物 reload 的具體反例；不新增組合矩陣。production 食用檔通過 299 個既有及相關案例。G124 verifier 繼承 G123 的所有歷史、host、guides、G122 守恆與品質門檻；完整必要套件交 PR CI，不在本機重跑。

以下限制分開保留：明確 provider 須提供資料根，沒有自動讀取 Java datapack；普通未擴充 Cookery／任意第三方 producer 不由此介面憑空接通；任意秘製串 native inventory icon 仍有平台投影限制；食用、原生事件、聲畫與完整植物操作仍須同候選實測。G123／T142／W119 已部署的家族載入、保存演練及 227／31／681 指南接收證據只用來更正過時現況記錄，不冒充 G124 驗收。

G124 PR／CI、完整家族 Native、fresh 停服存檔演練及 LIVE 部署另依精確來源收據進行。本狀態頁不宣稱本候選已部署或 client 通過；`client=false`、`production_ready=false`。
