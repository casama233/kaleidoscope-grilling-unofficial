# A2.8.48 原作聲畫回饋修復

本版依 Java 1.1.1 原碼修復烤爐、調料、榨油、黃金串、無敵效果與盤子／食譜的
聲音和粒子。保留 2.8.45 的熱食完成判定、原生龍血、共享進食分支、秘製串手持顯示，
以及 2.8.46 的三語系列標籤及 canonical 2.8.47 的第三人稱進食抬手。完整功能面比較和未完成項見
[本次 Java 審查](PARITY-AUDIT-20261003.md)。

- 火箱煙／火改為原作各自的位置、概率與初速；刷油改用 `grill_flip`，移除自創的烹調階段火聲。
- 調料加入五粒 end rod、搖勻 12 粒 happy；落錘 14 粒 crit 與隨機 .82–.94 音高。瓶子放、堆、取各用原作事件及音量。
- 黃金串完成時補 18 點螺旋 spark；無敵持續時每十 ticks 一粒，受擊六 ticks 內只回饋一次，使用原生碰撞高度定位 8 spark+4 end rod。
- 普通串成功盾分支補 28 spark、盾聲與紫水晶聲。盤子放取、牆上食譜放取改回對應 itemframe 聲，食譜完成改回原作 action-success。
- 六種 `kaleidoscope_grilling:feedback_*` 粒子皆為單次一粒、零 emitter 偏移，由顯式 Molang 速度控制。沒有把原版 steady/manual emitter 的呼叫次數錯當粒數，也不覆蓋任何 vanilla 粒子。
- 音效和粒子失敗互相隔離；API 接受／失敗有累計計數，錯誤最多每 1200 ticks 告警一次。這些計數表示 API 呼叫結果，並非已看見畫面。

粒子外觀和後續運動採釘選 Mojang `v1.26.50.4` 定義；原作事件的數量、位置、
高斯散布、初速與音效參數各有來源。Bedrock 後續粒子物理不是 Java particle class
的完整拷貝。烤爐仍沿用每四 server ticks 的取樣，不能宣稱等同 Java view-local
`animateTick` 的整體密度。熔岩辣椒油环境粒子、普通串致死分支的完整特效、
部分原作 GUI／整合仍未完成。

新回歸檢查粒子分布、範圍、冷卻、one-shot 定義、Molang 單位換算和錯誤隔離。
`development/native/feedback-probe.js` 只供隔離候選驗證原生 API，使用非玩家豬實體；
不得打包、不得在正式存檔執行，也不能代替 Windows 真人聲畫驗收。

包及模組升為 2.8.48，UUID／Cookery 1.0.8 依賴保持既有來源。指南內容與分類不變；由 canonical 2.8.47 的 payload 0.3.16 同步升為 0.3.17，
發布 revision 為 kg-guide-a3-2848。家族候選必須重新產生逐檔收據並驗證，
舊版 BDS／真人結果不能自動繼承到這份新內容。

依 2026-10-03 最新家族維護政策，完整 static、BDS、saved_world_migration 通過後，
為這份候選收據登記持續授權的 deferred_client_acceptance，即可更新 luosen live
供真人開發測試；保留 client=false、production_ready=false 與 pending_client_acceptance。

本候選以正常 merge 保留 PR #121 的第三人稱手臂旋轉修復與其來源／回歸。
先前未部署的 feedback 2.8.47 候選因版本碰撞撤回，詳見
[版本碰撞處理紀錄](RELEASE-COLLISION-20261003.md)；不重用其版號或驗收收據。
