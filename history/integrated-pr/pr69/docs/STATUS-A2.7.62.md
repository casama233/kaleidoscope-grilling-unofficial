# A2.7.62 — Big Vat Render Corrective

本批針對實機截圖中仍然存在的大缸渲染問題做根因修正，不改大缸容量、流體資料、互動、掉落或持久化格式。

## 實機現象

使用者截圖可分成兩個真正的渲染問題：

1. 放置後的大缸內沿出現一圈很細的草地綠色漏光／縫線。
2. 大缸拿在手上時仍使用 Bedrock 預設 custom-block item 姿勢，模型過大且貼近鏡頭，沒有 Java 原版的手持比例與角度。

截圖中的黑色方框線是 Minecraft 對目前瞄準方塊繪製的 selection outline；它不是大缸模型的一部分，因此本批不靠改 collision/selection box 去隱藏它。

## 根因 1：頂圈仍在使用透明洞平面

Java `big_vat.json` 的最上層是一個 16×4×16 元素；其 top texture 區域是一張 16×16 圖，其中中間 12×12 像素完全透明，只留下 2px 寬的外圈。

舊 Bedrock 轉換直接保留這個做法：

- `big_vat_0..4.geo.json` 的頂部 cube 使用完整 16×16 `up` face；
- 主材質使用 `alpha_test`；
- 四面內壁剛好在透明洞邊界 x/z = ±6。

在實機的 texture sampling / alpha cutoff 下，透明洞邊界與內壁共邊會把後方草地漏成一圈細線。這不是調整 UV 常數或把內壁偏移 0.01 能可靠解決的問題。

### 修正

五個液位幾何現在都：

- 移除原 16×16 alpha-cutout `up` face；
- 新增四條真實頂圈幾何：
  - north: 16×2
  - south: 16×2
  - west: 2×12
  - east: 2×12
- 四條幾何只取原貼圖中確定為 255 alpha 的外圈像素；
- 缸體 `*` material 從 `alpha_test` 改為 `opaque`；
- `fluid` material 仍保持 `blend`，液面邏輯不變。

因此主缸體現在不再依賴任何透明像素來挖洞，綠色內沿縫的成因被直接移除。

## 根因 2：Java 手持 transform 只被記錄，沒有被使用

倉庫已有：

`projects/grilling/reports/java_display_transforms/big_vat.json`

其中保存 Java 原版：

- first-person right: rotation `[0,45,0]`, scale `0.4`
- first-person left: rotation `[0,-135,0]`, scale `0.4`
- third-person right/left: rotation `[75,45,0]`, translation `[0,2.5,0]`, scale `0.375`

但舊報告明確標記 `applied_to_bedrock: false`。正式 Gameplay Core 沒有 `big_vat` attachable，因此拿起時一直回退到 Bedrock 的預設 block-item render。

### 修正

新增：

- `resource_pack/attachables/big_vat.attachable.json`
- `resource_pack/models/entity/a2762_big_vat_hand.geo.json`
- `resource_pack/animations/a2762_big_vat_hand.animation.json`
- `resource_pack/render_controllers/a2762_big_vat_hand.render_controllers.json`

手持幾何：

- 由正式 `big_vat_0` 空缸 shell 派生；
- shell 先向下平移 8 model units，把 Java 0..16 block-space 置中到 attachable hand-space；
- bound `root` 只負責 `q.item_slot_to_bone_name(context.item_slot)`；
- 真正的 rotation / scale / translation 全部放在 child `display` bone，避免重演舊調料瓶「動畫直接搬動 bound root 導致模型跑到玩家腿附近」的問題；
- first/third person、left/right 的 transform 逐值來自上述 Java display report；
- held shell 同樣使用實體頂圈，不再使用透明洞。

這條路徑使用穩定 attachable，不依賴 `minecraft:item_visual` 或 geometry `item_display_transforms` 的 Upcoming Creator Features。

## 防回歸

`tools/check_grilling_release.py` 現在額外驗證：

- 五個 Big Vat 世界幾何都沒有恢復 alpha-cutout top face；
- 四條實體頂圈的 origin / size / UV 精確存在；
- 放置幾何沒有 attachable binding；
- Big Vat 主 shell material 必須保持 opaque；
- hand geometry 必須綁定 item slot，且 shell transform 位於 child display bone；
- attachable 使用專用 hand geometry；
- 四組 first/third person transform 必須逐值等於 Java display report。

## 驗證邊界

本批可以由 canonical checker、JSON 解析、官方 Dash 編譯、compiled-output 比對與 deterministic package 證明「資源鏈與打包內容正確」。

但是否已在使用者目前的 Minecraft 客戶端完全消除綠縫、第一人稱大小是否最終視覺舒適，仍需要重新導入 A2.7.62 後的實機截圖確認。這次不把 CI 綠燈當作客戶端渲染驗收。
