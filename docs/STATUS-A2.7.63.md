# A2.7.63 — Client Visual Reference Gate

這批不假裝用靜態工具取代 Minecraft 實機，而是先把「能在進遊戲前抓掉的視覺斷鏈」變成 canonical CI 必跑項。

## 為什麼做這批

先前 Seasoning Bottle 曾經歷 A2.7.26 → A2.7.33 的 held/placed 修正。A2.7.33 的正確做法是把 -6Y hand-space 位移直接烘進 `geometry.kg_a2733.seasoning_bottle_hand`，因此 attachable **刻意不再綁** A2.7.26 的 hold animation。

也就是說：單純看到 `a2726_seasoning_bottle_hold.animation.json` 還在包裡，不能把它重新接回去；那會二次位移。A2.7.63 把這種『歷史資源還在、但 runtime 不應再引用』的情況寫成 guard。

## 新增 Visual Reference Gate

`development/gameplay_core/verify_visual_refs.py` 現在會掃 canonical BP/RP：

- attachable → geometry identifier
- attachable → render controller
- attachable → animation identifier / `scripts.animate` alias
- attachable → direct texture path
- `item_texture.json` → 真實 texture 檔
- `terrain_texture.json` → 真實 texture 檔
- behavior block → custom geometry
- behavior block material instance → terrain atlas key
- behavior item icon → item atlas key

任何引用缺失都會讓 `verify_current.py` fail closed。


## Gate 首次抓到的真斷鏈：Big Vat 水/熔岩

第一次跑 visual gate 即發現 `terrain_texture.json` 的 `kg_a26_water` / `kg_a26_lava` 分別指向包內不存在的 `textures/blocks/water_still_grey` / `textures/blocks/lava_still`。Big Vat 的 `fluid` material 又確實使用這兩個 key，因此這不是無用 dead entry，而是會影響水/熔岩液面的真實 resource chain。

Mojang `bedrock-samples@46ba6ea985fb5a92d79a9419198f10dda14c199d` 的 vanilla terrain atlas 已提供：

- `still_water_grey` → `textures/blocks/water_still_grey`
- `still_lava` → `textures/blocks/lava_still`

A2.7.63 因此改為 Big Vat 直接使用這兩個 vanilla atlas key，並移除假的 `kg_a26_water` / `kg_a26_lava` 自訂 alias；不把 Minecraft 原版貼圖複製進模組。

## 額外 guard

- 三個 Seasoning Bottle attachable 必須維持 A2733 baked hand-space geometry，且不得重新加入 root hold animation。
- 39 個 bite-stage skewer attachable 必須繼續綁定 A2725 first/third-person hold correction。

## 邊界

這個 gate 可以抓紫黑材質、缺 geometry、錯 render-controller 名稱、漏 animation alias 之類的靜態斷鏈；它**不能**判斷實際 FOV、手的位置是否美觀、Android/Windows 渲染差異、透明排序或動畫骨骼在真人皮膚上的效果。

因此仍保持：

- `minecraft_tested=false`
- `bds_tested=false`
- `client_visuals_tested=false`

下一步仍需要真 Minecraft 畫面 / Content Log 做 client visual 驗收。
