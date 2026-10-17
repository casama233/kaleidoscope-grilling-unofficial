# G125：場景聲畫、延後操作與滿背包守恆

本次從 G124 main `de445c13985cdcdab0f2353ef259aaa13e523e08` 分出操作、視覺、沉浸三個修補分支，整合時交叉審查。包／模組／自有相依為 2.8.125，指南身份 0.3.55，既有內容、UUID、Cookery 1.6.0 及 family API 0.2.10 保留。前版 STATUS 與 release-history 保持原身份。

已公開的修補來源見證為 [`2ef4b7b6ffa782316378dc5d8fef3f9217b098bf`](https://github.com/casama233/kaleidoscope-grilling-unofficial/commit/2ef4b7b6ffa782316378dc5d8fef3f9217b098bf)。完整 Git tree 與整合來源相符；main 的十七處精確變更接續 G124 原前像，舊來源鏈不改寫，fixture 本身不能擴大該公開 commit 所允許的來源。

Java 對照為 [作者 `9a1acdab27698457bec16c9362678e574895a28c`](https://github.com/breezeth-CN/KaleidoscopeGrilling/tree/9a1acdab27698457bec16c9362678e574895a28c)，Forge 1.20.1／NeoForge 1.21.1 分別核對。這是來源修補；沒有執行完整 Java JAR 或取得本候選的真人對照影片。

## 烤架取消與延後目標

G124 的爆炸 callback 延後執行卻沒有重新讀取取消狀態，也沒有確認仍是同一個烤架。G125 在 before-event 保護原方塊並只複製原生 ItemStack，延後才讀完整 metadata。取消為 true、事件不可讀、站點／朝向／內容／所有權／語義狀態改變時均保留當前站點；正常 phaseTicks 與 flipCooldown 推進不構成誤判。

playerBreak 在先前已被取消時不接手，已接手的延後拆除也使用相同目標守護。**這不代表能分辨之後其他插件再次將同一個 cancel 欄位寫成 true**：原生拆除本來已由本模組取消，後續同值寫入沒有獨立身份訊號。任意外部命令完全重建相同方塊、物品及 owner 記錄的不可觀測替換也不宣稱可識別。

交叉審查發現 `getCanDestroy`／`getCanPlaceOn` 不允許在 restricted execution 讀取；已將這些讀取移到延後階段。BDS 1.26.52.3 的隔離診斷使用原樣 production callback 與原生 chest 庫存，確認合法事件、後續取消、owner 改變、普通時鐘推進四條路徑。這只認證原生事件與 API 生命周期，沒有執行完整 customBreak、玩家操作、家族或存檔遷移。[精確範圍](evidence/grill-deferred-native-20261009.json)

## 操作交易與滿背包

榨油機延後放入油渣前先確認手部與站點 instance；同一機器的兩名玩家依最新容量逐次處理，不因第一人合法投料就取消第二人的點擊。進入扣料／credit 交易後仍嚴格確認方塊及保存前像；新放置的榨油機啟用新的 instance，六 tick 的壓榨動作也必須回到同一個站點。原生寫入需讀回，回滾只恢復本次確認寫入的值。大缸延後互動另外核對自己的 instance、狀態及保存前像，換站点後不套用舊點擊。

榨油機與大缸拆除也使用 instance／前像守護，先保存包含原方塊、資料與預定掉落的 prepared receipt，再確認撤除來源及每個實際掉落。失敗時必須確認回收所有產物，才恢復仍由本次交易控制的站點；未知掉落／remove、外來換入或部分保存不明保留詳細 incomplete 記錄。生存模式交回機器及油渣／保存油量的大缸，Creative 按原作不強制產生掉落。這不是全域 crash 原子交易，且原生玩家拆機仍需實測。

串譜製作、手動穿串、拆串共用原生出料 planner：先按扣料後的庫存預留可堆疊空間，剩餘物在玩家位置掉落，保留完整 native ItemStack 資料。滿背包本身不再拒絕有效操作；穿串保留剩餘棍，拆串交回各食材及一根棍。新副手串也是已交付產物，只有確認收回它及所有槽位／掉落，才可退主手材料。

未確認的 spawn、被其他流程接走的物品、清除失敗或外來槽位不會觸發盲目退款。共用的持久 player item receipt 阻止同玩家在未知結果上再次串譜／穿串／拆串。這是保守隔離，並不宣稱跨容器 crash 原子性；故障記錄須按實際交付結果恢復。

## 場景畫面

| 項目 | G125 修正 | 仍須驗證／適配界線 |
| --- | --- | --- |
| 烤架亮度 | 有效點火值 13→7，熄火 0，對應兩個 Java loader。 | 客戶端環境光與光影效果。 |
| 世界油液 | 官方 Bedrock water/lava 動畫條乘上原作三種油 tint；頂面 still、側面 flow。 | 原生 Bedrock sprite 適配，沒有宣稱 Java vanilla 像素、流體斜坡網格或流動物理相同。 |
| Premium 大缸 | 獨立滿亮液面、原作四層高度與 UV inset；缸壁不發光。 | 有界 transient helper，負載下可能跳中間幀，與地形動畫相位不保證同步。 |
| 秘製串牆譜 | 原 16px stick／食材 GUI mask 分層，讀實際食材、生熟、count 與 variant。 | 每張譜一個 helper；任意外部食材仍需可公開 palette，背包 icon 不受場景 helper 影響。 |

85 張極小 mask 為原作形狀與遮擋的固定分層，不枚舉食材組合。Mojang 動畫來源及授權、顏色計算、helper 配額與完整限制見 [場景修補證據](evidence/scene-visual-repair-20261009.md)。

## 沉浸、聲音與效果

Numb 將 Java tick×radian 轉為 Bedrock seconds×degrees：`20 × 0.32 × 180 / π = 366.6929889`，修正原本 20 倍過慢的相位。獨立 `kg_numb` controller 循環播放、零淡出、有界同步，進食／搖瓶／撒料期間讓出姿勢；結束只停止自己的 controller。四肢仍使用目前的 additive pose 與 move-speed 映射，尚未宣稱整個 Java 基礎姿勢相同。

交叉審查另外修正獨立循環與榨油錘擊同時控制手臂的回歸。成功啟動錘擊時暫停 Numb 十 tick；兩條刷油路徑暫停二十九 tick，包含現有動畫與淡出。只停止 `kg_numb`，不清除其他 controller；停止失敗下 tick 重試，離線／重生清理期限。

Premium 油壺透過近期公開 Oil API receipt 候選，每八 tick 為每名附近玩家独立做 1/5 抽樣，成對發出 lava／flame；保留原作範圍、位置與速度，沒有掃描整個世界或改油量。候選發現與 freshness 仍依賴既有放置 renderer。

搖瓶本人用不指定固定座標的 `Player.playSound`，旁觀者維持原 BlockPos one-shot；停止只停止本人的 handle。Stable 2.9.0 沒有 sound handle 的 move／seek，實際移動声場仍需真人聽覺驗收。重金屬只在效果提交、HP=1 並讀回後新增原生圖騰粒子，声音／粒子失敗不重做保命結算；它不是 Java entity event 35 的完整第一人稱畫面。

## 驗證與未完成範圍

本機只執行各修補影響的既有交易／顯示／效果檢查，新增兩個必要的烤架取消與 Numb 回歸入口。G125 verifier 繼承全部舊門檻，新增場景產出一致性與目前亮度檢查；完整必要套件交 canonical PR CI。來源審查、Python 原作翻譯圖像重組、API doubles 與資產 hash 均不充作真人畫面證明。

以下仍未完成：任意秘製串／餐盤的 native inventory 動態內容、熱食 badge、史萊姆／神秘串原生背包動畫、秘製串 eating HUD 動態色彩通道、Numb 準星偏移、可靠第一人稱碎屑抑制、完整圖騰 event 35、原生流體／碰撞與要塞生成入口、任意 Java 食物回呼及完整植物適配。JSON UI 的秘製串 HUD 路由仍待實作與驗證，不能因本次未完成而稱平台普遍不可能。

本候選需另外通過完整家族 static／BDS／fresh 停服存檔與 canonical family guard，再依既有授權更新 LIVE 供使用者實測。此工作區尚無該伺服器的有效連線／部署設定，不能把隔離 BDS 診斷或 CI 打包稱為 LIVE 更新。維持 `client=false`、`production_ready=false`、`pending_client_acceptance`。
