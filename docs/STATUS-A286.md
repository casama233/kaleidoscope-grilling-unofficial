# A2.8.6：烤架、大缸與手持模型追修

## 玩家證據與修正

| 問題 | 原因／修正 | 驗證界線 |
|---|---|---|
| 烤架移動視角時閃爍 | 烤網 Y=3.98438、爐口 Y=4，烤網 15×11 的邊緣跨入爐口。爐口改為四條實際邊框，烤網裁至內腔 14×10，保留有符號 UV；移除內腔頂部反向平面。涵蓋冷／熱、平放／帶腳及物品模型。 | 幾何交疊檢查通過；需客戶端移動視角確認。 |
| 未滿的大缸渲染異常 | 缸沿 Y=12 的底面原本是橫跨整個內腔的 16×16 平面，改成四邊環形。空缸、油及岩漿使用單面 alpha test，避免實心缸體參與不必要的透明排序；水保留 blend。保留 0–4 液位與液面頂面。 | 5 液位幾何及材質策略檢查通過；水的透明排序仍需客戶端確認。 |
| 空瓶與完成調料外觀相同 | canonical special_seasoning 原本直接引用空瓶幾何。現改為滿內容物；pending 使用半高內容物作狀態識別。64 種既有實體 ID 保留其既有份量／顏色映射。內容物獨立不透明繪製，再繪製玻璃外殼。 | 模型和渲染引用可區分；pending 的半高是通用狀態示意，並非精確配方容量。 |
| 瓶子在肩膀、廚具架在背後 | 67 瓶＋1 架移除 root→display→element 多層靜態骨架，改為單一 grip 綁定；內容物採獨立同錨點幾何。廚具架从世界座標移到手部錨點；左右手、第一／第三人稱各自使用 grip 動畫。 | 使用已有實機修復參考的單骨架方案；不能宣稱本次已完成客戶端姿勢驗收。 |

不新增常駐提示。39 種串的咬合階段、原生進食、A2.8.5 交易結算與持久化機制保持不變。

## 證據與限制

- `python3 development/gameplay_core/verify_current.py`：通過，涵蓋既有玩法回歸、107 attachable 引用、68 個重綁定物品、10 個開口幾何及方塊材質策略。
- 獨立 BDS 1.26.51.1：30 個大缸狀態組合、4 個烤架狀態及 107 個可持物品註冊通過。這不是客戶端渲染測試。
- 保留包 UUID、方塊／物品 ID、世界狀態鍵及原有依賴。
- R05／R06 仍開放，需更新後的第一／第三人稱、移動視角、部分液位及水液面畫面驗收。

## 技術參考

- [Microsoft：Attachables 與物品骨架綁定](https://learn.microsoft.com/en-us/minecraft/creator/documents/attachables?view=minecraft-bedrock-stable)
- [Microsoft：材質與單面／透明渲染](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/blockreference/examples/blockcomponents/minecraftblock_material_instances?view=minecraft-bedrock-experimental)
- [Blockbench Bedrock 解析／匯出](https://github.com/JannisX11/blockbench/blob/master/js/formats/bedrock/bedrock.js)：Bedrock X 座標鏡射且保留面名；因此保留原先內壁面方向，沒有把 Java／世界 X 軸假設套用到 Bedrock 幾何。
