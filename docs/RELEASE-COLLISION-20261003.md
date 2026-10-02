# 2.8.47 候選碰撞與 2.8.48 來源

PR #120 的原作聲畫回饋原先使用未合併、未部署的 2.8.47 候選。
該候選最後提交為 `cc57184b7e4579db136bb993f73382c177b93770`，原始 pack hash 為：

| Pack | 檔案數 | 未部署候選 SHA256 |
| --- | ---: | --- |
| BP | 523 | `e655bef297d5378d2c1a300a9203531c7bb471c308c05d50da1e385a249978bb` |
| RP | 1669 | `5b977b77aef9476b443449581770a26068cb8f10bf2dce41dab79bcfce24a076` |

在它等待 CI 時，另一項已授權的第三人稱進食修復 PR #121 以
`de66c6e2c6095bc29736ac9108df3c50396b702f` 完成並合併到 main
`e8c9358`，占用正式 2.8.47。其合法 BP／RP hash 分別為
`37a3ca99a5726a736cb14120a0e57cc9a789ebc9cdbd64f46ef461fbb46dea2d` 與
`c5a68498572ca8ded146de57f48ff272903e26f2eb9bfc022d9d8e96ad0461b4`。

因此撤回原 feedback 2.8.47 候選；它沒有部署，不作正式 release-history 的第二份 47。
原始提交、artifact、外部逐檔收據與驗證 log 保持原樣，並由正常 merge 的第一父提交保留。
本次以 canonical main 的 47 history entry 為準，另追加全新 2.8.48。

合併保留 47 的選定手臂 rotation、主副手分支、第三人稱／原生 use-item-progress 限制、
物品切換停止條件、Mojang 來源 fixture 及完整回歸；48 在此基礎加入已審查的聲畫回饋。
包、模組、配對相依、兩個 bridge config 同步 2.8.48；指南 payload 升為 0.3.17、
revision `kg-guide-a3-2848`，內容與分類保持 canonical。

48 必須重新取得自己 exact source 的 CI、完整家族 static／BDS／存檔演練與逐檔收據。
47 候選的結果不繼承為 48 驗收；client 與 production_ready 保持 false，直到相應真人驗收。
