# G117：瓶爆炸取消與手持營養結算

2026-10-08。基於canonical G116／`b4bd3229f254adf58be1ee413f89daa1ab9c4df0`，
只修兩項已重現的production交易問題，保留G116餐盤修補與現行素材。
來源／包身份以`baseline.json`及append-only `release-history.json`為準。
包與模組2.8.117、guide0.3.47；UUID、Cookery1.6.0、server2.9.0及server-ui2.2.0相依不變。

## 修補範圍

1. **瓶爆炸取消**：舊`scheduleNativeBottleExplosion`只在最初檢查cancel。
   排程後有其他before-event訂閱者取消時，仍把瓶變AIR並清除完整native容器及保存記錄，沒有掉落。
   現在延後工作必須再次確認`cancel===false`；已取消或event不可讀時不修改瓶、ItemStack或ownership。
   捕捉目標／owner的既有保護，以及確認未取消時的原本毀損／不掉落行為保留。
2. **手持提前食用**：G116已修餐盤營養，但手持`hungerSettle`仍用hunger增加前取得的saturation view。
   hunger10／saturation10的牛肉串在25-tick停止時，寫入15超出舊cap10並退回整筆交易。
   現在hunger寫入後在`commitEating`內重新取得saturation，尊重live effectiveMax。
   取得／寫入失敗仍回復完整原物品、hunger與saturation；成功只扣一份、給一次原有效果。

不修改原配方、checkpoint／release grace、熱食倍數、正常原生完成路徑或G116餐盤路徑。
放置盤完整mesh、yaw／dirty／helper清理與手持五行內容／decoder仍是獨立工作，
來源集中在[舊PR處置索引](audit/PR-TRIAGE.md)，沒有把舊union套回現行包。

## 本機針對性證據

先用新增的最小production函式回歸確認舊來源確實失敗，再修來源。
沒有增加另一套測試框架；本機只執行受影響的既有入口，完整必需套件由本候選PR CI執行。

| 入口 | 結果與範圍 |
| --- | --- |
| `node --test development/gameplay_core/test_seasoning_native_storage.mjs` | 98通過。新增一項具體故障回歸：較後cancel及不可讀event保留完整瓶、原容器identity與兩筆保存資料；既有未取消爆炸、owner replacement及rollback仍通過。 |
| `node --test development/gameplay_core/test_eating_native_completion.mjs development/gameplay_core/test_full_skewer_flow.mjs` | 323通過。兩项新增回歸覆蓋captured-cap故障、較低live cap、exact stack、重複stop／complete及refresh／寫入失敗回滾；沿用既有主副手、Creative、熱食、原生完成和全串管線檢查。 |

飽和度案例使用G116餐盤回歸已有的native captured-cap模型；它使舊手持production函式在10／10條件回滾，
修補後得到hunger15／saturation15並只消耗一份。10／2對照得到15／8；較低effectiveMax被尊重。
這些是API doubles直接執行production函式的B證據，**不是新的BDS或真Player事件觀察**。
版本／指南生成及freeze身份檢查不算玩法或client證據。

## 家族與真人驗收

canonical PR／必要CI／合併、完整家族static／BDS載入、停服存檔rehearsal、候選准入及LIVE讀回須綁定新的G117身份。
不能將G114／G116或原診斷候選的收據、載入及真人觀察沿用成G117接受。
本頁沒有聲稱本候選已部署；實際家族收據與LIVE狀態由完整家族流程另行記錄。

受影響原生／client情境：較後插件取消的瓶爆炸、event生命週期、完整瓶資料重啟保留；
手持固定／秘製串在不同hunger與saturation下提前停止，核對一次扣料、metadata、原營養及效果。
保留合法未取消爆炸、未到checkpoint取消、完整食用和主副手控制，不使用模擬玩家。
維持`client=false`、`production_ready=false`及`pending_client_acceptance`，直到實際人工作業驗收。
