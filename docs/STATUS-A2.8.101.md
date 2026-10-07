# G101 Cloud Molang 修補

客戶端內容記錄確認 `variable.kg_velocity.x ?? 0`（y/z 同樣）不能作為 Molang `??` 的直接變數左運算元。本版把 Cloud 的三軸輸入改成 `variable.kg_velocity_x/y/z ?? 0`，保留未傳參時的零值回退；生成器與 canonical Native caller 同步。

Caller 仍把 Java blocks/tick 乘 20 傳入 blocks/second，Cloud 仍除以 20 還原。既有 vector 傳參保留供其他粒子使用；三個 scalar 使用同一數值。Cloud JSON 在還原變數名稱後與 G100 相同，其他 Java 公式、粒子數量、來源 RNG、G100 原世界參照與 G94 音效修補均保持。沒有更改存檔身份或其他玩法。指南 catalog 與 payload 的獨立內容協議 revision 維持 0.3.33，內容與 bytes 均未改動；它不是 pack release 身份。

兩組受影響的來源回歸共 39 項通過，覆蓋三軸 scalar 數值、未提供 event velocity 時的零值、其他 vector 使用者、客戶端報錯的 member-left forms、零值回退保留，以及原來源初始化公式守恆。生成器重現／check 與 JavaScript 語法檢查通過。這是針對已確認錯誤的靜態契約守衛，不是完整 Minecraft Molang parser 或真人渲染驗收。

Canonical release lineage 繼承 G100；既有驗證入口會執行受影響的回歸與生成器，沒有重複加入同一套測試。完整家族 static／Native BDS／存檔演練／准入／live 更新由家族流程另行記錄。

`client=false`、`production_ready=false`、`pending_client_acceptance`。Client 需清空內容記錄後重連並觸發放屁 Cloud，確認三軸 parser error 消失與畫面；nearest-player attraction、完整 Java Cloud 渲染／網路／混音差距仍未完成。
