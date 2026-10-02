# A2.8.42：同一角色的效果快取一致性

承接 [A2.8.41 審查修復](STATUS-A2.8.41.md) 的全部功能與剩餘差距。本版修正最終檢查發現的 adapter 重現：同一角色由不同 JavaScript wrapper 讀寫效果時，WeakMap 快取可能回傳之前的期限，後续 tick 写回會蓋掉已提交效果。現在以原生 Entity.id 共用單 tick 快取；每 tick 清除 ID map，沒有無限累積。無 ID adapter 僅使用 WeakMap fallback。

讀出與回傳值均複製每個效果項，未提交的 duration 修改不污染快取；持久寫入拋錯時棄置快取並讓下一次讀取核對實際值。12 個新增回歸包含不同 wrapper、未提交修改、寫後拋錯，以及原先生命週期／排程／設定／aux 測試。完整 canonical gate、Dash export、家族／原生／存檔證據另行記錄。

BP/RP 與 release history 同步新身份 2.8.42，不改寫 2.8.41。已登記 Cookery API 模組／宣告未變，維持 0.2.3；指南內容未變，維持 0.3.14。原生玩家事件、聲畫、多人體驗與 Java 未等價部分仍未宣稱通過；本版仍需自己的完整家族收據與真人驗收，不沿用旧延期許可。
