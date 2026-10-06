# 煙火完整 Java 還原目標與部署門檻

使用者要求森羅煙火全部玩法、音效、邏輯、特效與細節一致，完成後才更新 live。此要求涵蓋完整還原，不能把「已修復某幾項」或 BDS 載入成功當成 100%。本輪不以中間候選更新 live；保留原有 live 版本，直到這項完成條件被實際滿足或使用者明確調整範圍。

原作來源基準為作者 `9a1acdab27698457bec16c9362678e574895a28c`（本輪重新 fetch 後仍為 main）以及維護中的 Forge 1.20.1／NeoForge 1.21.1 正式 1.1.1 發布。主要邏輯比對使用 NeoForge 1.21.1；不能把它的結果直接外推為 Forge 每個回呼也已驗收。先前 fixture 保留其歷史身分。Java 發布分支來源及新版本由酒館 `family/java-upstream.json` 和 BSM 六小時上游報告追蹤。

## 2.8.73 的可交付修復

- `CursedSkewerItem` 致死分支的物品破碎／雷擊聲與 24 個傷害粒子、18 個大煙粒子補齊；普通串透過原生傷害處理，而非直接 `kill()` 跳過 Heavy Metal 救援。
- 實際 BDS 顯示 `entityHurt` before 回呼的生命元件為暫時計入本次傷害的值。Heavy Metal 改判斷該暫存生命值是否 <=0，且足以穿透吸收效果的最大護盾上限；修正原本「傷害 >= 已減少生命」造成非致死誤觸，以及原本 `health>0` 阻止真正致死救援的錯誤。取消後原生生命回復，再於可寫階段結算為 1 HP。原作死亡事件與多 addon 的最後回呼順序仍另列，不宣稱此一修復閉合全部 G08。
- 六種選定原版音效事件改用官方 Java 1.21.1 原始音源與事件 gain/pitch/weight，包含紫水晶 shimmer 的 0.2 原始事件音量。mod 自己的 17 原始音檔保留。
- 普通串使用原版傷害 sprite 及八格煙 sprite；煙 sprite 僅整合至 atlas，不修改像素。原作數量、中心、Gaussian spread、速度和選定生命週期／尺寸參數有來源。Bedrock 連續積分、煙碰撞、初始隨機速度、光照／相機與混音尚未等價驗收。

來源檢查只驗證所修復的條件、輸出及失敗路徑。原生 probe 使用真實 mob 及 production callback，不建立模擬玩家；它驗證原生傷害／救援結果，不驗證真人畫面或聽感。所有聲畫保留 `client=false`。

## 不能標為 100% 的具體缺口

| 範圍 | 當前差距與關閉條件 |
|---|---|
| 全部進食／第三人稱 | 主副手、ONE/TWO/THREE/ALT/FOUR、皮膚與 FOV、旁觀者、取消、連吃、換槽、斷線 checkpoint 結算，需對同候選與同 Java 基準逐場景核對。原生 side callback 與客戶端錄影不能互相替代。 |
| Heavy Metal／效果 | 所選 BDS 的暫存生命值判定修復不等於 Java LivingDeathEvent 的任意 addon 排序、同 tick 多次致死、原生不死圖騰、死亡畫面／粒子全部一致。穩定 API 不提供剩餘吸收點數；對吸收效果最大值仍不足以證明致死的命中，採保守不觸發，部分已消耗護盾的致死救援仍有缺口。未知引擎需要重新核對這個原生語義。 |
| 原生新要塞折耳根 | stable runtime 沒有完整的原版 fresh-fortress generation callback；明示 producer API 仍存在。不能以附近掃描改玩家作物冒充原作 25% 新生成替換。 |
| 麻木準星／CapsLock | 原作 mixin 改動每人第一人稱準星，並有 CapsLock 架子操作。stable InputButton 只列 Jump、Sneak；現有腳本／骨架／蹲下替代不等價。 |
| 物品圖示與 tooltip | 任意食材組合的動態背包圖示、熱食 badge、模型 tint、全部光照與鏡頭呈現仍需 renderer 與真人比對。已有 static generated icons 不能代表任意組合。 |
| 油流與特殊整合 | 世界油目前是 bounded script simulation，不能宣稱為 Java FluidType。任意 Java 食品 finishUsingItem 回呼、Create、Maid、KubeJS 等需要对应 Bedrock 模組與正式契約，Java JVM 回呼不會被自動執行。 |
| 核心生存流程／資料 | 全部原作配方材料、數量、時間、動作、設備交換、熱度 bucket、拆除／爆炸／滿容器、跨區塊、重啟／重登入及多 addon 狀態不能只靠已有資料表一致或新世界初始化判為完整一致。 |
| 音效／粒子引擎 | 原始音源／sprite 一致不保證混音、衰減、隨機樣本選擇、tick motion、collision、光照與相機完全一致。需要兩個實際客戶端對照。 |

官方 capability 依據：[InputButton](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/inputbutton?view=minecraft-bedrock-stable)、[WorldBeforeEvents](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/worldbeforeevents?view=minecraft-bedrock-stable)、[Dimension](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/dimension?view=minecraft-bedrock-stable)。API 清單與原作要求的比對屬能力判斷；不是聲畫驗收。

## 驗收與後續

保留 [前次完整功能面審查](JAVA-PARITY-AUDIT-20261005.md)、[2.8.67 修復狀態](STATUS-A2.8.67.md)、[2.8.69 顯示修復](STATUS-A2.8.69.md) 與 [Cookery 1.6.0 適配](STATUS-A2.8.72.md) 的各自版本與證據範圍，不改寫歷史收據成為目前完整通過。

只有全部在範圍內的原作行為與實際聲畫完成核對，才能寫完成。平台不支持的能力或未驗收場景仍開放時，不發布虛構百分比，也不把本次候選部署成「100% 完成版」。達到使用者部署條件後，仍按 canonical PR／CI／合併、完整家族准入、停服備份、最新存檔演練與收據流程安裝；相同不可變候選已有成功證據會重用，不額外反覆跑相同 hash 或測試。
